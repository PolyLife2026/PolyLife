from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Competition, CompetitionParticipant
from ..serializers.competition import CompetitionSerializer
from ..serializers.competition_result import CompetitionResultSerializer
from ..services.competition_ranking import recalculate_competition_rankings
from .permissions import IsCoach


@method_decorator(csrf_exempt, name="dispatch")
class CompetitionCreateView(generics.CreateAPIView):
    """
    SCRUM-124: POST /team1/api/competitions/

    Creates a new competition.
    Only coaches/admins may create competitions.
    """

    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    authentication_classes = []  # for test purposes only
    permission_classes = [IsCoach]

    def perform_create(self, serializer):
        user_id = self.request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers")

        serializer.save(created_by=user_id)


class CompetitionJoinView(APIView):
    """
    SCRUM-27

    POST /team1/api/competitions/<id>/join/

    Allows a participant to join a competition.
    """

    authentication_classes = []

    def post(self, request, pk):

        user_id = request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers")

        try:
            competition = Competition.objects.get(
                competition_id=pk,
                is_deleted=False
            )
        except Competition.DoesNotExist:
            return Response(
                {"detail": "Competition not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only pending competitions accept participants
        if competition.status != Competition.Status.PENDING:
            return Response(
                {"detail": "Competition is closed for enrollment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if CompetitionParticipant.objects.filter(
            competition=competition,
            user_id=user_id
        ).exists():
            return Response(
                {"detail": "Already joined this competition."},
                status=status.HTTP_409_CONFLICT
            )

        CompetitionParticipant.objects.create(
            competition=competition,
            user_id=user_id
        )

        return Response(
            {"message": "Successfully joined competition."},
            status=status.HTTP_201_CREATED
        )

class CompetitionResultView(APIView):
    """
    SCRUM-28

    POST/PUT /team1/api/competitions/<id>/results/

    Records (or updates) a single participant's score in a competition and
    immediately recalculates rankings for the whole competition. Restricted
    to coaches/admins (same as CompetitionCreateView).
    """

    authentication_classes = []
    permission_classes = [IsCoach]

    def _record_result(self, request, pk):
        try:
            competition = Competition.objects.get(
                competition_id=pk,
                is_deleted=False,
            )
        except Competition.DoesNotExist:
            return Response(
                {"detail": "Competition not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompetitionResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]
        score = serializer.validated_data["score"]

        try:
            participant = CompetitionParticipant.objects.get(
                competition=competition, user_id=user_id
            )
        except CompetitionParticipant.DoesNotExist:
            return Response(
                {"detail": "This user has not joined the competition."},
                status=status.HTTP_404_NOT_FOUND,
            )

        participant.total_score = score
        participant.save(update_fields=["total_score"])

        # SCRUM-28 (subtask 3): recalculate rankings for the whole competition.
        recalculate_competition_rankings(competition.competition_id)
        participant.refresh_from_db()

        return Response(
            {
                "user_id": participant.user_id,
                "total_score": participant.total_score,
                "rank": participant.rank,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        return self._record_result(request, pk)

    def put(self, request, pk):
        return self._record_result(request, pk)
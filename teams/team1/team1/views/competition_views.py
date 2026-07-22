from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import get_object_or_404
from ..models import Competition, CompetitionParticipant
from ..serializers.competition import (
    CompetitionSerializer,
    CompetitionListSerializer,
    CompetitionDetailSerializer,
)
from ..serializers.competition_result import CompetitionResultSerializer
from ..serializers.competition_leaderboard import CompetitionLeaderboardSerializer
from ..services.competition_ranking import recalculate_competition_rankings
from .permissions import IsCoach


@method_decorator(csrf_exempt, name="dispatch")
class CompetitionListCreateView(generics.ListCreateAPIView):
    """
    GET /team1/api/competitions/ — list competitions
    POST /team1/api/competitions/ — create (coach only)
    """

    authentication_classes = []

    def get_queryset(self):
        return Competition.objects.filter(is_deleted=False).order_by("-date_start")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CompetitionSerializer
        return CompetitionListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCoach()]
        return []

    def perform_create(self, serializer):
        user_id = self.request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers")

        serializer.save(created_by=user_id)


class CompetitionDetailView(generics.RetrieveAPIView):
    """GET /team1/api/competitions/<id>/ — competition details"""

    lookup_field = "competition_id"
    authentication_classes = []
    permission_classes = []
    serializer_class = CompetitionDetailSerializer

    def get_queryset(self):
        return Competition.objects.filter(is_deleted=False)


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

class CompetitionLeaderboardView(generics.ListAPIView):
    """
    SCRUM-29

    GET /team1/api/competitions/<id>/leaderboard/

    Returns participants of a competition ordered by rank (best first).
    Supports pagination (global PageNumberPagination, subtask 3) and an
    optional `?user_id=` filter to look up a single participant's row
    (subtask 3: filtering).
    Open to any authenticated participant, not just coaches.
    """

    authentication_classes = []
    serializer_class = CompetitionLeaderboardSerializer

    def get_queryset(self):
        competition_id = self.kwargs["pk"]

        get_object_or_404(Competition, competition_id=competition_id, is_deleted=False)

        queryset = CompetitionParticipant.objects.filter(
            competition_id=competition_id
        ).order_by("rank", "-total_score")

        user_id = self.request.query_params.get("user_id")
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)

        return queryset

class CompetitionFinalRankingsView(generics.ListAPIView):
    """
    SCRUM-30

    GET /team1/api/competitions/<id>/final-rankings/

    Same ordered data as the live leaderboard, but only returned once the
    competition has actually ended (subtask 2). While it's still
    pending/active, the response explicitly tells the caller the
    rankings aren't final yet instead of silently returning partial data.
    """

    authentication_classes = []
    serializer_class = CompetitionLeaderboardSerializer

    def list(self, request, *args, **kwargs):
        competition = get_object_or_404(
            Competition, competition_id=self.kwargs["pk"], is_deleted=False
        )

        if competition.status != Competition.Status.FINISHED:
            return Response(
                {
                    "detail": "Final rankings are not available yet: "
                              "the competition has not ended.",
                    "status": competition.status,
                },
                status=status.HTTP_409_CONFLICT,
            )

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return CompetitionParticipant.objects.filter(
            competition_id=self.kwargs["pk"]
        ).order_by("rank", "-total_score")
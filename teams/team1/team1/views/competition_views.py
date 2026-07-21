from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Competition
from ..serializers.competition import CompetitionSerializer
from .permissions import IsCoach


@method_decorator(csrf_exempt, name="dispatch")
class CompetitionCreateView(generics.CreateAPIView):
    """
    SCRUM-124: POST /team1/api/competitions/
    Creates a new competition. Only coaches/admins may create competitions
    (SCRUM-125), enforced the same way as ChallengeCreateView via IsCoach.
    """
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    authentication_classes = []  # for test purposes only, same as ChallengeCreateView
    permission_classes = [IsCoach]

    def perform_create(self, serializer):
        user_id = self.request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers")

        serializer.save(created_by=user_id)
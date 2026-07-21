from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from ..models import Challenge
from ..serializers.challenge import ChallengeSerializer
from .permissions import IsCoach, IsChallengeCreator 
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import generics

from ..models import ParticipantScore
from ..serializers.challenge import LeaderboardSerializer



# Create your views here.

class ChallengeCreateView(generics.CreateAPIView):
    """
    POST /team1/api/challenges/
    Creates a new challenge. The request body should contain the challenge data in JSON format.
    required Header:
      X-User-Id: <user_id> (the id of the user creating the challenge)
      X-User-Role: <user_role> (the role of the user creating the challenge, e.g., "coach")
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

    authentication_classes = []  #for test purposes only
    
    permission_classes = [IsCoach]  #only for test without logging in

    def perform_create(self, serializer):
        # Get the user id from the request headers
        user_id = self.request.META.get('HTTP_X_USER_ID')
        
        # Check if the user id is present
        # Assuming you have a field named created_by in your Challenge model
        if user_id:
            serializer.save(created_by=user_id)
        else:
            # Handle the case where the user id is not provided in the headers
            raise PermissionDenied("Missing user id in headers")


class ChallengeDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Challenge.objects.all()

    serializer_class = ChallengeSerializer

    permission_classes = [IsCoach, IsChallengeCreator]

    lookup_field = 'challenge_id'

    def update(self, request, *args, **kwargs):
        # get the challenge instance
        instance = self.get_object()

        # check if the challenge is in 'active' status (or 'created' based on your logic)
        if instance.status != instance.Status.CREATED:
            raise ValidationError({
                "detail": "Challenges can only be updated when in 'active' status."
            })
        
        # check if the challenge's start date has passed
        if instance.date_start and instance.date_start <= timezone.now():
            raise ValidationError({
                "detail": "The challenge start time has been reached or passed, and it can no longer be updated."
            })

        return super().update(request, *args, **kwargs)
    
    #soft delete the challenge
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Block deletion if challenge is not in CREATED status (e.g., STARTED or ENDED)
        if instance.status != instance.Status.CREATED:
            return Response(
                {"error": "Deletion is not allowed after the challenge has started."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform soft delete
        instance.is_deleted = True
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChallengeLeaderboardView(generics.GenericAPIView):

    serializer_class = LeaderboardSerializer

    authentication_classes = []
    permission_classes = []

    def get(self, request, challenge_id):

        page_number = request.GET.get("page", 1)

        queryset = ParticipantScore.objects.filter(
            challenge_id=challenge_id
        ).order_by("-score", "user_id")

        paginator = Paginator(queryset, 10)

        page = paginator.get_page(page_number)

        rank = (page.number - 1) * paginator.per_page + 1

        data = []

        for participant in page.object_list:

            data.append({
                "rank": rank,
                "user_id": participant.user_id,
                "score": participant.score,
            })

            rank += 1

        serializer = self.get_serializer(data, many=True)

        return Response(serializer.data)
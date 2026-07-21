from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from ..models import Challenge
from ..serializers.challenge import ChallengeSerializer
from .permissions import IsCoach, IsChallengeCreator 
from rest_framework.exceptions import ValidationError
from django.utils import timezone

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

class ChallengeUpdateView(generics.RetrieveUpdateAPIView):

    queryset = Challenge.objects.all()

    serializer_class = ChallengeSerializer

    permission_classes = [IsCoach, IsChallengeCreator]  # only the coach can update the challenge

    lookup_field = 'challenge_id'

    def update(self, request, *args, **kwargs):
        # get the challenge instance
        instance = self.get_object()

        # check if the challenge is in 'active' status
        if instance.status != 'created':
            raise ValidationError({
                "detail": "Challenges can only be updated when in 'active' status."
            })
        
        # check if the challenge's start date has passed
        if instance.date_start and instance.date_start <= timezone.now():
            raise ValidationError({
                "detail": "The challenge start time has been reached or passed, and it can no longer be updated."
            })

        # if all checks pass, proceed with the update
        return super().update(request, *args, **kwargs)

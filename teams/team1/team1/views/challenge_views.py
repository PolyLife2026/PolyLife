from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from ..models import Challenge
from ..serializers.challenge import ChallengeSerializer
from .permissions import IsCoach

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
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny  
from .models import Challenge
from .serializers import ChallengeSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class ChallengeCreateView(generics.CreateAPIView):
    """
    POST /team1/api/challenges/
    Creates a new challenge. The request body should contain the challenge data in JSON format.
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

    authentication_classes = []  #for test purposes only
    
    permission_classes = [AllowAny]  #only for test without logging in

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from ..models import Challenge
from ..models import ParticipantChallenge
from ..serializers.challenge import ChallengeSerializer, ChallengeDetailSerializer, ChallengeListSerializer
from .permissions import IsCoach, IsChallengeCreator 
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework.views import APIView

from ..models import ParticipantScore
from ..serializers.challenge import LeaderboardSerializer

from django_filters.rest_framework import DjangoFilterBackend
from .filters import ChallengeFilter
from django.shortcuts import get_object_or_404

from ..models import UserBadge, Reward
from ..serializers.challenge import ChallengeResultSerializer
from ..services.challenge_lifecycle import (
    refresh_challenge_status,
    refresh_all_challenge_statuses,
)

# Create your views here.

class ChallengeListCreateView(generics.ListCreateAPIView):
    """
    API view to retrieve a list of active challenges or create a new challenge.

    Endpoints:
    - GET /team1/api/challenges/ : Retrieves a list of challenges that are not soft-deleted and not cancelled.
    - POST /team1/api/challenges/ : Creates a new challenge. Requires 'IsCoach' permission. 
                                    The creator's user ID is extracted from the 'X-User-Id' header.
    """
    # For testing purposes without logging in
    authentication_classes = [] 

    serializer_class = ChallengeListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChallengeFilter
    
    def get_queryset(self):
        # Exclude soft-deleted and cancelled challenges
        # NOTE: Make sure 'CANCELLED' matches your exact model Status choices
        return Challenge.objects.filter(
            is_deleted=False
        ).exclude(
            status='cancelled'
        ).order_by('-date_start')

    def get_serializer_class(self):
        # Use different serializers based on request method
        if self.request.method == 'POST':
            return ChallengeSerializer
        return ChallengeListSerializer

    def get_permissions(self):
        # Apply IsCoach permission ONLY for POST (creation)
        if self.request.method == 'POST':
            return [IsCoach()]
        # GET (list) is accessible based on your general policy (e.g., AllowAny)
        return []

    def list(self, request, *args, **kwargs):
        refresh_all_challenge_statuses()
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Get the user id from the request headers
        user_id = self.request.META.get('HTTP_X_USER_ID')
        
        if user_id:
            serializer.save(created_by=int(user_id), status=Challenge.Status.CREATED)
        else:
            raise PermissionDenied("Missing user id in headers")


class ChallengeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or soft-delete a specific challenge.

    Endpoints:
    - GET /team1/api/challenges/<challenge_id>/ : Retrieves detailed information about a specific challenge.
    - PUT/PATCH /team1/api/challenges/<challenge_id>/ : Updates the challenge. Only allowed if the challenge is in 
                                                        'CREATED' status and the start time has not passed. 
                                                        Requires 'IsCoach' and 'IsChallengeCreator' permissions.
    - DELETE /team1/api/challenges/<challenge_id>/ : Soft-deletes the challenge by setting the 'is_deleted' flag.
                                                     Only allowed if the challenge is in 'CREATED' status.
    """

    lookup_field = 'challenge_id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsCoach(), IsChallengeCreator()]

    def get_queryset(self):
        # 1. Fix soft-delete issue: Only return challenges that are not deleted
        return Challenge.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        # 2. Fix serialization issue: Use DetailSerializer only for GET requests
        if self.request.method == 'GET':
            return ChallengeDetailSerializer
        # Use default serializer for PUT, PATCH, DELETE
        return ChallengeSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        refresh_challenge_status(instance)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
    
    # soft delete the challenge
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

class ChallengeJoinView(APIView):
    """
    API view to allow a user to join a specific challenge.

    Endpoints:
    - POST /team1/api/challenges/<pk>/join/ : Registers the user as a participant in the challenge.
                                              Requires the 'X-User-Id' header for identification.
                                              The challenge must be active and not deleted.
    """
    def post(self, request, pk, format=None):
        # SCRUM-81: Read user_id from X-User-Id header
        user_id_str = request.META.get('HTTP_X_USER_ID')
        if not user_id_str:
            return Response(
                {"error": "X-User-Id header is required."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            return Response(
                {"error": "Invalid X-User-Id format."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the active challenge and refresh its status first
        challenge = get_object_or_404(Challenge, pk=pk, is_deleted=False)
        refresh_challenge_status(challenge)
        challenge.refresh_from_db()

        allowed_statuses = [
            Challenge.Status.CREATED,
            Challenge.Status.STARTED,
            "active",  # legacy status normalized on read
        ]
        if challenge.status not in allowed_statuses:
            return Response(
                {"error": f"Cannot join challenge. Current status is {challenge.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if ParticipantChallenge.objects.filter(challenge=challenge, user_id=user_id).exists():
            return Response(
                {"error": "User has already joined this challenge."},
                status=status.HTTP_409_CONFLICT
            )

        ParticipantChallenge.objects.create(
            challenge=challenge,
            user_id=user_id
        )
        
        return Response(
            {"message": "Successfully joined the challenge."}, 
            status=status.HTTP_201_CREATED
        )

    

class MyRankView(generics.GenericAPIView):
    """
    API view to retrieve the current user's rank in a specific challenge.

    Endpoints:
    - GET /team1/api/challenges/<challenge_id>/my-rank/ : Calculates and returns the rank and score 
                                                          of the user identified by the 'X-User-Id' header.
    """

    serializer_class = LeaderboardSerializer

    authentication_classes = []
    permission_classes = []

    def get(self, request, challenge_id):

        user_id = request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers.")

        try:
            participant = ParticipantScore.objects.get(
                challenge_id=challenge_id,
                user_id=user_id,
            )
        except ParticipantScore.DoesNotExist:
            return Response(
                {"detail": "Participant not found."},
                status=404,
            )

        rank = (
                ParticipantScore.objects.filter(
                    challenge_id=challenge_id,
                    score__gt=participant.score,
                ).count()
                + 1
        )

        serializer = self.get_serializer({
            "rank": rank,
            "user_id": participant.user_id,
            "score": participant.score,
        })

        return Response(serializer.data)


class ChallengeLeaderboardView(generics.GenericAPIView):
    """
    API view to retrieve a paginated leaderboard for a specific challenge.

    Endpoints:
    - GET /team1/api/challenges/<challenge_id>/leaderboard/ : Returns a list of participants ordered 
                                                               by their score in descending order.
    """

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


class MyChallengeResultView(generics.GenericAPIView):
    """
    API view to retrieve the participant's final result after the challenge ends.

    Endpoints:
    - GET /team1/api/challenges/<challenge_id>/my-results/ : Returns the total score, final rank, 
                                                              earned badges, and rewards for the user 
                                                              identified by the 'X-User-Id' header.
                                                              The challenge status must be 'ENDED'.
    """

    serializer_class = ChallengeResultSerializer

    authentication_classes = []
    permission_classes = []

    def get(self, request, challenge_id):

        user_id = request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers.")

        try:
            challenge = Challenge.objects.get(
                challenge_id=challenge_id,
                is_deleted=False,
            )
        except Challenge.DoesNotExist:
            return Response(
                {"detail": "Challenge not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if challenge.status != Challenge.Status.ENDED:
            return Response(
                {"detail": "Challenge is not completed yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            participant = ParticipantChallenge.objects.get(
                challenge=challenge,
                user_id=user_id,
            )

            score = ParticipantScore.objects.get(
                challenge=challenge,
                user_id=user_id,
            )

        except (
            ParticipantChallenge.DoesNotExist,
            ParticipantScore.DoesNotExist,
        ):
            return Response(
                {"detail": "Participant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_badges = (
            UserBadge.objects
            .filter(
                challenge=challenge,
                user_id=user_id,
            )
            .select_related("reward")
        )

        badges = [
            badge.reward.badge_type
            for badge in user_badges
        ]

        rewards = [
            badge.reward.description
            for badge in user_badges
            if badge.reward.description
        ]

        serializer = self.get_serializer({
            "final_rank": participant.final_rank,
            "total_score": score.score,
            "badges": badges,
            "rewards": rewards,
        })

        return Response(serializer.data)

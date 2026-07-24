"""
URL configuration for the team1 app.

This module defines the URL routing for the PolyLife microservice, covering
endpoints for Challenges, Activities, and Competitions. It maps each API 
endpoint to its corresponding class-based view.
"""

from django.urls import path

from . import views
from .views.activity_views import ActivityCreateView, ActivityUpdateView
from .views.challenge_views import (
    ChallengeListCreateView,
    ChallengeDetailView,
    ChallengeLeaderboardView,
    ChallengeJoinView,
    MyRankView,
    MyChallengeResultView,
)
from .views.competition_views import (
    CompetitionListCreateView,
    CompetitionDetailView,
    CompetitionJoinView,
    CompetitionResultView,
    CompetitionLeaderboardView,
    CompetitionFinalRankingsView,
    CompetitionStartView,
    CompetitionFinishView,
)

app_name = "team1"

urlpatterns = [
    # ==========================================
    # Challenge Endpoints
    # ==========================================
    
    # GET: Retrieve a list of active challenges.
    # POST: Create a new challenge (requires Coach permissions).
    path(
        "api/challenges/",
        ChallengeListCreateView.as_view(),
        name="challenge-list-create",
    ),
    
    # GET: Retrieve detailed information about a specific challenge.
    # PUT/PATCH: Update challenge details (if not started).
    # DELETE: Soft-delete the challenge.
    path(
        "api/challenges/<int:challenge_id>/",
        ChallengeDetailView.as_view(),
        name="challenge-detail",
    ),
    
    # POST: Register the current user (from X-User-Id) to a specific challenge.
    path(
        "api/challenges/<int:pk>/join/",
        ChallengeJoinView.as_view(),
        name="challenge-join",
    ),
    
    # GET: Retrieve the paginated leaderboard for a specific challenge.
    path(
        "api/challenges/<int:challenge_id>/leaderboard/",
        ChallengeLeaderboardView.as_view(),
        name="challenge-leaderboard",
    ),
    
    # GET: Retrieve the current user's specific rank and score in a challenge.
    path(
        "api/challenges/<int:challenge_id>/my-rank/",
        MyRankView.as_view(),
        name="my-rank",
    ),
    
    # GET: Retrieve the current user's final results, badges, and rewards 
    # after a challenge has ENDED.
    path(
        "api/challenges/<int:challenge_id>/my-results/",
        MyChallengeResultView.as_view(),
        name="my-results",
    ),

    # ==========================================
    # Activity Endpoints
    # ==========================================
    
    # POST: Submit a new activity for an active challenge/competition.
    path(
        "api/activities/",
        ActivityCreateView.as_view(),
        name="activity-create",
    ),
    
    # PUT/PATCH: Update an existing activity submission.
    # DELETE: Remove an activity submission.
    path(
        "api/activities/<int:activity_id>/",
        ActivityUpdateView.as_view(),
        name="activity-update",
    ),

    # ==========================================
    # Competition Endpoints
    # ==========================================
    
    # GET: Retrieve a list of competitions.
    # POST: Create a new competition.
    path(
        "api/competitions/",
        CompetitionListCreateView.as_view(),
        name="competition-list-create",
    ),
    
    # GET: Retrieve details for a specific competition.
    # PUT/PATCH/DELETE: Update or soft-delete a competition.
    path(
        "api/competitions/<int:competition_id>/",
        CompetitionDetailView.as_view(),
        name="competition-detail",
    ),
    
    # POST: Register the current user to participate in a competition.
    path(
        "api/competitions/<int:pk>/join/",
        CompetitionJoinView.as_view(),
        name="competition-join",
    ),
    
    # POST: Manually start a competition (updates status to STARTED).
    path(
        "api/competitions/<int:pk>/start/",
        CompetitionStartView.as_view(),
        name="competition-start",
    ),
    
    # POST: Manually finish/end a competition (updates status to ENDED).
    path(
        "api/competitions/<int:pk>/finish/",
        CompetitionFinishView.as_view(),
        name="competition-finish",
    ),
    
    # GET: Retrieve the current user's specific result and stats in a competition.
    path(
        "api/competitions/<int:pk>/results/",
        CompetitionResultView.as_view(),
        name="competition-results",
    ),
    
    # GET: Retrieve the current active leaderboard for a running competition.
    path(
        "api/competitions/<int:pk>/leaderboard/",
        CompetitionLeaderboardView.as_view(),
        name="competition-leaderboard",
    ),
    
    # GET: Retrieve the finalized overall rankings once the competition has ended.
    path(
        "api/competitions/<int:pk>/final-rankings/",
        CompetitionFinalRankingsView.as_view(),
        name="competition-final-rankings",
    ),
]

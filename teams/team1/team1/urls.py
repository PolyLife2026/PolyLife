from django.urls import path

from . import views
from .views.activity_views import ActivityCreateView, ActivityUpdateView
from .views.challenge_views import ChallengeCreateView, ChallengeDetailView, ChallengeLeaderboardView
from .views.competition_views import (
    CompetitionCreateView,
    CompetitionJoinView,
)

app_name = "team1"

urlpatterns = [
    # path("api/whoami", views.whoami, name="whoami"),

    # Challenge
    path(
        "api/challenges/",
        ChallengeCreateView.as_view(),
        name="challenge-create",
    ),
    path(
        "api/challenges/<int:challenge_id>/",
        ChallengeDetailView.as_view(),
        name="challenge-detail",
    ),

    # Activity
    path(
        "api/activities/",
        ActivityCreateView.as_view(),
        name="activity-create",
    ),
    path(
        "api/activities/<int:activity_id>/",
        ActivityUpdateView.as_view(),
        name="activity-update",
    ),

    # Competition
    path(
        "api/competitions/",
        CompetitionCreateView.as_view(),
        name="competition-create",
    ),
    path(
        "api/competitions/<int:pk>/join/",
        CompetitionJoinView.as_view(),
        name="competition-join",
    ),
    path(
        "api/challenges/<int:challenge_id>/leaderboard/",
        ChallengeLeaderboardView.as_view(),
        name="challenge-leaderboard",
    ),
]
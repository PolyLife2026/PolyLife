from django.urls import path

from . import views
from .views.activity_views import ActivityCreateView, ActivityUpdateView
from .views.challenge_views import (
    ChallengeListCreateView,
    ChallengeDetailView,
    ChallengeLeaderboardView,
    ChallengeJoinView,
    MyRankView,
    MyChallengeResultView,   # <-- اضافه شد
)
from .views.competition_views import (
    CompetitionCreateView,
    CompetitionJoinView,
    CompetitionResultView,
    CompetitionLeaderboardView,
    CompetitionFinalRankingsView,
)

app_name = "team1"

urlpatterns = [
    # path("api/whoami", views.whoami, name="whoami"),

    # Challenge
    path(
        "api/challenges/",
        ChallengeListCreateView.as_view(),
        name="challenge-list-create",
    ),
    path(
        "api/challenges/<int:challenge_id>/",
        ChallengeDetailView.as_view(),
        name="challenge-detail",
    ),
    path(
        "api/challenges/<int:pk>/join/",
        ChallengeJoinView.as_view(),
        name="challenge-join",
    ),
    path(
        "api/challenges/<int:challenge_id>/leaderboard/",
        ChallengeLeaderboardView.as_view(),
        name="challenge-leaderboard",
    ),
    path(
        "api/challenges/<int:challenge_id>/my-rank/",
        MyRankView.as_view(),
        name="my-rank",
    ),
    path(
        "api/challenges/<int:challenge_id>/my-results/",
        MyChallengeResultView.as_view(),
        name="my-results",
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
        "api/competitions/<int:pk>/results/",
        CompetitionResultView.as_view(),
        name="competition-results",
    ),
    path(
        "api/competitions/<int:pk>/leaderboard/",
        CompetitionLeaderboardView.as_view(),
        name="competition-leaderboard",
    ),
    path(
        "api/competitions/<int:pk>/final-rankings/",
        CompetitionFinalRankingsView.as_view(),
        name="competition-final-rankings",
    ),
]
from django.urls import path
from . import views
from .views.challenge_views import ChallengeCreateView
from .views.activity_views import ActivityCreateView
app_name = "team1"

urlpatterns = [
    #path("api/whoami", views.whoami, name="whoami"),
    # Add your team's routes here.
    path('api/challenges/', ChallengeCreateView.as_view(), name='challenge-create'),
    path('api/activities/', ActivityCreateView.as_view(), name='activity-create'),
]

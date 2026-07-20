from django.urls import path

from . import views
from .views import ChallengeCreateView


app_name = "team1"

urlpatterns = [
    path("api/whoami", views.whoami, name="whoami"),
    # Add your team's routes here.
    path('api/challenges/', ChallengeCreateView.as_view(), name='challenge-create'),

]

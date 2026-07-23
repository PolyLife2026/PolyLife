from django.urls import path

from . import views

app_name = "team1"

urlpatterns = [
    path("api/whoami", views.whoami, name="whoami"),
    
    # Competition endpoints
    path("api/competitions", views.competitions_list, name="competitions_list"),
    path("api/competitions/<int:competition_id>", views.competition_detail, name="competition_detail"),
    path("api/competitions/create", views.create_competition, name="create_competition"),
    
    # Activity endpoints
    path("api/competitions/<int:competition_id>/activity", views.register_activity, name="register_activity"),
    path("api/competitions/<int:competition_id>/activity/<int:activity_id>", views.delete_activity, name="delete_activity"),
    path("api/competitions/<int:competition_id>/my-activities", views.user_activities, name="user_activities"),
    
    # Leaderboard endpoints
    path("api/competitions/<int:competition_id>/leaderboard", views.competition_leaderboard, name="competition_leaderboard"),
]

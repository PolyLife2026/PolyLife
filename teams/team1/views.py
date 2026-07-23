from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import F, Sum, Count
import json
from .models import Competition, Activity, Leaderboard


def whoami(request):
    """
    Example endpoint.

    The gateway already authenticated the user against the core and injected
    these headers — your team never decodes JWTs. Just read them.
    """
    return JsonResponse(
        {
            "team": "team1",
            "user_id": request.headers.get("X-User-Id", ""),
            "username": request.headers.get("X-User-Username", ""),
        }
    )


def get_user_info(request):
    """Extract authenticated user info from headers."""
    return {
        "user_id": int(request.headers.get("X-User-Id", "0")),
        "username": request.headers.get("X-User-Username", ""),
    }


@require_http_methods(["GET"])
def competitions_list(request):
    """
    GET /api/competitions
    List all competitions with automatic status update.
    """
    competitions = Competition.objects.all()
    
    # Update status for all competitions
    for competition in competitions:
        competition.update_status()
    
    data = []
    for comp in competitions:
        data.append({
            "id": comp.id,
            "title": comp.title,
            "description": comp.description,
            "start_date": comp.start_date.isoformat(),
            "end_date": comp.end_date.isoformat(),
            "status": comp.status,
            "created_by": comp.created_by,
            "created_at": comp.created_at.isoformat(),
        })
    
    return JsonResponse({"competitions": data})


@require_http_methods(["GET"])
def competition_detail(request, competition_id):
    """
    GET /api/competitions/<id>
    Get details of a specific competition.
    """
    try:
        competition = Competition.objects.get(id=competition_id)
        competition.update_status()
        
        return JsonResponse({
            "id": competition.id,
            "title": competition.title,
            "description": competition.description,
            "start_date": competition.start_date.isoformat(),
            "end_date": competition.end_date.isoformat(),
            "status": competition.status,
            "created_by": competition.created_by,
            "created_at": competition.created_at.isoformat(),
            "updated_at": competition.updated_at.isoformat(),
        })
    except Competition.DoesNotExist:
        return JsonResponse({"error": "Competition not found"}, status=404)


@require_http_methods(["POST"])
def create_competition(request):
    """
    POST /api/competitions
    Create a new competition (coach only).
    Requires: title, start_date, end_date, description (optional)
    """
    try:
        user = get_user_info(request)
        data = json.loads(request.body)
        
        competition = Competition.objects.create(
            title=data.get("title"),
            description=data.get("description", ""),
            start_date=timezone.datetime.fromisoformat(data.get("start_date")),
            end_date=timezone.datetime.fromisoformat(data.get("end_date")),
            created_by=user["user_id"],
        )
        
        # Create empty leaderboard
        Leaderboard.objects.create(competition=competition)
        
        return JsonResponse({
            "id": competition.id,
            "title": competition.title,
            "status": competition.status,
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["POST"])
def register_activity(request, competition_id):
    """
    POST /api/competitions/<id>/activity
    Register an activity for the current user in a competition.
    Participant can register their own activity.
    
    Body:
    {
        "activity_type": "run|walk|swim|cycle|gym|sports|other",
        "distance": 5.5,  # optional, in km
        "duration": 45,   # optional, in minutes
        "calories_burned": 400,  # optional
        "notes": "Great workout!",  # optional
        "activity_date": "2024-01-15T10:30:00"  # ISO format
    }
    """
    try:
        user = get_user_info(request)
        
        if not user["user_id"]:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        competition = Competition.objects.get(id=competition_id)
        competition.update_status()
        
        # Check if competition is active
        if competition.status not in ["started", "pending"]:
            if competition.status == "ended":
                return JsonResponse(
                    {"error": "Competition has ended"},
                    status=400
                )
        
        data = json.loads(request.body)
        
        activity = Activity.objects.create(
            competition=competition,
            user_id=user["user_id"],
            activity_type=data.get("activity_type"),
            distance=data.get("distance"),
            duration=data.get("duration"),
            calories_burned=data.get("calories_burned"),
            notes=data.get("notes", ""),
            activity_date=timezone.datetime.fromisoformat(data.get("activity_date")),
        )
        
        # Update or create leaderboard entry
        leaderboard, created = Leaderboard.objects.get_or_create(
            competition=competition,
            user_id=user["user_id"],
            defaults={"username": user["username"]}
        )
        
        if not created:
            leaderboard.username = user["username"]
        
        # Recalculate leaderboard stats
        stats = Activity.objects.filter(
            competition=competition,
            user_id=user["user_id"]
        ).aggregate(
            total_activities=Count("id"),
            total_distance=Sum("distance"),
            total_duration=Sum("duration"),
            total_calories=Sum("calories_burned"),
            last_activity=Sum("activity_date")  # This won't work as intended
        )
        
        leaderboard.total_activities = stats["total_activities"] or 0
        leaderboard.total_distance = stats["total_distance"] or 0
        leaderboard.total_duration = stats["total_duration"] or 0
        leaderboard.total_calories = stats["total_calories"] or 0
        
        last_activity = Activity.objects.filter(
            competition=competition,
            user_id=user["user_id"]
        ).latest("activity_date")
        leaderboard.last_activity_date = last_activity.activity_date
        
        leaderboard.save()
        
        # Update rankings for all participants
        update_competition_rankings(competition)
        
        return JsonResponse({
            "id": activity.id,
            "message": "Activity registered successfully",
            "activity": {
                "activity_type": activity.activity_type,
                "distance": activity.distance,
                "duration": activity.duration,
                "calories_burned": activity.calories_burned,
            }
        }, status=201)
    except Competition.DoesNotExist:
        return JsonResponse({"error": "Competition not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def update_competition_rankings(competition):
    """
    Update rankings for all participants in a competition.
    Ordered by: total_distance DESC, then total_activities DESC
    """
    leaderboards = Leaderboard.objects.filter(
        competition=competition
    ).order_by("-total_distance", "-total_activities")
    
    for rank, leaderboard in enumerate(leaderboards, 1):
        leaderboard.rank = rank
        leaderboard.save()


@require_http_methods(["GET"])
def competition_leaderboard(request, competition_id):
    """
    GET /api/competitions/<id>/leaderboard
    Get the leaderboard for a competition.
    """
    try:
        competition = Competition.objects.get(id=competition_id)
        competition.update_status()
        
        leaderboards = Leaderboard.objects.filter(
            competition=competition
        ).order_by("rank")
        
        data = []
        for entry in leaderboards:
            data.append({
                "rank": entry.rank,
                "user_id": entry.user_id,
                "username": entry.username,
                "total_activities": entry.total_activities,
                "total_distance": float(entry.total_distance),
                "total_duration": entry.total_duration,
                "total_calories": entry.total_calories,
                "last_activity_date": entry.last_activity_date.isoformat() if entry.last_activity_date else None,
            })
        
        return JsonResponse({
            "competition": {
                "id": competition.id,
                "title": competition.title,
                "status": competition.status,
            },
            "leaderboard": data
        })
    except Competition.DoesNotExist:
        return JsonResponse({"error": "Competition not found"}, status=404)


@require_http_methods(["GET"])
def user_activities(request, competition_id):
    """
    GET /api/competitions/<id>/my-activities
    Get all activities of the current user in a competition.
    """
    try:
        user = get_user_info(request)
        competition = Competition.objects.get(id=competition_id)
        
        activities = Activity.objects.filter(
            competition=competition,
            user_id=user["user_id"]
        ).order_by("-activity_date")
        
        data = []
        for activity in activities:
            data.append({
                "id": activity.id,
                "activity_type": activity.activity_type,
                "distance": activity.distance,
                "duration": activity.duration,
                "calories_burned": activity.calories_burned,
                "notes": activity.notes,
                "activity_date": activity.activity_date.isoformat(),
                "created_at": activity.created_at.isoformat(),
            })
        
        return JsonResponse({
            "user_id": user["user_id"],
            "username": user["username"],
            "competition": competition.title,
            "activities": data
        })
    except Competition.DoesNotExist:
        return JsonResponse({"error": "Competition not found"}, status=404)


@require_http_methods(["DELETE"])
def delete_activity(request, competition_id, activity_id):
    """
    DELETE /api/competitions/<id>/activity/<activity_id>
    Delete an activity (user can only delete their own).
    """
    try:
        user = get_user_info(request)
        activity = Activity.objects.get(
            id=activity_id,
            competition_id=competition_id,
            user_id=user["user_id"]
        )
        
        competition = activity.competition
        activity.delete()
        
        # Update leaderboard
        leaderboard = Leaderboard.objects.get(
            competition=competition,
            user_id=user["user_id"]
        )
        
        stats = Activity.objects.filter(
            competition=competition,
            user_id=user["user_id"]
        ).aggregate(
            total_activities=Count("id"),
            total_distance=Sum("distance"),
            total_duration=Sum("duration"),
            total_calories=Sum("calories_burned"),
        )
        
        leaderboard.total_activities = stats["total_activities"] or 0
        leaderboard.total_distance = stats["total_distance"] or 0
        leaderboard.total_duration = stats["total_duration"] or 0
        leaderboard.total_calories = stats["total_calories"] or 0
        leaderboard.save()
        
        # Update rankings
        update_competition_rankings(competition)
        
        return JsonResponse({"message": "Activity deleted successfully"})
    except Activity.DoesNotExist:
        return JsonResponse({"error": "Activity not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

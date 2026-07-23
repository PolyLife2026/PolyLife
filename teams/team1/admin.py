from django.contrib import admin
from .models import Competition, Activity, Leaderboard


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date", "created_by", "created_at")
    list_filter = ("status", "created_at", "start_date")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic Info", {"fields": ("title", "description")}),
        ("Schedule", {"fields": ("start_date", "end_date")}),
        ("Status", {"fields": ("status",)}),
        ("Metadata", {"fields": ("created_by", "created_at", "updated_at")}),
    )


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("competition", "user_id", "activity_type", "distance", "duration", "activity_date")
    list_filter = ("activity_type", "competition", "activity_date")
    search_fields = ("user_id", "notes")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Participation", {"fields": ("competition", "user_id")}),
        ("Activity Details", {"fields": ("activity_type", "distance", "duration", "calories_burned", "activity_date")}),
        ("Notes", {"fields": ("notes",)}),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ("rank", "username", "competition", "total_distance", "total_activities", "total_calories")
    list_filter = ("competition", "updated_at")
    search_fields = ("username", "user_id")
    readonly_fields = ("updated_at", "competition", "user_id")
    fieldsets = (
        ("Participation", {"fields": ("competition", "user_id", "username")}),
        ("Statistics", {"fields": ("total_activities", "total_distance", "total_duration", "total_calories")}),
        ("Ranking", {"fields": ("rank", "last_activity_date")}),
        ("Metadata", {"fields": ("updated_at",)}),
    )

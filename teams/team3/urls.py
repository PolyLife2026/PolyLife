from django.urls import path

from . import views

app_name = "team3"

urlpatterns = [
    path("whoami", views.whoami, name="whoami"),

    path("health-profile/", views.HealthProfileView.as_view(), name="health-profile"),
    path("food-items/search/", views.FoodSearchView.as_view(), name="food-search"),
    path("search-history/", views.SearchHistoryView.as_view(), name="search-history"),
    path("favorites/", views.FavoriteFoodView.as_view(), name="favorites"),
    path("favorites/<uuid:pk>/", views.FavoriteFoodDetailView.as_view(), name="favorite-detail"),
    path("error-reports/", views.ErrorReportView.as_view(), name="error-reports"),

    path("meal-logs/", views.MealLogView.as_view(), name="meal-logs"),
    path("meal-logs/items/<uuid:pk>/", views.MealLogItemDetailView.as_view(), name="meal-log-item-detail"),
    path("meal-logs/copy/", views.CopyMealView.as_view(), name="meal-log-copy"),
    path("meal-logs/quick-add/", views.QuickAddCalorieView.as_view(), name="meal-log-quick-add"),
    path("dashboard/daily/", views.DailyDashboardView.as_view(), name="dashboard-daily"),
    path("dashboard/weekly/", views.WeeklyReportView.as_view(), name="dashboard-weekly"),
    path("dashboard/streak/", views.StreakView.as_view(), name="dashboard-streak"),
]

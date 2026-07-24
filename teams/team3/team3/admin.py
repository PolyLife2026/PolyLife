from django.contrib import admin
from .models import (
    HealthProfile, FoodItem, FoodUnit, MealLog, MealLogItem,
    FavoriteFood, SearchHistory, ErrorReport, DailyStreak,
)

admin.site.register(HealthProfile)
admin.site.register(FoodItem)
admin.site.register(FoodUnit)
admin.site.register(MealLog)
admin.site.register(MealLogItem)
admin.site.register(FavoriteFood)
admin.site.register(SearchHistory)
admin.site.register(ErrorReport)
admin.site.register(DailyStreak)

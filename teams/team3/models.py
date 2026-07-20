import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class HealthProfile(BaseModel):
    user_id = models.CharField(max_length=255, unique=True, db_index=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    goal = models.CharField(max_length=50, null=True, blank=True)

class FoodItem(BaseModel):
    name = models.CharField(max_length=150, db_index=True)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=6, decimal_places=2)
    carbs = models.DecimalField(max_digits=6, decimal_places=2)
    fat = models.DecimalField(max_digits=6, decimal_places=2)

class MealLog(BaseModel):
    user_id = models.CharField(max_length=255, db_index=True)
    log_date = models.DateField()
    total_calories = models.IntegerField(default=0)

class MealLogItem(BaseModel):
    meal_log = models.ForeignKey(MealLog, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    quantity_grams = models.DecimalField(max_digits=6, decimal_places=2)
    meal_type = models.CharField(max_length=50)

class FavoriteFood(BaseModel):
    user_id = models.CharField(max_length=255, db_index=True)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)

class SearchHistory(BaseModel):
    user_id = models.CharField(max_length=255, db_index=True)
    search_query = models.CharField(max_length=255)

class ErrorReport(BaseModel):
    user_id = models.CharField(max_length=255)
    error_message = models.TextField()
    stack_trace = models.TextField(null=True, blank=True)

class DailyStreak(BaseModel):
    user_id = models.CharField(max_length=255, unique=True, db_index=True)
    streak_count = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
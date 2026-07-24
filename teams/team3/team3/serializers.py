from rest_framework import serializers
from .models import (
    HealthProfile, FoodItem, FoodUnit, MealLog, MealLogItem,
    FavoriteFood, SearchHistory, ErrorReport, DailyStreak,
)


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = ["id", "user_id", "height", "weight", "age", "gender", "goal", "created_at", "updated_at"]
        read_only_fields = ["id", "user_id", "created_at", "updated_at"]


class FoodUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodUnit
        fields = ["id", "unit_name", "grams_per_unit"]


class FoodItemSerializer(serializers.ModelSerializer):
    units = FoodUnitSerializer(many=True, read_only=True)
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = [
            "id", "name", "category", "category_label",
            "calories", "protein", "carbs", "fat", "units", "is_favorite",
        ]

    def get_is_favorite(self, obj):
        favorite_ids = self.context.get("favorite_food_ids")
        if favorite_ids is None:
            return None
        return obj.id in favorite_ids


class MealLogItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    food_item_id = serializers.PrimaryKeyRelatedField(
        queryset=FoodItem.objects.filter(is_deleted=False), source="food_item", write_only=True
    )
    consumed_calories = serializers.SerializerMethodField()

    class Meta:
        model = MealLogItem
        fields = [
            "id", "food_item", "food_item_id", "quantity_grams",
            "unit_name", "unit_quantity", "meal_type", "note", "consumed_calories", "created_at",
        ]
        read_only_fields = ["id", "quantity_grams", "unit_name", "unit_quantity", "created_at"]

    def get_consumed_calories(self, obj):
        return round(float(obj.food_item.calories) * float(obj.quantity_grams) / 100, 2)


class MealLogSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = MealLog
        fields = ["id", "log_date", "total_calories", "items"]

    def get_items(self, obj):
        active_items = obj.items.filter(is_deleted=False)
        return MealLogItemSerializer(active_items, many=True).data


class FavoriteFoodSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)
    food_item_id = serializers.PrimaryKeyRelatedField(
        queryset=FoodItem.objects.filter(is_deleted=False), source="food_item", write_only=True
    )

    class Meta:
        model = FavoriteFood
        fields = ["id", "food_item", "food_item_id", "created_at"]
        read_only_fields = ["id", "created_at"]


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ["id", "search_query", "created_at"]
        read_only_fields = ["id", "created_at"]


class ErrorReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorReport
        fields = ["id", "error_message", "stack_trace", "created_at"]
        read_only_fields = ["id", "created_at"]


class DailyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStreak
        fields = ["id", "streak_count", "last_active_date"]

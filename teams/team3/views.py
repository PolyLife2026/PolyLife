import datetime
from django.http import JsonResponse
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    HealthProfile, FoodItem, MealLog, MealLogItem,
    FavoriteFood, SearchHistory, ErrorReport, DailyStreak,
)
from .serializers import (
    HealthProfileSerializer, FoodItemSerializer, MealLogSerializer, MealLogItemSerializer,
    FavoriteFoodSerializer, SearchHistorySerializer, ErrorReportSerializer, DailyStreakSerializer,
)


def whoami(request):
    return JsonResponse({
        "team": "team3",
        "user_id": request.headers.get("X-User-Id", ""),
        "username": request.headers.get("X-User-Username", ""),
    })


def calculate_health_metrics(profile):
    """Return a dict with bmi / bmr / target_calories, or {} if data is incomplete."""
    if not (profile.height and profile.weight and profile.age and profile.gender):
        return {}

    height_cm = float(profile.height)
    weight_kg = float(profile.weight)
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 2)

    if profile.gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * profile.age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * profile.age - 161

    target = bmr * 1.4
    if profile.goal == "lose":
        target -= 500
    elif profile.goal == "gain":
        target += 500

    return {"bmi": bmi, "bmr": round(bmr, 2), "target_calories": int(target)}


def get_target_calories(user_id, fallback=2000):
    profile = HealthProfile.objects.filter(user_id=user_id, is_deleted=False).first()
    if not profile:
        return fallback
    metrics = calculate_health_metrics(profile)
    return metrics.get("target_calories", fallback)


def recompute_meal_log_total(meal_log):
    total = 0
    for item in meal_log.items.filter(is_deleted=False).select_related("food_item"):
        total += float(item.food_item.calories) * float(item.quantity_grams) / 100
    meal_log.total_calories = round(total)
    meal_log.save(update_fields=["total_calories", "updated_at"])
    return meal_log.total_calories


def update_daily_streak(user_id, log_date, total_calories, target_calories):
    """A day 'counts' if the user logged something and stayed within ~105% of target."""
    streak, _ = DailyStreak.objects.get_or_create(user_id=user_id)
    counts_today = 0 < total_calories <= target_calories * 1.05

    if streak.last_active_date == log_date:
        pass 
    elif streak.last_active_date == log_date - datetime.timedelta(days=1) and counts_today:
        streak.streak_count += 1
        streak.last_active_date = log_date
    elif counts_today:
        streak.streak_count = 1
        streak.last_active_date = log_date
    else:
        streak.streak_count = 0
        streak.last_active_date = log_date

    streak.save()
    return streak


def get_quick_add_food_item():
    item, _ = FoodItem.objects.get_or_create(
        name="Quick Add (manual calorie entry)",
        defaults={"calories": 100, "protein": 0, "carbs": 0, "fat": 0},
    )
    return item



class HealthProfileView(APIView):
    def get(self, request):
        profile = HealthProfile.objects.filter(user_id=request.user_id, is_deleted=False).first()
        if not profile:
            return Response({"detail": "پروفایل سلامتی هنوز ثبت نشده."}, status=status.HTTP_404_NOT_FOUND)
        data = HealthProfileSerializer(profile).data
        data.update(calculate_health_metrics(profile))
        return Response(data)

    def post(self, request):
        data = request.data
        profile, _ = HealthProfile.objects.update_or_create(
            user_id=request.user_id,
            defaults={
                "height": data.get("height"),
                "weight": data.get("weight"),
                "age": data.get("age"),
                "gender": data.get("gender"),
                "goal": data.get("goal"),
                "is_deleted": False,
            },
        )
        payload = HealthProfileSerializer(profile).data
        payload.update(calculate_health_metrics(profile))
        return Response(payload, status=status.HTTP_200_OK)


class FoodSearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        qs = FoodItem.objects.filter(is_deleted=False)

        if q:
            qs = qs.filter(name__icontains=q)
            if request.user_id:
                SearchHistory.objects.create(user_id=request.user_id, search_query=q)

        results = list(qs[:20])

        if q and not results and len(q) > 3:
            results = list(FoodItem.objects.filter(is_deleted=False, name__icontains=q[:3])[:20])

        return Response(FoodItemSerializer(results, many=True).data)


class SearchHistoryView(APIView):
    def get(self, request):
        history = SearchHistory.objects.filter(
            user_id=request.user_id, is_deleted=False
        ).order_by("-created_at")[:10]
        return Response(SearchHistorySerializer(history, many=True).data)

    def delete(self, request):
        SearchHistory.objects.filter(user_id=request.user_id).update(is_deleted=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteFoodView(APIView):
    def get(self, request):
        favorites = FavoriteFood.objects.filter(user_id=request.user_id, is_deleted=False)
        return Response(FavoriteFoodSerializer(favorites, many=True).data)

    def post(self, request):
        serializer = FavoriteFoodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        favorite, created = FavoriteFood.objects.get_or_create(
            user_id=request.user_id,
            food_item=serializer.validated_data["food_item"],
        )
        if not created and favorite.is_deleted:
            favorite.is_deleted = False
            favorite.save()
        return Response(FavoriteFoodSerializer(favorite).data, status=status.HTTP_201_CREATED)


class FavoriteFoodDetailView(APIView):
    def delete(self, request, pk):
        favorite = FavoriteFood.objects.filter(id=pk, user_id=request.user_id).first()
        if not favorite:
            return Response(status=status.HTTP_404_NOT_FOUND)
        favorite.is_deleted = True
        favorite.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ErrorReportView(APIView):
    def post(self, request):
        serializer = ErrorReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ErrorReport.objects.create(
            user_id=request.user_id,
            error_message=serializer.validated_data["error_message"],
            stack_trace=serializer.validated_data.get("stack_trace", ""),
        )
        return Response(ErrorReportSerializer(report).data, status=status.HTTP_201_CREATED)



class MealLogView(APIView):
    def get(self, request):
        log_date_str = request.query_params.get("date", str(datetime.date.today()))
        log_date = datetime.date.fromisoformat(log_date_str)
        meal_log = MealLog.objects.filter(
            user_id=request.user_id, log_date=log_date, is_deleted=False
        ).first()
        if not meal_log:
            return Response({"log_date": str(log_date), "total_calories": 0, "items": []})
        return Response(MealLogSerializer(meal_log).data)

    def post(self, request):
        data = request.data
        log_date_str = data.get("log_date", str(datetime.date.today()))
        log_date = datetime.date.fromisoformat(log_date_str)

        meal_log, _ = MealLog.objects.get_or_create(
            user_id=request.user_id, log_date=log_date, is_deleted=False,
            defaults={"total_calories": 0},
        )

        item = MealLogItem.objects.create(
            meal_log=meal_log,
            food_item_id=data["food_item_id"],
            quantity_grams=data["quantity_grams"],
            meal_type=data.get("meal_type", "snack"),
        )

        total = recompute_meal_log_total(meal_log)
        target = get_target_calories(request.user_id)
        update_daily_streak(request.user_id, log_date, total, target)

        return Response(MealLogItemSerializer(item).data, status=status.HTTP_201_CREATED)


class MealLogItemDetailView(APIView):
    def patch(self, request, pk):
        item = MealLogItem.objects.filter(id=pk, meal_log__user_id=request.user_id).first()
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if "quantity_grams" in request.data:
            item.quantity_grams = request.data["quantity_grams"]
        if "meal_type" in request.data:
            item.meal_type = request.data["meal_type"]
        item.save()

        total = recompute_meal_log_total(item.meal_log)
        target = get_target_calories(request.user_id)
        update_daily_streak(request.user_id, item.meal_log.log_date, total, target)

        return Response(MealLogItemSerializer(item).data)

    def delete(self, request, pk):
        item = MealLogItem.objects.filter(id=pk, meal_log__user_id=request.user_id).first()
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)

        item.is_deleted = True
        item.save()

        total = recompute_meal_log_total(item.meal_log)
        target = get_target_calories(request.user_id)
        update_daily_streak(request.user_id, item.meal_log.log_date, total, target)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CopyMealView(APIView):

    def post(self, request):
        from_date = datetime.date.fromisoformat(request.data["from_date"])
        to_date = datetime.date.fromisoformat(request.data.get("to_date", str(datetime.date.today())))

        source_log = MealLog.objects.filter(
            user_id=request.user_id, log_date=from_date, is_deleted=False
        ).first()
        if not source_log:
            return Response({"detail": "برای تاریخ مبدأ وعده‌ای ثبت نشده."}, status=status.HTTP_404_NOT_FOUND)

        target_log, _ = MealLog.objects.get_or_create(
            user_id=request.user_id, log_date=to_date, is_deleted=False,
            defaults={"total_calories": 0},
        )

        for source_item in source_log.items.filter(is_deleted=False):
            MealLogItem.objects.create(
                meal_log=target_log,
                food_item=source_item.food_item,
                quantity_grams=source_item.quantity_grams,
                meal_type=source_item.meal_type,
            )

        total = recompute_meal_log_total(target_log)
        target_cal = get_target_calories(request.user_id)
        update_daily_streak(request.user_id, to_date, total, target_cal)

        return Response(MealLogSerializer(target_log).data, status=status.HTTP_201_CREATED)


class QuickAddCalorieView(APIView):
    """Log a raw calorie amount without picking a specific food (see get_quick_add_food_item)."""

    def post(self, request):
        data = request.data
        log_date_str = data.get("log_date", str(datetime.date.today()))
        log_date = datetime.date.fromisoformat(log_date_str)
        calories = float(data["calories"])

        meal_log, _ = MealLog.objects.get_or_create(
            user_id=request.user_id, log_date=log_date, is_deleted=False,
            defaults={"total_calories": 0},
        )

        quick_food = get_quick_add_food_item()
        item = MealLogItem.objects.create(
            meal_log=meal_log,
            food_item=quick_food,
            quantity_grams=calories, 
            meal_type=data.get("meal_type", "snack"),
        )

        total = recompute_meal_log_total(meal_log)
        target = get_target_calories(request.user_id)
        update_daily_streak(request.user_id, log_date, total, target)

        return Response(MealLogItemSerializer(item).data, status=status.HTTP_201_CREATED)


class DailyDashboardView(APIView):
    def get(self, request):
        log_date_str = request.query_params.get("date", str(datetime.date.today()))
        log_date = datetime.date.fromisoformat(log_date_str)

        meal_log = MealLog.objects.filter(
            user_id=request.user_id, log_date=log_date, is_deleted=False
        ).first()
        total = meal_log.total_calories if meal_log else 0
        target = get_target_calories(request.user_id)

        return Response({
            "log_date": str(log_date),
            "total_calories": total,
            "target_calories": target,
            "remaining_calories": target - total,
            "over_target": total > target,
        })


class WeeklyReportView(APIView):
    def get(self, request):
        end_date_str = request.query_params.get("end_date", str(datetime.date.today()))
        end_date = datetime.date.fromisoformat(end_date_str)
        start_date = end_date - datetime.timedelta(days=6)

        logs = MealLog.objects.filter(
            user_id=request.user_id, log_date__range=[start_date, end_date], is_deleted=False
        ).order_by("log_date")

        days = [{"log_date": str(l.log_date), "total_calories": l.total_calories} for l in logs]
        total_sum = sum(d["total_calories"] for d in days)
        average = round(total_sum / len(days), 2) if days else 0

        return Response({
            "start_date": str(start_date),
            "end_date": str(end_date),
            "days": days,
            "average_daily_calories": average,
        })


class StreakView(APIView):
    def get(self, request):
        streak = DailyStreak.objects.filter(user_id=request.user_id).first()
        if not streak:
            return Response({"streak_count": 0, "last_active_date": None})
        return Response(DailyStreakSerializer(streak).data)

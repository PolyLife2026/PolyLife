from django.test import TestCase, Client
from .models import FoodItem, FoodUnit


class HealthProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.headers = {"HTTP_X_USER_ID": "test-user-1", "HTTP_X_USER_USERNAME": "tester"}

    def test_create_and_get_health_profile(self):
        resp = self.client.post(
            "/api/health-profile/",
            data={"height": 180, "weight": 75, "age": 25, "gender": "male", "goal": "lose"},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("bmi", resp.json())
        self.assertIn("target_calories", resp.json())


class FoodSearchTests(TestCase):
    def setUp(self):
        FoodItem.objects.create(name="zzz_unique_test_food", calories=165, protein=31, carbs=0, fat=3.6)
        self.headers = {"HTTP_X_USER_ID": "test-user-1", "HTTP_X_USER_USERNAME": "tester"}

    def test_search_finds_food(self):
        resp = self.client.get("/api/food-items/search/?q=zzz_unique_test_food", **self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)


class MealLogTests(TestCase):
    def setUp(self):
        self.food = FoodItem.objects.create(name="cooked_rice", calories=130, protein=2.7, carbs=28, fat=0.3)
        self.headers = {"HTTP_X_USER_ID": "test-user-2", "HTTP_X_USER_USERNAME": "tester2"}

    def test_log_meal_and_dashboard(self):
        resp = self.client.post(
            "/api/meal-logs/",
            data={"food_item_id": str(self.food.id), "quantity_grams": 200, "meal_type": "lunch"},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(resp.status_code, 201)

        dashboard = self.client.get("/api/dashboard/daily/", **self.headers)
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json()["total_calories"], 260)


class UnitBasedLoggingTests(TestCase):
    def setUp(self):
        self.food = FoodItem.objects.create(
            name="zzz_apple_test", category="fruit", calories=52, protein=0.3, carbs=14, fat=0.2
        )
        FoodUnit.objects.create(food_item=self.food, unit_name="گرم", grams_per_unit=1)
        self.unit_piece = FoodUnit.objects.create(
            food_item=self.food, unit_name="عدد", grams_per_unit=150
        )
        self.headers = {"HTTP_X_USER_ID": "test-user-3", "HTTP_X_USER_USERNAME": "tester3"}

    def test_log_by_unit_count_converts_to_grams(self):
        resp = self.client.post(
            "/api/meal-logs/",
            data={
                "food_item_id": str(self.food.id),
                "unit_id": str(self.unit_piece.id),
                "unit_quantity": 2,
                "meal_type": "snack",
            },
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["quantity_grams"], "300.00")
        self.assertEqual(data["unit_name"], "عدد")
        self.assertEqual(data["consumed_calories"], 156.0)

    def test_search_returns_units_and_category(self):
        resp = self.client.get(
            f"/api/food-items/search/?q=zzz_apple_test", **self.headers
        )
        self.assertEqual(resp.status_code, 200)
        item = resp.json()[0]
        self.assertEqual(item["category"], "fruit")
        unit_names = {u["unit_name"] for u in item["units"]}
        self.assertIn("عدد", unit_names)
        self.assertIn("گرم", unit_names)


class FavoriteToggleTests(TestCase):
    def setUp(self):
        self.food = FoodItem.objects.create(
            name="zzz_favorite_test", calories=100, protein=1, carbs=1, fat=1
        )
        self.headers = {"HTTP_X_USER_ID": "test-user-4", "HTTP_X_USER_USERNAME": "tester4"}

    def test_toggle_favorite_on_then_off(self):
        resp = self.client.post(
            "/api/favorites/toggle/",
            data={"food_item_id": str(self.food.id)},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json()["is_favorite"])

        resp2 = self.client.post(
            "/api/favorites/toggle/",
            data={"food_item_id": str(self.food.id)},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(resp2.json()["is_favorite"])

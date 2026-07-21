from django.test import TestCase, Client
from .models import FoodItem


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
        FoodItem.objects.create(name="chicken_breast", calories=165, protein=31, carbs=0, fat=3.6)
        self.headers = {"HTTP_X_USER_ID": "test-user-1", "HTTP_X_USER_USERNAME": "tester"}

    def test_search_finds_food(self):
        resp = self.client.get("/api/food-items/search/?q=chicken", **self.headers)
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

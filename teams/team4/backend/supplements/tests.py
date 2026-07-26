from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from store.models import Category, Product

from .models import Supplement


class SupplementApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.supplement = Supplement.objects.create(
            name="Creatine",
            scientific_name="Creatine Monohydrate",
            description="Strength supplement",
            dosage="5 grams daily",
            usage_instructions="Take with water",
            benefits="Improved performance",
            side_effects="Possible stomach discomfort",
            warnings="Consult a doctor when necessary",
            fda_reference="Example reference",
        )

        category = Category.objects.create(
            name="Supplements",
            slug="supplements",
        )

        self.product = Product.objects.create(
            name="Creatine Package",
            slug="creatine-package",
            description="Creatine product",
            price=Decimal("300000.00"),
            stock_quantity=5,
            category=category,
            supplement_id=self.supplement.id,
        )

    def test_supplement_list(self):
        response = self.client.get("/api/supplements/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_supplement_detail(self):
        response = self.client.get(
            f"/api/supplements/{self.supplement.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Creatine")
        self.assertEqual(response.data["dosage"], "5 grams daily")

    def test_store_link_returns_related_product(self):
        response = self.client.get(
            f"/api/supplements/{self.supplement.id}/buy/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["store_products"][0]["id"],
            self.product.id,
        )

    def test_deleted_supplement_is_hidden(self):
        self.supplement.is_deleted = True
        self.supplement.save()

        response = self.client.get(
            f"/api/supplements/{self.supplement.id}/"
        )

        self.assertEqual(response.status_code, 404)
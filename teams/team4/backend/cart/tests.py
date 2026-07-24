from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from store.models import Category, Product

from .models import DiscountCode, Invoice, Order, Transaction


class CartApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_USER_ID="10",
            HTTP_X_USER_USERNAME="test-user",
        )

        category = Category.objects.create(
            name="Supplements",
            slug="supplements",
        )

        self.product = Product.objects.create(
            name="Whey Protein",
            slug="whey-protein",
            description="Protein supplement",
            price=Decimal("500000.00"),
            stock_quantity=10,
            category=category,
        )

        self.coupon = DiscountCode.objects.create(
            code="SALAM10",
            discount_percent=Decimal("10.00"),
            max_uses=100,
        )

    def test_authentication_header_is_required(self):
        client = APIClient()

        response = client.get("/api/cart/")

        self.assertEqual(response.status_code, 401)

    def test_add_product_to_cart(self):
        response = self.client.post(
            "/api/cart/add/",
            {
                "product_id": self.product.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["cart"]["items"][0]["quantity"],
            2,
        )

    def test_quantity_zero_removes_product(self):
        self.client.post(
            "/api/cart/add/",
            {
                "product_id": self.product.id,
                "quantity": 2,
            },
            format="json",
        )

        response = self.client.post(
            "/api/cart/update/",
            {
                "product_id": self.product.id,
                "quantity": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cart"]["items"], [])

    def test_invalid_coupon_returns_error(self):
        response = self.client.post(
            "/api/cart/apply-coupon/",
            {"code": "INVALID"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "Invalid discount code.",
        )

    def test_checkout_creates_order_transaction_and_invoice(self):
        self.client.post(
            "/api/cart/add/",
            {
                "product_id": self.product.id,
                "quantity": 2,
            },
            format="json",
        )

        response = self.client.post(
            "/api/cart/checkout/",
            {"discount_code": "SALAM10"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Invoice.objects.count(), 1)

        order = Order.objects.get()
        self.assertEqual(order.status, Order.STATUS_PAID)
        self.assertEqual(
            order.final_amount,
            Decimal("900000.00"),
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    def test_failed_checkout_preserves_cart(self):
        self.client.post(
            "/api/cart/add/",
            {
                "product_id": self.product.id,
                "quantity": 2,
            },
            format="json",
        )

        self.product.stock_quantity = 1
        self.product.save(update_fields=["stock_quantity"])

        response = self.client.post(
            "/api/cart/checkout/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        cart_response = self.client.get("/api/cart/")
        self.assertEqual(
            cart_response.data["items"][0]["quantity"],
            2,
        )

    def test_order_history_only_returns_current_user_orders(self):
        Order.objects.create(
            user_id=10,
            total_amount=Decimal("100.00"),
            final_amount=Decimal("100.00"),
            status=Order.STATUS_PAID,
        )

        Order.objects.create(
            user_id=20,
            total_amount=Decimal("200.00"),
            final_amount=Decimal("200.00"),
            status=Order.STATUS_PAID,
        )

        response = self.client.get("/api/cart/orders/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user_id"], 10)
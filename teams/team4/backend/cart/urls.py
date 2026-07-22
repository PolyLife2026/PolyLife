from django.urls import path

from . import views

urlpatterns = [
    path("", views.cart_detail, name="cart-detail"),
    path("add/", views.cart_add, name="cart-add"),
    path("update/", views.cart_update, name="cart-update"),
    path(
        "apply-coupon/",
        views.apply_coupon,
        name="apply-coupon",
    ),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order-history"),
    path(
        "invoices/<str:invoice_number>/",
        views.invoice_detail,
        name="invoice-detail",
    ),
]
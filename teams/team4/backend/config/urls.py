from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView


def health_check(request):
    return JsonResponse({"status": "ok", "team": "team4"})


def whoami(request):
    return JsonResponse({
        "user_id": request.headers.get("X-User-Id", ""),
        "username": request.headers.get("X-User-Username", ""),
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health"),
    path("api/whoami/", whoami, name="whoami"),
    path("api/store/", include("store.urls")),
    path("api/supplements/", include("supplements.urls")),
    path("api/cart/", include("cart.urls")),

    # ── صفحات فرانت‌اند ──────────────────────────────────────────
    path("", TemplateView.as_view(template_name="store/home.html"), name="home"),
    path("store/products/",
         TemplateView.as_view(template_name="store/products.html"), name="products-page"),
    path("store/products/<int:pk>/",
         TemplateView.as_view(template_name="store/product_detail.html"), name="product-detail-page"),
    path("supplements/<int:pk>/",
         TemplateView.as_view(template_name="supplements/supplement_detail.html"), name="supplement-detail-page"),
    path("cart/",
         TemplateView.as_view(template_name="cart/cart.html"), name="cart-page"),
    path("checkout/",
         TemplateView.as_view(template_name="cart/checkout.html"), name="checkout-page"),
    path("orders/",
         TemplateView.as_view(template_name="cart/orders.html"), name="orders-page"),
]
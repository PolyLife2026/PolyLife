from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse(
        {
            "status": "ok",
            "team": "team4",
            "service": "store-supplements-cart",
        }
    )


def whoami(request):
    return JsonResponse(
        {
            "user_id": request.headers.get("X-User-Id", ""),
            "username": request.headers.get("X-User-Username", ""),
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health"),
    path("api/whoami/", whoami, name="whoami"),
    path("api/store/", include("store.urls")),
    path(
        "api/supplements/",
        include("supplements.urls"),
    ),
    path("api/cart/", include("cart.urls")),
]
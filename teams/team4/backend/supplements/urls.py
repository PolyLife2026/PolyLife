from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.SupplementListView.as_view(),
        name="supplement-list",
    ),
    path(
        "<int:pk>/",
        views.SupplementDetailView.as_view(),
        name="supplement-detail",
    ),
    path(
        "<int:pk>/buy/",
        views.supplement_store_link,
        name="supplement-store-link",
    ),
]
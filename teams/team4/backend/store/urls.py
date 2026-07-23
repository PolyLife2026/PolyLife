from django.urls import path

from . import views

urlpatterns = [
    path(
        "categories/",
        views.CategoryListView.as_view(),
        name="category-list",
    ),
    path(
        "products/",
        views.ProductListView.as_view(),
        name="product-list",
    ),
    path(
        "products/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "products/<int:pk>/share/",
        views.product_share_link,
        name="product-share",
    ),
    path(
        "admin/products/",
        views.AdminProductListCreateView.as_view(),
    ),
]
from django.urls import reverse
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)

class Meta:
    model = Product
    fields = [
        "category",
        "brand",
        "sport_type",
        "supplement_id",
    ]
    
class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )
    min_rating = django_filters.NumberFilter(
        field_name="rating",
        lookup_expr="gte",
    )

    class Meta:
        model = Product
        fields = ["category", "brand", "sport_type"]


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(
            parent=None,
            is_deleted=False,
        ).prefetch_related("children")


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "brand"]
    ordering_fields = ["price", "rating", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related("category")


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related("category")


@api_view(["GET"])
def product_share_link(request, pk):
    try:
        product = Product.objects.get(
            pk=pk,
            is_active=True,
            is_deleted=False,
        )
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    product_path = f"/api/store/products/{product.pk}/"
    share_url = request.build_absolute_uri(
        reverse("product-detail-page", args=[product.id])
    )

    return Response(
        {
            "product_id": product.pk,
            "product_name": product.name,
            "share_url": share_url,
        }
    )
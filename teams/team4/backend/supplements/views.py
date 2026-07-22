from rest_framework import filters, generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from store.models import Product

from .models import Supplement
from .serializers import (
    SupplementDetailSerializer,
    SupplementListSerializer,
)


class SupplementListView(generics.ListAPIView):
    serializer_class = SupplementListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "scientific_name", "description"]

    def get_queryset(self):
        return Supplement.objects.filter(
            is_deleted=False,
        ).order_by("name")


class SupplementDetailView(generics.RetrieveAPIView):
    serializer_class = SupplementDetailSerializer

    def get_queryset(self):
        return Supplement.objects.filter(is_deleted=False)


@api_view(["GET"])
def supplement_store_link(request, pk):
    try:
        supplement = Supplement.objects.get(
            pk=pk,
            is_deleted=False,
        )
    except Supplement.DoesNotExist:
        return Response(
            {"error": "Supplement not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    products = Product.objects.filter(
        supplement_id=pk,
        is_active=True,
        is_deleted=False,
    ).values(
        "id",
        "name",
        "price",
        "stock_quantity",
    )

    store_path = f"/api/store/products/?supplement_id={pk}"

    return Response(
        {
            "supplement_id": supplement.id,
            "supplement_name": supplement.name,
            "store_products": list(products),
            "store_url": request.build_absolute_uri(store_path),
        }
    )
from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "is_deleted"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock_quantity", "category", "brand", "is_active"]
    list_filter = ["category", "brand", "is_active"]
    search_fields = ["name", "brand"]
    prepopulated_fields = {"slug": ("name",)}

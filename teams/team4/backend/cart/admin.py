from django.contrib import admin
from .models import DiscountCode, Order, OrderItem, Transaction, Invoice


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_percent", "used_count", "max_uses", "is_active", "expires_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user_id", "final_amount", "status", "created_at"]
    list_filter = ["status"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction_ref", "order", "amount", "status", "created_at"]
    list_filter = ["status"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "user_id", "order", "created_at"]

from django.contrib import admin
from .models import Supplement


@admin.register(Supplement)
class SupplementAdmin(admin.ModelAdmin):
    list_display = ["name", "scientific_name"]
    search_fields = ["name", "scientific_name"]

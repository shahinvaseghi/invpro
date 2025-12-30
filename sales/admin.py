"""
Admin configuration for sales module.
"""
from django.contrib import admin
from unfold.admin import ModelAdmin

from . import models


@admin.register(models.ItemPriceCard)
class ItemPriceCardAdmin(ModelAdmin):
    list_display = ("company", "item", "price", "currency", "effective_date", "expiry_date", "is_enabled", "sort_order")
    list_filter = ("company", "currency", "is_enabled", "effective_date", "expiry_date")
    search_fields = ("item__name", "item__name_en", "item_code", "item__item_code")
    readonly_fields = ("item_code", "created_at", "edited_at", "created_by", "edited_by")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("company", "item", "item_code", "price", "currency")
        }),
        ("Date Information", {
            "fields": ("effective_date", "expiry_date"),
            "classes": ("collapse",)
        }),
        ("Additional Information", {
            "fields": ("notes",),
            "classes": ("collapse",)
        }),
        ("Status & Ordering", {
            "fields": ("is_enabled", "sort_order")
        }),
        ("Metadata", {
            "fields": ("created_at", "edited_at", "created_by", "edited_by", "metadata"),
            "classes": ("collapse",)
        }),
    )


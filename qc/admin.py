from django.contrib import admin
from unfold.admin import ModelAdmin

from . import models


@admin.register(models.ReceiptInspection)
class ReceiptInspectionAdmin(ModelAdmin):
    list_display = (
        "company",
        "inspection_code",
        "temporary_receipt_code",
        "inspection_status",
        "approval_decision",
        "nonconformity_flag",
        "is_enabled",
    )
    list_filter = (
        "company",
        "inspection_status",
        "approval_decision",
        "nonconformity_flag",
        "is_enabled",
    )
    search_fields = ("inspection_code", "temporary_receipt_code", "inspector__first_name", "inspector__last_name")
    readonly_fields = ("temporary_receipt_code", "inspector_code")

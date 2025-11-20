from django.contrib import admin

from . import models


@admin.register(models.WorkCenter)
class WorkCenterAdmin(admin.ModelAdmin):
    list_display = ("company", "public_code", "name", "is_enabled", "sort_order")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "name_en")


@admin.register(models.BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ("bom_code", "company", "finished_item_code", "version", "is_active", "is_enabled")
    list_filter = ("company", "is_active", "is_enabled")
    search_fields = ("bom_code", "finished_item_code")
    readonly_fields = ("bom_code", "finished_item_code")


@admin.register(models.BOMMaterial)
class BOMMaterialAdmin(admin.ModelAdmin):
    list_display = ("company", "bom", "material_item_code", "quantity_per_unit", "unit", "line_number")
    list_filter = ("company", "material_type")
    search_fields = ("bom__bom_code", "material_item_code")
    readonly_fields = ("material_item_code",)


@admin.register(models.Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("company", "process_code", "finished_item_code", "revision", "approval_status", "is_primary")
    list_filter = ("company", "approval_status", "is_primary", "is_enabled")
    search_fields = ("process_code", "finished_item_code", "bom_code", "revision")
    readonly_fields = ("finished_item_code",)


@admin.register(models.ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ("company", "process", "sequence_order", "work_center", "labor_minutes_per_unit")
    list_filter = ("company", "process")
    search_fields = ("process__process_code", "work_center__public_code")
    ordering = ("process", "sequence_order")


@admin.register(models.ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ("company", "order_code", "finished_item_code", "quantity_planned", "status", "priority")
    list_filter = ("company", "status", "priority")
    search_fields = ("order_code", "finished_item_code", "customer_reference")
    readonly_fields = ("finished_item_code", "process_code")


@admin.register(models.OrderPerformance)
class OrderPerformanceAdmin(admin.ModelAdmin):
    list_display = ("company", "order", "report_date", "quantity_produced", "quantity_scrapped")
    list_filter = ("company", "report_date")
    search_fields = ("order__order_code", "finished_item_code")


@admin.register(models.TransferToLine)
class TransferToLineAdmin(admin.ModelAdmin):
    list_display = ("company", "transfer_code", "order", "transfer_date", "status")
    list_filter = ("company", "status")
    search_fields = ("transfer_code", "order__order_code")


@admin.register(models.TransferToLineItem)
class TransferToLineItemAdmin(admin.ModelAdmin):
    list_display = ("company", "transfer", "material_item_code", "quantity_required", "quantity_transferred")
    list_filter = ("company", "transfer")
    search_fields = ("transfer__transfer_code", "material_item_code")


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("public_code", "first_name", "last_name", "company", "is_enabled")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "first_name", "last_name", "company__display_name")


@admin.register(models.PersonAssignment)
class PersonAssignmentAdmin(admin.ModelAdmin):
    list_display = ("person", "company", "work_center_type", "work_center_id", "is_primary", "is_enabled")
    list_filter = ("company", "work_center_type", "is_primary", "is_enabled")
    search_fields = ("person__first_name", "person__last_name", "work_center_type", "work_center_id")


@admin.register(models.Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("public_code", "name", "machine_type", "work_center", "status", "is_enabled")
    list_filter = ("company", "machine_type", "status", "is_enabled")
    search_fields = ("public_code", "name", "name_en", "manufacturer", "model_number", "serial_number")


@admin.register(models.WorkLine)
class WorkLineAdmin(admin.ModelAdmin):
    list_display = ("company", "warehouse", "public_code", "name", "is_enabled")
    list_filter = ("company", "warehouse", "is_enabled")
    search_fields = ("public_code", "name", "name_en")

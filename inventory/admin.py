from django.contrib import admin

from . import models


@admin.register(models.ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ("company", "public_code", "name", "is_enabled", "sort_order")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "name_en")


@admin.register(models.ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ("company", "public_code", "name", "is_enabled", "sort_order")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "name_en")


@admin.register(models.ItemSubcategory)
class ItemSubcategoryAdmin(admin.ModelAdmin):
    list_display = ("company", "category", "public_code", "name", "is_enabled", "sort_order")
    list_filter = ("company", "category", "is_enabled")
    search_fields = ("public_code", "name", "name_en")


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("company", "public_code", "name", "is_enabled")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "name_en")


@admin.register(models.WorkLine)
class WorkLineAdmin(admin.ModelAdmin):
    list_display = ("company", "warehouse", "public_code", "name", "is_enabled")
    list_filter = ("company", "warehouse", "is_enabled")
    search_fields = ("public_code", "name", "name_en")


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("company", "item_code", "name", "type", "category", "is_enabled")
    list_filter = ("company", "type", "category", "has_lot_tracking", "is_enabled")
    search_fields = ("item_code", "name", "name_en")
    readonly_fields = ("item_code", "sequence_segment", "batch_number", "type_code", "category_code", "subcategory_code")


@admin.register(models.ItemSpec)
class ItemSpecAdmin(admin.ModelAdmin):
    list_display = ("company", "item", "description", "is_enabled", "sort_order")
    list_filter = ("company", "item", "is_enabled")
    search_fields = ("item__item_code", "description")


@admin.register(models.ItemUnit)
class ItemUnitAdmin(admin.ModelAdmin):
    list_display = ("company", "item", "from_unit", "to_unit", "is_primary", "is_enabled")
    list_filter = ("company", "item", "is_primary", "is_enabled")
    search_fields = ("item__item_code", "from_unit", "to_unit")


@admin.register(models.ItemWarehouse)
class ItemWarehouseAdmin(admin.ModelAdmin):
    list_display = ("company", "item", "warehouse", "is_primary", "is_enabled")
    list_filter = ("company", "warehouse", "is_primary", "is_enabled")
    search_fields = ("item__item_code", "warehouse__name")


@admin.register(models.ItemSubstitute)
class ItemSubstituteAdmin(admin.ModelAdmin):
    list_display = ("company", "source_item", "target_item", "is_bidirectional", "is_enabled")
    list_filter = ("company", "is_bidirectional", "is_enabled")
    search_fields = ("source_item__item_code", "target_item__item_code")


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("company", "public_code", "name", "city", "is_enabled")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "tax_id")


@admin.register(models.SupplierCategory)
class SupplierCategoryAdmin(admin.ModelAdmin):
    list_display = ("company", "supplier", "category", "is_primary", "is_enabled")
    list_filter = ("company", "category", "is_primary", "is_enabled")
    search_fields = ("supplier__name", "category__name")


@admin.register(models.SupplierSubcategory)
class SupplierSubcategoryAdmin(admin.ModelAdmin):
    list_display = ("company", "supplier", "subcategory", "is_primary", "is_enabled")
    list_filter = ("company", "subcategory", "is_primary", "is_enabled")
    search_fields = ("supplier__name", "subcategory__name")


@admin.register(models.SupplierItem)
class SupplierItemAdmin(admin.ModelAdmin):
    list_display = ("company", "supplier", "item", "is_primary", "is_enabled")
    list_filter = ("company", "supplier", "is_primary", "is_enabled")
    search_fields = ("supplier__name", "item__item_code")


@admin.register(models.PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ("company", "request_code", "item", "quantity_requested", "status", "priority")
    list_filter = ("company", "status", "priority")
    search_fields = ("request_code", "item__item_code", "requested_by__first_name", "requested_by__last_name")


@admin.register(models.ReceiptTemporary)
class ReceiptTemporaryAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "warehouse", "status", "is_converted", "is_enabled")
    list_filter = ("company", "status", "is_converted", "is_enabled")
    search_fields = ("document_code", "item__item_code", "warehouse__name")


@admin.register(models.ReceiptPermanent)
class ReceiptPermanentAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "warehouse", "quantity", "is_locked", "is_enabled")
    list_filter = ("company", "is_locked", "is_enabled")
    search_fields = ("document_code", "item__item_code", "warehouse__name")


@admin.register(models.ReceiptConsignment)
class ReceiptConsignmentAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "supplier", "ownership_status", "is_enabled")
    list_filter = ("company", "ownership_status", "is_enabled")
    search_fields = ("document_code", "item__item_code", "supplier__name")


@admin.register(models.ItemLot)
class ItemLotAdmin(admin.ModelAdmin):
    list_display = ("company", "lot_code", "item", "status", "quantity")
    list_filter = ("company", "status")
    search_fields = ("lot_code", "item__item_code", "receipt_document_code")


@admin.register(models.IssuePermanent)
class IssuePermanentAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "destination_type", "quantity", "is_locked")
    list_filter = ("company", "destination_type", "is_locked")
    search_fields = ("document_code", "item__item_code", "destination_code")


@admin.register(models.IssueConsumption)
class IssueConsumptionAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "consumption_type", "quantity", "is_locked")
    list_filter = ("company", "consumption_type", "is_locked")
    search_fields = ("document_code", "item__item_code", "cost_center_code")


@admin.register(models.IssueConsignment)
class IssueConsignmentAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "destination_type", "quantity")
    list_filter = ("company", "destination_type", "is_enabled")
    search_fields = ("document_code", "item__item_code", "consignment_receipt_code")


@admin.register(models.StocktakingDeficit)
class StocktakingDeficitAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "quantity_adjusted", "is_locked")
    list_filter = ("company", "is_locked")
    search_fields = ("document_code", "item__item_code", "warehouse__name")


@admin.register(models.StocktakingSurplus)
class StocktakingSurplusAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "item", "quantity_adjusted", "is_locked")
    list_filter = ("company", "is_locked")
    search_fields = ("document_code", "item__item_code", "warehouse__name")


@admin.register(models.StocktakingRecord)
class StocktakingRecordAdmin(admin.ModelAdmin):
    list_display = ("company", "document_code", "stocktaking_session_id", "approval_status", "is_enabled")
    list_filter = ("company", "approval_status", "is_enabled")
    search_fields = ("document_code", "confirmed_by__first_name", "confirmed_by__last_name")


@admin.register(models.WarehouseRequest)
class WarehouseRequestAdmin(admin.ModelAdmin):
    list_display = ("company", "request_code", "item", "quantity_requested", "request_status", "priority", "needed_by_date")
    list_filter = ("company", "request_status", "priority", "warehouse", "request_date")
    search_fields = ("request_code", "item_code", "requester_code", "purpose")
    readonly_fields = ("request_code", "item_code", "warehouse_code", "requester_code", "department_unit_code", "approved_by_code")

from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.db.models import Q
from unfold.admin import ModelAdmin, TabularInline

from . import models


@admin.register(models.ItemType)
class ItemTypeAdmin(ModelAdmin):
    list_display = ("company", "public_code", "name", "is_enabled", "sort_order")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "name_en")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("company", "public_code", "name", "name_en")
        }),
        ("Additional Information", {
            "fields": ("description", "notes"),
            "classes": ("collapse",)
        }),
        ("Status & Ordering", {
            "fields": ("is_enabled", "sort_order")
        }),
    )


@admin.register(models.ItemCategory)
class ItemCategoryAdmin(ModelAdmin):
    list_display = ("company", "public_code", "name", "is_enabled", "sort_order")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "name_en")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("company", "public_code", "name", "name_en")
        }),
        ("Additional Information", {
            "fields": ("description", "notes"),
            "classes": ("collapse",)
        }),
        ("Status & Ordering", {
            "fields": ("is_enabled", "sort_order")
        }),
    )


@admin.register(models.ItemSubcategory)
class ItemSubcategoryAdmin(ModelAdmin):
    list_display = ("company", "category", "public_code", "name", "is_enabled", "sort_order")
    list_filter = ("company", "category", "is_enabled")
    search_fields = ("public_code", "name", "name_en")
    autocomplete_fields = ["category"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("company", "category", "public_code", "name", "name_en")
        }),
        ("Additional Information", {
            "fields": ("description", "notes"),
            "classes": ("collapse",)
        }),
        ("Status & Ordering", {
            "fields": ("is_enabled", "sort_order")
        }),
    )


@admin.register(models.Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ("company", "public_code", "name", "is_enabled")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "name_en")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("company", "public_code", "name", "name_en")
        }),
        ("Additional Information", {
            "fields": ("description", "notes", "location_label"),
            "classes": ("collapse",)
        }),
        ("Status", {
            "fields": ("is_enabled",)
        }),
    )
    
    def get_search_results(self, request, queryset, search_term):
        """Filter queryset based on active company from session."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Filter by active company from session
        active_company_id = request.session.get('active_company_id')
        if active_company_id:
            queryset = queryset.filter(company_id=active_company_id, is_enabled=1)
        
        return queryset, use_distinct
    
    def get_queryset(self, request):
        """Filter queryset based on active company from session."""
        qs = super().get_queryset(request)
        
        # Filter by active company from session
        active_company_id = request.session.get('active_company_id')
        if active_company_id:
            qs = qs.filter(company_id=active_company_id, is_enabled=1)
        
        return qs


# WorkLine moved to production module
# Register it in production/admin.py instead


@admin.register(models.Item)
class ItemAdmin(ModelAdmin):
    list_display = ("company", "item_code", "name", "type", "category", "is_enabled")
    list_filter = ("company", "type", "category", "has_lot_tracking", "is_enabled")
    search_fields = ("item_code", "name", "name_en")
    readonly_fields = ("item_code", "sequence_segment", "batch_number", "type_code", "category_code", "subcategory_code", "full_item_code", "created_at", "edited_at")
    
    def get_search_results(self, request, queryset, search_term):
        """Filter queryset based on active company from session."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Filter by active company from session
        active_company_id = request.session.get('active_company_id')
        if active_company_id:
            queryset = queryset.filter(company_id=active_company_id, is_enabled=1)
        
        return queryset, use_distinct
    
    def get_queryset(self, request):
        """Filter queryset based on active company from session."""
        qs = super().get_queryset(request)
        
        # Filter by active company from session
        active_company_id = request.session.get('active_company_id')
        if active_company_id:
            qs = qs.filter(company_id=active_company_id, is_enabled=1)
        
        return qs
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("company", "type", "category", "subcategory", "name", "name_en")
        }),
        ("Codes", {
            "fields": ("user_segment", "item_code", "full_item_code", "type_code", "category_code", "subcategory_code", "sequence_segment"),
            "classes": ("collapse",)
        }),
        ("Batch Information", {
            "fields": ("batch_number", "secondary_batch_number"),
            "classes": ("collapse",)
        }),
        ("Product Details", {
            "fields": ("description", "notes", "is_sellable", "has_lot_tracking", "requires_temporary_receipt")
        }),
        ("Tax Information", {
            "fields": ("tax_id", "tax_title"),
            "classes": ("collapse",)
        }),
        ("Stock & Units", {
            "fields": ("min_stock", "default_unit", "default_unit_id", "primary_unit")
        }),
        ("Status & Ordering", {
            "fields": ("is_enabled", "sort_order")
        }),
        ("Metadata", {
            "fields": ("created_at", "edited_at", "metadata"),
            "classes": ("collapse",)
        }),
    )


@admin.register(models.ItemSpec)
class ItemSpecAdmin(ModelAdmin):
    list_display = ("company", "item", "description", "is_enabled", "sort_order")
    list_filter = ("company", "item", "is_enabled")
    search_fields = ("item__item_code", "description")
    autocomplete_fields = ["item"]


@admin.register(models.ItemUnit)
class ItemUnitAdmin(ModelAdmin):
    list_display = ("company", "item", "from_unit", "to_unit", "is_primary", "is_enabled")
    list_filter = ("company", "item", "is_primary", "is_enabled")
    search_fields = ("item__item_code", "from_unit", "to_unit")
    autocomplete_fields = ["item"]


@admin.register(models.ItemWarehouse)
class ItemWarehouseAdmin(ModelAdmin):
    list_display = ("company", "item", "warehouse", "is_primary", "is_enabled")
    list_filter = ("company", "warehouse", "is_primary", "is_enabled")
    search_fields = ("item__item_code", "warehouse__name")
    autocomplete_fields = ["item", "warehouse"]


@admin.register(models.ItemSubstitute)
class ItemSubstituteAdmin(ModelAdmin):
    list_display = ("company", "source_item", "target_item", "is_bidirectional", "is_enabled")
    list_filter = ("company", "is_bidirectional", "is_enabled")
    search_fields = ("source_item__item_code", "target_item__item_code")
    autocomplete_fields = ["source_item", "target_item"]


@admin.register(models.Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ("company", "public_code", "name", "city", "is_enabled")
    list_filter = ("company", "is_enabled")
    search_fields = ("public_code", "name", "tax_id")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("company", "public_code", "name", "name_en")
        }),
        ("Contact Information", {
            "fields": ("address", "city", "state", "country", "phone_number", "mobile_number", "email"),
            "classes": ("collapse",)
        }),
        ("Tax Information", {
            "fields": ("tax_id",),
            "classes": ("collapse",)
        }),
        ("Additional Information", {
            "fields": ("description",),
            "classes": ("collapse",)
        }),
        ("Status & Ordering", {
            "fields": ("is_enabled", "sort_order")
        }),
    )
    
    def get_search_results(self, request, queryset, search_term):
        """Filter queryset based on active company from session."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Filter by active company from session
        active_company_id = request.session.get('active_company_id')
        if active_company_id:
            queryset = queryset.filter(company_id=active_company_id, is_enabled=1)
        
        return queryset, use_distinct
    
    def get_queryset(self, request):
        """Filter queryset based on active company from session."""
        qs = super().get_queryset(request)
        
        # Filter by active company from session
        active_company_id = request.session.get('active_company_id')
        if active_company_id:
            qs = qs.filter(company_id=active_company_id, is_enabled=1)
        
        return qs


@admin.register(models.SupplierCategory)
class SupplierCategoryAdmin(ModelAdmin):
    list_display = ("company", "supplier", "category", "is_primary", "is_enabled")
    list_filter = ("company", "category", "is_primary", "is_enabled")
    search_fields = ("supplier__name", "category__name")
    autocomplete_fields = ["supplier", "category"]


@admin.register(models.SupplierSubcategory)
class SupplierSubcategoryAdmin(ModelAdmin):
    list_display = ("company", "supplier", "subcategory", "is_primary", "is_enabled")
    list_filter = ("company", "subcategory", "is_primary", "is_enabled")
    search_fields = ("supplier__name", "subcategory__name")
    autocomplete_fields = ["supplier", "subcategory"]


@admin.register(models.SupplierItem)
class SupplierItemAdmin(ModelAdmin):
    list_display = ("company", "supplier", "item", "is_primary", "is_enabled")
    list_filter = ("company", "supplier", "is_primary", "is_enabled")
    search_fields = ("supplier__name", "item__item_code")
    autocomplete_fields = ["supplier", "item"]


@admin.register(models.PurchaseRequest)
class PurchaseRequestAdmin(ModelAdmin):
    list_display = ("company", "request_code", "item", "quantity_requested", "status", "priority")
    list_filter = ("company", "status", "priority")
    search_fields = ("request_code", "item__item_code", "requested_by__username")
    autocomplete_fields = ["item", "requested_by", "approver"]


@admin.register(models.ReceiptTemporary)
class ReceiptTemporaryAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date", "status", "is_converted", "is_enabled")
    list_filter = ("company", "status", "is_converted", "is_enabled")
    search_fields = ("document_code", "supplier__name", "supplier__public_code")
    autocomplete_fields = ["supplier", "qc_approved_by"]


class ReceiptPermanentLineInline(TabularInline):
    """Inline for receipt permanent lines."""
    model = models.ReceiptPermanentLine
    extra = 1
    fields = ("item", "warehouse", "unit", "quantity", "entered_unit", "entered_quantity", "supplier", "line_notes")
    autocomplete_fields = ["item", "warehouse", "supplier"]
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset to filter querysets based on active company."""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Get active company from session
        active_company_id = request.session.get('active_company_id')
        
        if active_company_id:
            # Store company_id for use in form
            formset.company_id = active_company_id
            
            # Override form to filter querysets and remove add/edit buttons
            original_form = formset.form
            
            class FilteredForm(original_form):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    company_id = getattr(formset, 'company_id', None)
                    
                    if company_id:
                        # Filter item queryset - include all enabled items from company
                        if 'item' in self.fields:
                            # Get all enabled items from company
                            queryset = models.Item.objects.filter(
                                company_id=company_id,
                                is_enabled=1
                            ).order_by('name')
                            
                            # Include current item if editing
                            if getattr(self.instance, 'item_id', None):
                                queryset = models.Item.objects.filter(
                                    company_id=company_id
                                ).filter(
                                    Q(is_enabled=1) | Q(pk=self.instance.item_id)
                                ).order_by('name')
                            
                            self.fields['item'].queryset = queryset
                            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
                            
                            # Remove add/edit buttons by using AutocompleteSelect widget without related buttons
                            from django.contrib.admin.widgets import AutocompleteSelect
                            widget = self.fields['item'].widget
                            if isinstance(widget, AutocompleteSelect):
                                widget.can_add_related = False
                                widget.can_change_related = False
                                widget.can_delete_related = False
                        
                        # Filter warehouse queryset
                        if 'warehouse' in self.fields:
                            queryset = models.Warehouse.objects.filter(
                                company_id=company_id,
                                is_enabled=1
                            ).order_by('name')
                            
                            # Include current warehouse if editing
                            if getattr(self.instance, 'warehouse_id', None):
                                queryset = models.Warehouse.objects.filter(
                                    company_id=company_id
                                ).filter(
                                    Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                                ).order_by('name')
                            
                            self.fields['warehouse'].queryset = queryset
                            self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
                            
                            # Remove add/edit buttons
                            widget = self.fields['warehouse'].widget
                            if isinstance(widget, AutocompleteSelect):
                                widget.can_add_related = False
                                widget.can_change_related = False
                                widget.can_delete_related = False
                        
                        # Filter supplier queryset
                        if 'supplier' in self.fields:
                            queryset = models.Supplier.objects.filter(
                                company_id=company_id,
                                is_enabled=1
                            ).order_by('name')
                            
                            # Include current supplier if editing
                            if getattr(self.instance, 'supplier_id', None):
                                queryset = models.Supplier.objects.filter(
                                    company_id=company_id
                                ).filter(
                                    Q(is_enabled=1) | Q(pk=self.instance.supplier_id)
                                ).order_by('name')
                            
                            self.fields['supplier'].queryset = queryset
                            self.fields['supplier'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
                            
                            # Remove add/edit buttons
                            widget = self.fields['supplier'].widget
                            if isinstance(widget, AutocompleteSelect):
                                widget.can_add_related = False
                                widget.can_change_related = False
                                widget.can_delete_related = False
            
            formset.form = FilteredForm
        
        return formset


@admin.register(models.ReceiptPermanent)
class ReceiptPermanentAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date", "is_locked", "is_enabled")
    list_filter = ("company", "is_locked", "is_enabled")
    search_fields = ("document_code", "temporary_receipt__document_code", "purchase_request__request_code", "warehouse_request__request_code")
    autocomplete_fields = ["temporary_receipt", "purchase_request"]
    readonly_fields = ("document_code", "document_date", "temporary_receipt_code", "purchase_request_code", "created_at", "edited_at")
    inlines = [ReceiptPermanentLineInline]
    
    fieldsets = (
        ("Related Documents", {
            "fields": ("temporary_receipt", "temporary_receipt_code", "purchase_request", "purchase_request_code"),
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/rtl.css',)
        }
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form to filter querysets based on active company."""
        form = super().get_form(request, obj, **kwargs)
        
        # Get active company from session
        active_company_id = request.session.get('active_company_id')
        
        if active_company_id:
            # Filter temporary_receipt queryset: only QC-approved, unconverted, enabled, with at least one line
            if 'temporary_receipt' in form.base_fields:
                from django.db.models import Exists, OuterRef
                from inventory.models import ReceiptTemporaryLine
                
                form.base_fields['temporary_receipt'].queryset = models.ReceiptTemporary.objects.filter(
                    company_id=active_company_id,
                    qc_approved_by__isnull=False,
                    qc_approved_at__isnull=False,
                    status=models.ReceiptTemporary.Status.APPROVED,
                    is_converted=0,
                    is_enabled=1
                ).filter(
                    Exists(
                        ReceiptTemporaryLine.objects.filter(
                            document=OuterRef('pk'),
                            is_enabled=1
                        )
                    )
                ).order_by('-document_date', 'document_code')
                
                # Custom label: show only document_code
                form.base_fields['temporary_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
            
            # Filter purchase_request queryset: only from same company
            if 'purchase_request' in form.base_fields:
                form.base_fields['purchase_request'].queryset = models.PurchaseRequest.objects.filter(
                    company_id=active_company_id
                ).order_by('-request_date', 'request_code')
                
                # Custom label: show only request_code
                form.base_fields['purchase_request'].label_from_instance = lambda obj: f"{obj.request_code}"
        
        return form
    
    def save_model(self, request, obj, form, change):
        """Auto-set company from session and handle document code generation."""
        # Auto-set company from session if not set
        if not obj.company_id:
            active_company_id = request.session.get('active_company_id')
            if active_company_id:
                obj.company_id = active_company_id
        
        # Auto-set created_by if creating new
        if not change:
            obj.created_by = request.user
        
        # Auto-generate document_code if not set
        if not obj.document_code:
            from inventory.forms.base import generate_document_code
            obj.document_code = generate_document_code(models.ReceiptPermanent, obj.company_id, "PRM")
        
        # Auto-set document_date if not set
        if not obj.document_date:
            from django.utils import timezone
            obj.document_date = timezone.now().date()
        
        # Auto-set requires_temporary_receipt based on temporary_receipt
        if obj.temporary_receipt:
            obj.requires_temporary_receipt = 1
        else:
            obj.requires_temporary_receipt = 0
        
        # Save the object
        super().save_model(request, obj, form, change)
        
        # Handle temporary receipt conversion (same logic as form)
        if obj.temporary_receipt:
            temp = obj.temporary_receipt
            updated_fields = set()
            if temp.is_locked != 1:
                temp.is_locked = 1
                updated_fields.add('is_locked')
            if temp.is_converted != 1:
                temp.is_converted = 1
                updated_fields.add('is_converted')
            if temp.converted_receipt_id != obj.id:
                temp.converted_receipt = obj
                temp.converted_receipt_code = obj.document_code
                updated_fields.update({'converted_receipt', 'converted_receipt_code'})
            if updated_fields:
                temp.edited_by = obj.edited_by or obj.created_by or temp.edited_by
                updated_fields.add('edited_by')
                temp.save(update_fields=list(updated_fields))


@admin.register(models.ReceiptConsignment)
class ReceiptConsignmentAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date", "ownership_status", "is_enabled")
    list_filter = ("company", "ownership_status", "is_enabled")
    search_fields = ("document_code",)


@admin.register(models.ItemLot)
class ItemLotAdmin(ModelAdmin):
    list_display = ("company", "lot_code", "item", "status", "quantity")
    list_filter = ("company", "status")
    search_fields = ("lot_code", "item__item_code", "receipt_document_code")
    autocomplete_fields = ["item"]


@admin.register(models.IssuePermanent)
class IssuePermanentAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date", "is_locked")
    list_filter = ("company", "is_locked")
    search_fields = ("document_code",)


@admin.register(models.IssueConsumption)
class IssueConsumptionAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date", "is_locked")
    list_filter = ("company", "is_locked")
    search_fields = ("document_code",)


@admin.register(models.IssueConsignment)
class IssueConsignmentAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date")
    list_filter = ("company", "is_enabled")
    search_fields = ("document_code",)


@admin.register(models.StocktakingDeficit)
class StocktakingDeficitAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date", "stocktaking_session_id", "is_locked")
    list_filter = ("company", "is_locked")
    search_fields = ("document_code",)


@admin.register(models.StocktakingSurplus)
class StocktakingSurplusAdmin(ModelAdmin):
    list_display = ("company", "document_code", "document_date", "stocktaking_session_id", "is_locked")
    list_filter = ("company", "is_locked")
    search_fields = ("document_code",)


@admin.register(models.StocktakingRecord)
class StocktakingRecordAdmin(ModelAdmin):
    list_display = ("company", "document_code", "stocktaking_session_id", "approval_status", "is_enabled")
    list_filter = ("company", "approval_status", "is_enabled")
    search_fields = ("document_code", "confirmed_by__first_name", "confirmed_by__last_name")


@admin.register(models.WarehouseRequest)
class WarehouseRequestAdmin(ModelAdmin):
    list_display = ("company", "request_code", "item", "quantity_requested", "request_status", "priority", "needed_by_date")
    list_filter = ("company", "request_status", "priority", "warehouse", "request_date")
    search_fields = ("request_code", "item_code", "purpose")
    readonly_fields = ("request_code", "item_code", "warehouse_code", "department_unit_code")
    autocomplete_fields = ["item", "warehouse", "requester"]

"""
Receipt forms for inventory module.

This module contains forms for:
- Temporary Receipts
- Permanent Receipts (with line items)
- Consignment Receipts (with line items)
"""
from collections import deque
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any

from django import forms
from django.forms import inlineformset_factory
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from inventory.models import (
    Item,
    ItemUnit,
    Warehouse,
    Supplier,
    ReceiptTemporary,
    ReceiptTemporaryLine,
    ReceiptPermanent,
    ReceiptConsignment,
    ReceiptPermanentLine,
    ReceiptConsignmentLine,
    PurchaseRequest,
    WarehouseRequest,
)
from inventory.forms.base import (
    UNIT_CHOICES,
    ReceiptBaseForm,
    generate_document_code,
    BaseLineFormSet,
)
from inventory.widgets import JalaliDateInput
import logging

logger = logging.getLogger('inventory.forms.receipt')


class ReceiptTemporaryForm(forms.ModelForm):
    """Header-only form for temporary receipt documents with multi-line support."""

    class Meta:
        model = ReceiptTemporary
        fields = [
            'document_code',
            'document_date',
            'expected_receipt_date',
            'supplier',
            'source_document_type',
            'source_document_code',
            'status',
            'qc_approval_notes',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
            'expected_receipt_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'source_document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'source_document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.HiddenInput(),
            'qc_approval_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'document_code': _('Document Code'),
            'document_date': _('Document Date'),
            'expected_receipt_date': _('Expected Conversion Date'),
            'supplier': _('Supplier'),
            'source_document_type': _('Source Document Type'),
            'source_document_code': _('Source Document Code'),
            'status': _('Status'),
            'qc_approval_notes': _('QC Notes'),
        }

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required and hidden (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
            self.fields['document_code'].widget = forms.HiddenInput()
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            self.fields['document_date'].widget = forms.HiddenInput()
            # Set initial value to today if creating new
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        
        if 'status' in self.fields:
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['status'].required = False
            if not self.instance.pk:
                self.fields['status'].initial = ReceiptTemporary.Status.DRAFT
        
        if self.company_id:
            self._filter_company_scoped_fields()

    def _filter_company_scoped_fields(self) -> None:
        """Filter querysets based on active company."""
        from inventory.forms.base import ReceiptBaseForm
        if 'supplier' in self.fields:
            from inventory.models import Supplier
            self.fields['supplier'].queryset = Supplier.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['supplier'].label_from_instance = lambda obj: f"{obj.name} · {obj.public_code}"
            self.fields['supplier'].empty_label = _("--- انتخاب کنید ---")

    def clean_document_code(self) -> str:
        """Auto-generate document_code if not provided."""
        document_code = self.cleaned_data.get('document_code', '').strip()
        if not document_code:
            # Will be generated in save() method
            return ''
        return document_code
    
    def clean_document_date(self):
        """Auto-generate document_date if not provided."""
        document_date = self.cleaned_data.get('document_date')
        if not document_date:
            # Return today's date as default
            return timezone.now().date()
        return document_date

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Ensure document_code and document_date are set (will be generated in save if empty)
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        if self.company_id:
            if cleaned_data.get('supplier'):
                supplier = cleaned_data.get('supplier')
                if supplier.company_id != self.company_id:
                    self.add_error('supplier', _('Selected supplier belongs to a different company.'))
        return cleaned_data

    def save(self, commit: bool = True):
        """Save form instance."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptTemporary, instance.company_id, "TMP")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.status = self.cleaned_data.get('status') or ReceiptTemporary.Status.DRAFT
        instance.is_locked = getattr(self.instance, 'is_locked', 0) or 0
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ReceiptPermanentForm(forms.ModelForm):
    """Header-only form for permanent receipt documents with multi-line support."""

    class Meta:
        model = ReceiptPermanent
        fields = [
            'document_code',
            'document_date',
            'temporary_receipt',
            'purchase_request',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
        }

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required and hidden (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
            self.fields['document_code'].widget = forms.HiddenInput()
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            self.fields['document_date'].widget = forms.HiddenInput()
            # Set initial value to today if creating new
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id:
            if 'temporary_receipt' in self.fields:
                # Only show temporary receipts that are QC approved and not yet converted
                self.fields['temporary_receipt'].queryset = ReceiptTemporary.objects.filter(
                    company_id=self.company_id,
                    qc_approved_by__isnull=False,  # Must be QC approved
                    qc_approved_at__isnull=False,   # Must have approval date
                    status=ReceiptTemporary.Status.APPROVED,
                    is_converted=0,  # Not yet converted
                    is_enabled=1
                ).order_by('-document_date', 'document_code')
                self.fields['temporary_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
            
            if 'purchase_request' in self.fields:
                self.fields['purchase_request'].queryset = PurchaseRequest.objects.filter(
                    company_id=self.company_id
                ).order_by('-request_date', 'request_code')
                self.fields['purchase_request'].label_from_instance = lambda obj: f"{obj.request_code}"

    def clean_document_code(self) -> str:
        """Auto-generate document_code if not provided."""
        document_code = self.cleaned_data.get('document_code', '').strip()
        if not document_code:
            # Will be generated in save() method
            return ''
        return document_code
    
    def clean_document_date(self):
        """Auto-generate document_date if not provided."""
        document_date = self.cleaned_data.get('document_date')
        if not document_date:
            # Return today's date as default
            return timezone.now().date()
        return document_date

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Ensure document_code and document_date are set (will be generated in save if empty)
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        if self.company_id:
            if cleaned_data.get('temporary_receipt'):
                temp = cleaned_data.get('temporary_receipt')
                if temp.company_id != self.company_id:
                    self.add_error('temporary_receipt', _('Selected temporary receipt belongs to a different company.'))
            if cleaned_data.get('purchase_request'):
                pr = cleaned_data.get('purchase_request')
                if pr.company_id != self.company_id:
                    self.add_error('purchase_request', _('Selected purchase request belongs to a different company.'))
        return cleaned_data

    def save(self, commit: bool = True):
        """Save form instance."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptPermanent, instance.company_id, "PRM")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        # Automatically set requires_temporary_receipt based on whether temporary_receipt is selected
        if self.cleaned_data.get('temporary_receipt'):
            instance.requires_temporary_receipt = 1
        else:
            instance.requires_temporary_receipt = 0
        
        if commit:
            instance.save()
            # Handle temporary receipt conversion
            if instance.temporary_receipt:
                temp = instance.temporary_receipt
                updated_fields = set()
                if temp.is_locked != 1:
                    temp.is_locked = 1
                    updated_fields.add('is_locked')
                if temp.is_converted != 1:
                    temp.is_converted = 1
                    updated_fields.add('is_converted')
                if temp.converted_receipt_id != instance.id:
                    temp.converted_receipt = instance
                    temp.converted_receipt_code = instance.document_code
                    updated_fields.update({'converted_receipt', 'converted_receipt_code'})
                if updated_fields:
                    temp.edited_by = instance.edited_by or instance.created_by or temp.edited_by
                    updated_fields.add('edited_by')
                    temp.save(update_fields=list(updated_fields))
        return instance


class ReceiptConsignmentForm(forms.ModelForm):
    """Header-only form for consignment receipt documents with multi-line support."""

    requires_temporary_receipt = forms.BooleanField(
        required=False,
        label=_('Requires Temporary Receipt'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = ReceiptConsignment
        fields = [
            'document_code',
            'document_date',
            'consignment_contract_code',
            'expected_return_date',
            'valuation_method',
            'requires_temporary_receipt',
            'temporary_receipt',
            'purchase_request',
            'warehouse_request',
            'ownership_status',
            'conversion_receipt',
            'conversion_date',
            'return_document_id',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
            'consignment_contract_code': forms.TextInput(attrs={'class': 'form-control'}),
            'expected_return_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'ownership_status': forms.TextInput(attrs={'class': 'form-control'}),
            'conversion_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'return_document_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required (they're auto-generated, already hidden in Meta)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            # Set initial value to today if creating new
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id:
            if 'temporary_receipt' in self.fields:
                self.fields['temporary_receipt'].queryset = ReceiptTemporary.objects.filter(
                    company_id=self.company_id
                ).order_by('-document_date', 'document_code')
                self.fields['temporary_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
            
            if 'purchase_request' in self.fields:
                self.fields['purchase_request'].queryset = PurchaseRequest.objects.filter(
                    company_id=self.company_id
                ).order_by('-request_date', 'request_code')
                self.fields['purchase_request'].label_from_instance = lambda obj: f"{obj.request_code}"
            
            if 'warehouse_request' in self.fields:
                self.fields['warehouse_request'].queryset = WarehouseRequest.objects.filter(
                    company_id=self.company_id
                ).order_by('-needed_by_date', 'request_code')
                self.fields['warehouse_request'].label_from_instance = lambda obj: f"{obj.request_code}"
            
            if 'conversion_receipt' in self.fields:
                self.fields['conversion_receipt'].queryset = ReceiptPermanent.objects.filter(
                    company_id=self.company_id
                ).order_by('-document_date', 'document_code')
                self.fields['conversion_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
        
        if self.instance.pk:
            self.fields['requires_temporary_receipt'].initial = bool(self.instance.requires_temporary_receipt)

    def clean_document_code(self) -> str:
        """Auto-generate document_code if not provided."""
        document_code = self.cleaned_data.get('document_code', '').strip()
        if not document_code:
            # Will be generated in save() method
            return ''
        return document_code
    
    def clean_document_date(self):
        """Auto-generate document_date if not provided."""
        document_date = self.cleaned_data.get('document_date')
        if not document_date:
            # Return today's date as default
            return timezone.now().date()
        return document_date

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Ensure document_code and document_date are set (will be generated in save if empty)
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        if self.company_id:
            if cleaned_data.get('temporary_receipt'):
                temp = cleaned_data.get('temporary_receipt')
                if temp.company_id != self.company_id:
                    self.add_error('temporary_receipt', _('Selected temporary receipt belongs to a different company.'))
            if cleaned_data.get('purchase_request'):
                pr = cleaned_data.get('purchase_request')
                if pr.company_id != self.company_id:
                    self.add_error('purchase_request', _('Selected purchase request belongs to a different company.'))
            if cleaned_data.get('warehouse_request'):
                wr = cleaned_data.get('warehouse_request')
                if wr.company_id != self.company_id:
                    self.add_error('warehouse_request', _('Selected warehouse request belongs to a different company.'))
            if cleaned_data.get('conversion_receipt'):
                cr = cleaned_data.get('conversion_receipt')
                if cr.company_id != self.company_id:
                    self.add_error('conversion_receipt', _('Selected conversion receipt belongs to a different company.'))
        return cleaned_data

    def save(self, commit: bool = True):
        """Save form instance."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptConsignment, instance.company_id, "CNG")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        if commit:
            instance.save()
        return instance


class ReceiptLineBaseForm(forms.ModelForm):
    """Base form for receipt line items."""
    
    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        logger.info("=" * 80)
        logger.info("ReceiptLineBaseForm.__init__() called")
        logger.info(f"company_id parameter: {company_id}")
        logger.info(f"kwargs keys: {list(kwargs.keys())}")
        if 'instance' in kwargs:
            instance = kwargs['instance']
            # Don't log instance directly as it may trigger __str__ which accesses document
            if instance:
                logger.info(f"Instance from kwargs: pk={getattr(instance, 'pk', None)}, item_id={getattr(instance, 'item_id', None)}, document_id={getattr(instance, 'document_id', None)}")
            else:
                logger.info("Instance from kwargs: None")
        super().__init__(*args, **kwargs)
        # Don't log self.instance directly as it may trigger __str__ which accesses document
        logger.info(f"After super().__init__(), instance pk: {getattr(self.instance, 'pk', None)}")
        logger.info(f"Instance item_id: {getattr(self.instance, 'item_id', None)}")
        logger.info(f"Instance document_id: {getattr(self.instance, 'document_id', None)}")
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        logger.info(f"Final company_id: {self.company_id}")
        self._unit_factor = Decimal('1')
        self._entered_unit_value = None
        self._entered_quantity_value = None
        
        if self.company_id:
            if 'item' in self.fields:
                logger.info("Setting up item field queryset")
                # For existing instances, include the current item even if disabled
                # Use models.Item instead of Item to avoid UnboundLocalError
                from .. import models
                queryset = models.Item.objects.filter(company_id=self.company_id, is_enabled=1)
                logger.info(f"Initial queryset count (enabled only): {queryset.count()}")
                
                # Collect item IDs that should be included (from instance or initial data)
                item_ids_to_include = []
                
                # Include item from instance if it exists
                if getattr(self.instance, 'pk', None) and getattr(self.instance, 'item_id', None):
                    item_ids_to_include.append(self.instance.item_id)
                    logger.info(f"Instance has pk and item_id={self.instance.item_id}, will include in queryset")
                
                # Include item from initial data if it exists (for formsets with pre-populated data)
                if 'item' in self.initial and self.initial['item']:
                    initial_item_id = self.initial['item']
                    if isinstance(initial_item_id, models.Item):
                        initial_item_id = initial_item_id.pk
                    if initial_item_id and initial_item_id not in item_ids_to_include:
                        item_ids_to_include.append(initial_item_id)
                        logger.info(f"Initial data has item_id={initial_item_id}, will include in queryset")
                
                # Build queryset with included items
                if item_ids_to_include:
                    logger.info(f"Including {len(item_ids_to_include)} items in queryset: {item_ids_to_include}")
                    queryset = models.Item.objects.filter(
                        company_id=self.company_id
                    ).filter(
                        Q(is_enabled=1) | Q(pk__in=item_ids_to_include)
                    )
                    logger.info(f"Final queryset count (with included items): {queryset.count()}")
                    for item_id in item_ids_to_include:
                        in_queryset = queryset.filter(pk=item_id).exists()
                        logger.info(f"Item_id={item_id} in queryset: {in_queryset}")
                else:
                    logger.info("No items to include, using enabled items only")
                
                self.fields['item'].queryset = queryset.order_by('name')
                self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
                logger.info(f"Item field queryset set, count: {self.fields['item'].queryset.count()}")
                if self.instance.item_id:
                    in_queryset = self.fields['item'].queryset.filter(pk=self.instance.item_id).exists()
                    logger.info(f"Instance item_id={self.instance.item_id} in queryset: {in_queryset}")
            
            if 'warehouse' in self.fields:
                # First, try to get item to set warehouse queryset based on allowed warehouses
                item = None
                if getattr(self.instance, 'item_id', None):
                    try:
                        from .. import models
                        item = models.Item.objects.filter(pk=self.instance.item_id, company_id=self.company_id).first()
                    except Exception:
                        pass
                
                if item:
                    # Set warehouse queryset based on item's allowed warehouses
                    self._set_warehouse_queryset(item=item)
                else:
                    # Fallback: For existing instances, include the current warehouse even if disabled
                    queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
                    if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                        # Include the current warehouse even if it's disabled
                        queryset = Warehouse.objects.filter(
                            company_id=self.company_id
                        ).filter(
                            Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                        )
                    self.fields['warehouse'].queryset = queryset.order_by('name')
                    self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            
            if 'supplier' in self.fields:
                # For existing instances, include the current supplier even if disabled
                queryset = Supplier.objects.filter(company_id=self.company_id, is_enabled=1)
                if getattr(self.instance, 'pk', None) and getattr(self.instance, 'supplier_id', None):
                    # Include the current supplier even if it's disabled
                    queryset = Supplier.objects.filter(
                        company_id=self.company_id
                    ).filter(
                        Q(is_enabled=1) | Q(pk=self.instance.supplier_id)
                    )
                self.fields['supplier'].queryset = queryset.order_by('name')
                self.fields['supplier'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
        
        # Set unit choices - use all UNIT_CHOICES initially (will be filtered by JavaScript)
        if 'unit' in self.fields:
            self.fields['unit'].choices = UNIT_CHOICES
        
        
        # Restore entered values if editing
        logger.info(f"Form is_bound: {self.is_bound}")
        logger.info(f"Instance has pk: {getattr(self.instance, 'pk', None) is not None}")
        if not self.is_bound and getattr(self.instance, 'pk', None):
            logger.info("Restoring entered values for existing instance")
            # Get item first to set unit choices properly
            # Use item_id to avoid RelatedObjectDoesNotExist if document is missing
            item_id = getattr(self.instance, 'item_id', None)
            item = None
            if item_id:
                # Check if document exists before accessing item (to avoid RelatedObjectDoesNotExist)
                document_id = getattr(self.instance, 'document_id', None)
                if document_id:
                    try:
                        # Try to get item directly by item_id to avoid accessing through instance
                        from ..models import Item
                        item = Item.objects.filter(pk=item_id, company_id=self.company_id).first()
                        if item:
                            logger.info(f"Instance item: {item.name} ({item.item_code})")
                        else:
                            # Fallback: try to access through instance
                            item = getattr(self.instance, 'item', None)
                            if item:
                                logger.info(f"Instance item (via instance): {item.name} ({item.item_code})")
                    except Exception as e:
                        logger.warning(f"Could not access instance.item: {e}, using item_id={item_id}")
                else:
                    logger.info(f"Instance has no document_id, cannot access item. item_id={item_id}")
                    # Try to get item directly by item_id
                    try:
                        from ..models import Item
                        item = Item.objects.filter(pk=item_id, company_id=self.company_id).first()
                        if item:
                            logger.info(f"Instance item (direct lookup): {item.name} ({item.item_code})")
                    except Exception as e:
                        logger.warning(f"Could not get item directly: {e}")
            else:
                logger.info("Instance has no item_id")
            if item and 'unit' in self.fields:
                logger.info("Setting unit choices for item")
                # Set unit choices based on item
                self._set_unit_choices_for_item(item)
            
            # Set warehouse queryset based on item (for existing instances)
            if item and 'warehouse' in self.fields:
                logger.info("Setting warehouse queryset for item")
                self._set_warehouse_queryset(item=item)
            
            # Get unit value from entered_unit or unit (prioritize entered_unit for display)
            entry_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
            logger.info(f"Entry unit: {entry_unit}")
            if 'unit' in self.fields and entry_unit:
                # Ensure the unit is in choices, if not add it
                unit_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in unit_choices]
                if entry_unit not in unit_codes:
                    # Add current unit to choices if not present
                    self.fields['unit'].choices = unit_choices + [(entry_unit, entry_unit)]
                
                # Django ChoiceField uses instance.field for display when editing
                # So we need to set instance.unit to the entered_unit for proper display
                if hasattr(self.instance, 'unit'):
                    # Store the original unit if we're changing it
                    if not hasattr(self.instance, '_original_unit'):
                        self.instance._original_unit = self.instance.unit
                    # Set unit to entered_unit for display purposes
                    self.instance.unit = entry_unit
                
                # Also set initial as backup
                self.initial['unit'] = entry_unit
            
            if 'quantity' in self.fields and getattr(self.instance, 'entered_quantity', None) is not None:
                self.initial['quantity'] = self.instance.entered_quantity
    
    def _set_unit_choices_for_item(self, item: Optional[Item]) -> None:
        """Set unit choices based on item."""
        if not item or 'unit' not in self.fields:
            return
        
        placeholder = UNIT_CHOICES[0]
        allowed = self._get_item_allowed_units(item)
        if allowed:
            unit_choices = [placeholder] + [(row['value'], row['label']) for row in allowed]
        else:
            unit_choices = [placeholder]
        
        # Ensure current unit is in choices
        current_unit = getattr(self.instance, 'unit', '') or getattr(self.instance, 'entered_unit', '')
        if current_unit:
            unit_codes = [code for code, _ in unit_choices]
            if current_unit not in unit_codes:
                unit_choices.append((current_unit, current_unit))
        
        self.fields['unit'].choices = unit_choices
    
    def clean_item(self) -> Optional[Item]:
        """Clean item and update unit and warehouse choices."""
        item = self.cleaned_data.get('item')
        
        # Update warehouse queryset based on allowed warehouses
        if item:
            self._set_warehouse_queryset(item=item)
        
        return item
    
    def clean_warehouse(self) -> Optional[Warehouse]:
        """Validate warehouse against item's allowed warehouses."""
        warehouse = self.cleaned_data.get('warehouse')
        item = self.cleaned_data.get('item')
        
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    raise forms.ValidationError(
                        _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.')
                    )
            else:
                # No warehouses configured for this item - this is an error
                raise forms.ValidationError(
                    _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.')
                )
        
        return warehouse
    
    def clean_unit(self) -> str:
        """Validate unit."""
        unit = self.cleaned_data.get('unit')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item:
            allowed = {row['value'] for row in self._get_item_allowed_units(item)}
            if unit and unit not in allowed:
                raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        return unit
    
    def _get_item_allowed_warehouses(self, item: Optional[Item]) -> list:
        """Get list of allowed warehouses for an item."""
        if not item:
            return []
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]
        # IMPORTANT: If no warehouses configured, this means the item CANNOT be received anywhere
        # Only return warehouses if explicitly configured
        # This enforces strict warehouse restrictions
        return [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]
    
    def _set_warehouse_queryset(self, item: Optional[Item] = None) -> None:
        """Set warehouse field queryset based on selected item's allowed warehouses."""
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        
        # If item not provided, try to resolve it
        if item is None:
            item = self._resolve_item()
        
        if item:
            allowed_ids = [int(option['value']) for option in self._get_item_allowed_warehouses(item)]
            if allowed_ids:
                # Only show allowed warehouses
                # For existing instances, include the current warehouse even if disabled
                queryset = Warehouse.objects.filter(pk__in=allowed_ids, is_enabled=1)
                if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                    # Include the current warehouse even if it's disabled
                    queryset = Warehouse.objects.filter(
                        pk__in=allowed_ids
                    ).filter(
                        Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                    )
                warehouse_field.queryset = queryset.order_by('name')
                return
            else:
                # No warehouses configured - show empty queryset (will show error in validation)
                # But include current warehouse if editing
                if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                    warehouse_field.queryset = Warehouse.objects.filter(pk=self.instance.warehouse_id)
                else:
                    warehouse_field.queryset = Warehouse.objects.none()
                return
        
        # Fallback: show all warehouses in company if no item selected
        if self.company_id:
            # For existing instances, include the current warehouse even if disabled
            queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
            if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                # Include the current warehouse even if it's disabled
                queryset = Warehouse.objects.filter(
                    company_id=self.company_id
                ).filter(
                    Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                )
            warehouse_field.queryset = queryset.order_by('name')
    
    def _resolve_item(self, candidate: Any = None) -> Optional[Item]:
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        # Check form data (POST)
        if self.data:
            item_key = None
            for key in self.data.keys():
                if key.endswith('-item'):
                    item_key = key
                    break
            if item_key:
                try:
                    item_id = self.data.get(item_key)
                    if item_id:
                        return Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        # Check instance (for edit mode)
        item_id = getattr(self.instance, 'item_id', None)
        if item_id:
            # Check if instance has document before accessing item (to avoid RelatedObjectDoesNotExist)
            if hasattr(self.instance, 'document_id') and self.instance.document_id:
                try:
                    return self.instance.item
                except Exception:
                    # If document doesn't exist, try to get item directly by item_id
                    try:
                        return Item.objects.get(pk=item_id, company_id=self.company_id)
                    except Item.DoesNotExist:
                        pass
            else:
                # Instance has no document, get item directly by item_id
                try:
                    return Item.objects.get(pk=item_id, company_id=self.company_id)
                except Item.DoesNotExist:
                    pass
        # Check initial data (for new forms with pre-selected item)
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None
    
    def _get_item_allowed_units(self, item: Optional[Item]) -> list:
        """Get list of allowed units for an item."""
        if not item:
            return []
        codes = []
        
        def add(code: str) -> None:
            if code and code not in codes:
                codes.append(code)
        
        # Add default and primary units (always add both, even if same or None)
        add(item.default_unit)
        add(item.primary_unit)
        
        # Add units from ItemUnit conversions
        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]
    
    def _get_unit_factor(self, item: Item, unit_code: str) -> Decimal:
        """Calculate conversion factor from unit_code to item's default_unit."""
        default_unit = item.default_unit
        if not unit_code or unit_code == default_unit:
            return Decimal('1')
        
        graph = {}
        for conversion in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            from_qty = conversion.from_quantity
            to_qty = conversion.to_quantity
            if from_qty in (None, 0) or to_qty in (None, 0):
                continue
            graph.setdefault(conversion.from_unit, []).append((conversion.to_unit, to_qty / from_qty))
            graph.setdefault(conversion.to_unit, []).append((conversion.from_unit, from_qty / to_qty))
        
        visited = set()
        queue = deque([(unit_code, Decimal('1'))])
        while queue:
            unit, factor = queue.popleft()
            if unit == default_unit:
                return factor
            if unit in visited:
                continue
            visited.add(unit)
            for neighbor, ratio in graph.get(unit, []):
                queue.append((neighbor, factor * ratio))
        
        return Decimal('1')
    
    def _validate_unit(self, cleaned_data: Dict[str, Any]) -> None:
        """Validate unit and calculate conversion factor."""
        self._unit_factor = Decimal('1')
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        unit = cleaned_data.get('unit') or item.default_unit
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        allowed.add(item.default_unit)
        if unit not in allowed:
            self.add_error('unit', _('Selected unit is not configured for this item.'))
        factor = self._get_unit_factor(item, unit)
        self._unit_factor = factor
        self._entered_unit_value = unit
        cleaned_data['unit'] = item.default_unit
    
    def _normalize_quantity(self, cleaned_data: Dict[str, Any]) -> None:
        """Normalize quantity to base unit and save entered value."""
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        quantity = cleaned_data.get('quantity')
        if not item or quantity in (None, ''):
            return
        factor = getattr(self, '_unit_factor', Decimal('1'))
        if not isinstance(quantity, Decimal):
            try:
                quantity = Decimal(str(quantity))
            except (InvalidOperation, TypeError):
                return
        
        self._entered_quantity_value = quantity
        cleaned_data['quantity'] = quantity * factor
        cleaned_data['unit'] = item.default_unit
        self.instance.unit = item.default_unit
        self.instance.quantity = cleaned_data['quantity']
    
    def clean(self) -> Dict[str, Any]:
        """Validate and normalize form data."""
        cleaned_data = super().clean()
        self._validate_unit(cleaned_data)
        self._normalize_quantity(cleaned_data)
        return cleaned_data
    
    def save(self, commit: bool = True):
        """Save form instance with entered values."""
        instance = super().save(commit=False)
        
        # Save entered unit and quantity
        entered_unit = self._entered_unit_value or getattr(instance, 'entered_unit', '') or instance.unit
        instance.entered_unit = entered_unit
        if self._entered_quantity_value is not None:
            instance.entered_quantity = self._entered_quantity_value
        elif instance.entered_quantity is None:
            instance.entered_quantity = instance.quantity
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ReceiptPermanentLineForm(ReceiptLineBaseForm):
    """Form for permanent receipt line items."""
    
    class Meta:
        model = ReceiptPermanentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'supplier',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean_item(self) -> Optional[Item]:
        """Clean item and validate that items requiring temporary receipt cannot be added directly."""
        item = super().clean_item()
        
        # Check if item requires temporary receipt
        if item and item.requires_temporary_receipt == 1:
            # Check if temporary receipt is selected (passed from view)
            if hasattr(self, '_temp_receipt') and self._temp_receipt:
                # Temporary receipt is selected, so this item is allowed
                return item
            
            # Check if temporary receipt is selected in the parent document
            # Document is already saved at this point, so we can check it
            if hasattr(self, 'instance') and self.instance:
                # Try to get document from instance
                parent_doc = getattr(self.instance, 'document', None)
                if parent_doc and parent_doc.temporary_receipt_id:
                    # Temporary receipt is selected, so this item is allowed
                    return item
                
                # For new instances, document might not be set yet
                # Try to get it from formset's instance
                if hasattr(self, 'formset') and self.formset and hasattr(self.formset, 'instance'):
                    parent_doc = self.formset.instance
                    if parent_doc and parent_doc.temporary_receipt_id:
                        # Temporary receipt is selected, so this item is allowed
                        return item
            
            # For new instances, check POST data to see if temporary_receipt is selected
            # Try to get it from formset's data if available
            if hasattr(self, 'formset') and self.formset and hasattr(self.formset, 'data'):
                temp_receipt_id = self.formset.data.get('temporary_receipt', '')
                if temp_receipt_id:
                    # Temporary receipt is selected, so this item is allowed
                    return item
            
            # Also check self.data directly
            if hasattr(self, 'data') and self.data:
                temp_receipt_id = self.data.get('temporary_receipt', '')
                if temp_receipt_id:
                    # Temporary receipt is selected, so this item is allowed
                    return item
            
            raise forms.ValidationError(
                _('این کالا نیاز به رسید موقت دارد. لطفاً ابتدا رسید موقت ایجاد کنید و پس از تایید QC، رسید دائم را ثبت کنید.')
            )
        
        return item


class ReceiptConsignmentLineForm(ReceiptLineBaseForm):
    """Form for consignment receipt line items."""
    
    class Meta:
        model = ReceiptConsignmentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'supplier',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# Create formsets
ReceiptPermanentLineFormSet = inlineformset_factory(
    ReceiptPermanent,
    ReceiptPermanentLine,
    form=ReceiptPermanentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

ReceiptConsignmentLineFormSet = inlineformset_factory(
    ReceiptConsignment,
    ReceiptConsignmentLine,
    form=ReceiptConsignmentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ReceiptTemporaryLineForm(ReceiptLineBaseForm):
    """Form for temporary receipt line items."""
    
    class Meta:
        model = ReceiptTemporaryLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'expected_receipt_date',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'expected_receipt_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'expected_receipt_date': _('Expected Conversion Date'),
            'line_notes': _('Notes'),
        }


# Create formsets
ReceiptTemporaryLineFormSet = inlineformset_factory(
    ReceiptTemporary,
    ReceiptTemporaryLine,
    form=ReceiptTemporaryLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


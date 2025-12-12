"""
Base forms and helper functions for inventory forms.

This module contains:
- Helper functions (get_feature_approvers, generate_document_code, etc.)
- Constants (UNIT_CHOICES)
- Base form classes (ReceiptBaseForm, IssueBaseForm, StocktakingBaseForm, etc.)
- Base formset classes (BaseLineFormSet)
"""
from collections import deque
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any, List

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger('inventory.forms.base')

from inventory.models import (
    Item,
    ItemUnit,
    Warehouse,
    Supplier,
    ReceiptTemporary,
    ReceiptPermanent,
    PurchaseRequest,
    WarehouseRequest,
    ReceiptConsignment,
    ItemSerial,
    CURRENCY_CHOICES,
)
from shared.models import CompanyUnit
from inventory.fields import JalaliDateField
from inventory.widgets import JalaliDateInput

# WorkLine moved to production module
from shared.utils.modules import get_work_line_model
WorkLine = get_work_line_model()

User = get_user_model()

# Unit choices constant
UNIT_CHOICES = [
    ("", _("--- انتخاب کنید ---")),
    ("EA", _("عدد (EA)")),
    ("KG", _("کیلوگرم (KG)")),
    ("G", _("گرم (G)")),
    ("TON", _("تن")),
    ("L", _("لیتر (L)")),
    ("ML", _("میلی‌لیتر (ML)")),
    ("M", _("متر (M)")),
    ("CM", _("سانتی‌متر (CM)")),
    ("MM", _("میلی‌متر (MM)")),
    ("M2", _("متر مربع (M²)")),
    ("M3", _("متر مکعب (M³)")),
    ("BOX", _("بسته (BOX)")),
    ("CARTON", _("کارتن")),
    ("PAIR", _("جفت")),
    ("ROLL", _("رول")),
    ("SET", _("ست")),
]


def get_purchase_request_approvers(company_id: Optional[int]) -> Any:
    """
    Get queryset of User objects that can approve purchase requests.
    
    Args:
        company_id: Company ID to filter approvers
        
    Returns:
        QuerySet of User objects with approval permission
    """
    return get_feature_approvers("inventory.requests.purchase", company_id)


def generate_document_code(model: Any, company_id: int, prefix: str) -> str:
    """
    Generate a sequential document code for a model.
    
    Format: {PREFIX}-{YYYYMM}-{SEQUENCE}
    Example: PRM-202511-000001
    
    Args:
        model: Django model class
        company_id: Company ID
        prefix: Prefix for the document code (e.g., "PRM", "TMP")
        
    Returns:
        Generated document code string
    """
    today = timezone.now()
    month_year = today.strftime("%Y%m")
    base = f"{prefix}-{month_year}"
    last_code = (
        model.objects.filter(company_id=company_id, document_code__startswith=base)
        .order_by("-document_code")
        .values_list("document_code", flat=True)
        .first()
    )
    sequence = 0
    if last_code:
        try:
            sequence = int(last_code.split("-")[-1])
        except (ValueError, IndexError):
            sequence = 0
    return f"{base}-{sequence + 1:06d}"


def get_feature_approvers(feature_code: str, company_id: Optional[int]) -> Any:
    """
    Get queryset of User objects that can approve a specific feature.
    
    Args:
        feature_code: Feature permission code (e.g., "inventory.requests.purchase")
        company_id: Company ID to filter approvers
        
    Returns:
        QuerySet of User objects with approval permission
    """
    if not company_id:
        return User.objects.none()

    approved_users = User.objects.filter(
        Q(is_superuser=True)
        | Q(
            company_accesses__company_id=company_id,
            company_accesses__access_level__permissions__resource_code=feature_code,
            company_accesses__access_level__permissions__can_approve=1,
        )
        | Q(
            groups__profile__access_levels__permissions__resource_code=feature_code,
            groups__profile__access_levels__permissions__can_approve=1,
        )
    ).distinct()

    return approved_users.order_by('username', 'first_name', 'last_name')


class ReceiptBaseForm(forms.ModelForm):
    """Base helpers for receipt forms with company-aware querysets."""

    date_widget = JalaliDateInput(attrs={'class': 'form-control'})
    datetime_widget = forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local', 'step': 60},
        format='%Y-%m-%dT%H:%M',
    )

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """
        Initialize receipt base form.
        
        Args:
            company_id: Active company ID for filtering querysets
        """
        self.company_id = company_id or getattr(kwargs.get('instance'), 'company_id', None)
        self._unit_factor = Decimal('1')
        self._entered_unit_value = None
        self._entered_quantity_value = None
        self._entered_unit_price_value = None
        super().__init__(*args, **kwargs)

        if 'currency' in self.fields:
            self.fields['currency'].widget = forms.Select(attrs={'class': 'form-control'})
            self.fields['currency'].choices = [('', _('--- انتخاب کنید ---'))] + list(CURRENCY_CHOICES)
            self.fields['currency'].required = False

        if 'document_date' in self.fields:
            self.fields['document_date'].widget = self.date_widget
            self.fields['document_date'].required = False
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
            self.fields['document_date'].widget = forms.HiddenInput()
        if 'document_code' in self.fields:
            self.fields['document_code'].widget = forms.HiddenInput()
            self.fields['document_code'].required = False

        if self.company_id:
            self._filter_company_scoped_fields()
        
        # Set unit choices - this must be done before restoring initial values
        self._set_unit_choices()
        
        # Restore entered values if editing
        if not self.is_bound and getattr(self.instance, 'pk', None):
            entry_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
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
            entry_price = getattr(self.instance, 'entered_unit_price', None)
            if 'unit_price' in self.fields and entry_price is not None:
                self.initial['unit_price'] = entry_price
            if 'unit_price_estimate' in self.fields and entry_price is not None:
                self.initial['unit_price_estimate'] = entry_price
        
        if 'expected_return_date' in self.fields:
            self.fields['expected_return_date'].widget = self.date_widget
        if 'expected_receipt_date' in self.fields:
            self.fields['expected_receipt_date'].widget = self.date_widget
        if 'conversion_date' in self.fields:
            self.fields['conversion_date'].widget = self.date_widget
        if 'document_code' in self.fields:
            self.fields['document_code'].widget = forms.HiddenInput()
            self.fields['document_code'].required = False

    def _filter_company_scoped_fields(self) -> None:
        """Filter querysets based on active company."""
        if 'item' in self.fields:
            # For existing instances, include the current item even if disabled
            queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1)
            if getattr(self.instance, 'pk', None) and getattr(self.instance, 'item_id', None):
                # Include the current item even if it's disabled
                queryset = Item.objects.filter(
                    company_id=self.company_id
                ).filter(
                    Q(is_enabled=1) | Q(pk=self.instance.item_id)
                )
            self.fields['item'].queryset = queryset
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        if 'warehouse' in self.fields:
            # For existing instances, include the current warehouse even if disabled
            queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
            if getattr(self.instance, 'pk', None) and getattr(self.instance, 'warehouse_id', None):
                # Include the current warehouse even if it's disabled
                queryset = Warehouse.objects.filter(
                    company_id=self.company_id
                ).filter(
                    Q(is_enabled=1) | Q(pk=self.instance.warehouse_id)
                )
            self.fields['warehouse'].queryset = queryset
            self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.name} · {obj.public_code}"
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
            self.fields['supplier'].queryset = queryset
            self.fields['supplier'].label_from_instance = lambda obj: f"{obj.name} · {obj.public_code}"
        if 'temporary_receipt' in self.fields:
            self.fields['temporary_receipt'].queryset = ReceiptTemporary.objects.filter(company_id=self.company_id)
            self.fields['temporary_receipt'].label_from_instance = lambda obj: f"{obj.document_code} · {obj.item.name}"
        if 'purchase_request' in self.fields:
            self.fields['purchase_request'].queryset = PurchaseRequest.objects.filter(
                company_id=self.company_id,
                status=PurchaseRequest.Status.APPROVED,
            )
            self.fields['purchase_request'].label_from_instance = lambda obj: f"{obj.request_code} · {obj.item.name}"
        if 'warehouse_request' in self.fields:
            self.fields['warehouse_request'].queryset = WarehouseRequest.objects.filter(
                company_id=self.company_id,
                request_status='approved',
                is_locked=1,
            )
            self.fields['warehouse_request'].label_from_instance = lambda obj: f"{obj.request_code} · {obj.item.name}"
        if 'conversion_receipt' in self.fields:
            self.fields['conversion_receipt'].queryset = ReceiptPermanent.objects.filter(company_id=self.company_id)
            self.fields['conversion_receipt'].label_from_instance = lambda obj: f"{obj.document_code} · {obj.item.name}"

    def _clean_company_match(self, cleaned_data: Dict[str, Any], field_name: str, model_verbose: str) -> None:
        """Validate that selected object belongs to active company."""
        obj = cleaned_data.get(field_name)
        if obj and getattr(obj, 'company_id', None) != self.company_id:
            self.add_error(field_name, _('Selected %(model)s must belong to the active company.') % {'model': model_verbose})

    def _get_item_allowed_units(self, item: Optional[Item]) -> List[Dict[str, str]]:
        """Get list of allowed units for an item."""
        if not item:
            return []
        codes = []

        def add(code: str) -> None:
            if code and code not in codes:
                codes.append(code)

        add(item.default_unit)
        add(item.primary_unit)

        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)

        # If no units found, add default unit 'EA' as fallback
        if not codes:
            codes.append('EA')
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]

    def _resolve_item(self, candidate: Any = None) -> Optional[Item]:
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None

    def _set_unit_choices(self) -> None:
        """Set unit field choices based on selected item."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        item = self._resolve_item()
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            entry_unit = getattr(self.instance, 'entered_unit', None)
            if entry_unit and entry_unit not in [code for code, _ in allowed]:
                label_map = dict(allowed)
                allowed.append((entry_unit, label_map.get(entry_unit, entry_unit)))
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.choices = [placeholder]

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


class IssueBaseForm(ReceiptBaseForm):
    """Base form for issue documents."""

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize issue base form."""
        super().__init__(*args, company_id=company_id, **kwargs)
        self._serial_item = self._resolve_item()
        self._configure_serial_field()

    def _filter_company_scoped_fields(self) -> None:
        """Filter querysets based on active company."""
        super()._filter_company_scoped_fields()

        if 'department_unit' in self.fields:
            queryset = CompanyUnit.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['department_unit'].queryset = queryset
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.name}"
            self.fields['department_unit'].required = False

        if 'work_line' in self.fields and WorkLine:
            queryset = WorkLine.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['work_line'].queryset = queryset
            self.fields['work_line'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.name}"
            self.fields['work_line'].required = False

        if 'consignment_receipt' in self.fields:
            queryset = ReceiptConsignment.objects.filter(company_id=self.company_id)
            self.fields['consignment_receipt'].queryset = queryset
            self.fields['consignment_receipt'].label_from_instance = lambda obj: f"{obj.document_code} · {obj.item.name}"

    def _configure_serial_field(self) -> None:
        """Configure serial field based on item."""
        serial_field = self.fields.get('serials')
        if not serial_field:
            return

        item = self._serial_item
        if not item or item.has_lot_tracking != 1:
            self.fields.pop('serials', None)
            return

        queryset = ItemSerial.objects.filter(
            company_id=self.company_id,
            item=item,
        )
        status_filter = Q(current_status=ItemSerial.Status.AVAILABLE)
        if getattr(self.instance, 'pk', None):
            status_filter |= Q(
                current_status=ItemSerial.Status.RESERVED,
                current_document_type=self.instance.__class__.__name__,
                current_document_id=self.instance.pk,
            )
        serial_field.queryset = queryset.filter(status_filter).order_by("serial_code")
        serial_field.required = False
        serial_field.help_text = _('Use the "Assign Serials" action to manage serial numbers.')
        if getattr(self.instance, 'pk', None):
            serial_field.initial = self.instance.serials.values_list("pk", flat=True)

    def clean(self) -> Dict[str, Any]:
        """Validate and normalize form data."""
        cleaned_data = super().clean()

        if self.company_id:
            for field_name, verbose in [
                ('department_unit', _('unit')),
                ('work_line', _('work line')),
                ('consignment_receipt', _('consignment receipt')),
            ]:
                if field_name in self.fields and cleaned_data.get(field_name):
                    self._clean_company_match(cleaned_data, field_name, verbose)

            warehouse = cleaned_data.get('warehouse')
            work_line = cleaned_data.get('work_line')
            if warehouse and work_line and work_line.warehouse_id != warehouse.id:
                self.add_error('work_line', _('Selected work line belongs to a different warehouse.'))

        self._validate_serials(cleaned_data)
        return cleaned_data

    def _validate_serials(self, cleaned_data: Dict[str, Any]) -> None:
        """Validate serial numbers."""
        if 'serials' not in self.fields:
            return

        item = self._serial_item
        if not item or item.has_lot_tracking != 1:
            return

        selected_serials = cleaned_data.get('serials') or []
        quantity = cleaned_data.get('quantity')
        if quantity in (None, ''):
            quantity = getattr(self.instance, 'quantity', None)
        if quantity is None:
            return

        try:
            quantity_decimal = Decimal(quantity)
        except (InvalidOperation, TypeError):
            self.add_error('quantity', _('Quantity must be a whole number for serialised items.'))
            return

        expected = int(quantity_decimal)
        if quantity_decimal != Decimal(expected):
            self.add_error('quantity', _('Quantity must be a whole number for serialised items.'))
            return

        if len(selected_serials) != expected:
            self.add_error('serials', _('Select exactly %(count)s serial numbers.') % {'count': expected})

        invalid_serials = [serial for serial in selected_serials if serial.item_id != item.id]
        if invalid_serials:
            self.add_error('serials', _('Selected serial numbers do not belong to this item.'))


class StocktakingBaseForm(forms.ModelForm):
    """Shared helpers for stocktaking documents."""

    unit_placeholder = UNIT_CHOICES[0][1]

    def __init__(self, *args, company_id: Optional[int] = None, user: Optional[Any] = None, **kwargs):
        """Initialize stocktaking base form."""
        self.company_id = company_id or getattr(kwargs.get('instance'), 'company_id', None)
        self.user = user  # Store user for permission checks in subclasses
        self.date_widget = JalaliDateInput(attrs={'class': 'form-control'})
        self.datetime_widget = forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        super().__init__(*args, **kwargs)

        if 'document_date' in self.fields:
            self.fields['document_date'].widget = forms.HiddenInput()
            self.fields['document_date'].required = False
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        if 'inventory_snapshot_time' in self.fields:
            self.fields['inventory_snapshot_time'].widget = forms.HiddenInput()
            self.fields['inventory_snapshot_time'].required = False
            if not getattr(self.instance, 'pk', None):
                self.fields['inventory_snapshot_time'].initial = timezone.now()
        if 'approved_at' in self.fields:
            self.fields['approved_at'].widget = self.datetime_widget
            self.fields['approved_at'].required = False
            self.fields['approved_at'].input_formats = ['%Y-%m-%dT%H:%M']
        if 'document_code' in self.fields:
            self.fields['document_code'].widget = forms.HiddenInput()
            self.fields['document_code'].required = False
        for hidden_field in (
            'adjustment_metadata',
            'variance_document_ids',
            'variance_document_codes',
            'record_metadata',
        ):
            if hidden_field in self.fields:
                self.fields[hidden_field].widget = forms.HiddenInput()
                self.fields[hidden_field].required = False
        if 'notes' in self.fields:
            self.fields['notes'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        if 'quantity_adjusted' in self.fields:
            self.fields['quantity_adjusted'].widget.attrs.update({'readonly': 'readonly'})
            self.fields['quantity_adjusted'].required = False

        if self.company_id:
            self._filter_company_scoped_fields()
        self._set_unit_choices()
        self._set_warehouse_queryset()

    def _filter_company_scoped_fields(self) -> None:
        """Filter querysets based on active company."""
        if 'item' in self.fields:
            self.fields['item'].queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        if 'warehouse' in self.fields:
            self.fields['warehouse'].queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.name}"
            self.fields['warehouse'].empty_label = _("--- انتخاب کنید ---")
        if 'confirmed_by' in self.fields:
            from shared.models import User
            # Get users who have access to this company
            self.fields['confirmed_by'].queryset = User.objects.filter(
                company_accesses__company_id=self.company_id,
                company_accesses__is_enabled=1,
                is_active=True
            ).distinct()
            def confirmed_by_label(obj):
                full_name = obj.get_full_name()
                return f"{obj.username} - {full_name}" if full_name else obj.username
            self.fields['confirmed_by'].label_from_instance = confirmed_by_label
        if 'approver' in self.fields:
            from shared.models import User
            # Get users who can approve stocktaking records
            approvers = get_feature_approvers("inventory.stocktaking.records", self.company_id)
            self.fields['approver'].queryset = approvers
            self.fields['approver'].empty_label = _("--- انتخاب کنید ---")
            def approver_label(obj):
                full_name = obj.get_full_name()
                return f"{obj.username} - {full_name}" if full_name else obj.username
            self.fields['approver'].label_from_instance = approver_label

    def _resolve_item(self, candidate: Any = None) -> Optional[Item]:
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None

    def _get_item_allowed_units(self, item: Optional[Item]) -> List[Dict[str, str]]:
        """Get list of allowed units for an item."""
        if not item:
            return []
        codes = []

        def add(code: str) -> None:
            if code and code not in codes:
                codes.append(code)

        add(item.default_unit)
        add(item.primary_unit)

        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)

        # If no units found, add default unit 'EA' as fallback
        if not codes:
            codes.append('EA')
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]

    def _get_item_allowed_warehouses(self, item: Optional[Item]) -> List[Dict[str, str]]:
        """Get list of allowed warehouses for an item."""
        if not item:
            return []
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]
        if not warehouses:
            warehouses = list(Warehouse.objects.filter(company_id=item.company_id, is_enabled=1))
        return [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]

    def _set_unit_choices(self) -> None:
        """Set unit field choices based on selected item."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        item = self._resolve_item()
        placeholder = UNIT_CHOICES[0]
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            current = getattr(self.instance, 'unit', None)
            if current and current not in [code for code, _ in allowed]:
                label_map = dict(allowed)
                allowed.append((current, label_map.get(current, current)))
            unit_field.widget = forms.Select(attrs={'class': 'form-control'})
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.widget = forms.Select(attrs={'class': 'form-control'})
            unit_field.choices = [placeholder]

    def _set_warehouse_queryset(self) -> None:
        """Set warehouse field queryset based on selected item."""
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        item = self._resolve_item()
        if item:
            allowed_ids = [int(option['value']) for option in self._get_item_allowed_warehouses(item)]
            if allowed_ids:
                warehouse_field.queryset = Warehouse.objects.filter(pk__in=allowed_ids, is_enabled=1)
                return
        if self.company_id:
            warehouse_field.queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)

    def _validate_unit(self, cleaned_data: Dict[str, Any]) -> None:
        """Validate unit."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        unit = cleaned_data.get('unit')
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        if unit and unit not in allowed:
            self.add_error('unit', _('Selected unit is not configured for this item.'))

    def _validate_warehouse(self, cleaned_data: Dict[str, Any]) -> None:
        """Validate warehouse against item's allowed warehouses."""
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        warehouse = cleaned_data.get('warehouse')
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    self.add_error('warehouse', _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.'))
            else:
                # No warehouses configured for this item - this is an error
                self.add_error('warehouse', _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.'))

    def clean(self) -> Dict[str, Any]:
        """Validate and normalize form data."""
        cleaned_data = super().clean()
        self._validate_unit(cleaned_data)
        self._validate_warehouse(cleaned_data)
        return cleaned_data


class BaseLineFormSet(forms.BaseInlineFormSet):
    """Base formset class for handling company_id in line forms."""
    
    def __init__(self, *args, company_id: Optional[int] = None, request=None, **kwargs):
        """Initialize formset with company_id and request."""
        logger.info("=" * 80)
        logger.info("BaseLineFormSet.__init__() called")
        logger.info(f"company_id: {company_id}")
        logger.info(f"kwargs keys: {list(kwargs.keys())}")
        if 'instance' in kwargs:
            instance = kwargs['instance']
            # Don't log instance directly as it may trigger __str__ which accesses document
            if instance:
                logger.info(f"Instance: pk={getattr(instance, 'pk', None)}, is_locked={getattr(instance, 'is_locked', 'N/A')}")
            else:
                logger.info("Instance: None")
        else:
            instance = None
        
        # Store initial data for get_extra() method - set BEFORE super().__init__()
        # because Django may call get_extra() during initialization
        initial = kwargs.get('initial')
        if initial and instance is None and 'data' not in kwargs:
            initial_count = len(initial) if isinstance(initial, (list, tuple)) else 0
            if initial_count > 0:
                # Store initial count to use in get_extra()
                self._dynamic_extra = initial_count
                logger.info(f"Will adjust extra to {initial_count} based on initial data count")
            else:
                # Don't set _dynamic_extra to None if initial is empty - let default extra be used
                self._dynamic_extra = None
                logger.info("Initial is empty, will use default extra from formset factory")
        else:
            # Don't set _dynamic_extra if no initial - let default extra be used
            self._dynamic_extra = None
            logger.info("No initial data, will use default extra from formset factory")
        
        self.company_id = company_id
        self.request = request
        super().__init__(*args, **kwargs)
        logger.info(f"After super().__init__(), forms count: {len(self.forms)}")
        # Pass company_id and request to all forms in the formset and update querysets
        for i, form in enumerate(self.forms):
            logger.info(f"  Processing form {i}: instance pk={getattr(form.instance, 'pk', None)}, item_id={getattr(form.instance, 'item_id', None)}")
            form.company_id = company_id
            form.request = request
            # Update querysets after company_id is set
            if hasattr(form, '_update_querysets_after_company_id'):
                form._update_querysets_after_company_id()
            # Also update destination_type queryset if method exists
            if hasattr(form, '_update_destination_type_queryset'):
                form._update_destination_type_queryset()
            # Log item field state
            if hasattr(form, 'fields') and 'item' in form.fields:
                item_field = form.fields['item']
                logger.info(f"    Form {i} item field: queryset count={item_field.queryset.count()}, value={form['item'].value()}")
                item_id = getattr(form.instance, 'item_id', None)
                if item_id:
                    try:
                        in_queryset = item_field.queryset.filter(pk=item_id).exists()
                        logger.info(f"    Form {i} instance item_id={item_id} in queryset: {in_queryset}")
                    except Exception as e:
                        logger.warning(f"    Form {i} error checking item in queryset: {e}")
    
    def _construct_form(self, i, **kwargs):
        """Construct form with company_id and request."""
        logger.info(f"BaseLineFormSet._construct_form() called for index {i}")
        form = super()._construct_form(i, **kwargs)
        logger.info(f"  Form {i} constructed: instance pk={getattr(form.instance, 'pk', None)}, item_id={getattr(form.instance, 'item_id', None)}")
        form.company_id = self.company_id
        form.request = self.request
        # Update querysets after company_id is set
        if hasattr(form, '_update_querysets_after_company_id'):
            form._update_querysets_after_company_id()
        # Also update destination_type queryset if method exists
        if hasattr(form, '_update_destination_type_queryset'):
            form._update_destination_type_queryset()
        # Log item field state
        if hasattr(form, 'fields') and 'item' in form.fields:
            item_field = form.fields['item']
            item_id = getattr(form.instance, 'item_id', None)
            logger.info(f"  Form {i} item field after update: queryset count={item_field.queryset.count()}, value={form['item'].value()}, instance item_id={item_id}")
            if item_id:
                try:
                    in_queryset = item_field.queryset.filter(pk=item_id).exists()
                    logger.info(f"  Form {i} instance item_id={item_id} in queryset: {in_queryset}")
                except Exception as e:
                    logger.warning(f"  Form {i} error checking item in queryset: {e}")
        return form
    
    def get_extra(self):
        """Return extra count, dynamically adjusted based on initial data if needed."""
        logger.info("BaseLineFormSet.get_extra() called")
        # Check if we have dynamic extra set in __init__
        if hasattr(self, '_dynamic_extra') and self._dynamic_extra is not None:
            logger.info(f"Using _dynamic_extra: {self._dynamic_extra}")
            return self._dynamic_extra
        # Also check self.initial (set by Django after __init__)
        if hasattr(self, 'initial') and self.initial:
            initial_count = len(self.initial) if isinstance(self.initial, (list, tuple)) else 0
            logger.info(f"Using self.initial count: {initial_count}")
            if initial_count > 0:
                return initial_count
        default_extra = super().get_extra()
        logger.info(f"Using default extra: {default_extra}")
        return default_extra
    
    @property
    def empty_form(self):
        """Return empty form with company_id and request."""
        form = self._construct_form('__prefix__')
        form.company_id = self.company_id
        form.request = self.request
        # Set document on instance if instance has document_id (for empty forms in edit mode)
        # This prevents RelatedObjectDoesNotExist when accessing form.instance.item
        if hasattr(self, 'instance') and self.instance and hasattr(self.instance, 'pk') and self.instance.pk:
            if hasattr(form.instance, 'document'):
                # Try to set document from parent instance
                try:
                    # Check if document field exists and is a ForeignKey
                    if hasattr(form.instance, 'document_id'):
                        # Set document_id directly to avoid RelatedObjectDoesNotExist
                        form.instance.document_id = self.instance.pk
                    else:
                        # Try to set document object
                        form.instance.document = self.instance
                except Exception:
                    # If document is a ForeignKey and instance doesn't exist, skip
                    pass
        # Update querysets after company_id is set
        if hasattr(form, '_update_querysets_after_company_id'):
            form._update_querysets_after_company_id()
        # Also update destination_type queryset if method exists
        if hasattr(form, '_update_destination_type_queryset'):
            form._update_destination_type_queryset()
        return form
    
    def clean(self) -> Dict[str, Any]:
        """Validate that at least one line has an item."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"")
        logger.info(f"🧹 CLEANING BaseLineFormSet...")
        logger.info(f"   Formset prefix: {self.prefix}")
        logger.info(f"   Total forms: {len(self.forms)}")
        logger.info(f"   Has errors: {any(self.errors)}")
        
        if any(self.errors):
            logger.warning(f"   ⚠️  Formset already has errors, skipping clean")
            return
        
        # Count non-empty forms (forms with an item)
        non_empty_forms = 0
        logger.info(f"")
        logger.info(f"   📊 Analyzing forms:")
        
        for i, form in enumerate(self.forms):
            logger.info(f"      Form {i}:")
            logger.info(f"         - Has cleaned_data: {bool(form.cleaned_data)}")
            
            if form.cleaned_data:
                is_deleted = form.cleaned_data.get('DELETE', False)
                item = form.cleaned_data.get('item')
                
                logger.info(f"         - Is deleted: {is_deleted}")
                logger.info(f"         - Has item: {bool(item)}")
                if item:
                    logger.info(f"         - Item: {item.name} (ID: {item.id})")
                
                # Check if form is marked for deletion
                if is_deleted:
                    logger.info(f"         ⚠️  Form marked for deletion, skipping")
                    continue
                # Check if form has an item
                if item:
                    non_empty_forms += 1
                    logger.info(f"         ✅ VALID FORM (counted)")
                else:
                    logger.info(f"         ⚠️  Form has no item, not counted")
            else:
                logger.info(f"         ⚠️  Form has no cleaned_data, not counted")
        
        logger.info(f"")
        logger.info(f"   📊 Summary: {non_empty_forms} non-empty form(s) found")
        
        # If min_num is set and we don't have enough non-empty forms, raise validation error
        # Django's validate_min might not catch empty forms correctly, so we check manually
        min_num = getattr(self, 'min_num', 0)
        logger.info(f"   Required minimum: {min_num}")
        
        if min_num and non_empty_forms < min_num:
            logger.error(f"   ❌ ERROR: Not enough forms! Required: {min_num}, Found: {non_empty_forms}")
            raise forms.ValidationError(
                _('Please add at least %(min_num)d line(s) with an item.') % {'min_num': min_num}
            )
        
        logger.info(f"   ✅ Formset clean validation passed")


# Note: IssueLineBaseForm and ReceiptLineBaseForm are very large classes
# They will be added in separate files (issue.py and receipt.py) to keep base.py manageable



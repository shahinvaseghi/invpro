"""
Request forms for inventory module.

This module contains forms for:
- Purchase Requests
- Warehouse Requests
"""
from typing import Optional, Dict, Any

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from inventory.models import (
    Item,
    ItemUnit,
    PurchaseRequest,
    WarehouseRequest,
    Warehouse,
)
from shared.models import CompanyUnit
from inventory.forms.base import (
    UNIT_CHOICES,
    get_feature_approvers,
)
from inventory.widgets import JalaliDateInput

User = get_user_model()


class PurchaseRequestForm(forms.ModelForm):
    """Form for creating/editing purchase requests."""
    
    class Meta:
        model = PurchaseRequest
        fields = [
            'item',
            'unit',
            'quantity_requested',
            'needed_by_date',
            'priority',
            'reason_code',
            'approver',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'needed_by_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'reason_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'approver': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'item': _('Item'),
            'unit': _('Unit'),
            'quantity_requested': _('Requested Quantity'),
            'needed_by_date': _('Needed By Date'),
            'priority': _('Priority'),
            'reason_code': _('Reason Code / Notes'),
            'approver': _('Approver'),
        }

    def __init__(self, *args, company_id: Optional[int] = None, request_user: Optional[Any] = None, **kwargs):
        """Initialize form with company filtering."""
        self.company_id = company_id
        self.request_user = request_user
        super().__init__(*args, **kwargs)

        self.fields['unit'].choices = UNIT_CHOICES
        if 'reason_code' in self.fields:
            self.fields['reason_code'].required = False

        if self.company_id:
            self.fields['item'].queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
            approvers = get_feature_approvers("inventory.requests.purchase", self.company_id)
            self.fields['approver'].queryset = approvers
            self.fields['approver'].empty_label = _("--- انتخاب کنید ---")
            self.fields['approver'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} · {obj.username}"
        else:
            self.fields['item'].queryset = Item.objects.none()
            self.fields['approver'].queryset = User.objects.none()

        if 'approver' in self.fields:
            self.fields['approver'].required = True

        self._set_unit_choices()

    def _resolve_item(self, candidate: Any = None) -> Optional[Item]:
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        return None

    def _get_item_allowed_units(self, item: Optional[Item]) -> list:
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

    def _set_unit_choices(self) -> None:
        """Set unit field choices based on selected item."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        item = self._resolve_item()
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.choices = [placeholder]

    def clean_unit(self) -> str:
        """Validate unit."""
        unit = self.cleaned_data.get('unit')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item:
            allowed = {row['value'] for row in self._get_item_allowed_units(item)}
            if unit and unit not in allowed:
                raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        return unit

    def clean_approver(self) -> Any:
        """Validate approver has access to company."""
        approver = self.cleaned_data.get('approver')
        if approver and self.company_id:
            # Check if user has access to this company
            from shared.models import UserCompanyAccess
            has_access = UserCompanyAccess.objects.filter(
                user=approver,
                company_id=self.company_id,
                is_enabled=1
            ).exists()
            if not has_access:
                raise forms.ValidationError(_('Selected approver must have access to the active company.'))
        return approver

    def clean(self) -> Dict[str, Any]:
        """Validate and normalize form data."""
        cleaned_data = super().clean()
        self._set_unit_choices()
        return cleaned_data


class WarehouseRequestForm(forms.ModelForm):
    """Form for creating/editing warehouse requests."""
    
    class Meta:
        model = WarehouseRequest
        fields = [
            'item',
            'unit',
            'quantity_requested',
            'warehouse',
            'department_unit',
            'needed_by_date',
            'priority',
            'purpose',
            'approver',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'department_unit': forms.Select(attrs={'class': 'form-control'}),
            'needed_by_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'approver': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'item': _('Item'),
            'unit': _('Unit'),
            'quantity_requested': _('Requested Quantity'),
            'warehouse': _('Warehouse'),
            'department_unit': _('Organizational Unit'),
            'needed_by_date': _('Needed By Date'),
            'priority': _('Priority'),
            'purpose': _('Purpose / Notes'),
            'approver': _('Approver'),
        }

    def __init__(self, *args, company_id: Optional[int] = None, request_user: Optional[Any] = None, **kwargs):
        """Initialize form with company filtering."""
        self.company_id = company_id
        self.request_user = request_user
        super().__init__(*args, **kwargs)

        self.fields['unit'].choices = UNIT_CHOICES
        self.fields['purpose'].required = False
        self.fields['department_unit'].required = False

        if self.company_id:
            self.fields['item'].queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
            self.fields['warehouse'].queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            self.fields['department_unit'].queryset = CompanyUnit.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            self.fields['department_unit'].empty_label = _("--- انتخاب کنید ---")
            approvers = get_feature_approvers("inventory.requests.warehouse", self.company_id)
            self.fields['approver'].queryset = approvers
            self.fields['approver'].empty_label = _("--- انتخاب کنید ---")
        else:
            self.fields['item'].queryset = Item.objects.none()
            self.fields['warehouse'].queryset = Warehouse.objects.none()
            self.fields['department_unit'].queryset = CompanyUnit.objects.none()
            self.fields['approver'].queryset = User.objects.none()

        if 'approver' in self.fields:
            self.fields['approver'].required = True

        self._set_unit_choices()

    def _resolve_item(self, candidate: Any = None) -> Optional[Item]:
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        return None

    def _get_item_allowed_units(self, item: Optional[Item]) -> list:
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

    def _set_unit_choices(self) -> None:
        """Set unit field choices based on selected item."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        item = self._resolve_item()
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.choices = [placeholder]

    def clean_unit(self) -> str:
        """Validate unit."""
        unit = self.cleaned_data.get('unit')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item:
            allowed = {row['value'] for row in self._get_item_allowed_units(item)}
            if unit and unit not in allowed:
                raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        return unit

    def clean_approver(self) -> Any:
        """Validate approver has access to company."""
        approver = self.cleaned_data.get('approver')
        if approver and self.company_id:
            # Check if user has access to this company
            from shared.models import UserCompanyAccess
            has_access = UserCompanyAccess.objects.filter(
                user=approver,
                company_id=self.company_id,
                is_enabled=1
            ).exists()
            if not has_access:
                raise forms.ValidationError(_('Selected approver must have access to the active company.'))
        return approver

    def clean(self) -> Dict[str, Any]:
        """Validate and normalize form data."""
        cleaned_data = super().clean()
        self._set_unit_choices()
        return cleaned_data


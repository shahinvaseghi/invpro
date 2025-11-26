"""
Request forms for inventory module.

This module contains forms for:
- Purchase Requests
- Warehouse Requests
"""
from typing import Optional, Dict, Any

from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from inventory.models import (
    Item,
    ItemUnit,
    PurchaseRequest,
    PurchaseRequestLine,
    WarehouseRequest,
    Warehouse,
)
from shared.models import CompanyUnit
from inventory.forms.base import (
    UNIT_CHOICES,
    get_feature_approvers,
    BaseLineFormSet,
)
from inventory.widgets import JalaliDateInput

User = get_user_model()


class PurchaseRequestForm(forms.ModelForm):
    """Header-only form for purchase requests with multi-line support."""
    
    class Meta:
        model = PurchaseRequest
        fields = [
            'needed_by_date',
            'priority',
            'reason_code',
            'approver',
        ]
        widgets = {
            'needed_by_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'reason_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'approver': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
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

        if 'reason_code' in self.fields:
            self.fields['reason_code'].required = False

        if self.company_id:
            approvers = get_feature_approvers("inventory.requests.purchase", self.company_id)
            self.fields['approver'].queryset = approvers
            self.fields['approver'].empty_label = _("--- انتخاب کنید ---")
            self.fields['approver'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} · {obj.username}"
        else:
            self.fields['approver'].queryset = User.objects.none()

        if 'approver' in self.fields:
            self.fields['approver'].required = True

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


class PurchaseRequestLineForm(forms.ModelForm):
    """Form for purchase request line items."""
    
    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = PurchaseRequestLine
        fields = [
            'item',
            'unit',
            'quantity_requested',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'item': _('Item'),
            'unit': _('Unit'),
            'quantity_requested': _('Requested Quantity'),
            'line_notes': _('Notes'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, request=None, **kwargs):
        """Initialize form with company filtering and optional filters."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        self.request = request
        
        if self.company_id:
            if 'item' in self.fields:
                # Base queryset: enabled items
                base_queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1)
                
                # Apply optional filters from request
                if self.request:
                    # Filter by item_type (optional)
                    item_type_id = self.request.GET.get('item_type') or self.request.POST.get('item_type')
                    if item_type_id:
                        try:
                            base_queryset = base_queryset.filter(type_id=int(item_type_id))
                        except (ValueError, TypeError):
                            pass
                    
                    # Filter by category (optional)
                    category_id = self.request.GET.get('category') or self.request.POST.get('category')
                    if category_id:
                        try:
                            base_queryset = base_queryset.filter(category_id=int(category_id))
                        except (ValueError, TypeError):
                            pass
                    
                    # Filter by subcategory (optional)
                    subcategory_id = self.request.GET.get('subcategory') or self.request.POST.get('subcategory')
                    if subcategory_id:
                        try:
                            base_queryset = base_queryset.filter(subcategory_id=int(subcategory_id))
                        except (ValueError, TypeError):
                            pass
                    
                    # Search by name or code (optional)
                    search_term = self.request.GET.get('item_search') or self.request.POST.get('item_search')
                    if search_term:
                        search_term = search_term.strip()
                        if search_term:
                            base_queryset = base_queryset.filter(
                                Q(name__icontains=search_term) |
                                Q(item_code__icontains=search_term) |
                                Q(full_item_code__icontains=search_term)
                            )
                
                # If editing and instance has an item, include it even if disabled
                if hasattr(self, 'instance') and self.instance and hasattr(self.instance, 'item_id') and self.instance.item_id:
                    instance_item_id = self.instance.item_id
                    self.fields['item'].queryset = Item.objects.filter(
                        Q(company_id=self.company_id, is_enabled=1) | Q(pk=instance_item_id)
                    ).order_by('name')
                else:
                    self.fields['item'].queryset = base_queryset.order_by('name')
                
                self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        
        # Set unit choices
        if 'unit' in self.fields:
            self.fields['unit'].choices = UNIT_CHOICES
        
        # Restore unit value if editing
        if not self.is_bound and getattr(self.instance, 'pk', None):
            if 'unit' in self.fields and getattr(self.instance, 'unit', None):
                unit_value = self.instance.unit
                unit_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in unit_choices]
                if unit_value not in unit_codes:
                    self.fields['unit'].choices = unit_choices + [(unit_value, unit_value)]
                self.initial['unit'] = unit_value
    
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
    
    def _set_unit_choices_for_item(self, item: Optional[Item]) -> None:
        """Set unit field choices based on selected item."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        
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
    
    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        item = self._resolve_item(cleaned_data.get('item'))
        if item and 'unit' in self.fields:
            self._set_unit_choices_for_item(item)
        return cleaned_data


PurchaseRequestLineFormSet = inlineformset_factory(
    PurchaseRequest,
    PurchaseRequestLine,
    form=PurchaseRequestLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


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
            self._setup_item_queryset()
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

    def _setup_item_queryset(self) -> None:
        """Setup item queryset, including instance item if editing."""
        if self.company_id:
            # Base queryset: enabled items
            base_queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1)
            
            # If editing and instance has an item, include it even if disabled
            if hasattr(self, 'instance') and self.instance and hasattr(self.instance, 'item_id') and self.instance.item_id:
                instance_item_id = self.instance.item_id
                # Include instance item even if disabled
                self.fields['item'].queryset = Item.objects.filter(
                    Q(company_id=self.company_id, is_enabled=1) | Q(pk=instance_item_id)
                ).order_by('name')
            else:
                self.fields['item'].queryset = base_queryset.order_by('name')
            
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        else:
            self.fields['item'].queryset = Item.objects.none()

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

    def _get_item_allowed_warehouses(self, item: Optional[Item]) -> list:
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
        placeholder = UNIT_CHOICES[0]
        item = self._resolve_item()
        
        # Get current unit value from instance (for edit mode)
        current_unit = None
        if hasattr(self, 'instance') and self.instance and hasattr(self.instance, 'unit'):
            current_unit = self.instance.unit
        
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            unit_field.choices = [placeholder] + allowed
            
            # If current unit is not in allowed units, add it to choices
            if current_unit and current_unit not in [choice[0] for choice in allowed]:
                # Find label for current unit from UNIT_CHOICES
                unit_label = dict(UNIT_CHOICES).get(current_unit, current_unit)
                unit_field.choices.append((current_unit, unit_label))
        else:
            # If no item resolved, use placeholder
            unit_field.choices = [placeholder]
            # But if we have a current unit value, add it to choices
            if current_unit:
                unit_label = dict(UNIT_CHOICES).get(current_unit, current_unit)
                unit_field.choices.append((current_unit, unit_label))

    def clean_unit(self) -> str:
        """Validate unit."""
        unit = self.cleaned_data.get('unit')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item:
            allowed = {row['value'] for row in self._get_item_allowed_units(item)}
            if unit and unit not in allowed:
                raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        return unit

    def clean_warehouse(self) -> Any:
        """Validate warehouse is allowed for selected item."""
        warehouse = self.cleaned_data.get('warehouse')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item and warehouse:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            if warehouse.pk not in allowed_ids:
                raise forms.ValidationError(_('Selected warehouse is not allowed for this item.'))
        return warehouse

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


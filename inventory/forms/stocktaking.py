"""
Stocktaking forms for inventory module.

This module contains forms for:
- Stocktaking Deficit (with line items)
- Stocktaking Surplus (with line items)
- Stocktaking Record
"""
from typing import Optional

from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from inventory.models import (
    StocktakingDeficit,
    StocktakingDeficitLine,
    StocktakingSurplus,
    StocktakingSurplusLine,
    StocktakingRecord,
)
from inventory.forms.base import (
    StocktakingBaseForm,
    generate_document_code,
    BaseLineFormSet,
)


class StocktakingDeficitForm(StocktakingBaseForm):
    """Header-only form for stocktaking deficit documents with multi-line support."""

    class Meta:
        model = StocktakingDeficit
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit: bool = True):
        """Save with auto-generated document code."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingDeficit, instance.company_id, "STD")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class StocktakingDeficitLineForm(StocktakingBaseForm):
    """Form for stocktaking deficit line items."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = StocktakingDeficitLine
        fields = [
            'item',
            'warehouse',
            'unit',
            'quantity_expected',
            'quantity_counted',
            'quantity_adjusted',
            'valuation_method',
            'unit_cost',
            'total_cost',
            'reason_code',
            'investigation_reference',
            'adjustment_metadata',
        ]
        widgets = {
            'quantity_expected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_counted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_adjusted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'investigation_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_unit(self):
        """Validate unit and ensure it's in choices."""
        unit = self.cleaned_data.get('unit')
        if not unit:
            return unit
        
        # Get item - try from cleaned_data first, then from data
        item = None
        if 'item' in self.cleaned_data:
            item_id = self.cleaned_data.get('item')
            if item_id:
                try:
                    from inventory.models import Item
                    item = Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        
        # If item not in cleaned_data yet, try to get from data
        if not item and self.data:
            item_id = self.data.get(self.add_prefix('item'))
            if item_id:
                try:
                    from inventory.models import Item
                    item = Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        
        # If still no item, try instance
        if not item and hasattr(self.instance, 'item_id') and self.instance.item_id:
            item = self.instance.item
        
        # If we have an item, check if unit is allowed
        if item:
            # Get allowed units for this item
            allowed_units = self._get_item_allowed_units(item)
            allowed_codes = [row['value'] for row in allowed_units]
            
            # If unit is not in allowed units, add it to choices
            if unit not in allowed_codes:
                # Add unit to choices to avoid validation error
                current_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in current_choices if code]
                if unit not in unit_codes:
                    from inventory.forms.base import UNIT_CHOICES
                    label_map = {value: str(label) for value, label in UNIT_CHOICES}
                    label = label_map.get(unit, unit)
                    self.fields['unit'].choices = current_choices + [(unit, label)]
        else:
            # No item yet - just ensure unit is in choices (accept any valid unit)
            current_choices = list(self.fields['unit'].choices)
            unit_codes = [code for code, _ in current_choices if code]
            if unit not in unit_codes:
                from inventory.forms.base import UNIT_CHOICES
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                label = label_map.get(unit, unit)
                self.fields['unit'].choices = current_choices + [(unit, label)]
        
        return unit

    def clean(self):
        """Validate quantity calculations."""
        cleaned_data = super().clean()
        expected = cleaned_data.get('quantity_expected')
        counted = cleaned_data.get('quantity_counted')
        if expected is not None and counted is not None:
            adjusted = expected - counted
            if adjusted < 0:
                self.add_error('quantity_counted', _('Counted quantity cannot exceed expected balance for a deficit document.'))
            cleaned_data['quantity_adjusted'] = adjusted
        unit_cost = cleaned_data.get('unit_cost')
        if unit_cost not in (None, '') and cleaned_data.get('quantity_adjusted') not in (None, ''):
            try:
                cleaned_data['total_cost'] = cleaned_data['quantity_adjusted'] * unit_cost
            except TypeError:
                pass
        return cleaned_data


class StocktakingSurplusForm(StocktakingBaseForm):
    """Header-only form for stocktaking surplus documents with multi-line support."""

    class Meta:
        model = StocktakingSurplus
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit: bool = True):
        """Save with auto-generated document code."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingSurplus, instance.company_id, "STS")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class StocktakingSurplusLineForm(StocktakingBaseForm):
    """Form for stocktaking surplus line items."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize form and customize labels."""
        super().__init__(*args, **kwargs)
        # Change label for quantity_adjusted to "مقدار افزایش یافته" for surplus
        if 'quantity_adjusted' in self.fields:
            self.fields['quantity_adjusted'].label = _('مقدار افزایش یافته')

    class Meta:
        model = StocktakingSurplusLine
        fields = [
            'item',
            'warehouse',
            'unit',
            'quantity_expected',
            'quantity_counted',
            'quantity_adjusted',
            'valuation_method',
            'unit_cost',
            'total_cost',
            'reason_code',
            'investigation_reference',
            'adjustment_metadata',
        ]
        widgets = {
            'quantity_expected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_counted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_adjusted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'investigation_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_unit(self):
        """Validate unit and ensure it's in choices."""
        unit = self.cleaned_data.get('unit')
        if not unit:
            return unit
        
        # Get item - try from cleaned_data first, then from data
        item = None
        if 'item' in self.cleaned_data:
            item_id = self.cleaned_data.get('item')
            if item_id:
                try:
                    from inventory.models import Item
                    item = Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        
        # If item not in cleaned_data yet, try to get from data
        if not item and self.data:
            item_id = self.data.get(self.add_prefix('item'))
            if item_id:
                try:
                    from inventory.models import Item
                    item = Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        
        # If still no item, try instance
        if not item and hasattr(self.instance, 'item_id') and self.instance.item_id:
            item = self.instance.item
        
        # If we have an item, check if unit is allowed
        if item:
            # Get allowed units for this item
            allowed_units = self._get_item_allowed_units(item)
            allowed_codes = [row['value'] for row in allowed_units]
            
            # If unit is not in allowed units, add it to choices
            if unit not in allowed_codes:
                # Add unit to choices to avoid validation error
                current_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in current_choices if code]
                if unit not in unit_codes:
                    from inventory.forms.base import UNIT_CHOICES
                    label_map = {value: str(label) for value, label in UNIT_CHOICES}
                    label = label_map.get(unit, unit)
                    self.fields['unit'].choices = current_choices + [(unit, label)]
        else:
            # No item yet - just ensure unit is in choices (accept any valid unit)
            current_choices = list(self.fields['unit'].choices)
            unit_codes = [code for code, _ in current_choices if code]
            if unit not in unit_codes:
                from inventory.forms.base import UNIT_CHOICES
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                label = label_map.get(unit, unit)
                self.fields['unit'].choices = current_choices + [(unit, label)]
        
        return unit

    def clean(self):
        """Validate quantity calculations."""
        cleaned_data = super().clean()
        expected = cleaned_data.get('quantity_expected')
        counted = cleaned_data.get('quantity_counted')
        if expected is not None and counted is not None:
            adjusted = counted - expected
            if adjusted < 0:
                self.add_error('quantity_counted', _('Counted quantity cannot be less than expected for a surplus document.'))
            cleaned_data['quantity_adjusted'] = adjusted
        unit_cost = cleaned_data.get('unit_cost')
        if unit_cost not in (None, '') and cleaned_data.get('quantity_adjusted') not in (None, ''):
            try:
                cleaned_data['total_cost'] = cleaned_data['quantity_adjusted'] * unit_cost
            except TypeError:
                pass
        return cleaned_data


class StocktakingRecordForm(StocktakingBaseForm):
    """Create/update form for stocktaking records."""
    
    # Define approval status choices
    APPROVAL_STATUS_CHOICES = [
        ('pending', _('در انتظار تایید')),
        ('approved', _('تایید شده')),
        ('rejected', _('رد شده')),
    ]
    
    approval_status = forms.ChoiceField(
        choices=APPROVAL_STATUS_CHOICES,
        label=_('وضعیت تایید'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='pending',
    )

    class Meta:
        model = StocktakingRecord
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
            'inventory_snapshot_time',
            'confirmed_by',
            'confirmation_notes',
            'variance_document_ids',
            'variance_document_codes',
            'final_inventory_value',
            'approver',  # Moved before approval_status
            'approval_status',
            'approved_at',
            'approver_notes',
            'record_metadata',
        ]
        widgets = {
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'confirmation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'final_inventory_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approver_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        """Initialize form with user for permission checks."""
        super().__init__(*args, user=user, **kwargs)
        if 'approval_status' in self.fields and not getattr(self.instance, 'pk', None):
            self.fields['approval_status'].initial = 'pending'
        
        # Hide approved_at field - it's automatically set when status is approved
        if 'approved_at' in self.fields:
            self.fields['approved_at'].widget = forms.HiddenInput()
            self.fields['approved_at'].required = False
        
        # Only the selected approver can change approval_status
        if self.instance.pk and 'approval_status' in self.fields:
            if self.user and self.instance.approver_id:
                if self.user.id != self.instance.approver_id:
                    # User is not the approver - make approval_status readonly
                    self.fields['approval_status'].widget.attrs['disabled'] = 'disabled'
                    self.fields['approval_status'].help_text = _('فقط تأییدکننده انتخاب شده می‌تواند وضعیت را تغییر دهد')
            elif not self.instance.approver_id:
                # No approver selected yet - anyone can change status
                pass
        for field_name in ('variance_document_ids', 'variance_document_codes', 'record_metadata'):
            if field_name in self.fields and not getattr(self.instance, field_name, None):
                default_value = [] if field_name != 'record_metadata' else {}
                self.fields[field_name].initial = default_value
        if 'document_date' in self.fields and not getattr(self.instance, 'pk', None):
            self.fields['document_date'].initial = timezone.now().date()
        if 'inventory_snapshot_time' in self.fields and not getattr(self.instance, 'pk', None):
            self.fields['inventory_snapshot_time'].initial = timezone.now()

    def clean(self):
        """Validate approval status changes."""
        cleaned_data = super().clean()
        
        # Server-side permission check: only approver can change approval_status
        if self.instance.pk and 'approval_status' in cleaned_data:
            if self.user and self.instance.approver_id:
                if self.user.id != self.instance.approver_id:
                    # User is not the approver - restore original status
                    if self.instance.approval_status != cleaned_data['approval_status']:
                        self.add_error('approval_status', _('فقط تأییدکننده انتخاب شده می‌تواند وضعیت را تغییر دهد'))
                        cleaned_data['approval_status'] = self.instance.approval_status
        
        return cleaned_data

    def save(self, commit: bool = True):
        """Save with auto-generated document code and approval handling."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingRecord, instance.company_id, "STR")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        if not instance.inventory_snapshot_time:
            instance.inventory_snapshot_time = timezone.now()
        if instance.confirmed_by_id:
            instance.confirmed_by_code = instance.confirmed_by.username
        if instance.approver_id:
            instance.approver_notes = instance.approver_notes or ''
        
        # Set approved_at when status changes to approved
        if instance.approval_status == 'approved' and not instance.approved_at:
            instance.approved_at = timezone.now()
        # Clear approved_at if status changes back to pending or rejected
        elif instance.approval_status in ('pending', 'rejected'):
            instance.approved_at = None
            
        if commit:
            instance.save()
            self.save_m2m()
        return instance


# Create formsets
StocktakingDeficitLineFormSet = inlineformset_factory(
    StocktakingDeficit,
    StocktakingDeficitLine,
    form=StocktakingDeficitLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

StocktakingSurplusLineFormSet = inlineformset_factory(
    StocktakingSurplus,
    StocktakingSurplusLine,
    form=StocktakingSurplusLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


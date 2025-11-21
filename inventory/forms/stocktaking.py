"""
Stocktaking forms for inventory module.

This module contains forms for:
- Stocktaking Deficit
- Stocktaking Surplus
- Stocktaking Record
"""
from typing import Optional

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from inventory.models import StocktakingDeficit, StocktakingSurplus, StocktakingRecord
from inventory.forms.base import (
    StocktakingBaseForm,
    generate_document_code,
)


class StocktakingDeficitForm(StocktakingBaseForm):
    """Create/update form for stocktaking deficit adjustments."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = StocktakingDeficit
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
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
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_expected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_counted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_adjusted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'investigation_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }

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

    def save(self, commit: bool = True):
        """Save with auto-generated document code."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingDeficit, instance.company_id, "STD")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.item_code = instance.item.item_code if instance.item_id else instance.item_code
        instance.warehouse_code = instance.warehouse.public_code if instance.warehouse_id else instance.warehouse_code
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class StocktakingSurplusForm(StocktakingBaseForm):
    """Create/update form for stocktaking surplus adjustments."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = StocktakingSurplus
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
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
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_expected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_counted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_adjusted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'investigation_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }

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

    def save(self, commit: bool = True):
        """Save with auto-generated document code."""
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingSurplus, instance.company_id, "STS")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.item_code = instance.item.item_code if instance.item_id else instance.item_code
        instance.warehouse_code = instance.warehouse.public_code if instance.warehouse_id else instance.warehouse_code
        if commit:
            instance.save()
            self.save_m2m()
        return instance


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


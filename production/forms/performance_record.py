"""
Performance Record forms for production module.
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from inventory.fields import JalaliDateField
from production.models import (
    PerformanceRecord,
    PerformanceRecordMaterial,
    PerformanceRecordPerson,
    PerformanceRecordMachine,
    ProductOrder,
    TransferToLine,
    Person,
    Machine,
    WorkLine,
)


class PerformanceRecordForm(forms.ModelForm):
    """Form for creating/editing performance records."""
    
    # Override performance_date to use JalaliDateField
    performance_date = JalaliDateField(
        required=True,
        label=_('Performance Date'),
    )
    
    class Meta:
        model = PerformanceRecord
        fields = [
            'order',
            'transfer',
            'performance_date',
            'quantity_planned',
            'quantity_actual',
            'approved_by',
            'notes',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control', 'id': 'id_order'}),
            'transfer': forms.Select(attrs={'class': 'form-control', 'id': 'id_transfer'}),
            'quantity_planned': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0',
                'readonly': True,
            }),
            'quantity_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0',
            }),
            'approved_by': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'order': _('Product Order'),
            'transfer': _('Transfer to Line (Optional)'),
            'performance_date': _('Performance Date'),
            'quantity_planned': _('Planned Quantity'),
            'quantity_actual': _('Actual Quantity Produced'),
            'approved_by': _('Approver'),
            'notes': _('Notes'),
        }
        help_texts = {
            'order': _('Select the product order for this performance record'),
            'transfer': _('Select the transfer document used (optional, will auto-populate materials if selected)'),
            'quantity_planned': _('Planned quantity from the order (read-only)'),
            'quantity_actual': _('Enter the actual quantity produced'),
            'approved_by': _('Select the user who can approve this performance record'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        if self.company_id:
            # Filter Product Orders by company - only orders with process
            self.fields['order'].queryset = ProductOrder.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
                process__isnull=False,  # Only orders with process
            ).select_related('bom', 'finished_item', 'process').order_by('-order_date', 'order_code')
            
            # Filter TransferToLine by company - only approved transfers
            self.fields['transfer'].queryset = TransferToLine.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
                status='approved',  # Only approved transfers
            ).select_related('order').order_by('-transfer_date', 'transfer_code')
            
            # Filter approved_by (User) - only users with approve permission for production.performance_records
            from shared.models import UserCompanyAccess, AccessLevelPermission
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Find access levels that have approve permission for production.performance_records
            approve_access_levels = list(AccessLevelPermission.objects.filter(
                module_code='production',
                resource_code='production.performance_records',
                can_approve=1,
            ).values_list('access_level_id', flat=True))
            
            # Find users with those access levels for this company
            approver_user_ids = list(UserCompanyAccess.objects.filter(
                company_id=self.company_id,
                access_level_id__in=approve_access_levels,
                is_enabled=1,
            ).values_list('user_id', flat=True))
            
            # Filter User queryset to show only users with approve permission
            # Also include superusers automatically
            if approver_user_ids:
                self.fields['approved_by'].queryset = User.objects.filter(
                    Q(id__in=approver_user_ids) | Q(is_superuser=True),
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
            else:
                # If no approvers found, show only superusers
                self.fields['approved_by'].queryset = User.objects.filter(
                    is_superuser=True,
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            self.fields['order'].queryset = ProductOrder.objects.none()
            self.fields['transfer'].queryset = TransferToLine.objects.none()
            self.fields['approved_by'].queryset = User.objects.none()
        
        # If editing, set readonly fields
        if self.instance and self.instance.pk:
            if self.instance.is_locked:
                # Locked - make all fields readonly except notes
                for field_name in self.fields:
                    if field_name != 'notes':
                        self.fields[field_name].widget.attrs['readonly'] = True
                        self.fields[field_name].widget.attrs['disabled'] = True
    
    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        order = cleaned_data.get('order')
        quantity_planned = cleaned_data.get('quantity_planned')
        quantity_actual = cleaned_data.get('quantity_actual')
        
        # Validate order is selected
        if not order:
            self.add_error('order', _('Please select a product order.'))
            return cleaned_data
        
        # Validate order has process
        if not order.process:
            self.add_error('order', _('Selected order must have a process assigned.'))
            return cleaned_data
        
        # Set quantity_planned from order if not set
        if not quantity_planned and order:
            cleaned_data['quantity_planned'] = order.quantity_planned
        
        # Validate quantity_actual
        if quantity_actual is not None and quantity_actual < 0:
            self.add_error('quantity_actual', _('Actual quantity cannot be negative.'))
        
        # Validate transfer belongs to order if selected
        transfer = cleaned_data.get('transfer')
        if transfer and transfer.order_id != order.id:
            self.add_error('transfer', _('Selected transfer must belong to the selected order.'))
        
        return cleaned_data


class PerformanceRecordMaterialForm(forms.ModelForm):
    """Form for performance record material items."""
    
    class Meta:
        model = PerformanceRecordMaterial
        fields = [
            'material_item',
            'quantity_required',
            'quantity_waste',
            'unit',
            'is_extra',
            'notes',
        ]
        widgets = {
            'material_item': forms.Select(attrs={'class': 'form-control'}),
            'quantity_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0',
                'readonly': True,
            }),
            'quantity_waste': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0',
            }),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'is_extra': forms.HiddenInput(),  # Hidden, managed automatically
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'material_item': _('Material Item'),
            'quantity_required': _('Required Quantity'),
            'quantity_waste': _('Waste Quantity'),
            'unit': _('Unit'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Material item queryset will be set dynamically based on transfer
        self.fields['material_item'].queryset = forms.ModelChoiceField(
            queryset=None,
            required=True,
        ).queryset
    
    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        quantity_waste = cleaned_data.get('quantity_waste', Decimal('0'))
        quantity_required = cleaned_data.get('quantity_required', Decimal('0'))
        
        if quantity_waste < 0:
            self.add_error('quantity_waste', _('Waste quantity cannot be negative.'))
        
        if quantity_waste > quantity_required:
            self.add_error('quantity_waste', _('Waste quantity cannot exceed required quantity.'))
        
        return cleaned_data


class PerformanceRecordPersonForm(forms.ModelForm):
    """Form for performance record person items."""
    
    class Meta:
        model = PerformanceRecordPerson
        fields = [
            'person',
            'work_minutes',
            'work_line',
            'notes',
        ]
        widgets = {
            'person': forms.Select(attrs={'class': 'form-control'}),
            'work_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'work_line': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'person': _('Person'),
            'work_minutes': _('Work Minutes'),
            'work_line': _('Work Line'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, process_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if self.company_id:
            # Filter Person by company
            self.fields['person'].queryset = Person.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).order_by('first_name', 'last_name')
            
            # Filter WorkLine by company and process work lines
            work_line_queryset = WorkLine.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            
            # If process is provided, filter to work lines in that process
            if process_id:
                from production.models import Process
                try:
                    process = Process.objects.get(pk=process_id, company_id=self.company_id)
                    work_line_queryset = work_line_queryset.filter(processes=process)
                except Process.DoesNotExist:
                    pass
            
            self.fields['work_line'].queryset = work_line_queryset.order_by('name')
        else:
            self.fields['person'].queryset = Person.objects.none()
            self.fields['work_line'].queryset = WorkLine.objects.none()
    
    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        work_minutes = cleaned_data.get('work_minutes', Decimal('0'))
        
        if work_minutes < 0:
            self.add_error('work_minutes', _('Work minutes cannot be negative.'))
        
        return cleaned_data


class PerformanceRecordMachineForm(forms.ModelForm):
    """Form for performance record machine items."""
    
    class Meta:
        model = PerformanceRecordMachine
        fields = [
            'machine',
            'work_minutes',
            'work_line',
            'notes',
        ]
        widgets = {
            'machine': forms.Select(attrs={'class': 'form-control'}),
            'work_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'work_line': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'machine': _('Machine'),
            'work_minutes': _('Work Minutes'),
            'work_line': _('Work Line'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, process_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if self.company_id:
            # Filter Machine by company
            self.fields['machine'].queryset = Machine.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).order_by('name')
            
            # Filter WorkLine by company and process work lines
            work_line_queryset = WorkLine.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            
            # If process is provided, filter to work lines in that process
            if process_id:
                from production.models import Process
                try:
                    process = Process.objects.get(pk=process_id, company_id=self.company_id)
                    work_line_queryset = work_line_queryset.filter(processes=process)
                except Process.DoesNotExist:
                    pass
            
            self.fields['work_line'].queryset = work_line_queryset.order_by('name')
        else:
            self.fields['machine'].queryset = Machine.objects.none()
            self.fields['work_line'].queryset = WorkLine.objects.none()
    
    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        work_minutes = cleaned_data.get('work_minutes', Decimal('0'))
        
        if work_minutes < 0:
            self.add_error('work_minutes', _('Work minutes cannot be negative.'))
        
        return cleaned_data


# Create formsets
PerformanceRecordMaterialFormSet = inlineformset_factory(
    PerformanceRecord,
    PerformanceRecordMaterial,
    form=PerformanceRecordMaterialForm,
    extra=0,
    can_delete=True,
    min_num=0,
    validate_min=False,
)

PerformanceRecordPersonFormSet = inlineformset_factory(
    PerformanceRecord,
    PerformanceRecordPerson,
    form=PerformanceRecordPersonForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)

PerformanceRecordMachineFormSet = inlineformset_factory(
    PerformanceRecord,
    PerformanceRecordMachine,
    form=PerformanceRecordMachineForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


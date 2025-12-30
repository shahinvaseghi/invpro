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
    ProcessOperation,
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
            'document_type',
            'order',
            'operation',
            'transfer',
            'performance_date',
            'quantity_planned',
            'quantity_actual',
            'approved_by',
            'notes',
        ]
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_document_type'}),
            'order': forms.Select(attrs={'class': 'form-control', 'id': 'id_order'}),
            'operation': forms.Select(attrs={'class': 'form-control', 'id': 'id_operation'}),
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
            'document_type': _('Document Type'),
            'order': _('Product Order'),
            'operation': _('Process Operation'),
            'transfer': _('Transfer to Line (Optional)'),
            'performance_date': _('Performance Date'),
            'quantity_planned': _('Planned Quantity'),
            'quantity_actual': _('Actual Quantity Produced'),
            'approved_by': _('Approver'),
            'notes': _('Notes'),
        }
        help_texts = {
            'document_type': _('Select whether this is an operational (for specific operation) or general (for entire order) performance record'),
            'order': _('Select the product order for this performance record'),
            'operation': _('Select the process operation (only for operational documents)'),
            'transfer': _('Select the transfer document used (optional, will auto-populate materials if selected)'),
            'quantity_planned': _('Planned quantity from the order (read-only, only for general documents)'),
            'quantity_actual': _('Enter the actual quantity produced (only for general documents)'),
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
            self.fields['operation'].queryset = ProcessOperation.objects.none()
            self.fields['transfer'].queryset = TransferToLine.objects.none()
            self.fields['approved_by'].queryset = User.objects.none()
        
        # Set initial document_type if creating new record
        if not self.instance.pk:
            self.fields['document_type'].initial = PerformanceRecord.DocumentType.OPERATIONAL
        
        # Setup dynamic field visibility based on document_type
        self._setup_field_visibility()
        
        # If editing, set readonly fields
        if self.instance and self.instance.pk:
            if self.instance.is_locked:
                # Locked - make all fields readonly except notes
                for field_name in self.fields:
                    if field_name != 'notes':
                        self.fields[field_name].widget.attrs['readonly'] = True
                        self.fields[field_name].widget.attrs['disabled'] = True
    
    def _setup_field_visibility(self):
        """Setup field visibility based on document_type."""
        # Get current document_type value
        if self.is_bound:
            document_type = self.data.get('document_type', self.initial.get('document_type'))
        elif self.instance and self.instance.pk:
            document_type = self.instance.document_type
        else:
            document_type = self.fields['document_type'].initial or PerformanceRecord.DocumentType.OPERATIONAL
        
        # Show/hide fields based on document_type
        # Note: Actual visibility will be controlled by JavaScript in template
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            # For operational: show operation, hide quantity fields
            self.fields['operation'].required = True
            self.fields['quantity_planned'].required = False
            self.fields['quantity_actual'].required = False
        else:
            # For general: hide operation, show quantity fields
            self.fields['operation'].required = False
            self.fields['quantity_planned'].required = True
            self.fields['quantity_actual'].required = True
        
        # Update operation queryset based on selected order
        if self.company_id:
            # Get order from form data or instance
            order_id = None
            if self.is_bound:
                order_id = self.data.get('order')
            elif self.instance and self.instance.pk:
                order_id = self.instance.order_id
            
            if order_id:
                try:
                    order = ProductOrder.objects.get(pk=order_id, company_id=self.company_id)
                    if order.process:
                        # Get operations that don't have performance records yet
                        operations_with_performance = PerformanceRecord.objects.filter(
                            company_id=self.company_id,
                            order=order,
                            document_type=PerformanceRecord.DocumentType.OPERATIONAL,
                        ).values_list('operation_id', flat=True)
                        
                        self.fields['operation'].queryset = ProcessOperation.objects.filter(
                            process=order.process,
                            company_id=self.company_id,
                        ).exclude(id__in=operations_with_performance).order_by('sequence_order', 'id')
                    else:
                        self.fields['operation'].queryset = ProcessOperation.objects.none()
                except ProductOrder.DoesNotExist:
                    self.fields['operation'].queryset = ProcessOperation.objects.none()
            else:
                self.fields['operation'].queryset = ProcessOperation.objects.none()
    
    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        order = cleaned_data.get('order')
        operation = cleaned_data.get('operation')
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
        
        # Validate document_type and operation relationship
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            if not operation:
                self.add_error('operation', _('Operation must be specified for operational performance records.'))
            else:
                # Validate operation belongs to order's process
                if operation.process_id != order.process_id:
                    self.add_error('operation', _('Selected operation must belong to the selected order\'s process.'))
            
            # For operational documents, quantity fields are not required
            cleaned_data['quantity_planned'] = None
            cleaned_data['quantity_actual'] = None
        else:
            # For general documents, operation must be null
            if operation:
                self.add_error('operation', _('Operation must be null for general performance records.'))
            cleaned_data['operation'] = None
            
            # Validate that all operations have performance records
            if not self.instance.pk:  # Only check when creating new record
                all_operations = ProcessOperation.objects.filter(
                    process=order.process,
                    company_id=self.company_id,
                )
                operations_with_performance = PerformanceRecord.objects.filter(
                    company_id=self.company_id,
                    order=order,
                    document_type=PerformanceRecord.DocumentType.OPERATIONAL,
                ).values_list('operation_id', flat=True)
                
                missing_operations = all_operations.exclude(id__in=operations_with_performance)
                if missing_operations.exists():
                    missing_names = ', '.join([op.name or f"Operation {op.sequence_order}" for op in missing_operations[:5]])
                    if missing_operations.count() > 5:
                        missing_names += f" ... ({missing_operations.count()} total)"
                    self.add_error(
                        'document_type',
                        _('Cannot create general performance record. The following operations still need performance records: {operations}').format(
                            operations=missing_names
                        )
                    )
            
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
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, process_id: Optional[int] = None, operation_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if self.company_id:
            # If operation_id is provided, filter by operation's work line personnel
            if operation_id:
                try:
                    operation = ProcessOperation.objects.select_related('work_line').get(
                        pk=operation_id,
                        company_id=self.company_id,
                    )
                    if operation.work_line:
                        # Filter Person by work line personnel
                        self.fields['person'].queryset = operation.work_line.personnel.filter(
                            company_id=self.company_id,
                            is_enabled=1,
                        ).order_by('first_name', 'last_name')
                        # Set work_line to operation's work_line (read-only)
                        self.fields['work_line'].queryset = WorkLine.objects.filter(
                            pk=operation.work_line_id,
                            company_id=self.company_id,
                        )
                        # Set initial value for work_line
                        self.fields['work_line'].initial = operation.work_line_id
                        # Make work_line read-only since it's determined by operation
                        self.fields['work_line'].widget.attrs['readonly'] = True
                    else:
                        # No work line assigned to operation
                        self.fields['person'].queryset = Person.objects.none()
                        self.fields['work_line'].queryset = WorkLine.objects.none()
                except ProcessOperation.DoesNotExist:
                    # Fallback to company-wide filter
                    self.fields['person'].queryset = Person.objects.filter(
                        company_id=self.company_id,
                        is_enabled=1,
                    ).order_by('first_name', 'last_name')
                    self.fields['work_line'].queryset = WorkLine.objects.filter(
                        company_id=self.company_id,
                        is_enabled=1,
                    ).order_by('name')
            else:
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
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, process_id: Optional[int] = None, operation_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if self.company_id:
            # If operation_id is provided, filter by operation's work line machines
            if operation_id:
                try:
                    operation = ProcessOperation.objects.select_related('work_line').get(
                        pk=operation_id,
                        company_id=self.company_id,
                    )
                    if operation.work_line:
                        # Filter Machine by work line machines
                        self.fields['machine'].queryset = operation.work_line.machines.filter(
                            company_id=self.company_id,
                            is_enabled=1,
                        ).order_by('name')
                        # Set work_line to operation's work_line (read-only)
                        self.fields['work_line'].queryset = WorkLine.objects.filter(
                            pk=operation.work_line_id,
                            company_id=self.company_id,
                        )
                        # Set initial value for work_line
                        self.fields['work_line'].initial = operation.work_line_id
                        # Make work_line read-only since it's determined by operation
                        self.fields['work_line'].widget.attrs['readonly'] = True
                    else:
                        # No work line assigned to operation
                        self.fields['machine'].queryset = Machine.objects.none()
                        self.fields['work_line'].queryset = WorkLine.objects.none()
                except ProcessOperation.DoesNotExist:
                    # Fallback to company-wide filter
                    self.fields['machine'].queryset = Machine.objects.filter(
                        company_id=self.company_id,
                        is_enabled=1,
                    ).order_by('name')
                    self.fields['work_line'].queryset = WorkLine.objects.filter(
                        company_id=self.company_id,
                        is_enabled=1,
                    ).order_by('name')
            else:
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


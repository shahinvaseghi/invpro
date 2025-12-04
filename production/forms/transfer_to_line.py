"""
Transfer to Line Request forms for production module.
"""
from typing import Optional
from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from inventory.fields import JalaliDateField
from production.models import TransferToLine, TransferToLineItem, ProductOrder


class TransferToLineForm(forms.ModelForm):
    """Form for creating/editing transfer to line requests."""
    
    # Override transfer_date to use JalaliDateField
    transfer_date = JalaliDateField(
        required=True,
        label=_('تاریخ انتقال'),
    )
    
    # Transfer type: 'full' for all materials, 'operations' for selected operations
    transfer_type = forms.ChoiceField(
        choices=[
            ('full', _('انتقال همه مواد')),
            ('operations', _('انتقال عملیات انتخابی')),
        ],
        initial='full',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_('نوع انتقال'),
        help_text=_('انتخاب کنید که آیا همه مواد انتقال داده شوند یا مواد از عملیات خاص'),
    )
    
    # Selected operations (for transfer_type='operations')
    selected_operations = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label=_('انتخاب عملیات'),
        help_text=_('عملیات‌هایی که مواد آنها باید انتقال داده شود را انتخاب کنید'),
    )
    
    # Override is_scrap_replacement as BooleanField to handle checkbox properly
    is_scrap_replacement = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('جایگزینی ضایعات'),
        help_text=_('اگر این انتقال برای جایگزینی مواد ضایعاتی است، این گزینه را انتخاب کنید'),
    )
    
    class Meta:
        model = TransferToLine
        fields = [
            'order',
            'transfer_date',
            'approved_by',
            'is_scrap_replacement',
            'qc_approved_by',
            'notes',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control', 'id': 'id_order'}),
            'approved_by': forms.Select(attrs={'class': 'form-control'}),
            'qc_approved_by': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'order': _('سفارش محصول'),
            'transfer_date': _('تاریخ انتقال'),
            'approved_by': _('تایید کننده'),
            'qc_approved_by': _('تایید کننده QC'),
            'notes': _('یادداشت‌ها'),
        }
        help_texts = {
            'order': _('سفارش محصول را برای این درخواست انتقال انتخاب کنید'),
            'approved_by': _('کاربری که می‌تواند این درخواست انتقال را تایید کند انتخاب کنید'),
            'qc_approved_by': _('کاربری که می‌تواند تایید QC را برای این درخواست انتقال انجام دهد (فقط برای جایگزینی ضایعات)'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        if self.company_id:
            # Filter Product Orders by company and valid statuses for transfer
            # Show orders that are planned, released, or in_progress and have BOM
            self.fields['order'].queryset = ProductOrder.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
                status__in=['planned', 'released', 'in_progress'],  # Valid statuses for transfer
                bom__isnull=False,  # Must have BOM for transfer
            ).select_related('bom', 'finished_item').order_by('-order_date', 'order_code')
            
            # Filter approved_by (User) - only users with approve permission for production.transfer_requests
            from shared.models import UserCompanyAccess, AccessLevelPermission
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Find access levels that have approve permission for production.transfer_requests
            approve_access_levels = list(AccessLevelPermission.objects.filter(
                module_code='production',
                resource_code='production.transfer_requests',
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
            
            # Filter QC approvers - users with QC approval permission for transfer requests
            # Use resource code 'production.transfer_requests.qc_approval' for QC approvers
            qc_approve_access_levels = list(AccessLevelPermission.objects.filter(
                module_code='production',
                resource_code='production.transfer_requests.qc_approval',
                can_approve=1,
            ).values_list('access_level_id', flat=True))
            
            # If no specific QC approval permission found, fallback to regular approve permission
            if not qc_approve_access_levels:
                qc_approve_access_levels = approve_access_levels
            
            # Find users with QC approve permission for this company
            qc_approver_user_ids = list(UserCompanyAccess.objects.filter(
                company_id=self.company_id,
                access_level_id__in=qc_approve_access_levels,
                is_enabled=1,
            ).values_list('user_id', flat=True))
            
            # Filter QC approver queryset
            if qc_approver_user_ids:
                self.fields['qc_approved_by'].queryset = User.objects.filter(
                    Q(id__in=qc_approver_user_ids) | Q(is_superuser=True),
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
            else:
                # If no QC approvers found, show only superusers
                self.fields['qc_approved_by'].queryset = User.objects.filter(
                    is_superuser=True,
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            self.fields['order'].queryset = ProductOrder.objects.none()
            self.fields['approved_by'].queryset = User.objects.none()
            self.fields['qc_approved_by'].queryset = User.objects.none()
        
        # Initialize selected_operations choices (will be populated via JavaScript)
        self.fields['selected_operations'].choices = []
        
        # Set initial value for is_scrap_replacement from instance if editing
        if self.instance and self.instance.pk:
            self.fields['is_scrap_replacement'].initial = (self.instance.is_scrap_replacement == 1)
        
        # Make qc_approved_by field conditional (only shown when is_scrap_replacement is checked)
        # This will be handled via JavaScript in the template
    
    def clean(self) -> dict:
        """Validate form data."""
        cleaned_data = super().clean()
        order = cleaned_data.get('order')
        transfer_type = cleaned_data.get('transfer_type')
        selected_operations = cleaned_data.get('selected_operations', [])
        
        # Convert is_scrap_replacement from BooleanField (True/False) to PositiveSmallIntegerField (0/1)
        is_scrap_replacement_bool = cleaned_data.get('is_scrap_replacement', False)
        is_scrap_replacement = 1 if is_scrap_replacement_bool else 0
        cleaned_data['is_scrap_replacement'] = is_scrap_replacement
        
        qc_approved_by = cleaned_data.get('qc_approved_by')
        
        # Validate order is selected
        if not order:
            raise forms.ValidationError(_('Product Order is required.'))
        
        # Validate order has BOM
        if order and not order.bom:
            raise forms.ValidationError(_('Selected product order must have a BOM.'))
        
        # Validate scrap replacement: only allowed if order has previous transfers
        if order and is_scrap_replacement == 1:
            from production.models import TransferToLine
            # Check if order has any previous transfers (excluding scrap replacements)
            has_previous_transfers = TransferToLine.objects.filter(
                order=order,
                is_enabled=1,
                is_scrap_replacement=0,  # Exclude scrap replacements
            ).exists()
            
            if not has_previous_transfers:
                raise forms.ValidationError({
                    'is_scrap_replacement': _(
                        'Scrap replacement can only be selected for orders that have already been transferred. '
                        'This order has no previous transfer requests.'
                    )
                })
        
        # Validate QC approver if scrap replacement is checked
        if is_scrap_replacement == 1 and not qc_approved_by:
            raise forms.ValidationError({
                'qc_approved_by': _('QC approver is required when scrap replacement is selected.')
            })
        
        # If transfer_type is 'operations', validate that operations are selected
        if transfer_type == 'operations':
            if not selected_operations:
                raise forms.ValidationError({
                    'selected_operations': _('Please select at least one operation when transferring specific operations.')
                })
        
        # Validate against already transferred materials (if not scrap replacement)
        if order and is_scrap_replacement == 0:
            from production.utils.transfer import (
                is_full_order_transferred,
                get_available_operations_for_order,
            )
            
            # Check if full order is already transferred
            if transfer_type == 'full' and is_full_order_transferred(order, exclude_scrap_replacement=True):
                raise forms.ValidationError(
                    _('All materials for this order have already been transferred. '
                      'If this is for scrap replacement, please check the "Scrap Replacement" checkbox.')
                )
            
            # Check if selected operations are already transferred
            if transfer_type == 'operations':
                available_operations = get_available_operations_for_order(order, include_scrap_replacement=False)
                available_operation_ids = {str(op['id']) for op in available_operations}
                
                invalid_operations = [op_id for op_id in selected_operations if op_id not in available_operation_ids]
                if invalid_operations:
                    raise forms.ValidationError({
                        'selected_operations': _(
                            'Some selected operations have already been transferred. '
                            'If this is for scrap replacement, please check the "Scrap Replacement" checkbox.'
                        )
                    })
        
        return cleaned_data


class TransferToLineItemForm(forms.ModelForm):
    """Form for individual transfer to line item (extra requests only)."""
    
    # Filter fields (UI-only, not saved to database)
    material_type = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('نوع ماده'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('فیلتر کردن مواد بر اساس نوع'),
    )
    material_category_filter = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('دسته‌بندی'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('فیلتر کردن مواد بر اساس دسته‌بندی'),
    )
    material_subcategory_filter = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('زیردسته‌بندی'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('فیلتر کردن مواد بر اساس زیردسته‌بندی'),
    )
    
    class Meta:
        model = TransferToLineItem
        fields = [
            'material_item',
            'quantity_required',
            'unit',
            'source_warehouse',
            'destination_work_center',
            'material_scrap_allowance',
            'notes',
        ]
        widgets = {
            'material_item': forms.Select(attrs={
                'class': 'form-control searchable-select',
                'data-searchable': 'true'
            }),
            'quantity_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0'
            }),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'source_warehouse': forms.Select(attrs={
                'class': 'form-control searchable-select',
                'data-searchable': 'true'
            }),
            'destination_work_center': forms.Select(attrs={
                'class': 'form-control searchable-select',
                'data-searchable': 'true'
            }),
            'material_scrap_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'material_item': _('کالای مورد نیاز'),
            'quantity_required': _('مقدار مورد نیاز'),
            'unit': _('واحد'),
            'source_warehouse': _('انبار مبدا'),
            'destination_work_center': _('خط کاری مقصد'),
            'material_scrap_allowance': _('ضریب ضایعات (%)'),
            'notes': _('یادداشت‌ها'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        if self.company_id:
            # Filter items by company
            from inventory.models import Item, Warehouse, ItemType, ItemCategory, ItemSubcategory
            from production.models import WorkLine
            
            # Material type filter
            self.fields['material_type'].queryset = ItemType.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).order_by('public_code', 'name')
            
            # Category filter (initially empty, populated via JavaScript)
            self.fields['material_category_filter'].queryset = ItemCategory.objects.none()
            
            # Subcategory filter (initially empty, populated via JavaScript)
            self.fields['material_subcategory_filter'].queryset = ItemSubcategory.objects.none()
            
            # Material item (initially all items, filtered via JavaScript)
            self.fields['material_item'].queryset = Item.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).select_related('type', 'category', 'subcategory').order_by('item_code', 'name')
            
            self.fields['source_warehouse'].queryset = Warehouse.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).order_by('public_code', 'name')
            
            self.fields['destination_work_center'].queryset = WorkLine.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).select_related('warehouse').order_by('public_code', 'name')
            
            # Unit field will be populated dynamically via JavaScript based on selected item
            self.fields['unit'].widget.attrs['disabled'] = True
            
            # If editing existing item, populate filter fields from item
            if self.instance and self.instance.pk and self.instance.material_item:
                item = self.instance.material_item
                if item.type:
                    self.fields['material_type'].initial = item.type_id
                if item.category:
                    self.fields['material_category_filter'].initial = item.category_id
                if item.subcategory:
                    self.fields['material_subcategory_filter'].initial = item.subcategory_id
        else:
            from inventory.models import Item, Warehouse, ItemType, ItemCategory, ItemSubcategory
            from production.models import WorkLine
            
            self.fields['material_type'].queryset = ItemType.objects.none()
            self.fields['material_category_filter'].queryset = ItemCategory.objects.none()
            self.fields['material_subcategory_filter'].queryset = ItemSubcategory.objects.none()
            self.fields['material_item'].queryset = Item.objects.none()
            self.fields['source_warehouse'].queryset = Warehouse.objects.none()
            self.fields['destination_work_center'].queryset = WorkLine.objects.none()
    
    def clean(self) -> dict:
        """Validate form data."""
        cleaned_data = super().clean()
        material_item = cleaned_data.get('material_item')
        quantity_required = cleaned_data.get('quantity_required')
        unit = cleaned_data.get('unit')
        
        # Remove filter fields from cleaned_data (they're not saved to DB)
        if 'material_category_filter' in cleaned_data:
            del cleaned_data['material_category_filter']
        if 'material_subcategory_filter' in cleaned_data:
            del cleaned_data['material_subcategory_filter']
        if 'material_type' in cleaned_data:
            del cleaned_data['material_type']
        
        # Validate material item is selected
        if not material_item:
            raise forms.ValidationError(_('Material item is required.'))
        
        # Validate quantity is positive
        if quantity_required and quantity_required <= 0:
            raise forms.ValidationError(_('Quantity must be greater than zero.'))
        
        # Validate unit is selected
        if material_item and not unit:
            raise forms.ValidationError(_('Unit is required for the selected material.'))
        
        return cleaned_data
    
    def full_clean(self) -> None:
        """Override to exclude filter fields from validation."""
        # Temporarily remove filter fields from self.fields for validation
        filter_fields = ['material_type', 'material_category_filter', 'material_subcategory_filter']
        saved_fields = {}
        for field_name in filter_fields:
            if field_name in self.fields:
                saved_fields[field_name] = self.fields[field_name]
                del self.fields[field_name]
        
        try:
            super().full_clean()
        finally:
            # Restore filter fields after validation
            self.fields.update(saved_fields)


# FormSet for extra request items
TransferToLineItemFormSet = inlineformset_factory(
    TransferToLine,
    TransferToLineItem,
    form=TransferToLineItemForm,
    extra=1,  # Show 1 empty form initially
    can_delete=True,  # Allow deletion of existing lines
    min_num=0,  # Allow zero extra items (all items can come from BOM)
    validate_min=False,  # Don't validate minimum (can be 0)
)


"""
Transfer to Line Request forms for production module.
"""
from typing import Optional
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from inventory.fields import JalaliDateField
from production.models import TransferToLine, TransferToLineItem, ProductOrder


class TransferToLineForm(forms.ModelForm):
    """Form for creating/editing transfer to line requests."""
    
    # Override transfer_date to use JalaliDateField
    transfer_date = JalaliDateField(
        required=True,
        label=_('Transfer Date'),
    )
    
    class Meta:
        model = TransferToLine
        fields = [
            'order',
            'transfer_date',
            'approved_by',
            'notes',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'approved_by': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'order': _('Product Order'),
            'transfer_date': _('Transfer Date'),
            'approved_by': _('Approver'),
            'notes': _('Notes'),
        }
        help_texts = {
            'order': _('Select the product order for this transfer request'),
            'approved_by': _('Select the user who can approve this transfer request'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        if self.company_id:
            # Filter Product Orders by company and approved status
            self.fields['order'].queryset = ProductOrder.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
                status='approved',  # Only show approved orders
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
            if approver_user_ids:
                self.fields['approved_by'].queryset = User.objects.filter(
                    id__in=approver_user_ids,
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
            else:
                # No approvers found, show empty queryset
                self.fields['approved_by'].queryset = User.objects.none()
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            self.fields['order'].queryset = ProductOrder.objects.none()
            self.fields['approved_by'].queryset = User.objects.none()
    
    def clean(self) -> dict:
        """Validate form data."""
        cleaned_data = super().clean()
        order = cleaned_data.get('order')
        
        # Validate order is selected
        if not order:
            raise forms.ValidationError(_('Product Order is required.'))
        
        # Validate order has BOM
        if order and not order.bom:
            raise forms.ValidationError(_('Selected product order must have a BOM.'))
        
        return cleaned_data


class TransferToLineItemForm(forms.ModelForm):
    """Form for individual transfer to line item (extra requests only)."""
    
    # Filter fields (UI-only, not saved to database)
    material_type = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('Material Type'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Filter materials by type'),
    )
    material_category_filter = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('Category'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Filter materials by category'),
    )
    material_subcategory_filter = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('Subcategory'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Filter materials by subcategory'),
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
            'material_item': forms.Select(attrs={'class': 'form-control'}),
            'quantity_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0'
            }),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'source_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'destination_work_center': forms.Select(attrs={'class': 'form-control'}),
            'material_scrap_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'material_item': _('Material Item'),
            'quantity_required': _('Quantity Required'),
            'unit': _('Unit'),
            'source_warehouse': _('Source Warehouse'),
            'destination_work_center': _('Destination Work Center'),
            'material_scrap_allowance': _('Scrap Allowance (%)'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        if self.company_id:
            # Filter items by company
            from inventory.models import Item, Warehouse, ItemType, ItemCategory, ItemSubcategory
            from production.models import WorkCenter
            
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
            
            self.fields['destination_work_center'].queryset = WorkCenter.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).order_by('public_code', 'name')
            
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
            from production.models import WorkCenter
            
            self.fields['material_type'].queryset = ItemType.objects.none()
            self.fields['material_category_filter'].queryset = ItemCategory.objects.none()
            self.fields['material_subcategory_filter'].queryset = ItemSubcategory.objects.none()
            self.fields['material_item'].queryset = Item.objects.none()
            self.fields['source_warehouse'].queryset = Warehouse.objects.none()
            self.fields['destination_work_center'].queryset = WorkCenter.objects.none()
    
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


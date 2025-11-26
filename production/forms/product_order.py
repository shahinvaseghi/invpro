"""
Product Order forms for production module.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _

from inventory.fields import JalaliDateField
from production.models import ProductOrder, BOM


class ProductOrderForm(forms.ModelForm):
    """Form for creating/editing product orders."""
    
    # Override due_date to use JalaliDateField
    due_date = JalaliDateField(
        required=False,
        label=_('Due Date'),
    )
    
    # Optional: Create transfer request from this order
    create_transfer_request = forms.BooleanField(
        required=False,
        label=_('Create Transfer Request'),
        help_text=_('Check to create a transfer to line request from this order'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    
    # Transfer request approver (only shown if create_transfer_request is checked)
    transfer_approved_by = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('Transfer Request Approver'),
        help_text=_('Select the user who can approve the transfer request'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = ProductOrder
        fields = [
            'bom',
            'quantity_planned',
            'approved_by',
            'due_date',
            'priority',
            'customer_reference',
            'notes',
        ]
        widgets = {
            'bom': forms.Select(attrs={'class': 'form-control'}),
            'quantity_planned': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0'
            }),
            'approved_by': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'customer_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'bom': _('BOM (Bill of Materials)'),
            'quantity_planned': _('Quantity'),
            'approved_by': _('Approver'),
            'due_date': _('Due Date'),
            'priority': _('Priority'),
            'customer_reference': _('Customer Reference'),
            'notes': _('Notes'),
        }
        help_texts = {
            'bom': _('Select the BOM for this production order'),
            'quantity_planned': _('Enter the planned quantity to produce'),
            'approved_by': _('Select the user who can approve this order'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        if self.company_id:
            # Filter BOMs by company
            self.fields['bom'].queryset = BOM.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).select_related('finished_item').order_by('finished_item__item_code', 'version')
            
            # Filter approved_by (User) - only users with approve permission for production.product_orders
            from shared.models import UserCompanyAccess, AccessLevelPermission
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Find access levels that have approve permission for production.product_orders
            approve_access_levels = list(AccessLevelPermission.objects.filter(
                module_code='production',
                resource_code='production.product_orders',
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
            
            # Filter transfer_approved_by (users with approve permission for transfer_requests)
            from shared.models import AccessLevelPermission as ALP
            transfer_approve_access_levels = list(ALP.objects.filter(
                module_code='production',
                resource_code='production.transfer_requests',
                can_approve=1,
            ).values_list('access_level_id', flat=True))
            
            transfer_approver_user_ids = list(UserCompanyAccess.objects.filter(
                company_id=self.company_id,
                access_level_id__in=transfer_approve_access_levels,
                is_enabled=1,
            ).values_list('user_id', flat=True))
            
            if transfer_approver_user_ids:
                self.fields['transfer_approved_by'].queryset = User.objects.filter(
                    id__in=transfer_approver_user_ids,
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
            else:
                self.fields['transfer_approved_by'].queryset = User.objects.none()
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            self.fields['bom'].queryset = BOM.objects.none()
            self.fields['approved_by'].queryset = User.objects.none()
            self.fields['transfer_approved_by'].queryset = User.objects.none()
    
    def clean(self) -> dict:
        """Validate form data."""
        cleaned_data = super().clean()
        bom = cleaned_data.get('bom')
        quantity_planned = cleaned_data.get('quantity_planned')
        create_transfer_request = cleaned_data.get('create_transfer_request')
        transfer_approved_by = cleaned_data.get('transfer_approved_by')
        
        # Validate BOM is selected
        if not bom:
            raise forms.ValidationError(_('BOM is required.'))
        
        # Validate quantity is positive
        if quantity_planned and quantity_planned <= 0:
            raise forms.ValidationError(_('Quantity must be greater than zero.'))
        
        # If create_transfer_request is checked, transfer_approved_by is required
        if create_transfer_request and not transfer_approved_by:
            raise forms.ValidationError(_('Transfer Request Approver is required when creating a transfer request.'))
        
        # Auto-set finished_item from BOM if not already set
        if bom and not self.instance.finished_item_id:
            self.instance.finished_item = bom.finished_item
        
        return cleaned_data


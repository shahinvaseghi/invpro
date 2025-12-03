"""
Product Order forms for production module.
"""
from typing import Optional
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from inventory.fields import JalaliDateField
from production.models import ProductOrder, BOM, Process


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
    
    # Transfer type: 'full' for all materials, 'operations' for selected operations
    transfer_type = forms.ChoiceField(
        choices=[
            ('full', _('انتقال همه مواد')),
            ('operations', _('انتقال عملیات انتخابی')),
        ],
        initial='full',
        required=False,
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
    
    class Meta:
        model = ProductOrder
        fields = [
            'process',
            'quantity_planned',
            'approved_by',
            'due_date',
            'priority',
            'customer_reference',
            'notes',
        ]
        widgets = {
            'process': forms.Select(attrs={'class': 'form-control', 'id': 'id_process'}),
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
            'process': _('Process (فرایند)'),
            'quantity_planned': _('Quantity'),
            'approved_by': _('Approver'),
            'due_date': _('Due Date'),
            'priority': _('Priority'),
            'customer_reference': _('Customer Reference'),
            'notes': _('Notes'),
        }
        help_texts = {
            'process': _('Select the process for this production order'),
            'quantity_planned': _('Enter the planned quantity to produce'),
            'approved_by': _('Select the user who can approve this order'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        if self.company_id:
            # Filter Processes by company - show all enabled processes
            self.fields['process'].queryset = Process.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            ).select_related('finished_item', 'bom').order_by('finished_item__item_code', 'revision')
            
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
            
            # Also include superusers automatically for transfer approvers
            if transfer_approver_user_ids:
                self.fields['transfer_approved_by'].queryset = User.objects.filter(
                    Q(id__in=transfer_approver_user_ids) | Q(is_superuser=True),
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
            else:
                # If no approvers found, show only superusers
                self.fields['transfer_approved_by'].queryset = User.objects.filter(
                    is_superuser=True,
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            self.fields['process'].queryset = Process.objects.none()
            self.fields['approved_by'].queryset = User.objects.none()
            self.fields['transfer_approved_by'].queryset = User.objects.none()
        
        # Initialize selected_operations choices (will be populated via JavaScript)
        self.fields['selected_operations'].choices = []
    
    def clean(self) -> dict:
        """Validate form data."""
        cleaned_data = super().clean()
        process = cleaned_data.get('process')
        quantity_planned = cleaned_data.get('quantity_planned')
        create_transfer_request = cleaned_data.get('create_transfer_request')
        transfer_approved_by = cleaned_data.get('transfer_approved_by')
        transfer_type = cleaned_data.get('transfer_type', 'full')
        selected_operations = cleaned_data.get('selected_operations', [])
        
        # Validate Process is selected
        if not process:
            raise forms.ValidationError(_('Process is required.'))
        
        # Validate quantity is positive
        if quantity_planned and quantity_planned <= 0:
            raise forms.ValidationError(_('Quantity must be greater than zero.'))
        
        # If create_transfer_request is checked, transfer_approved_by is required
        if create_transfer_request and not transfer_approved_by:
            raise forms.ValidationError(_('Transfer Request Approver is required when creating a transfer request.'))
        
        # If create_transfer_request is checked and transfer_type is 'operations', validate that operations are selected
        if create_transfer_request and transfer_type == 'operations':
            if not selected_operations:
                raise forms.ValidationError({
                    'selected_operations': _('Please select at least one operation when transferring specific operations.')
                })
        
        # Auto-set finished_item and bom from Process
        if process:
            if not self.instance.finished_item_id:
                self.instance.finished_item = process.finished_item
            if process.bom and not self.instance.bom_id:
                self.instance.bom = process.bom
        
        return cleaned_data


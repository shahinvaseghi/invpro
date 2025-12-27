"""
Forms for Service Request.
"""
from typing import Optional, Any
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from procurement.models import ServiceRequest
from inventory.models import Supplier
from inventory.widgets import JalaliDateInput
from shared.forms.base import BaseModelForm


class ServiceRequestForm(BaseModelForm):
    """Form for service request."""
    
    class Meta:
        model = ServiceRequest
        fields = [
            'supplier',
            'service_description',
            'priority',
            'needed_by_date',
            'estimated_cost',
            'approver',
            'approval_notes',
        ]
        widgets = {
            'service_description': forms.Textarea(attrs={'rows': 5}),
            'needed_by_date': JalaliDateInput(),
            'estimated_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'approval_notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'supplier': _('Service Provider / Supplier'),
            'service_description': _('Service Description'),
            'priority': _('Priority'),
            'needed_by_date': _('Needed By Date'),
            'estimated_cost': _('Estimated Cost'),
            'approver': _('Approver'),
            'approval_notes': _('Approval Notes'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, company_id=company_id, **kwargs)
        
        if company_id:
            # Filter suppliers by company
            if 'supplier' in self.fields:
                self.fields['supplier'].queryset = Supplier.objects.filter(
                    company_id=company_id, is_enabled=1
                ).order_by('name')
                self.fields['supplier'].empty_label = _("--- انتخاب کنید ---")
                self.fields['supplier'].required = False
            
            # Filter approvers by company
            if 'approver' in self.fields:
                from inventory.forms.base import get_feature_approvers
                approvers = get_feature_approvers("procurement.services.request", company_id)
                self.fields['approver'].queryset = approvers
                self.fields['approver'].empty_label = _("--- انتخاب کنید ---")
                self.fields['approver'].required = False
        
        # Set default request_date (will be set in view)
        # Set default priority
        if not self.instance.pk:
            if 'priority' in self.fields:
                self.fields['priority'].initial = ServiceRequest.Priority.NORMAL


"""
Forms for Service Invoice.
"""
from typing import Optional, Any
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from procurement.models import ServiceInvoice, ServiceRequest
from inventory.models import Supplier
from inventory.widgets import JalaliDateInput
from shared.forms.base import BaseModelForm


class ServiceInvoiceForm(BaseModelForm):
    """Form for service invoice."""
    
    class Meta:
        model = ServiceInvoice
        fields = [
            'supplier',
            'party',
            'service_request',
            'invoice_date',
            'invoice_number',
            'service_description',
            'subtotal',
            'vat_rate',
            'vat_amount',
            'total_amount',
            'notes',
        ]
        widgets = {
            'invoice_date': JalaliDateInput(),
            'invoice_number': forms.TextInput(),
            'service_description': forms.Textarea(attrs={'rows': 5}),
            'subtotal': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'vat_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'vat_amount': forms.HiddenInput(),
            'total_amount': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'supplier': _('Service Provider / Supplier'),
            'party': _('Party (Accounting)'),
            'service_request': _('Service Request'),
            'invoice_date': _('Invoice Date'),
            'invoice_number': _('Invoice Number (Supplier)'),
            'service_description': _('Service Description'),
            'subtotal': _('Subtotal'),
            'vat_rate': _('VAT Rate (%)'),
            'notes': _('Notes'),
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
            
            # Filter parties by company
            if 'party' in self.fields:
                from accounting.models import Party
                self.fields['party'].queryset = Party.objects.filter(
                    company_id=company_id, is_enabled=1
                ).order_by('party_name')
                self.fields['party'].empty_label = _("--- انتخاب کنید ---")
                self.fields['party'].required = False
            
            # Filter service requests by company
            if 'service_request' in self.fields:
                self.fields['service_request'].queryset = ServiceRequest.objects.filter(
                    company_id=company_id
                ).order_by('-request_date', '-request_code')
                self.fields['service_request'].empty_label = _("--- انتخاب کنید ---")
                self.fields['service_request'].required = False
        
        # Set default invoice_date and vat_rate
        if not self.instance.pk:
            if 'invoice_date' in self.fields:
                self.fields['invoice_date'].initial = timezone.now().date()
            if 'vat_rate' in self.fields:
                self.fields['vat_rate'].initial = 9.0


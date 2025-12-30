"""
Forms for Payment Request.
"""
from typing import Optional, Any
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from ..models.payment_requests import PaymentRequest
from ..models.parties import Party
from ..models.accounts import Account
from procurement.models import PurchaseInvoice, ServiceInvoice
from inventory.widgets import JalaliDateInput
from shared.forms.base import BaseModelForm


class PaymentRequestForm(BaseModelForm):
    """Form for payment request."""
    
    class Meta:
        model = PaymentRequest
        fields = [
            'payment_type',
            'party',
            'purchase_invoice',
            'service_invoice',
            'expense_category',
            'expense_description',
            'prepayment_account',
            'request_date',
            'amount',
            'due_date',
            'notes',
        ]
        widgets = {
            'request_date': JalaliDateInput(),
            'due_date': JalaliDateInput(),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'expense_description': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'payment_type': _('Payment Type'),
            'party': _('Party'),
            'purchase_invoice': _('Purchase Invoice'),
            'service_invoice': _('Service Invoice'),
            'expense_category': _('Expense Category'),
            'expense_description': _('Expense Description'),
            'prepayment_account': _('Prepayment Account'),
            'request_date': _('Request Date'),
            'amount': _('Amount'),
            'due_date': _('Due Date'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, company_id=company_id, **kwargs)
        
        if company_id:
            # Filter parties by company
            if 'party' in self.fields:
                self.fields['party'].queryset = Party.objects.filter(
                    company_id=company_id, is_enabled=1
                ).order_by('party_name')
                self.fields['party'].empty_label = _("--- انتخاب کنید ---")
                self.fields['party'].required = False
            
            # Filter purchase invoices by company
            if 'purchase_invoice' in self.fields:
                self.fields['purchase_invoice'].queryset = PurchaseInvoice.objects.filter(
                    company_id=company_id
                ).order_by('-invoice_date', '-invoice_code')
                self.fields['purchase_invoice'].empty_label = _("--- انتخاب کنید ---")
                self.fields['purchase_invoice'].required = False
            
            # Filter service invoices by company
            if 'service_invoice' in self.fields:
                self.fields['service_invoice'].queryset = ServiceInvoice.objects.filter(
                    company_id=company_id
                ).order_by('-invoice_date', '-invoice_code')
                self.fields['service_invoice'].empty_label = _("--- انتخاب کنید ---")
                self.fields['service_invoice'].required = False
            
            # Filter expense categories by company
            if 'expense_category' in self.fields:
                from ..models.income_expense_categories import IncomeExpenseCategory
                self.fields['expense_category'].queryset = IncomeExpenseCategory.objects.filter(
                    company_id=company_id, is_enabled=1
                ).order_by('category_name')
                self.fields['expense_category'].empty_label = _("--- انتخاب کنید ---")
                self.fields['expense_category'].required = False
            
            # Filter prepayment accounts by company (only tafsili accounts - level 3)
            if 'prepayment_account' in self.fields:
                self.fields['prepayment_account'].queryset = Account.objects.filter(
                    company_id=company_id,
                    account_level=3,
                    is_enabled=1
                ).order_by('account_code')
                self.fields['prepayment_account'].empty_label = _("--- انتخاب کنید ---")
                self.fields['prepayment_account'].required = False
        
        # Set default request_date
        if not self.instance.pk and 'request_date' in self.fields:
            self.fields['request_date'].initial = timezone.now().date()
    
    def clean(self):
        """Validate form data based on payment_type."""
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        
        if payment_type == PaymentRequest.PaymentType.PURCHASE_INVOICE:
            if not cleaned_data.get('purchase_invoice'):
                raise forms.ValidationError({
                    'purchase_invoice': _('Purchase invoice is required for purchase invoice payments.')
                })
            if not cleaned_data.get('party'):
                raise forms.ValidationError({
                    'party': _('Party is required for purchase invoice payments.')
                })
        
        elif payment_type == PaymentRequest.PaymentType.SERVICE_INVOICE:
            if not cleaned_data.get('service_invoice'):
                raise forms.ValidationError({
                    'service_invoice': _('Service invoice is required for service invoice payments.')
                })
            if not cleaned_data.get('party'):
                raise forms.ValidationError({
                    'party': _('Party is required for service invoice payments.')
                })
        
        elif payment_type == PaymentRequest.PaymentType.DIRECT_EXPENSE:
            if not cleaned_data.get('expense_category'):
                raise forms.ValidationError({
                    'expense_category': _('Expense category is required for direct expense payments.')
                })
            if not cleaned_data.get('expense_description'):
                raise forms.ValidationError({
                    'expense_description': _('Expense description is required for direct expense payments.')
                })
        
        elif payment_type == PaymentRequest.PaymentType.PREPAYMENT:
            if not cleaned_data.get('prepayment_account'):
                raise forms.ValidationError({
                    'prepayment_account': _('Prepayment account is required for prepayment payments.')
                })
            if not cleaned_data.get('party'):
                raise forms.ValidationError({
                    'party': _('Party is required for prepayment payments.')
                })
        
        return cleaned_data


"""
Forms for Purchase Invoice.
"""
from typing import Optional, Any
from django import forms
from django.forms import inlineformset_factory
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from procurement.models import PurchaseInvoice, PurchaseInvoiceLine, PurchaseOrder
from inventory.models import Item, Supplier, ReceiptPermanent
from inventory.forms.base import UNIT_CHOICES, BaseLineFormSet
from inventory.widgets import JalaliDateInput
from shared.forms.base import BaseModelForm


class PurchaseInvoiceForm(BaseModelForm):
    """Form for purchase invoice header."""
    
    class Meta:
        model = PurchaseInvoice
        fields = [
            'supplier',
            'party',
            'receipt_permanent',
            'purchase_order',
            'invoice_date',
            'invoice_number',
            'vat_rate',
            'notes',
        ]
        widgets = {
            'invoice_date': JalaliDateInput(),
            'invoice_number': forms.TextInput(),
            'vat_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'supplier': _('Supplier'),
            'party': _('Party (Accounting)'),
            'receipt_permanent': _('Receipt (Permanent)'),
            'purchase_order': _('Purchase Order'),
            'invoice_date': _('Invoice Date'),
            'invoice_number': _('Invoice Number (Supplier)'),
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
            
            # Filter receipts by company
            if 'receipt_permanent' in self.fields:
                self.fields['receipt_permanent'].queryset = ReceiptPermanent.objects.filter(
                    company_id=company_id
                ).order_by('-document_date', '-document_code')
                self.fields['receipt_permanent'].empty_label = _("--- انتخاب کنید ---")
                self.fields['receipt_permanent'].required = False
            
            # Filter purchase orders by company
            if 'purchase_order' in self.fields:
                self.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(
                    company_id=company_id
                ).order_by('-order_date', '-order_code')
                self.fields['purchase_order'].empty_label = _("--- انتخاب کنید ---")
                self.fields['purchase_order'].required = False
        
        # Set default invoice_date and vat_rate
        if not self.instance.pk:
            if 'invoice_date' in self.fields:
                self.fields['invoice_date'].initial = timezone.now().date()
            if 'vat_rate' in self.fields:
                self.fields['vat_rate'].initial = 9.0


class PurchaseInvoiceLineForm(forms.ModelForm):
    """Form for purchase invoice line items."""
    
    unit = forms.ChoiceField(
        label=_('Unit'),
        choices=UNIT_CHOICES,
    )
    
    class Meta:
        model = PurchaseInvoiceLine
        fields = [
            'item',
            'unit',
            'quantity',
            'unit_price',
            'line_notes',
        ]
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.001'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
            'line_notes': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'item': _('Item'),
            'unit': _('Unit'),
            'quantity': _('Quantity'),
            'unit_price': _('Unit Price'),
            'line_notes': _('Notes'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        if self.company_id:
            if 'item' in self.fields:
                # Filter items by company
                base_queryset = Item.objects.filter(
                    company_id=self.company_id, is_enabled=1
                )
                
                # If editing and instance has an item, include it even if disabled
                if self.instance and self.instance.pk and hasattr(self.instance, 'item_id') and self.instance.item_id:
                    instance_item_id = self.instance.item_id
                    self.fields['item'].queryset = Item.objects.filter(
                        Q(company_id=self.company_id, is_enabled=1) | Q(pk=instance_item_id)
                    ).order_by('name')
                else:
                    self.fields['item'].queryset = base_queryset.order_by('name')
                
                self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        
        # Set unit choices if instance has a unit
        if not self.is_bound and self.instance and self.instance.pk:
            if 'unit' in self.fields and getattr(self.instance, 'unit', None):
                unit_value = self.instance.unit
                unit_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in unit_choices]
                if unit_value not in unit_codes:
                    self.fields['unit'].choices = unit_choices + [(unit_value, unit_value)]
                self.initial['unit'] = unit_value
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Auto-calculate line_total if quantity and unit_price are provided
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity and unit_price:
            # line_total will be calculated in model.save()
            pass
        
        return cleaned_data


# Create formset
PurchaseInvoiceLineFormSet = inlineformset_factory(
    PurchaseInvoice,
    PurchaseInvoiceLine,
    form=PurchaseInvoiceLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


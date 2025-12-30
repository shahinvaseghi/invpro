"""
Forms for Purchase Order.
"""
from typing import Optional, Any
from django import forms
from django.forms import inlineformset_factory
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from procurement.models import PurchaseOrder, PurchaseOrderLine
from inventory.models import Item, Supplier
from inventory.forms.base import UNIT_CHOICES, BaseLineFormSet
from inventory.widgets import JalaliDateInput
from shared.forms.base import BaseModelForm


class PurchaseOrderForm(BaseModelForm):
    """Form for purchase order header."""
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier',
            'purchase_request',
            'order_date',
            'expected_delivery_date',
            'delivery_address',
            'payment_terms',
            'notes',
        ]
        widgets = {
            'order_date': JalaliDateInput(),
            'expected_delivery_date': JalaliDateInput(),
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'payment_terms': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'supplier': _('Supplier'),
            'purchase_request': _('Purchase Request'),
            'order_date': _('Order Date'),
            'expected_delivery_date': _('Expected Delivery Date'),
            'delivery_address': _('Delivery Address'),
            'payment_terms': _('Payment Terms'),
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
            
            # Filter purchase requests by company
            if 'purchase_request' in self.fields:
                from inventory.models import PurchaseRequest
                self.fields['purchase_request'].queryset = PurchaseRequest.objects.filter(
                    company_id=company_id
                ).order_by('-request_date', '-request_code')
                self.fields['purchase_request'].empty_label = _("--- انتخاب کنید ---")
                self.fields['purchase_request'].required = False
        
        # Set default order_date
        if not self.instance.pk and 'order_date' in self.fields:
            self.fields['order_date'].initial = timezone.now().date()


class PurchaseOrderLineForm(forms.ModelForm):
    """Form for purchase order line items."""
    
    unit = forms.ChoiceField(
        label=_('Unit'),
        choices=UNIT_CHOICES,
    )
    
    class Meta:
        model = PurchaseOrderLine
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
        
        # Auto-calculate total_amount if quantity and unit_price are provided
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity and unit_price:
            # total_amount will be calculated in model.save()
            pass
        
        return cleaned_data


# Create formset
PurchaseOrderLineFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderLine,
    form=PurchaseOrderLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


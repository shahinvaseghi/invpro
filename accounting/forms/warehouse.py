"""
Forms for warehouse accounting.
"""
from decimal import Decimal
from typing import Optional
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from ..models.warehouse import WarehouseExpenseDocument, WarehouseExpenseDocumentLine
from shared.forms.base import BaseModelForm


class WarehouseExpenseDocumentForm(BaseModelForm):
    """Form for creating/editing warehouse expense documents."""
    
    class Meta:
        model = WarehouseExpenseDocument
        fields = [
            'document_date',
            'receipt_type',
            'receipt_id',
            'receipt_code',
            'total_amount',
            'status',
            'description',
        ]
        widgets = {
            'document_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'receipt_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_receipt_type'}),
            'receipt_id': forms.Select(attrs={'class': 'form-control', 'id': 'id_receipt_id'}),
            'receipt_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'id': 'id_receipt_code'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.receipt = kwargs.pop('receipt', None)
        super().__init__(*args, **kwargs)
        
        # Make receipt_id a Select field with empty choices initially
        self.fields['receipt_id'].widget = forms.Select(attrs={'class': 'form-control', 'id': 'id_receipt_id'})
        self.fields['receipt_id'].choices = [('', '--- انتخاب کنید ---')]
        self.fields['receipt_id'].required = True
        
        # If receipt is provided, pre-fill fields
        if self.receipt:
            if not self.instance.pk:
                # Set receipt info for new documents
                if hasattr(self.receipt, 'document_code'):
                    self.fields['receipt_code'].initial = self.receipt.document_code
                    self.fields['receipt_id'].initial = self.receipt.pk
                    self.fields['receipt_id'].choices = [
                        ('', '--- انتخاب کنید ---'),
                        (self.receipt.pk, self.receipt.document_code)
                    ]
                    
                    # Determine receipt type
                    receipt_class = self.receipt.__class__.__name__
                    if 'Permanent' in receipt_class:
                        self.fields['receipt_type'].initial = 'PERMANENT'
                    elif 'Temporary' in receipt_class:
                        self.fields['receipt_type'].initial = 'TEMPORARY'
                    elif 'Consignment' in receipt_class:
                        self.fields['receipt_type'].initial = 'CONSIGNMENT'


def get_unit_conversion_factor(item, from_unit: str, to_unit: str) -> Optional[Decimal]:
    """
    Get conversion factor to convert from from_unit to to_unit.
    
    Returns:
        Conversion factor (Decimal) or None if no conversion found.
        If factor is 2.5, it means 1 from_unit = 2.5 to_unit
    """
    from inventory.models import ItemUnit
    
    if from_unit == to_unit:
        return Decimal('1.0')
    
    # Try direct conversion: from_unit -> to_unit
    conversion = ItemUnit.objects.filter(
        item=item,
        company_id=item.company_id,
        from_unit=from_unit,
        to_unit=to_unit,
        is_enabled=1,
    ).first()
    
    if conversion:
        # from_quantity from_unit = to_quantity to_unit
        # So: 1 from_unit = (to_quantity / from_quantity) to_unit
        if conversion.from_quantity > 0:
            return conversion.to_quantity / conversion.from_quantity
    
    # Try reverse conversion: to_unit -> from_unit
    reverse_conversion = ItemUnit.objects.filter(
        item=item,
        company_id=item.company_id,
        from_unit=to_unit,
        to_unit=from_unit,
        is_enabled=1,
    ).first()
    
    if reverse_conversion:
        # to_quantity to_unit = from_quantity from_unit
        # So: 1 from_unit = (to_quantity / from_quantity) to_unit
        # But we need reverse: 1 to_unit = (from_quantity / to_quantity) from_unit
        if reverse_conversion.to_quantity > 0:
            return reverse_conversion.from_quantity / reverse_conversion.to_quantity
    
    return None


def convert_unit_price(unit_price: Decimal, item, from_unit: str, to_unit: str) -> Optional[Decimal]:
    """
    Convert unit price from from_unit to to_unit.
    
    Args:
        unit_price: Price per from_unit
        item: Item object
        from_unit: Source unit
        to_unit: Target unit
    
    Returns:
        Converted price per to_unit, or None if conversion not found
    """
    if from_unit == to_unit:
        return unit_price
    
    factor = get_unit_conversion_factor(item, from_unit, to_unit)
    if factor is None:
        return None
    
    # If 1 from_unit = factor to_unit, then:
    # price_per_from_unit * factor = price_per_to_unit
    return unit_price * factor


class WarehouseExpenseDocumentLineForm(BaseModelForm):
    """Form for warehouse expense document line."""
    
    class Meta:
        model = WarehouseExpenseDocumentLine
        fields = [
            'item',
            'item_code',
            'warehouse',
            'warehouse_code',
            'unit',
            'quantity',
            'unit_price',
            'base_unit',
            'base_unit_price',
            'total_price',
            'line_notes',
        ]
        widgets = {
            'item': forms.HiddenInput(),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'warehouse': forms.HiddenInput(),
            'warehouse_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'step': '0.000001'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'base_unit': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'base_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'step': '0.01'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'step': '0.01'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'item_code': _('کد کالا'),
            'warehouse_code': _('کد انبار'),
            'unit': _('واحد'),
            'quantity': _('مقدار'),
            'unit_price': _('قیمت واحد'),
            'base_unit': _('واحد اصلی'),
            'base_unit_price': _('قیمت واحد اصلی'),
            'total_price': _('قیمت کل'),
            'line_notes': _('توضیحات'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make unit_price required
        self.fields['unit_price'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        unit_price = cleaned_data.get('unit_price')
        quantity = cleaned_data.get('quantity')
        item = cleaned_data.get('item')
        unit = cleaned_data.get('unit')
        
        if unit_price and quantity and item:
            # Calculate total price
            cleaned_data['total_price'] = unit_price * quantity
            
            # Convert unit_price to base_unit_price
            base_unit = item.default_unit
            cleaned_data['base_unit'] = base_unit
            
            if unit != base_unit:
                # Convert price from unit to base_unit
                converted_price = convert_unit_price(unit_price, item, unit, base_unit)
                if converted_price is not None:
                    cleaned_data['base_unit_price'] = converted_price
                else:
                    # If no conversion found, use same price
                    cleaned_data['base_unit_price'] = unit_price
            else:
                cleaned_data['base_unit_price'] = unit_price
        
        return cleaned_data


WarehouseExpenseDocumentLineFormSet = inlineformset_factory(
    WarehouseExpenseDocument,
    WarehouseExpenseDocumentLine,
    form=WarehouseExpenseDocumentLineForm,
    extra=0,
    can_delete=False,
    min_num=1,
    validate_min=True,
)


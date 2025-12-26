"""
Forms for sales module.
"""
from decimal import Decimal
from typing import Optional

from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, BaseFormSet
from django.utils.translation import gettext_lazy as _

from shared.forms.base import BaseModelForm

from .models import ItemPriceCard


class ItemPriceCardForm(BaseModelForm):
    """Form for creating/editing item price card."""
    
    # Filter fields for item selection
    item_type_filter = forms.ChoiceField(
        required=False,
        label=_('Item Type'),
        widget=forms.Select(attrs={'class': 'form-control item-type-filter'}),
    )
    item_category_filter = forms.ChoiceField(
        required=False,
        label=_('Item Category'),
        widget=forms.Select(attrs={'class': 'form-control item-category-filter'}),
    )
    item_subcategory_filter = forms.ChoiceField(
        required=False,
        label=_('Item Subcategory'),
        widget=forms.Select(attrs={'class': 'form-control item-subcategory-filter'}),
    )
    
    class Meta:
        model = ItemPriceCard
        fields = [
            'item',
            'price',
            'currency',
            'effective_date',
            'expiry_date',
            'notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control item-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0'
            }),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'effective_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'item': _('Item'),
            'price': _('Price'),
            'currency': _('Currency'),
            'effective_date': _('Effective Date'),
            'expiry_date': _('Expiry Date'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if self.company_id:
            from inventory.models import Item, ItemType, ItemCategory, ItemSubcategory
            
            # Filter items: only sellable items (is_sellable=1)
            items_qs = Item.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
                is_sellable=1  # Only sellable items
            ).select_related('type', 'category', 'subcategory').order_by('item_code')
            
            self.fields['item'].queryset = items_qs
            
            # Populate filter choices
            types = ItemType.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item_type_filter'].choices = [('', '--------')] + [(t.id, t.name) for t in types]
            
            categories = ItemCategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item_category_filter'].choices = [('', '--------')] + [(c.id, c.name) for c in categories]
            
            subcategories = ItemSubcategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item_subcategory_filter'].choices = [('', '--------')] + [(s.id, s.name) for s in subcategories]
            
            # Set label_from_instance for better display
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        else:
            from inventory.models import Item
            self.fields['item'].queryset = Item.objects.none()
            self.fields['item_type_filter'].choices = [('', '--------')]
            self.fields['item_category_filter'].choices = [('', '--------')]
            self.fields['item_subcategory_filter'].choices = [('', '--------')]
    
    def clean_price(self):
        """Validate price is positive."""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError(_('Price must be positive.'))
        return price
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        
        # Check if item already has a price card for this company
        if item and self.company_id:
            existing = ItemPriceCard.objects.filter(
                company_id=self.company_id,
                item=item
            )
            # Exclude current instance if editing
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError({
                    'item': _('This item already has a price card. Please update the existing one instead.')
                })
        
        return cleaned_data


class ItemPriceCardFormSetBase(BaseFormSet):
    """Base formset class for handling company_id in price card forms."""
    
    def __init__(self, *args, company_id=None, **kwargs):
        """Initialize formset and pass company_id to all forms."""
        self.company_id = company_id
        super().__init__(*args, **kwargs)
        
        # Pass company_id to all forms
        for form in self.forms:
            if hasattr(form, '__init__'):
                # Re-initialize form with company_id
                form.company_id = company_id
                # Update querysets if company_id is set
                if company_id and hasattr(form, 'fields'):
                    from inventory.models import Item, ItemType, ItemCategory, ItemSubcategory
                    
                    # Filter items: only sellable items
                    items_qs = Item.objects.filter(
                        company_id=company_id,
                        is_enabled=1,
                        is_sellable=1
                    ).select_related('type', 'category', 'subcategory').order_by('item_code')
                    
                    if 'item' in form.fields:
                        form.fields['item'].queryset = items_qs
                        form.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
                    
                    # Update filter choices
                    if 'item_type_filter' in form.fields:
                        types = ItemType.objects.filter(company_id=company_id, is_enabled=1)
                        form.fields['item_type_filter'].choices = [('', '--------')] + [(t.id, t.name) for t in types]
                    
                    if 'item_category_filter' in form.fields:
                        categories = ItemCategory.objects.filter(company_id=company_id, is_enabled=1)
                        form.fields['item_category_filter'].choices = [('', '--------')] + [(c.id, c.name) for c in categories]
                    
                    if 'item_subcategory_filter' in form.fields:
                        subcategories = ItemSubcategory.objects.filter(company_id=company_id, is_enabled=1)
                        form.fields['item_subcategory_filter'].choices = [('', '--------')] + [(s.id, s.name) for s in subcategories]


# Formset for creating multiple price cards at once
ItemPriceCardFormSet = modelformset_factory(
    ItemPriceCard,
    form=ItemPriceCardForm,
    formset=ItemPriceCardFormSetBase,
    extra=1,  # Show 1 empty form initially
    can_delete=True,
    min_num=1,
    validate_min=True,
)


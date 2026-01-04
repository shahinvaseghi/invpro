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
from accounting.models import Party, Account
from accounting.forms import PartyForm
from .models import ItemPriceCard, SalesSettings


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
            'item': forms.Select(attrs={'class': 'form-control item-select'}, choices=[('', '--- انتخاب کنید ---')]),
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
            
            # Set queryset to all sellable items for validation
            # JavaScript will still populate the dropdown via API, but Django can validate the selected value
            self.fields['item'].queryset = Item.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
                is_sellable=1
            )
            
            # Populate filter choices
            types = ItemType.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item_type_filter'].choices = [('', '--------')] + [(t.id, t.name) for t in types]
            
            categories = ItemCategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item_category_filter'].choices = [('', '--------')] + [(c.id, c.name) for c in categories]
            
            subcategories = ItemSubcategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item_subcategory_filter'].choices = [('', '--------')] + [(s.id, s.name) for s in subcategories]
        else:
            from inventory.models import Item
            self.fields['item'].queryset = Item.objects.none()
            self.fields['item_type_filter'].choices = [('', '--------')]
            self.fields['item_category_filter'].choices = [('', '--------')]
            self.fields['item_subcategory_filter'].choices = [('', '--------')]
        
        # Ensure the item field widget doesn't show all options initially
        # JavaScript will populate it dynamically
        if 'item' in self.fields:
            self.fields['item'].widget.attrs['data-dynamic'] = 'true'
    
    def clean_price(self):
        """Validate price is positive."""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError(_('Price must be positive.'))
        return price
    
    def clean_item(self):
        """Validate that the selected item is valid and belongs to the company."""
        item = self.cleaned_data.get('item')
        
        if not item:
            return item
        
        # Handle case where item might be an ID (string or int) instead of object
        item_id = None
        if hasattr(item, 'pk'):
            item_id = item.pk
        elif isinstance(item, (int, str)):
            item_id = int(item) if str(item).isdigit() else None
        
        # Validate that item exists and belongs to the company
        if self.company_id:
            from inventory.models import Item
            try:
                if item_id:
                    item_obj = Item.objects.get(pk=item_id, company_id=self.company_id, is_enabled=1)
                else:
                    item_obj = Item.objects.get(pk=item.pk, company_id=self.company_id, is_enabled=1)
                
                # Also check if item is sellable
                if not item_obj.is_sellable:
                    raise ValidationError(_('Selected item is not sellable.'))
                
                return item_obj
            except Item.DoesNotExist:
                raise ValidationError(_('Please select a valid option. That option is not among the available options.'))
            except (ValueError, TypeError) as e:
                raise ValidationError(_('Please select a valid option. That option is not among the available options.'))
        
        return item
    
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
                    
                    # Set queryset to all sellable items for validation
                    # JavaScript will still populate the dropdown via API, but Django can validate the selected value
                    if 'item' in form.fields:
                        form.fields['item'].queryset = Item.objects.filter(
                            company_id=company_id,
                            is_enabled=1,
                            is_sellable=1
                        )
                    
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
    
    def get_extra(self):
        """Return extra count - always return 1 for create mode to show only one initial row."""
        # In create mode (no instance), return 1 to show only one empty form
        # User can add more rows using the "Add Price Card" button
        if not hasattr(self, 'instance') or self.instance is None:
            return 1
        # For update mode, use default extra
        return super().get_extra()
    
    def get_min_num(self):
        """Return min_num - return 0 in create mode to prevent extra forms."""
        # In create mode, return 0 so Django doesn't create min_num + extra forms
        # We only want 'extra' forms (which is 1) in create mode
        if not hasattr(self, 'instance') or self.instance is None:
            return 0
        # For update mode, use default min_num
        return super().get_min_num()


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


class SalesSettingsForm(BaseModelForm):
    """Form for sales settings."""
    
    class Meta:
        model = SalesSettings
        fields = [
            # TafsiliHierarchy fields removed
        ]
        widgets = {
            'customer_tafsili_level': forms.Select(attrs={
                'class': 'form-control',
            }),
            'bank_tafsili_level': forms.Select(attrs={
                'class': 'form-control',
            }),
            'check_tafsili_level': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'customer_tafsili_level': _('سطح تفصیلی مشتری‌ها'),
            'bank_tafsili_level': _('سطح تفصیلی بانک‌ها'),
            'check_tafsili_level': _('سطح تفصیلی چک‌ها'),
        }
        help_texts = {
            'customer_tafsili_level': _('سطح تفصیلی که برای مشتری‌ها استفاده می‌شود'),
            'bank_tafsili_level': _('سطح تفصیلی که برای بانک‌ها استفاده می‌شود'),
            'check_tafsili_level': _('سطح تفصیلی که برای چک‌ها استفاده می‌شود'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with tafsili level choices."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id

        # Set choices for tafsili level fields
        tafsili_choices = [(1, _('سطح 1')), (2, _('سطح 2')), (3, _('سطح 3'))]

        # Set choices for all three fields
        self.fields['customer_tafsili_level'].choices = tafsili_choices
        self.fields['bank_tafsili_level'].choices = tafsili_choices
        self.fields['check_tafsili_level'].choices = tafsili_choices

        # Add empty option
        self.fields['customer_tafsili_level'].choices = [('', _('انتخاب کنید...'))] + tafsili_choices
        self.fields['bank_tafsili_level'].choices = [('', _('انتخاب کنید...'))] + tafsili_choices
        self.fields['check_tafsili_level'].choices = [('', _('انتخاب کنید...'))] + tafsili_choices
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()

        # No additional validation needed for simple choice fields

        return cleaned_data


class CustomerForm(PartyForm):
    """Form for creating/editing customers."""
    
    class Meta(PartyForm.Meta):
        pass
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, company_id=company_id, **kwargs)
        
        # Set party_type to customer for new instances
        if not self.instance.pk:
            self.initial['party_type'] = 'customer'
            self.fields['party_type'].widget = forms.HiddenInput()
        
        # Tafsili level choices are already set as simple choice field


class IncomeReceiptLocationForm(BaseModelForm):
    """Form for creating/editing income receipt locations."""
    
    class Meta:
        from .models import IncomeReceiptLocation
        model = IncomeReceiptLocation
        fields = [
            'treasury_account',
            'receipt_method',
            'location_name',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'treasury_account': forms.Select(attrs={'class': 'form-control'}),
            'receipt_method': forms.Select(attrs={'class': 'form-control'}),
            'location_name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'treasury_account': _('حساب نقدی/بانکی'),
            'receipt_method': _('روش دریافت'),
            'location_name': _('نام محل دریافت درآمد'),
            'notes': _('توضیحات'),
            'is_enabled': _('فعال'),
        }
        help_texts = {
            'treasury_account': _('حساب نقدی یا بانکی که از ماژول حسابداری خوانده می‌شود'),
            'receipt_method': _('روش دریافت درآمد (پوز، نقد، حساب، چک، پایا، ساتنا، پل یا چند مورد با هم)'),
            'location_name': _('نام محل دریافت درآمد'),
            'notes': _('توضیحات و یادداشت‌ها'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if company_id:
            from accounting.models import TreasuryAccount
            
            # Filter treasury accounts by company and active status
            self.fields['treasury_account'].queryset = TreasuryAccount.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).order_by('account_type', 'account_name')
            
            self.fields['treasury_account'].empty_label = _("--- انتخاب کنید ---")
            self.fields['treasury_account'].label_from_instance = lambda obj: f"{obj.get_account_type_display()} - {obj.account_name}"
        else:
            from accounting.models import TreasuryAccount
            self.fields['treasury_account'].queryset = TreasuryAccount.objects.none()

"""
BOM (Bill of Materials) forms for production module.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _

from inventory.models import ItemType, ItemCategory, ItemSubcategory
from production.models import BOM, BOMMaterial


class BOMForm(forms.ModelForm):
    """Form for creating/editing BOM Header (Finished Product)."""
    
    # Cascading filters for Item selection (not saved to DB)
    item_type = forms.ModelChoiceField(
        queryset=ItemType.objects.none(),
        required=False,
        label=_('Item Type'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_item_type'}),
    )
    item_category = forms.ModelChoiceField(
        queryset=ItemCategory.objects.none(),
        required=False,
        label=_('Category'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_item_category'}),
    )
    item_subcategory = forms.ModelChoiceField(
        queryset=ItemSubcategory.objects.none(),
        required=False,
        label=_('Subcategory'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_item_subcategory'}),
    )
    
    class Meta:
        model = BOM
        fields = [
            'finished_item',
            'version',
            'is_active',
            'description',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'finished_item': forms.Select(attrs={'class': 'form-control', 'id': 'id_finished_item'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'finished_item': _('Finished Product'),
            'version': _('Version'),
            'is_active': _('Active'),
            'description': _('Description'),
            'notes': _('Notes'),
            'is_enabled': _('Status'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        # Set default is_enabled if not provided (for new BOMs)
        if not self.instance.pk and 'is_enabled' in self.fields:
            self.fields['is_enabled'].initial = 1

        from inventory.models import Item, ItemType, ItemCategory, ItemSubcategory
        
        if self.company_id:
            # Populate type queryset
            self.fields['item_type'].queryset = ItemType.objects.filter(
                company_id=self.company_id, 
                is_enabled=1
            ).order_by('name')
            
            # Populate category queryset (will be filtered by JS)
            self.fields['item_category'].queryset = ItemCategory.objects.filter(
                company_id=self.company_id, 
                is_enabled=1
            ).order_by('name')
            
            # Populate subcategory queryset (will be filtered by JS)
            self.fields['item_subcategory'].queryset = ItemSubcategory.objects.filter(
                company_id=self.company_id, 
                is_enabled=1
            ).order_by('name')
            
            # Filter items by company
            items_qs = Item.objects.filter(company_id=self.company_id, is_enabled=1).order_by('item_code')
            self.fields['finished_item'].queryset = items_qs
            
            # On edit: populate filter fields from existing instance
            if self.instance.pk and self.instance.finished_item:
                self.fields['item_type'].initial = self.instance.finished_item.type
                self.fields['item_category'].initial = self.instance.finished_item.category
                self.fields['item_subcategory'].initial = self.instance.finished_item.subcategory
        else:
            self.fields['item_type'].queryset = ItemType.objects.none()
            self.fields['item_category'].queryset = ItemCategory.objects.none()
            self.fields['item_subcategory'].queryset = ItemSubcategory.objects.none()
            self.fields['finished_item'].queryset = Item.objects.none()


class BOMMaterialLineForm(forms.ModelForm):
    """Form for BOM Material Line (used in formset)."""
    
    # Cascading filters for Material selection
    material_category_filter = forms.ChoiceField(
        required=False,
        label=_('Material Category'),
        widget=forms.Select(attrs={'class': 'form-control material-category-filter'}),
    )
    material_subcategory_filter = forms.ChoiceField(
        required=False,
        label=_('Material Subcategory'),
        widget=forms.Select(attrs={'class': 'form-control material-subcategory-filter'}),
    )
    
    unit = forms.CharField(
        max_length=30,
        required=False,  # Will be validated in clean() if material_item is selected
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control material-unit'}),
    )
    
    # Override is_optional to use BooleanField (checkbox) instead of IntegerField
    # We'll convert it to integer (0/1) in clean_is_optional and save
    is_optional = forms.BooleanField(
        required=False,
        label=_('Optional'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=False,
    )
    
    class Meta:
        model = BOMMaterial
        fields = [
            'material_type',
            'material_item',
            'quantity_per_unit',
            'unit',
            'scrap_allowance',
            'is_optional',
            'description',
        ]
        widgets = {
            'material_type': forms.Select(attrs={'class': 'form-control material-type'}),
            'material_item': forms.Select(attrs={'class': 'form-control material-item'}),
            'quantity_per_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0'
            }),
            'scrap_allowance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            # is_optional is defined explicitly above, so don't include it here
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'material_type': _('Material Type'),
            'material_item': _('Material/Component'),
            'quantity_per_unit': _('Quantity'),
            'unit': _('Unit'),
            'scrap_allowance': _('Scrap %'),
            'is_optional': _('Optional'),
            'description': _('Description'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id

        if self.company_id:
            from inventory.models import Item, ItemType, ItemCategory, ItemSubcategory, ItemUnit
            
            # Filter material type by company
            self.fields['material_type'].queryset = ItemType.objects.filter(
                company_id=self.company_id, 
                is_enabled=1
            ).order_by('name')
            
            # Populate category filter choices
            categories = ItemCategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['material_category_filter'].choices = [('', '--------')] + [(c.id, c.name) for c in categories]
            
            # Populate subcategory filter choices
            subcategories = ItemSubcategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['material_subcategory_filter'].choices = [('', '--------')] + [(s.id, s.name) for s in subcategories]
            
            # Filter items by company
            items_qs = Item.objects.filter(company_id=self.company_id, is_enabled=1).select_related('type', 'category', 'subcategory').order_by('item_code')
            self.fields['material_item'].queryset = items_qs
            
            # Add custom widget to include data attributes
            self.fields['material_item'].widget.attrs.update({'class': 'form-control material-item'})
        else:
            from inventory.models import Item, ItemType, ItemUnit
            self.fields['material_type'].queryset = ItemType.objects.none()
            self.fields['material_category_filter'].choices = [('', '--------')]
            self.fields['material_subcategory_filter'].choices = [('', '--------')]
            self.fields['material_item'].queryset = Item.objects.none()
    
    def clean_is_optional(self) -> int:
        """Convert Boolean checkbox value to integer (0 or 1) for database storage."""
        value = self.cleaned_data.get('is_optional')
        
        # BooleanField returns True/False, convert to 1/0
        if value is True:
            result = 1
        else:
            result = 0
        
        return result
    
    def clean(self) -> dict:
        """Clean form data and remove filter fields from cleaned_data."""
        cleaned_data = super().clean()
        
        # Remove filter fields from cleaned_data (they're not saved to DB)
        # These are UI-only fields for cascading dropdowns
        if 'material_category_filter' in cleaned_data:
            del cleaned_data['material_category_filter']
        if 'material_subcategory_filter' in cleaned_data:
            del cleaned_data['material_subcategory_filter']
        
        # If material_item is selected, unit is required
        material_item = cleaned_data.get('material_item')
        unit = cleaned_data.get('unit')
        material_type = cleaned_data.get('material_type')
        
        # Auto-set material_type from material_item if not provided
        if material_item and not material_type:
            try:
                from inventory.models import Item
                # material_item might be an Item instance or an ID
                if hasattr(material_item, 'pk'):
                    item = material_item
                elif hasattr(material_item, 'id'):
                    item = Item.objects.get(pk=material_item.id, company_id=self.company_id)
                else:
                    item = Item.objects.get(pk=material_item, company_id=self.company_id)
                
                if item.type:
                    cleaned_data['material_type'] = item.type
            except Exception:
                pass
        
        if material_item and not unit:
            self.add_error('unit', _('Please select a unit for the selected material.'))
        
        # Ensure is_optional is set (should already be set by clean_is_optional, but just in case)
        if 'is_optional' not in cleaned_data or cleaned_data.get('is_optional') is None:
            cleaned_data['is_optional'] = 0
        
        # If no material_item, don't require other fields (empty form)
        if not material_item:
            # Clear required fields for empty forms
            for field in ['material_type', 'quantity_per_unit', 'unit']:
                if field in cleaned_data and not cleaned_data[field]:
                    cleaned_data[field] = None
        
        return cleaned_data
    
    def full_clean(self) -> None:
        """Override to exclude filter fields from validation."""
        # Temporarily remove filter fields from self.fields for validation
        filter_fields = ['material_category_filter', 'material_subcategory_filter']
        saved_fields = {}
        for field_name in filter_fields:
            if field_name in self.fields:
                saved_fields[field_name] = self.fields[field_name]
                del self.fields[field_name]
        
        try:
            super().full_clean()
        finally:
            # Restore filter fields after validation
            self.fields.update(saved_fields)


# Custom Formset for BOM Materials
class BOMMaterialLineFormSetBase(forms.BaseInlineFormSet):
    """Custom formset with better validation for BOM materials."""
    
    def clean(self) -> None:
        """Validate that at least one complete material line exists."""
        if any(self.errors):
            return
        
        # Count non-empty forms (forms with material_item selected)
        non_empty_forms = 0
        for form in self.forms:
            # Check if form has cleaned_data (validation passed)
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                # Check if form is not marked for deletion
                if not form.cleaned_data.get('DELETE', False):
                    material_item = form.cleaned_data.get('material_item')
                    if material_item:
                        non_empty_forms += 1
        
        if non_empty_forms == 0:
            raise forms.ValidationError(
                _('At least one material line with a selected material is required.')
            )


# Create the formset factory
BOMMaterialLineFormSet = forms.inlineformset_factory(
    BOM,
    BOMMaterial,
    form=BOMMaterialLineForm,
    formset=BOMMaterialLineFormSetBase,
    extra=1,  # Start with 1 empty line
    can_delete=True,
    min_num=0,  # We handle minimum validation in clean()
    validate_min=False,  # We handle minimum validation in clean()
)


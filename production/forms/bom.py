"""
BOM (Bill of Materials) forms for production module.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _

from inventory.models import ItemType, ItemCategory, ItemSubcategory
from production.models import BOM, BOMMaterial, BOMMaterialAlternative


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
            'description',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'finished_item': forms.Select(attrs={'class': 'form-control', 'id': 'id_finished_item'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'finished_item': _('Finished Product'),
            'version': _('Version'),
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
            'source_warehouses',
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
            'source_warehouses': forms.HiddenInput(),  # Will be populated via JavaScript
            # is_optional is defined explicitly above, so don't include it here
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'material_type': _('Material Type'),
            'material_item': _('Material/Component'),
            'quantity_per_unit': _('Quantity'),
            'unit': _('Unit'),
            'scrap_allowance': _('Scrap %'),
            'source_warehouses': _('Source Warehouses'),
            'is_optional': _('Optional'),
            'description': _('Description'),
        }
        help_texts = {
            'source_warehouses': _('Select up to 5 source warehouses with priorities'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id

        if self.company_id:
            from inventory.models import Item, ItemType, ItemCategory, ItemSubcategory, ItemUnit, Warehouse
            
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


class BOMMaterialAlternativeForm(forms.ModelForm):
    """Form for BOM Material Alternative Item (used in formset)."""
    
    # Cascading filters for Alternative Item selection
    alternative_category_filter = forms.ChoiceField(
        required=False,
        label=_('Category'),
        widget=forms.Select(attrs={'class': 'form-control alternative-category-filter'}),
    )
    alternative_subcategory_filter = forms.ChoiceField(
        required=False,
        label=_('Subcategory'),
        widget=forms.Select(attrs={'class': 'form-control alternative-subcategory-filter'}),
    )
    
    unit = forms.CharField(
        max_length=50,
        required=False,  # Will be validated in clean() if alternative_item is selected
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control alternative-unit'}),
    )
    
    class Meta:
        model = BOMMaterialAlternative
        fields = [
            'alternative_item',
            'quantity',
            'unit',
            'priority',
            'source_warehouses',
            'description',
        ]
        widgets = {
            'alternative_item': forms.Select(attrs={'class': 'form-control alternative-item'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'min': '0'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
            'source_warehouses': forms.HiddenInput(),  # Will be populated via JavaScript
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'alternative_item': _('Alternative Item'),
            'quantity': _('Quantity'),
            'unit': _('Unit'),
            'priority': _('Priority'),
            'source_warehouses': _('Source Warehouses'),
            'description': _('Description'),
        }
        help_texts = {
            'source_warehouses': _('Select 1 to 5 source warehouses with priorities'),
            'priority': _('Priority order (1 = highest, must be unique)'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, bom_material_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id
        self.bom_material_id: Optional[int] = bom_material_id

        if self.company_id:
            from inventory.models import Item, ItemCategory, ItemSubcategory, ItemUnit
            
            # Populate category filter choices
            categories = ItemCategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['alternative_category_filter'].choices = [('', '--------')] + [(c.id, c.name) for c in categories]
            
            # Populate subcategory filter choices
            subcategories = ItemSubcategory.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['alternative_subcategory_filter'].choices = [('', '--------')] + [(s.id, s.name) for s in subcategories]
            
            # Filter items by company
            items_qs = Item.objects.filter(company_id=self.company_id, is_enabled=1).select_related('type', 'category', 'subcategory').order_by('item_code')
            self.fields['alternative_item'].queryset = items_qs
            
            # Add custom widget to include data attributes
            self.fields['alternative_item'].widget.attrs.update({'class': 'form-control alternative-item'})
        else:
            from inventory.models import Item
            self.fields['alternative_category_filter'].choices = [('', '--------')]
            self.fields['alternative_subcategory_filter'].choices = [('', '--------')]
            self.fields['alternative_item'].queryset = Item.objects.none()
    
    def clean(self) -> dict:
        """Clean form data and validate."""
        cleaned_data = super().clean()
        
        # Remove filter fields from cleaned_data (they're not saved to DB)
        if 'alternative_category_filter' in cleaned_data:
            del cleaned_data['alternative_category_filter']
        if 'alternative_subcategory_filter' in cleaned_data:
            del cleaned_data['alternative_subcategory_filter']
        
        # If alternative_item is selected, unit is required
        alternative_item = cleaned_data.get('alternative_item')
        unit = cleaned_data.get('unit')
        priority = cleaned_data.get('priority')
        
        if alternative_item and not unit:
            self.add_error('unit', _('Please select a unit for the selected alternative item.'))
        
        # Validate unit belongs to alternative item's allowed units
        if alternative_item and unit:
            from inventory.models import ItemUnit
            # Get all units for this item (from_unit and to_unit)
            item_units = ItemUnit.objects.filter(
                item=alternative_item,
                company_id=self.company_id,
                is_enabled=1
            )
            allowed_units = set()
            for item_unit in item_units:
                allowed_units.add(item_unit.from_unit)
                allowed_units.add(item_unit.to_unit)
            # Also add primary unit
            if alternative_item.primary_unit:
                allowed_units.add(alternative_item.primary_unit)
            if alternative_item.default_unit:
                allowed_units.add(alternative_item.default_unit)
            
            if unit not in allowed_units:
                self.add_error('unit', _('Selected unit is not valid for this alternative item.'))
        
        # Validate priority is between 1 and 10
        if priority is not None:
            if priority < 1 or priority > 10:
                self.add_error('priority', _('Priority must be between 1 and 10.'))
        
        # Validate source_warehouses (1-5 warehouses)
        source_warehouses = cleaned_data.get('source_warehouses', [])
        if isinstance(source_warehouses, list):
            if len(source_warehouses) > 5:
                self.add_error('source_warehouses', _('Maximum 5 source warehouses allowed.'))
            elif len(source_warehouses) > 0 and alternative_item:
                # Validate warehouses belong to alternative item's allowed warehouses
                from inventory.models import ItemWarehouse
                allowed_warehouse_ids = set(
                    ItemWarehouse.objects.filter(
                        item=alternative_item,
                        company_id=self.company_id,
                        is_enabled=1
                    ).values_list('warehouse_id', flat=True)
                )
                for wh in source_warehouses:
                    if isinstance(wh, dict) and 'warehouse_id' in wh:
                        if wh['warehouse_id'] not in allowed_warehouse_ids:
                            self.add_error('source_warehouses', _('One or more selected warehouses are not valid for this alternative item.'))
        
        # If no alternative_item, don't require other fields (empty form)
        if not alternative_item:
            for field in ['quantity', 'unit', 'priority']:
                if field in cleaned_data and not cleaned_data[field]:
                    cleaned_data[field] = None
        
        return cleaned_data
    
    def full_clean(self) -> None:
        """Override to exclude filter fields from validation."""
        # Temporarily remove filter fields from self.fields for validation
        filter_fields = ['alternative_category_filter', 'alternative_subcategory_filter']
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


# Custom Formset for BOM Material Alternatives
class BOMMaterialAlternativeFormSetBase(forms.BaseInlineFormSet):
    """Custom formset with validation for BOM material alternatives."""
    
    def clean(self) -> None:
        """Validate alternatives: max 10, unique priorities, unique items."""
        if any(self.errors):
            return
        
        # Get all non-deleted forms with alternative_item
        alternatives = []
        priorities = set()
        items = set()
        
        for form in self.forms:
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                if not form.cleaned_data.get('DELETE', False):
                    alternative_item = form.cleaned_data.get('alternative_item')
                    priority = form.cleaned_data.get('priority')
                    
                    if alternative_item:
                        alternatives.append(form)
                        
                        # Check for duplicate priorities
                        if priority in priorities:
                            raise forms.ValidationError(
                                _('Priority values must be unique. Duplicate priority: %(priority)s') % {'priority': priority}
                            )
                        priorities.add(priority)
                        
                        # Check for duplicate items
                        if alternative_item in items:
                            raise forms.ValidationError(
                                _('Each alternative item can only be added once per BOM material line.')
                            )
                        items.add(alternative_item)
        
        # Check maximum 10 alternatives
        if len(alternatives) > 10:
            raise forms.ValidationError(
                _('Maximum 10 alternative items allowed per BOM material line.')
            )


# Create the formset factory
BOMMaterialAlternativeFormSet = forms.inlineformset_factory(
    BOMMaterial,
    BOMMaterialAlternative,
    form=BOMMaterialAlternativeForm,
    formset=BOMMaterialAlternativeFormSetBase,
    extra=1,  # Start with 1 empty line for template
    can_delete=True,
    min_num=0,
    validate_min=False,
)


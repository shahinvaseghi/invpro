"""
Forms for production module.
"""
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shared.models import CompanyUnit
from inventory.models import ItemType, ItemCategory, ItemSubcategory
from .models import BOM, BOMMaterial, Machine, Person, WorkLine

# Import Warehouse for WorkLine (optional dependency - only if inventory module is installed)
try:
    from inventory.models import Warehouse
except ImportError:
    Warehouse = None


class PersonForm(forms.ModelForm):
    """Form for creating/editing personnel."""
    
    use_personnel_code_as_username = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Use Personnel Code as Username'),
        help_text=_('If checked, username will be same as personnel code'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'use_personnel_code'})
    )
    
    class Meta:
        model = Person
        fields = [
            'first_name',
            'last_name',
            'first_name_en',
            'last_name_en',
            'national_id',
            'personnel_code',
            'username',
            'phone_number',
            'mobile_number',
            'email',
            'description',
            'notes',
            'is_enabled',
            'company_units',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'personnel_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'personnel_code_field'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'username_field'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
            'company_units': forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),
        }
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'first_name_en': _('First Name (English)'),
            'last_name_en': _('Last Name (English)'),
            'national_id': _('National ID'),
            'personnel_code': _('Personnel Code'),
            'username': _('Username'),
            'phone_number': _('Phone'),
            'mobile_number': _('Mobile'),
            'email': _('Email'),
            'description': _('Description'),
            'notes': _('Notes'),
            'is_enabled': _('Status'),
            'company_units': _('Company Units'),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        if self.company_id:
            self.fields['company_units'].queryset = CompanyUnit.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['company_units'].help_text = _('Select one or more organizational units.')
        else:
            self.fields['company_units'].queryset = CompanyUnit.objects.none()
            self.fields['company_units'].help_text = _('Please select a company first.')

        self.fields['company_units'].required = False

        # If editing and username equals personnel_code, check the box
        if self.instance.pk and self.instance.username == self.instance.personnel_code:
            self.fields['use_personnel_code_as_username'].initial = True
    
    def clean(self):
        cleaned_data = super().clean()
        use_personnel_code = cleaned_data.get('use_personnel_code_as_username')
        personnel_code = cleaned_data.get('personnel_code')
        username = cleaned_data.get('username')
        
        # If checkbox is checked, use personnel_code as username
        if use_personnel_code:
            if not personnel_code:
                raise forms.ValidationError(_('Personnel Code is required when using it as username.'))
            cleaned_data['username'] = personnel_code
        else:
            if not username:
                raise forms.ValidationError(_('Username is required when not using personnel code.'))
        
        # Ensure selected units belong to the same company
        if self.company_id:
            units = cleaned_data.get('company_units')
            if units and units.filter(~Q(company_id=self.company_id)).exists():
                raise forms.ValidationError(_('Selected units must belong to the active company.'))
        
        return cleaned_data


class MachineForm(forms.ModelForm):
    """Form for creating/editing machines."""
    
    class Meta:
        model = Machine
        fields = [
            'name',
            'name_en',
            'machine_type',
            'work_center',
            'manufacturer',
            'model_number',
            'serial_number',
            'purchase_date',
            'installation_date',
            'capacity_specs',
            'maintenance_schedule',
            'last_maintenance_date',
            'next_maintenance_date',
            'status',
            'description',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'machine_type': forms.TextInput(attrs={'class': 'form-control'}),
            'work_center': forms.Select(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'capacity_specs': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'maintenance_schedule': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'last_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name'),
            'name_en': _('Name (English)'),
            'machine_type': _('Machine Type'),
            'work_center': _('Work Center'),
            'manufacturer': _('Manufacturer'),
            'model_number': _('Model Number'),
            'serial_number': _('Serial Number'),
            'purchase_date': _('Purchase Date'),
            'installation_date': _('Installation Date'),
            'capacity_specs': _('Capacity Specifications'),
            'maintenance_schedule': _('Maintenance Schedule'),
            'last_maintenance_date': _('Last Maintenance Date'),
            'next_maintenance_date': _('Next Maintenance Date'),
            'status': _('Status'),
            'description': _('Description'),
            'notes': _('Notes'),
            'is_enabled': _('Status'),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        if self.company_id:
            from .models import WorkCenter
            self.fields['work_center'].queryset = WorkCenter.objects.filter(company_id=self.company_id, is_enabled=1)
        else:
            from .models import WorkCenter
            self.fields['work_center'].queryset = WorkCenter.objects.none()


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
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)
        
        # Set default is_enabled if not provided (for new BOMs)
        if not self.instance.pk and 'is_enabled' in self.fields:
            self.fields['is_enabled'].initial = 1

        if self.company_id:
            from inventory.models import Item, ItemType, ItemCategory, ItemSubcategory
            
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
            from inventory.models import Item
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
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id

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
    
    def clean_is_optional(self):
        """Convert Boolean checkbox value to integer (0 or 1) for database storage."""
        value = self.cleaned_data.get('is_optional')
        
        # BooleanField returns True/False, convert to 1/0
        if value is True:
            result = 1
        else:
            result = 0
        
        return result
    
    def clean(self):
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
            except Exception as e:
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
    
    def full_clean(self):
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
class BOMMaterialLineFormSet(forms.BaseInlineFormSet):
    """Custom formset with better validation for BOM materials."""
    
    def clean(self):
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
    formset=BOMMaterialLineFormSet,
    extra=1,  # Start with 1 empty line
    can_delete=True,
    min_num=0,  # We handle minimum validation in clean()
    validate_min=False,  # We handle minimum validation in clean()
)


class WorkLineForm(forms.ModelForm):
    """Form for creating/editing work lines."""
    
    personnel = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label=_('پرسنل'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        help_text=_('یک یا چند پرسنل را برای این خط کاری انتخاب کنید'),
    )
    machines = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label=_('ماشین‌ها'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        help_text=_('یک یا چند ماشین را برای این خط کاری انتخاب کنید'),
    )
    
    class Meta:
        model = WorkLine
        fields = ['warehouse', 'name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled', 'personnel', 'machines']
        widgets = {
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'warehouse': _('انبار (اختیاری)'),
            'name': _('نام (فارسی)'),
            'name_en': _('نام (انگلیسی)'),
            'description': _('توضیحات'),
            'notes': _('یادداشت‌ها'),
            'sort_order': _('ترتیب نمایش'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if company_id:
            # Filter warehouses by company (only if inventory module is installed)
            if Warehouse:
                self.fields['warehouse'].queryset = Warehouse.objects.filter(
                    company_id=company_id,
                    is_enabled=1,
                ).order_by('name')
            else:
                self.fields['warehouse'].widget = forms.HiddenInput()
                self.fields['warehouse'].required = False
            
            # Filter personnel by company
            self.fields['personnel'].queryset = Person.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('first_name', 'last_name')
            
            # Filter machines by company
            self.fields['machines'].queryset = Machine.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
        else:
            if Warehouse:
                self.fields['warehouse'].queryset = Warehouse.objects.none()
            else:
                self.fields['warehouse'].widget = forms.HiddenInput()
            self.fields['personnel'].queryset = Person.objects.none()
            self.fields['machines'].queryset = Machine.objects.none()


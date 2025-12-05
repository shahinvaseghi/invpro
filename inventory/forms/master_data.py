"""
Master data forms for inventory module.

This module contains forms for:
- Item Types, Categories, Subcategories
- Warehouses
- Suppliers and Supplier Categories
- Items and Item Units
"""
import logging
from typing import Optional, Dict, Any

from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('inventory.forms.master_data')


class IntegerCheckboxField(forms.IntegerField):
    """Integer field specifically for checkbox values (0/1)."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        super().__init__(**kwargs)
    
    def to_python(self, value):
        """Convert value to int, defaulting to 0 if None or empty."""
        if value is None or value == '':
            return 0
        # Handle 'on' from checkbox (checked state)
        if value == 'on':
            return 1
        try:
            int_val = int(value)
            return int_val
        except (ValueError, TypeError):
            return 0
    
    def clean(self, value):
        """Ensure value is always 0 or 1."""
        # First convert to Python value (handles None/empty)
        python_value = self.to_python(value)
        # Ensure it's 0 or 1
        # Important: We must return int, not bool, for PositiveSmallIntegerField
        result = 1 if python_value == 1 else 0
        return result
    
    def has_changed(self, initial, data):
        """Override to ensure checkbox changes are detected correctly."""
        # For checkboxes, we need to compare 0/1 values
        if initial is None:
            initial = 0
        if data is None:
            data = 0
        try:
            initial_int = int(initial) if initial is not None else 0
            data_int = int(data) if data is not None else 0
            return initial_int != data_int
        except (ValueError, TypeError):
            return True


class IntegerCheckboxInput(forms.CheckboxInput):
    """Checkbox widget that works with IntegerField (0/1) values."""
    
    def value_from_datadict(self, data, files, name):
        """Return '1' if checked, '0' if unchecked (as string for IntegerField)."""
        # Since we always set value="1" in HTML, if checkbox is in POST, it's checked
        # If checkbox is not in POST, it's unchecked
        if name not in data:
            # Checkbox not in POST means it's unchecked
            return '0'
        
        # Checkbox is in POST, so it's checked
        # The value will be '1' (since we set value="1" in HTML)
        value = data.get(name)
        
        # Accept '1', 'on', or 1 as checked
        if value in ('1', 'on', 1):
            return '1'
        
        # If value is anything else (shouldn't happen, but just in case)
        return '0'
    
    def format_value(self, value):
        """Format value for rendering."""
        # Return the value as-is for CheckboxInput
        # CheckboxInput uses format_value to determine if checkbox should be checked
        # But we need to ensure the value attribute is set correctly
        if value is None:
            return 0
        try:
            int_value = int(value)
            return int_value
        except (ValueError, TypeError):
            return 0
    
    def value_omitted_from_data(self, data, files, name):
        """Check if checkbox value is omitted from data."""
        # For checkboxes, if name is not in data, it means unchecked
        return name not in data
    
    def get_context(self, name, value, attrs):
        """Get context for template rendering."""
        # Format the value to determine checked state
        formatted_value = self.format_value(value)
        int_value = int(formatted_value) if formatted_value is not None else 0
        
        # IMPORTANT: Always set value="1" in HTML so when checkbox is checked, it sends "1"
        # The checked state is determined by the 'checked' attribute, not the value
        # When checkbox is checked, it sends the value attribute; when unchecked, it's not in POST
        
        # Ensure value attribute is always "1" (not "0")
        # This way, when checked, POST will have value="1", when unchecked, field won't be in POST
        if 'value' in attrs:
            attrs = attrs.copy()
        else:
            attrs = attrs.copy() if attrs else {}
        
        # Always set value="1" - checked state is controlled by 'checked' attribute
        attrs['value'] = '1'
        
        # Call super() with modified attrs
        context = super().get_context(name, formatted_value, attrs)
        
        # Set checked attribute based on value
        if int_value == 1:
            context['widget']['attrs']['checked'] = True
        else:
            context['widget']['attrs'].pop('checked', None)
        
        # Ensure value is "1" in widget context too
        context['widget']['value'] = '1'
        context['widget']['attrs']['value'] = '1'
        
        return context

from inventory.models import (
    ItemType,
    ItemCategory,
    ItemSubcategory,
    Item,
    Supplier,
    SupplierCategory,
    Warehouse,
    ItemUnit,
)
from inventory.forms.base import UNIT_CHOICES


class ItemTypeForm(forms.ModelForm):
    """Form for creating/editing item types."""
    
    class Meta:
        model = ItemType
        fields = ['name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name (Persian)'),
            'name_en': _('Name (English)'),
            'description': _('Description'),
            'notes': _('Notes'),
            'sort_order': _('Sort Order'),
            'is_enabled': _('Status'),
        }


class ItemCategoryForm(forms.ModelForm):
    """Form for creating/editing item categories."""
    
    class Meta:
        model = ItemCategory
        fields = ['name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name (Persian)'),
            'name_en': _('Name (English)'),
            'description': _('Description'),
            'notes': _('Notes'),
            'sort_order': _('Sort Order'),
            'is_enabled': _('Status'),
        }


class ItemSubcategoryForm(forms.ModelForm):
    """Form for creating/editing item subcategories."""
    
    class Meta:
        model = ItemSubcategory
        fields = ['category', 'name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'category': _('Item Category'),
            'name': _('Name (Persian)'),
            'name_en': _('Name (English)'),
            'description': _('Description'),
            'notes': _('Notes'),
            'sort_order': _('Sort Order'),
            'is_enabled': _('Status'),
        }


from shared.forms.base import BaseModelForm


class WarehouseForm(BaseModelForm):
    """Form for creating/editing warehouses."""
    
    def __init__(self, *args, **kwargs):
        """Initialize form and remove company_id if not needed."""
        # company_id is set automatically by AutoSetFieldsMixin in view
        kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Warehouse
        fields = ['name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        labels = {
            'name': _('Name (Persian)'),
            'name_en': _('Name (English)'),
            'description': _('Description'),
            'notes': _('Notes'),
            'sort_order': _('Sort Order'),
            'is_enabled': _('Status'),
        }


class SupplierForm(forms.ModelForm):
    """Form for creating/editing suppliers."""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'name_en', 'phone_number', 'mobile_number',
            'email', 'address', 'city', 'state', 'country', 'tax_id',
            'description', 'sort_order', 'is_enabled'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name (Persian)'),
            'name_en': _('Name (English)'),
            'phone_number': _('Phone Number'),
            'mobile_number': _('Mobile Number'),
            'email': _('Email'),
            'address': _('Address'),
            'city': _('City'),
            'state': _('State/Province'),
            'country': _('Country Code'),
            'tax_id': _('Tax ID'),
            'description': _('Description'),
            'sort_order': _('Sort Order'),
            'is_enabled': _('Status'),
        }


class SupplierCategoryForm(forms.ModelForm):
    """Form for creating/editing supplier categories with optional subcategories and items."""

    is_primary = forms.BooleanField(
        required=False,
        label=_('دستهٔ اصلی'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    subcategories = forms.ModelMultipleChoiceField(
        queryset=ItemSubcategory.objects.none(),
        required=False,
        label=_('زیردسته‌های قابل تأمین'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-grid'}),
        help_text=_('در صورت نیاز، زیردسته‌های مربوط به این تأمین‌کننده را انتخاب کنید.'),
    )
    items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.none(),
        required=False,
        label=_('کالاهای قابل تأمین'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-grid'}),
        help_text=_('کالاهای موجود در همان دسته‌بندی (و زیردسته‌های انتخابی) را می‌توانید انتخاب کنید.'),
    )

    class Meta:
        model = SupplierCategory
        fields = ['supplier', 'category', 'is_primary', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'supplier': _('تأمین‌کننده'),
            'category': _('دسته‌بندی کالا'),
            'notes': _('یادداشت‌ها'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with company filtering."""
        self.company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)

        if self.company_id:
            self.fields['supplier'].queryset = Supplier.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            self.fields['category'].queryset = ItemCategory.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )

            category_id = self._resolve_category_id()
            subcategory_qs = ItemSubcategory.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            if category_id:
                subcategory_qs = subcategory_qs.filter(category_id=category_id)
            self.fields['subcategories'].queryset = subcategory_qs.order_by('category__name', 'name')

            item_qs = Item.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            if category_id:
                item_qs = item_qs.filter(category_id=category_id)
            selected_sub_ids = self._selected_subcategory_ids()
            if selected_sub_ids:
                item_qs = item_qs.filter(subcategory_id__in=selected_sub_ids)
            self.fields['items'].queryset = item_qs.order_by('name')
        else:
            self.fields['subcategories'].queryset = ItemSubcategory.objects.none()
            self.fields['items'].queryset = Item.objects.none()

        self.fields['supplier'].label_from_instance = lambda obj: obj.name
        self.fields['category'].label_from_instance = lambda obj: obj.name
        self.fields['subcategories'].label_from_instance = lambda obj: f"{obj.category.name} / {obj.name}"
        self.fields['items'].label_from_instance = lambda obj: obj.name

        # Prefill selections when editing
        if self.instance.pk:
            supplier = self.instance.supplier
            company = self.instance.company
            category = self.instance.category
            if supplier and company and category:
                sub_initial = supplier.subcategories.filter(
                    company=company,
                    subcategory__category=category,
                ).values_list('subcategory_id', flat=True)
                self.fields['subcategories'].initial = list(sub_initial)

                item_initial = supplier.items.filter(
                    company=company,
                    item__category=category,
                ).values_list('item_id', flat=True)
                self.fields['items'].initial = list(item_initial)

    def _resolve_category_id(self) -> Optional[int]:
        """Return current category id from data, instance, or initial."""
        if self.is_bound:
            value = self.data.get('category')
        else:
            value = self.initial.get('category') or getattr(self.instance, 'category_id', None)
        try:
            return int(value) if value else None
        except (TypeError, ValueError):
            return None

    def _selected_subcategory_ids(self) -> list:
        """Get selected subcategory IDs from form data."""
        if self.is_bound:
            return [int(pk) for pk in self.data.getlist('subcategories') if pk.isdigit()]
        initial = self.initial.get('subcategories')
        if initial:
            return list(initial)
        return []

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        supplier = cleaned_data.get('supplier')
        category = cleaned_data.get('category')
        subcategories = cleaned_data.get('subcategories') or []
        items = cleaned_data.get('items') or []

        if supplier and category:
            if supplier.company_id != category.company_id:
                raise forms.ValidationError(
                    _('تأمین‌کننده و دسته‌ی انتخاب‌شده مربوط به شرکت‌های متفاوت هستند.')
                )

            qs = SupplierCategory.objects.filter(
                company_id=supplier.company_id,
                supplier=supplier,
                category=category,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    _('برای این تأمین‌کننده و دسته‌بندی قبلاً ثبت انجام شده است.')
                )

            invalid_subcategories = [
                sub for sub in subcategories if sub.category_id != category.id
            ]
            if invalid_subcategories:
                self.add_error(
                    'subcategories',
                    _('زیردسته‌های انتخاب‌شده باید متعلق به همان دسته باشند.'),
                )

            selected_sub_ids = {sub.id for sub in subcategories}
            invalid_items = []
            for item in items:
                if item.category_id != category.id:
                    invalid_items.append(item)
                elif selected_sub_ids and item.subcategory_id and item.subcategory_id not in selected_sub_ids:
                    invalid_items.append(item)
            if invalid_items:
                self.add_error(
                    'items',
                    _('کالاهای انتخاب‌شده باید در زیردسته‌های انتخاب‌شده یا همان دسته باشند.'),
                )

        return cleaned_data


class ItemForm(BaseModelForm):
    """Form for creating/editing items."""

    is_sellable = IntegerCheckboxField(
        label=_('قابل فروش است'),
        widget=IntegerCheckboxInput(attrs={'class': 'form-check-input'}),
    )
    has_lot_tracking = IntegerCheckboxField(
        label=_('نیاز به رهگیری لات دارد'),
        widget=IntegerCheckboxInput(attrs={'class': 'form-check-input'}),
    )
    requires_temporary_receipt = IntegerCheckboxField(
        label=_('ورود از طریق رسید موقت'),
        widget=IntegerCheckboxInput(attrs={'class': 'form-check-input'}),
    )
    serial_in_qc = IntegerCheckboxField(
        label=_('سریال در QC'),
        widget=IntegerCheckboxInput(attrs={'class': 'form-check-input'}),
    )
    is_enabled = IntegerCheckboxField(
        label=_('فعال باشد'),
        widget=IntegerCheckboxInput(attrs={'class': 'form-check-input'}),
        initial=1,
    )
    default_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label=_('واحد اصلی'),
        # BaseModelForm automatically applies 'form-control' class
    )
    primary_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label=_('واحد گزارش (برای گزارش‌گیری)'),
        # BaseModelForm automatically applies 'form-control' class
    )
    allowed_warehouses = forms.ModelMultipleChoiceField(
        queryset=Warehouse.objects.none(),
        label=_('انبارهای مجاز'),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        help_text=_('حداقل یک انبار انتخاب کنید؛ اولین مورد به عنوان انبار اصلی ذخیره می‌شود.'),
    )

    class Meta:
        model = Item
        fields = [
            'type', 'category', 'subcategory',
            'user_segment', 'name', 'name_en',
            'secondary_batch_number',
            'is_sellable', 'has_lot_tracking', 'requires_temporary_receipt', 'serial_in_qc',
            'supply_type', 'planning_type', 'lead_time',
            'tax_id', 'tax_title', 'min_stock',
            'default_unit', 'primary_unit',
            'description', 'notes',
            'sort_order', 'is_enabled',
        ]
        widgets = {
            # BaseModelForm automatically applies 'form-control' class, but we can add extra attributes
            'user_segment': forms.TextInput(attrs={'maxlength': '2'}),
            'secondary_batch_number': forms.TextInput(attrs={'maxlength': '50'}),
            'lead_time': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
            'min_stock': forms.NumberInput(attrs={'step': '0.001'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'type': _('نوع کالا'),
            'category': _('دسته‌بندی'),
            'subcategory': _('زیردسته'),
            'user_segment': _('کد کاربری (۲ رقم)'),
            'name': _('نام (فارسی)'),
            'name_en': _('نام (English)'),
            'secondary_batch_number': _('بچ نامبر ثانویه'),
            'supply_type': _('نوع تامین'),
            'planning_type': _('نوع برنامه ریزی'),
            'lead_time': _('زمان تامین (روز)'),
            'tax_id': _('شناسه مالیاتی'),
            'tax_title': _('عنوان مالیاتی'),
            'min_stock': _('حداقل موجودی'),
            'description': _('توضیح کوتاه'),
            'notes': _('یادداشت‌ها'),
            'sort_order': _('ترتیب نمایش'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with company filtering."""
        self.company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)

        if self.company_id:
            self.fields['type'].queryset = ItemType.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            self.fields['category'].queryset = ItemCategory.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            self.fields['subcategory'].queryset = ItemSubcategory.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
            self.fields['allowed_warehouses'].queryset = Warehouse.objects.filter(
                company_id=self.company_id,
                is_enabled=1,
            )
        else:
            self.fields['allowed_warehouses'].queryset = Warehouse.objects.none()

        if self.instance.pk:
            selected = self.instance.warehouses.values_list('warehouse_id', flat=True)
            self.fields['allowed_warehouses'].initial = list(selected)
            
            # Set initial values for IntegerField checkboxes (0/1) from instance
            # IntegerField with CheckboxInput will work correctly with 0/1 values
            self.fields['is_sellable'].initial = self.instance.is_sellable
            self.fields['has_lot_tracking'].initial = self.instance.has_lot_tracking
            self.fields['requires_temporary_receipt'].initial = self.instance.requires_temporary_receipt
            self.fields['serial_in_qc'].initial = self.instance.serial_in_qc
            self.fields['is_enabled'].initial = self.instance.is_enabled

        self.fields['type'].label_from_instance = lambda obj: obj.name
        self.fields['category'].label_from_instance = lambda obj: obj.name
        self.fields['subcategory'].label_from_instance = lambda obj: obj.name
        self.fields['allowed_warehouses'].widget.attrs.update({'class': 'checkbox-grid'})
        self.fields['allowed_warehouses'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.name}"

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        item_type = cleaned_data.get('type')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        user_segment = cleaned_data.get('user_segment')
        warehouses = cleaned_data.get('allowed_warehouses')

        if item_type and category and item_type.company_id != category.company_id:
            raise forms.ValidationError(_('نوع کالا و دسته‌بندی انتخاب‌شده مربوط به شرکت‌های متفاوت هستند.'))

        if category and subcategory:
            if subcategory.category_id != category.id:
                raise forms.ValidationError(_('زیردسته انتخاب‌شده با دسته‌بندی هم‌خوانی ندارد.'))

        if user_segment and not user_segment.isdigit():
            self.add_error('user_segment', _('کد کاربری باید فقط عدد باشد.'))
        elif user_segment and len(user_segment) != 2:
            self.add_error('user_segment', _('کد کاربری باید دقیقاً دو رقم باشد.'))

        if not warehouses:
            self.add_error('allowed_warehouses', _('حداقل یک انبار باید انتخاب شود.'))
        elif self.company_id and warehouses.filter(~Q(company_id=self.company_id)).exists():
            self.add_error('allowed_warehouses', _('انبارهای انتخاب شده باید متعلق به همان شرکت فعال باشند.'))

        # IntegerCheckboxField already handles conversion to 0/1 in its clean() method
        # But we need to ensure fields are ALWAYS in cleaned_data, even if not in POST
        # IntegerCheckboxInput.value_from_datadict returns '0' or '1' as string
        # IntegerCheckboxField.clean() will convert to int 0 or 1
        checkbox_fields = ['is_sellable', 'has_lot_tracking', 'requires_temporary_receipt', 'serial_in_qc', 'is_enabled']
        for field_name in checkbox_fields:
            # Ensure field is always in cleaned_data
            if field_name not in cleaned_data:
                # If field is not in cleaned_data, it means it wasn't in POST (unchecked)
                # IntegerCheckboxField should have handled this, but ensure it's 0
                cleaned_data[field_name] = 0
            else:
                # Field is in cleaned_data, ensure it's 0 or 1
                value = cleaned_data.get(field_name)
                if value is None:
                    cleaned_data[field_name] = 0
                else:
                    try:
                        int_value = int(value)
                        cleaned_data[field_name] = 1 if int_value == 1 else 0
                    except (ValueError, TypeError):
                        cleaned_data[field_name] = 0

        return cleaned_data


class ItemUnitForm(forms.ModelForm):
    """Form for defining unit conversions for an item."""

    from_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label=_('واحد مبنا'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    to_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label=_('واحد تبدیل'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = ItemUnit
        fields = ['id', 'public_code', 'from_unit', 'from_quantity', 'to_unit', 'to_quantity', 'description', 'notes']
        widgets = {
            'public_code': forms.HiddenInput(),
            'from_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'to_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'from_quantity': _('مقدار مبنا'),
            'to_quantity': _('مقدار معادل'),
            'description': _('توضیح'),
            'notes': _('یادداشت‌ها'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form."""
        super().__init__(*args, **kwargs)
        self.fields['public_code'].required = False
        # نمایش بهتر برای فرم حذف
        if 'DELETE' in self.fields:
            self.fields['DELETE'].label = _('حذف شود؟')

    def set_company_id(self, company_id: Optional[int]) -> None:
        """Set company_id for form."""
        self.company_id = company_id


class ItemUnitFormSet(forms.BaseInlineFormSet):
    """FormSet for managing item unit conversions."""
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize formset with company_id."""
        self.company_id = company_id
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if hasattr(form, 'set_company_id'):
                form.set_company_id(self.company_id)
    
    def clean(self) -> Dict[str, Any]:
        """Override clean to skip validation for completely empty forms."""
        cleaned_data = super().clean()
        # Mark completely empty forms as valid (they will be ignored in save)
        for form in self.forms:
            if form.cleaned_data:
                # Check if form is empty (only DELETE checkbox or all fields empty)
                non_delete_fields = {k: v for k, v in form.cleaned_data.items() if k != 'DELETE'}
                if not any(v for v in non_delete_fields.values() if v):
                    # Form is empty - clear errors
                    form._errors = {}
        return cleaned_data
    
    def is_valid(self) -> bool:
        """Override is_valid to allow empty formsets."""
        # If formset is completely empty (no forms), it's still valid
        if not self.forms or self.total_form_count() == 0:
            return True
        
        # Call parent validation first to populate cleaned_data
        valid = super().is_valid()
        
        # If validation failed, check if all forms are empty (after clean)
        if not valid:
            all_empty = True
            for form in self.forms:
                # Check if form has any non-empty fields (excluding DELETE and hidden fields)
                if form.cleaned_data:
                    non_delete_fields = {k: v for k, v in form.cleaned_data.items() 
                                       if k != 'DELETE' and k not in ['id', 'public_code']}
                    if any(v for v in non_delete_fields.values() if v):
                        all_empty = False
                        break
                # Also check if form has any data in POST (for new forms)
                elif form.data:
                    # Check if any visible fields have values
                    visible_fields = ['from_quantity', 'from_unit', 'to_quantity', 'to_unit', 'description', 'notes']
                    has_data = any(form.data.get(f'{form.prefix}-{field}') for field in visible_fields)
                    if has_data:
                        all_empty = False
                        break
            
            # If all forms are empty, formset is valid (units are optional)
            if all_empty:
                # Clear all errors
                self._errors = []
                for form in self.forms:
                    form._errors = {}
                return True
        
        return valid


# Create ItemUnitFormSet using inlineformset_factory
# Note: We need to define the formset class first, then use it in inlineformset_factory
_ItemUnitFormSetBase = ItemUnitFormSet  # Store the class
ItemUnitFormSet = inlineformset_factory(
    Item,
    ItemUnit,
    form=ItemUnitForm,
    formset=_ItemUnitFormSetBase,
    extra=0,  # No empty rows by default - user adds rows as needed
    can_delete=True,
)


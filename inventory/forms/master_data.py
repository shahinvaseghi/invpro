"""
Master data forms for inventory module.

This module contains forms for:
- Item Types, Categories, Subcategories
- Warehouses
- Suppliers and Supplier Categories
- Items and Item Units
"""
from typing import Optional, Dict, Any

from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

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


class WarehouseForm(forms.ModelForm):
    """Form for creating/editing warehouses."""
    
    class Meta:
        model = Warehouse
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


class ItemForm(forms.ModelForm):
    """Form for creating/editing items."""

    is_sellable = forms.BooleanField(
        required=False,
        label=_('قابل فروش است'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    has_lot_tracking = forms.BooleanField(
        required=False,
        label=_('نیاز به رهگیری لات دارد'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    requires_temporary_receipt = forms.BooleanField(
        required=False,
        label=_('ورود از طریق رسید موقت'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    is_enabled = forms.BooleanField(
        required=False,
        label=_('فعال باشد'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=True,
    )
    default_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label=_('واحد اصلی'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    primary_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        label=_('واحد گزارش (برای گزارش‌گیری)'),
        widget=forms.Select(attrs={'class': 'form-control'}),
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
            'is_sellable', 'has_lot_tracking', 'requires_temporary_receipt',
            'tax_id', 'tax_title', 'min_stock',
            'default_unit', 'primary_unit',
            'description', 'notes',
            'sort_order', 'is_enabled',
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'user_segment': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'secondary_batch_number': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_title': forms.TextInput(attrs={'class': 'form-control'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'type': _('نوع کالا'),
            'category': _('دسته‌بندی'),
            'subcategory': _('زیردسته'),
            'user_segment': _('کد کاربری (۲ رقم)'),
            'name': _('نام (فارسی)'),
            'name_en': _('نام (English)'),
            'secondary_batch_number': _('بچ نامبر ثانویه'),
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


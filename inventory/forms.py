"""
Forms for inventory module.
"""
from collections import deque
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import (
    ItemType,
    ItemCategory,
    ItemSubcategory,
    Item,
    Supplier,
    SupplierCategory,
    SupplierSubcategory,
    SupplierItem,
    Warehouse,
    WorkLine,
    ItemUnit,
    ItemWarehouse,
    ReceiptTemporary,
    ReceiptPermanent,
    ReceiptConsignment,
    IssuePermanent,
    IssueConsumption,
    IssueConsignment,
    ItemSerial,
    CURRENCY_CHOICES,
    StocktakingDeficit,
    StocktakingSurplus,
    StocktakingRecord,
    PurchaseRequest,
    WarehouseRequest,
    # Line models
    IssuePermanentLine,
    IssueConsumptionLine,
    IssueConsignmentLine,
    ReceiptPermanentLine,
    ReceiptConsignmentLine,
)
from shared.models import CompanyUnit, Person
from .services import serials as serial_service
from .fields import JalaliDateField
from .widgets import JalaliDateInput
from inventory.utils.jalali import today_jalali

User = get_user_model()


def get_purchase_request_approvers(company_id):
    """
    Get queryset of Person objects that can approve purchase requests.
    For now, returns all active Person objects in the company.
    In future, this can be filtered by role/permission.
    """
    return Person.objects.filter(company_id=company_id, is_enabled=1).order_by('first_name', 'last_name')

UNIT_CHOICES = [
    ("", _("--- انتخاب کنید ---")),
    ("EA", _("عدد (EA)")),
    ("KG", _("کیلوگرم (KG)")),
    ("G", _("گرم (G)")),
    ("TON", _("تن")),
    ("L", _("لیتر (L)")),
    ("ML", _("میلی‌لیتر (ML)")),
    ("M", _("متر (M)")),
    ("CM", _("سانتی‌متر (CM)")),
    ("MM", _("میلی‌متر (MM)")),
    ("M2", _("متر مربع (M²)")),
    ("M3", _("متر مکعب (M³)")),
    ("BOX", _("بسته (BOX)")),
    ("CARTON", _("کارتن")),
    ("PAIR", _("جفت")),
    ("ROLL", _("رول")),
    ("SET", _("ست")),
]


def generate_document_code(model, company_id, prefix: str) -> str:
    today = timezone.now()
    month_year = today.strftime("%Y%m")
    base = f"{prefix}-{month_year}"
    last_code = (
        model.objects.filter(company_id=company_id, document_code__startswith=base)
        .order_by("-document_code")
        .values_list("document_code", flat=True)
        .first()
    )
    sequence = 0
    if last_code:
        try:
            sequence = int(last_code.split("-")[-1])
        except (ValueError, IndexError):
            sequence = 0
    return f"{base}-{sequence + 1:06d}"


def get_feature_approvers(feature_code: str, company_id: int):
    if not company_id:
        return Person.objects.none()

    approved_users = User.objects.filter(
        Q(
            company_accesses__company_id=company_id,
            company_accesses__access_level__permissions__resource_code=feature_code,
            company_accesses__access_level__permissions__can_approve=1,
        )
        | Q(
            groups__profile__access_levels__permissions__resource_code=feature_code,
            groups__profile__access_levels__permissions__can_approve=1,
        )
    ).distinct()

    return (
        Person.objects.filter(
            company_id=company_id,
            user__in=approved_users,
            is_enabled=1,
        )
        .order_by('first_name', 'last_name', 'public_code')
    )


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = [
            'item',
            'unit',
            'quantity_requested',
            'needed_by_date',
            'priority',
            'reason_code',
            'approver',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'needed_by_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'reason_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'approver': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'item': _('Item'),
            'unit': _('Unit'),
            'quantity_requested': _('Requested Quantity'),
            'needed_by_date': _('Needed By Date'),
            'priority': _('Priority'),
            'reason_code': _('Reason Code / Notes'),
            'approver': _('Approver'),
        }

    def __init__(self, *args, company_id=None, request_user=None, **kwargs):
        self.company_id = company_id
        self.request_user = request_user
        super().__init__(*args, **kwargs)

        self.fields['unit'].choices = UNIT_CHOICES
        if 'reason_code' in self.fields:
            self.fields['reason_code'].required = False

        if self.company_id:
            self.fields['item'].queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
            approvers = get_feature_approvers("inventory.requests.purchase", self.company_id)
            self.fields['approver'].queryset = approvers
            self.fields['approver'].empty_label = _("--- انتخاب کنید ---")
            self.fields['approver'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} · {obj.public_code}"
        else:
            self.fields['item'].queryset = Item.objects.none()
            self.fields['approver'].queryset = Person.objects.none()

        self._set_unit_choices()

    def _resolve_item(self, candidate=None):
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        return None

    def _get_item_allowed_units(self, item: Item):
        if not item:
            return []
        codes = []

        def add(code: str):
            if code and code not in codes:
                codes.append(code)

        add(item.default_unit)
        add(item.primary_unit)

        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)

        # If no units found, add default unit 'EA' as fallback
        if not codes:
            codes.append('EA')
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]

    def _set_unit_choices(self):
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        item = self._resolve_item()
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.choices = [placeholder]

    def clean_unit(self):
        unit = self.cleaned_data.get('unit')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item:
            allowed = {row['value'] for row in self._get_item_allowed_units(item)}
            if unit and unit not in allowed:
                raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        return unit

    def clean_approver(self):
        approver = self.cleaned_data.get('approver')
        if approver and self.company_id and approver.company_id != self.company_id:
            raise forms.ValidationError(_('Selected approver must belong to the active company.'))
        return approver

    def clean(self):
        cleaned_data = super().clean()
        self._set_unit_choices()
        return cleaned_data


class WarehouseRequestForm(forms.ModelForm):
    class Meta:
        model = WarehouseRequest
        fields = [
            'item',
            'unit',
            'quantity_requested',
            'warehouse',
            'department_unit',
            'needed_by_date',
            'priority',
            'purpose',
            'approver',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'department_unit': forms.Select(attrs={'class': 'form-control'}),
            'needed_by_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'approver': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'item': _('Item'),
            'unit': _('Unit'),
            'quantity_requested': _('Requested Quantity'),
            'warehouse': _('Warehouse'),
            'department_unit': _('Organizational Unit'),
            'needed_by_date': _('Needed By Date'),
            'priority': _('Priority'),
            'purpose': _('Purpose / Notes'),
            'approver': _('Approver'),
        }

    def __init__(self, *args, company_id=None, request_user=None, **kwargs):
        self.company_id = company_id
        self.request_user = request_user
        super().__init__(*args, **kwargs)

        self.fields['unit'].choices = UNIT_CHOICES
        self.fields['purpose'].required = False
        self.fields['department_unit'].required = False

        if self.company_id:
            self.fields['item'].queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
            self.fields['warehouse'].queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            self.fields['department_unit'].queryset = CompanyUnit.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            self.fields['department_unit'].empty_label = _("--- انتخاب کنید ---")
            approvers = get_feature_approvers("inventory.requests.warehouse", self.company_id)
            self.fields['approver'].queryset = approvers
            self.fields['approver'].empty_label = _("--- انتخاب کنید ---")
            self.fields['approver'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} · {obj.public_code}"
        else:
            self.fields['item'].queryset = Item.objects.none()
            self.fields['warehouse'].queryset = Warehouse.objects.none()
            self.fields['department_unit'].queryset = CompanyUnit.objects.none()
            self.fields['approver'].queryset = Person.objects.none()

        self._set_unit_choices()
        self._set_warehouse_queryset()

    def _resolve_item(self, candidate=None):
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                return None
        return None

    def _get_item_allowed_units(self, item: Item):
        if not item:
            return []
        codes = []

        def add(code: str):
            if code and code not in codes:
                codes.append(code)

        add(item.default_unit)
        add(item.primary_unit)

        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)

        # If no units found, add default unit 'EA' as fallback
        if not codes:
            codes.append('EA')
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]

    def _get_item_allowed_warehouses(self, item: Item):
        if not item:
            return []
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]
        if not warehouses:
            warehouses = list(Warehouse.objects.filter(company_id=item.company_id, is_enabled=1))
        return [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]

    def _set_unit_choices(self):
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        item = self._resolve_item()
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            current = getattr(self.instance, 'unit', None)
            if current and current not in [code for code, _ in allowed]:
                label_map = dict(allowed)
                allowed.append((current, label_map.get(current, current)))
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.choices = [placeholder]

    def _set_warehouse_queryset(self):
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        item = self._resolve_item()
        if item:
            allowed_ids = [int(option['value']) for option in self._get_item_allowed_warehouses(item)]
            if allowed_ids:
                warehouse_field.queryset = Warehouse.objects.filter(pk__in=allowed_ids, is_enabled=1)
                return
        if self.company_id:
            warehouse_field.queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)

    def clean_unit(self):
        unit = self.cleaned_data.get('unit')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item:
            allowed = {row['value'] for row in self._get_item_allowed_units(item)}
            if unit and unit not in allowed:
                raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        return unit

    def clean_warehouse(self):
        warehouse = self.cleaned_data.get('warehouse')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if warehouse and item:
            allowed = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            if allowed and warehouse.id not in allowed:
                raise forms.ValidationError(_('Selected warehouse is not permitted for this item.'))
        return warehouse

    def clean_approver(self):
        approver = self.cleaned_data.get('approver')
        if approver and self.company_id and approver.company_id != self.company_id:
            raise forms.ValidationError(_('Selected approver must belong to the active company.'))
        return approver

    def clean(self):
        cleaned_data = super().clean()
        self._set_unit_choices()
        self._set_warehouse_queryset()
        return cleaned_data


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

    def _resolve_category_id(self):
        """Return current category id from data, instance, or initial."""

        if self.is_bound:
            value = self.data.get('category')
        else:
            value = self.initial.get('category') or getattr(self.instance, 'category_id', None)
        try:
            return int(value) if value else None
        except (TypeError, ValueError):
            return None

    def _selected_subcategory_ids(self):
        if self.is_bound:
            return [int(pk) for pk in self.data.getlist('subcategories') if pk.isdigit()]
        initial = self.initial.get('subcategories')
        if initial:
            return list(initial)
        return []

    def clean(self):
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
            'tax_id': _('شناسه مالیاتی'),
            'tax_title': _('عنوان مالیاتی'),
            'min_stock': _('حداقل موجودی'),
            'description': _('توضیح کوتاه'),
            'notes': _('یادداشت‌ها'),
            'sort_order': _('ترتیب نمایش'),
        }

    def __init__(self, *args, **kwargs):
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

    def clean(self):
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
        super().__init__(*args, **kwargs)
        self.fields['public_code'].required = False
        # نمایش بهتر برای فرم حذف
        if 'DELETE' in self.fields:
            self.fields['DELETE'].label = _('حذف شود؟')

    def set_company_id(self, company_id):
        self.company_id = company_id


class ItemUnitFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if hasattr(form, 'set_company_id'):
                form.set_company_id(self.company_id)


ItemUnitFormSet = inlineformset_factory(
    Item,
    ItemUnit,
    form=ItemUnitForm,
    formset=ItemUnitFormSet,
    extra=2,
    can_delete=True,
)


class ReceiptBaseForm(forms.ModelForm):
    """Base helpers for receipt forms with company-aware querysets."""

    date_widget = JalaliDateInput(attrs={'class': 'form-control'})
    datetime_widget = forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local', 'step': 60},
        format='%Y-%m-%dT%H:%M',
    )

    def __init__(self, *args, company_id=None, **kwargs):
        self.company_id = company_id or getattr(kwargs.get('instance'), 'company_id', None)
        self._unit_factor = Decimal('1')
        self._entered_unit_value = None
        self._entered_quantity_value = None
        self._entered_unit_price_value = None
        super().__init__(*args, **kwargs)

        if 'currency' in self.fields:
            self.fields['currency'].widget = forms.Select(attrs={'class': 'form-control'})
            self.fields['currency'].choices = [('', _('--- انتخاب کنید ---'))] + list(CURRENCY_CHOICES)
            self.fields['currency'].required = False

        if 'document_date' in self.fields:
            self.fields['document_date'].widget = self.date_widget
            self.fields['document_date'].required = False
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
            self.fields['document_date'].widget = forms.HiddenInput()
        if 'document_code' in self.fields:
            self.fields['document_code'].widget = forms.HiddenInput()
            self.fields['document_code'].required = False

        if self.company_id:
            self._filter_company_scoped_fields()
        
        # Set unit choices - this must be done before restoring initial values
        self._set_unit_choices()
        
        # Restore entered values if editing
        if not self.is_bound and getattr(self.instance, 'pk', None):
            entry_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
            if 'unit' in self.fields and entry_unit:
                # Ensure the unit is in choices, if not add it
                unit_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in unit_choices]
                if entry_unit not in unit_codes:
                    # Add current unit to choices if not present
                    self.fields['unit'].choices = unit_choices + [(entry_unit, entry_unit)]
                # Django ChoiceField uses instance.field for display when editing
                # So we need to set instance.unit to the entered_unit for proper display
                if hasattr(self.instance, 'unit'):
                    # Store the original unit if we're changing it
                    if not hasattr(self.instance, '_original_unit'):
                        self.instance._original_unit = self.instance.unit
                    # Set unit to entered_unit for display purposes
                    self.instance.unit = entry_unit
                # Also set initial as backup
                self.initial['unit'] = entry_unit
            
            if 'quantity' in self.fields and getattr(self.instance, 'entered_quantity', None) is not None:
                self.initial['quantity'] = self.instance.entered_quantity
            entry_price = getattr(self.instance, 'entered_unit_price', None)
            if 'unit_price' in self.fields and entry_price is not None:
                self.initial['unit_price'] = entry_price
            if 'unit_price_estimate' in self.fields and entry_price is not None:
                self.initial['unit_price_estimate'] = entry_price
        
        if 'expected_return_date' in self.fields:
            self.fields['expected_return_date'].widget = self.date_widget
        if 'expected_receipt_date' in self.fields:
            self.fields['expected_receipt_date'].widget = self.date_widget
        if 'conversion_date' in self.fields:
            self.fields['conversion_date'].widget = self.date_widget
        if 'document_code' in self.fields:
            self.fields['document_code'].widget = forms.HiddenInput()
            self.fields['document_code'].required = False

    def _filter_company_scoped_fields(self):
        if 'item' in self.fields:
            self.fields['item'].queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        if 'warehouse' in self.fields:
            self.fields['warehouse'].queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.name} · {obj.public_code}"
        if 'supplier' in self.fields:
            self.fields['supplier'].queryset = Supplier.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['supplier'].label_from_instance = lambda obj: f"{obj.name} · {obj.public_code}"
        if 'temporary_receipt' in self.fields:
            self.fields['temporary_receipt'].queryset = ReceiptTemporary.objects.filter(company_id=self.company_id)
            self.fields['temporary_receipt'].label_from_instance = lambda obj: f"{obj.document_code} · {obj.item.name}"
        if 'purchase_request' in self.fields:
            self.fields['purchase_request'].queryset = PurchaseRequest.objects.filter(
                company_id=self.company_id,
                status=PurchaseRequest.Status.APPROVED,
            )
            self.fields['purchase_request'].label_from_instance = lambda obj: f"{obj.request_code} · {obj.item.name}"
        if 'warehouse_request' in self.fields:
            self.fields['warehouse_request'].queryset = WarehouseRequest.objects.filter(
                company_id=self.company_id,
                request_status='approved',
                is_locked=1,
            )
            self.fields['warehouse_request'].label_from_instance = lambda obj: f"{obj.request_code} · {obj.item.name}"
        if 'conversion_receipt' in self.fields:
            self.fields['conversion_receipt'].queryset = ReceiptPermanent.objects.filter(company_id=self.company_id)
            self.fields['conversion_receipt'].label_from_instance = lambda obj: f"{obj.document_code} · {obj.item.name}"

    def _clean_company_match(self, cleaned_data, field_name, model_verbose):
        obj = cleaned_data.get(field_name)
        if obj and getattr(obj, 'company_id', None) != self.company_id:
            self.add_error(field_name, _('Selected %(model)s must belong to the active company.') % {'model': model_verbose})

    def _get_item_allowed_units(self, item: Item):
        if not item:
            return []
        codes = []

        def add(code: str):
            if code and code not in codes:
                codes.append(code)

        add(item.default_unit)
        add(item.primary_unit)

        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)

        # If no units found, add default unit 'EA' as fallback
        if not codes:
            codes.append('EA')
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]

    def _resolve_item(self, candidate=None):
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None

    def _set_unit_choices(self):
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        item = self._resolve_item()
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            entry_unit = getattr(self.instance, 'entered_unit', None)
            if entry_unit and entry_unit not in [code for code, _ in allowed]:
                label_map = dict(allowed)
                allowed.append((entry_unit, label_map.get(entry_unit, entry_unit)))
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.choices = [placeholder]

    def _get_unit_factor(self, item: Item, unit_code: str) -> Decimal:
        default_unit = item.default_unit
        if not unit_code or unit_code == default_unit:
            return Decimal('1')

        graph = {}
        for conversion in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            from_qty = conversion.from_quantity
            to_qty = conversion.to_quantity
            if from_qty in (None, 0) or to_qty in (None, 0):
                continue
            graph.setdefault(conversion.from_unit, []).append((conversion.to_unit, to_qty / from_qty))
            graph.setdefault(conversion.to_unit, []).append((conversion.from_unit, from_qty / to_qty))

        visited = set()
        queue = deque([(unit_code, Decimal('1'))])
        while queue:
            unit, factor = queue.popleft()
            if unit == default_unit:
                return factor
            if unit in visited:
                continue
            visited.add(unit)
            for neighbor, ratio in graph.get(unit, []):
                queue.append((neighbor, factor * ratio))

        return Decimal('1')

    def _validate_unit(self, cleaned_data):
        self._unit_factor = Decimal('1')
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        unit = cleaned_data.get('unit') or item.default_unit
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        allowed.add(item.default_unit)
        if unit not in allowed:
            self.add_error('unit', _('Selected unit is not configured for this item.'))
        factor = self._get_unit_factor(item, unit)
        self._unit_factor = factor
        self._entered_unit_value = unit
        cleaned_data['unit'] = item.default_unit

    def _normalize_quantity(self, cleaned_data):
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        quantity = cleaned_data.get('quantity')
        if not item or quantity in (None, ''):
            return
        factor = getattr(self, '_unit_factor', Decimal('1'))
        if not isinstance(quantity, Decimal):
            try:
                quantity = Decimal(str(quantity))
            except (InvalidOperation, TypeError):
                return
        self._entered_quantity_value = quantity
        cleaned_data['quantity'] = quantity * factor
        cleaned_data['unit'] = item.default_unit
        self.instance.unit = item.default_unit
        self.instance.quantity = cleaned_data['quantity']

    def clean(self):
        cleaned_data = super().clean()
        self._validate_unit(cleaned_data)
        self._normalize_quantity(cleaned_data)
        return cleaned_data


class ReceiptTemporaryForm(ReceiptBaseForm):
    """Create/update form for temporary receipts."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = ReceiptTemporary
        fields = [
            'document_code',
            'document_date',
            'item',
            'warehouse',
            'unit',
            'quantity',
            'expected_receipt_date',
            'supplier',
            'source_document_type',
            'source_document_code',
            'status',
            'qc_approval_notes',
        ]
        widgets = {
            'document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'source_document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'source_document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'qc_approval_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'document_code': _('Document Code'),
            'document_date': _('Document Date'),
            'item': _('Item'),
            'warehouse': _('Warehouse'),
            'quantity': _('Quantity'),
            'expected_receipt_date': _('Expected Conversion Date'),
            'supplier': _('Supplier'),
            'source_document_type': _('Source Document Type'),
            'source_document_code': _('Source Document Code'),
            'status': _('Status'),
            'qc_approval_notes': _('QC Notes'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'status' in self.fields:
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['status'].required = False
            if not self.instance.pk:
                self.fields['status'].initial = ReceiptTemporary.Status.DRAFT

    def clean(self):
        cleaned_data = super().clean()
        if self.company_id:
            self._clean_company_match(cleaned_data, 'item', _('item'))
            self._clean_company_match(cleaned_data, 'warehouse', _('warehouse'))
            if cleaned_data.get('supplier'):
                self._clean_company_match(cleaned_data, 'supplier', _('supplier'))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptTemporary, instance.company_id, "TMP")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.status = self.cleaned_data.get('status') or ReceiptTemporary.Status.DRAFT
        instance.is_locked = getattr(self.instance, 'is_locked', 0) or 0
        instance.unit = self.instance.unit  # ensure default unit persisted
        instance.quantity = self.instance.quantity
        entered_unit = self._entered_unit_value or getattr(instance, 'entered_unit', '') or instance.unit
        instance.entered_unit = entered_unit
        if self._entered_quantity_value is not None:
            instance.entered_quantity = self._entered_quantity_value
        elif instance.entered_quantity is None:
            instance.entered_quantity = instance.quantity
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class ReceiptPermanentForm(forms.ModelForm):
    """Header-only form for permanent receipt documents with multi-line support."""

    requires_temporary_receipt = forms.BooleanField(
        required=False,
        label=_('Requires Temporary Receipt'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = ReceiptPermanent
        fields = [
            'document_code',
            'document_date',
            'requires_temporary_receipt',
            'temporary_receipt',
            'purchase_request',
            'warehouse_request',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
        }

    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required and hidden (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
            self.fields['document_code'].widget = forms.HiddenInput()
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            self.fields['document_date'].widget = forms.HiddenInput()
            # Set initial value to today if creating new
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id:
            if 'temporary_receipt' in self.fields:
                self.fields['temporary_receipt'].queryset = ReceiptTemporary.objects.filter(
                    company_id=self.company_id
                ).order_by('-document_date', 'document_code')
                self.fields['temporary_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
            
            if 'purchase_request' in self.fields:
                self.fields['purchase_request'].queryset = PurchaseRequest.objects.filter(
                    company_id=self.company_id
                ).order_by('-request_date', 'request_code')
                self.fields['purchase_request'].label_from_instance = lambda obj: f"{obj.request_code}"
            
            if 'warehouse_request' in self.fields:
                self.fields['warehouse_request'].queryset = WarehouseRequest.objects.filter(
                    company_id=self.company_id
                ).order_by('-needed_by_date', 'request_code')
                self.fields['warehouse_request'].label_from_instance = lambda obj: f"{obj.request_code}"
        
        if self.instance.pk:
            self.fields['requires_temporary_receipt'].initial = bool(self.instance.requires_temporary_receipt)

    def clean_document_code(self):
        """Auto-generate document_code if not provided."""
        document_code = self.cleaned_data.get('document_code', '').strip()
        if not document_code:
            # Will be generated in save() method
            return ''
        return document_code
    
    def clean_document_date(self):
        """Auto-generate document_date if not provided."""
        document_date = self.cleaned_data.get('document_date')
        if not document_date:
            # Return today's date as default
            return timezone.now().date()
        return document_date

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure document_code and document_date are set (will be generated in save if empty)
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        if self.company_id:
            if cleaned_data.get('temporary_receipt'):
                temp = cleaned_data.get('temporary_receipt')
                if temp.company_id != self.company_id:
                    self.add_error('temporary_receipt', _('Selected temporary receipt belongs to a different company.'))
            if cleaned_data.get('purchase_request'):
                pr = cleaned_data.get('purchase_request')
                if pr.company_id != self.company_id:
                    self.add_error('purchase_request', _('Selected purchase request belongs to a different company.'))
            if cleaned_data.get('warehouse_request'):
                wr = cleaned_data.get('warehouse_request')
                if wr.company_id != self.company_id:
                    self.add_error('warehouse_request', _('Selected warehouse request belongs to a different company.'))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptPermanent, instance.company_id, "PRM")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.requires_temporary_receipt = 1 if self.cleaned_data.get('requires_temporary_receipt') else 0
        
        if commit:
            instance.save()
            # Handle temporary receipt conversion
            if instance.temporary_receipt:
                temp = instance.temporary_receipt
                updated_fields = set()
                if temp.is_locked != 1:
                    temp.is_locked = 1
                    updated_fields.add('is_locked')
                if temp.is_converted != 1:
                    temp.is_converted = 1
                    updated_fields.add('is_converted')
                if temp.converted_receipt_id != instance.id:
                    temp.converted_receipt = instance
                    temp.converted_receipt_code = instance.document_code
                    updated_fields.update({'converted_receipt', 'converted_receipt_code'})
                if updated_fields:
                    temp.edited_by = instance.edited_by or instance.created_by or temp.edited_by
                    updated_fields.add('edited_by')
                    temp.save(update_fields=list(updated_fields))
        return instance

class ReceiptConsignmentForm(forms.ModelForm):
    """Header-only form for consignment receipt documents with multi-line support."""

    requires_temporary_receipt = forms.BooleanField(
        required=False,
        label=_('Requires Temporary Receipt'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = ReceiptConsignment
        fields = [
            'document_code',
            'document_date',
            'consignment_contract_code',
            'expected_return_date',
            'valuation_method',
            'requires_temporary_receipt',
            'temporary_receipt',
            'purchase_request',
            'warehouse_request',
            'ownership_status',
            'conversion_receipt',
            'conversion_date',
            'return_document_id',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
            'consignment_contract_code': forms.TextInput(attrs={'class': 'form-control'}),
            'expected_return_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'ownership_status': forms.TextInput(attrs={'class': 'form-control'}),
            'conversion_date': JalaliDateInput(attrs={'class': 'form-control'}),
            'return_document_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required (they're auto-generated, already hidden in Meta)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            # Set initial value to today if creating new
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id:
            if 'temporary_receipt' in self.fields:
                self.fields['temporary_receipt'].queryset = ReceiptTemporary.objects.filter(
                    company_id=self.company_id
                ).order_by('-document_date', 'document_code')
                self.fields['temporary_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
            
            if 'purchase_request' in self.fields:
                self.fields['purchase_request'].queryset = PurchaseRequest.objects.filter(
                    company_id=self.company_id
                ).order_by('-request_date', 'request_code')
                self.fields['purchase_request'].label_from_instance = lambda obj: f"{obj.request_code}"
            
            if 'warehouse_request' in self.fields:
                self.fields['warehouse_request'].queryset = WarehouseRequest.objects.filter(
                    company_id=self.company_id
                ).order_by('-needed_by_date', 'request_code')
                self.fields['warehouse_request'].label_from_instance = lambda obj: f"{obj.request_code}"
            
            if 'conversion_receipt' in self.fields:
                self.fields['conversion_receipt'].queryset = ReceiptPermanent.objects.filter(
                    company_id=self.company_id
                ).order_by('-document_date', 'document_code')
                self.fields['conversion_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
        
        if self.instance.pk:
            self.fields['requires_temporary_receipt'].initial = bool(self.instance.requires_temporary_receipt)

    def clean_document_code(self):
        """Auto-generate document_code if not provided."""
        document_code = self.cleaned_data.get('document_code', '').strip()
        if not document_code:
            # Will be generated in save() method
            return ''
        return document_code
    
    def clean_document_date(self):
        """Auto-generate document_date if not provided."""
        document_date = self.cleaned_data.get('document_date')
        if not document_date:
            # Return today's date as default
            return timezone.now().date()
        return document_date

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure document_code and document_date are set (will be generated in save if empty)
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        if self.company_id:
            if cleaned_data.get('temporary_receipt'):
                temp = cleaned_data.get('temporary_receipt')
                if temp.company_id != self.company_id:
                    self.add_error('temporary_receipt', _('Selected temporary receipt belongs to a different company.'))
            if cleaned_data.get('purchase_request'):
                pr = cleaned_data.get('purchase_request')
                if pr.company_id != self.company_id:
                    self.add_error('purchase_request', _('Selected purchase request belongs to a different company.'))
            if cleaned_data.get('warehouse_request'):
                wr = cleaned_data.get('warehouse_request')
                if wr.company_id != self.company_id:
                    self.add_error('warehouse_request', _('Selected warehouse request belongs to a different company.'))
            if cleaned_data.get('conversion_receipt'):
                conv = cleaned_data.get('conversion_receipt')
                if conv.company_id != self.company_id:
                    self.add_error('conversion_receipt', _('Selected conversion receipt belongs to a different company.'))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptConsignment, instance.company_id, "CON")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.requires_temporary_receipt = 1 if self.cleaned_data.get('requires_temporary_receipt') else 0
        
        if commit:
            instance.save()
        return instance


class IssueBaseForm(ReceiptBaseForm):
    """Base form for issue documents."""

    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, company_id=company_id, **kwargs)
        self._serial_item = self._resolve_item()
        self._configure_serial_field()

    def _filter_company_scoped_fields(self):
        super()._filter_company_scoped_fields()

        if 'department_unit' in self.fields:
            queryset = CompanyUnit.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['department_unit'].queryset = queryset
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.name}"
            self.fields['department_unit'].required = False

        if 'work_line' in self.fields:
            queryset = WorkLine.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['work_line'].queryset = queryset
            self.fields['work_line'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.name}"
            self.fields['work_line'].required = False

        if 'consignment_receipt' in self.fields:
            queryset = ReceiptConsignment.objects.filter(company_id=self.company_id)
            self.fields['consignment_receipt'].queryset = queryset
            self.fields['consignment_receipt'].label_from_instance = lambda obj: f"{obj.document_code} · {obj.item.name}"

    def _configure_serial_field(self):
        serial_field = self.fields.get('serials')
        if not serial_field:
            return

        item = self._serial_item
        if not item or item.has_lot_tracking != 1:
            self.fields.pop('serials', None)
            return

        queryset = ItemSerial.objects.filter(
            company_id=self.company_id,
            item=item,
        )
        status_filter = Q(current_status=ItemSerial.Status.AVAILABLE)
        if getattr(self.instance, 'pk', None):
            status_filter |= Q(
                current_status=ItemSerial.Status.RESERVED,
                current_document_type=self.instance.__class__.__name__,
                current_document_id=self.instance.pk,
            )
        serial_field.queryset = queryset.filter(status_filter).order_by("serial_code")
        serial_field.required = False
        serial_field.help_text = _('Use the "Assign Serials" action to manage serial numbers.')
        if getattr(self.instance, 'pk', None):
            serial_field.initial = self.instance.serials.values_list("pk", flat=True)

    def clean(self):
        cleaned_data = super().clean()

        if self.company_id:
            for field_name, verbose in [
                ('department_unit', _('unit')),
                ('work_line', _('work line')),
                ('consignment_receipt', _('consignment receipt')),
            ]:
                if field_name in self.fields and cleaned_data.get(field_name):
                    self._clean_company_match(cleaned_data, field_name, verbose)

            warehouse = cleaned_data.get('warehouse')
            work_line = cleaned_data.get('work_line')
            if warehouse and work_line and work_line.warehouse_id != warehouse.id:
                self.add_error('work_line', _('Selected work line belongs to a different warehouse.'))

        self._validate_serials(cleaned_data)
        return cleaned_data

    def _validate_serials(self, cleaned_data):
        if 'serials' not in self.fields:
            return

        item = self._serial_item
        if not item or item.has_lot_tracking != 1:
            return

        selected_serials = cleaned_data.get('serials') or []
        quantity = cleaned_data.get('quantity')
        if quantity in (None, ''):
            quantity = getattr(self.instance, 'quantity', None)
        if quantity is None:
            return

        try:
            quantity_decimal = Decimal(quantity)
        except (InvalidOperation, TypeError):
            self.add_error('quantity', _('Quantity must be a whole number for serialised items.'))
            return

        expected = int(quantity_decimal)
        if quantity_decimal != Decimal(expected):
            self.add_error('quantity', _('Quantity must be a whole number for serialised items.'))
            return

        if len(selected_serials) != expected:
            self.add_error('serials', _('Select exactly %(count)s serial numbers.') % {'count': expected})

        invalid_serials = [serial for serial in selected_serials if serial.item_id != item.id]
        if invalid_serials:
            self.add_error('serials', _('Selected serial numbers do not belong to this item.'))


class IssuePermanentForm(forms.ModelForm):
    """Header-only form for permanent issue documents with multi-line support."""

    department_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Organizational Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which company unit received this issue.'),
    )

    class Meta:
        model = IssuePermanent
        fields = [
            'document_code',
            'document_date',
            'department_unit',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
        }

    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required and hidden (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
            self.fields['document_code'].widget = forms.HiddenInput()
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            self.fields['document_date'].widget = forms.HiddenInput()
            # Set initial value to today if creating new
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id and 'department_unit' in self.fields:
            self.fields['department_unit'].queryset = CompanyUnit.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('name')
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"

    def clean_document_code(self):
        """Auto-generate document_code if not provided."""
        document_code = self.cleaned_data.get('document_code')
        if not document_code:
            # Will be generated in save()
            return ''
        return document_code
    
    def clean_document_date(self):
        """Auto-generate document_date if not provided."""
        document_date = self.cleaned_data.get('document_date')
        if not document_date:
            # Will be generated in save()
            return timezone.now().date()
        return document_date
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Set default values for document_code and document_date if not provided
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Ensure company_id is set
        if not instance.company_id and self.company_id:
            instance.company_id = self.company_id
        
        if not instance.document_code:
            instance.document_code = generate_document_code(IssuePermanent, instance.company_id, "ISP")
        if not instance.document_date:
            instance.document_date = timezone.now().date()

        department_unit = self.cleaned_data.get('department_unit')
        if department_unit:
            instance.department_unit = department_unit
            instance.department_unit_code = department_unit.public_code
        else:
            instance.department_unit = None
            instance.department_unit_code = ''
        
        if commit:
            instance.save()
        return instance


class IssueConsumptionForm(forms.ModelForm):
    """Header-only form for consumption issue documents with multi-line support."""

    class Meta:
        model = IssueConsumption
        fields = [
            'document_code',
            'document_date',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),  # Hidden, auto-generated
        }

    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            # Set initial value for document_date
            if not self.instance.pk:
                self.fields['document_date'].initial = timezone.now().date()
    
    def clean_document_date(self):
        """Clean and provide default value for document_date"""
        date_value = self.cleaned_data.get('document_date')
        if not date_value:
            date_value = timezone.now().date()
        return date_value
    
    def clean_document_code(self):
        """Clean and provide default value for document_code"""
        code_value = self.cleaned_data.get('document_code')
        if not code_value:
            code_value = ''
        return code_value

    def clean(self):
        cleaned_data = super().clean()
        
        # Set default values for document_code and document_date if not provided
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(IssueConsumption, instance.company_id, "ISU")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        
        if commit:
            instance.save()
        return instance


class IssueConsignmentForm(forms.ModelForm):
    """Header-only form for consignment issue documents with multi-line support."""

    department_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Organizational Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which company unit received this consignment.'),
    )

    class Meta:
        model = IssueConsignment
        fields = [
            'document_code',
            'document_date',
            'department_unit',
        ]
        widgets = {
            'document_code': forms.HiddenInput(),
            'document_date': forms.HiddenInput(),
        }

    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        
        # Make document_code and document_date not required (they're auto-generated)
        if 'document_code' in self.fields:
            self.fields['document_code'].required = False
        if 'document_date' in self.fields:
            self.fields['document_date'].required = False
            # Set initial value for document_date
            if not self.instance.pk:
                self.fields['document_date'].initial = timezone.now().date()
        
        if self.company_id and 'department_unit' in self.fields:
            self.fields['department_unit'].queryset = CompanyUnit.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('name')
            self.fields['department_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
    
    def clean_document_date(self):
        """Clean and provide default value for document_date"""
        date_value = self.cleaned_data.get('document_date')
        if not date_value:
            date_value = timezone.now().date()
        return date_value
    
    def clean_document_code(self):
        """Clean and provide default value for document_code"""
        code_value = self.cleaned_data.get('document_code')
        if not code_value:
            code_value = ''
        return code_value

    def clean(self):
        cleaned_data = super().clean()
        
        # Set default values for document_code and document_date if not provided
        if not cleaned_data.get('document_code'):
            cleaned_data['document_code'] = ''
        if not cleaned_data.get('document_date'):
            cleaned_data['document_date'] = timezone.now().date()
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(IssueConsignment, instance.company_id, "ICN")
        if not instance.document_date:
            instance.document_date = timezone.now().date()

        department_unit = self.cleaned_data.get('department_unit')
        if department_unit:
            instance.department_unit = department_unit
            instance.department_unit_code = department_unit.public_code
        else:
            instance.department_unit = None
            instance.department_unit_code = ''
        
        if commit:
            instance.save()
        return instance


class StocktakingBaseForm(forms.ModelForm):
    """Shared helpers for stocktaking documents."""

    unit_placeholder = UNIT_CHOICES[0][1]

    def __init__(self, *args, company_id=None, user=None, **kwargs):
        self.company_id = company_id or getattr(kwargs.get('instance'), 'company_id', None)
        self.user = user  # Store user for permission checks in subclasses
        self.date_widget = JalaliDateInput(attrs={'class': 'form-control'})
        self.datetime_widget = forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        super().__init__(*args, **kwargs)

        if 'document_date' in self.fields:
            self.fields['document_date'].widget = forms.HiddenInput()
            self.fields['document_date'].required = False
            if not getattr(self.instance, 'pk', None):
                self.fields['document_date'].initial = timezone.now().date()
        if 'inventory_snapshot_time' in self.fields:
            self.fields['inventory_snapshot_time'].widget = forms.HiddenInput()
            self.fields['inventory_snapshot_time'].required = False
            if not getattr(self.instance, 'pk', None):
                self.fields['inventory_snapshot_time'].initial = timezone.now()
        if 'approved_at' in self.fields:
            self.fields['approved_at'].widget = self.datetime_widget
            self.fields['approved_at'].required = False
            self.fields['approved_at'].input_formats = ['%Y-%m-%dT%H:%M']
        if 'document_code' in self.fields:
            self.fields['document_code'].widget = forms.HiddenInput()
            self.fields['document_code'].required = False
        for hidden_field in (
            'adjustment_metadata',
            'variance_document_ids',
            'variance_document_codes',
            'record_metadata',
        ):
            if hidden_field in self.fields:
                self.fields[hidden_field].widget = forms.HiddenInput()
                self.fields[hidden_field].required = False
        if 'notes' in self.fields:
            self.fields['notes'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        if 'quantity_adjusted' in self.fields:
            self.fields['quantity_adjusted'].widget.attrs.update({'readonly': 'readonly'})
            self.fields['quantity_adjusted'].required = False

        if self.company_id:
            self._filter_company_scoped_fields()
        self._set_unit_choices()
        self._set_warehouse_queryset()

    def _filter_company_scoped_fields(self):
        if 'item' in self.fields:
            self.fields['item'].queryset = Item.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
        if 'warehouse' in self.fields:
            self.fields['warehouse'].queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.name}"
            self.fields['warehouse'].empty_label = _("--- انتخاب کنید ---")
        if 'confirmed_by' in self.fields:
            from shared.models import User
            # Get users who have access to this company
            self.fields['confirmed_by'].queryset = User.objects.filter(
                company_accesses__company_id=self.company_id,
                company_accesses__is_enabled=1,
                is_active=True
            ).distinct()
            def confirmed_by_label(obj):
                full_name = obj.get_full_name()
                return f"{obj.username} - {full_name}" if full_name else obj.username
            self.fields['confirmed_by'].label_from_instance = confirmed_by_label
        if 'approver' in self.fields:
            from shared.models import User
            # Get users who have access to this company
            self.fields['approver'].queryset = User.objects.filter(
                company_accesses__company_id=self.company_id,
                company_accesses__is_enabled=1,
                is_active=True
            ).distinct()
            def approver_label(obj):
                full_name = obj.get_full_name()
                return f"{obj.username} - {full_name}" if full_name else obj.username
            self.fields['approver'].label_from_instance = approver_label

    def _resolve_item(self, candidate=None):
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if self.data and self.data.get('item'):
            try:
                return Item.objects.get(pk=self.data.get('item'), company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None

    def _get_item_allowed_units(self, item: Item):
        if not item:
            return []
        codes = []

        def add(code: str):
            if code and code not in codes:
                codes.append(code)

        add(item.default_unit)
        add(item.primary_unit)

        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)

        # If no units found, add default unit 'EA' as fallback
        if not codes:
            codes.append('EA')
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]

    def _get_item_allowed_warehouses(self, item: Item):
        if not item:
            return []
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]
        if not warehouses:
            warehouses = list(Warehouse.objects.filter(company_id=item.company_id, is_enabled=1))
        return [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]

    def _set_unit_choices(self):
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        item = self._resolve_item()
        placeholder = UNIT_CHOICES[0]
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            current = getattr(self.instance, 'unit', None)
            if current and current not in [code for code, _ in allowed]:
                label_map = dict(allowed)
                allowed.append((current, label_map.get(current, current)))
            unit_field.widget = forms.Select(attrs={'class': 'form-control'})
            unit_field.choices = [placeholder] + allowed
        else:
            unit_field.widget = forms.Select(attrs={'class': 'form-control'})
            unit_field.choices = [placeholder]

    def _set_warehouse_queryset(self):
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        item = self._resolve_item()
        if item:
            allowed_ids = [int(option['value']) for option in self._get_item_allowed_warehouses(item)]
            if allowed_ids:
                warehouse_field.queryset = Warehouse.objects.filter(pk__in=allowed_ids, is_enabled=1)
                return
        if self.company_id:
            warehouse_field.queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1)

    def _validate_unit(self, cleaned_data):
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        unit = cleaned_data.get('unit')
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        if unit and unit not in allowed:
            self.add_error('unit', _('Selected unit is not configured for this item.'))

    def _validate_warehouse(self, cleaned_data):
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        warehouse = cleaned_data.get('warehouse')
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    self.add_error('warehouse', _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.'))
            else:
                # No warehouses configured for this item - this is an error
                self.add_error('warehouse', _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.'))

    def clean(self):
        cleaned_data = super().clean()
        self._validate_unit(cleaned_data)
        self._validate_warehouse(cleaned_data)
        return cleaned_data


class StocktakingDeficitForm(StocktakingBaseForm):
    """Create/update form for stocktaking deficit adjustments."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = StocktakingDeficit
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
            'item',
            'warehouse',
            'unit',
            'quantity_expected',
            'quantity_counted',
            'quantity_adjusted',
            'valuation_method',
            'unit_cost',
            'total_cost',
            'reason_code',
            'investigation_reference',
            'adjustment_metadata',
        ]
        widgets = {
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_expected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_counted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_adjusted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'investigation_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        expected = cleaned_data.get('quantity_expected')
        counted = cleaned_data.get('quantity_counted')
        if expected is not None and counted is not None:
            adjusted = expected - counted
            if adjusted < 0:
                self.add_error('quantity_counted', _('Counted quantity cannot exceed expected balance for a deficit document.'))
            cleaned_data['quantity_adjusted'] = adjusted
        unit_cost = cleaned_data.get('unit_cost')
        if unit_cost not in (None, '') and cleaned_data.get('quantity_adjusted') not in (None, ''):
            try:
                cleaned_data['total_cost'] = cleaned_data['quantity_adjusted'] * unit_cost
            except TypeError:
                pass
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingDeficit, instance.company_id, "STD")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.item_code = instance.item.item_code if instance.item_id else instance.item_code
        instance.warehouse_code = instance.warehouse.public_code if instance.warehouse_id else instance.warehouse_code
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class StocktakingSurplusForm(StocktakingBaseForm):
    """Create/update form for stocktaking surplus adjustments."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = StocktakingSurplus
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
            'item',
            'warehouse',
            'unit',
            'quantity_expected',
            'quantity_counted',
            'quantity_adjusted',
            'valuation_method',
            'unit_cost',
            'total_cost',
            'reason_code',
            'investigation_reference',
            'adjustment_metadata',
        ]
        widgets = {
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_expected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_counted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'quantity_adjusted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'investigation_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        expected = cleaned_data.get('quantity_expected')
        counted = cleaned_data.get('quantity_counted')
        if expected is not None and counted is not None:
            adjusted = counted - expected
            if adjusted < 0:
                self.add_error('quantity_counted', _('Counted quantity cannot be less than expected for a surplus document.'))
            cleaned_data['quantity_adjusted'] = adjusted
        unit_cost = cleaned_data.get('unit_cost')
        if unit_cost not in (None, '') and cleaned_data.get('quantity_adjusted') not in (None, ''):
            try:
                cleaned_data['total_cost'] = cleaned_data['quantity_adjusted'] * unit_cost
            except TypeError:
                pass
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingSurplus, instance.company_id, "STS")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.item_code = instance.item.item_code if instance.item_id else instance.item_code
        instance.warehouse_code = instance.warehouse.public_code if instance.warehouse_id else instance.warehouse_code
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class StocktakingRecordForm(StocktakingBaseForm):
    """Create/update form for stocktaking records."""
    
    # Define approval status choices
    APPROVAL_STATUS_CHOICES = [
        ('pending', _('در انتظار تایید')),
        ('approved', _('تایید شده')),
        ('rejected', _('رد شده')),
    ]
    
    approval_status = forms.ChoiceField(
        choices=APPROVAL_STATUS_CHOICES,
        label=_('وضعیت تایید'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='pending',
    )

    class Meta:
        model = StocktakingRecord
        fields = [
            'document_code',
            'document_date',
            'stocktaking_session_id',
            'inventory_snapshot_time',
            'confirmed_by',
            'confirmation_notes',
            'variance_document_ids',
            'variance_document_codes',
            'final_inventory_value',
            'approver',  # Moved before approval_status
            'approval_status',
            'approved_at',
            'approver_notes',
            'record_metadata',
        ]
        widgets = {
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'confirmation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'final_inventory_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approver_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        if 'approval_status' in self.fields and not getattr(self.instance, 'pk', None):
            self.fields['approval_status'].initial = 'pending'
        
        # Hide approved_at field - it's automatically set when status is approved
        if 'approved_at' in self.fields:
            self.fields['approved_at'].widget = forms.HiddenInput()
            self.fields['approved_at'].required = False
        
        # Only the selected approver can change approval_status
        if self.instance.pk and 'approval_status' in self.fields:
            if self.user and self.instance.approver_id:
                if self.user.id != self.instance.approver_id:
                    # User is not the approver - make approval_status readonly
                    self.fields['approval_status'].widget.attrs['disabled'] = 'disabled'
                    self.fields['approval_status'].help_text = _('فقط تأییدکننده انتخاب شده می‌تواند وضعیت را تغییر دهد')
            elif not self.instance.approver_id:
                # No approver selected yet - anyone can change status
                pass
        for field_name in ('variance_document_ids', 'variance_document_codes', 'record_metadata'):
            if field_name in self.fields and not getattr(self.instance, field_name, None):
                default_value = [] if field_name != 'record_metadata' else {}
                self.fields[field_name].initial = default_value
        if 'document_date' in self.fields and not getattr(self.instance, 'pk', None):
            self.fields['document_date'].initial = timezone.now().date()
        if 'inventory_snapshot_time' in self.fields and not getattr(self.instance, 'pk', None):
            self.fields['inventory_snapshot_time'].initial = timezone.now()

    def clean(self):
        cleaned_data = super().clean()
        
        # Server-side permission check: only approver can change approval_status
        if self.instance.pk and 'approval_status' in cleaned_data:
            if self.user and self.instance.approver_id:
                if self.user.id != self.instance.approver_id:
                    # User is not the approver - restore original status
                    if self.instance.approval_status != cleaned_data['approval_status']:
                        self.add_error('approval_status', _('فقط تأییدکننده انتخاب شده می‌تواند وضعیت را تغییر دهد'))
                        cleaned_data['approval_status'] = self.instance.approval_status
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(StocktakingRecord, instance.company_id, "STR")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        if not instance.inventory_snapshot_time:
            instance.inventory_snapshot_time = timezone.now()
        if instance.confirmed_by_id:
            instance.confirmed_by_code = instance.confirmed_by.username
        if instance.approver_id:
            instance.approver_notes = instance.approver_notes or ''
        
        # Set approved_at when status changes to approved
        if instance.approval_status == 'approved' and not instance.approved_at:
            instance.approved_at = timezone.now()
        # Clear approved_at if status changes back to pending or rejected
        elif instance.approval_status in ('pending', 'rejected'):
            instance.approved_at = None
            
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssueLineSerialAssignmentForm(forms.Form):
    """Form for assigning serials to a specific issue line."""
    serials = forms.ModelMultipleChoiceField(
        queryset=ItemSerial.objects.none(),
        required=False,
        label=_('Serial Numbers'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'serial-checkboxes'}),
    )

    def __init__(self, line, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = line
        self.company_id = line.company_id

        if line.item and line.item.has_lot_tracking == 1:
            # Base queryset: same company, same item, same warehouse
            queryset = ItemSerial.objects.filter(
                company_id=self.company_id,
                item=line.item,
                current_warehouse=line.warehouse,
            )
            # Only show:
            # 1. AVAILABLE serials (not yet assigned to any issue)
            # 2. RESERVED serials that belong to THIS specific line (allow editing)
            # Exclude: ISSUED, CONSUMED, DAMAGED, RETURNED serials (already issued)
            # Exclude: RESERVED serials that belong to other lines
            line_class_name = line.__class__.__name__
            line_pk = line.pk
            
            # Available serials OR reserved serials for this specific line
            status_filter = (
                Q(current_status=ItemSerial.Status.AVAILABLE) |
                Q(
                    current_status=ItemSerial.Status.RESERVED,
                    current_document_type=line_class_name,
                    current_document_id=line_pk,
                )
            )
            # Exclude already-issued/consumed/damaged/returned serials
            excluded_statuses = [
                ItemSerial.Status.ISSUED,
                ItemSerial.Status.CONSUMED,
                ItemSerial.Status.DAMAGED,
                ItemSerial.Status.RETURNED,
            ]
            status_filter = status_filter & ~Q(current_status__in=excluded_statuses)
            
            self.fields['serials'].queryset = queryset.filter(status_filter).order_by('serial_code')
            self.initial['serials'] = line.serials.values_list('pk', flat=True)
            try:
                required = int(Decimal(line.quantity))
            except (InvalidOperation, TypeError):
                required = None
            if required is not None:
                self.fields['serials'].help_text = _('%(count)s serial(s) required for this line.') % {'count': required}
        else:
            self.fields['serials'].help_text = _('This item does not require serial tracking.')
            self.fields['serials'].widget = forms.HiddenInput()

    def clean_serials(self):
        serials = self.cleaned_data.get('serials')
        item = getattr(self.line, 'item', None)
        if not item or item.has_lot_tracking != 1:
            return ItemSerial.objects.none()

        try:
            required = int(Decimal(self.line.quantity))
        except (InvalidOperation, TypeError):
            raise forms.ValidationError(_('Quantity must be a whole number before assigning serials.'))

        if Decimal(self.line.quantity) != Decimal(required):
            raise forms.ValidationError(_('Quantity must be a whole number before assigning serials.'))

        selected = list(serials)
        if len(selected) != required:
            raise forms.ValidationError(
                _('You must select exactly %(count)s serial(s). Currently %(current)s selected.')
                % {'count': required, 'current': len(selected)}
            )

        invalid = [serial for serial in selected if serial.item_id != item.id]
        if invalid:
            raise forms.ValidationError(_('Selected serials do not belong to the requested item.'))

        return serials

    def save(self, user=None):
        line = self.line
        if line.item and line.item.has_lot_tracking == 1:
            previous_serial_ids = set(line.serials.values_list('id', flat=True))
            selected_serials = list(self.cleaned_data.get('serials'))
            line.serials.set(selected_serials)
            serial_service.sync_issue_line_serials(line, previous_serial_ids, user=user)
        else:
            line.serials.clear()
        return line


# ============================================================================
# Line Forms and Formsets (Multi-line support)
# ============================================================================

class IssueLineBaseForm(forms.ModelForm):
    """Base form for issue line items."""
    
    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        self._unit_factor = Decimal('1')
        self._entered_unit_value = None
        self._entered_quantity_value = None
        
        if self.company_id:
            if 'item' in self.fields:
                self.fields['item'].queryset = Item.objects.filter(
                    company_id=self.company_id, is_enabled=1
                ).order_by('name')
                self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
            
            if 'warehouse' in self.fields:
                self.fields['warehouse'].queryset = Warehouse.objects.filter(
                    company_id=self.company_id, is_enabled=1
                ).order_by('name')
                self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
        
        # Set unit choices - this must be done before restoring initial values
        self._set_unit_choices()
        
        # Restore entered values if editing
        if not self.is_bound and getattr(self.instance, 'pk', None):
            entry_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
            if 'unit' in self.fields and entry_unit:
                # Ensure the unit is in choices, if not add it
                unit_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in unit_choices]
                if entry_unit not in unit_codes:
                    # Add current unit to choices if not present
                    self.fields['unit'].choices = unit_choices + [(entry_unit, entry_unit)]
                # Django ChoiceField uses instance.field for display when editing
                # So we need to set instance.unit to the entered_unit for proper display
                if hasattr(self.instance, 'unit'):
                    # Store the original unit if we're changing it
                    if not hasattr(self.instance, '_original_unit'):
                        self.instance._original_unit = self.instance.unit
                    # Set unit to entered_unit for display purposes
                    self.instance.unit = entry_unit
                # Also set initial as backup
                self.initial['unit'] = entry_unit
            
            if 'quantity' in self.fields and getattr(self.instance, 'entered_quantity', None) is not None:
                self.initial['quantity'] = self.instance.entered_quantity
    
    def clean_item(self):
        """Clean item and update unit and warehouse choices."""
        item = self.cleaned_data.get('item')
        
        # Update unit choices immediately after item is cleaned
        # This ensures choices are set before unit validation
        if item:
            self._set_unit_choices(item=item)
            # Also update warehouse queryset based on allowed warehouses
            self._set_warehouse_queryset(item=item)
        
        return item
    
    def _get_item_allowed_warehouses(self, item: Item):
        """Get list of allowed warehouses for an item."""
        if not item:
            return []
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]
        # IMPORTANT: If no warehouses configured, this means the item CANNOT be received anywhere
        # Only return warehouses if explicitly configured
        # This enforces strict warehouse restrictions
        return [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]
    
    def _set_warehouse_queryset(self, item=None):
        """Set warehouse field queryset based on selected item's allowed warehouses."""
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        
        # If item not provided, try to resolve it
        if item is None:
            item = self._resolve_item()
        
        if item:
            allowed_ids = [int(option['value']) for option in self._get_item_allowed_warehouses(item)]
            if allowed_ids:
                # Only show allowed warehouses
                warehouse_field.queryset = Warehouse.objects.filter(pk__in=allowed_ids, is_enabled=1).order_by('name')
                return
            else:
                # No warehouses configured - show empty queryset (will show error in validation)
                warehouse_field.queryset = Warehouse.objects.none()
                return
        
        # Fallback: show all warehouses in company if no item selected
        if self.company_id:
            warehouse_field.queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
    
    def clean_warehouse(self):
        """Validate warehouse against item's allowed warehouses."""
        warehouse = self.cleaned_data.get('warehouse')
        item = self.cleaned_data.get('item')
        
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    raise forms.ValidationError(
                        _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.')
                    )
            else:
                # No warehouses configured for this item - this is an error
                raise forms.ValidationError(
                    _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.')
                )
        
        return warehouse
    
    def clean_unit(self):
        """Validate unit and update choices based on selected item."""
        unit = self.cleaned_data.get('unit')
        
        # Get item from cleaned_data (it should already be cleaned by clean_item)
        item = self.cleaned_data.get('item')
        
        # If no item is selected, don't validate unit (allow empty)
        if not item:
            return unit
        
        # Update unit choices again (in case clean_item wasn't called or item changed)
        self._set_unit_choices(item=item)
        
        # Now validate unit against allowed units
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        allowed.add(item.default_unit)
        
        # Also check current choices in the field
        unit_field = self.fields.get('unit')
        if unit_field:
            choice_values = {choice[0] for choice in unit_field.choices if choice[0]}
            allowed.update(choice_values)
        
        # If unit is provided and not in allowed list, raise error
        if unit and unit not in allowed:
            raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        
        return unit
    
    def _resolve_item(self, candidate=None):
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        # Check form data (POST)
        if self.data:
            item_key = None
            for key in self.data.keys():
                if key.endswith('-item'):
                    item_key = key
                    break
            if item_key:
                try:
                    item_id = self.data.get(item_key)
                    if item_id:
                        return Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        # Check instance (for edit mode)
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        # Check initial data (for new forms with pre-selected item)
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None
    
    def _get_item_allowed_units(self, item: Item):
        """Get list of allowed units for an item."""
        if not item:
            return []
        codes = []
        
        def add(code: str):
            if code and code not in codes:
                codes.append(code)
        
        # Add default and primary units (always add both, even if same or None)
        add(item.default_unit)
        add(item.primary_unit)
        
        # Add units from ItemUnit conversions
        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]
    
    def _set_unit_choices(self, item=None):
        """Set unit field choices based on selected item."""
        unit_field = self.fields.get('unit')
        if not unit_field:
            return
        placeholder = UNIT_CHOICES[0]
        
        # If item not provided, try to resolve it
        if item is None:
            item = self._resolve_item()
        
        # Get current unit from instance if editing
        current_unit = None
        if not self.is_bound and getattr(self.instance, 'pk', None):
            current_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
        
        # Also get unit from cleaned_data if available (for validation)
        if not current_unit and hasattr(self, 'cleaned_data'):
            current_unit = self.cleaned_data.get('unit')
        
        if item:
            allowed = [(row['value'], row['label']) for row in self._get_item_allowed_units(item)]
            allowed_codes = [code for code, _ in allowed]
            
            # Add current unit if editing and it's not in allowed list
            if current_unit and current_unit not in allowed_codes:
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                allowed.append((current_unit, label_map.get(current_unit, current_unit)))
            
            # If no units found, add default_unit as fallback
            if not allowed and item.default_unit:
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                allowed.append((item.default_unit, label_map.get(item.default_unit, item.default_unit)))
            
            unit_field.choices = [placeholder] + allowed
        else:
            # No item selected, but if editing and have current_unit, add it
            if current_unit:
                label_map = {value: str(label) for value, label in UNIT_CHOICES}
                unit_field.choices = [placeholder, (current_unit, label_map.get(current_unit, current_unit))]
            else:
                unit_field.choices = [placeholder]
    
    def _get_unit_factor(self, item: Item, unit_code: str) -> Decimal:
        """Calculate conversion factor from unit_code to item's default_unit."""
        default_unit = item.default_unit
        if not unit_code or unit_code == default_unit:
            return Decimal('1')
        
        graph = {}
        for conversion in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            from_qty = conversion.from_quantity
            to_qty = conversion.to_quantity
            if from_qty in (None, 0) or to_qty in (None, 0):
                continue
            graph.setdefault(conversion.from_unit, []).append((conversion.to_unit, to_qty / from_qty))
            graph.setdefault(conversion.to_unit, []).append((conversion.from_unit, from_qty / to_qty))
        
        visited = set()
        queue = deque([(unit_code, Decimal('1'))])
        while queue:
            unit, factor = queue.popleft()
            if unit == default_unit:
                return factor
            if unit in visited:
                continue
            visited.add(unit)
            for neighbor, ratio in graph.get(unit, []):
                queue.append((neighbor, factor * ratio))
        
        return Decimal('1')
    
    def _validate_unit(self, cleaned_data):
        """Validate unit and calculate conversion factor."""
        self._unit_factor = Decimal('1')
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        unit = cleaned_data.get('unit') or item.default_unit
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        allowed.add(item.default_unit)
        if unit not in allowed:
            self.add_error('unit', _('Selected unit is not configured for this item.'))
        factor = self._get_unit_factor(item, unit)
        self._unit_factor = factor
        self._entered_unit_value = unit
        cleaned_data['unit'] = item.default_unit
    
    def _normalize_quantity(self, cleaned_data):
        """Normalize quantity to base unit and save entered value."""
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        quantity = cleaned_data.get('quantity')
        if not item or quantity in (None, ''):
            return
        factor = getattr(self, '_unit_factor', Decimal('1'))
        if not isinstance(quantity, Decimal):
            try:
                quantity = Decimal(str(quantity))
            except (InvalidOperation, TypeError):
                return
        self._entered_quantity_value = quantity
        cleaned_data['quantity'] = quantity * factor
        cleaned_data['unit'] = item.default_unit
        self.instance.unit = item.default_unit
        self.instance.quantity = cleaned_data['quantity']
    
    def clean(self):
        """Validate and normalize form data."""
        cleaned_data = super().clean()
        
        # Check if form is empty (for inline formsets, empty forms should be skipped)
        item = cleaned_data.get('item')
        if not item:
            # If this is an empty form in a formset, mark all fields as empty
            # Django will skip it during save()
            return cleaned_data
        
        # Validate warehouse against item's allowed warehouses
        warehouse = cleaned_data.get('warehouse')
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    self.add_error('warehouse', _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.'))
            else:
                # No warehouses configured for this item - this is an error
                self.add_error('warehouse', _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.'))
        
        self._validate_unit(cleaned_data)
        self._normalize_quantity(cleaned_data)
        return cleaned_data
    
    def save(self, commit=True):
        """Save form instance with entered values."""
        instance = super().save(commit=False)
        
        # Save entered unit and quantity
        entered_unit = self._entered_unit_value or getattr(instance, 'entered_unit', '') or instance.unit
        instance.entered_unit = entered_unit
        if self._entered_quantity_value is not None:
            instance.entered_quantity = self._entered_quantity_value
        elif instance.entered_quantity is None:
            instance.entered_quantity = instance.quantity
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssuePermanentLineForm(IssueLineBaseForm):
    """Form for permanent issue line items."""
    
    destination_type = forms.ModelChoiceField(
        queryset=WorkLine.objects.none(),
        required=False,
        label=_('Work Line'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Select the work line that receives this issue.'),
    )
    
    class Meta:
        model = IssuePermanentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'destination_type', 'destination_id', 'destination_code', 'reason_code',
            'unit_price', 'currency', 'tax_amount', 'discount_amount', 'total_amount',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'destination_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination_code': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, company_id=company_id, **kwargs)
        
        # Set destination_type (WorkLine) queryset
        if self.company_id and 'destination_type' in self.fields:
            self.fields['destination_type'].queryset = WorkLine.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('warehouse__name', 'name')
            self.fields['destination_type'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name} ({obj.warehouse.name if obj.warehouse else ''})"
            self.fields['destination_type'].empty_label = _("--- انتخاب کنید ---")
            
            # If editing and instance has destination_type, try to find matching WorkLine
            if not self.is_bound and getattr(self.instance, 'pk', None):
                if self.instance.destination_type == 'work_line' and self.instance.destination_id:
                    # If destination_type is 'work_line', use destination_id
                    try:
                        work_line = WorkLine.objects.get(
                            company_id=self.company_id,
                            id=self.instance.destination_id
                        )
                        self.initial['destination_type'] = work_line.id
                    except WorkLine.DoesNotExist:
                        pass
                elif self.instance.destination_type and not self.instance.destination_id:
                    # Try to find WorkLine by code (for old data)
                    try:
                        work_line = WorkLine.objects.get(
                            company_id=self.company_id,
                            public_code=self.instance.destination_type
                        )
                        self.initial['destination_type'] = work_line.id
                    except WorkLine.DoesNotExist:
                        pass
    
    def clean_destination_type(self):
        """Validate destination_type (WorkLine)."""
        work_line = self.cleaned_data.get('destination_type')
        # Store work_line for later use in save()
        self._destination_work_line = work_line
        return work_line
    
    def save(self, commit=True):
        """Save with destination_type handling."""
        instance = super().save(commit=False)
        
        # Handle destination_type (WorkLine)
        work_line = getattr(self, '_destination_work_line', None)
        if work_line is None:
            # Try to get from cleaned_data if _destination_work_line not set
            work_line = self.cleaned_data.get('destination_type')
        
        if work_line and isinstance(work_line, WorkLine):
            instance.destination_type = 'work_line'
            instance.destination_id = work_line.id
            instance.destination_code = work_line.public_code
        else:
            # Set default empty value if not provided
            instance.destination_type = ''
            instance.destination_id = None
            instance.destination_code = ''
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssueConsumptionLineForm(IssueLineBaseForm):
    """Form for consumption issue line items."""
    
    destination_type_choice = forms.ChoiceField(
        choices=[
            ('', _('--- انتخاب کنید ---')),
            ('company_unit', _('واحد کاری (Company Unit)')),
            ('work_line', _('خط کاری (Work Line)')),
        ],
        required=False,
        label=_('نوع مقصد'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_destination_type_choice'}),
        help_text=_('ابتدا نوع مقصد را انتخاب کنید.'),
    )
    
    destination_company_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('واحد کاری'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_destination_company_unit'}),
    )
    
    destination_work_line = forms.ModelChoiceField(
        queryset=WorkLine.objects.none(),
        required=False,
        label=_('خط کاری'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_destination_work_line'}),
    )
    
    work_line = forms.ModelChoiceField(
        queryset=WorkLine.objects.none(),
        required=False,
        label=_('Work Line'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = IssueConsumptionLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'destination_type_choice', 'destination_company_unit', 'destination_work_line',  # Destination fields
            'consumption_type', 'work_line',  # consumption_type is hidden, managed by destination_type_choice
            'reference_document_type', 'reference_document_id', 'reference_document_code',
            'production_transfer_id', 'production_transfer_code',
            'unit_cost', 'total_cost', 'cost_center_code',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'consumption_type': forms.HiddenInput(),  # Hidden, set automatically based on destination_type_choice
            'work_line': forms.Select(attrs={'class': 'form-control'}),
            'reference_document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_document_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference_document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'production_transfer_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'production_transfer_code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'cost_center_code': forms.HiddenInput(),  # Hidden, used internally for company_unit storage
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, company_id=company_id, **kwargs)
        # Update querysets if company_id is available
        self._update_querysets_after_company_id()
    
    def _update_querysets_after_company_id(self):
        """Update querysets after company_id is set (called from BaseLineFormSet)."""
        if not self.company_id:
            return
        
        # Set work_line queryset
        if 'work_line' in self.fields:
            self.fields['work_line'].queryset = WorkLine.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('warehouse__name', 'name')
            self.fields['work_line'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name} ({obj.warehouse.name if obj.warehouse else ''})"
        
        # Set destination_company_unit queryset
        if 'destination_company_unit' in self.fields:
            self.fields['destination_company_unit'].queryset = CompanyUnit.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).order_by('name')
            self.fields['destination_company_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            self.fields['destination_company_unit'].empty_label = _("--- انتخاب کنید ---")
        
        # Set destination_work_line queryset (initially all work lines, will be filtered by JavaScript based on warehouse)
        if 'destination_work_line' in self.fields:
            self.fields['destination_work_line'].queryset = WorkLine.objects.filter(
                company_id=self.company_id, is_enabled=1
            ).select_related('warehouse').order_by('warehouse__name', 'name')
            self.fields['destination_work_line'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name} ({obj.warehouse.name if obj.warehouse else ''})"
            self.fields['destination_work_line'].empty_label = _("--- انتخاب کنید ---")
        
        # If editing, set initial values based on consumption_type
        if not self.is_bound and getattr(self.instance, 'pk', None):
            dest_type = getattr(self.instance, 'consumption_type', None)
            # Set consumption_type initial value (hidden field)
            if dest_type:
                self.initial['consumption_type'] = dest_type
            
            if dest_type == 'company_unit':
                # Try to get company unit from cost_center_code (where we stored it)
                if hasattr(self.instance, 'cost_center_code') and self.instance.cost_center_code:
                    try:
                        unit = CompanyUnit.objects.get(
                            company_id=self.company_id,
                            public_code=self.instance.cost_center_code
                        )
                        self.initial['destination_type_choice'] = 'company_unit'
                        self.initial['destination_company_unit'] = unit.id
                        # Show the company unit field container (JavaScript will handle display)
                    except CompanyUnit.DoesNotExist:
                        pass
            elif dest_type == 'work_line' and self.instance.work_line:
                self.initial['destination_type_choice'] = 'work_line'
                self.initial['destination_work_line'] = self.instance.work_line.id
                # Show the work line field container (JavaScript will handle display)
    
    def clean(self):
        """Validate destination selection."""
        cleaned_data = super().clean()
        dest_type_choice = cleaned_data.get('destination_type_choice')
        dest_company_unit = cleaned_data.get('destination_company_unit')
        dest_work_line = cleaned_data.get('destination_work_line')
        
        # Check if item is selected (required for validation)
        item = cleaned_data.get('item')
        if not item:
            # If no item, skip destination validation (form will be skipped anyway)
            return cleaned_data
        
        # Require destination_type_choice to be selected
        if not dest_type_choice:
            self.add_error('destination_type_choice', _('Please select a destination type.'))
            return cleaned_data
        
        # Validate based on selected destination type
        if dest_type_choice == 'company_unit':
            if not dest_company_unit:
                self.add_error('destination_company_unit', _('Please select a company unit.'))
        elif dest_type_choice == 'work_line':
            if not dest_work_line:
                self.add_error('destination_work_line', _('Please select a work line.'))
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save with destination handling."""
        instance = super().save(commit=False)
        
        dest_type_choice = self.cleaned_data.get('destination_type_choice')
        dest_company_unit = self.cleaned_data.get('destination_company_unit')
        dest_work_line = self.cleaned_data.get('destination_work_line')
        
        # Set destination based on choice
        if dest_type_choice == 'company_unit' and dest_company_unit:
            instance.consumption_type = 'company_unit'
            # For company_unit, we store the unit ID in a way we can retrieve it later
            # Since IssueConsumptionLine doesn't have destination_id, we can store it in cost_center_code as temporary solution
            # Or we need to check if model has these fields
            instance.work_line = None
            # Store company unit code in cost_center_code for now (or we could add destination fields to model)
            if hasattr(instance, 'cost_center_code'):
                instance.cost_center_code = dest_company_unit.public_code
        elif dest_type_choice == 'work_line' and dest_work_line:
            instance.consumption_type = 'work_line'
            instance.work_line = dest_work_line
            if hasattr(instance, 'cost_center_code') and instance.cost_center_code:
                # Clear cost_center_code if it was used for company_unit
                try:
                    CompanyUnit.objects.get(public_code=instance.cost_center_code)
                    instance.cost_center_code = ''
                except CompanyUnit.DoesNotExist:
                    pass
        else:
            # If no choice made, this should have been caught by validation
            # But if we reach here, it means validation didn't catch it
            # This should not happen, but we need to handle it
            # Don't save if consumption_type is not set (validation should prevent this)
            if not getattr(instance, 'consumption_type', None) and not instance.pk:
                # This is a new instance without consumption_type - validation should have caught this
                # We'll let the database constraint catch it if validation didn't
                pass
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssueConsignmentLineForm(IssueLineBaseForm):
    """Form for consignment issue line items."""
    
    consignment_receipt = forms.ModelChoiceField(
        queryset=ReceiptConsignment.objects.none(),
        required=False,
        label=_('Consignment Receipt'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which consignment receipt this issue is related to.'),
    )
    
    destination_type = forms.ModelChoiceField(
        queryset=WorkLine.objects.none(),
        required=False,
        label=_('Work Line'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Select the work line that receives this issue.'),
    )
    
    class Meta:
        model = IssueConsignmentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity',
            'consignment_receipt',
            'destination_type', 'destination_id', 'destination_code', 'reason_code',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'destination_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination_code': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, company_id=company_id, **kwargs)
        
        if self.company_id:
            if 'consignment_receipt' in self.fields:
                self.fields['consignment_receipt'].queryset = ReceiptConsignment.objects.filter(
                    company_id=self.company_id
                ).order_by('-document_date', 'document_code')
                self.fields['consignment_receipt'].label_from_instance = lambda obj: f"{obj.document_code}"
            
            # Set destination_type (WorkLine) queryset
            if 'destination_type' in self.fields:
                self.fields['destination_type'].queryset = WorkLine.objects.filter(
                    company_id=self.company_id, is_enabled=1
                ).order_by('warehouse__name', 'name')
                self.fields['destination_type'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name} ({obj.warehouse.name if obj.warehouse else ''})"
                self.fields['destination_type'].empty_label = _("--- انتخاب کنید ---")
                
                # If editing and instance has destination_type, try to find matching WorkLine
                if not self.is_bound and getattr(self.instance, 'pk', None):
                    if self.instance.destination_type == 'work_line' and self.instance.destination_id:
                        try:
                            work_line = WorkLine.objects.get(
                                company_id=self.company_id,
                                id=self.instance.destination_id
                            )
                            self.initial['destination_type'] = work_line.id
                        except WorkLine.DoesNotExist:
                            pass
                    elif self.instance.destination_type and not self.instance.destination_id:
                        try:
                            work_line = WorkLine.objects.get(
                                company_id=self.company_id,
                                public_code=self.instance.destination_type
                            )
                            self.initial['destination_type'] = work_line.id
                        except WorkLine.DoesNotExist:
                            pass
    
    def clean_destination_type(self):
        """Validate destination_type (WorkLine)."""
        work_line = self.cleaned_data.get('destination_type')
        self._destination_work_line = work_line
        return work_line
    
    def save(self, commit=True):
        """Save with destination_type handling."""
        instance = super().save(commit=False)
        
        # Handle destination_type (WorkLine)
        work_line = getattr(self, '_destination_work_line', None) or self.cleaned_data.get('destination_type')
        
        if work_line and isinstance(work_line, WorkLine):
            instance.destination_type = 'work_line'
            instance.destination_id = work_line.id
            instance.destination_code = work_line.public_code
        else:
            instance.destination_type = ''
            instance.destination_id = None
            instance.destination_code = ''
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ReceiptLineBaseForm(forms.ModelForm):
    """Base form for receipt line items."""
    
    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    entered_price_unit = forms.CharField(
        label=_('Entered Price Unit'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Optional: unit for price (e.g., BOX)')}),
        help_text=_("Unit for entered_unit_price (e.g., BOX, CARTON). If empty, same as entered_unit."),
    )
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or getattr(self.instance, 'company_id', None)
        self._unit_factor = Decimal('1')
        self._entered_unit_value = None
        self._entered_quantity_value = None
        self._entered_unit_price_value = None
        
        if self.company_id:
            if 'item' in self.fields:
                self.fields['item'].queryset = Item.objects.filter(
                    company_id=self.company_id, is_enabled=1
                ).order_by('name')
                self.fields['item'].label_from_instance = lambda obj: f"{obj.name} · {obj.item_code}"
            
            if 'warehouse' in self.fields:
                self.fields['warehouse'].queryset = Warehouse.objects.filter(
                    company_id=self.company_id, is_enabled=1
                ).order_by('name')
                self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            
            if 'supplier' in self.fields:
                self.fields['supplier'].queryset = Supplier.objects.filter(
                    company_id=self.company_id, is_enabled=1
                ).order_by('name')
                self.fields['supplier'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
        
        # Set unit choices - use all UNIT_CHOICES initially (will be filtered by JavaScript)
        if 'unit' in self.fields:
            self.fields['unit'].choices = UNIT_CHOICES
        
        # Ensure entered_price_unit is a CharField, not ChoiceField
        if 'entered_price_unit' in self.fields:
            self.fields['entered_price_unit'].required = False
            # Make sure it's not a ChoiceField (Django might auto-convert it)
            if isinstance(self.fields['entered_price_unit'], forms.ChoiceField):
                # Convert to CharField
                self.fields['entered_price_unit'] = forms.CharField(
                    label=self.fields['entered_price_unit'].label,
                    required=False,
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Optional: unit for price (e.g., BOX)')}),
                    help_text=_("Unit for entered_unit_price (e.g., BOX, CARTON). If empty, same as entered_unit."),
                )
        
        # Restore entered values if editing
        if not self.is_bound and getattr(self.instance, 'pk', None):
            # Get item first to set unit choices properly
            item = getattr(self.instance, 'item', None)
            if item and 'unit' in self.fields:
                # Set unit choices based on item
                self._set_unit_choices_for_item(item)
            
            # Get unit value from entered_unit or unit (prioritize entered_unit for display)
            entry_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
            if 'unit' in self.fields and entry_unit:
                # Ensure the unit is in choices, if not add it
                unit_choices = list(self.fields['unit'].choices)
                unit_codes = [code for code, _ in unit_choices]
                if entry_unit not in unit_codes:
                    # Add current unit to choices if not present
                    self.fields['unit'].choices = unit_choices + [(entry_unit, entry_unit)]
                
                # Django ChoiceField uses instance.field for display when editing
                # So we need to set instance.unit to the entered_unit for proper display
                if hasattr(self.instance, 'unit'):
                    # Store the original unit if we're changing it
                    if not hasattr(self.instance, '_original_unit'):
                        self.instance._original_unit = self.instance.unit
                    # Set unit to entered_unit for display purposes
                    self.instance.unit = entry_unit
                
                # Also set initial as backup
                self.initial['unit'] = entry_unit
            
            if 'quantity' in self.fields and getattr(self.instance, 'entered_quantity', None) is not None:
                self.initial['quantity'] = self.instance.entered_quantity
            entry_price = getattr(self.instance, 'entered_unit_price', None)
            if 'unit_price' in self.fields and entry_price is not None:
                self.initial['unit_price'] = entry_price
            if 'unit_price_estimate' in self.fields and entry_price is not None:
                self.initial['unit_price_estimate'] = entry_price
            if 'entered_price_unit' in self.fields:
                entered_price_unit = getattr(self.instance, 'entered_price_unit', '') or getattr(self.instance, 'entered_unit', '')
                if entered_price_unit:
                    self.initial['entered_price_unit'] = entered_price_unit
    
    def _set_unit_choices_for_item(self, item):
        """Set unit choices based on item."""
        if not item or 'unit' not in self.fields:
            return
        
        placeholder = UNIT_CHOICES[0]
        allowed = self._get_item_allowed_units(item)
        if allowed:
            unit_choices = [placeholder] + [(row['value'], row['label']) for row in allowed]
        else:
            unit_choices = [placeholder]
        
        # Ensure current unit is in choices
        current_unit = getattr(self.instance, 'unit', '') or getattr(self.instance, 'entered_unit', '')
        if current_unit:
            unit_codes = [code for code, _ in unit_choices]
            if current_unit not in unit_codes:
                unit_choices.append((current_unit, current_unit))
        
        self.fields['unit'].choices = unit_choices
    
    def clean_item(self):
        """Clean item and update unit and warehouse choices."""
        item = self.cleaned_data.get('item')
        
        # Update warehouse queryset based on allowed warehouses
        if item:
            self._set_warehouse_queryset(item=item)
        
        return item
    
    def clean_warehouse(self):
        """Validate warehouse against item's allowed warehouses."""
        warehouse = self.cleaned_data.get('warehouse')
        item = self.cleaned_data.get('item')
        
        if warehouse and item:
            allowed_ids = {int(option['value']) for option in self._get_item_allowed_warehouses(item)}
            # If item has allowed warehouses configured, warehouse must be in that list
            # If no warehouses configured, item cannot be received (error)
            if allowed_ids:
                if warehouse.id not in allowed_ids:
                    raise forms.ValidationError(
                        _('انبار انتخاب شده برای این کالا مجاز نیست. لطفاً یکی از انبارهای مجاز را انتخاب کنید.')
                    )
            else:
                # No warehouses configured for this item - this is an error
                raise forms.ValidationError(
                    _('این کالا هیچ انبار مجازی ندارد. لطفاً ابتدا در تعریف کالا، حداقل یک انبار مجاز را انتخاب کنید.')
                )
        
        return warehouse
    
    def clean_unit(self):
        """Validate unit."""
        unit = self.cleaned_data.get('unit')
        item = self._resolve_item(self.cleaned_data.get('item'))
        if item:
            allowed = {row['value'] for row in self._get_item_allowed_units(item)}
            if unit and unit not in allowed:
                raise forms.ValidationError(_('Selected unit is not configured for this item.'))
        return unit
    
    def _get_item_allowed_warehouses(self, item: Item):
        """Get list of allowed warehouses for an item."""
        if not item:
            return []
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]
        # IMPORTANT: If no warehouses configured, this means the item CANNOT be received anywhere
        # Only return warehouses if explicitly configured
        # This enforces strict warehouse restrictions
        return [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]
    
    def _set_warehouse_queryset(self, item=None):
        """Set warehouse field queryset based on selected item's allowed warehouses."""
        warehouse_field = self.fields.get('warehouse')
        if not warehouse_field:
            return
        
        # If item not provided, try to resolve it
        if item is None:
            item = self._resolve_item()
        
        if item:
            allowed_ids = [int(option['value']) for option in self._get_item_allowed_warehouses(item)]
            if allowed_ids:
                # Only show allowed warehouses
                warehouse_field.queryset = Warehouse.objects.filter(pk__in=allowed_ids, is_enabled=1).order_by('name')
                return
            else:
                # No warehouses configured - show empty queryset (will show error in validation)
                warehouse_field.queryset = Warehouse.objects.none()
                return
        
        # Fallback: show all warehouses in company if no item selected
        if self.company_id:
            warehouse_field.queryset = Warehouse.objects.filter(company_id=self.company_id, is_enabled=1).order_by('name')
    
    def _resolve_item(self, candidate=None):
        """Resolve item from form data or instance."""
        if isinstance(candidate, Item):
            return candidate
        if candidate:
            try:
                return Item.objects.get(pk=candidate, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        # Check form data (POST)
        if self.data:
            item_key = None
            for key in self.data.keys():
                if key.endswith('-item'):
                    item_key = key
                    break
            if item_key:
                try:
                    item_id = self.data.get(item_key)
                    if item_id:
                        return Item.objects.get(pk=item_id, company_id=self.company_id)
                except (Item.DoesNotExist, ValueError, TypeError):
                    pass
        # Check instance (for edit mode)
        if getattr(self.instance, 'item_id', None):
            return self.instance.item
        # Check initial data (for new forms with pre-selected item)
        initial_item = self.initial.get('item')
        if isinstance(initial_item, Item):
            return initial_item
        if initial_item:
            try:
                return Item.objects.get(pk=initial_item, company_id=self.company_id)
            except (Item.DoesNotExist, ValueError, TypeError):
                pass
        return None
    
    def _get_item_allowed_units(self, item: Item):
        """Get list of allowed units for an item."""
        if not item:
            return []
        codes = []
        
        def add(code: str):
            if code and code not in codes:
                codes.append(code)
        
        # Add default and primary units (always add both, even if same or None)
        add(item.default_unit)
        add(item.primary_unit)
        
        # Add units from ItemUnit conversions
        for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)
        
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        return [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]
    
    def _get_unit_factor(self, item: Item, unit_code: str) -> Decimal:
        """Calculate conversion factor from unit_code to item's default_unit."""
        default_unit = item.default_unit
        if not unit_code or unit_code == default_unit:
            return Decimal('1')
        
        graph = {}
        for conversion in ItemUnit.objects.filter(item=item, company_id=item.company_id):
            from_qty = conversion.from_quantity
            to_qty = conversion.to_quantity
            if from_qty in (None, 0) or to_qty in (None, 0):
                continue
            graph.setdefault(conversion.from_unit, []).append((conversion.to_unit, to_qty / from_qty))
            graph.setdefault(conversion.to_unit, []).append((conversion.from_unit, from_qty / to_qty))
        
        visited = set()
        queue = deque([(unit_code, Decimal('1'))])
        while queue:
            unit, factor = queue.popleft()
            if unit == default_unit:
                return factor
            if unit in visited:
                continue
            visited.add(unit)
            for neighbor, ratio in graph.get(unit, []):
                queue.append((neighbor, factor * ratio))
        
        return Decimal('1')
    
    def _validate_unit(self, cleaned_data):
        """Validate unit and calculate conversion factor."""
        self._unit_factor = Decimal('1')
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        unit = cleaned_data.get('unit') or item.default_unit
        allowed = {row['value'] for row in self._get_item_allowed_units(item)}
        allowed.add(item.default_unit)
        if unit not in allowed:
            self.add_error('unit', _('Selected unit is not configured for this item.'))
        factor = self._get_unit_factor(item, unit)
        self._unit_factor = factor
        self._entered_unit_value = unit
        cleaned_data['unit'] = item.default_unit
    
    def _normalize_quantity(self, cleaned_data):
        """Normalize quantity to base unit and save entered value."""
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        quantity = cleaned_data.get('quantity')
        if not item or quantity in (None, ''):
            return
        factor = getattr(self, '_unit_factor', Decimal('1'))
        if not isinstance(quantity, Decimal):
            try:
                quantity = Decimal(str(quantity))
            except (InvalidOperation, TypeError):
                return
        
        self._entered_quantity_value = quantity
        cleaned_data['quantity'] = quantity * factor
        cleaned_data['unit'] = item.default_unit
        self.instance.unit = item.default_unit
        self.instance.quantity = cleaned_data['quantity']
    
    def _normalize_price(self, cleaned_data):
        """Normalize price to base unit and save entered value.
        
        Logic:
        - entered_unit_price: Price as entered by user
        - entered_price_unit: Unit for entered_unit_price (if empty, same as entered_unit)
        - unit_price: Price normalized to item's default_unit (EA)
        
        If entered_price_unit is provided, use it for price normalization.
        Otherwise, assume price is for the same unit as quantity (entered_unit).
        """
        if 'unit' not in self.fields:
            return
        item = self._resolve_item(cleaned_data.get('item'))
        if not item:
            return
        
        # Get the entered unit for quantity (before normalization)
        entered_unit = getattr(self, '_entered_unit_value', None) or cleaned_data.get('unit')
        
        # Get the entered unit for price (if specified, otherwise use entered_unit)
        entered_price_unit = cleaned_data.get('entered_price_unit', '').strip()
        if not entered_price_unit:
            entered_price_unit = entered_unit
        
        # Calculate price factor: convert from entered_price_unit to default_unit
        # IMPORTANT: For price, we need the INVERSE of the quantity factor
        # Quantity: 1 BOX = 1000 EA, so factor = 1000 (multiply BOX by 1000 to get EA)
        # Price: 100000 per BOX -> ? per EA
        # If 1 BOX = 1000 EA, then price per EA = price per BOX / 1000
        # So we need to DIVIDE by the quantity factor, not multiply
        if entered_price_unit and entered_price_unit != item.default_unit:
            quantity_factor = self._get_unit_factor(item, entered_price_unit)
            # For price conversion, we need the inverse: price per larger unit -> price per smaller unit
            # Example: 100000 per BOX, 1 BOX = 1000 EA -> 100000 / 1000 = 100 per EA
            price_factor = Decimal('1') / quantity_factor if quantity_factor != Decimal('0') else Decimal('1')
        else:
            price_factor = Decimal('1')
        
        # Handle unit_price
        if 'unit_price' in self.fields:
            unit_price = cleaned_data.get('unit_price')
            if unit_price not in (None, ''):
                if not isinstance(unit_price, Decimal):
                    try:
                        unit_price = Decimal(str(unit_price))
                    except (InvalidOperation, TypeError):
                        return
                
                # Save entered price (as entered by user, for entered_price_unit)
                self._entered_unit_price_value = unit_price
                
                # Convert to base unit price: price per entered_price_unit -> price per default_unit
                # Example: 100000 per BOX -> 100 per EA (if 1 BOX = 1000 EA, so divide by 1000)
                cleaned_data['unit_price'] = unit_price * price_factor
        
        # Handle unit_price_estimate
        if 'unit_price_estimate' in self.fields:
            unit_price_estimate = cleaned_data.get('unit_price_estimate')
            if unit_price_estimate not in (None, ''):
                if not isinstance(unit_price_estimate, Decimal):
                    try:
                        unit_price_estimate = Decimal(str(unit_price_estimate))
                    except (InvalidOperation, TypeError):
                        return
                # Save entered price (same as unit_price for estimate)
                if self._entered_unit_price_value is None:
                    self._entered_unit_price_value = unit_price_estimate
                # Convert to base unit price using price_factor (inverse of quantity factor)
                cleaned_data['unit_price_estimate'] = unit_price_estimate * price_factor
    
    def clean_entered_price_unit(self):
        """Validate entered_price_unit."""
        entered_price_unit = self.cleaned_data.get('entered_price_unit', '').strip()
        # If provided, validate it's a valid unit for the item
        if entered_price_unit:
            item = self._resolve_item(self.cleaned_data.get('item'))
            if item:
                allowed_units = {row['value'] for row in self._get_item_allowed_units(item)}
                if entered_price_unit not in allowed_units:
                    # Don't raise error, just warn - user might enter a unit that's not in the list
                    # But we'll use it anyway for price normalization
                    pass
        return entered_price_unit
    
    def clean(self):
        """Validate and normalize form data."""
        cleaned_data = super().clean()
        self._validate_unit(cleaned_data)
        self._normalize_quantity(cleaned_data)
        self._normalize_price(cleaned_data)
        return cleaned_data
    
    def save(self, commit=True):
        """Save form instance with entered values."""
        instance = super().save(commit=False)
        
        # Save entered unit, quantity, and price
        entered_unit = self._entered_unit_value or getattr(instance, 'entered_unit', '') or instance.unit
        instance.entered_unit = entered_unit
        if self._entered_quantity_value is not None:
            instance.entered_quantity = self._entered_quantity_value
        elif instance.entered_quantity is None:
            instance.entered_quantity = instance.quantity
        if self._entered_unit_price_value is not None:
            instance.entered_unit_price = self._entered_unit_price_value
            # Save entered_price_unit if provided, otherwise use entered_unit
            entered_price_unit = self.cleaned_data.get('entered_price_unit', '').strip()
            if not entered_price_unit:
                entered_price_unit = entered_unit
            instance.entered_price_unit = entered_price_unit
        elif hasattr(instance, 'entered_price_unit') and not instance.entered_price_unit:
            # If no price entered, set entered_price_unit to entered_unit for consistency
            instance.entered_price_unit = entered_unit
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ReceiptPermanentLineForm(ReceiptLineBaseForm):
    """Form for permanent receipt line items."""
    
    class Meta:
        model = ReceiptPermanentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity', 'entered_unit_price', 'entered_price_unit',
            'supplier',
            'unit_price', 'currency', 'tax_amount', 'discount_amount', 'total_amount',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_price_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Optional: unit for price (e.g., BOX)')}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ReceiptConsignmentLineForm(ReceiptLineBaseForm):
    """Form for consignment receipt line items."""
    
    class Meta:
        model = ReceiptConsignmentLine
        fields = [
            'item', 'warehouse', 'unit', 'quantity',
            'entered_unit', 'entered_quantity', 'entered_unit_price', 'entered_price_unit',
            'supplier',
            'unit_price_estimate', 'currency',
            'line_notes',
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'entered_price_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Optional: unit for price (e.g., BOX)')}),
            'unit_price_estimate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'line_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# Base FormSet classes for company_id handling
class BaseLineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, company_id=None, **kwargs):
        self.company_id = company_id
        super().__init__(*args, **kwargs)
        # Pass company_id to all forms in the formset and update querysets
        for form in self.forms:
            form.company_id = company_id
            # Update querysets after company_id is set
            if hasattr(form, '_update_querysets_after_company_id'):
                form._update_querysets_after_company_id()
    
    def clean(self):
        """Validate that at least one line has an item."""
        if any(self.errors):
            return
        
        # Count non-empty forms (forms with an item)
        non_empty_forms = 0
        for form in self.forms:
            # Check if form is marked for deletion
            if form.cleaned_data.get('DELETE', False):
                continue
            # Check if form has an item
            if form.cleaned_data and form.cleaned_data.get('item'):
                non_empty_forms += 1
        
        # If min_num is set and we don't have enough non-empty forms, raise validation error
        # Django's validate_min might not catch empty forms correctly, so we check manually
        min_num = getattr(self, 'min_num', 0)
        if min_num and non_empty_forms < min_num:
            raise forms.ValidationError(
                _('Please add at least %(min_num)d line(s) with an item.') % {'min_num': min_num}
            )


# Create formsets
IssuePermanentLineFormSet = inlineformset_factory(
    IssuePermanent,
    IssuePermanentLine,
    form=IssuePermanentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

IssueConsumptionLineFormSet = inlineformset_factory(
    IssueConsumption,
    IssueConsumptionLine,
    form=IssueConsumptionLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

IssueConsignmentLineFormSet = inlineformset_factory(
    IssueConsignment,
    IssueConsignmentLine,
    form=IssueConsignmentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

ReceiptPermanentLineFormSet = inlineformset_factory(
    ReceiptPermanent,
    ReceiptPermanentLine,
    form=ReceiptPermanentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

ReceiptConsignmentLineFormSet = inlineformset_factory(
    ReceiptConsignment,
    ReceiptConsignmentLine,
    form=ReceiptConsignmentLineForm,
    formset=BaseLineFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

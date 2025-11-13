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
    Warehouse,
    WorkLine,
    Item,
    Supplier,
    SupplierCategory,
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
)
from shared.models import CompanyUnit, Person

User = get_user_model()

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
            'needed_by_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
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
            'needed_by_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
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
        fields = ['public_code', 'name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'public_code': _('Code'),
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
        fields = ['public_code', 'name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'public_code': _('Code'),
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
        fields = ['category', 'public_code', 'name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'category': _('Item Category'),
            'public_code': _('Code'),
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
        fields = ['public_code', 'name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled']
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '6'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'public_code': _('Code'),
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
            'public_code', 'name', 'name_en', 'phone_number', 'mobile_number',
            'email', 'address', 'city', 'state', 'country', 'tax_id',
            'description', 'sort_order', 'is_enabled'
        ]
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '6'}),
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
            'public_code': _('Code'),
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
    """Form for creating/editing supplier categories."""
    
    is_primary = forms.BooleanField(
        required=False,
        label=_('دستهٔ اصلی'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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

        self.fields['supplier'].label_from_instance = lambda obj: obj.name
        self.fields['category'].label_from_instance = lambda obj: obj.name

    def clean(self):
        cleaned_data = super().clean()
        supplier = cleaned_data.get('supplier')
        category = cleaned_data.get('category')

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

    date_widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
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

        if not self.is_bound and getattr(self.instance, 'pk', None):
            entry_unit = getattr(self.instance, 'entered_unit', '') or getattr(self.instance, 'unit', '')
            if 'unit' in self.fields and entry_unit:
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

        if self.company_id:
            self._filter_company_scoped_fields()
        self._set_unit_choices()

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

class ReceiptPermanentForm(ReceiptBaseForm):
    """Create/update form for permanent receipts."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
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
            'item',
            'warehouse',
            'unit',
            'quantity',
            'supplier',
            'unit_price',
            'currency',
            'requires_temporary_receipt',
            'temporary_receipt',
            'purchase_request',
            'warehouse_request',
            'tax_amount',
            'discount_amount',
            'total_amount',
        ]
        widgets = {
            'document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
                        'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }
        labels = {
            'document_code': _('Document Code'),
            'document_date': _('Document Date'),
            'item': _('Item'),
            'warehouse': _('Warehouse'),
            'quantity': _('Quantity'),
            'supplier': _('Supplier'),
            'unit_price': _('Unit Price'),
            'currency': _('Currency'),
            'temporary_receipt': _('Temporary Receipt'),
            'purchase_request': _('Purchase Request'),
            'warehouse_request': _('Warehouse Request'),
            'tax_amount': _('Tax Amount'),
            'discount_amount': _('Discount Amount'),
            'total_amount': _('Total Amount'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['requires_temporary_receipt'].initial = bool(self.instance.requires_temporary_receipt)

    def clean(self):
        cleaned_data = super().clean()
        if self.company_id:
            self._clean_company_match(cleaned_data, 'item', _('item'))
            self._clean_company_match(cleaned_data, 'warehouse', _('warehouse'))
            if cleaned_data.get('supplier'):
                self._clean_company_match(cleaned_data, 'supplier', _('supplier'))
            if cleaned_data.get('temporary_receipt'):
                self._clean_company_match(cleaned_data, 'temporary_receipt', _('temporary receipt'))
            if cleaned_data.get('purchase_request'):
                self._clean_company_match(cleaned_data, 'purchase_request', _('purchase request'))
            if cleaned_data.get('warehouse_request'):
                self._clean_company_match(cleaned_data, 'warehouse_request', _('warehouse request'))
                warehouse_request = cleaned_data.get('warehouse_request')
                item = cleaned_data.get('item')
                warehouse = cleaned_data.get('warehouse')
                if warehouse_request and item and warehouse_request.item_id != item.id:
                    self.add_error('warehouse_request', _('Selected warehouse request is for a different item.'))
                if warehouse_request and warehouse and warehouse_request.warehouse_id != warehouse.id:
                    self.add_error('warehouse_request', _('Selected warehouse request is for a different warehouse.'))

        factor = getattr(self, '_unit_factor', Decimal('1'))
        unit_price = cleaned_data.get('unit_price')
        if unit_price not in (None, '') and factor not in (None, Decimal('0')):
            try:
                if not isinstance(unit_price, Decimal):
                    unit_price = Decimal(str(unit_price))
                self._entered_unit_price_value = unit_price
                cleaned_data['unit_price'] = unit_price / factor
                self.instance.unit_price = cleaned_data['unit_price']
            except (InvalidOperation, TypeError):
                pass
        else:
            self._entered_unit_price_value = None
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptPermanent, instance.company_id, "PRM")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.requires_temporary_receipt = 1 if self.cleaned_data.get('requires_temporary_receipt') else 0
        instance.is_locked = getattr(self.instance, 'is_locked', 0) or 0
        instance.unit = self.instance.unit
        instance.quantity = self.instance.quantity
        instance.entered_unit = self._entered_unit_value or getattr(instance, 'entered_unit', '') or instance.unit
        if self._entered_quantity_value is not None:
            instance.entered_quantity = self._entered_quantity_value
        elif instance.entered_quantity is None:
            instance.entered_quantity = instance.quantity
        if self._entered_unit_price_value is not None:
            instance.entered_unit_price = self._entered_unit_price_value
        elif self.cleaned_data.get('unit_price') in (None, ''):
            instance.entered_unit_price = None
        if commit:
            instance.save()
            self.save_m2m()
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

class ReceiptConsignmentForm(ReceiptBaseForm):
    """Create/update form for consignment receipts."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
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
            'item',
            'warehouse',
            'unit',
            'quantity',
            'supplier',
            'consignment_contract_code',
            'expected_return_date',
            'valuation_method',
            'unit_price_estimate',
            'currency',
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
            'document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'consignment_contract_code': forms.TextInput(attrs={'class': 'form-control'}),
            'valuation_method': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price_estimate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
                        'ownership_status': forms.TextInput(attrs={'class': 'form-control'}),
            'return_document_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'document_code': _('Document Code'),
            'document_date': _('Document Date'),
            'item': _('Item'),
            'warehouse': _('Warehouse'),
            'quantity': _('Quantity'),
            'supplier': _('Supplier'),
            'consignment_contract_code': _('Contract Code'),
            'expected_return_date': _('Expected Return Date'),
            'valuation_method': _('Valuation Method'),
            'unit_price_estimate': _('Estimated Unit Price'),
            'currency': _('Currency'),
            'temporary_receipt': _('Temporary Receipt'),
            'purchase_request': _('Purchase Request'),
            'warehouse_request': _('Warehouse Request'),
            'ownership_status': _('Ownership Status'),
            'conversion_receipt': _('Conversion Receipt'),
            'conversion_date': _('Conversion Date'),
            'return_document_id': _('Return Document'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['requires_temporary_receipt'].initial = bool(self.instance.requires_temporary_receipt)

    def clean(self):
        cleaned_data = super().clean()
        if self.company_id:
            self._clean_company_match(cleaned_data, 'item', _('item'))
            self._clean_company_match(cleaned_data, 'warehouse', _('warehouse'))
            self._clean_company_match(cleaned_data, 'supplier', _('supplier'))
            if cleaned_data.get('temporary_receipt'):
                self._clean_company_match(cleaned_data, 'temporary_receipt', _('temporary receipt'))
            if cleaned_data.get('purchase_request'):
                self._clean_company_match(cleaned_data, 'purchase_request', _('purchase request'))
            if cleaned_data.get('warehouse_request'):
                self._clean_company_match(cleaned_data, 'warehouse_request', _('warehouse request'))
                warehouse_request = cleaned_data.get('warehouse_request')
                item = cleaned_data.get('item')
                warehouse = cleaned_data.get('warehouse')
                if warehouse_request and item and warehouse_request.item_id != item.id:
                    self.add_error('warehouse_request', _('Selected warehouse request is for a different item.'))
                if warehouse_request and warehouse and warehouse_request.warehouse_id != warehouse.id:
                    self.add_error('warehouse_request', _('Selected warehouse request is for a different warehouse.'))
            if cleaned_data.get('conversion_receipt'):
                self._clean_company_match(cleaned_data, 'conversion_receipt', _('conversion receipt'))

        factor = getattr(self, '_unit_factor', Decimal('1'))
        unit_price_estimate = cleaned_data.get('unit_price_estimate')
        if unit_price_estimate not in (None, '') and factor not in (None, Decimal('0')):
            try:
                if not isinstance(unit_price_estimate, Decimal):
                    unit_price_estimate = Decimal(str(unit_price_estimate))
                self._entered_unit_price_value = unit_price_estimate
                cleaned_data['unit_price_estimate'] = unit_price_estimate / factor
                self.instance.unit_price_estimate = cleaned_data['unit_price_estimate']
            except (InvalidOperation, TypeError):
                pass
        else:
            self._entered_unit_price_value = None
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(ReceiptConsignment, instance.company_id, "CON")
        if not instance.document_date:
            instance.document_date = timezone.now().date()
        instance.requires_temporary_receipt = 1 if self.cleaned_data.get('requires_temporary_receipt') else 0
        instance.is_locked = getattr(self.instance, 'is_locked', 0) or 0
        instance.unit = self.instance.unit
        instance.quantity = self.instance.quantity
        instance.entered_unit = self._entered_unit_value or getattr(instance, 'entered_unit', '') or instance.unit
        if self._entered_quantity_value is not None:
            instance.entered_quantity = self._entered_quantity_value
        elif instance.entered_quantity is None:
            instance.entered_quantity = instance.quantity
        if self._entered_unit_price_value is not None:
            instance.entered_unit_price = self._entered_unit_price_value
        elif self.cleaned_data.get('unit_price_estimate') in (None, ''):
            instance.entered_unit_price = None
        if commit:
            instance.save()
            self.save_m2m()
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
        serial_field.required = True
        serial_field.help_text = _('Select the serial numbers for each unit issued.')
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


class IssuePermanentForm(IssueBaseForm):
    """Create/update form for permanent issues."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    department_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Organizational Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which company unit received this issue.'),
    )
    serials = forms.ModelMultipleChoiceField(
        queryset=ItemSerial.objects.none(),
        required=False,
        label=_('Serial Numbers'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text=_('Select serial numbers when the item requires tracking.'),
    )

    class Meta:
        model = IssuePermanent
        fields = [
            'document_code',
            'document_date',
            'item',
            'warehouse',
            'unit',
            'quantity',
            'destination_type',
            'destination_id',
            'destination_code',
            'reason_code',
            'department_unit',
            'serials',
            'unit_price',
            'currency',
            'tax_amount',
            'discount_amount',
            'total_amount',
        ]
        widgets = {
            'document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'destination_type': forms.TextInput(attrs={'class': 'form-control'}),
            'destination_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination_code': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
                        'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(IssuePermanent, instance.company_id, "ISP")
        if not instance.document_date:
            instance.document_date = timezone.now().date()

        department_unit = self.cleaned_data.get('department_unit')
        instance.department_unit = department_unit
        instance.department_unit_code = department_unit.public_code if department_unit else ''

        instance.unit = self.instance.unit
        instance.quantity = self.instance.quantity
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssueConsumptionForm(IssueBaseForm):
    """Create/update form for consumption issues."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    department_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Organizational Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which company unit consumes this issue.'),
    )
    work_line = forms.ModelChoiceField(
        queryset=WorkLine.objects.none(),
        required=False,
        label=_('Work Line'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    serials = forms.ModelMultipleChoiceField(
        queryset=ItemSerial.objects.none(),
        required=False,
        label=_('Serial Numbers'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text=_('Select serial numbers when the item requires tracking.'),
    )

    class Meta:
        model = IssueConsumption
        fields = [
            'document_code',
            'document_date',
            'item',
            'warehouse',
            'unit',
            'quantity',
            'consumption_type',
            'department_unit',
            'work_line',
            'serials',
            'reference_document_type',
            'reference_document_id',
            'reference_document_code',
            'production_transfer_id',
            'production_transfer_code',
            'unit_cost',
            'total_cost',
        ]
        widgets = {
            'document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'consumption_type': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_document_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference_document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'production_transfer_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'production_transfer_code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(IssueConsumption, instance.company_id, "ISU")
        if not instance.document_date:
            instance.document_date = timezone.now().date()

        department_unit = self.cleaned_data.get('department_unit')
        work_line = self.cleaned_data.get('work_line')
        instance.department_unit = department_unit
        instance.work_line = work_line
        instance.department_unit_code = department_unit.public_code if department_unit else ''
        instance.work_line_code = work_line.public_code if work_line else ''

        instance.unit = self.instance.unit
        instance.quantity = self.instance.quantity
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class IssueConsignmentForm(IssueBaseForm):
    """Create/update form for consignment issues."""

    unit = forms.ChoiceField(
        label=_('Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    department_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Organizational Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Optional: specify which company unit received this consignment.'),
    )
    serials = forms.ModelMultipleChoiceField(
        queryset=ItemSerial.objects.none(),
        required=False,
        label=_('Serial Numbers'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text=_('Select serial numbers when the item requires tracking.'),
    )

    class Meta:
        model = IssueConsignment
        fields = [
            'document_code',
            'document_date',
            'item',
            'warehouse',
            'unit',
            'quantity',
            'consignment_receipt',
            'destination_type',
            'destination_id',
            'destination_code',
            'reason_code',
            'department_unit',
            'serials',
        ]
        widgets = {
            'document_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'destination_type': forms.TextInput(attrs={'class': 'form-control'}),
            'destination_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination_code': forms.TextInput(attrs={'class': 'form-control'}),
            'reason_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.document_code:
            instance.document_code = generate_document_code(IssueConsignment, instance.company_id, "ICN")
        if not instance.document_date:
            instance.document_date = timezone.now().date()

        department_unit = self.cleaned_data.get('department_unit')
        instance.department_unit = department_unit
        instance.department_unit_code = department_unit.public_code if department_unit else ''

        consignment_receipt = self.cleaned_data.get('consignment_receipt')
        if consignment_receipt:
            instance.consignment_receipt_code = consignment_receipt.document_code
        else:
            instance.consignment_receipt_code = ''

        instance.unit = self.instance.unit
        instance.quantity = self.instance.quantity
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class StocktakingBaseForm(forms.ModelForm):
    """Shared helpers for stocktaking documents."""

    unit_placeholder = UNIT_CHOICES[0][1]

    def __init__(self, *args, company_id=None, **kwargs):
        self.company_id = company_id or getattr(kwargs.get('instance'), 'company_id', None)
        self.date_widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
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
            self.fields['confirmed_by'].queryset = Person.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['confirmed_by'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.first_name} {obj.last_name}"
        if 'approver' in self.fields:
            self.fields['approver'].queryset = Person.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['approver'].label_from_instance = lambda obj: f"{obj.public_code} - {obj.first_name} {obj.last_name}"

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
            if allowed_ids and warehouse.id not in allowed_ids:
                self.add_error('warehouse', _('Selected warehouse is not permitted for this item.'))

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
            'approval_status',
            'approved_at',
            'approver',
            'approver_notes',
            'record_metadata',
        ]
        widgets = {
            'stocktaking_session_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'confirmation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'final_inventory_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approval_status': forms.TextInput(attrs={'class': 'form-control'}),
            'approver_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'approval_status' in self.fields and not getattr(self.instance, 'pk', None):
            self.fields['approval_status'].initial = 'pending'
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
            instance.confirmed_by_code = instance.confirmed_by.public_code
        if instance.approver_id:
            instance.approver_notes = instance.approver_notes or ''
        if commit:
            instance.save()
            self.save_m2m()
        return instance

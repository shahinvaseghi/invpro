# ticketing/forms/base.py - Base Forms (Complete Documentation)

**هدف**: Base form classes و helper functions برای ماژول ticketing

این فایل شامل:
- TicketingBaseForm: Base form class برای تمام ticketing forms
- TicketFormMixin: Mixin برای ticket-related forms

---

## وابستگی‌ها

- `django.forms`
- `django.utils.translation.gettext_lazy`

---

## TicketingBaseForm

### `TicketingBaseForm(forms.ModelForm)`

**توضیح**: Base form class برای تمام ticketing models

**Inheritance**: `forms.ModelForm`

**Meta**:
- `abstract = True`

**متدها**:

#### `__init__(self, *args, **kwargs) -> None`

**توضیح**: فرم را با company context initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `**kwargs`: آرگومان‌های keyword (می‌تواند شامل `request` باشد)

**مقدار بازگشتی**: ندارد

**منطق**:
1. `request` را از kwargs pop می‌کند و در `self.request` ذخیره می‌کند
2. `super().__init__()` را فراخوانی می‌کند
3. اگر `request` وجود دارد و `active_company_id` در session موجود است:
   - `_filter_foreign_keys_by_company()` را فراخوانی می‌کند

---

#### `_filter_foreign_keys_by_company(self, company_id: int) -> None`

**توضیح**: Foreign key fields را بر اساس company فیلتر می‌کند.

**پارامترهای ورودی**:
- `company_id` (int): شناسه شرکت فعال

**مقدار بازگشتی**: ندارد

**منطق**:
1. برای هر field در `self.fields`:
   - اگر field یک `ModelChoiceField` باشد:
     - اگر model مربوطه field `company` داشته باشد:
       - queryset را بر اساس `company_id` فیلتر می‌کند

**نکات مهم**:
- فقط ModelChoiceField ها فیلتر می‌شوند
- فقط اگر model field `company` داشته باشد

---

## TicketFormMixin

### `TicketFormMixin`

**توضیح**: Mixin برای ticket-related forms

**متدها**:

#### `clean(self) -> Dict[str, Any]`

**توضیح**: Cross-field validation را انجام می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. Ticket-specific validation را اضافه می‌کند (در حال حاضر خالی است)
3. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- این mixin برای future ticket-specific validation استفاده می‌شود
- در حال حاضر فقط `super().clean()` را فراخوانی می‌کند

---

## استفاده در پروژه

### در Forms
```python
class TicketCategoryForm(TicketingBaseForm):
    class Meta:
        model = TicketCategory
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # request automatically available in self.request
        # Foreign keys automatically filtered by company
```

---

## الگوهای مشترک

1. **Company Filtering**: Foreign key fields به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Request Context**: `request` object در `self.request` در دسترس است
3. **Abstract Base**: `TicketingBaseForm` یک abstract base class است


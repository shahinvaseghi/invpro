# shared/forms/base.py - Base Form Classes

**هدف**: کلاس‌های پایه فرم برای تمام ماژول‌ها

این فایل شامل کلاس‌های پایه زیر است:
- `BaseModelForm` - کلاس پایه ModelForm با استایل خودکار widgetها
- `BaseFormset` - کلاس پایه formset با قابلیت‌های مشترک

---

## کلاس‌ها

### `BaseModelForm`

**توضیح**: کلاس پایه ModelForm با استایل خودکار widgetها

این form به صورت خودکار کلاس‌های CSS پیش‌فرض را به تمام فیلدهای form اعمال می‌کند:
- Checkbox inputs → `'form-check-input'` class
- Radio inputs → `'form-check-input'` class
- سایر inputs → `'form-control'` class

**Type**: `forms.ModelForm`

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: مقداردهی اولیه form و اعمال استایل پیش‌فرض widget

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `**kwargs`: آرگومان‌های keyword

**منطق**:
1. `company_id` را از kwargs pop می‌کند (اگر ارائه شده باشد)
2. اگر `company_id` وجود داشته باشد، آن را به `self.company_id` تنظیم می‌کند
3. `super().__init__()` را فراخوانی می‌کند
4. `_apply_default_widget_styling()` را فراخوانی می‌کند

**نکته**: `company_id` به صورت اختیاری pop می‌شود تا از TypeError جلوگیری شود اگر form به آن نیاز نداشته باشد

#### `_apply_default_widget_styling(self) -> None`

**توضیح**: اعمال کلاس‌های CSS پیش‌فرض به تمام فیلدهای form

**منطق**:
1. برای هر فیلد در `self.fields`:
   - widget را از field دریافت می‌کند
   - اگر widget قبلاً دارای `class` attribute باشد، skip می‌کند
   - بر اساس نوع widget:
     - اگر `CheckboxInput` باشد: `'form-check-input'` را اضافه می‌کند
     - اگر `RadioSelect` باشد: `'form-check-input'` را اضافه می‌کند
     - در غیر این صورت: `'form-control'` را اضافه می‌کند

---

### `BaseFormset`

**توضیح**: کلاس پایه formset helper

این کلاس قابلیت‌های مشترک برای formsets را ارائه می‌دهد مانند تنظیم request روی تمام forms و ذخیره با company context.

**Type**: `forms.BaseFormSet`

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: مقداردهی اولیه formset و تنظیم request روی تمام forms اگر ارائه شده باشد

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `**kwargs`: آرگومان‌های keyword

**منطق**:
1. `request` را از kwargs pop می‌کند (اگر ارائه شده باشد)
2. `self.request` را تنظیم می‌کند
3. `super().__init__()` را فراخوانی می‌کند
4. اگر `request` وجود داشته باشد، `_set_request_on_forms()` را فراخوانی می‌کند

#### `_set_request_on_forms(self) -> None`

**توضیح**: تنظیم request object روی تمام forms در formset

**منطق**:
1. برای هر form در `self.forms`:
   - اگر form دارای `request` attribute باشد، آن را به `self.request` تنظیم می‌کند

#### `save_with_company(self, company_id: Optional[int], commit: bool = True) -> List[Any]`

**توضیح**: ذخیره تمام forms در formset با company_id

**پارامترهای ورودی**:
- `company_id`: Company ID برای تنظیم روی تمام form instances
- `commit`: آیا باید در دیتابیس ذخیره شود (پیش‌فرض: `True`)

**مقدار بازگشتی**:
- `List[Any]`: لیست instances ذخیره شده

**منطق**:
1. لیست `instances` را ایجاد می‌کند
2. برای هر form در `self.forms`:
   - اگر form معتبر باشد و حذف نشده باشد (`DELETE=False`):
     - instance را با `form.save(commit=False)` دریافت می‌کند
     - اگر `company_id` وجود داشته باشد و instance دارای `company_id` attribute باشد، آن را تنظیم می‌کند
     - اگر `commit=True` باشد، instance را ذخیره می‌کند
     - instance را به لیست اضافه می‌کند
3. لیست instances را برمی‌گرداند

---

## وابستگی‌ها

- `django.forms`: `forms.ModelForm`, `forms.BaseFormSet`
- `django.forms.formsets`: `BaseFormSet`
- `typing`: `Optional`, `Any`

---

## استفاده در پروژه

### استفاده از BaseModelForm

```python
from shared.forms.base import BaseModelForm
from inventory.models import Item

class ItemForm(BaseModelForm):
    class Meta:
        model = Item
        fields = ['name', 'code', 'is_enabled']
        # No need to define widgets - styling is automatic
        # Checkbox inputs automatically get 'form-check-input'
        # Other inputs automatically get 'form-control'
```

### استفاده از BaseFormset

```python
from shared.forms.base import BaseFormset
from django.forms import formset_factory

class MyFormset(BaseFormset):
    form = MyForm
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request:
            self._set_request_on_forms()

MyFormsetFactory = formset_factory(MyForm, formset=MyFormset, extra=1)

# Usage in view
formset = MyFormsetFactory(request.POST, request=request)
if formset.is_valid():
    company_id = request.session.get('active_company_id')
    instances = formset.save_with_company(company_id)
```

---

## نکات مهم

1. **Automatic Widget Styling**: `BaseModelForm` به صورت خودکار کلاس‌های CSS را به widgetها اعمال می‌کند، بنابراین نیازی به تعریف widgets در Meta نیست

2. **Company ID Handling**: `BaseModelForm` به صورت اختیاری `company_id` را از kwargs pop می‌کند تا از TypeError جلوگیری شود

3. **Request Propagation**: `BaseFormset` request را روی تمام forms در formset تنظیم می‌کند

4. **Company Scoping**: `BaseFormset.save_with_company()` به صورت خودکار `company_id` را روی تمام instances تنظیم می‌کند

5. **Skip Existing Classes**: اگر widget قبلاً دارای `class` attribute باشد، `_apply_default_widget_styling()` آن را skip می‌کند

6. **Checkbox and Radio**: هر دو `CheckboxInput` و `RadioSelect` کلاس `'form-check-input'` دریافت می‌کنند

7. **Other Inputs**: تمام سایر input types (TextInput, Select, Textarea, NumberInput, etc.) کلاس `'form-control'` دریافت می‌کنند

8. **Formset Validation**: `save_with_company()` فقط forms معتبر و غیر حذف شده را ذخیره می‌کند

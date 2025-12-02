# accounting/forms/cost_centers.py - Cost Center Forms (Complete Documentation)

**هدف**: Forms برای مدیریت مراکز هزینه

این فایل شامل **1 form class** است:
- `CostCenterForm`: فرم ایجاد/ویرایش مرکز هزینه

---

## وابستگی‌ها

- `django.forms`: `ModelForm`
- `django.utils.translation`: `gettext_lazy as _`
- `typing`: `Optional`
- `accounting.models`: `CostCenter`
- `shared.models`: `CompanyUnit`, `Company`
- `shared.utils.modules`: `get_work_line_model`

---

## Forms

### `CostCenterForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش مرکز هزینه

**Model**: `CostCenter`

**Fields**:
- `cost_center_name` (CharField): نام مرکز هزینه (فارسی)
  - Widget: `TextInput`
  - Label: `'نام مرکز هزینه'`
  - Required: `True`

- `cost_center_name_en` (CharField): نام مرکز هزینه (انگلیسی)
  - Widget: `TextInput`
  - Label: `'نام مرکز هزینه (انگلیسی)'`
  - Required: `False`

- `company_unit` (ForeignKey): واحد کاری
  - Widget: `Select`
  - Label: `'واحد کاری'`
  - Required: `True`
  - Queryset: فیلتر شده بر اساس `company_id` و `is_enabled=1`
  - Display: `"{public_code} · {name}"`

- `work_line` (ForeignKey): خط کاری
  - Widget: `Select` (یا `HiddenInput` اگر ماژول تولید نصب نشده)
  - Label: `'خط کاری'`
  - Required: `False`
  - Help Text: `'خط کاری تولید (اختیاری - فقط در صورت نصب ماژول تولید)'`
  - Queryset: فیلتر شده بر اساس `company_id` و `is_enabled=1` (اگر ماژول تولید نصب شده)
  - Display: `"{public_code} · {name}"`
  - اگر ماژول تولید نصب نشده: فیلد مخفی می‌شود

- `description` (TextField): توضیحات
  - Widget: `Textarea` (rows=4)
  - Label: `'توضیحات'`
  - Required: `False`

- `is_enabled` (PositiveSmallIntegerField): وضعیت فعال/غیرفعال
  - Widget: `Select`
  - Label: `'وضعیت'`
  - Required: `False`

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: مقداردهی اولیه فرم با company_id و فیلتر کردن queryset ها

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال (از session)
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id` در `self.company_id`
3. اگر `company_id` وجود دارد:
   - تنظیم `self.instance.company` برای instance جدید
   - فیلتر کردن `company_unit` queryset:
     - فیلتر بر اساس `company_id` و `is_enabled=1`
     - مرتب‌سازی بر اساس `name`
     - تنظیم `empty_label` به `"--- انتخاب کنید ---"`
     - تنظیم `label_from_instance` به `"{public_code} · {name}"`
   - فیلتر کردن `work_line` queryset:
     - بررسی نصب بودن ماژول تولید با `get_work_line_model()`
     - اگر ماژول تولید نصب شده:
       - فیلتر بر اساس `company_id` و `is_enabled=1`
       - مرتب‌سازی بر اساس `name`
       - تنظیم `empty_label` به `"--- انتخاب کنید (اختیاری) ---"`
       - تنظیم `label_from_instance` به `"{public_code} · {name}"`
     - اگر ماژول تولید نصب نشده:
       - تغییر widget به `HiddenInput`
       - تنظیم `required = False`

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی company_unit و work_line

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. فراخوانی `super().clean()`
2. دریافت `company_unit` از cleaned_data:
   - اگر `company_unit` وجود دارد و `company_id` موجود است:
     - بررسی می‌کند که `company_unit.company_id == company_id`
     - در غیر این صورت `ValidationError` می‌اندازد
3. دریافت `work_line` از cleaned_data:
   - اگر `work_line` وجود دارد و `company_id` موجود است:
     - بررسی می‌کند که `work_line.company_id == company_id`
     - در غیر این صورت `ValidationError` می‌اندازد
4. برگرداندن cleaned_data

---

## استفاده در پروژه

### Import Form

```python
from accounting.forms import CostCenterForm
```

### استفاده در View ها

```python
# در CreateView
form = CostCenterForm(company_id=request.session.get('active_company_id'))

# در UpdateView
form = CostCenterForm(instance=cost_center, company_id=request.session.get('active_company_id'))
```

---

## نکات مهم

1. **Company Scoping**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **Production Module Dependency**: فیلد `work_line` فقط در صورت نصب ماژول تولید نمایش داده می‌شود
3. **Code Auto-Generation**: کد مرکز هزینه به صورت خودکار در مدل `CostCenter.save()` تولید می‌شود
4. **Company Unit Validation**: واحد کاری انتخاب شده باید متعلق به شرکت فعال باشد
5. **Work Line Validation**: خط کاری انتخاب شده باید متعلق به شرکت فعال باشد

---

**Last Updated**: 2025-12-02


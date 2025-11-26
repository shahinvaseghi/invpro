# shared/forms/companies.py - Company Forms (Complete Documentation)

**هدف**: Forms برای مدیریت شرکت‌ها و واحدهای سازمانی در ماژول shared

این فایل شامل **2 Form Classes**:
- `CompanyForm`: Form برای ایجاد و ویرایش شرکت‌ها
- `CompanyUnitForm`: Form برای ایجاد و ویرایش واحدهای سازمانی

---

## وابستگی‌ها

- `shared.models`: `Company`, `CompanyUnit`
- `django.forms`
- `django.utils.translation`: `gettext_lazy`
- `typing`: `Optional`

---

## CompanyForm

**Type**: `forms.ModelForm`

**Model**: `Company`

**توضیح**: Form برای ایجاد و ویرایش شرکت‌ها.

**Fields**:
- `public_code`: کد عمومی (maxlength: 3)
- `legal_name`: نام قانونی
- `display_name`, `display_name_en`: نام نمایشی (فارسی و انگلیسی)
- `registration_number`: شماره ثبت
- `tax_id`: شناسه مالیاتی
- `phone_number`, `email`, `website`: اطلاعات تماس
- `address`, `city`, `state`, `country`: آدرس
- `is_enabled`: وضعیت

**Widgets**:
- Text inputs با `form-control` class
- Email input برای email
- URL input برای website
- Textarea برای address (3 rows)
- Select برای is_enabled

**Labels**:
- تمام labels با `gettext_lazy` ترجمه شده‌اند

**نکات مهم**:
- `public_code` محدود به 3 کاراکتر است
- `country` محدود به 3 کاراکتر است (ISO code)

---

## CompanyUnitForm

**Type**: `forms.ModelForm`

**Model**: `CompanyUnit`

**توضیح**: Form برای ایجاد و ویرایش واحدهای سازمانی.

**Fields**:
- `public_code`: کد عمومی (maxlength: 5)
- `name`, `name_en`: نام واحد (فارسی و انگلیسی)
- `parent_unit`: واحد بالادست (optional)
- `description`: توضیحات
- `notes`: یادداشت‌ها
- `is_enabled`: وضعیت

**Additional Field**:
- `parent_unit`: `ModelChoiceField` با queryset filtered by company

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company filtering.

**پارامترهای ورودی**:
- `company_id`: شناسه شرکت (optional)

**منطق**:
1. دریافت `company_id` از parameter یا `self.instance.company_id`
2. فیلتر `parent_unit` queryset:
   - اگر `company_id` موجود باشد: فقط units همان company
   - اگر instance موجود باشد: exclude خود instance (برای جلوگیری از circular reference)
3. تنظیم choices برای `is_enabled` (فارسی)

**نکات مهم**:
- `parent_unit` queryset بر اساس company فیلتر می‌شود
- خود instance از queryset exclude می‌شود (برای جلوگیری از circular reference)

---

#### `clean_parent_unit(self) -> Optional[CompanyUnit]`

**توضیح**: Validate که parent unit متعلق به همان company باشد.

**مقدار بازگشتی**:
- `Optional[CompanyUnit]`: parent unit (اگر valid باشد)

**منطق**:
- اگر `parent` و `company_id` موجود باشند:
  - بررسی `parent.company_id == self.company_id`
  - اگر برابر نباشند: raise `ValidationError`

**نکات مهم**:
- Parent unit باید متعلق به همان company باشد
- این برای حفظ company scoping است

---

## نکات مهم

### 1. Company Scoping
- `CompanyUnitForm` بر اساس `company_id` فیلتر می‌شود
- Parent unit باید متعلق به همان company باشد

### 2. Hierarchical Structure
- Units می‌توانند `parent_unit` داشته باشند
- Circular references جلوگیری می‌شوند (خود instance از queryset exclude می‌شود)

### 3. Field Constraints
- `public_code` در Company: maxlength 3
- `public_code` در CompanyUnit: maxlength 5
- `country` در Company: maxlength 3 (ISO code)

### 4. Language Support
- CompanyUnitForm labels به فارسی هستند
- CompanyForm labels با `gettext_lazy` ترجمه شده‌اند

---

## استفاده در پروژه

### در Views
```python
from shared.forms import CompanyForm, CompanyUnitForm

# Company
form = CompanyForm(request.POST, instance=company)

# Company Unit
form = CompanyUnitForm(request.POST, instance=unit, company_id=company_id)
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `Company` و `CompanyUnit` models استفاده می‌کند

### Shared Views
- در `shared/views/companies.py` استفاده می‌شود

### Inventory Module
- Company units در issue destinations استفاده می‌شوند


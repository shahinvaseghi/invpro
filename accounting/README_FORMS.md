# accounting/forms/ - Accounting Forms Package (Complete Documentation)

**هدف**: Forms package برای ماژول Accounting

**نکته**: این forms در package `accounting/forms/` قرار دارند. فایل `accounting/forms.py` برای backward compatibility حفظ شده است.

این package شامل **3 فایل**:
- `fiscal_years.py`: `FiscalYearForm` - Form برای ایجاد و ویرایش سال‌های مالی
- `periods.py`: `PeriodForm` - Form برای ایجاد و ویرایش دوره‌های حسابداری
- `accounts.py`: `AccountForm` - Form برای ایجاد و ویرایش حساب‌ها (Chart of Accounts)

---

## ساختار Package

```
accounting/forms/
├── __init__.py          # Export همه forms
├── fiscal_years.py      # FiscalYearForm
├── periods.py           # PeriodForm
└── accounts.py          # AccountForm
```

---

## وابستگی‌ها

- `accounting.models`: `FiscalYear`, `Period`, `Account`
- `shared.models`: `Company`
- `django.forms`
- `django.utils.translation`: `gettext_lazy`
- `typing`: `Optional`

---

## FiscalYearForm

**Type**: `forms.ModelForm`

**Model**: `FiscalYear`

**توضیح**: Form برای ایجاد و ویرایش سال‌های مالی.

**Fields**:
- `fiscal_year_code` (CharField, maxlength: 10): کد سال مالی
- `fiscal_year_name` (CharField): نام سال مالی
- `start_date` (DateField): تاریخ شروع
- `end_date` (DateField): تاریخ پایان
- `is_current` (PositiveSmallIntegerField): پرچم سال مالی جاری
- `is_enabled` (PositiveSmallIntegerField): وضعیت

**Widgets**:
- Text inputs با `form-control` class
- Date inputs با `type='date'`
- Select برای `is_current` و `is_enabled`

**Labels**:
- تمام labels با `gettext_lazy` ترجمه شده‌اند

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company setting.

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت (optional)

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را تنظیم می‌کند
3. اگر `company_id` وجود دارد و instance جدید است (`not self.instance.pk`):
   - Company را از دیتابیس می‌گیرد و به `instance.company` اختصاص می‌دهد
   - در صورت عدم وجود Company، خطا را نادیده می‌گیرد

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی تاریخ‌های سال مالی.

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `start_date` و `end_date` را از cleaned_data می‌گیرد
3. اگر هر دو وجود دارند:
   - بررسی می‌کند که `end_date` بعد از `start_date` باشد
   - در غیر این صورت `ValidationError` می‌اندازد
4. cleaned_data را برمی‌گرداند

---

## periods.py

### `PeriodForm`

**Type**: `forms.ModelForm`

**Model**: `Period`

**توضیح**: Form برای ایجاد و ویرایش دوره‌های حسابداری.

**File**: `accounting/forms/periods.py`

**Fields**:
- `fiscal_year` (ForeignKey): سال مالی
- `period_code` (CharField, maxlength: 10): کد دوره
- `period_name` (CharField): نام دوره
- `start_date` (DateField): تاریخ شروع
- `end_date` (DateField): تاریخ پایان
- `is_enabled` (PositiveSmallIntegerField): وضعیت

**Widgets**:
- Select برای `fiscal_year` (با company filtering)
- Text inputs با `form-control` class
- Date inputs با `type='date'`
- Select برای `is_enabled`

**Labels**:
- تمام labels با `gettext_lazy` ترجمه شده‌اند

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company filtering برای fiscal_year.

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت (optional)

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را تنظیم می‌کند
3. اگر `company_id` وجود دارد:
   - queryset `fiscal_year` را بر اساس `company_id` و `is_enabled=1` فیلتر می‌کند
   - queryset را بر اساس `-fiscal_year_code` مرتب می‌کند
4. اگر `company_id` وجود دارد و instance جدید است:
   - Company را از دیتابیس می‌گیرد و به `instance.company` اختصاص می‌دهد

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی تاریخ‌های دوره و محدوده سال مالی.

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `start_date`, `end_date`, و `fiscal_year` را از cleaned_data می‌گیرد
3. اگر `start_date` و `end_date` وجود دارند:
   - بررسی می‌کند که `end_date` بعد از `start_date` باشد
4. اگر `fiscal_year`, `start_date`, و `end_date` وجود دارند:
   - بررسی می‌کند که `start_date` در محدوده سال مالی باشد (`>= fiscal_year.start_date`)
   - بررسی می‌کند که `end_date` در محدوده سال مالی باشد (`<= fiscal_year.end_date`)
5. در صورت عدم اعتبار، `ValidationError` می‌اندازد
6. cleaned_data را برمی‌گرداند

---

## accounts.py

### `AccountForm`

**Type**: `forms.ModelForm`

**Model**: `Account`

**توضیح**: Form برای ایجاد و ویرایش حساب‌ها (Chart of Accounts).

**File**: `accounting/forms/accounts.py`

**Fields**:
- `account_code` (CharField, maxlength: 20): کد حساب
- `account_name` (CharField): نام فارسی حساب
- `account_name_en` (CharField, blank=True): نام انگلیسی حساب
- `account_type` (CharField, choices=ACCOUNT_TYPE_CHOICES): نوع حساب
- `account_level` (PositiveSmallIntegerField, choices=ACCOUNT_LEVEL_CHOICES): سطح حساب
- `parent_account` (ForeignKey, required=False): حساب والد (optional)
- `normal_balance` (CharField, choices=NORMAL_BALANCE_CHOICES): طرف مانده عادی
- `opening_balance` (DecimalField): مانده افتتاحیه
- `description` (TextField, blank=True): توضیحات
- `is_enabled` (PositiveSmallIntegerField): وضعیت

**Widgets**:
- Text inputs با `form-control` class
- Select برای `account_type`, `account_level`, `parent_account`, `normal_balance`, `is_enabled`
- NumberInput برای `opening_balance` با `step='0.01'`
- Textarea برای `description` با 3 rows

**Labels**:
- تمام labels با `gettext_lazy` ترجمه شده‌اند

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, exclude_account_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company filtering برای parent_account.

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت (optional)
- `exclude_account_id` (Optional[int]): شناسه حساب برای حذف از parent choices (برای جلوگیری از circular references)

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را تنظیم می‌کند
3. اگر `company_id` وجود دارد:
   - queryset `parent_account` را بر اساس `company_id` و `is_enabled=1` فیلتر می‌کند
   - اگر `exclude_account_id` وجود دارد، آن را از queryset حذف می‌کند (برای جلوگیری از circular references)
   - queryset را بر اساس `account_code` مرتب می‌کند
4. `parent_account` را optional می‌کند (`required = False`)
5. اگر `company_id` وجود دارد و instance جدید است:
   - Company را از دیتابیس می‌گیرد و به `instance.company` اختصاص می‌دهد

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی ساختار حساب و normal_balance.

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `account_type`, `normal_balance`, `parent_account`, و `account_level` را از cleaned_data می‌گیرد
3. اعتبارسنجی `normal_balance` بر اساس `account_type`:
   - اگر `account_type` در `['ASSET', 'EXPENSE']` باشد، `normal_balance` باید `'DEBIT'` باشد
   - اگر `account_type` در `['LIABILITY', 'EQUITY', 'REVENUE']` باشد، `normal_balance` باید `'CREDIT'` باشد
4. اعتبارسنجی `parent_account`:
   - اگر `parent_account` وجود دارد:
     - بررسی می‌کند که `parent_account` متعلق به همان شرکت باشد (`company_id`)
     - بررسی می‌کند که سطح حساب والد کمتر از سطح حساب فرزند باشد (`parent_account.account_level < account_level`)
5. در صورت عدم اعتبار، `ValidationError` می‌اندازد
6. cleaned_data را برمی‌گرداند

---

## استفاده در پروژه

### Import Forms

```python
# از package (توصیه می‌شود)
from accounting.forms import FiscalYearForm, PeriodForm, AccountForm

# از package submodule
from accounting.forms.fiscal_years import FiscalYearForm
from accounting.forms.periods import PeriodForm
from accounting.forms.accounts import AccountForm

# از فایل اصلی (backward compatibility)
from accounting.forms import FiscalYearForm, PeriodForm, AccountForm
```

### استفاده در Views

#### FiscalYearForm
- در `FiscalYearCreateView` و `FiscalYearUpdateView` استفاده می‌شود
- `company_id` از session گرفته می‌شود و به form kwargs اضافه می‌شود

#### PeriodForm
- در views مربوط به Period استفاده می‌شود (در آینده)
- `company_id` از session گرفته می‌شود
- `fiscal_year` queryset بر اساس company فیلتر می‌شود

#### AccountForm
- در `AccountCreateView` و `AccountUpdateView` استفاده می‌شود
- `company_id` از session گرفته می‌شود
- در `UpdateView`, `exclude_account_id` برای جلوگیری از circular references تنظیم می‌شود
- `parent_account` queryset بر اساس company فیلتر می‌شود

---

## نکات مهم

1. **Company Scoping**: تمام forms از `company_id` برای فیلتر کردن queryset‌ها استفاده می‌کنند
2. **Date Validation**: تاریخ‌ها در `clean()` اعتبارسنجی می‌شوند
3. **Fiscal Year Range**: دوره‌ها باید در محدوده سال مالی باشند
4. **Account Hierarchy**: حساب‌های والد باید سطح کمتری از حساب فرزند داشته باشند
5. **Normal Balance**: `normal_balance` بر اساس `account_type` اعتبارسنجی می‌شود
6. **Circular References**: در `AccountForm`, حساب فعلی از parent choices حذف می‌شود
7. **Auto Company Setting**: برای instance های جدید، company به صورت خودکار تنظیم می‌شود

---

## Backward Compatibility

فایل `accounting/forms.py` برای backward compatibility حفظ شده است و تمام forms را از package import می‌کند:

```python
from accounting.forms import (
    FiscalYearForm,
    PeriodForm,
    AccountForm,
)
```

این به این معنی است که import paths قدیمی همچنان کار می‌کنند:

```python
# این import paths همچنان کار می‌کنند
from accounting.forms import FiscalYearForm
from accounting import forms
```

---

**Last Updated**: 2025-12-01


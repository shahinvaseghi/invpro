# accounting/forms/parties.py - Party Forms (Complete Documentation)

**هدف**: Forms برای مدیریت Party و PartyAccount

این فایل شامل **2 form class** است:
- `PartyForm`: فرم ایجاد/ویرایش طرف حساب
- `PartyAccountForm`: فرم ایجاد/ویرایش حساب طرف حساب

---

## وابستگی‌ها

- `django.forms`: `ModelForm`
- `django.utils.translation`: `gettext_lazy as _`
- `typing`: `Optional`
- `accounting.models`: `Party`, `PartyAccount`, `Account`
- `shared.models`: `Company`

---

## Forms

### `PartyForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش طرف حساب

**Model**: `Party`

**Fields**:
- `party_type` (CharField): نوع طرف حساب
  - Widget: `Select`
  - Label: `'نوع طرف حساب'`
  - Required: `True`
  - Choices: `'customer'` (مشتری), `'supplier'` (تأمین‌کننده), `'employee'` (کارمند), `'other'` (سایر)

- `party_name` (CharField): نام طرف حساب (فارسی)
  - Widget: `TextInput`
  - Label: `'نام طرف حساب'`
  - Required: `True`

- `party_name_en` (CharField): نام طرف حساب (انگلیسی)
  - Widget: `TextInput`
  - Label: `'نام طرف حساب (انگلیسی)'`
  - Required: `False`

- `national_id` (CharField): کد ملی / شماره ثبت
  - Widget: `TextInput`
  - Label: `'کد ملی / شماره ثبت'`
  - Required: `False`

- `tax_id` (CharField): شناسه مالیاتی
  - Widget: `TextInput`
  - Label: `'شناسه مالیاتی'`
  - Required: `False`

- `address` (TextField): آدرس
  - Widget: `Textarea` (rows=3)
  - Label: `'آدرس'`
  - Required: `False`

- `phone` (CharField): شماره تلفن
  - Widget: `TextInput`
  - Label: `'تلفن'`
  - Required: `False`

- `email` (EmailField): ایمیل
  - Widget: `EmailInput`
  - Label: `'ایمیل'`
  - Required: `False`

- `contact_person` (CharField): شخص رابط
  - Widget: `TextInput`
  - Label: `'شخص رابط'`
  - Required: `False`

- `notes` (TextField): توضیحات
  - Widget: `Textarea` (rows=4)
  - Label: `'توضیحات'`
  - Required: `False`

- `is_enabled` (PositiveSmallIntegerField): وضعیت فعال/غیرفعال
  - Widget: `Select`
  - Label: `'وضعیت'`
  - Required: `False`

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: مقداردهی اولیه فرم با company_id

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال (از session)
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id` در `self.company_id`
3. اگر `company_id` وجود دارد:
   - دریافت شرکت از دیتابیس
   - تنظیم `self.instance.company` برای instance جدید

---

### `PartyAccountForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش حساب طرف حساب

**Model**: `PartyAccount`

**Fields**:
- `party` (ForeignKey): طرف حساب
  - Widget: `Select`
  - Label: `'طرف حساب'`
  - Required: `True`
  - Queryset: فیلتر شده بر اساس `company_id` و `is_enabled=1`
  - Display: `"{party_code} · {party_name}"`

- `account` (ForeignKey): حساب تفصیلی
  - Widget: `Select`
  - Label: `'حساب تفصیلی'`
  - Required: `True`
  - Help Text: `'حساب تفصیلی مرتبط با این طرف حساب'`
  - Queryset: فیلتر شده بر اساس `company_id`, `account_level=3`, و `is_enabled=1`
  - Display: `"{account_code} · {account_name}"`

- `is_primary` (PositiveSmallIntegerField): حساب اصلی
  - Widget: `Select`
  - Label: `'حساب اصلی'`
  - Required: `False`
  - Help Text: `'اگر این حساب اصلی طرف حساب است، انتخاب کنید'`

- `notes` (TextField): توضیحات
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
   - فیلتر کردن `party` queryset:
     - فیلتر بر اساس `company_id` و `is_enabled=1`
     - مرتب‌سازی بر اساس `party_name`
     - تنظیم `empty_label` به `"--- انتخاب کنید ---"`
     - تنظیم `label_from_instance` به `"{party_code} · {party_name}"`
   - فیلتر کردن `account` queryset:
     - فیلتر بر اساس `company_id`, `account_level=3`, و `is_enabled=1`
     - مرتب‌سازی بر اساس `account_code`
     - تنظیم `empty_label` به `"--- انتخاب کنید ---"`
     - تنظیم `label_from_instance` به `"{account_code} · {account_name}"`

---

## استفاده در پروژه

### Import Forms

```python
from accounting.forms import PartyForm, PartyAccountForm
```

### استفاده در View ها

```python
# در CreateView
form = PartyForm(company_id=request.session.get('active_company_id'))

# در UpdateView
form = PartyForm(instance=party, company_id=request.session.get('active_company_id'))
```

---

## نکات مهم

1. **Company Scoping**: تمام forms باید `company_id` دریافت کنند تا queryset ها به درستی فیلتر شوند
2. **Party Code Auto-Generation**: کد طرف حساب به صورت خودکار در مدل `Party.save()` تولید می‌شود
3. **Account Level Validation**: `PartyAccountForm` فقط حساب‌های تفصیلی (`account_level=3`) را نمایش می‌دهد
4. **Primary Account**: هر طرف حساب می‌تواند یک حساب اصلی داشته باشد (`is_primary=1`)
5. **Party-Account Uniqueness**: هر ترکیب `(company, party, account)` باید یکتا باشد (constraint در مدل)

---

**Last Updated**: 2025-12-02


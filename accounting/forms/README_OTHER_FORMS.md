# accounting/forms/ - Other Forms (Complete Documentation)

**هدف**: مستندات کامل سایر فرم‌های ماژول accounting

این فایل شامل مستندات کامل فرم‌های زیر است:
- `DocumentAttachmentUploadForm`, `DocumentAttachmentFilterForm` (`document_attachments.py`)
- `GLAccountForm` (`gl_accounts.py`)
- `SubAccountForm` (`sub_accounts.py`)
- `TafsiliAccountForm` (`tafsili_accounts.py`)
- `TafsiliHierarchyForm` (`tafsili_hierarchy.py`)

---

## وابستگی‌ها

- `django.forms`: `ModelForm`, `Form`
- `django.utils.translation`: `gettext_lazy as _`
- `typing`: `Optional`
- `accounting.models`: `Account`, `TafsiliHierarchy`, `DocumentAttachment`, `AccountingDocument`, `SubAccountGLAccountRelation`, `TafsiliSubAccountRelation`
- `shared.models`: `Company`

---

## Document Attachment Forms

### `DocumentAttachmentUploadForm(forms.Form)`

**توضیح**: فرم برای آپلود پیوست‌های اسناد حسابداری

**Type**: `forms.Form` (نه ModelForm)

**Fields**:
- `document_number` (CharField, max_length=50, required=False): شماره سند حسابداری
  - Widget: `TextInput`
  - Label: `'شماره سند'`
  - Help Text: `'شماره سند حسابداری که می‌خواهید فایل را به آن مرتبط کنید'`
  - Placeholder: `'مثال: DOC-1403-001'`
- `files` (FileField, required=True): فایل‌های پیوست (multiple support)
  - Widget: `FileInput` (multiple=True, accept='image/*,.pdf,.doc,.docx')
  - Label: `'فایل‌ها'`
  - Help Text: `'می‌توانید یک یا چند فایل را انتخاب کنید (تصاویر فاکتور، رسید و...)'`
- `file_type` (ChoiceField, required=True): نوع فایل
  - Widget: `Select`
  - Label: `'نوع فایل'`
  - Choices: `[('', _('انتخاب کنید'))] + DocumentAttachment.FILE_TYPE_CHOICES`
- `description` (CharField, required=False): توضیحات
  - Widget: `Textarea` (rows=3)
  - Label: `'توضیحات'`

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company_id

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id` در `self.company_id`

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی document_number و جستجوی سند

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. فراخوانی `super().clean()`
2. دریافت `document_number` از cleaned_data
3. اگر `document_number` و `company_id` وجود دارند:
   - جستجوی `AccountingDocument` با `document_number` و `company_id`
   - در صورت یافت شدن، ذخیره در `self._document` برای استفاده بعدی
   - در صورت `DoesNotExist`: `ValidationError` با پیام "سندی با این شماره یافت نشد."
   - در صورت `MultipleObjectsReturned`: `ValidationError` با پیام "چند سند با این شماره یافت شد."
4. در غیر این صورت: `self._document = None`
5. برگرداندن cleaned_data

---

### `DocumentAttachmentFilterForm(forms.Form)`

**توضیح**: فرم برای فیلتر کردن پیوست‌های اسناد در لیست

**Type**: `forms.Form`

**Fields**:
- `document_number` (CharField, max_length=50, required=False): شماره سند
  - Widget: `TextInput`
  - Label: `'شماره سند'`
  - Placeholder: `'جستجو بر اساس شماره سند'`
- `file_type` (ChoiceField, required=False): نوع فایل
  - Widget: `Select`
  - Label: `'نوع فایل'`
  - Choices: `[('', _('همه'))] + DocumentAttachment.FILE_TYPE_CHOICES`
- `date_from` (DateField, required=False): از تاریخ
  - Widget: `DateInput` (type='date')
  - Label: `'از تاریخ'`
- `date_to` (DateField, required=False): تا تاریخ
  - Widget: `DateInput` (type='date')
  - Label: `'تا تاریخ'`
- `uploaded_by` (IntegerField, required=False): کاربر آپلودکننده
  - Widget: `HiddenInput`
  - Label: `'کاربر آپلودکننده'`

---

## GL Account Forms

### `GLAccountForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش حساب‌های کل (level 1)

**Model**: `Account`

**Fields**:
- `account_code` (CharField, max_length=20): کد کل
  - Widget: `TextInput`
  - Label: `'کد کل'`
  - Placeholder: `'مثال: 1 یا 10'`
  - Required: `True`
- `account_name` (CharField): نام کل
  - Widget: `TextInput`
  - Label: `'نام کل'`
  - Placeholder: `'مثال: دارایی'`
  - Required: `True`
- `account_name_en` (CharField, blank=True): نام کل (انگلیسی)
  - Widget: `TextInput`
  - Label: `'نام کل (انگلیسی)'`
  - Required: `False`
- `account_type` (CharField): نوع حساب
  - Widget: `Select`
  - Label: `'نوع حساب'`
  - Required: `True`
  - Choices: از مدل Account
- `normal_balance` (CharField): طرف تراز
  - Widget: `Select`
  - Label: `'طرف تراز'`
  - Required: `True`
  - Choices: از مدل Account
- `opening_balance` (DecimalField): مانده ابتدای دوره
  - Widget: `NumberInput` (step='0.01')
  - Label: `'مانده ابتدای دوره'`
  - Required: `False`
- `description` (TextField, blank=True): شرح
  - Widget: `Textarea` (rows=3)
  - Label: `'شرح'`
  - Required: `False`
- `is_enabled` (PositiveSmallIntegerField): وضعیت
  - Widget: `Select`
  - Label: `'وضعیت'`
  - Required: `False`

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company_id و تنظیم account_level

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id` در `self.company_id`
3. اگر instance جدید است (`not self.instance.pk`):
   - تنظیم `self.instance.account_level = 1` (حساب کل)
4. حذف فیلدهای غیرقابل تغییر:
   - حذف `account_level` (ثابت است)
   - حذف `parent_account` (ثابت است)
5. اگر `company_id` وجود دارد و instance جدید است:
   - دریافت Company و تنظیم `self.instance.company`

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی normal_balance بر اساس account_type و یکتایی کد

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. فراخوانی `super().clean()`
2. دریافت `account_type`, `normal_balance`, `account_code`
3. اعتبارسنجی normal_balance:
   - اگر `account_type` در `['ASSET', 'EXPENSE']` باشد: باید `normal_balance == 'DEBIT'`
   - اگر `account_type` در `['LIABILITY', 'EQUITY', 'REVENUE']` باشد: باید `normal_balance == 'CREDIT'`
   - در غیر این صورت: `ValidationError`
4. اعتبارسنجی یکتایی کد:
   - جستجوی حساب‌های موجود با همان `account_code`, `company_id`, و `account_level=1`
   - اگر instance در حال ویرایش است، از جستجو حذف می‌شود
   - در صورت وجود: `ValidationError` با پیام "کد کل باید یکتا باشد."
5. برگرداندن cleaned_data

---

## Sub Account Forms

### `SubAccountForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش حساب‌های معین (level 2) با ارتباط به حساب‌های کل

**Model**: `Account`

**Additional Fields**:
- `gl_accounts` (ModelMultipleChoiceField, required=True): حساب‌های کل مرتبط
  - Widget: `SelectMultiple` (size='5')
  - Label: `'حساب‌های کل مرتبط'`
  - Help Text: `'می‌توانید یک یا چند حساب کل را انتخاب کنید'`
  - Queryset: فیلتر شده بر اساس `company_id`, `account_level=1`, `is_enabled=1`

**Model Fields**:
- `account_code`: کد معین
- `account_name`: نام معین
- `account_name_en`: نام معین (انگلیسی)
- `normal_balance`: طرف تراز
- `opening_balance`: مانده ابتدای دوره
- `description`: شرح
- `is_enabled`: وضعیت

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, exclude_account_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company_id و فیلتر کردن GL accounts

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال
- `exclude_account_id` (Optional[int]): شناسه حساب برای حذف از queryset
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id`
3. تنظیم `account_level = 2` برای instance جدید
4. حذف فیلدهای غیرقابل تغییر: `account_level`, `account_type`, `parent_account`
5. اگر `company_id` وجود دارد:
   - فیلتر کردن `gl_accounts` queryset:
     - `company_id` مطابق
     - `account_level=1`
     - `is_enabled=1`
     - مرتب‌سازی بر اساس `account_code`
   - اگر instance در حال ویرایش است:
     - بارگذاری ارتباطات موجود از `SubAccountGLAccountRelation`
     - تنظیم `initial['gl_accounts']`
6. تنظیم company برای instance جدید

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی GL accounts و یکتایی کد

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. فراخوانی `super().clean()`
2. دریافت `gl_accounts`, `account_code`
3. اعتبارسنجی GL accounts:
   - باید حداقل یک حساب کل انتخاب شده باشد
   - همه حساب‌های کل باید متعلق به همان شرکت باشند
   - همه باید `account_level=1` باشند
   - همه باید نوع یکسانی داشته باشند
   - به‌ارث بردن `account_type` و `normal_balance` از اولین حساب کل
4. اعتبارسنجی یکتایی کد معین
5. برگرداندن cleaned_data

#### `save(self, commit=True) -> Account`

**توضیح**: ذخیره حساب و ایجاد/به‌روزرسانی ارتباطات با حساب‌های کل

**پارامترهای ورودی**:
- `commit` (bool): آیا instance ذخیره شود یا نه

**مقدار بازگشتی**:
- `Account`: instance ذخیره شده

**منطق**:
1. فراخوانی `super().save(commit=commit)`
2. اگر `commit=True` و `company_id` وجود دارد:
   - حذف ارتباطات موجود از `SubAccountGLAccountRelation`
   - ایجاد ارتباطات جدید برای هر GL account انتخاب شده
   - تنظیم `is_primary=1` برای اولین حساب (primary)
   - تنظیم `is_primary=0` برای بقیه
3. برگرداندن instance

---

## Tafsili Account Forms

### `TafsiliAccountForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش حساب‌های تفصیلی (level 3) با ارتباط به حساب‌های معین

**Model**: `Account`

**Additional Fields**:
- `tafsili_type` (ChoiceField, required=True): نوع تفصیلی
  - Widget: `Select`
  - Label: `'نوع تفصیلی'`
  - Choices: `TAFSILI_TYPE_CHOICES` (CUSTOMER, SUPPLIER, EMPLOYEE, PROJECT, COST_CENTER, BANK_ACCOUNT, CHECK, OTHER)
- `is_floating` (BooleanField, required=False): تفصیلی شناور
  - Widget: `CheckboxInput`
  - Label: `'تفصیلی شناور'`
  - Help Text: `'اگر فعال باشد، می‌تواند به چند معین ارتباط داده شود'`
- `national_id` (CharField, max_length=20, required=False): کد ملی / شناسه ملی / کد اقتصادی
  - Widget: `TextInput`
  - Label: `'کد ملی / شناسه ملی / کد اقتصادی'`
- `bank_account_number` (CharField, max_length=50, required=False): شماره حساب بانکی
  - Widget: `TextInput`
  - Label: `'شماره حساب بانکی'`
- `contact_info` (CharField, max_length=500, required=False): اطلاعات تماس
  - Widget: `Textarea` (rows=2)
  - Label: `'اطلاعات تماس (آدرس/تلفن/ایمیل)'`
- `sub_accounts` (ModelMultipleChoiceField, required=False): حساب‌های معین مرتبط
  - Widget: `SelectMultiple` (size='5')
  - Label: `'حساب‌های معین مرتبط'`
  - Help Text: `'می‌توانید یک یا چند حساب معین را انتخاب کنید'`
  - Queryset: فیلتر شده بر اساس `company_id`, `account_level=2`, `is_enabled=1`

**Model Fields**:
- `account_code`: کد تفصیلی
- `account_name`: نام تفصیلی
- `account_name_en`: نام تفصیلی (انگلیسی)
- `normal_balance`: طرف تراز
- `opening_balance`: مانده ابتدای دوره
- `description`: شرح
- `is_enabled`: وضعیت

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, exclude_account_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company_id و فیلتر کردن sub accounts

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال
- `exclude_account_id` (Optional[int]): شناسه حساب برای حذف از queryset
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id`
3. تنظیم `account_level = 3` برای instance جدید
4. حذف فیلدهای غیرقابل تغییر: `account_level`, `account_type`, `parent_account`
5. اگر `company_id` وجود دارد:
   - فیلتر کردن `sub_accounts` queryset:
     - `company_id` مطابق
     - `account_level=2`
     - `is_enabled=1`
     - مرتب‌سازی بر اساس `account_code`
   - اگر instance در حال ویرایش است:
     - بارگذاری ارتباطات موجود از `TafsiliSubAccountRelation`
     - تنظیم `initial['sub_accounts']`
     - اگر بیش از یک ارتباط وجود دارد: `initial['is_floating'] = True`
6. تنظیم company برای instance جدید

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی sub accounts و یکتایی کد

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. فراخوانی `super().clean()`
2. دریافت `sub_accounts`, `account_code`, `is_floating`
3. اعتبارسنجی sub accounts:
   - اگر `is_floating=False`: باید حداقل یک حساب معین انتخاب شده باشد
   - همه حساب‌های معین باید متعلق به همان شرکت باشند
   - همه باید `account_level=2` باشند
   - همه باید نوع یکسانی داشته باشند
   - به‌ارث بردن `account_type` و `normal_balance` از اولین حساب معین
4. اعتبارسنجی یکتایی کد تفصیلی
5. برگرداندن cleaned_data

#### `save(self, commit=True) -> Account`

**توضیح**: ذخیره حساب و ایجاد/به‌روزرسانی ارتباطات با حساب‌های معین

**پارامترهای ورودی**:
- `commit` (bool): آیا instance ذخیره شود یا نه

**مقدار بازگشتی**:
- `Account`: instance ذخیره شده

**منطق**:
1. فراخوانی `super().save(commit=commit)`
2. اگر `commit=True` و `company_id` وجود دارد:
   - حذف ارتباطات موجود از `TafsiliSubAccountRelation`
   - ایجاد ارتباطات جدید برای هر sub account انتخاب شده
   - تنظیم `is_primary=1` برای اولین حساب (primary)
   - تنظیم `is_primary=0` برای بقیه
3. برگرداندن instance

---

## Tafsili Hierarchy Forms

### `TafsiliHierarchyForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش تفصیلی چند سطحی

**Model**: `TafsiliHierarchy`

**Fields**:
- `code` (CharField, max_length=50): کد تفصیلی چند سطحی
  - Widget: `TextInput`
  - Label: `'کد تفصیلی چند سطحی'`
  - Required: `True`
  - Validators: `NUMERIC_CODE_VALIDATOR`
- `name` (CharField, max_length=200): نام تفصیلی چند سطحی
  - Widget: `TextInput`
  - Label: `'نام تفصیلی چند سطحی'`
  - Required: `True`
- `name_en` (CharField, max_length=200, blank=True): نام تفصیلی چند سطحی (انگلیسی)
  - Widget: `TextInput`
  - Label: `'نام تفصیلی چند سطحی (انگلیسی)'`
  - Required: `False`
- `parent` (ForeignKey to TafsiliHierarchy, null=True, blank=True): تفصیلی چند سطحی والد
  - Widget: `Select`
  - Label: `'تفصیلی چند سطحی والد'`
  - Required: `False`
  - Queryset: فیلتر شده بر اساس `company_id`, `is_enabled=1`، مرتب‌سازی بر اساس `level`, `sort_order`, `code`
- `tafsili_account` (ForeignKey to Account, null=True, blank=True, limit_choices_to={'account_level': 3}): تفصیلی اصلی مرتبط
  - Widget: `Select`
  - Label: `'تفصیلی اصلی مرتبط'`
  - Required: `False`
  - Queryset: فیلتر شده بر اساس `company_id`, `account_level=3`, `is_enabled=1`
- `sort_order` (PositiveSmallIntegerField, default=0): ترتیب نمایش
  - Widget: `NumberInput` (min='0')
  - Label: `'ترتیب نمایش'`
  - Required: `False`
- `description` (TextField, blank=True): توضیحات
  - Widget: `Textarea` (rows=3)
  - Label: `'توضیحات'`
  - Required: `False`
- `is_enabled` (PositiveSmallIntegerField): وضعیت
  - Widget: `Select`
  - Label: `'وضعیت'`
  - Required: `False`

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, exclude_hierarchy_id: Optional[int] = None, **kwargs)`

**توضیح**: Initialize form با company_id و فیلتر کردن parent و tafsili_account

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال
- `exclude_hierarchy_id` (Optional[int]): شناسه hierarchy برای حذف از parent choices
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id`
3. اگر `company_id` وجود دارد:
   - فیلتر کردن `parent` queryset:
     - `company_id` مطابق
     - `is_enabled=1`
     - اگر `exclude_hierarchy_id` وجود دارد، از queryset حذف می‌شود
     - مرتب‌سازی: `level`, `sort_order`, `code`
   - فیلتر کردن `tafsili_account` queryset:
     - `company_id` مطابق
     - `account_level=3` (فقط تفصیلی)
     - `is_enabled=1`
     - مرتب‌سازی: `account_code`
4. تنظیم `parent` و `tafsili_account` به optional
5. تنظیم company برای instance جدید

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی یکتایی کد

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. فراخوانی `super().clean()`
2. دریافت `code`, `parent`
3. اعتبارسنجی یکتایی کد:
   - جستجوی hierarchy های موجود با همان `code` و `company_id`
   - اگر instance در حال ویرایش است، از جستجو حذف می‌شود
   - در صورت وجود: `ValidationError` با پیام "کد تفصیلی چند سطحی باید یکتا باشد."
4. برگرداندن cleaned_data

---

## استفاده در پروژه

### Import Forms

```python
from accounting.forms import (
    GLAccountForm,
    SubAccountForm,
    TafsiliAccountForm,
    TafsiliHierarchyForm,
    DocumentAttachmentUploadForm,
    DocumentAttachmentFilterForm,
)
```

### استفاده در View ها

```python
# GL Account
form = GLAccountForm(company_id=request.session.get('active_company_id'))

# Sub Account
form = SubAccountForm(company_id=request.session.get('active_company_id'))

# Tafsili Account
form = TafsiliAccountForm(company_id=request.session.get('active_company_id'))

# Tafsili Hierarchy
form = TafsiliHierarchyForm(
    company_id=request.session.get('active_company_id'),
    exclude_hierarchy_id=instance.pk if instance.pk else None
)

# Document Attachment Upload
form = DocumentAttachmentUploadForm(company_id=request.session.get('active_company_id'))
```

---

## نکات مهم

1. **Company Scoping**: تمام forms از `company_id` برای فیلتر کردن queryset ها استفاده می‌کنند
2. **Account Level**: `account_level` به صورت خودکار تنظیم می‌شود (1=کل، 2=معین، 3=تفصیلی)
3. **Relation Management**: `SubAccountForm` و `TafsiliAccountForm` از M2M fields استفاده می‌کنند و در `save()` ارتباطات را مدیریت می‌کنند
4. **Floating Tafsili**: `TafsiliAccountForm` از `is_floating` برای پشتیبانی از تفصیلی شناور استفاده می‌کند
5. **Hierarchy Structure**: `TafsiliHierarchyForm` از `parent` برای ساختار سلسله‌مراتبی استفاده می‌کند
6. **Code Validation**: تمام forms یکتایی کد را در سطح company اعتبارسنجی می‌کنند
7. **Type Inheritance**: `SubAccountForm` و `TafsiliAccountForm` نوع حساب و طرف تراز را از اولین حساب مرتبط به‌ارث می‌برند

---

**Last Updated**: 2025-12-02

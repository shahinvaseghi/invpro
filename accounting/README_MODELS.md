# accounting/models.py - Accounting Models (Complete Documentation)

**هدف**: تمام model classes برای ماژول Accounting

این فایل شامل **20 model class** است که به دسته‌های زیر تقسیم می‌شوند:
- Base Models (Abstract)
- Fiscal Year Management Models
- Chart of Accounts Models
- Accounting Document Models
- Party Management Models
- Cost Center Models
- Income/Expense Category Models
- Hierarchy Models
- Attachment Models
- Account Relation Models

---

## وابستگی‌ها

- `shared.models`: `ActivatableModel`, `CompanyScopedModel`, `LockableModel`, `MetadataModel`, `SortableModel`, `TimeStampedModel`, `NUMERIC_CODE_VALIDATOR`, `ENABLED_FLAG_CHOICES`
- `inventory.utils.codes`: `generate_sequential_code` (برای استفاده در آینده)
- `django.db.models`
- `django.core.validators`: `MinValueValidator`, `RegexValidator`
- `django.utils.timezone`
- `django.conf.settings`: `AUTH_USER_MODEL`
- `decimal.Decimal`

---

## Validators و Constants

### `POSITIVE_DECIMAL`
- `MinValueValidator(Decimal("0"))`: مقادیر مثبت یا صفر

---

## Helper Functions

### `get_fiscal_year_from_date(company_id: int, document_date) -> Optional[FiscalYear]`

**توضیح**: دریافت سال مالی برای یک company و date مشخص.

**پارامترهای ورودی**:
- `company_id` (int): شناسه شرکت
- `document_date`: تاریخ سند (Date)

**مقدار بازگشتی**:
- `Optional[FiscalYear]`: سال مالی که شامل `document_date` است، یا `None` اگر پیدا نشود

**منطق**:
1. جستجو برای `FiscalYear` با:
   - `company_id=company_id`
   - `start_date__lte=document_date`
   - `end_date__gte=document_date`
   - `is_enabled=1`
2. اگر یک سال مالی پیدا شود، return آن
3. اگر `FiscalYear.DoesNotExist` رخ دهد، return `None`
4. اگر `FiscalYear.MultipleObjectsReturned` رخ دهد:
   - فیلتر و مرتب‌سازی بر اساس `-start_date`
   - return اولین (most recent)

**نکات مهم**:
- فقط enabled fiscal years در نظر گرفته می‌شوند
- اگر چند سال مالی match کنند، most recent (بزرگترین start_date) انتخاب می‌شود

---

## Base Models (Abstract)

### `AccountingBaseModel`

**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `MetadataModel`

**توضیح**: Base model برای تمام accounting models

**Fields** (از mixins):
- `company` (ForeignKey): Company scope
- `company_code` (CharField): Cached company code
- `created_at`, `edited_at` (DateTime): Timestamps
- `created_by`, `edited_by` (ForeignKey): User references
- `is_enabled` (PositiveSmallIntegerField): Activation flag
- `enabled_at`, `disabled_at` (DateTime): Activation timestamps
- `enabled_by`, `disabled_by` (ForeignKey): Activation user references
- `metadata` (JSONField): Extensible metadata

**Methods**:
- هیچ متد خاصی ندارد (abstract base)

---

### `AccountingSortableModel`

**Inheritance**: `AccountingBaseModel`, `SortableModel`

**توضیح**: Base model با sort_order برای entities قابل مرتب‌سازی

**Fields** (اضافی):
- `sort_order` (PositiveSmallIntegerField): ترتیب نمایش

---

### `FiscalYearMixin`

**Inheritance**: `models.Model` (abstract mixin)

**توضیح**: Mixin برای auto-populate کردن `fiscal_year_id` از `document_date`.

**Fields**:
- `fiscal_year` (ForeignKey to FiscalYear, null=True, blank=True): سال مالی (auto-populated)

**Methods**:

#### `get_document_date_field_name(self) -> str`
- **Returns**: نام field برای document date (default: `'document_date'`)
- **Logic**: می‌تواند override شود اگر field name متفاوت باشد

#### `save(self, *args, **kwargs) -> None`
- **Logic**:
  1. اگر `fiscal_year_id` موجود نباشد:
     - دریافت `document_date` از field (از `get_document_date_field_name()`)
     - اگر `document_date` و `company_id` موجود باشند:
       - فراخوانی `get_fiscal_year_from_date(company_id, document_date)`
       - اگر fiscal year پیدا شود: `self.fiscal_year = fiscal_year`
  2. فراخوانی `super().save()`

#### `clean(self) -> None`
- **Logic**:
  1. دریافت `document_date` از field
  2. اگر `document_date` و `fiscal_year` موجود باشند:
     - بررسی: `document_date >= fiscal_year.start_date`
     - اگر نه: raise `ValidationError` ("Document date is before fiscal year start date")
     - بررسی: `document_date <= fiscal_year.end_date`
     - اگر نه: raise `ValidationError` ("Document date is after fiscal year end date")
  3. فراخوانی `super().clean()`

**نکات مهم**:
- برای models با `document_date` استفاده می‌شود
- `fiscal_year` به صورت خودکار از `document_date` populate می‌شود
- Validation: `document_date` باید در range `fiscal_year` باشد

---

### `AccountingDocumentBase`

**Inheritance**: `AccountingBaseModel`, `LockableModel`, `FiscalYearMixin`

**توضیح**: Base model برای document-style models با fiscal year support

**Fields**:
- `document_code` (CharField, max_length=30, blank=True, editable=False): کد سند (auto-generated)
- `document_date` (DateField, default=timezone.now): تاریخ سند
- `notes` (TextField, blank=True): یادداشت‌ها
- `fiscal_year` (ForeignKey to FiscalYear, null=True, blank=True): سال مالی (auto-populated از `document_date` - از `FiscalYearMixin`)
- `is_locked` (PositiveSmallIntegerField): Lock status (از LockableModel)
- `locked_at`, `unlocked_at` (DateTime): Lock timestamps
- `locked_by`, `unlocked_by` (ForeignKey): Lock user references
- `editing_by`, `editing_started_at`, `editing_session_key` (از LockableModel): Edit lock fields

**Methods**:
- از `FiscalYearMixin` استفاده می‌کند که `fiscal_year` را از `document_date` auto-populate می‌کند

---

## Fiscal Year Management Models

### `FiscalYear`

**Inheritance**: `AccountingBaseModel`

**توضیح**: تعریف سال مالی برای دوره‌های حسابداری

**Fields**:
- `fiscal_year_code` (CharField, max_length=10, validators=[NUMERIC_CODE_VALIDATOR]): کد سال مالی (مثلاً '1403')
- `fiscal_year_name` (CharField, max_length=100): نام سال مالی
- `start_date` (DateField): تاریخ شروع سال مالی
- `end_date` (DateField): تاریخ پایان سال مالی
- `is_current` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): پرچم سال مالی جاری
- `is_closed` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): پرچم سال مالی بسته شده
- `closed_at` (DateTimeField, null=True, blank=True): زمان بسته شدن سال مالی
- `closed_by` (ForeignKey to User, null=True, blank=True): کاربری که سال مالی را بسته است
- `opening_document_id` (BigIntegerField, null=True, blank=True): ارجاع به سند افتتاحیه (در آینده FK به AccountingDocument)
- `closing_document_id` (BigIntegerField, null=True, blank=True): ارجاع به سند اختتامیه (در آینده FK به AccountingDocument)

**Constraints**:
- Unique: `(company, fiscal_year_code)`

**Ordering**: `("company", "-fiscal_year_code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای سال مالی

**مقدار بازگشتی**:
- `str`: `"{fiscal_year_code} - {fiscal_year_name}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی تاریخ‌های سال مالی

**منطق**:
1. بررسی می‌کند که `start_date` و `end_date` وجود داشته باشند
2. بررسی می‌کند که `end_date` بعد از `start_date` باشد
3. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. `clean()` را فراخوانی می‌کند
2. `super().save()` را فراخوانی می‌کند

---

### `Period`

**Inheritance**: `AccountingBaseModel`

**توضیح**: دوره حسابداری درون یک سال مالی (معمولاً ماهانه)

**Fields**:
- `fiscal_year` (ForeignKey to FiscalYear, on_delete=CASCADE): سال مالی مربوطه
- `period_code` (CharField, max_length=10): کد دوره (مثلاً '1403-01')
- `period_name` (CharField, max_length=100): نام دوره
- `start_date` (DateField): تاریخ شروع دوره
- `end_date` (DateField): تاریخ پایان دوره
- `is_closed` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): پرچم دوره بسته شده
- `closed_at` (DateTimeField, null=True, blank=True): زمان بسته شدن دوره
- `closed_by` (ForeignKey to User, null=True, blank=True): کاربری که دوره را بسته است

**Constraints**:
- Unique: `(company, fiscal_year, period_code)`

**Ordering**: `("company", "fiscal_year", "period_code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای دوره

**مقدار بازگشتی**:
- `str`: `"{period_code} - {period_name}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی تاریخ‌های دوره

**منطق**:
1. بررسی می‌کند که `start_date` و `end_date` وجود داشته باشند
2. بررسی می‌کند که `end_date` بعد از `start_date` باشد
3. اگر `fiscal_year` وجود دارد:
   - بررسی می‌کند که `start_date` در محدوده سال مالی باشد
   - بررسی می‌کند که `end_date` در محدوده سال مالی باشد
4. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. `clean()` را فراخوانی می‌کند
2. `super().save()` را فراخوانی می‌کند

---

## Chart of Accounts Models

### `Account`

**Inheritance**: `AccountingSortableModel`

**توضیح**: حساب‌های کل، معین و تفصیلی (Chart of Accounts)

**Choices**:
- `ACCOUNT_TYPE_CHOICES`: `'ASSET'`, `'LIABILITY'`, `'EQUITY'`, `'REVENUE'`, `'EXPENSE'`
- `ACCOUNT_LEVEL_CHOICES`: `1` (General Ledger - کل), `2` (Subsidiary Ledger - معین), `3` (Detail Ledger - تفصیلی)
- `NORMAL_BALANCE_CHOICES`: `'DEBIT'`, `'CREDIT'`

**Fields**:
- `account_code` (CharField, max_length=20, validators=[NUMERIC_CODE_VALIDATOR]): کد سلسله‌مراتبی حساب (مثلاً '1.01.001')
- `account_name` (CharField, max_length=200): نام فارسی/محلی حساب
- `account_name_en` (CharField, max_length=200, blank=True): نام انگلیسی حساب
- `account_type` (CharField, max_length=30, choices=ACCOUNT_TYPE_CHOICES): نوع حساب
- `account_level` (PositiveSmallIntegerField, choices=ACCOUNT_LEVEL_CHOICES): سطح حساب (1=کل، 2=معین، 3=تفصیلی)
- `parent_account` (ForeignKey to 'self', on_delete=PROTECT, null=True, blank=True): حساب والد برای ساختار سلسله‌مراتبی
- `normal_balance` (CharField, max_length=10, choices=NORMAL_BALANCE_CHOICES): طرف مانده عادی
- `is_system_account` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): حساب‌های سیستم قابل حذف نیستند
- `opening_balance` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مانده افتتاحیه برای سال مالی جاری
- `current_balance` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), editable=False): مانده دوره جاری (محاسبه شده)
- `description` (TextField, blank=True): توضیحات و یادداشت‌های استفاده

**Constraints**:
- Unique: `(company, account_code)`

**Ordering**: `("company", "account_code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای حساب

**مقدار بازگشتی**:
- `str`: `"{account_code} - {account_name}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی ساختار حساب

**منطق**:
1. اگر `parent_account` وجود دارد:
   - بررسی می‌کند که `parent_account` متعلق به همان شرکت باشد
   - بررسی می‌کند که سطح حساب والد کمتر از سطح حساب فرزند باشد
2. اعتبارسنجی `normal_balance` بر اساس `account_type`:
   - اگر `account_type` در `['ASSET', 'EXPENSE']` باشد، `normal_balance` باید `'DEBIT'` باشد
   - اگر `account_type` در `['LIABILITY', 'EQUITY', 'REVENUE']` باشد، `normal_balance` باید `'CREDIT'` باشد
3. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. `clean()` را فراخوانی می‌کند
2. `super().save()` را فراخوانی می‌کند

---

### `AccountBalance`

**Inheritance**: `AccountingBaseModel`

**توضیح**: ردیابی مانده حساب‌ها بر اساس دوره

**Fields**:
- `account` (ForeignKey to Account, on_delete=CASCADE): حساب مربوطه
- `fiscal_year` (ForeignKey to FiscalYear, on_delete=CASCADE): سال مالی برای ردیابی مانده
- `period_start` (DateField): تاریخ شروع دوره مانده
- `period_end` (DateField): تاریخ پایان دوره مانده
- `debit_total` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مجموع بدهکارها در دوره
- `credit_total` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مجموع بستانکارها در دوره
- `opening_balance` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00')): مانده در شروع دوره
- `closing_balance` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00')): مانده در پایان دوره
- `updated_at` (DateTimeField, auto_now=True): زمان آخرین به‌روزرسانی

**Constraints**:
- Unique: `(company, account, fiscal_year, period_start, period_end)`

**Ordering**: `("company", "fiscal_year", "period_start")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای مانده حساب

**مقدار بازگشتی**:
- `str`: `"{account.account_code} - {period_start} to {period_end}"`

---

## Accounting Document Models

### `AccountingDocument`

**Inheritance**: `AccountingDocumentBase` (که شامل `FiscalYearMixin` است)

**توضیح**: سند حسابداری - رکورد تراکنشی اصلی که از اصول دفترداری دوطرفه پیروی می‌کند

**Choices**:
- `DOCUMENT_TYPE_CHOICES`: `'MANUAL'`, `'AUTOMATIC'`, `'OPENING'`, `'CLOSING'`, `'ADJUSTMENT'`
- `STATUS_CHOICES`: `'DRAFT'`, `'POSTED'`, `'LOCKED'`, `'REVERSED'`, `'CANCELLED'`

**Fields**:
- `document_number` (CharField, max_length=30, unique=True, editable=False): شماره سند (auto-generated)
- `document_type` (CharField, max_length=30, choices=DOCUMENT_TYPE_CHOICES): نوع سند
- `fiscal_year` (ForeignKey to FiscalYear, on_delete=PROTECT, null=False): سال مالی سند (required - override از FiscalYearMixin که null=True بود)
- `period` (ForeignKey to Period, on_delete=SET_NULL, null=True, blank=True): ارجاع اختیاری به دوره
- `description` (TextField): توضیحات/شرح سند
- `reference_number` (CharField, max_length=100, blank=True): شماره مرجع خارجی (شماره فاکتور، شماره رسید و غیره)
- `reference_type` (CharField, max_length=50, blank=True): نوع مرجع (مثلاً 'INVENTORY_RECEIPT', 'SALES_INVOICE')
- `reference_id` (BigIntegerField, null=True, blank=True): کلید خارجی به سند مرجع (polymorphic)
- `total_debit` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مجموع تمام خطوط بدهکار
- `total_credit` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مجموع تمام خطوط بستانکار (باید برابر total_debit باشد)
- `status` (CharField, max_length=20, choices=STATUS_CHOICES, default='DRAFT'): وضعیت workflow سند
- `posted_at` (DateTimeField, null=True, blank=True): زمان ثبت سند
- `posted_by` (ForeignKey to User, null=True, blank=True): کاربری که سند را ثبت کرده است
- `locked_at` (DateTimeField, null=True, blank=True): زمان قفل شدن سند (override از LockableModel)
- `locked_by` (ForeignKey to User, null=True, blank=True): کاربری که سند را قفل کرده است (override از LockableModel)
- `reversed_document` (ForeignKey to 'self', on_delete=SET_NULL, null=True, blank=True, related_name='reversal_documents'): ارجاع به سند معکوس در صورت معکوس شدن
- `attachment_count` (PositiveSmallIntegerField, default=0): تعداد فایل‌های پیوست شده

**Constraints**:
- Unique: `(company, document_number)`
- Check: `total_debit = total_credit` (در سطح دیتابیس)

**Ordering**: `("company", "-document_date", "-document_number")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای سند

**مقدار بازگشتی**:
- `str`: `"{document_number} - {document_date}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی مجموع سند

**منطق**:
1. بررسی می‌کند که `total_debit` برابر `total_credit` باشد
2. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. `clean()` را فراخوانی می‌کند
2. `super().save()` را فراخوانی می‌کند

---

### `AccountingDocumentLine`

**Inheritance**: `AccountingBaseModel`

**توضیح**: خطوط سند حسابداری با support برای account hierarchy (کل، معین، تفصیلی)

**Fields**:
- `document` (ForeignKey to AccountingDocument, on_delete=CASCADE, related_name='lines'): سند والد
- `line_number` (PositiveSmallIntegerField): شماره خط متوالی درون سند
- `gl_account` (ForeignKey to Account, on_delete=PROTECT, related_name='document_lines_as_gl', limit_choices_to={'account_level': 1}, null=True, blank=True): حساب کل (GL Account)
- `sub_account` (ForeignKey to Account, on_delete=PROTECT, related_name='document_lines_as_sub', limit_choices_to={'account_level': 2}, null=True, blank=True): حساب معین (Sub Account) - Optional
- `tafsili_account` (ForeignKey to Account, on_delete=PROTECT, related_name='document_lines_as_tafsili', limit_choices_to={'account_level': 3}, null=True, blank=True): حساب تفصیلی (Tafsili Account) - Optional
- `description` (CharField, max_length=255, blank=True): توضیحات خط
- `debit` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مبلغ بدهکار
- `credit` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مبلغ بستانکار
- `sort_order` (PositiveSmallIntegerField, default=0): ترتیب نمایش

**Constraints**:
- Unique: `(company, document, line_number)`
- Check: `(debit > 0 AND credit = 0) OR (debit = 0 AND credit > 0)` - هر خط باید یا بدهکار یا بستانکار باشد، نه هر دو

**Ordering**: `("company", "document", "sort_order", "line_number")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای خط سند

**مقدار بازگشتی**:
- `str`: `"{document.document_number} - Line {line_number}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی مبالغ خط و account hierarchy

**منطق**:
1. **بررسی debit/credit**:
   - اگر `debit > 0` و `credit > 0` باشد: raise `ValidationError` ("Line must be either debit or credit, not both.")
   - اگر `debit == 0` و `credit == 0` باشد: raise `ValidationError` ("Line must have either debit or credit amount.")
2. **بررسی account hierarchy**:
   - اگر `sub_account` موجود باشد:
     - بررسی: `sub_account.gl_account_relations.filter(gl_account=self.gl_account).exists()`
     - اگر نه: raise `ValidationError` ("Selected sub account is not related to the selected GL account.")
   - اگر `tafsili_account` موجود باشد:
     - اگر `sub_account` موجود باشد:
       - بررسی: `tafsili_account.tafsili_sub_relations.filter(sub_account=self.sub_account).exists()`
       - اگر نه: raise `ValidationError` ("Selected tafsili account is not related to the selected sub account.")
     - اگر `sub_account` موجود نباشد:
       - دریافت sub_accounts از `gl_account`: `Account.objects.filter(gl_account_relations__gl_account=self.gl_account)`
       - بررسی: `tafsili_account.tafsili_sub_relations.filter(sub_account__in=sub_accounts).exists()`
       - اگر نه: raise `ValidationError` ("Selected tafsili account is not related to any sub account of the selected GL account.")

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. `clean()` را فراخوانی می‌کند
2. `super().save()` را فراخوانی می‌کند

**نکات مهم**:
- Account hierarchy validation: sub_account باید به gl_account مرتبط باشد، tafsili_account باید به sub_account (یا sub_accounts از gl_account) مرتبط باشد
- از `SubAccountGLAccountRelation` و `TafsiliSubAccountRelation` برای validation استفاده می‌شود

---

## استفاده در پروژه

### Base Models
- `AccountingBaseModel`: برای تمام models حسابداری استفاده می‌شود
- `AccountingSortableModel`: برای entities قابل مرتب‌سازی (مثل Account)
- `AccountingDocumentBase`: برای document-style models (مثل AccountingDocument)

### Fiscal Year Management
- `FiscalYear`: برای تعریف سال‌های مالی
- `Period`: برای تعریف دوره‌های حسابداری درون سال مالی

### Chart of Accounts
- `Account`: برای ساختار سلسله‌مراتبی حساب‌ها (کل، معین، تفصیلی)
- `AccountBalance`: برای ردیابی مانده حساب‌ها بر اساس دوره

### Accounting Documents
- `AccountingDocument`: برای اسناد حسابداری با اصول دفترداری دوطرفه
- `AccountingDocumentLine`: برای خطوط اسناد حسابداری

---

## نکات مهم

1. **Double-Entry Bookkeeping**: تمام اسناد باید `total_debit = total_credit` داشته باشند (در سطح model و database constraint)
2. **Account Hierarchy**: حساب‌ها می‌توانند ساختار سلسله‌مراتبی داشته باشند (parent_account)
3. **Normal Balance Validation**: `normal_balance` بر اساس `account_type` اعتبارسنجی می‌شود
4. **System Accounts**: حساب‌های سیستم (`is_system_account=1`) قابل حذف نیستند
5. **Document Line Validation**: هر خط باید یا بدهکار یا بستانکار باشد، نه هر دو (constraint در database)
6. **Account Hierarchy Validation**: در `AccountingDocumentLine`، sub_account باید به gl_account مرتبط باشد و tafsili_account باید به sub_account مرتبط باشد
7. **Fiscal Year Auto-Population**: از `FiscalYearMixin` برای auto-populate کردن `fiscal_year` از `document_date` استفاده می‌شود
8. **Fiscal Year Constraints**: دوره‌ها باید در محدوده سال مالی مربوطه باشند
9. **Company Scoping**: تمام models بر اساس `company` ایزوله می‌شوند
10. **Forward References**: `opening_document_id`, `closing_document_id`, `party_id`, `cost_center_id` به صورت BigIntegerField هستند و در آینده به ForeignKey تبدیل می‌شوند

---

## Party Management Models

### `Party`

**Inheritance**: `AccountingSortableModel`

**توضیح**: مدل طرف حساب برای ردیابی مشتریان، تأمین‌کنندگان و سایر شرکای تجاری

**Choices**:
- `party_type`: `'customer'` (مشتری), `'supplier'` (تأمین‌کننده), `'employee'` (کارمند), `'other'` (سایر)

**Fields**:
- `party_type` (CharField, max_length=20): نوع طرف حساب
- `party_code` (CharField, max_length=10, validators=[NUMERIC_CODE_VALIDATOR], blank=True, editable=False): کد طرف حساب (auto-generated)
- `party_name` (CharField, max_length=200): نام طرف حساب (فارسی)
- `party_name_en` (CharField, max_length=200, blank=True): نام طرف حساب (انگلیسی)
- `national_id` (CharField, max_length=20, blank=True): کد ملی / شماره ثبت
- `tax_id` (CharField, max_length=20, blank=True): شناسه مالیاتی
- `address` (TextField, blank=True): آدرس
- `phone` (CharField, max_length=50, blank=True): شماره تلفن
- `email` (EmailField, blank=True): آدرس ایمیل
- `contact_person` (CharField, max_length=200, blank=True): شخص رابط
- `notes` (TextField, blank=True): توضیحات اضافی

**Constraints**:
- Unique: `(company, party_code)`
- Unique: `(company, party_name)`

**Ordering**: `("company", "party_type", "sort_order", "party_code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای طرف حساب

**مقدار بازگشتی**:
- `str`: `"{party_code} - {party_name}"`

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با auto-generation کد طرف حساب

**منطق**:
1. اگر `party_code` وجود ندارد و `company_id` و `party_type` موجود هستند:
   - تولید کد متوالی با `generate_sequential_code()`
   - فیلتر اضافی: `{"party_type": self.party_type}`
   - عرض کد: 10 رقم
2. فراخوانی `super().save()`

---

### `PartyAccount`

**Inheritance**: `AccountingSortableModel`

**توضیح**: مدل حساب طرف حساب برای ارتباط طرف حساب با حساب‌های تفصیلی

**Fields**:
- `party` (ForeignKey to Party, on_delete=CASCADE, related_name='accounts'): طرف حساب مربوطه
- `account` (ForeignKey to Account, on_delete=PROTECT, related_name='party_accounts', limit_choices_to={'account_level': 3}): حساب تفصیلی
- `account_code` (CharField, max_length=30, blank=True, editable=False): کد حساب (کش شده)
- `account_name` (CharField, max_length=200, blank=True, editable=False): نام حساب (کش شده)
- `is_primary` (PositiveSmallIntegerField, default=0): حساب اصلی (1=بله، 0=خیر)
- `notes` (TextField, blank=True): توضیحات درباره این حساب

**Constraints**:
- Unique: `(company, party, account)`

**Ordering**: `("company", "party", "-is_primary", "account_code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای حساب طرف حساب

**مقدار بازگشتی**:
- `str`: `"{party.party_name} - {account.account_code}"`

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با cache کردن کد و نام حساب

**منطق**:
1. اگر `account` وجود دارد:
   - اگر `account_code` خالی است، از `account.account_code` پر می‌شود
   - اگر `account_name` خالی است، از `account.account_name` پر می‌شود
2. فراخوانی `super().save()`

---

## Cost Center Models

### `CostCenter`

**Inheritance**: `AccountingSortableModel`

**توضیح**: مدل مرکز هزینه برای ردیابی هزینه‌ها بر اساس واحد سازمانی و خط کاری

**Fields**:
- `cost_center_code` (CharField, max_length=10, validators=[NUMERIC_CODE_VALIDATOR], blank=True, editable=False): کد مرکز هزینه (auto-generated)
- `cost_center_name` (CharField, max_length=200): نام مرکز هزینه (فارسی)
- `cost_center_name_en` (CharField, max_length=200, blank=True): نام مرکز هزینه (انگلیسی)
- `company_unit` (ForeignKey to 'shared.CompanyUnit', on_delete=PROTECT, related_name='cost_centers'): واحد سازمانی که این مرکز هزینه به آن تعلق دارد
- `company_unit_code` (CharField, max_length=5, validators=[NUMERIC_CODE_VALIDATOR], blank=True, editable=False): کد واحد سازمانی (کش شده)
- `work_line` (ForeignKey to 'production.WorkLine', on_delete=SET_NULL, related_name='cost_centers', null=True, blank=True): خط کاری تولید (اختیاری - فقط در صورت نصب ماژول تولید)
- `work_line_code` (CharField, max_length=5, validators=[NUMERIC_CODE_VALIDATOR], blank=True, editable=False): کد خط کاری (کش شده)
- `description` (TextField, blank=True): توضیحات و یادداشت‌ها درباره این مرکز هزینه

**Constraints**:
- Unique: `(company, cost_center_code)`
- Unique: `(company, cost_center_name)`

**Ordering**: `("company", "sort_order", "cost_center_code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای مرکز هزینه

**مقدار بازگشتی**:
- `str`: `"{cost_center_code} - {cost_center_name}"`

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با auto-generation کد و cache کردن کدها

**منطق**:
1. اگر `cost_center_code` وجود ندارد و `company_id` موجود است:
   - تولید کد متوالی با `generate_sequential_code()`
   - عرض کد: 10 رقم
2. اگر `company_unit` وجود دارد و `company_unit_code` خالی است:
   - Cache کردن `company_unit.public_code` در `company_unit_code`
3. اگر `work_line` وجود دارد و `work_line_code` خالی است:
   - Cache کردن `work_line.public_code` در `work_line_code`
4. فراخوانی `super().save()`

---

## Income/Expense Category Models

### `IncomeExpenseCategory`

**Inheritance**: `AccountingSortableModel`

**توضیح**: مدل دسته‌بندی برای طبقه‌بندی تراکنش‌های درآمد و هزینه

**Choices**:
- `category_type`: `'income'` (درآمد), `'expense'` (هزینه)

**Fields**:
- `category_type` (CharField, max_length=20): نوع دسته‌بندی (درآمد یا هزینه)
- `category_code` (CharField, max_length=10, validators=[NUMERIC_CODE_VALIDATOR], blank=True, editable=False): کد دسته‌بندی (auto-generated)
- `category_name` (CharField, max_length=200): نام دسته‌بندی (فارسی)
- `category_name_en` (CharField, max_length=200, blank=True): نام دسته‌بندی (انگلیسی)
- `description` (TextField, blank=True): توضیحات و یادداشت‌ها درباره این دسته‌بندی

**Constraints**:
- Unique: `(company, category_type, category_code)`
- Unique: `(company, category_type, category_name)`

**Ordering**: `("company", "category_type", "sort_order", "category_code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای دسته‌بندی

**مقدار بازگشتی**:
- `str`: `"{type_label} - {category_code} - {category_name}"` (type_label: "درآمد" یا "هزینه")

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با auto-generation کد دسته‌بندی

**منطق**:
1. اگر `category_code` وجود ندارد و `company_id` و `category_type` موجود هستند:
   - تولید کد متوالی با `generate_sequential_code()`
   - فیلتر اضافی: `{"category_type": self.category_type}`
   - عرض کد: 10 رقم
2. فراخوانی `super().save()`

---

## Hierarchy Models

### `TafsiliHierarchy`

**Inheritance**: `AccountingBaseModel`

**توضیح**: ساختار سلسله‌مراتبی برای تفصیلی چند سطحی - امکان ایجاد ساختار درختی برای سازماندهی و طبقه‌بندی بهتر حساب‌های تفصیلی

**Fields**:
- `code` (CharField, max_length=50, validators=[NUMERIC_CODE_VALIDATOR]): کد تفصیلی چند سطحی (یکتا در شرکت)
- `name` (CharField, max_length=200): نام تفصیلی چند سطحی
- `name_en` (CharField, max_length=200, blank=True): نام تفصیلی چند سطحی (انگلیسی)
- `parent` (ForeignKey to 'self', on_delete=CASCADE, related_name='children', null=True, blank=True): تفصیلی چند سطحی والد (برای ساختار درختی)
- `tafsili_account` (ForeignKey to Account, on_delete=SET_NULL, related_name='hierarchies', null=True, blank=True, limit_choices_to={'account_level': 3}): تفصیلی اصلی مرتبط (اختیاری - برای ریشه‌های درخت)
- `level` (PositiveSmallIntegerField, default=1, editable=False): سطح در درخت (1=ریشه، 2=زیرگروه اول، ...)
- `sort_order` (PositiveSmallIntegerField, default=0): ترتیب نمایش
- `description` (TextField, blank=True): توضیحات

**Constraints**:
- Unique: `(company, code)`

**Ordering**: `("company", "level", "sort_order", "code")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای تفصیلی چند سطحی

**مقدار بازگشتی**:
- `str`: `"{code} - {name}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی ساختار سلسله‌مراتبی

**منطق**:
1. اگر `parent` وجود دارد:
   - بررسی می‌کند که `parent` متعلق به همان شرکت باشد
   - بررسی می‌کند که circular reference وجود نداشته باشد (یک node نمی‌تواند والد خودش باشد)
   - عمق بررسی: حداکثر 100 سطح (safety limit)
2. اگر `tafsili_account` ارائه شده:
   - بررسی می‌کند که `tafsili_account` متعلق به همان شرکت باشد
   - بررسی می‌کند که `account_level = 3` باشد (فقط تفصیلی)
3. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با محاسبه level و اعتبارسنجی

**منطق**:
1. محاسبه `level` بر اساس `parent`:
   - اگر `parent` وجود دارد: `level = parent.level + 1`
   - در غیر این صورت: `level = 1`
2. فراخوانی `clean()` برای اعتبارسنجی
3. فراخوانی `super().save()`
4. به‌روزرسانی سطح children در صورت تغییر level:
   - برای هر child، `save()` را فراخوانی می‌کند تا level آن‌ها دوباره محاسبه شود

#### `get_full_path(self) -> str`

**توضیح**: دریافت مسیر کامل از ریشه تا این node

**مقدار بازگشتی**:
- `str`: مسیر کامل با فرمت `"root > parent > ... > current"`

**منطق**:
1. شروع از node فعلی
2. پیمایش به بالا از طریق `parent`
3. جمع‌آوری نام‌ها در لیست
4. برگرداندن مسیر با separator `" > "`

#### `get_full_code_path(self) -> str`

**توضیح**: دریافت مسیر کامل کد از ریشه تا این node

**مقدار بازگشتی**:
- `str`: مسیر کامل کد با فرمت `"code1 > code2 > ... > current_code"`

**منطق**:
1. شروع از node فعلی
2. پیمایش به بالا از طریق `parent`
3. جمع‌آوری کدها در لیست
4. برگرداندن مسیر با separator `" > "`

---

## Attachment Models

### `DocumentAttachment`

**Inheritance**: `AccountingBaseModel`

**توضیح**: مدل فایل‌های پیوست برای اسناد حسابداری (مثل تصاویر فاکتور، رسید). امکان آپلود و اتصال فایل‌ها به اسناد حسابداری

**Choices**:
- `FILE_TYPE_CHOICES`: `'INVOICE'` (فاکتور), `'RECEIPT'` (رسید), `'CONTRACT'` (قرارداد), `'CHECK'` (چک), `'OTHER'` (سایر)

**Fields**:
- `document` (ForeignKey to AccountingDocument, on_delete=CASCADE, related_name='attachments', null=True, blank=True): سند حسابداری مرتبط (اختیاری)
- `document_number` (CharField, max_length=50, blank=True): شماره سند (برای جستجو و فیلتر)
- `file` (FileField, upload_to='accounting/documents/%Y/%m/'): فایل پیوست
- `file_type` (CharField, max_length=30, choices=FILE_TYPE_CHOICES, default='OTHER'): نوع فایل
- `file_name` (CharField, max_length=255): نام اصلی فایل
- `file_size` (PositiveIntegerField): حجم فایل به بایت
- `mime_type` (CharField, max_length=100, blank=True): نوع MIME فایل
- `description` (TextField, blank=True): توضیحات فایل
- `uploaded_by` (ForeignKey to User, on_delete=SET_NULL, related_name="accounting_attachments_uploaded", null=True, blank=True): کاربری که فایل را آپلود کرده
- `uploaded_at` (DateTimeField, auto_now_add=True): تاریخ و زمان آپلود

**Constraints**:
- هیچ unique constraint ندارد (چند فایل می‌توانند برای یک سند آپلود شوند)

**Ordering**: `("company", "-uploaded_at", "document_number")`

**Indexes**:
- `("company", "document")` - برای جستجوی سریع بر اساس سند
- `("company", "document_number")` - برای جستجوی سریع بر اساس شماره سند
- `("company", "file_type")` - برای فیلتر کردن بر اساس نوع فایل

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای پیوست

**مقدار بازگشتی**:
- `str`: `"{file_name} - {document_number or 'بدون سند'}"`

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با auto-populate metadata فایل

**منطق**:
1. اگر `file` وجود دارد و `file_name` خالی است:
   - استخراج نام فایل از `file.name` (آخرین بخش بعد از `/`)
2. اگر `file` وجود دارد و `file_size` خالی است:
   - خواندن `file.size` و ذخیره در `file_size`
   - در صورت خطا (AttributeError, OSError)، نادیده گرفته می‌شود
3. اگر `uploaded_by` خالی است و `_uploaded_by` در instance وجود دارد:
   - استفاده از `_uploaded_by` (برای تنظیم دستی)
4. فراخوانی `super().save()`

#### `get_file_size_display(self) -> str`

**توضیح**: دریافت حجم فایل به صورت خوانا برای انسان

**مقدار بازگشتی**:
- `str`: حجم فایل با واحد مناسب (B, KB, MB, GB, TB)

**منطق**:
1. شروع از `file_size` (بر حسب بایت)
2. تقسیم متوالی بر 1024.0 تا زمانی که کمتر از 1024 شود
3. برگرداندن مقدار با واحد مناسب (B, KB, MB, GB, TB)

---

## Account Relation Models

### `SubAccountGLAccountRelation`

**Inheritance**: `AccountingBaseModel`

**توضیح**: رابطه many-to-many بین حساب‌های معین (Sub Account) و حساب‌های کل (GL Account). امکان تعلق یک حساب معین به چند حساب کل (floating sub account)

**Fields**:
- `sub_account` (ForeignKey to Account, on_delete=CASCADE, related_name='gl_relations', limit_choices_to={'account_level': 2}): حساب معین
- `gl_account` (ForeignKey to Account, on_delete=CASCADE, related_name='sub_relations', limit_choices_to={'account_level': 1}): حساب کل
- `is_primary` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): حساب کل اصلی (برای نمایش پیش‌فرض)
- `notes` (TextField, blank=True): یادداشت‌های اضافی

**Constraints**:
- Unique: `(company, sub_account, gl_account)`

**Ordering**: `("company", "sub_account", "-is_primary", "gl_account")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای رابطه

**مقدار بازگشتی**:
- `str`: `"{sub_account.account_code} → {gl_account.account_code}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی رابطه

**منطق**:
1. بررسی می‌کند که `sub_account.account_level = 2` باشد (معین)
2. بررسی می‌کند که `gl_account.account_level = 1` باشد (کل)
3. بررسی می‌کند که هر دو حساب متعلق به همان شرکت باشند
4. بررسی می‌کند که هر دو حساب نوع یکسانی داشته باشند (`account_type`)
5. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. فراخوانی `clean()` برای اعتبارسنجی
2. فراخوانی `super().save()`

---

### `TafsiliSubAccountRelation`

**Inheritance**: `AccountingBaseModel`

**توضیح**: رابطه many-to-many بین حساب‌های تفصیلی (Tafsili Account) و حساب‌های معین (Sub Account). امکان تعلق یک حساب تفصیلی به چند حساب معین (floating tafsili)

**Fields**:
- `tafsili_account` (ForeignKey to Account, on_delete=CASCADE, related_name='tafsili_sub_relations', limit_choices_to={'account_level': 3}): حساب تفصیلی
- `sub_account` (ForeignKey to Account, on_delete=CASCADE, related_name='tafsili_account_relations', limit_choices_to={'account_level': 2}): حساب معین
- `is_primary` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): حساب معین اصلی (برای نمایش پیش‌فرض)
- `notes` (TextField, blank=True): یادداشت‌های اضافی

**Constraints**:
- Unique: `(company, tafsili_account, sub_account)`

**Ordering**: `("company", "tafsili_account", "-is_primary", "sub_account")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای رابطه

**مقدار بازگشتی**:
- `str`: `"{tafsili_account.account_code} → {sub_account.account_code}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی رابطه

**منطق**:
1. بررسی می‌کند که `tafsili_account.account_level = 3` باشد (تفصیلی)
2. بررسی می‌کند که `sub_account.account_level = 2` باشد (معین)
3. بررسی می‌کند که هر دو حساب متعلق به همان شرکت باشند
4. بررسی می‌کند که هر دو حساب نوع یکسانی داشته باشند (`account_type`)
5. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. فراخوانی `clean()` برای اعتبارسنجی
2. فراخوانی `super().save()`

---

**Last Updated**: 2025-12-02

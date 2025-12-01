# accounting/models.py - Accounting Models (Complete Documentation)

**هدف**: تمام model classes برای ماژول Accounting

این فایل شامل **8 model class** است که به دسته‌های زیر تقسیم می‌شوند:
- Base Models (Abstract)
- Fiscal Year Management Models
- Chart of Accounts Models
- Accounting Document Models

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

### `AccountingDocumentBase`

**Inheritance**: `AccountingBaseModel`, `LockableModel`

**توضیح**: Base model برای document-style models

**Fields**:
- `document_code` (CharField, max_length=30, blank=True, editable=False): کد سند (auto-generated)
- `document_date` (DateField, default=timezone.now): تاریخ سند
- `notes` (TextField, blank=True): یادداشت‌ها
- `is_locked` (PositiveSmallIntegerField): Lock status (از LockableModel)
- `locked_at`, `unlocked_at` (DateTime): Lock timestamps
- `locked_by`, `unlocked_by` (ForeignKey): Lock user references
- `editing_by`, `editing_started_at`, `editing_session_key` (از LockableModel): Edit lock fields

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

**Inheritance**: `AccountingDocumentBase`

**توضیح**: سند حسابداری - رکورد تراکنشی اصلی که از اصول دفترداری دوطرفه پیروی می‌کند

**Choices**:
- `DOCUMENT_TYPE_CHOICES`: `'MANUAL'`, `'AUTOMATIC'`, `'OPENING'`, `'CLOSING'`, `'ADJUSTMENT'`
- `STATUS_CHOICES`: `'DRAFT'`, `'POSTED'`, `'LOCKED'`, `'REVERSED'`, `'CANCELLED'`

**Fields**:
- `document_number` (CharField, max_length=30, unique=True, editable=False): شماره سند (auto-generated)
- `document_type` (CharField, max_length=30, choices=DOCUMENT_TYPE_CHOICES): نوع سند
- `fiscal_year` (ForeignKey to FiscalYear, on_delete=PROTECT): سال مالی سند
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
- `locked_at` (DateTimeField, null=True, blank=True): زمان قفل شدن سند
- `locked_by` (ForeignKey to User, null=True, blank=True): کاربری که سند را قفل کرده است
- `reversed_document` (ForeignKey to 'self', on_delete=SET_NULL, null=True, blank=True): ارجاع به سند معکوس در صورت معکوس شدن
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

**توضیح**: خطوط سند حسابداری

**Fields**:
- `document` (ForeignKey to AccountingDocument, on_delete=CASCADE): سند والد
- `line_number` (PositiveSmallIntegerField): شماره خط متوالی درون سند
- `account` (ForeignKey to Account, on_delete=PROTECT): حسابی که بدهکار یا بستانکار می‌شود
- `debit_amount` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مبلغ بدهکار (باید 0 باشد اگر credit_amount > 0)
- `credit_amount` (DecimalField, max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[POSITIVE_DECIMAL]): مبلغ بستانکار (باید 0 باشد اگر debit_amount > 0)
- `description` (TextField, blank=True): توضیحات خط
- `party_id` (BigIntegerField, null=True, blank=True): ارجاع اختیاری به طرف حساب (در آینده FK به accounting_party)
- `cost_center_id` (BigIntegerField, null=True, blank=True): تخصیص اختیاری مرکز هزینه (در آینده FK به accounting_cost_center)
- `project_id` (BigIntegerField, null=True, blank=True): ارجاع اختیاری به پروژه
- `vat_rate` (DecimalField, max_digits=5, decimal_places=2, null=True, blank=True): نرخ درصد مالیات بر ارزش افزوده در صورت وجود
- `vat_amount` (DecimalField, max_digits=18, decimal_places=2, null=True, blank=True): مبلغ مالیات بر ارزش افزوده در صورت وجود
- `reference` (CharField, max_length=100, blank=True): مرجع اضافی برای خط

**Constraints**:
- Unique: `(company, document, line_number)`
- Check: `(debit_amount > 0 AND credit_amount = 0) OR (debit_amount = 0 AND credit_amount > 0)` - هر خط باید یا بدهکار یا بستانکار باشد، نه هر دو

**Ordering**: `("company", "document", "line_number")`

**Methods**:

#### `__str__(self) -> str`

**توضیح**: نمایش رشته‌ای خط سند

**مقدار بازگشتی**:
- `str`: `"{document.document_number} - Line {line_number}"`

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی مبالغ خط

**منطق**:
1. بررسی می‌کند که اگر `debit_amount > 0` و `credit_amount > 0` نباشد (هر دو نمی‌توانند مثبت باشند)
2. بررسی می‌کند که `debit_amount` یا `credit_amount` حداقل یکی مثبت باشد (هر دو نمی‌توانند صفر باشند)
3. در صورت عدم اعتبار، `ValidationError` می‌اندازد

#### `save(self, *args, **kwargs) -> None`

**توضیح**: ذخیره با اعتبارسنجی

**منطق**:
1. `clean()` را فراخوانی می‌کند
2. `super().save()` را فراخوانی می‌کند

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
5. **Document Line Validation**: هر خط باید یا بدهکار یا بستانکار باشد، نه هر دو
6. **Fiscal Year Constraints**: دوره‌ها باید در محدوده سال مالی مربوطه باشند
7. **Company Scoping**: تمام models بر اساس `company` ایزوله می‌شوند
8. **Forward References**: `opening_document_id`, `closing_document_id`, `party_id`, `cost_center_id` به صورت BigIntegerField هستند و در آینده به ForeignKey تبدیل می‌شوند

---

**Last Updated**: 2025-12-01

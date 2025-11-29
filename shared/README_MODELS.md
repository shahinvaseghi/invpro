# shared/models.py - Shared Models (Complete Documentation)

**هدف**: Mixins و model classes اصلی سیستم که در تمام ماژول‌ها استفاده می‌شوند

این فایل شامل:
- **7 Abstract Mixins**: برای استفاده در سایر models
- **11 Model Classes**: entities اصلی سیستم
- **2 Constants**: Validators و Choices

---

## وابستگی‌ها

- `django.contrib.auth.models`: `AbstractUser`, `Group`
- `django.core.validators`: `RegexValidator`
- `django.db.models`
- `django.conf.settings`

---

## Constants

### `NUMERIC_CODE_VALIDATOR`
- `RegexValidator(regex=r"^\d+$")`: فقط کاراکترهای عددی مجاز
- برای استفاده در تمام modules

### `ENABLED_FLAG_CHOICES`
- `(0, "Disabled")`
- `(1, "Enabled")`
- برای استفاده در تمام modules

---

## Abstract Mixins

### `TimeStampedModel`
**توضیح**: اضافه کردن timestamp و user tracking fields

**Fields**:
- `created_at` (DateTimeField, auto_now_add=True): زمان ایجاد
- `created_by` (ForeignKey → User, null=True, blank=True): کاربر ایجاد کننده
- `edited_at` (DateTimeField, auto_now=True): زمان آخرین ویرایش
- `edited_by` (ForeignKey → User, null=True, blank=True): کاربر ویرایش کننده

**نکات مهم**:
- Abstract model
- استفاده از `related_name="%(app_label)s_%(class)s_created"` برای جلوگیری از conflict

---

### `ActivatableModel`
**توضیح**: اضافه کردن activation/deactivation tracking

**Fields**:
- `is_enabled` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=1): فعال/غیرفعال
- `enabled_at` (DateTimeField, null=True, blank=True): زمان فعال شدن
- `enabled_by` (ForeignKey → User, null=True, blank=True): کاربر فعال کننده
- `disabled_at` (DateTimeField, null=True, blank=True): زمان غیرفعال شدن
- `disabled_by` (ForeignKey → User, null=True, blank=True): کاربر غیرفعال کننده

**نکات مهم**:
- Abstract model
- Default: `is_enabled=1` (فعال)

---

### `MetadataModel`
**توضیح**: اضافه کردن JSON metadata field

**Fields**:
- `metadata` (JSONField, default=dict, blank=True): JSON metadata

**نکات مهم**:
- Abstract model
- برای ذخیره اطلاعات اضافی به صورت JSON

---

### `SortableModel`
**توضیح**: اضافه کردن sort_order field

**Fields**:
- `sort_order` (PositiveSmallIntegerField, default=0): ترتیب نمایش

**نکات مهم**:
- Abstract model
- برای مرتب‌سازی records

---

### `EditableModel`
**توضیح**: Track کردن کاربری که در حال ویرایش record است (برای جلوگیری از concurrent editing)

**Fields**:
- `editing_by` (ForeignKey → User, null=True, blank=True): کاربر در حال ویرایش
- `editing_started_at` (DateTimeField, null=True, blank=True): زمان شروع ویرایش
- `editing_session_key` (CharField, max_length=40, blank=True): Django session key

**Methods**:
- `clear_edit_lock()`: پاک کردن edit lock
- `is_being_edited_by(user=None, session_key=None)`: بررسی اینکه آیا record توسط کاربر دیگری در حال ویرایش است

**نکات مهم**:
- Abstract model
- برای جلوگیری از concurrent editing
- `is_being_edited_by()`: اگر user یا session_key match کند، False برمی‌گرداند (یعنی توسط همان کاربر ویرایش می‌شود)

---

### `LockableModel`
**Inheritance**: `EditableModel`

**توضیح**: اضافه کردن lock/unlock functionality

**Fields** (اضافی):
- `is_locked` (PositiveSmallIntegerField, default=0): قفل شده (0=unlocked, 1=locked)
- `locked_at` (DateTimeField, null=True, blank=True): زمان قفل شدن
- `locked_by` (ForeignKey → User, null=True, blank=True): کاربر قفل کننده
- `unlocked_at` (DateTimeField, null=True, blank=True): زمان باز شدن
- `unlocked_by` (ForeignKey → User, null=True, blank=True): کاربر باز کننده

**نکات مهم**:
- Abstract model
- از `EditableModel` ارث می‌برد
- برای قفل کردن records بعد از approval/finalization

---

### `CompanyScopedModel`
**توضیح**: Base برای multi-company isolation

**Fields**:
- `company` (ForeignKey → Company, on_delete=CASCADE): Company scope
- `company_code` (CharField, max_length=8, validators=[NUMERIC_CODE_VALIDATOR], blank=True, editable=False): کد company (cache)

**Methods**:
- `save()`: Auto-populate `company_code` from `company.public_code` if not set

**نکات مهم**:
- Abstract model
- تمام models با company scope باید از این mixin استفاده کنند
- `company_code` به صورت خودکار cache می‌شود

---

## Model Classes

### `User`
**Inheritance**: `AbstractUser`, `MetadataModel`, `EditableModel`

**Fields** (اضافی):
- `email` (EmailField, unique=True): ایمیل (required)
- `phone_number` (CharField, max_length=30, blank=True): شماره تلفن
- `mobile_number` (CharField, max_length=30, blank=True): شماره موبایل
- `first_name_en` (CharField, max_length=120, blank=True): نام انگلیسی
- `last_name_en` (CharField, max_length=120, blank=True): نام خانوادگی انگلیسی
- `default_company` (ForeignKey → Company, null=True, blank=True): Company پیش‌فرض
- `metadata` (JSONField): از MetadataModel
- `editing_by`, `editing_started_at`, `editing_session_key`: از EditableModel

**REQUIRED_FIELDS**: `["email"]`

**نکات مهم**:
- Extends Django's `AbstractUser`
- `default_company`: برای استفاده در context processor

---

### `Company`
**Inheritance**: `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `EditableModel`

**Fields**:
- `public_code` (CharField, max_length=3, unique=True, validators=[NUMERIC_CODE_VALIDATOR]): کد عمومی (3 رقم)
- `legal_name` (CharField, max_length=180, unique=True): نام قانونی
- `display_name` (CharField, max_length=180, unique=True): نام نمایشی
- `display_name_en` (CharField, max_length=180, blank=True): نام نمایشی انگلیسی
- `registration_number` (CharField, max_length=60, unique=True, null=True, blank=True): شماره ثبت
- `tax_id` (CharField, max_length=60, unique=True, null=True, blank=True): شناسه مالیاتی
- `phone_number` (CharField, max_length=30, blank=True): شماره تلفن
- `email` (EmailField, blank=True): ایمیل
- `website` (URLField, blank=True): وب‌سایت
- `address` (TextField, blank=True): آدرس
- `city` (CharField, max_length=120, blank=True): شهر
- `state` (CharField, max_length=120, blank=True): استان
- `country` (CharField, max_length=3, blank=True): کشور
- و fields از mixins

**Ordering**: `("public_code",)`

**نکات مهم**:
- Multi-tenant system: هر company یک tenant است
- `public_code`: 3 رقم، unique

---

### `CompanyUnit`
**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `EditableModel`

**Fields**:
- `company` (ForeignKey → Company): از CompanyScopedModel
- `company_code` (CharField): از CompanyScopedModel
- `public_code` (CharField, max_length=5, validators=[NUMERIC_CODE_VALIDATOR]): کد عمومی (5 رقم)
- `name` (CharField, max_length=180): نام
- `name_en` (CharField, max_length=180, blank=True): نام انگلیسی
- `unit_type` (CharField, max_length=30): نوع واحد
- `parent_unit` (ForeignKey → "self", null=True, blank=True): واحد والد (hierarchical)
- `description` (CharField, max_length=255, blank=True): توضیحات
- `notes` (TextField, blank=True): یادداشت‌ها
- و fields از mixins

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, name)`

**نکات مهم**:
- Hierarchical structure (parent_unit)
- هر company می‌تواند چندین unit داشته باشد

---

### `AccessLevel`
**Inheritance**: `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `EditableModel`

**Fields**:
- `code` (CharField, max_length=30, unique=True, blank=True, editable=False): کد دسترسی (auto-generated)
- `name` (CharField, max_length=120): نام
- `description` (TextField, blank=True): توضیحات
- `is_global` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی global (0=company-specific, 1=global)
- و fields از mixins

**Methods**:
- `save()`: Auto-generate `code` from `name` if not set:
  - Convert to uppercase
  - Remove special characters
  - Replace spaces with underscores
  - Limit to 25 chars (leaving room for sequence suffix)
  - Add sequence suffix if code exists

**Ordering**: `("code",)`

**نکات مهم**:
- `is_global=1`: دسترسی در تمام companies
- `is_global=0`: دسترسی فقط در company خاص

---

### `AccessLevelPermission`
**Inheritance**: `TimeStampedModel`, `MetadataModel`, `EditableModel`

**Fields**:
- `access_level` (ForeignKey → AccessLevel, on_delete=CASCADE)
- `module_code` (CharField, max_length=30): کد ماژول
- `resource_type` (CharField, max_length=40): نوع resource
- `resource_code` (CharField, max_length=60): کد resource
- `can_view` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی مشاهده
- `can_create` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی ایجاد
- `can_edit` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی ویرایش
- `can_delete` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی حذف
- `can_approve` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی تایید
- و fields از mixins

**Constraints**:
- Unique: `(access_level, module_code, resource_code)`

**نکات مهم**:
- هر permission یک resource خاص را در یک module خاص تعریف می‌کند
- CRUD + Approve permissions

---

### `GroupProfile`
**Inheritance**: `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `EditableModel`

**Fields**:
- `group` (OneToOneField → Group): Django Group
- `description` (CharField, max_length=255, blank=True): توضیحات
- `access_levels` (ManyToMany → AccessLevel, blank=True): دسترسی‌های مرتبط
- و fields از mixins

**نکات مهم**:
- Extends Django's `Group` model
- هر group می‌تواند چندین access level داشته باشد

---

### `UserCompanyAccess`
**Inheritance**: `TimeStampedModel`, `ActivatableModel`, `MetadataModel`

**Fields**:
- `user` (ForeignKey → User)
- `company` (ForeignKey → Company)
- `access_level` (ForeignKey → AccessLevel)
- `is_enabled` (PositiveSmallIntegerField): از ActivatableModel
- و fields از mixins

**Constraints**:
- Unique: `(user, company)` (یک user فقط یک access level در هر company)

**نکات مهم**:
- Mapping بین users و companies با access levels
- یک user می‌تواند در چندین company با access levels مختلف باشد

---

### `SMTPServer`
**Inheritance**: `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `EditableModel`

**Fields**:
- `name` (CharField, max_length=120): نام
- `host` (CharField, max_length=255): SMTP host
- `port` (PositiveIntegerField): SMTP port
- `use_tls` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): استفاده از TLS
- `use_ssl` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): استفاده از SSL
- `username` (CharField, max_length=255, blank=True): نام کاربری
- `password` (CharField, max_length=255, blank=True): رمز عبور
- `from_email` (EmailField): ایمیل فرستنده
- `from_name` (CharField, max_length=120, blank=True): نام فرستنده
- و fields از mixins

**نکات مهم**:
- برای پیکربندی SMTP servers برای ارسال ایمیل

---

### `SectionRegistry`
**Inheritance**: `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `SortableModel`

**Fields**:
- `section_code` (CharField, max_length=6, unique=True, validators=[NUMERIC_CODE_VALIDATOR]): کد section (6 رقم، فرمت XXYYZZ)
- `nickname` (CharField, max_length=50, unique=True, null=True, blank=True): نام مستعار
- `module_code` (CharField, max_length=3): کد ماژول (3 رقم اول)
- `menu_number` (CharField, max_length=2): شماره منو (2 رقم میانی)
- `submenu_number` (CharField, max_length=2): شماره زیرمنو (2 رقم آخر)
- `name` (CharField, max_length=180): نام فارسی
- `name_en` (CharField, max_length=180, blank=True): نام انگلیسی
- `description` (CharField, max_length=255, blank=True): توضیحات
- `sort_order` (PositiveSmallIntegerField): از SortableModel
- و fields از mixins

**Constraints**:
- Unique: `section_code`
- Unique: `nickname` (اگر موجود باشد)

**Ordering**: `("module_code", "menu_number", "submenu_number", "sort_order")`

**نکات مهم**:
- Central registry برای تمام sections/features
- استفاده در Entity Reference System
- `section_code`: فرمت XXYYZZ (module(3) + menu(2) + submenu(2))

---

### `ActionRegistry`
**Inheritance**: `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `SortableModel`

**Fields**:
- `section` (ForeignKey → SectionRegistry): Section مرتبط
- `action_name` (CharField, max_length=50): نام action (مثلاً "show", "approve", "delete")
- `action_label` (CharField, max_length=120): برچسب فارسی
- `action_label_en` (CharField, max_length=120, blank=True): برچسب انگلیسی
- `parameter_schema` (JSONField, default=dict, blank=True): Schema برای parameters
- `sort_order` (PositiveSmallIntegerField): از SortableModel
- و fields از mixins

**Ordering**: `("section", "sort_order", "action_name")`

**نکات مهم**:
- Registry برای actions موجود در هر section
- استفاده در Entity Reference System
- `parameter_schema`: JSON schema برای parameters مورد نیاز action

---

### `Notification`
**Inheritance**: `TimeStampedModel`

**Fields**:
- `user` (ForeignKey → User): کاربر دریافت کننده
- `company` (ForeignKey → Company, null=True, blank=True): Company context
- `notification_type` (CharField, max_length=50): نوع notification (مثلاً "approval_pending", "approved")
- `notification_key` (CharField, max_length=100, unique=True): کلید یکتا
- `message` (CharField, max_length=500): پیام
- `url_name` (CharField, max_length=100): Django URL name
- `count` (PositiveIntegerField, default=1): تعداد items
- `is_read` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): خوانده شده (0=unread, 1=read)
- `read_at` (DateTimeField, null=True, blank=True): زمان خواندن
- `created_at` (DateTimeField): از TimeStampedModel
- `created_by` (ForeignKey → User): از TimeStampedModel

**Constraints**:
- Unique: `notification_key`

**نکات مهم**:
- برای notifications سیستم (approvals, requests, etc.)
- `notification_key`: برای get_or_create logic
- `is_read`: برای tracking read/unread status

---

## نکات مهم

1. **Mixins**: تمام mixins abstract هستند و برای استفاده در سایر models
2. **Company Scoping**: تمام models با company scope از `CompanyScopedModel` استفاده می‌کنند
3. **Activation**: تمام models از `ActivatableModel` استفاده می‌کنند (`is_enabled`)
4. **Timestamps**: تمام models از `TimeStampedModel` استفاده می‌کنند
5. **Edit Locking**: بسیاری از models از `EditableModel` استفاده می‌کنند
6. **Code Generation**: برخی models کدها را به صورت خودکار generate می‌کنند
7. **Entity Reference System**: `SectionRegistry` و `ActionRegistry` برای Entity Reference System استفاده می‌شوند

---

## Related Files

- `shared/README.md`: Overview کلی ماژول
- `shared/views/`: Views برای این models
- `shared/forms/`: Forms برای این models
- `docs/ENTITY_REFERENCE_SYSTEM.md`: مستندات Entity Reference System

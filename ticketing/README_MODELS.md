# ticketing/models.py - Ticketing Models (Complete Documentation)

**هدف**: تمام model classes برای ماژول ticketing

این فایل شامل 15 model class است که به دسته‌های زیر تقسیم می‌شوند:
- Base Models (Abstract)
- Master Data Models
- Permission Models
- Template Models (Dynamic Form Builder)
- Ticket Models
- Ticket Data Models

---

## وابستگی‌ها

- `shared.models`: `ActivatableModel`, `CompanyScopedModel`, `EditableModel`, `LockableModel`, `MetadataModel`, `SortableModel`, `TimeStampedModel`, `User`, `NUMERIC_CODE_VALIDATOR`, `ENABLED_FLAG_CHOICES`
- `django.contrib.auth.models`: `Group`
- `ticketing.utils.codes`: `generate_sequential_code`, `generate_template_code`, `generate_ticket_code`
- `django.db.models`
- `django.core.validators`: `RegexValidator`
- `django.utils.timezone`

---

## Base Models (Abstract)

### `TicketingBaseModel`
**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `EditableModel`

**توضیح**: Base model برای تمام ticketing models

**Fields** (از mixins):
- `company` (ForeignKey): Company scope
- `created_at`, `edited_at` (DateTime): Timestamps
- `created_by`, `edited_by` (ForeignKey): Metadata
- `is_enabled` (IntegerField): Activation flag
- `metadata` (JSONField): Metadata
- `editing_by`, `editing_started_at`, `editing_session_key`: Edit lock fields

---

### `TicketingSortableModel`
**Inheritance**: `TicketingBaseModel`, `SortableModel`

**توضیح**: Base model با sort_order

**Fields** (اضافی):
- `sort_order` (PositiveSmallIntegerField): ترتیب نمایش

---

## Master Data Models

### `TicketCategory`
**Inheritance**: `TicketingSortableModel`

**Fields**:
- `public_code` (CharField, max_length=10, validators=[NUMERIC_CODE_VALIDATOR]): کد عمومی
- `name` (CharField, max_length=120): نام فارسی
- `name_en` (CharField, max_length=120, blank=True): نام انگلیسی
- `description` (TextField, blank=True): توضیحات
- `parent_category` (ForeignKey → "self", null=True, blank=True, related_name="subcategories"): Category والد (hierarchical)

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, name)`

**Methods**:
- `save()`: Auto-generate `public_code` if not set (width=10)

**نکات مهم**:
- Hierarchical structure (parent_category)
- می‌تواند main category یا subcategory باشد

---

### `TicketPriority`
**Inheritance**: `TicketingSortableModel`

**Fields**:
- `public_code` (CharField, max_length=10, validators=[NUMERIC_CODE_VALIDATOR]): کد عمومی
- `name` (CharField, max_length=120): نام
- `name_en` (CharField, max_length=120, blank=True): نام انگلیسی
- `priority_level` (PositiveSmallIntegerField, default=3): سطح اولویت (1=highest, 5=lowest)
- `color` (CharField, max_length=7, blank=True): رنگ hex (مثلاً '#ff0000')
- `sla_hours` (IntegerField, null=True, blank=True): ساعت SLA برای response time
- و fields از mixins

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, name)`
- Unique: `(company, priority_level)`

**Indexes**:
- `tkt_priority_comp_level_idx`: روی `(company, priority_level)`

**Ordering**: `("company", "priority_level", "sort_order")`

**Methods**:
- `save()`: Auto-generate `public_code` if not set (width=10)

---

## Permission Models

### `TicketCategoryPermission`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `category` (ForeignKey → TicketCategory, on_delete=CASCADE, related_name="permissions"): Category
- `category_code` (CharField, max_length=10): کد category (cache)
- `user` (ForeignKey → User, null=True, blank=True): کاربر
- `group` (ForeignKey → Group, null=True, blank=True): گروه
- `can_create` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی ایجاد
- `can_respond` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی پاسخ
- `can_close` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی بستن

**Constraints**:
- Unique: `(category, user)` (اگر user موجود باشد)
- Unique: `(category, group)` (اگر group موجود باشد)

**Indexes**:
- Multiple indexes برای category, user, group با can_create, can_respond, can_close

**Methods**:
- `save()`: Auto-populate `category_code` from category
- `clean()`: Validation - یا user یا group باید set شود (نه هر دو)

**نکات مهم**:
- یا user یا group باید set شود (نه هر دو)
- برای permission-based access control

---

## Template Models (Dynamic Form Builder)

### `TicketTemplate`
**Inheritance**: `TicketingSortableModel`

**Fields**:
- `template_code` (CharField, max_length=16, unique=True): کد template (16 رقم)
- `name` (CharField, max_length=120): نام
- `name_en` (CharField, max_length=120, blank=True): نام انگلیسی
- `category` (ForeignKey → TicketCategory): Category
- `description` (TextField, blank=True): توضیحات
- `is_default` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): Template پیش‌فرض
- و fields از mixins

**Methods**:
- `save()`: Auto-generate `template_code` if not set (با `generate_template_code`)

**نکات مهم**:
- برای dynamic form builder
- هر template می‌تواند چندین field داشته باشد

---

### `TicketTemplateField`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `template` (ForeignKey → TicketTemplate, on_delete=CASCADE, related_name="fields"): Template
- `template_code` (CharField, max_length=16, blank=True): کد template (cache)
- `field_name` (CharField, max_length=50): نام field
- `field_label` (CharField, max_length=120): برچسب field
- `field_type` (CharField, max_length=30): نوع field (text, textarea, dropdown, radio, checkbox, multi_select, date, number, etc.)
- `field_order` (PositiveSmallIntegerField, default=0): ترتیب field
- `is_required` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): اجباری
- `is_enabled` (PositiveSmallIntegerField): از ActivatableModel
- `field_config` (JSONField, default=dict, blank=True): JSON configuration برای field
- `default_value` (TextField, blank=True): مقدار پیش‌فرض
- و fields از mixins

**Methods**:
- `save()`: Auto-populate `template_code` from template

**نکات مهم**:
- `field_config`: JSON schema برای field configuration (مثلاً options, validation rules)
- `field_type`: انواع مختلف field types برای dynamic forms

---

### `TicketTemplateFieldOption`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `field` (ForeignKey → TicketTemplateField, on_delete=CASCADE, related_name="options"): Field
- `option_value` (CharField, max_length=100): مقدار option
- `option_label` (CharField, max_length=120): برچسب option
- `is_default` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): پیش‌فرض
- `option_order` (PositiveSmallIntegerField, default=0): ترتیب option
- و fields از mixins

**نکات مهم**:
- برای dropdown, radio, checkbox, multi_select fields
- Fallback برای `field_config.options` (manual options)

---

### `TicketTemplatePermission`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `template` (ForeignKey → TicketTemplate, on_delete=CASCADE, related_name="permissions"): Template
- `template_code` (CharField, max_length=16, blank=True): کد template (cache)
- `user` (ForeignKey → User, null=True, blank=True): کاربر
- `group` (ForeignKey → Group, null=True, blank=True): گروه
- `can_create` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): دسترسی ایجاد ticket با این template
- و fields از mixins

**Constraints**:
- Unique: `(template, user)` (اگر user موجود باشد)
- Unique: `(template, group)` (اگر group موجود باشد)

**Methods**:
- `save()`: Auto-populate `template_code` from template
- `clean()`: Validation - یا user یا group باید set شود

**نکات مهم**:
- برای permission-based template access
- یا user یا group باید set شود

---

### `TicketTemplateEvent`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `template` (ForeignKey → TicketTemplate, on_delete=CASCADE, related_name="events"): Template
- `event_type` (CharField, max_length=50): نوع event (مثلاً 'created', 'updated', 'closed')
- `event_config` (JSONField, default=dict, blank=True): JSON configuration برای event
- `is_enabled` (PositiveSmallIntegerField): از ActivatableModel
- و fields از mixins

**نکات مهم**:
- برای event handling در templates
- `event_config`: JSON schema برای event configuration

---

### `TicketTemplateFieldEvent`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `field` (ForeignKey → TicketTemplateField, on_delete=CASCADE, related_name="events"): Field
- `event_type` (CharField, max_length=50): نوع event (مثلاً 'changed', 'validated')
- `event_config` (JSONField, default=dict, blank=True): JSON configuration برای event
- `is_enabled` (PositiveSmallIntegerField): از ActivatableModel
- و fields از mixins

**نکات مهم**:
- برای field-level event handling
- `event_config`: JSON schema برای event configuration

---

## Ticket Models

### `Ticket`
**Inheritance**: `TicketingBaseModel`, `LockableModel`

**Fields**:
- `ticket_code` (CharField, max_length=16, unique=True): کد ticket (16 رقم)
- `template` (ForeignKey → TicketTemplate, null=True, blank=True): Template مرتبط
- `title` (CharField, max_length=200): عنوان
- `description` (TextField): توضیحات
- `category` (ForeignKey → TicketCategory): Category
- `priority` (ForeignKey → TicketPriority): Priority
- `status` (CharField, max_length=20): وضعیت (مثلاً 'open', 'in_progress', 'resolved', 'closed')
- `reported_by` (ForeignKey → User): کاربر گزارش دهنده
- `assigned_to` (ForeignKey → User, null=True, blank=True): کاربر اختصاص داده شده
- `resolved_at` (DateTimeField, null=True, blank=True): زمان حل شدن
- `resolved_by` (ForeignKey → User, null=True, blank=True): کاربر حل کننده
- `closed_at` (DateTimeField, null=True, blank=True): زمان بسته شدن
- `closed_by` (ForeignKey → User, null=True, blank=True): کاربر بسته کننده
- `is_locked` (IntegerField): از LockableModel
- و fields از mixins

**Methods**:
- `save()`: Auto-generate `ticket_code` if not set (با `generate_ticket_code`)

**نکات مهم**:
- Main ticket model
- می‌تواند با template مرتبط باشد (برای dynamic fields)
- از LockableModel استفاده می‌کند

---

## Ticket Data Models

### `TicketFieldValue`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `ticket` (ForeignKey → Ticket, on_delete=CASCADE, related_name="field_values"): Ticket
- `field` (ForeignKey → TicketTemplateField, on_delete=CASCADE): Field از template
- `field_name` (CharField, max_length=50, blank=True): نام field (cache)
- `value_text` (TextField, blank=True): مقدار text
- `value_number` (DecimalField, null=True, blank=True): مقدار number
- `value_date` (DateField, null=True, blank=True): مقدار date
- `value_json` (JSONField, null=True, blank=True): مقدار JSON (برای multi_select, etc.)
- و fields از mixins

**Methods**:
- `save()`: Auto-populate `field_name` from field

**نکات مهم**:
- برای ذخیره مقادیر dynamic fields
- بسته به field_type، یکی از value fields استفاده می‌شود

---

### `TicketComment`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `ticket` (ForeignKey → Ticket, on_delete=CASCADE, related_name="comments"): Ticket
- `comment_text` (TextField): متن comment
- `comment_type` (CharField, max_length=20, default="comment"): نوع comment (comment, internal_note, resolution)
- `is_internal` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): داخلی (فقط برای staff)
- `created_by` (ForeignKey → User): از TimeStampedModel
- و fields از mixins

**نکات مهم**:
- برای comments و notes در tickets
- `is_internal=1`: فقط برای staff (نه reporter)

---

### `TicketAttachment`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `ticket` (ForeignKey → Ticket, on_delete=CASCADE, related_name="attachments"): Ticket
- `file` (FileField): فایل
- `file_name` (CharField, max_length=255): نام فایل
- `file_size` (PositiveIntegerField): اندازه فایل (bytes)
- `file_type` (CharField, max_length=50, blank=True): نوع فایل (MIME type)
- `description` (CharField, max_length=255, blank=True): توضیحات
- `uploaded_by` (ForeignKey → User): از TimeStampedModel
- و fields از mixins

**نکات مهم**:
- برای attachments در tickets
- `file_size`: برای validation و display

---

## نکات مهم

1. **Code Generation**: بسیاری از models کدها را به صورت خودکار generate می‌کنند
2. **Caching**: برخی models کدهای مرتبط را cache می‌کنند
3. **Company Scoping**: تمام models از `CompanyScopedModel` استفاده می‌کنند
4. **Activation**: تمام models از `ActivatableModel` استفاده می‌کنند (`is_enabled`)
5. **Edit Locking**: تمام models از `EditableModel` استفاده می‌کنند
6. **Locking**: `Ticket` از `LockableModel` استفاده می‌کند (`is_locked`)
7. **Dynamic Forms**: Template system برای dynamic form builder
8. **Permission System**: Category و Template permissions برای access control
9. **Hierarchical Categories**: `TicketCategory` با parent_category support

---

## Related Files

- `ticketing/README.md`: Overview کلی ماژول
- `ticketing/views/`: Views برای این models
- `ticketing/forms/`: Forms برای این models
- `ticketing/utils/codes.py`: Code generation utilities

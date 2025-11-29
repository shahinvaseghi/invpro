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
- `template_code` (CharField, max_length=30, unique=True): کد template (format: TMP-YYYYMMDD-XXXXXX)
- `name` (CharField, max_length=255): نام
- `description` (TextField, blank=True): توضیحات
- `category` (ForeignKey → TicketCategory, null=True, blank=True, related_name="templates"): Category
- `category_code` (CharField, max_length=10, blank=True): کد category (cache)
- `default_priority` (ForeignKey → TicketPriority, null=True, blank=True, related_name="templates"): Priority پیش‌فرض
- `default_priority_code` (CharField, max_length=10, blank=True): کد priority پیش‌فرض (cache)
- و fields از mixins

**Constraints**:
- Unique: `(company, template_code)`

**Indexes**:
- `tkt_tmpl_comp_cat_enabled_idx`: روی `(company, category, is_enabled, sort_order)`

**Ordering**: `("company", "sort_order", "template_code")`

**Methods**:
- `save()`: Auto-generate `template_code` if not set (با `generate_template_code`), cache `category_code` و `default_priority_code`

**نکات مهم**:
- برای dynamic form builder
- هر template می‌تواند چندین field داشته باشد
- `category` و `default_priority` اختیاری هستند

---

### `TicketTemplateField`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `template` (ForeignKey → TicketTemplate, on_delete=CASCADE, related_name="fields"): Template
- `template_code` (CharField, max_length=30): کد template (cache)
- `field_name` (CharField, max_length=255): نام field (label/name برای display)
- `field_type` (CharField, max_length=30, choices=FIELD_TYPE_CHOICES): نوع field
- `field_key` (CharField, max_length=100): کلید یکتا برای field در template (مثلاً 'item_code', 'description')
- `is_required` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): اجباری
- `default_value` (TextField, blank=True): مقدار پیش‌فرض
- `field_order` (PositiveSmallIntegerField, default=0): ترتیب field (row position)
- `help_text` (TextField, blank=True): متن راهنما
- `validation_rules` (JSONField, default=dict, blank=True): قوانین validation (min/max length, regex patterns, etc.)
- `field_config` (JSONField, default=dict, blank=True): Field-specific configuration (برای reference fields: entity types، برای file upload: allowed types, max size)
- `is_enabled` (PositiveSmallIntegerField): از ActivatableModel
- و fields از mixins

**FIELD_TYPE_CHOICES**:
- `short_text`, `long_text`, `radio`, `dropdown`, `file_upload`, `reference`, `checkbox`, `date`, `time`, `datetime`, `number`, `email`, `url`, `phone`, `multi_select`, `tags`, `rich_text`, `color`, `rating`, `slider`, `currency`, `signature`, `location`, `section`, `calculation`

**Constraints**:
- Unique: `(template, field_key)`

**Indexes**:
- `tkt_tmpl_field_order_idx`: روی `(template, field_order)`

**Ordering**: `("template", "field_order", "id")`

**Methods**:
- `save()`: Auto-populate `template_code` from template

**نکات مهم**:
- `field_key`: کلید یکتا برای field در template (برای lookup)
- `field_config`: JSON schema برای field configuration (مثلاً options, validation rules, entity types)
- `validation_rules`: JSON schema برای validation rules
- `field_type`: انواع مختلف field types برای dynamic forms

---

### `TicketTemplateFieldOption`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `template_field` (ForeignKey → TicketTemplateField, on_delete=CASCADE, related_name="options"): Field
- `template` (ForeignKey → TicketTemplate, on_delete=CASCADE, related_name="field_options"): Template (cache)
- `option_value` (CharField, max_length=255): مقدار option (stored value)
- `option_label` (CharField, max_length=255): برچسب option (displayed text)
- `option_order` (PositiveSmallIntegerField, default=0): ترتیب option در dropdown/radio list
- `is_default` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): پیش‌فرض
- و fields از mixins

**Constraints**:
- Unique: `(template_field, option_value)`

**Indexes**:
- `tkt_tmpl_field_opt_order_idx`: روی `(template_field, option_order)`

**Ordering**: `("template_field", "option_order", "id")`

**Methods**:
- `save()`: Auto-populate `template` from `template_field.template`

**نکات مهم**:
- برای dropdown, radio, checkbox, multi_select fields
- Fallback برای `field_config.options` (manual options)
- `template` به صورت خودکار از `template_field` populate می‌شود

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
- `template_code` (CharField, max_length=30): کد template (cache)
- `event_type` (CharField, max_length=30, choices=EVENT_TYPE_CHOICES): نوع event
- `event_order` (PositiveSmallIntegerField, default=0): ترتیب اجرا برای multiple events از همان type
- `action_reference` (CharField, max_length=255): Entity Reference System action (مثلاً 'users:show:gp=superuser', '0270:approve:code={ticket.reference_code}')
- `condition_rules` (JSONField, default=dict, blank=True): قوانین شرطی برای conditional execution (مثلاً {'field_key': 'priority', 'operator': 'equals', 'value': 'high'})
- `is_enabled` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=1): از ActivatableModel
- و fields از mixins

**EVENT_TYPE_CHOICES**:
- `on_open`, `on_close`, `on_respond`, `on_status_change`, `on_assigned`, `on_resolved`

**Indexes**:
- `tkt_tmpl_event_type_order_idx`: روی `(template, event_type, event_order)`

**Ordering**: `("template", "event_type", "event_order")`

**Methods**:
- `save()`: Auto-populate `template_code` from template

**نکات مهم**:
- برای event handling در templates
- `action_reference`: Entity Reference System action برای execution
- `condition_rules`: JSON schema برای conditional execution
- `event_order`: برای multiple events از همان type

---

### `TicketTemplateFieldEvent`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `template_field` (ForeignKey → TicketTemplateField, on_delete=CASCADE, related_name="events"): Field
- `template` (ForeignKey → TicketTemplate, on_delete=CASCADE, related_name="field_events"): Template (cache)
- `template_code` (CharField, max_length=30): کد template (cache)
- `event_type` (CharField, max_length=30, choices=EVENT_TYPE_CHOICES): نوع event
- `event_order` (PositiveSmallIntegerField, default=0): ترتیب اجرا برای multiple events
- `action_reference` (CharField, max_length=255): Entity Reference System action
- `condition_rules` (JSONField, default=dict, blank=True): قوانین شرطی برای conditional execution
- `is_enabled` (PositiveSmallIntegerField): از ActivatableModel
- و fields از mixins

**EVENT_TYPE_CHOICES**:
- `on_change`, `on_set`, `on_clear`

**Methods**:
- `save()`: Auto-populate `template` و `template_code` from `template_field`

**نکات مهم**:
- برای field-level event handling
- `action_reference`: Entity Reference System action برای execution
- `condition_rules`: JSON schema برای conditional execution

---

## Ticket Models

### `Ticket`
**Inheritance**: `TicketingBaseModel`, `LockableModel`

**Fields**:
- `ticket_code` (CharField, max_length=30, unique=True): کد ticket (format: TKT-YYYYMMDD-XXXXXX)
- `template` (ForeignKey → TicketTemplate, on_delete=PROTECT, related_name="tickets"): Template (required)
- `template_code` (CharField, max_length=30): کد template (cache)
- `title` (CharField, max_length=255): عنوان
- `description` (TextField, blank=True): توضیحات
- `category` (ForeignKey → TicketCategory, null=True, blank=True, related_name="tickets"): Category
- `category_code` (CharField, max_length=10, blank=True): کد category (cache)
- `priority` (ForeignKey → TicketPriority, null=True, blank=True, related_name="tickets"): Priority
- `priority_code` (CharField, max_length=10, blank=True): کد priority (cache)
- `status` (CharField, max_length=20, choices=STATUS_CHOICES, default="open"): وضعیت
- `reported_by` (ForeignKey → User, on_delete=PROTECT, related_name="reported_tickets"): کاربر گزارش دهنده
- `reported_by_username` (CharField, max_length=150): نام کاربری گزارش دهنده (cache)
- `assigned_to` (ForeignKey → User, null=True, blank=True, related_name="assigned_tickets"): کاربر اختصاص داده شده
- `assigned_to_username` (CharField, max_length=150, blank=True): نام کاربری اختصاص داده شده (cache)
- `assigned_at` (DateTimeField, null=True, blank=True): زمان اختصاص
- `opened_at` (DateTimeField, default=timezone.now): زمان باز شدن
- `first_response_at` (DateTimeField, null=True, blank=True): زمان اولین پاسخ
- `resolved_at` (DateTimeField, null=True, blank=True): زمان حل شدن
- `resolved_by` (ForeignKey → User, null=True, blank=True, related_name="resolved_tickets"): کاربر حل کننده
- `closed_at` (DateTimeField, null=True, blank=True): زمان بسته شدن
- `closed_by` (ForeignKey → User, null=True, blank=True, related_name="closed_tickets"): کاربر بسته کننده
- `resolution_notes` (TextField, blank=True): یادداشت‌های حل
- `related_entity_type` (CharField, max_length=50, blank=True): نوع entity مرتبط (مثلاً 'inventory.item', 'production.order')
- `related_entity_id` (BigIntegerField, null=True, blank=True): شناسه entity مرتبط
- `related_entity_code` (CharField, max_length=100, blank=True): کد entity مرتبط
- `attachments` (JSONField, default=list, blank=True): Array of file attachments با metadata
- `is_locked` (IntegerField): از LockableModel
- و fields از mixins

**STATUS_CHOICES**:
- `open`, `in_progress`, `assigned`, `pending`, `resolved`, `closed`, `cancelled`

**Constraints**:
- Unique: `(company, ticket_code)`

**Indexes**:
- `tkt_comp_status_created_idx`: روی `(company, status, created_at)`
- `tkt_comp_assign_status_idx`: روی `(company, assigned_to, status)`
- `tkt_comp_cat_status_idx`: روی `(company, category, status)`
- `tkt_comp_tmpl_status_idx`: روی `(company, template, status)`
- `tkt_comp_pri_status_idx`: روی `(company, priority, status)`
- `tkt_related_entity_idx`: روی `(related_entity_type, related_entity_id)`

**Ordering**: `("-created_at",)` (جدیدترین اول)

**Methods**:
- `save()`: Auto-generate `ticket_code` if not set (با `generate_ticket_code`), cache `template_code`, `category_code`, `priority_code`, `reported_by_username`, `assigned_to_username`

**نکات مهم**:
- Main ticket model
- `template` required است (on_delete=PROTECT)
- می‌تواند با entity دیگری مرتبط باشد (related_entity_type/id/code)
- `attachments`: JSON array برای file attachments
- از LockableModel استفاده می‌کند

---

## Ticket Data Models

### `TicketFieldValue`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `ticket` (ForeignKey → Ticket, on_delete=CASCADE, related_name="field_values"): Ticket
- `ticket_code` (CharField, max_length=30): کد ticket (cache)
- `template_field` (ForeignKey → TicketTemplateField, on_delete=PROTECT, related_name="ticket_values"): Field از template
- `template_field_key` (CharField, max_length=100): کلید field (cache)
- `field_value` (TextField, blank=True): مقدار field (text representation، JSON برای complex types)
- `field_value_json` (JSONField, null=True, blank=True): مقدار structured (برای reference fields، file uploads، etc.)
- و fields از mixins

**Constraints**:
- Unique: `(ticket, template_field)`

**Indexes**:
- `tkt_field_val_ticket_idx`: روی `ticket`
- `tkt_field_val_field_idx`: روی `template_field`

**Ordering**: `("ticket", "template_field__field_order")`

**Methods**:
- `save()`: Auto-populate `ticket_code` و `template_field_key` from ticket و template_field

**نکات مهم**:
- برای ذخیره مقادیر dynamic fields
- `field_value`: text representation (یا JSON string برای complex types)
- `field_value_json`: structured JSON (برای reference fields، file uploads)
- یک ticket فقط یک value برای هر template_field می‌تواند داشته باشد

---

### `TicketComment`
**Inheritance**: `TicketingBaseModel`

**Fields**:
- `ticket` (ForeignKey → Ticket, on_delete=CASCADE, related_name="comments"): Ticket
- `comment_text` (TextField): متن comment
- `comment_type` (CharField, max_length=20, choices=COMMENT_TYPE_CHOICES, default="comment"): نوع comment
- `is_internal` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): داخلی (فقط برای staff)
- `created_by` (ForeignKey → User): از TimeStampedModel
- و fields از mixins

**COMMENT_TYPE_CHOICES**:
- `comment`, `internal_note`, `resolution`

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
- **نکته**: `Ticket` model نیز `attachments` JSONField دارد (برای metadata)

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

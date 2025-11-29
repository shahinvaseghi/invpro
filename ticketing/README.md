# ticketing app overview

The ticketing module provides comprehensive ticket management with dynamic form builder capabilities. All models follow the standard invproj architecture with multi-company support and auditing.

**نکته مهم**: برای جزئیات کامل هر بخش، به فایل‌های README مربوطه مراجعه کنید:
- **Models**: [`README_MODELS.md`](README_MODELS.md) - مستندات کامل برای 15 model class
- **Views**: [`views/README.md`](views/README.md) - Overview کلی views و لینک به READMEهای جزئی‌تر
- **Forms**: [`forms/README.md`](forms/README.md) - Overview کلی forms
- **Utils**: [`utils/README.md`](utils/README.md) - توابع utility (codes.py)
- **Migrations**: [`migrations/README.md`](migrations/README.md) - خلاصه migrations

---

## models.py

Defines all ticketing-related entities. Major groups:

- **Base Models**
  - `TicketingBaseModel`: extends shared mixins for timestamps, activation, metadata, company scope, and edit locking.
  - `TicketingSortableModel`: adds `sort_order` to the base.

- **Master Data**
  - `TicketCategory`: hierarchical categories with parent_category support.
  - `TicketPriority`: priority levels with SLA support (sla_hours, priority_level, color).

- **Permission Models**
  - `TicketCategoryPermission`: permissions for users/groups to create/respond/close tickets in categories.

- **Template Models (Dynamic Form Builder)**
  - `TicketTemplate`: template for creating tickets with dynamic fields.
  - `TicketTemplateField`: dynamic field definition with 25+ field types (short_text, long_text, radio, dropdown, file_upload, reference, checkbox, date, time, datetime, number, email, url, phone, multi_select, tags, rich_text, color, rating, slider, currency, signature, location, section, calculation).
  - `TicketTemplateFieldOption`: options for radio, dropdown, or multi_select field types.
  - `TicketTemplatePermission`: permissions for users/groups to create/respond/close tickets using templates.
  - `TicketTemplateEvent`: events for ticket templates (on_open, on_close, on_respond, etc.) with action_reference (Entity Reference System).
  - `TicketTemplateFieldEvent`: events for template fields (on_change, on_set, on_clear).

- **Ticket Models**
  - `Ticket`: main ticket entity with related_entity (type/id/code), attachments JSONField, status tracking, and cached fields.

- **Ticket Data Models**
  - `TicketFieldValue`: field values for tickets (dynamic field data) with field_value (text) and field_value_json (structured).
  - `TicketComment`: comments/notes for tickets with comment_type and is_internal.
  - `TicketAttachment`: file attachments for tickets.

All models enforce unique constraints tailored to multi-company setups and use `save()` overrides to populate cached fields or generate codes.

---

## views.py

Views are organized in separate files:
- `base.py`: Base views and mixins
- `tickets.py`: Ticket management views
- `templates.py`: Template management views
- `categories.py`: Category management views
- `subcategories.py`: Subcategory management views
- `entity_reference.py`: Entity Reference System API views
- `debug.py`: Debug views (development only)
- `placeholders.py`: Placeholder views for future features

See [`views/README.md`](views/README.md) for complete documentation.

---

## forms.py

Forms are organized in separate files:
- `base.py`: Base forms and helper functions
- `tickets.py`: Ticket forms
- `templates.py`: Template forms
- `categories.py`: Category forms

See [`forms/README.md`](forms/README.md) for complete documentation.

---

## utils/

Utility functions for code generation:
- `codes.py`: Functions for generating sequential codes for templates and tickets

See [`utils/README.md`](utils/README.md) for complete documentation.

---

## admin.py

Registers all models with meaningful list displays, filters, and search fields.

---

## migrations/

- `0001_initial.py`: creates all ticketing tables
- `0002_add_template_events.py`: adds template events

See [`migrations/README.md`](migrations/README.md) for complete migration history.

---

## apps.py

Contains the default `TicketingConfig`. Hook into `ready()` if ticketing-specific signals or initialization are added later.

---

## tests.py

Provides unit tests for ticket management functionality.

Executed via `python manage.py test ticketing`.

---

## Future Work / Notes

- When new ticket types or workflows are implemented, update both the models and admin registration.
- Consider adding signals/services for ticket lifecycle events.
- Add API serializers/views (e.g., DRF) as part of future integration tasks.


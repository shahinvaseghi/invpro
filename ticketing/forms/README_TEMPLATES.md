# ticketing/forms/templates.py - Ticket Template Forms (Complete Documentation)

**هدف**: Forms برای مدیریت ticket templates در ماژول ticketing

این فایل شامل:
- TicketTemplateForm: فرم header برای template
- TicketTemplateFieldForm: فرم field entries
- TicketTemplateFieldOptionForm: فرم field option entries
- TicketTemplateEventForm: فرم template event entries
- TicketTemplateFieldEventForm: فرم field event entries
- TicketTemplatePermissionForm: فرم permission entries
- 3 Base Formset classes با validation
- 4 Formset factories

---

## وابستگی‌ها

- `ticketing.models`: `TicketTemplate`, `TicketTemplateField`, `TicketTemplateFieldOption`, `TicketTemplatePermission`, `TicketTemplateEvent`, `TicketTemplateFieldEvent`, `TicketCategory`, `TicketPriority`
- `ticketing.forms.base`: `TicketingBaseForm`
- `shared.models`: `ENABLED_FLAG_CHOICES`
- `django.forms`
- `django.forms.BaseInlineFormSet`, `inlineformset_factory`
- `django.contrib.auth.get_user_model`
- `django.contrib.auth.models.Group`
- `django.utils.translation.gettext_lazy`

---

## TicketTemplateForm

**Type**: `TicketingBaseForm`

**Model**: `TicketTemplate`

**Fields**:
- `name`, `description`, `category`, `default_priority`, `is_enabled`, `sort_order`

**متدها**:
- `__init__()`: فیلتر `category` و `default_priority` بر اساس company

---

## TicketTemplateFieldForm

**Type**: `forms.ModelForm`

**Model**: `TicketTemplateField`

**Fields**:
- `field_name`, `field_type`, `field_key`, `is_required`, `default_value`, `field_order`, `help_text`, `validation_rules`, `field_config`, `is_enabled`

**FIELD_TYPE_CHOICES**: 25 نوع field (short_text, long_text, radio, dropdown, checkbox, number, date, time, datetime, email, url, phone, file_upload, reference, multi_select, tags, rich_text, color, rating, slider, currency, signature, location, section, calculation)

**متدها**:
- `__init__()`: تنظیم field type choices، تبدیل `field_config` dict به JSON string برای نمایش

---

## TicketTemplateFieldOptionForm

**Type**: `forms.ModelForm`

**Model**: `TicketTemplateFieldOption`

**Fields**:
- `option_value`, `option_label`, `option_order`, `is_default`, `is_enabled`

---

## TicketTemplateEventForm

**Type**: `forms.ModelForm`

**Model**: `TicketTemplateEvent`

**Fields**:
- `event_type`, `event_order`, `action_reference`, `condition_rules`, `is_enabled`

---

## TicketTemplateFieldEventForm

**Type**: `forms.ModelForm`

**Model**: `TicketTemplateFieldEvent`

**Fields**:
- `event_type`, `event_order`, `action_reference`, `condition_rules`, `is_enabled`

---

## TicketTemplatePermissionForm

**Type**: `forms.ModelForm`

**Model**: `TicketTemplatePermission`

**Fields**:
- `user`, `group`, `can_create`, `can_respond`, `can_close`, `is_enabled`

**متدها**:
- `__init__()`: فیلتر users و groups
- `clean()`: بررسی که یا user یا group تنظیم شود (نه هر دو)

---

## BaseTicketTemplateFieldFormSet

**Type**: `BaseInlineFormSet`

**متدها**:
- `clean()`: بررسی unique بودن `field_key` در template

---

## BaseTicketTemplateFieldOptionFormSet

**Type**: `BaseInlineFormSet`

**متدها**:
- `clean()`: بررسی unique بودن `option_value` در field

---

## BaseTicketTemplatePermissionFormSet

**Type**: `BaseInlineFormSet`

**متدها**:
- `clean()`: بررسی که هر row یا user یا group داشته باشد

---

## Formset Factories

- `TicketTemplateFieldFormSet`: برای template fields
- `TicketTemplateFieldOptionFormSet`: برای field options
- `TicketTemplateEventFormSet`: برای template events
- `TicketTemplatePermissionFormSet`: برای template permissions

---

## نکات مهم

1. **Field Types**: 25 نوع field مختلف پشتیبانی می‌شود
2. **JSON Fields**: `field_config` و `validation_rules` به صورت JSON ذخیره می‌شوند
3. **Unique Validation**: `field_key` و `option_value` باید unique باشند
4. **Permission Validation**: یا user یا group باید تنظیم شود (نه هر دو)


# ticketing/forms/categories.py - Ticket Category Forms (Complete Documentation)

**هدف**: Forms برای مدیریت ticket categories در ماژول ticketing

این فایل شامل:
- TicketCategoryForm: فرم ایجاد/ویرایش category
- TicketCategoryPermissionForm: فرم permission entries
- BaseTicketCategoryPermissionFormSet: Formset base class با validation
- TicketCategoryPermissionFormSet: Formset factory

---

## وابستگی‌ها

- `ticketing.models`: `TicketCategory`, `TicketCategoryPermission`
- `ticketing.forms.base`: `TicketingBaseForm`
- `shared.models`: `ENABLED_FLAG_CHOICES`
- `django.forms`
- `django.forms.BaseInlineFormSet`, `inlineformset_factory`
- `django.contrib.auth.get_user_model`
- `django.contrib.auth.models.Group`
- `django.utils.translation.gettext_lazy`

---

## TicketCategoryForm

**Type**: `TicketingBaseForm`

**Model**: `TicketCategory`

**Fields**:
- `public_code`, `name`, `name_en`, `description`, `parent_category`, `is_enabled`, `sort_order`

**متدها**:
- `__init__()`: فیلتر `parent_category` بر اساس company و exclude self، تنظیم `public_code` به readonly در edit mode

---

## TicketCategoryPermissionForm

**Type**: `forms.ModelForm`

**Model**: `TicketCategoryPermission`

**Fields**:
- `user`, `group`, `can_create`, `can_respond`, `can_close`, `is_enabled`

**متدها**:
- `__init__()`: فیلتر users و groups
- `clean()`: بررسی که یا user یا group تنظیم شود (نه هر دو)

---

## BaseTicketCategoryPermissionFormSet

**Type**: `BaseInlineFormSet`

**متدها**:
- `clean()`: بررسی که هر row یا user یا group داشته باشد

---

## TicketCategoryPermissionFormSet

**Factory**: `inlineformset_factory`

**پارامترها**:
- `parent_model`: `TicketCategory`
- `model`: `TicketCategoryPermission`
- `form`: `TicketCategoryPermissionForm`
- `formset`: `BaseTicketCategoryPermissionFormSet`
- `fk_name`: `"category"`
- `extra`: `1`
- `can_delete`: `True`

---

## نکات مهم

1. **Parent Category**: می‌تواند parent category داشته باشد (hierarchical structure)
2. **Public Code**: در edit mode readonly است
3. **Permission Validation**: یا user یا group باید تنظیم شود (نه هر دو)


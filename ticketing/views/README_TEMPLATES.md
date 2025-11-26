# ticketing/views/templates.py - Ticket Template Views (Complete Documentation)

**هدف**: Views برای مدیریت ticket templates در ماژول ticketing

این فایل شامل views برای:
- TicketTemplateListView: فهرست templates
- TicketTemplateCreateView: ایجاد template جدید
- TicketTemplateUpdateView: ویرایش template
- TicketTemplateDeleteView: حذف template

---

## وابستگی‌ها

- `ticketing.models`: `TicketTemplate`, `TicketCategory`, `TicketPriority`
- `ticketing.forms.templates`: `TicketTemplateForm`, `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`
- `ticketing.views.base`: `TicketingBaseView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.db.transaction`
- `django.db.models.Q`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## TicketTemplateListView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, ListView`

**Template**: `ticketing/templates_list.html`

**Attributes**:
- `model`: `TicketTemplate`
- `template_name`: `'ticketing/templates_list.html'`
- `context_object_name`: `'templates'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'view_all'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company، search (name, template_code, description)، category filter
- `get_context_data()`: اضافه کردن `categories` برای filter dropdown

**Query Parameters**:
- `search`: جستجو در name, template_code, description
- `category`: فیلتر بر اساس category

**URL**: `/ticketing/templates/`

---

## TicketTemplateCreateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, CreateView`

**Template**: `ticketing/template_form.html`

**Form**: `TicketTemplateForm`

**Formsets**: `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `form_class`: `TicketTemplateForm`
- `template_name`: `'ticketing/template_form.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'create'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `request` به form
- `get_context_data()`: اضافه کردن 3 formsets و `categories`, `priorities`
- `form_valid()`: ذخیره template و تمام formsets، تنظیم `company_id` و `template_code` برای هر item

**نکات مهم**:
- از `@transaction.atomic` استفاده می‌کند
- 3 formsets مدیریت می‌شوند: fields, permissions, events

**URL**: `/ticketing/templates/create/`

---

## TicketTemplateUpdateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, UpdateView`

**Template**: `ticketing/template_form.html`

**Form**: `TicketTemplateForm`

**Formsets**: `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `form_class`: `TicketTemplateForm`
- `template_name`: `'ticketing/template_form.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'edit_own'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `request` به form
- `get_queryset()`: فیلتر بر اساس company
- `get_context_data()`: اضافه کردن 3 formsets و `categories`, `priorities` (با debug logging)
- `form_valid()`: ذخیره template و تمام formsets (با debug logging)

**نکات مهم**:
- Debug logging برای `field_config` در edit mode
- از `@transaction.atomic` استفاده می‌کند

**URL**: `/ticketing/templates/<pk>/edit/`

---

## TicketTemplateDeleteView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView`

**Template**: `ticketing/template_confirm_delete.html`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `template_name`: `'ticketing/template_confirm_delete.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'delete_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `page_title`

**URL**: `/ticketing/templates/<pk>/delete/`

---

## نکات مهم

1. **Multi-formset Management**: 3 formsets مدیریت می‌شوند (fields, permissions, events)
2. **Template Code**: `template_code` برای fields, permissions, events به صورت خودکار تنظیم می‌شود
3. **Transaction Management**: از `@transaction.atomic` استفاده می‌شود
4. **Debug Logging**: در UpdateView برای `field_config` debug logging وجود دارد

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Formset Management**: 3 formsets در create و update views مدیریت می‌شوند


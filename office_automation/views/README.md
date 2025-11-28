# office_automation/views.py - Views

**هدف**: Views برای ماژول اتوماسیون اداری

---

## Views

### Dashboard

#### `OfficeAutomationDashboardView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Dashboard view برای ماژول اتوماسیون اداری.

**Attributes**:
- `template_name`: `'office_automation/dashboard.html'`
- `feature_code`: `'office_automation.dashboard'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'office_automation'`
- `page_title`: `'اتوماسیون اداری'`

---

### Inbox Section (کارتابل)

#### `InboxIncomingLettersView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای نامه‌های ورودی.

**Attributes**:
- `template_name`: `'office_automation/inbox/incoming_letters.html'`
- `feature_code`: `'office_automation.inbox.incoming'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'office_automation'`
- `page_title`: `'نامه‌های ورودی'`

---

#### `InboxWriteLetterView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای نوشتن نامه.

**Attributes**:
- `template_name`: `'office_automation/inbox/write_letter.html'`
- `feature_code`: `'office_automation.inbox.write'`
- `required_action`: `'create'`

**Context**:
- `active_module`: `'office_automation'`
- `page_title`: `'نوشتن نامه'`

---

#### `InboxFillFormView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای پر کردن فرم.

**Attributes**:
- `template_name`: `'office_automation/inbox/fill_form.html'`
- `feature_code`: `'office_automation.inbox.fill_form'`
- `required_action`: `'create'`

**Context**:
- `active_module`: `'office_automation'`
- `page_title`: `'پر کردن فرم'`

---

### Processes Section (فرایندها)

#### `ProcessEngineView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای موتور تولید فرایند.

**Attributes**:
- `template_name`: `'office_automation/processes/engine.html'`
- `feature_code`: `'office_automation.processes.engine'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'office_automation'`
- `page_title`: `'موتور تولید فرایند'`

---

#### `ProcessFormConnectionView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای ارتباط فرایند و فرم‌ها.

**Attributes**:
- `template_name`: `'office_automation/processes/form_connection.html'`
- `feature_code`: `'office_automation.processes.form_connection'`
- `required_action`: `'edit_own'`

**Context**:
- `active_module`: `'office_automation'`
- `page_title`: `'ارتباط فرایند و فرم‌ها'`

---

### Forms Section (فرم‌ها)

#### `FormBuilderView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای ساخت فرم.

**Attributes**:
- `template_name`: `'office_automation/forms/builder.html'`
- `feature_code`: `'office_automation.forms.builder'`
- `required_action`: `'create'`

**Context**:
- `active_module`: `'office_automation'`
- `page_title`: `'ساخت فرم'`

---

## وابستگی‌ها

- `django.views.generic`: `TemplateView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`

---

## استفاده در پروژه

تمام views از `FeaturePermissionRequiredMixin` برای بررسی دسترسی استفاده می‌کنند و از `TemplateView` برای نمایش صفحات خالی استفاده می‌شوند.

---

## نکات مهم

1. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` برای بررسی دسترسی استفاده می‌کنند
2. **Placeholder Views**: در حال حاضر تمام views به صورت placeholder هستند و فقط template را نمایش می‌دهند
3. **Active Module**: تمام views `active_module` را در context تنظیم می‌کنند برای navigation highlighting


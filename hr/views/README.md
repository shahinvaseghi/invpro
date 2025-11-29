# hr/views.py - Views

**هدف**: Views برای ماژول منابع انسانی

---

## Views

### Dashboard

#### `HrDashboardView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Dashboard view برای ماژول منابع انسانی.

**Attributes**:
- `template_name`: `'hr/dashboard.html'`
- `feature_code`: `'hr.dashboard'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'منابع انسانی'`

---

### Personnel Section (پرسنل)

#### `PersonnelCreateView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Create view برای ایجاد پرسنل.

**Attributes**:
- `template_name`: `'hr/personnel/create.html'`
- `feature_code`: `'hr.personnel'`
- `required_action`: `'create'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'ایجاد پرسنل'`

---

#### `PersonnelDecreeAssignmentView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای تخصیص حکم به پرسنل.

**Attributes**:
- `template_name`: `'hr/personnel/decree_assignment.html'`
- `feature_code`: `'hr.personnel.decree'`
- `required_action`: `'edit_own'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'تخصیص حکم'`

---

#### `PersonnelFormCreateView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Create view برای ایجاد فرم پرسنل.

**Attributes**:
- `template_name`: `'hr/personnel/form_create.html'`
- `feature_code`: `'hr.personnel.form'`
- `required_action`: `'create'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'ایجاد فرم پرسنل'`

---

#### `PersonnelFormGroupListView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: List view برای گروه‌بندی فرم پرسنل.

**Attributes**:
- `template_name`: `'hr/personnel/form_group_list.html'`
- `feature_code`: `'hr.personnel.form_groups'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'گروه‌بندی فرم پرسنل'`

---

#### `PersonnelFormSubGroupListView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: List view برای زیر گروه‌بندی فرم پرسنل.

**Attributes**:
- `template_name`: `'hr/personnel/form_subgroup_list.html'`
- `feature_code`: `'hr.personnel.form_subgroups'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'زیر گروه‌بندی فرم پرسنل'`

---

### Requests Section (درخواست‌ها)

#### `LeaveRequestView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای درخواست مرخصی.

**Attributes**:
- `template_name`: `'hr/requests/leave.html'`
- `feature_code`: `'hr.requests.leave'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'درخواست مرخصی'`

---

#### `SickLeaveRequestView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای درخواست استعلاجی.

**Attributes**:
- `template_name`: `'hr/requests/sick_leave.html'`
- `feature_code`: `'hr.requests.sick_leave'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'درخواست استعلاجی'`

---

#### `LoanRequestView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای درخواست وام.

**Attributes**:
- `template_name`: `'hr/requests/loan.html'`
- `feature_code`: `'hr.requests.loan'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'درخواست وام'`

---

### Loan Section (وام)

#### `LoanManagementView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای مدیریت وام.

**Attributes**:
- `template_name`: `'hr/loans/management.html'`
- `feature_code`: `'hr.loans.management'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'مدیریت وام'`

---

#### `LoanSchedulingView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای نوبت‌بندی وام.

**Attributes**:
- `template_name`: `'hr/loans/scheduling.html'`
- `feature_code`: `'hr.loans.scheduling'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'نوبت‌بندی'`

---

#### `SavingsFundView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای صندوق اندوخته.

**Attributes**:
- `template_name`: `'hr/loans/savings_fund.html'`
- `feature_code`: `'hr.loans.savings_fund'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'hr'`
- `page_title`: `'صندوق اندوخته'`

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


# accounting/views.py - Views (Placeholder Views)

**هدف**: Placeholder views برای ماژول حسابداری

**نکته**: این فایل شامل placeholder views است. برای views پیاده‌سازی شده، به فایل‌های README زیر مراجعه کنید:
- `accounting/views/README_BASE.md`: Base views و mixins
- `accounting/views/README_FISCAL_YEARS.md`: CRUD views برای سال‌های مالی
- `accounting/views/README_ACCOUNTS.md`: CRUD views برای حساب‌ها (Chart of Accounts)

---

## Placeholder Views

### Dashboard

#### `AccountingDashboardView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Dashboard view برای ماژول حسابداری.

**Attributes**:
- `template_name`: `'accounting/dashboard.html'`
- `feature_code`: `'accounting.dashboard'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'حسابداری'`

---

### General Section (عمومی)

#### `GeneralLedgerListView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: List view برای اسناد کل.

**Attributes**:
- `template_name`: `'accounting/general/ledger_list.html'`
- `feature_code`: `'accounting.general.ledger'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'اسناد کل'`

---

#### `SubsidiaryLedgerListView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: List view برای معین‌ها.

**Attributes**:
- `template_name`: `'accounting/general/subsidiary_list.html'`
- `feature_code`: `'accounting.general.subsidiary'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'معین‌ها'`

---

#### `DetailLedgerListView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: List view برای تفصیلی‌ها.

**Attributes**:
- `template_name`: `'accounting/general/detail_list.html'`
- `feature_code`: `'accounting.general.detail'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'تفصیلی‌ها'`

---

### Accounting Documents (اسناد حسابداری)

#### `AccountingDocumentEntryView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای سند ورودی.

**Attributes**:
- `template_name`: `'accounting/documents/entry.html'`
- `feature_code`: `'accounting.documents.entry'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'سند ورودی'`

---

#### `AccountingDocumentExitView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای سند خروجی.

**Attributes**:
- `template_name`: `'accounting/documents/exit.html'`
- `feature_code`: `'accounting.documents.exit'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'سند خروجی'`

---

### Treasury (خزانه)

#### `TreasuryExpenseView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای سند هزینه.

**Attributes**:
- `template_name`: `'accounting/treasury/expense.html'`
- `feature_code`: `'accounting.treasury.expense'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'سند هزینه'`

---

#### `TreasuryIncomeView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای سند درآمد.

**Attributes**:
- `template_name`: `'accounting/treasury/income.html'`
- `feature_code`: `'accounting.treasury.income'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'سند درآمد'`

---

### Payroll (حقوق و دستمزد)

#### `PayrollDocumentView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای سند حقوق دستمزد.

**Attributes**:
- `template_name`: `'accounting/payroll/document.html'`
- `feature_code`: `'accounting.payroll.document'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'سند حقوق دستمزد'`

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


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

### Party Management (طرف حساب‌ها)

#### `PartiesView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای نمایش لیست طرف حساب‌ها

**Attributes**:
- `template_name`: `'accounting/parties/list.html'`
- `feature_code`: `'accounting.parties.list'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'طرف حساب‌ها'`
- `create_url`: URL برای ایجاد طرف حساب جدید
- `party_accounts_url`: URL برای حساب‌های طرف حساب

---

#### `PartyCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView)`

**توضیح**: View برای ایجاد طرف حساب جدید

**Attributes**:
- `model`: `Party`
- `form_class`: `PartyForm`
- `template_name`: `'accounting/parties/party_form.html'`
- `success_url`: `reverse_lazy('accounting:parties')`
- `feature_code`: `'accounting.parties.list'`
- `required_action`: `'create'`

**متدها**:

##### `get_form_kwargs(self) -> Dict`

**توضیح**: اضافه کردن `company_id` به form kwargs

**مقدار بازگشتی**:
- `Dict`: kwargs شامل `company_id` از session

##### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: تنظیم `created_by` و نمایش پیام موفقیت

**منطق**:
1. تنظیم `form.instance.created_by = self.request.user`
2. نمایش پیام موفقیت: `'طرف حساب با موفقیت ایجاد شد.'`
3. فراخوانی `super().form_valid(form)`

##### `get_context_data(self, **kwargs) -> Dict`

**توضیح**: اضافه کردن context برای template

**Context**:
- `page_title`: `'ایجاد طرف حساب'`
- `form_title`: `'ایجاد طرف حساب'`
- `breadcrumbs`: لیست breadcrumb (داشبورد، حسابداری، طرف حساب‌ها، ایجاد)
- `cancel_url`: URL برای لغو (بازگشت به لیست)

---

#### `PartyAccountsView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای نمایش لیست حساب‌های طرف حساب

**Attributes**:
- `template_name`: `'accounting/parties/accounts.html'`
- `feature_code`: `'accounting.parties.accounts'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'accounting'`
- `page_title`: `'حساب‌های طرف حساب'`
- `create_url`: URL برای ایجاد حساب طرف حساب جدید
- `parties_url`: URL برای طرف حساب‌ها

---

#### `PartyAccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView)`

**توضیح**: View برای ایجاد حساب طرف حساب جدید

**Attributes**:
- `model`: `PartyAccount`
- `form_class`: `PartyAccountForm`
- `template_name`: `'accounting/parties/party_account_form.html'`
- `success_url`: `reverse_lazy('accounting:party_accounts')`
- `feature_code`: `'accounting.parties.accounts'`
- `required_action`: `'create'`

**متدها**:

##### `get_form_kwargs(self) -> Dict`

**توضیح**: اضافه کردن `company_id` به form kwargs

**مقدار بازگشتی**:
- `Dict`: kwargs شامل `company_id` از session

##### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: تنظیم `created_by` و نمایش پیام موفقیت

**منطق**:
1. تنظیم `form.instance.created_by = self.request.user`
2. نمایش پیام موفقیت: `'حساب طرف حساب با موفقیت ایجاد شد.'`
3. فراخوانی `super().form_valid(form)`

##### `get_context_data(self, **kwargs) -> Dict`

**توضیح**: اضافه کردن context برای template

**Context**:
- `page_title`: `'ایجاد حساب طرف حساب'`
- `form_title`: `'ایجاد حساب طرف حساب'`
- `breadcrumbs`: لیست breadcrumb (داشبورد، حسابداری، حساب‌های طرف حساب، ایجاد)
- `cancel_url`: URL برای لغو (بازگشت به لیست)

---

## نکات مهم

1. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` برای بررسی دسترسی استفاده می‌کنند
2. **Placeholder Views**: برخی views به صورت placeholder هستند و فقط template را نمایش می‌دهند
3. **Active Module**: تمام views `active_module` را در context تنظیم می‌کنند برای navigation highlighting
4. **Company Scoping**: تمام forms باید `company_id` دریافت کنند تا queryset ها به درستی فیلتر شوند

---

**Last Updated**: 2025-12-02


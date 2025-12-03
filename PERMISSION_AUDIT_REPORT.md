# گزارش بررسی دسترسی‌های برنامه (Permission Audit Report)

**تاریخ بررسی**: $(date)
**تعداد کل feature_code های استفاده شده در views**: 129
**تعداد feature_code های تعریف شده در FEATURE_PERMISSION_MAP**: 77
**تعداد feature_code های گم شده**: 62

---

## فهرست feature_code های استفاده شده که در FEATURE_PERMISSION_MAP تعریف نشده‌اند

### Accounting Module (49 مورد)

#### Accounts Sub-modules (4 مورد)
- `accounting.accounts.gl`
- `accounting.accounts.sub`
- `accounting.accounts.tafsili`
- `accounting.accounts.tafsili_hierarchy`

#### Attachments (4 مورد)
- `accounting.attachments.attach_to_document`
- `accounting.attachments.download`
- `accounting.attachments.list`
- `accounting.attachments.upload`

#### Documents (4 مورد)
- `accounting.documents.create`
- `accounting.documents.list`
- `accounting.documents.status`
- `accounting.documents.tafsili_movements`

#### Income/Expense (8 مورد)
- `accounting.income_expense.categories`
- `accounting.income_expense.cost_allocation`
- `accounting.income_expense.cost_center_report`
- `accounting.income_expense.cost_centers`
- `accounting.income_expense.expense`
- `accounting.income_expense.expense_report`
- `accounting.income_expense.income`
- `accounting.income_expense.income_report`

#### Parties (5 مورد)
- `accounting.parties.accounts`
- `accounting.parties.balance_report`
- `accounting.parties.list`
- `accounting.parties.movements`
- `accounting.parties.transactions`

#### Reports (10 مورد)
- `accounting.reports.account_movements`
- `accounting.reports.balance_sheet`
- `accounting.reports.cash_flow`
- `accounting.reports.check_report`
- `accounting.reports.income_statement`
- `accounting.reports.monthly`
- `accounting.reports.party_statement`
- `accounting.reports.tafsili_cost_center`
- `accounting.reports.treasury_report`
- `accounting.reports.trial_balance`
- `accounting.reports.vat`

#### Settings (3 مورد)
- `accounting.settings`
- `accounting.settings.tax`
- `accounting.settings.treasury`

#### Tax (4 مورد)
- `accounting.tax.discrepancy_report`
- `accounting.tax.seasonal`
- `accounting.tax.ttms`
- `accounting.tax.validation`
- `accounting.tax.vat`

#### Treasury (8 مورد)
- `accounting.treasury.accounts`
- `accounting.treasury.cash_report`
- `accounting.treasury.checks`
- `accounting.treasury.pay`
- `accounting.treasury.receive`
- `accounting.treasury.reconciliation`
- `accounting.treasury.transactions`
- `accounting.treasury.transfer`

#### Utils (5 مورد)
- `accounting.utils.backup`
- `accounting.utils.close_temp`
- `accounting.utils.closing`
- `accounting.utils.integration`
- `accounting.utils.opening`

---

### Inventory Module (1 مورد)
- `inventory.master_data.item_subcategory` (توجه: در FEATURE_PERMISSION_MAP به صورت `inventory.master.item_subcategories` تعریف شده)

---

### Production Module (1 مورد)
- `production.tracking_identification` (Placeholder)

---

### Ticketing Module (3 مورد)
- `ticketing.management.categories`
- `ticketing.management.subcategories`
- `ticketing.management.templates`

---

## پیشنهادات

1. **Accounting Module**: اکثر feature_code های گم شده مربوط به ماژول Accounting هستند. باید تمام آن‌ها را به `FEATURE_PERMISSION_MAP` اضافه کرد.

2. **Inventory**: یک inconsistency در نامگذاری وجود دارد (`master_data` vs `master`). باید یکسان‌سازی شود.

3. **Production**: `production.tracking_identification` یک placeholder است و ممکن است هنوز نیاز به permission نداشته باشد.

4. **Ticketing**: این ماژول به نظر می‌رسد که در حال توسعه است و باید feature_code هایش به `FEATURE_PERMISSION_MAP` اضافه شود.

---

## نحوه استفاده

برای اضافه کردن feature_code های گم شده به `FEATURE_PERMISSION_MAP`، باید:

1. فایل `shared/permissions.py` را باز کنید
2. هر feature_code گم شده را به صورت `FeaturePermission` تعریف کنید
3. actions مناسب را برای هر feature تعیین کنید
4. بعد از اضافه کردن، باید در `/shared/access-levels/` آن‌ها را برای Access Level های مناسب تنظیم کنید

---

**نکته مهم**: بعد از اضافه کردن هر feature جدید به `FEATURE_PERMISSION_MAP`، حتماً باید در بخش Access Levels سیستم، permission های آن را برای Access Level های مناسب تنظیم کنید، در غیر این صورت کاربران نمی‌توانند به آن بخش دسترسی داشته باشند.


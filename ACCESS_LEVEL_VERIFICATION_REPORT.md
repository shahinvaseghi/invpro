# گزارش بررسی Access Level های کل ماژول‌ها

**تاریخ بررسی**: 2025-01-XX
**وضعیت Migration**: ✅ انجام شد (0027_add_qc_approval_fields_to_transfer_to_line)

---

## خلاصه

از آنجایی که `_prepare_feature_context` در `shared/views/base.py` از `FEATURE_PERMISSION_MAP` استفاده می‌کند، تمام feature_code هایی که در این map تعریف شده‌اند به طور خودکار در صفحه Access Level management نمایش داده می‌شوند.

### تعداد Feature Codes تعریف شده در FEATURE_PERMISSION_MAP: 78 مورد

---

## فهرست کامل Feature Codes تعریف شده (بر اساس ماژول)

### 1. Shared Module (6 مورد)

1. ✅ `shared.companies` - Companies
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

2. ✅ `shared.company_units` - Company Units
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

3. ✅ `shared.smtp_servers` - SMTP Servers
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

4. ✅ `shared.users` - Users
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

5. ✅ `shared.groups` - Groups
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

6. ✅ `shared.access_levels` - Access Levels
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, APPROVE

---

### 2. Production Module (9 مورد)

7. ✅ `production.personnel` - Personnel
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

8. ✅ `production.machines` - Machines
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

9. ✅ `production.work_lines` - Work Lines
   - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

10. ✅ `production.bom` - BOM (Bill of Materials)
    - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

11. ✅ `production.processes` - Processes
    - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, APPROVE

12. ✅ `production.product_orders` - Product Orders
    - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, APPROVE, CREATE_TRANSFER_FROM_ORDER

13. ✅ `production.transfer_requests` - Transfer to Line Requests
    - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, APPROVE, REJECT

14. ✅ `production.transfer_requests.qc_approval` - QC Approval for Transfer to Line Requests (جدید)
    - Actions: VIEW_OWN, VIEW_ALL, APPROVE, REJECT

15. ✅ `production.performance_records` - Performance Records
    - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, EDIT_OTHER, DELETE_OWN, DELETE_OTHER, APPROVE, REJECT, CREATE_RECEIPT

---

### 3. Inventory Module (15 مورد)

#### Master Data (5 مورد)
16. ✅ `inventory.master.item_types` - Item Types
17. ✅ `inventory.master.item_categories` - Item Categories
18. ✅ `inventory.master.item_subcategories` - Item Subcategories
19. ✅ `inventory.master.items` - Items
20. ✅ `inventory.master.item_serials` - Item Serials (only VIEW_OWN, VIEW_ALL)
21. ✅ `inventory.master.warehouses` - Warehouses

#### Suppliers (2 مورد)
22. ✅ `inventory.suppliers.categories` - Supplier Categories
23. ✅ `inventory.suppliers.list` - Suppliers

#### Receipts (3 مورد)
24. ✅ `inventory.receipts.temporary` - Temporary Receipts
25. ✅ `inventory.receipts.permanent` - Permanent Receipts
26. ✅ `inventory.receipts.consignment` - Consignment Receipts

#### Issues (3 مورد)
27. ✅ `inventory.issues.permanent` - Permanent Issues
28. ✅ `inventory.issues.consumption` - Consumption Issues
29. ✅ `inventory.issues.consignment` - Consignment Issues

#### Requests (2 مورد)
30. ✅ `inventory.requests.purchase` - Purchase Requests
31. ✅ `inventory.requests.warehouse` - Warehouse Requests

#### Stocktaking & Balance (3 مورد)
32. ✅ `inventory.stocktaking.deficit` - Stocktaking Deficit
33. ✅ `inventory.stocktaking.surplus` - Stocktaking Surplus
34. ✅ `inventory.stocktaking.records` - Stocktaking Records
35. ✅ `inventory.balance` - Inventory Balance (only VIEW_OWN, VIEW_ALL)

---

### 4. QC Module (1 مورد)

36. ✅ `qc.inspections` - QC Inspections
    - Actions: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, APPROVE, REJECT, CANCEL

---

### 5. Accounting Module (14 مورد)

37. ✅ `accounting.dashboard` - Accounting Dashboard (only VIEW_OWN, VIEW_ALL)

38. ✅ `accounting.fiscal_years` - Fiscal Years

39. ✅ `accounting.accounts` - Chart of Accounts

40. ✅ `accounting.general.ledger` - General Ledger

41. ✅ `accounting.general.subsidiary` - Subsidiary Ledgers

42. ✅ `accounting.general.detail` - Detail Ledgers

43. ✅ `accounting.documents.entry` - Entry Document

44. ✅ `accounting.documents.exit` - Exit Document

45. ✅ `accounting.treasury.expense` - Expense Document

46. ✅ `accounting.treasury.income` - Income Document

47. ✅ `accounting.payroll.payment` - Payroll Payment

48. ✅ `accounting.payroll.insurance_tax` - Insurance and Tax Settings

49. ✅ `accounting.payroll.document` - Payroll Document Upload

50. ✅ `accounting.payroll.bank_transfer` - Bank Transfer Output

---

### 6. Sales Module (2 مورد)

51. ✅ `sales.dashboard` - Sales Dashboard (only VIEW_OWN, VIEW_ALL)

52. ✅ `sales.invoice` - Sales Invoice

---

### 7. HR Module (11 مورد)

53. ✅ `hr.dashboard` - HR Dashboard (only VIEW_OWN, VIEW_ALL)

#### Personnel (5 مورد)
54. ✅ `hr.personnel` - Personnel
55. ✅ `hr.personnel.decree` - Personnel Decree Assignment
56. ✅ `hr.personnel.form` - Personnel Forms
57. ✅ `hr.personnel.form_groups` - Personnel Form Groups
58. ✅ `hr.personnel.form_subgroups` - Personnel Form Sub-Groups

#### Payroll (3 مورد)
59. ✅ `hr.payroll.decrees` - Payroll Decrees
60. ✅ `hr.payroll.decree_groups` - Decree Groups
61. ✅ `hr.payroll.decree_subgroups` - Decree Sub-Groups

#### Requests (3 مورد)
62. ✅ `hr.requests.leave` - Leave Requests
63. ✅ `hr.requests.sick_leave` - Sick Leave Requests
64. ✅ `hr.requests.loan` - Loan Requests

#### Loans (3 مورد)
65. ✅ `hr.loans.management` - Loan Management
66. ✅ `hr.loans.scheduling` - Loan Scheduling
67. ✅ `hr.loans.savings_fund` - Savings Fund

---

### 8. Office Automation Module (4 مورد)

68. ✅ `office_automation.dashboard` - Office Automation Dashboard (only VIEW_OWN, VIEW_ALL)

69. ✅ `office_automation.inbox.incoming` - Incoming Letters

70. ✅ `office_automation.inbox.write` - Write Letter

71. ✅ `office_automation.inbox.fill_form` - Fill Form

72. ✅ `office_automation.processes.engine` - Process Engine

73. ✅ `office_automation.processes.form_connection` - Process-Form Connection

74. ✅ `office_automation.forms.builder` - Form Builder

---

### 9. Transportation Module (1 مورد)

75. ✅ `transportation.dashboard` - Transportation Dashboard (only VIEW_OWN, VIEW_ALL)

---

### 10. Procurement Module (3 مورد)

76. ✅ `procurement.dashboard` - Procurement Dashboard (only VIEW_OWN, VIEW_ALL)

77. ✅ `procurement.purchases` - Purchases

78. ✅ `procurement.buyers` - Buyers

---

## نحوه بررسی

برای بررسی اینکه آیا تمام Access Level ها درست تنظیم شده‌اند:

1. وارد صفحه Access Level management شوید: `/shared/access-levels/`
2. یک Access Level را ویرایش کنید یا ایجاد کنید
3. در بخش "Feature Permissions" تمام feature های بالا را باید ببینید
4. هر ماژول در یک accordion جداگانه نمایش داده می‌شود

---

## نکات مهم

1. ✅ تمام feature_code های تعریف شده در `FEATURE_PERMISSION_MAP` به طور خودکار در Access Level management نمایش داده می‌شوند
2. ✅ permission جدید `production.transfer_requests.qc_approval` اضافه شده و در دسترس است
3. ⚠️ 62 feature_code که در views استفاده شده‌اند اما در `FEATURE_PERMISSION_MAP` تعریف نشده‌اند (بیشتر مربوط به Accounting) - برای جزئیات به `PERMISSION_AUDIT_REPORT.md` مراجعه کنید

---

## اقدامات پیشنهادی

1. ✅ Migration اجرا شد
2. ⏳ بررسی Access Level های موجود و تنظیم permissions برای هر ماژول (به صورت دستی در UI)
3. ⏳ اضافه کردن feature_code های گم شده به `FEATURE_PERMISSION_MAP` (اختیاری - برای Accounting module)

---

**نکته**: این گزارش فقط فهرست feature_code های تعریف شده در `FEATURE_PERMISSION_MAP` را نشان می‌دهد. برای تنظیم دقیق permissions در Access Level ها، باید در UI وارد شوید و برای هر Access Level، permissions مناسب را تنظیم کنید.


# لیست کامل فایل‌های HTML پروژه

**تاریخ ایجاد**: 2024-12-05  
**تعداد کل فایل‌ها**: 198 فایل

---

## 📁 دسته‌بندی بر اساس ماژول

### 🔵 ماژول `shared` (19 فایل)

#### Generic Templates (7 فایل)
- `shared/generic/generic_assignment.html`
- `shared/generic/generic_confirm_delete.html`
- `shared/generic/generic_dashboard.html`
- `shared/generic/generic_detail.html`
- `shared/generic/generic_form.html`
- `shared/generic/generic_list.html`
- `shared/generic/generic_report.html`

#### Partials (5 فایل)
- `shared/partials/empty_state.html`
- `shared/partials/filter_panel.html`
- `shared/partials/pagination.html`
- `shared/partials/row_actions.html`
- `shared/partials/stats_cards.html`

#### Base Templates (2 فایل)
- `shared/base.html`
- `base.html` (root)

#### Specific Views (5 فایل)
- `shared/access_level_detail.html`
- `shared/access_level_form.html`
- `shared/access_levels_list.html`
- `shared/companies.html`
- `shared/company_detail.html`
- `shared/company_form.html`
- `shared/company_unit_detail.html`
- `shared/company_unit_form.html`
- `shared/company_units.html`
- `shared/group_detail.html`
- `shared/group_form.html`
- `shared/groups_list.html`
- `shared/notifications.html`
- `shared/smtp_server_detail.html`
- `shared/smtp_server_form.html`
- `shared/smtp_server_list.html`
- `shared/user_detail.html`
- `shared/user_form.html`
- `shared/users_list.html`

---

### 🟢 ماژول `inventory` (48 فایل)

#### Master Data (15 فایل)
- `inventory/item_categories.html`
- `inventory/itemcategory_detail.html`
- `inventory/item_detail.html`
- `inventory/item_form.html`
- `inventory/item_import_result.html`
- `inventory/item_serials.html`
- `inventory/items.html`
- `inventory/item_subcategories.html`
- `inventory/itemsubcategory_detail.html`
- `inventory/itemtype_detail.html`
- `inventory/item_types.html`
- `inventory/supplier_categories.html`
- `inventory/suppliercategory_detail.html`
- `inventory/supplier_detail.html`
- `inventory/suppliers.html`
- `inventory/warehouse_detail.html`
- `inventory/warehouses.html`

#### Receipts (6 فایل)
- `inventory/receipt_consignment.html`
- `inventory/receipt_detail.html`
- `inventory/receipt_form.html`
- `inventory/receipt_permanent.html`
- `inventory/receipt_serial_assignment.html`
- `inventory/receipt_temporary.html`

#### Issues (5 فایل)
- `inventory/issue_consignment.html`
- `inventory/issue_consumption.html`
- `inventory/issue_detail.html`
- `inventory/issue_permanent.html`
- `inventory/issue_serial_assignment.html`
- `inventory/issue_warehouse_transfer_detail.html`
- `inventory/issue_warehouse_transfer.html`

#### Requests (4 فایل)
- `inventory/purchase_request_detail.html`
- `inventory/purchase_request_form.html`
- `inventory/purchase_requests.html`
- `inventory/warehouse_request_detail.html`
- `inventory/warehouse_request_form.html`
- `inventory/warehouse_requests.html`

#### Stocktaking (6 فایل)
- `inventory/stocktaking_deficit_detail.html`
- `inventory/stocktaking_deficit.html`
- `inventory/stocktaking_form.html`
- `inventory/stocktaking_record_detail.html`
- `inventory/stocktaking_records.html`
- `inventory/stocktaking_surplus_detail.html`
- `inventory/stocktaking_surplus.html`

#### Other (8 فایل)
- `inventory/base.html`
- `inventory/create_issue_from_warehouse_request.html`
- `inventory/create_receipt_from_purchase_request.html`
- `inventory/generic_form.html`
- `inventory/inventory_balance_details.html`
- `inventory/inventory_balance.html`
- `inventory/widgets/jalali_date_input.html`

---

### 🟡 ماژول `production` (30 فایل)

#### Master Data (12 فایل)
- `production/bom_detail.html`
- `production/bom_form.html`
- `production/bom_list.html`
- `production/machine_detail.html`
- `production/machine_form.html`
- `production/machines.html`
- `production/person_detail.html`
- `production/person_form.html`
- `production/personnel.html`
- `production/process_detail.html`
- `production/processes.html`
- `production/process_form.html`
- `production/product_order_detail.html`
- `production/product_order_form.html`
- `production/product_orders.html`
- `production/work_line_detail.html`
- `production/work_line_form.html`
- `production/work_lines.html`

#### Documents (12 فایل)
- `production/performance_record_detail.html`
- `production/performance_record_form.html`
- `production/performance_record_list.html`
- `production/performance_records.html`
- `production/rework_document_form.html`
- `production/rework_document_list.html`
- `production/rework.html`
- `production/rework_order_select.html`
- `production/transfer_to_line_detail.html`
- `production/transfer_to_line_form.html`
- `production/transfer_to_line_list.html`
- `production/transfer_requests.html`

#### Operations (4 فایل)
- `production/qc_operations_list.html`
- `production/rework_operations_list.html`
- `production/tracking_identification.html`

---

### 🔴 ماژول `accounting` (24 فایل)

#### Master Data (6 فایل)
- `accounting/account_detail.html`
- `accounting/fiscal_year_detail.html`
- `accounting/gl_account_detail.html`
- `accounting/sub_account_detail.html`
- `accounting/tafsili_account_detail.html`
- `accounting/tafsili_hierarchy_detail.html`

#### Treasury (4 فایل)
- `accounting/treasury/account_form.html`
- `accounting/treasury/accounts.html`
- `accounting/treasury/expense.html`
- `accounting/treasury/income.html`

#### Parties (4 فایل)
- `accounting/parties/accounts.html`
- `accounting/parties/list.html`
- `accounting/parties/party_account_form.html`
- `accounting/parties/party_form.html`

#### Income/Expense (4 فایل)
- `accounting/income_expense/categories.html`
- `accounting/income_expense/category_form.html`
- `accounting/income_expense/cost_center_form.html`
- `accounting/income_expense/cost_centers.html`

#### Documents (3 فایل)
- `accounting/documents/entry.html`
- `accounting/documents/exit.html`

#### General Ledger (3 فایل)
- `accounting/general/detail_list.html`
- `accounting/general/ledger_list.html`
- `accounting/general/subsidiary_list.html`

#### Attachments (2 فایل)
- `accounting/attachments/list.html`
- `accounting/attachments/upload.html`

#### Other (2 فایل)
- `accounting/dashboard.html`
- `accounting/payroll/document.html`

---

### 🟣 ماژول `ticketing` (18 فایل)

#### Master Data (12 فایل)
- `ticketing/categories.html`
- `ticketing/categories_list.html`
- `ticketing/category_detail.html`
- `ticketing/category_form.html`
- `ticketing/subcategories.html`
- `ticketing/subcategories_list.html`
- `ticketing/subcategory_detail.html`
- `ticketing/subcategory_form.html`
- `ticketing/template_create.html`
- `ticketing/template_detail.html`
- `ticketing/template_form.html`
- `ticketing/templates_list.html`

#### Tickets (4 فایل)
- `ticketing/ticket_create.html`
- `ticketing/ticket_detail.html`
- `ticketing/ticket_respond.html`

#### Other (2 فایل)
- `ticketing/auto_response.html`
- `ticketing/base.html`

---

### 🟠 ماژول `qc` (3 فایل)
- `qc/temporary_receipt_line_selection.html`
- `qc/temporary_receipt_rejection_management.html`
- `qc/temporary_receipts.html`

---

### ⚪ ماژول‌های دیگر

#### HR (13 فایل)
- `hr/dashboard.html`
- `hr/loans/management.html`
- `hr/loans/savings_fund.html`
- `hr/loans/scheduling.html`
- `hr/payroll/decree_group_list.html`
- `hr/payroll/decree_list.html`
- `hr/payroll/decree_subgroup_list.html`
- `hr/personnel/create.html`
- `hr/personnel/decree_assignment.html`
- `hr/personnel/form_create.html`
- `hr/personnel/form_group_list.html`
- `hr/personnel/form_subgroup_list.html`
- `hr/requests/leave.html`
- `hr/requests/loan.html`
- `hr/requests/sick_leave.html`

#### Office Automation (7 فایل)
- `office_automation/dashboard.html`
- `office_automation/forms/builder.html`
- `office_automation/inbox/fill_form.html`
- `office_automation/inbox/incoming_letters.html`
- `office_automation/inbox/write_letter.html`
- `office_automation/processes/engine.html`
- `office_automation/processes/form_connection.html`

#### Procurement (5 فایل)
- `procurement/buyer_assignment.html`
- `procurement/buyer_form.html`
- `procurement/buyer_list.html`
- `procurement/dashboard.html`
- `procurement/purchase_list.html`

#### Sales (2 فایل)
- `sales/dashboard.html`
- `sales/invoice_create.html`

#### Transportation (1 فایل)
- `transportation/dashboard.html`

#### UI Components (3 فایل)
- `ui/components/modules_menu.html`
- `ui/components/sidebar.html`
- `ui/dashboard.html`

#### Root (1 فایل)
- `login.html`

---

## 📊 خلاصه آماری

| ماژول | تعداد فایل | درصد |
|-------|-----------|------|
| `inventory` | 48 | 24.2% |
| `production` | 30 | 15.2% |
| `accounting` | 24 | 12.1% |
| `shared` | 19 | 9.6% |
| `ticketing` | 18 | 9.1% |
| `hr` | 13 | 6.6% |
| `office_automation` | 7 | 3.5% |
| `procurement` | 5 | 2.5% |
| `qc` | 3 | 1.5% |
| `sales` | 2 | 1.0% |
| `ui` | 3 | 1.5% |
| `transportation` | 1 | 0.5% |
| `root` | 1 | 0.5% |
| **جمع کل** | **198** | **100%** |

---

## 📝 نکات مهم

1. **Generic Templates**: فایل‌های `shared/generic/*.html` به عنوان base templates استفاده می‌شوند
2. **Partials**: فایل‌های `shared/partials/*.html` به عنوان reusable components استفاده می‌شوند
3. **Custom Templates**: برخی فایل‌ها (مثل `inventory/generic_form.html`) برای ماژول‌های خاص هستند
4. **Detail Templates**: تمام ماژول‌ها دارای templateهای `*_detail.html` برای نمایش جزئیات هستند
5. **Form Templates**: تمام ماژول‌ها دارای templateهای `*_form.html` برای فرم‌های create/edit هستند

---

**آخرین به‌روزرسانی**: 2024-12-05


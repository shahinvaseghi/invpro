# Generic Templates Migration Checklist

این فایل چک‌لیست کامل برای migration صفحات موجود به Generic Templates است.

## 📋 استراتژی Migration

### اصول کلی:
1. **از ساده به پیچیده**: ابتدا صفحات ساده، سپس صفحات پیچیده
2. **ماژول به ماژول**: یک ماژول را کامل کنید، سپس به ماژول بعدی بروید
3. **تست بعد از هر مرحله**: بعد از هر migration، تست کامل انجام دهید
4. **Backup**: قبل از هر تغییر، از فایل اصلی backup بگیرید

### مراحل Migration:
1. بررسی فایل موجود و شناسایی Context Variables
2. ایجاد view جدید یا به‌روزرسانی view موجود
3. تست در محیط development
4. تست UI/UX و responsive design
5. تست i18n (Persian/English)
6. تست permissions
7. Commit و push

---

## ✅ Phase 1: Migration صفحات List ساده - Shared Module

**اولویت**: بالا (ساده‌ترین صفحات)

### فایل‌های قابل جایگزینی:

- [ ] `templates/shared/companies.html` → `generic_list.html`
  - Context: `companies` → `object_list`
  - Headers: `public_code`, `display_name`, `legal_name`, `is_enabled`
  - Filter: search, status
  - Create URL: `shared:company_create`

- [ ] `templates/shared/company_units.html` → `generic_list.html`
  - Context: `company_units` → `object_list`
  - Headers: `public_code`, `name`, `parent_unit.name`, `is_enabled`
  - Filter: search, status
  - Create URL: `shared:company_unit_create`

- [ ] `templates/shared/users_list.html` → `generic_list.html`
  - Context: `users` → `object_list`
  - Headers: `username`, `email`, `first_name`, `last_name`, `is_active`
  - Filter: search, status
  - Create URL: `shared:user_create`

- [ ] `templates/shared/groups_list.html` → `generic_list.html`
  - Context: `groups` → `object_list`
  - Headers: `name`, `description`, `is_enabled`
  - Filter: search, status
  - Create URL: `shared:group_create`

- [ ] `templates/shared/access_levels_list.html` → `generic_list.html`
  - Context: `access_levels` → `object_list`
  - Headers: `code`, `name`, `description`, `is_enabled`
  - Filter: search, status
  - Create URL: `shared:access_level_create`

- [ ] `templates/shared/smtp_server_list.html` → `generic_list.html`
  - Context: `smtp_servers` → `object_list`
  - Headers: `name`, `host`, `port`, `is_enabled`
  - Filter: search, status
  - Create URL: `shared:smtp_server_create`

**نکات مهم**:
- تمام این صفحات ساختار مشابه دارند
- فیلتر ساده (search + status)
- بدون formset یا منطق پیچیده
- مناسب برای شروع migration

---

## ✅ Phase 2: Migration صفحات List - Inventory Master Data

**اولویت**: بالا (ساده، اما بیشتر)

### فایل‌های قابل جایگزینی:

- [ ] `templates/inventory/items.html` → `generic_list.html`
  - Context: `items` → `object_list`
  - Headers: `item_code`, `name`, `type.name`, `category.name`, `is_enabled`
  - Filter: search, type, category, status
  - Create URL: `inventory:item_create`
  - **نکته**: ممکن است نیاز به nested attributes داشته باشد

- [ ] `templates/inventory/item_types.html` → `generic_list.html`
  - Context: `item_types` → `object_list`
  - Headers: `public_code`, `name`, `is_enabled`
  - Filter: search, status
  - Create URL: `inventory:item_type_create`

- [ ] `templates/inventory/item_categories.html` → `generic_list.html`
  - Context: `item_categories` → `object_list`
  - Headers: `public_code`, `name`, `type.name`, `is_enabled`
  - Filter: search, type, status
  - Create URL: `inventory:item_category_create`

- [ ] `templates/inventory/item_subcategories.html` → `generic_list.html`
  - Context: `item_subcategories` → `object_list`
  - Headers: `public_code`, `name`, `category.name`, `is_enabled`
  - Filter: search, category, status
  - Create URL: `inventory:item_subcategory_create`

- [ ] `templates/inventory/warehouses.html` → `generic_list.html`
  - Context: `warehouses` → `object_list`
  - Headers: `public_code`, `name`, `is_enabled`
  - Filter: search, status
  - Create URL: `inventory:warehouse_create`

- [ ] `templates/inventory/suppliers.html` → `generic_list.html`
  - Context: `suppliers` → `object_list`
  - Headers: `public_code`, `name`, `supplier_code`, `is_enabled`
  - Filter: search, status
  - Create URL: `inventory:supplier_create`

- [ ] `templates/inventory/supplier_categories.html` → `generic_list.html`
  - Context: `supplier_categories` → `object_list`
  - Headers: `public_code`, `name`, `is_enabled`
  - Filter: search, status
  - Create URL: `inventory:supplier_category_create`

**نکات مهم**:
- برخی صفحات nested attributes دارند (مثل `type.name`)
- باید از template tag `getattr` استفاده شود
- فیلترها ممکن است cascading باشند (type → category → subcategory)

---

## ✅ Phase 3: Migration صفحات List با فیلتر پیچیده - Inventory Documents

**اولویت**: متوسط (فیلتر پیچیده‌تر)

### فایل‌های قابل جایگزینی:

- [ ] `templates/inventory/purchase_requests.html` → `generic_list.html`
  - Context: `purchase_requests` → `object_list`
  - Headers: `request_code`, `request_date`, `request_status`, `priority`, `is_locked`
  - Filter: search, status, priority, date range
  - Create URL: `inventory:purchase_request_create`
  - **نکته**: ممکن است stats summary داشته باشد

- [ ] `templates/inventory/warehouse_requests.html` → `generic_list.html`
  - Context: `warehouse_requests` → `object_list`
  - Headers: `request_code`, `request_date`, `request_status`, `priority`, `is_locked`
  - Filter: search, status, priority, date range
  - Create URL: `inventory:warehouse_request_create`

- [ ] `templates/inventory/receipt_temporary.html` → `generic_list.html`
  - Context: `receipts` → `object_list`
  - Headers: `document_code`, `document_date`, `supplier.name`, `status`, `is_locked`
  - Filter: search, status, supplier, date range
  - Create URL: `inventory:receipt_temporary_create`
  - **نکته**: ممکن است stats summary داشته باشد (awaiting_qc, qc_passed, etc.)

- [ ] `templates/inventory/receipt_permanent.html` → `generic_list.html`
  - Context: `receipts` → `object_list`
  - Headers: `document_code`, `document_date`, `supplier.name`, `is_locked`
  - Filter: search, supplier, date range
  - Create URL: `inventory:receipt_permanent_create`

- [ ] `templates/inventory/receipt_consignment.html` → `generic_list.html`
  - Context: `receipts` → `object_list`
  - Headers: `document_code`, `document_date`, `supplier.name`, `is_locked`
  - Filter: search, supplier, date range
  - Create URL: `inventory:receipt_consignment_create`

- [ ] `templates/inventory/issue_permanent.html` → `generic_list.html`
  - Context: `issues` → `object_list`
  - Headers: `document_code`, `document_date`, `destination_type`, `is_locked`
  - Filter: search, date range
  - Create URL: `inventory:issue_permanent_create`

- [ ] `templates/inventory/issue_consumption.html` → `generic_list.html`
  - Context: `issues` → `object_list`
  - Headers: `document_code`, `document_date`, `destination_type`, `is_locked`
  - Filter: search, date range
  - Create URL: `inventory:issue_consumption_create`

- [ ] `templates/inventory/issue_consignment.html` → `generic_list.html`
  - Context: `issues` → `object_list`
  - Headers: `document_code`, `document_date`, `destination_type`, `is_locked`
  - Filter: search, date range
  - Create URL: `inventory:issue_consignment_create`

- [ ] `templates/inventory/stocktaking_deficit.html` → `generic_list.html`
  - Context: `deficits` → `object_list`
  - Headers: `document_code`, `document_date`, `warehouse.name`, `is_locked`
  - Filter: search, warehouse, date range
  - Create URL: `inventory:stocktaking_deficit_create`

- [ ] `templates/inventory/stocktaking_surplus.html` → `generic_list.html`
  - Context: `surpluses` → `object_list`
  - Headers: `document_code`, `document_date`, `warehouse.name`, `is_locked`
  - Filter: search, warehouse, date range
  - Create URL: `inventory:stocktaking_surplus_create`

- [ ] `templates/inventory/stocktaking_records.html` → `generic_list.html`
  - Context: `records` → `object_list`
  - Headers: `record_code`, `record_date`, `is_locked`
  - Filter: search, date range
  - Create URL: `inventory:stocktaking_record_create`

**نکات مهم**:
- این صفحات ممکن است stats summary داشته باشند
- فیلترهای date range نیاز به تنظیمات خاص دارند
- برخی صفحات ممکن است workflow buttons داشته باشند (approve, reject)

---

## ✅ Phase 4: Migration صفحات List - Production Module

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/production/bom_list.html` → `generic_list.html`
  - Context: `boms` → `object_list`
  - Headers: `bom_code`, `finished_item.name`, `version`, `is_enabled`
  - Filter: search, finished_item, status
  - Create URL: `production:bom_create`

- [ ] `templates/production/processes.html` → `generic_list.html`
  - Context: `processes` → `object_list`
  - Headers: `process_code`, `finished_item.name`, `revision`, `is_enabled`
  - Filter: search, finished_item, status
  - Create URL: `production:process_create`

- [ ] `templates/production/product_orders.html` → `generic_list.html`
  - Context: `orders` → `object_list`
  - Headers: `order_code`, `finished_item.name`, `quantity_planned`, `status`, `due_date`
  - Filter: search, status, date range
  - Create URL: `production:product_order_create`

- [ ] `templates/production/machines.html` → `generic_list.html`
  - Context: `machines` → `object_list`
  - Headers: `public_code`, `name`, `machine_type`, `work_center.name`, `status`
  - Filter: search, machine_type, status
  - Create URL: `production:machine_create`

- [ ] `templates/production/personnel.html` → `generic_list.html`
  - Context: `persons` → `object_list`
  - Headers: `public_code`, `first_name`, `last_name`, `personnel_code`, `is_enabled`
  - Filter: search, status
  - Create URL: `production:person_create`

- [ ] `templates/production/work_lines.html` → `generic_list.html`
  - Context: `work_lines` → `object_list`
  - Headers: `public_code`, `name`, `warehouse.name`, `is_enabled`
  - Filter: search, warehouse, status
  - Create URL: `production:work_line_create`

- [ ] `templates/production/transfer_to_line_list.html` → `generic_list.html`
  - Context: `transfers` → `object_list`
  - Headers: `transfer_code`, `order.order_code`, `status`, `transfer_date`
  - Filter: search, status, date range
  - Create URL: `production:transfer_to_line_create`

- [ ] `templates/production/performance_record_list.html` → `generic_list.html`
  - Context: `records` → `object_list`
  - Headers: `record_code`, `order.order_code`, `status`, `record_date`
  - Filter: search, status, date range
  - Create URL: `production:performance_record_create`

**نکات مهم**:
- برخی صفحات nested attributes دارند
- ممکن است workflow buttons داشته باشند

---

## ✅ Phase 5: Migration صفحات List - Ticketing Module

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/ticketing/categories_list.html` → `generic_list.html`
  - Context: `categories` → `object_list`
  - Headers: `public_code`, `name`, `parent_category.name`, `is_enabled`
  - Filter: search, status
  - Create URL: `ticketing:category_create`

- [ ] `templates/ticketing/subcategories_list.html` → `generic_list.html`
  - Context: `subcategories` → `object_list`
  - Headers: `public_code`, `name`, `category.name`, `is_enabled`
  - Filter: search, category, status
  - Create URL: `ticketing:subcategory_create`

- [ ] `templates/ticketing/templates_list.html` → `generic_list.html`
  - Context: `templates` → `object_list`
  - Headers: `template_code`, `name`, `category.name`, `is_enabled`
  - Filter: search, category, status
  - Create URL: `ticketing:template_create`

**نکات مهم**:
- ساختار ساده
- nested attributes برای parent_category

---

## ✅ Phase 6: Migration صفحات Form ساده - Shared Module

**اولویت**: بالا (ساده‌ترین فرم‌ها)

### فایل‌های قابل جایگزینی:

- [ ] `templates/shared/company_form.html` → `generic_form.html`
  - Form: `CompanyForm`
  - Fields: `public_code`, `legal_name`, `display_name`, `registration_number`, `tax_id`, `phone_number`, `email`, `website`, `address`, `city`, `state`, `country`, `is_enabled`
  - Cancel URL: `shared:companies`

- [ ] `templates/shared/company_unit_form.html` → `generic_form.html`
  - Form: `CompanyUnitForm`
  - Fields: `public_code`, `name`, `parent_unit`, `is_enabled`
  - Cancel URL: `shared:company_units`

- [ ] `templates/shared/user_form.html` → `generic_form.html`
  - Form: `UserCreateForm` / `UserUpdateForm`
  - Fields: `username`, `email`, `first_name`, `last_name`, `phone_number`, `mobile_number`, `is_active`, `is_staff`, `is_superuser`, `groups`, `default_company`
  - Cancel URL: `shared:users`
  - **نکته**: ممکن است formset برای UserCompanyAccess داشته باشد

- [ ] `templates/shared/group_form.html` → `generic_form.html`
  - Form: `GroupForm`
  - Fields: `name`, `description`, `is_enabled`, `members`, `access_level`
  - Cancel URL: `shared:groups`

- [ ] `templates/shared/access_level_form.html` → `generic_form.html`
  - Form: `AccessLevelForm`
  - Fields: `code`, `name`, `description`, `is_enabled`, `is_global`
  - Cancel URL: `shared:access_levels`
  - **نکته**: ممکن است permission matrix داشته باشد (نیاز به override block)

- [ ] `templates/shared/smtp_server_form.html` → `generic_form.html`
  - Form: `SMTPServerForm`
  - Fields: `name`, `host`, `port`, `username`, `password`, `use_tls`, `use_ssl`, `is_enabled`
  - Cancel URL: `shared:smtp_servers`

**نکات مهم**:
- بیشتر فرم‌ها ساده هستند
- `access_level_form.html` ممکن است نیاز به override block برای permission matrix داشته باشد
- `user_form.html` ممکن است formset داشته باشد

---

## ✅ Phase 7: Migration صفحات Form - Inventory Master Data

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/inventory/item_form.html` → `generic_form.html`
  - Form: `ItemForm`
  - Fieldsets: Basic Info, Classification, Units, Warehouses
  - Cancel URL: `inventory:items`
  - **نکته**: ممکن است formset برای ItemUnit داشته باشد

- [ ] `templates/inventory/itemtype_form.html` → `generic_form.html`
  - Form: `ItemTypeForm`
  - Fields: `public_code`, `name`, `is_enabled`
  - Cancel URL: `inventory:item_types`

- [ ] `templates/inventory/itemcategory_form.html` → `generic_form.html`
  - Form: `ItemCategoryForm`
  - Fields: `public_code`, `name`, `type`, `is_enabled`
  - Cancel URL: `inventory:item_categories`

- [ ] `templates/inventory/itemsubcategory_form.html` → `generic_form.html`
  - Form: `ItemSubcategoryForm`
  - Fields: `public_code`, `name`, `category`, `is_enabled`
  - Cancel URL: `inventory:item_subcategories`

- [ ] `templates/inventory/warehouse_form.html` → `generic_form.html`
  - Form: `WarehouseForm`
  - Fields: `public_code`, `name`, `is_enabled`
  - Cancel URL: `inventory:warehouses`

- [ ] `templates/inventory/supplier_form.html` → `generic_form.html`
  - Form: `SupplierForm`
  - Fields: `public_code`, `name`, `supplier_code`, `category`, `phone_number`, `email`, `address`, `is_enabled`
  - Cancel URL: `inventory:suppliers`

- [ ] `templates/inventory/suppliercategory_form.html` → `generic_form.html`
  - Form: `SupplierCategoryForm`
  - Fields: `public_code`, `name`, `is_enabled`
  - Cancel URL: `inventory:supplier_categories`

**نکات مهم**:
- `item_form.html` پیچیده است و ممکن است formset داشته باشد
- سایر فرم‌ها ساده هستند

---

## ✅ Phase 8: Migration صفحات Form پیچیده - Inventory Documents

**اولویت**: پایین (پیچیده‌ترین فرم‌ها)

### فایل‌های قابل جایگزینی:

- [ ] `templates/inventory/purchase_request_form.html` → `generic_form.html`
  - Form: `PurchaseRequestForm` + `PurchaseRequestLineFormSet`
  - Fieldsets: Header, Lines
  - Cancel URL: `inventory:purchase_requests`
  - **نکته**: نیاز به formset handling

- [ ] `templates/inventory/warehouse_request_form.html` → `generic_form.html`
  - Form: `WarehouseRequestForm` + `WarehouseRequestLineFormSet`
  - Fieldsets: Header, Lines
  - Cancel URL: `inventory:warehouse_requests`
  - **نکته**: نیاز به formset handling

- [ ] `templates/inventory/receipt_form.html` → `generic_form.html`
  - Form: `ReceiptPermanentForm` / `ReceiptConsignmentForm` + Line Formset
  - Fieldsets: Header, Lines, Serials
  - Cancel URL: `inventory:receipt_permanent_list`
  - **نکته**: بسیار پیچیده - نیاز به formset + serial management

- [ ] `templates/inventory/stocktaking_form.html` → `generic_form.html`
  - Form: `StocktakingDeficitForm` / `StocktakingSurplusForm` + Line Formset
  - Fieldsets: Header, Lines
  - Cancel URL: `inventory:stocktaking_deficit_list`
  - **نکته**: نیاز به formset handling

**نکات مهم**:
- این فرم‌ها پیچیده‌ترین هستند
- نیاز به formset handling دارند
- ممکن است نیاز به override blocks داشته باشند
- بهتر است در آخر migration شوند

---

## ✅ Phase 9: Migration صفحات Form - Production Module

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/production/bom_form.html` → `generic_form.html`
  - Form: `BOMForm` + `BOMMaterialLineFormSet`
  - Fieldsets: Header, Materials
  - Cancel URL: `production:bom_list`
  - **نکته**: نیاز به formset handling

- [ ] `templates/production/process_form.html` → `generic_form.html`
  - Form: `ProcessForm` + `ProcessStepFormSet`
  - Fieldsets: Header, Steps
  - Cancel URL: `production:processes`
  - **نکته**: نیاز به formset handling

- [ ] `templates/production/product_order_form.html` → `generic_form.html`
  - Form: `ProductOrderForm`
  - Fields: `bom`, `quantity_planned`, `due_date`, `priority`, `customer_reference`, `notes`
  - Cancel URL: `production:product_orders`

- [ ] `templates/production/machine_form.html` → `generic_form.html`
  - Form: `MachineForm`
  - Fields: `name`, `machine_type`, `work_center`, `manufacturer`, `model_number`, `serial_number`, `status`, `is_enabled`
  - Cancel URL: `production:machines`

- [ ] `templates/production/person_form.html` → `generic_form.html`
  - Form: `PersonForm`
  - Fields: `first_name`, `last_name`, `personnel_code`, `username`, `phone_number`, `mobile_number`, `email`, `company_units`, `is_enabled`
  - Cancel URL: `production:personnel`

- [ ] `templates/production/work_line_form.html` → `generic_form.html`
  - Form: `WorkLineForm`
  - Fields: `name`, `warehouse`, `personnel`, `machines`, `is_enabled`
  - Cancel URL: `production:work_lines`
  - **نکته**: ManyToMany fields

- [ ] `templates/production/transfer_to_line_form.html` → `generic_form.html`
  - Form: `TransferToLineForm` + `TransferToLineItemFormSet`
  - Fieldsets: Header, Items
  - Cancel URL: `production:transfer_to_line_list`
  - **نکته**: نیاز به formset handling

- [ ] `templates/production/performance_record_form.html` → `generic_form.html`
  - Form: `PerformanceRecordForm` + Multiple Formsets
  - Fieldsets: Header, Materials, Personnel, Machines
  - Cancel URL: `production:performance_record_list`
  - **نکته**: بسیار پیچیده - چندین formset

**نکات مهم**:
- برخی فرم‌ها formset دارند
- `performance_record_form.html` بسیار پیچیده است

---

## ✅ Phase 10: Migration صفحات Form - Ticketing Module

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/ticketing/category_form.html` → `generic_form.html`
  - Form: `TicketCategoryForm`
  - Fields: `public_code`, `name`, `parent_category`, `is_enabled`
  - Cancel URL: `ticketing:categories`

- [ ] `templates/ticketing/subcategory_form.html` → `generic_form.html`
  - Form: `TicketSubcategoryForm`
  - Fields: `public_code`, `name`, `category`, `is_enabled`
  - Cancel URL: `ticketing:subcategories`

- [ ] `templates/ticketing/template_form.html` → `generic_form.html`
  - Form: `TicketTemplateForm` + Multiple Formsets
  - Fieldsets: Header, Fields, Permissions, Events
  - Cancel URL: `ticketing:templates`
  - **نکته**: بسیار پیچیده - چندین formset

**نکات مهم**:
- `template_form.html` بسیار پیچیده است

---

## ✅ Phase 11: Migration صفحات Confirm Delete

**اولویت**: بالا (ساده و تکراری)

### فایل‌های قابل جایگزینی (28 فایل):

**Shared Module:**
- [ ] `templates/shared/company_confirm_delete.html`
- [ ] `templates/shared/company_unit_confirm_delete.html`
- [ ] `templates/shared/user_confirm_delete.html`
- [ ] `templates/shared/group_confirm_delete.html`
- [ ] `templates/shared/access_level_confirm_delete.html`
- [ ] `templates/shared/smtp_server_confirm_delete.html`

**Inventory Module:**
- [ ] `templates/inventory/item_confirm_delete.html`
- [ ] `templates/inventory/itemtype_confirm_delete.html`
- [ ] `templates/inventory/itemcategory_confirm_delete.html`
- [ ] `templates/inventory/itemsubcategory_confirm_delete.html`
- [ ] `templates/inventory/warehouse_confirm_delete.html`
- [ ] `templates/inventory/supplier_confirm_delete.html`
- [ ] `templates/inventory/suppliercategory_confirm_delete.html`
- [ ] `templates/inventory/receipt_temporary_confirm_delete.html`
- [ ] `templates/inventory/receipt_permanent_confirm_delete.html`
- [ ] `templates/inventory/receipt_consignment_confirm_delete.html`
- [ ] `templates/inventory/issue_permanent_confirm_delete.html`
- [ ] `templates/inventory/issue_consumption_confirm_delete.html`
- [ ] `templates/inventory/issue_consignment_confirm_delete.html`
- [ ] `templates/inventory/stocktaking_deficit_confirm_delete.html`
- [ ] `templates/inventory/stocktaking_surplus_confirm_delete.html`
- [ ] `templates/inventory/stocktaking_record_confirm_delete.html`

**Production Module:**
- [ ] `templates/production/bom_confirm_delete.html`
- [ ] `templates/production/process_confirm_delete.html`
- [ ] `templates/production/product_order_confirm_delete.html`
- [ ] `templates/production/machine_confirm_delete.html`
- [ ] `templates/production/person_confirm_delete.html`
- [ ] `templates/production/work_line_confirm_delete.html`
- [ ] `templates/production/transfer_to_line_confirm_delete.html`
- [ ] `templates/production/performance_record_confirm_delete.html`

**Ticketing Module:**
- [ ] `templates/ticketing/category_confirm_delete.html`
- [ ] `templates/ticketing/subcategory_confirm_delete.html`
- [ ] `templates/ticketing/template_confirm_delete.html`

**نکات مهم**:
- تمام این صفحات ساختار یکسان دارند
- فقط نیاز به تنظیم Context Variables دارند
- سریع‌ترین migration

---

## ✅ Phase 12: Migration صفحات Detail

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/inventory/receipt_detail.html` → `generic_detail.html`
  - Context: `receipt` → `object`
  - Sections: Header Info, Lines Table, Serials, Attachments
  - Actions: Back, Edit, Delete, Lock

- [ ] `templates/inventory/issue_detail.html` → `generic_detail.html`
  - Context: `issue` → `object`
  - Sections: Header Info, Lines Table, Serials, Attachments
  - Actions: Back, Edit, Delete, Lock

**نکات مهم**:
- ممکن است نیاز به sections پیچیده داشته باشند
- ممکن است نیاز به override blocks داشته باشند

---

## ✅ Phase 13: Migration صفحات Dashboard

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/ui/dashboard.html` → `generic_dashboard.html`
- [ ] `templates/accounting/dashboard.html` → `generic_dashboard.html`
- [ ] `templates/hr/dashboard.html` → `generic_dashboard.html`
- [ ] `templates/office_automation/dashboard.html` → `generic_dashboard.html`
- [ ] `templates/procurement/dashboard.html` → `generic_dashboard.html`
- [ ] `templates/sales/dashboard.html` → `generic_dashboard.html`
- [ ] `templates/transportation/dashboard.html` → `generic_dashboard.html`

**نکات مهم**:
- هر dashboard ممکن است cards مختلف داشته باشد
- نیاز به تنظیم Context Variables برای cards

---

## ✅ Phase 14: Migration صفحات Assignment

**اولویت**: متوسط

### فایل‌های قابل جایگزینی:

- [ ] `templates/inventory/receipt_serial_assignment.html` → `generic_assignment.html`
  - Context: `receipt_line` → `object`
  - Table: Serials with checkboxes
  - Actions: Save, Cancel, Back

- [ ] `templates/inventory/issue_serial_assignment.html` → `generic_assignment.html`
  - Context: `issue_line` → `object`
  - Table: Available Serials with checkboxes
  - Actions: Save, Cancel, Back

- [ ] `templates/procurement/buyer_assignment.html` → `generic_assignment.html`
  - Context: Custom
  - Table: Buyers with assignments
  - Actions: Save, Cancel

- [ ] `templates/hr/personnel/decree_assignment.html` → `generic_assignment.html`
  - Context: Custom
  - Table: Personnel with assignments
  - Actions: Save, Cancel

**نکات مهم**:
- هر صفحه ممکن است ساختار table متفاوتی داشته باشد
- نیاز به تنظیم Context Variables برای table cells

---

## ✅ Phase 15: Migration صفحات Report

**اولویت**: پایین (پیچیده)

### فایل‌های قابل جایگزینی:

- [ ] `templates/inventory/inventory_balance.html` → `generic_report.html`
  - Context: `balances` → `table_data`
  - Filters: Warehouse, Item Type, Category, As-of Date
  - Stats: Total Items, Total Balance
  - Export: Excel/CSV
  - **نکته**: بسیار پیچیده - نیاز به تنظیمات خاص

- [ ] `templates/inventory/inventory_balance_details.html` → `generic_report.html`
  - Context: `balance_details` → `table_data`
  - Filters: Warehouse, Item, Date Range
  - Export: Excel/CSV
  - **نکته**: پیچیده

**نکات مهم**:
- این صفحات پیچیده‌ترین هستند
- نیاز به فیلترهای پیشرفته
- نیاز به export functionality
- بهتر است در آخر migration شوند

---

## ✅ Phase 16: Testing و Validation

**اولویت**: الزامی (بعد از هر phase)

### چک‌لیست Testing:

**Functional Testing:**
- [ ] تمام CRUD operations کار می‌کنند
- [ ] فیلترها و جستجو کار می‌کنند
- [ ] Pagination کار می‌کند
- [ ] Permissions درست اعمال می‌شوند
- [ ] Error handling درست است

**UI/UX Testing:**
- [ ] Responsive design در موبایل و دسکتاپ
- [ ] RTL/LTR درست کار می‌کند
- [ ] تمام buttons و links کار می‌کنند
- [ ] Empty states درست نمایش داده می‌شوند
- [ ] Loading states درست هستند

**i18n Testing:**
- [ ] تمام متن‌ها translate می‌شوند
- [ ] تاریخ‌ها به درستی نمایش داده می‌شوند (Jalali)
- [ ] RTL layout درست است

**Browser Testing:**
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (اگر در دسترس است)

**Performance Testing:**
- [ ] صفحات با داده زیاد سریع لود می‌شوند
- [ ] Pagination درست کار می‌کند
- [ ] Query optimization انجام شده است

---

## 📝 نکات مهم Migration

### 1. قبل از شروع:
- از فایل اصلی backup بگیرید
- Branch جدید ایجاد کنید
- Context Variables را شناسایی کنید

### 2. در حین Migration:
- ابتدا view را به‌روزرسانی کنید
- Context Variables را تنظیم کنید
- Template را تغییر دهید
- تست کنید

### 3. بعد از Migration:
- تست کامل انجام دهید
- Code review کنید
- Commit کنید
- Documentation به‌روزرسانی کنید

### 4. Override Blocks:
اگر نیاز به سفارشی‌سازی دارید، می‌توانید blocks را override کنید:
```django
{% extends "shared/generic/generic_list.html" %}
{% block table_rows %}
  <!-- Custom table rows -->
{% endblock %}
```

### 5. Context Variables:
همیشه Context Variables را در view تنظیم کنید، نه در template.

### 6. Error Handling:
مطمئن شوید که error handling درست است.

---

## 📊 آمار Migration

- **کل فایل‌های قابل جایگزینی**: ~104 فایل
- **صفحات List**: ~35 فایل
- **صفحات Form**: ~26 فایل
- **صفحات Confirm Delete**: ~28 فایل
- **صفحات Detail**: ~2 فایل
- **صفحات Dashboard**: ~7 فایل
- **صفحات Assignment**: ~4 فایل
- **صفحات Report**: ~2 فایل

---

## 🎯 اولویت‌بندی

1. **اولویت بالا**: Phase 1, 6, 11 (ساده‌ترین)
2. **اولویت متوسط**: Phase 2, 3, 4, 5, 7, 9, 10, 12, 13, 14
3. **اولویت پایین**: Phase 8, 15 (پیچیده‌ترین)

---

## ✅ نحوه استفاده از این چک‌لیست

1. از Phase 1 شروع کنید
2. هر فایل را یکی یکی migration کنید
3. بعد از هر migration، تست کنید
4. checkbox را تیک بزنید
5. به فایل بعدی بروید
6. بعد از اتمام هر phase، commit کنید
7. به phase بعدی بروید

---

## 📚 منابع

- `templates/shared/generic/README.md` - راهنمای کلی
- `templates/shared/generic/README_GENERIC_LIST.md` - مستندات List
- `templates/shared/generic/README_GENERIC_FORM.md` - مستندات Form
- `templates/shared/generic/README_GENERIC_CONFIRM_DELETE.md` - مستندات Delete
- `templates/shared/generic/README_GENERIC_DETAIL.md` - مستندات Detail
- `templates/shared/generic/README_GENERIC_DASHBOARD.md` - مستندات Dashboard
- `templates/shared/generic/README_GENERIC_ASSIGNMENT.md` - مستندات Assignment
- `templates/shared/generic/README_GENERIC_REPORT.md` - مستندات Report
- `templates/shared/generic/README_GENERIC_TAGS.md` - مستندات Template Tags

---

**آخرین به‌روزرسانی**: 2025-11-30


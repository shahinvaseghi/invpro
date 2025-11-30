# خلاصه Migration Template ها به Generic Templates

این فایل شامل لیست کامل ماژول‌ها و فایل‌هایی است که به generic templates migrate شده‌اند.

---

## ماژول Shared ✅ (100% - 15 template)

### فایل‌های View:
- `shared/views/users.py`
- `shared/views/groups.py`
- `shared/views/access_levels.py`
- `shared/views/companies.py`
- `shared/views/company_units.py`
- `shared/views/smtp_server.py`

### Templates منتقل شده:

#### List Templates (3):
1. `templates/shared/groups_list.html` → extends `shared/generic/generic_list.html`
2. `templates/shared/access_levels_list.html` → extends `shared/generic/generic_list.html`
3. `templates/shared/smtp_server_list.html` → extends `shared/generic/generic_list.html`

#### Form Templates (6):
1. `templates/shared/user_form.html` → extends `shared/generic/generic_form.html`
2. `templates/shared/company_form.html` → extends `shared/generic/generic_form.html`
3. `templates/shared/company_unit_form.html` → extends `shared/generic/generic_form.html`
4. `templates/shared/group_form.html` → extends `shared/generic/generic_form.html`
5. `templates/shared/access_level_form.html` → extends `shared/generic/generic_form.html`
6. `templates/shared/smtp_server_form.html` → extends `shared/generic/generic_form.html`

#### Delete Templates (6):
- همه از `shared/generic/generic_confirm_delete.html` استفاده می‌کنند:
  1. User Delete
  2. Company Delete
  3. Company Unit Delete
  4. Group Delete
  5. Access Level Delete
  6. SMTP Server Delete

---

## ماژول Ticketing ✅ (100% - 9 template)

### فایل‌های View:
- `ticketing/views/categories.py`
- `ticketing/views/subcategories.py`
- `ticketing/views/templates.py`

### Templates منتقل شده:

#### Categories (3):
1. `templates/ticketing/categories_list.html` → extends `shared/generic/generic_list.html`
2. `templates/ticketing/category_form.html` → extends `shared/generic/generic_form.html`
3. Category Delete → `shared/generic/generic_confirm_delete.html`

#### Subcategories (3):
1. `templates/ticketing/subcategories_list.html` → extends `shared/generic/generic_list.html`
2. `templates/ticketing/subcategory_form.html` → extends `shared/generic/generic_form.html`
3. Subcategory Delete → `shared/generic/generic_confirm_delete.html`

#### Templates (3):
1. `templates/ticketing/templates_list.html` → extends `shared/generic/generic_list.html`
2. `templates/ticketing/template_form.html` → extends `shared/generic/generic_form.html`
3. Template Delete → `shared/generic/generic_confirm_delete.html`

---

## ماژول Production ✅ (100% - 23 template)

### فایل‌های View:
- `production/views/bom.py`
- `production/views/machine.py`
- `production/views/performance_record.py`
- `production/views/personnel.py`
- `production/views/process.py`
- `production/views/product_order.py`
- `production/views/transfer_to_line.py`
- `production/views/work_line.py`

### Templates منتقل شده:

#### BOM (3):
1. `templates/production/bom_list.html` → extends `shared/generic/generic_list.html`
2. `templates/production/bom_form.html` → extends `shared/generic/generic_form.html`
3. BOM Delete → `shared/generic/generic_confirm_delete.html`

#### Machine (3):
1. `templates/production/machines.html` → extends `shared/generic/generic_list.html`
2. `templates/production/machine_form.html` → extends `shared/generic/generic_form.html`
3. Machine Delete → `shared/generic/generic_confirm_delete.html`

#### Performance Record (3):
1. `templates/production/performance_record_list.html` → extends `shared/generic/generic_list.html`
2. `templates/production/performance_record_form.html` → extends `shared/generic/generic_form.html`
3. Performance Record Delete → `shared/generic/generic_confirm_delete.html`

#### Personnel (3):
1. `templates/production/personnel.html` → extends `shared/generic/generic_list.html`
2. `templates/production/person_form.html` → extends `shared/generic/generic_form.html`
3. Personnel Delete → `shared/generic/generic_confirm_delete.html`

#### Process (3):
1. `templates/production/processes.html` → extends `shared/generic/generic_list.html`
2. `templates/production/process_form.html` → extends `shared/generic/generic_form.html`
3. Process Delete → `shared/generic/generic_confirm_delete.html`

#### Product Order (3):
1. `templates/production/product_orders.html` → extends `shared/generic/generic_list.html`
2. `templates/production/product_order_form.html` → extends `shared/generic/generic_form.html`
3. Product Order Delete → `shared/generic/generic_confirm_delete.html`

#### Transfer to Line (3):
1. `templates/production/transfer_to_line_list.html` → extends `shared/generic/generic_list.html`
2. `templates/production/transfer_to_line_form.html` → extends `shared/generic/generic_form.html`
3. Transfer to Line Delete → `shared/generic/generic_confirm_delete.html`

#### Work Line (3):
1. `templates/production/work_lines.html` → extends `shared/generic/generic_list.html`
2. `templates/production/work_line_form.html` → extends `shared/generic/generic_form.html`
3. Work Line Delete → `shared/generic/generic_confirm_delete.html`

---

## ماژول Inventory ✅ (100% - 39 template - تمام templates قابل migration)

### فایل‌های View:
- `inventory/views/master_data.py`
- `inventory/views/receipts.py`
- `inventory/views/issues.py`
- `inventory/views/requests.py`
- `inventory/views/stocktaking.py`

### Templates منتقل شده:

#### Master Data (21 template - 100%):

**Item Types (3):**
1. `templates/inventory/item_types.html` → extends `shared/generic/generic_list.html`
2. `templates/inventory/itemtype_form.html` → extends `shared/generic/generic_form.html`
3. Item Type Delete → `shared/generic/generic_confirm_delete.html`

**Item Categories (3):**
1. `templates/inventory/item_categories.html` → extends `shared/generic/generic_list.html`
2. `templates/inventory/itemcategory_form.html` → extends `shared/generic/generic_form.html`
3. Item Category Delete → `shared/generic/generic_confirm_delete.html`

**Item Subcategories (3):**
1. `templates/inventory/item_subcategories.html` → extends `shared/generic/generic_list.html`
2. `templates/inventory/itemsubcategory_form.html` → extends `shared/generic/generic_form.html`
3. Item Subcategory Delete → `shared/generic/generic_confirm_delete.html`

**Items (3):**
1. `templates/inventory/items.html` → extends `shared/generic/generic_list.html`
2. `templates/inventory/item_form.html` → extends `shared/generic/generic_form.html`
3. Item Delete → `shared/generic/generic_confirm_delete.html`

**Warehouses (3):**
1. `templates/inventory/warehouses.html` → extends `shared/generic/generic_list.html`
2. `templates/inventory/warehouse_form.html` → extends `shared/generic/generic_form.html`
3. Warehouse Delete → `shared/generic/generic_confirm_delete.html`

**Suppliers (3):**
1. `templates/inventory/suppliers.html` → extends `shared/generic/generic_list.html`
2. `templates/inventory/supplier_form.html` → extends `shared/generic/generic_form.html`
3. Supplier Delete → `shared/generic/generic_confirm_delete.html`

**Supplier Categories (3):**
1. `templates/inventory/supplier_categories.html` → extends `shared/generic/generic_list.html`
2. `templates/inventory/suppliercategory_form.html` → extends `shared/generic/generic_form.html`
3. Supplier Category Delete → `shared/generic/generic_confirm_delete.html`

#### Receipts (6 template - List & Delete):

**Temporary Receipts (2):**
1. `templates/inventory/receipt_temporary.html` → extends `shared/generic/generic_list.html`
2. Temporary Receipt Delete → `shared/generic/generic_confirm_delete.html`

**Permanent Receipts (2):**
1. `templates/inventory/receipt_permanent.html` → extends `shared/generic/generic_list.html`
2. Permanent Receipt Delete → `shared/generic/generic_confirm_delete.html`

**Consignment Receipts (2):**
1. `templates/inventory/receipt_consignment.html` → extends `shared/generic/generic_list.html`
2. Consignment Receipt Delete → `shared/generic/generic_confirm_delete.html`

#### Issues (6 template - List & Delete):

**Permanent Issues (2):**
1. `templates/inventory/issue_permanent.html` → extends `shared/generic/generic_list.html`
2. Permanent Issue Delete → `shared/generic/generic_confirm_delete.html`

**Consumption Issues (2):**
1. `templates/inventory/issue_consumption.html` → extends `shared/generic/generic_list.html`
2. Consumption Issue Delete → `shared/generic/generic_confirm_delete.html`

**Consignment Issues (2):**
1. `templates/inventory/issue_consignment.html` → extends `shared/generic/generic_list.html`
2. Consignment Issue Delete → `shared/generic/generic_confirm_delete.html`

#### Requests (2 template - List):

**Purchase Requests (1):**
1. `templates/inventory/purchase_requests.html` → extends `shared/generic/generic_list.html`

**Warehouse Requests (1):**
1. `templates/inventory/warehouse_requests.html` → extends `shared/generic/generic_list.html`

#### Stocktaking (6 template - List & Delete):

**Stocktaking Deficit (2):**
1. `templates/inventory/stocktaking_deficit.html` → extends `shared/generic/generic_list.html`
2. Stocktaking Deficit Delete → `shared/generic/generic_confirm_delete.html`

**Stocktaking Surplus (2):**
1. `templates/inventory/stocktaking_surplus.html` → extends `shared/generic/generic_list.html`
2. Stocktaking Surplus Delete → `shared/generic/generic_confirm_delete.html`

**Stocktaking Records (2):**
1. `templates/inventory/stocktaking_records.html` → extends `shared/generic/generic_list.html`
2. Stocktaking Record Delete → `shared/generic/generic_confirm_delete.html`

---

## ماژول QC ✅ (100% - 1 template)

### فایل‌های View:
- `qc/views/inspections.py`

### Templates منتقل شده:

#### List Templates (1):
1. `templates/qc/temporary_receipts.html` → extends `shared/generic/generic_list.html`

---

## آمار کلی Migration

### ✅ تکمیل شده:
- **Shared**: 15 template (100%)
- **Ticketing**: 9 template (100%)
- **Production**: 23 template (100%)
- **Inventory**: 39 template (100% - تمام templates قابل migration) ✅
- **QC**: 1 template (100%)

**جمع کل: 87 template**

### 📋 باقی مانده:
- **Inventory**: 
  - ✅ Form templates که از Mixins استفاده می‌کنند (نیازی به migration ندارند - از shared templates استفاده می‌کنند)
  - ✅ Special Pages (Balance, Detail, Serial Assignment, Import) - صفحات خاص با ساختار منحصر به فرد که نیاز به migration ندارند
- **QC**: 
  - ✅ Special Pages (Line Selection, Rejection Management) - صفحات خاص با ساختار منحصر به فرد که نیاز به migration ندارند

---

## Generic Templates استفاده شده:

1. **`templates/shared/generic/generic_list.html`**
   - برای تمام List views
   - Blocks قابل override: `page_title`, `breadcrumb_extra`, `page_actions`, `filter_fields`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`, `pagination`

2. **`templates/shared/generic/generic_form.html`**
   - برای تمام Form views (Create & Update)
   - Blocks قابل override: `breadcrumb_extra`, `before_form`, `form_sections`, `form_extra`, `extra_styles`, `form_scripts`, `form_actions_extra`

3. **`templates/shared/generic/generic_confirm_delete.html`**
   - برای تمام Delete views
   - Context variables مورد نیاز: `delete_title`, `confirmation_message`, `object_details`, `cancel_url`, `breadcrumbs`

---

## تغییرات کلیدی در Views:

### Context Variables مشترک:
- `page_title`: عنوان صفحه
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `object_list`: برای List views (به جای نام‌های اختصاصی)
- `form_title`: عنوان فرم
- `delete_title`: عنوان صفحه حذف
- `confirmation_message`: پیام تایید
- `object_details`: جزئیات object برای delete
- `cancel_url`: URL برای cancel
- `create_url`, `edit_url_name`, `delete_url_name`, `lock_url_name`: URL names برای actions

### Context Object Name:
- همه List views: از نام اختصاصی به `'object_list'` تغییر یافت

---

**آخرین به‌روزرسانی:** 
- ✅ تمام List و Delete templates migrate شدند
- ✅ Form templates از Mixins استفاده می‌کنند
- ✅ ماژول Inventory 100% تکمیل شد (تمام templates قابل migration migrate شدند)
- ✅ ماژول QC 100% تکمیل شد


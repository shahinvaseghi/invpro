# inventory/views/ - Views Documentation

این پوشه شامل تمام views ماژول inventory است.

## فایل‌ها

### base.py
- **README**: [README_BASE.md](README_BASE.md)
- **توضیح**: کلاس‌های پایه و mixin‌های قابل استفاده مجدد

### api.py
- **README**: [README_API.md](README_API.md)
- **توضیح**: JSON API endpoints برای تعاملات دینامیک

### master_data.py
- **README**: [README_MASTER_DATA.md](README_MASTER_DATA.md)
- **توضیح**: CRUD views برای داده‌های اصلی (Item Types, Categories, Items, Warehouses, Suppliers)

### receipts.py
- **README**: [README_RECEIPTS.md](README_RECEIPTS.md)
- **توضیح**: Views برای مدیریت رسیدها (Temporary, Permanent, Consignment)

### issues.py
- **README**: [README_ISSUES.md](README_ISSUES.md)
- **توضیح**: Views برای مدیریت حواله‌ها (Permanent, Consumption, Consignment)

### requests.py
- **README**: [README_REQUESTS.md](README_REQUESTS.md)
- **توضیح**: Views برای مدیریت درخواست‌ها (Purchase Requests, Warehouse Requests)

### stocktaking.py
- **README**: [README_STOCKTAKING.md](README_STOCKTAKING.md)
- **توضیح**: Views برای مدیریت شمارش انبار (Deficit, Surplus, Record)

### balance.py
- **README**: [README_BALANCE.md](README_BALANCE.md)
- **توضیح**: Views برای محاسبه و نمایش موجودی انبار

### item_import.py
- **README**: [README_ITEM_IMPORT.md](README_ITEM_IMPORT.md)
- **توضیح**: Views برای import کالاها از Excel

### create_issue_from_warehouse_request.py
- **README**: [README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md](README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md)
- **توضیح**: Views برای ایجاد حواله از درخواست انبار (صفحه انتخاب)

### issues_from_warehouse_request.py
- **README**: [README_ISSUES_FROM_WAREHOUSE_REQUEST.md](README_ISSUES_FROM_WAREHOUSE_REQUEST.md)
- **توضیح**: Views برای ایجاد مستقیم حواله از درخواست انبار

---

## الگوهای مشترک

تمام views از الگوهای مشترک زیر پیروی می‌کنند:

1. **Base Class**: از `InventoryBaseView` استفاده می‌کنند
2. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
3. **Lock Protection**: Update/Delete views از `DocumentLockProtectedMixin` استفاده می‌کنند
4. **Permission Checking**: از `FeaturePermissionRequiredMixin` برای بررسی مجوزها استفاده می‌کنند
5. **Multi-line Support**: Views با formset از `LineFormsetMixin` استفاده می‌کنند
6. **Generic Templates**: List و Delete views از `shared/generic/generic_list.html` و `shared/generic/generic_confirm_delete.html` استفاده می‌کنند

---

## Template Migration Status

### ✅ تکمیل شده (39 templates):
- **Master Data**: 21 template (List, Form, Delete برای Item Types, Categories, Subcategories, Warehouses, Suppliers, Supplier Categories, Items)
- **Receipts**: 6 template (List & Delete برای Temporary, Permanent, Consignment Receipts)
- **Issues**: 6 template (List & Delete برای Permanent, Consumption, Consignment Issues)
- **Requests**: 2 template (List برای Purchase Requests, Warehouse Requests)
- **Stocktaking**: 6 template (List & Delete برای Deficit, Surplus, Records)

### 📋 باقی‌مانده (نیازی به migration ندارند):
- **Form Templates**: Form templates که از Mixins استفاده می‌کنند (`ReceiptFormMixin`, `PurchaseRequestFormMixin`, `WarehouseRequestFormMixin`, `StocktakingFormMixin`) - این‌ها از `receipt_form.html` یا template های خاص استفاده می‌کنند که از shared templates استفاده می‌کنند
- **Special Pages**: صفحات خاص با ساختار منحصر به فرد:
  - Detail Views (`receipt_detail.html`, `issue_detail.html`)
  - Balance Views (`inventory_balance.html`, `inventory_balance_details.html`)
  - Serial Assignment (`receipt_serial_assignment.html`, `issue_serial_assignment.html`)
  - Import (`item_import_result.html`)
  - Create from Request (`create_receipt_from_purchase_request.html`, `create_issue_from_warehouse_request.html`)
  - Item Serials (`item_serials.html`)

**برای جزئیات کامل migration، به [`docs/TEMPLATE_MIGRATION_CHECKLIST_INVENTORY.md`](../../docs/TEMPLATE_MIGRATION_CHECKLIST_INVENTORY.md) مراجعه کنید.**

---

## مستندات کامل

برای جزئیات کامل هر فایل، به README مربوطه مراجعه کنید.


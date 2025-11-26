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

---

## مستندات کامل

برای جزئیات کامل هر فایل، به README مربوطه مراجعه کنید.


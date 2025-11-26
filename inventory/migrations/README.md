# inventory/migrations/ - Migrations Documentation

این پوشه شامل تمام migration files ماژول inventory است.

## خلاصه Migrations

### Initial Migrations
- `0001_initial.py`: ایجاد ساختار اولیه دیتابیس
- `0002_warehouserequest_and_more.py`: اضافه کردن WarehouseRequest و سایر مدل‌ها

### Code and Structure Updates
- `0003_item_full_item_code_alter_item_item_code.py`: اضافه کردن full_item_code
- `0004_remove_issueconsignment_activated_at_and_more.py`: حذف فیلدهای activated_at/updated_at
- `0005_issueconsignment_department_unit_and_more.py`: اضافه کردن department_unit
- `0006_issueconsignment_created_by_and_more.py`: اضافه کردن created_by

### Stocktaking
- `0014_stocktaking_created_updated_by.py`: اضافه کردن created_by/updated_by به stocktaking
- `0020_change_stocktaking_users.py`: تغییر فیلدهای کاربر در stocktaking

### Purchase Requests
- `0015_purchaserequest_is_locked_and_more.py`: اضافه کردن is_locked
- `0022_alter_purchaserequest_approver_and_more.py`: تغییر approver
- `0029_add_purchase_request_line.py`: اضافه کردن PurchaseRequestLine
- `0030_migrate_purchase_request_to_lines.py`: تبدیل PurchaseRequest به multi-line

### Serial Tracking
- `0016_itemserial_remove_issueconsignment_updated_at_and_more.py`: اضافه کردن ItemSerial
- `0025_add_secondary_batch_and_serial_numbers.py`: اضافه کردن secondary serial/batch

### Receipts
- `0017_remove_issueconsignment_consignment_receipt_and_more.py`: تغییرات در consignment
- `0018_add_entered_price_unit.py`: اضافه کردن entered_price و entered_unit
- `0019_make_consignment_receipt_optional.py`: اختیاری کردن consignment_receipt
- `0031_add_receipt_temporary_line.py`: اضافه کردن ReceiptTemporaryLine
- `0032_add_notes_to_receipt_temporary.py`: اضافه کردن notes

### Production Integration
- `0026_add_personnel_machines_to_workline.py`: اضافه کردن personnel/machines
- `0027_move_workline_to_production.py`: انتقال WorkLine به ماژول production
- `0028_move_workline_to_production.py`: (duplicate)

---

## نکات مهم

1. **Migration Order**: Migrations باید به ترتیب اجرا شوند
2. **Data Migrations**: برخی migrations شامل data migration هستند
3. **Backward Compatibility**: تمام migrations backward compatible هستند

---

## مستندات کامل

برای جزئیات کامل هر migration، به فایل مربوطه مراجعه کنید.


# qc/migrations/ - Migrations Documentation

این پوشه شامل تمام migration files ماژول QC است.

## خلاصه Migrations

### Initial Migrations
- `0001_initial.py`: ایجاد ساختار اولیه دیتابیس

### Cleanup
- `0002_remove_receiptinspection_activated_at_and_more.py`: حذف فیلدهای activated_at/updated_at
- `0003_remove_receiptinspection_updated_at_and_more.py`: حذف updated_at

### Approval
- `0004_alter_receiptinspection_approved_by_and_more.py`: تغییر approved_by
- `0005_change_receipt_inspection_approved_by_to_user.py`: تبدیل approved_by به User

---

## نکات مهم

1. **Simple Structure**: ماژول QC ساختار ساده‌ای دارد
2. **Approval Workflow**: Approval workflow اضافه شده است

---

## مستندات کامل

برای جزئیات کامل هر migration، به فایل مربوطه مراجعه کنید.


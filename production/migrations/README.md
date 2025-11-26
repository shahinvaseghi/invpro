# production/migrations/ - Migrations Documentation

این پوشه شامل تمام migration files ماژول production است.

## خلاصه Migrations

### Initial Migrations
- `0001_initial.py`: ایجاد ساختار اولیه دیتابیس

### Code Updates
- `0002_alter_workcenter_public_code.py`: تغییر public_code در WorkCenter

### BOM Restructuring
- `0003_remove_bommaterial_activated_at_and_more.py`: حذف فیلدهای activated_at/updated_at
- `0004_remove_bommaterial_updated_at_and_more.py`: حذف updated_at
- `0006_bom_restructure.py`: بازسازی ساختار BOM
- `0007_bom_company_code_bom_disabled_at_bom_disabled_by_and_more.py`: اضافه کردن company_code و disabled fields
- `0008_alter_bommaterial_material_type.py`: تغییر material_type
- `0009_bom_material_type_to_fk.py`: تبدیل material_type به ForeignKey
- `0010_bom_unit_to_fk.py`: تبدیل unit به ForeignKey
- `0011_bom_unit_back_to_char.py`: برگشت unit به CharField

### Process Updates
- `0014_update_process_model.py`: به‌روزرسانی مدل Process
- `0015_remove_effective_dates_from_process.py`: حذف effective dates
- `0016_remove_effective_dates_from_process.py`: (duplicate)
- `0017_fix_process_revision_constraint.py`: رفع constraint revision
- `0018_change_process_approved_by_to_user.py`: تغییر approved_by به User

### Product Orders
- `0019_add_bom_and_approved_by_to_product_order.py`: اضافه کردن BOM و approved_by

### Transfer to Line
- `0020_update_transfer_to_line_model.py`: به‌روزرسانی مدل TransferToLine

### Performance Records
- `0021_performancerecord_performancerecordperson_and_more.py`: اضافه کردن PerformanceRecord و PerformanceRecordPerson

### WorkLine Migration
- `0013_move_workline_to_production.py`: انتقال WorkLine از inventory به production

---

## نکات مهم

1. **BOM Evolution**: BOM چندین بار بازسازی شده است
2. **Process Changes**: Process model چندین بار به‌روزرسانی شده است
3. **WorkLine Migration**: WorkLine از ماژول inventory به production منتقل شده است

---

## مستندات کامل

برای جزئیات کامل هر migration، به فایل مربوطه مراجعه کنید.


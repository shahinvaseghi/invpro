# Database Migrations - Overview

**هدف**: مستندسازی تمام migration files در پروژه

این فایل شامل لیست کامل تمام migration files در تمام ماژول‌های پروژه است. هر migration file تغییرات schema دیتابیس را در یک نسخه خاص از پروژه نشان می‌دهد.

---

## ماژول‌ها

- **Inventory**: 33 migration files
- **Production**: 21 migration files
- **QC**: 5 migration files
- **Ticketing**: 2 migration files
- **Shared**: 12 migration files
- **UI**: 0 migration files (فقط `__init__.py`)

**جمع کل**: 73 migration files (بدون `__init__.py`)

---

## Inventory Module Migrations

### `0001_initial.py`
**هدف**: ایجاد schema اولیه برای ماژول Inventory

**Models ایجاد شده**:
- ItemType, ItemCategory, ItemSubcategory
- Item, Warehouse, Supplier, SupplierCategory
- ReceiptTemporary, ReceiptPermanent, ReceiptConsignment
- IssuePermanent, IssueConsumption, IssueConsignment
- StocktakingDeficit, StocktakingSurplus, StocktakingRecord
- PurchaseRequest, WarehouseRequest
- ItemSerial, ItemSerialHistory

---

### `0002_warehouserequest_and_more.py`
**هدف**: اضافه کردن WarehouseRequest و تغییرات مرتبط

**تغییرات**:
- ایجاد مدل `WarehouseRequest`
- اضافه کردن فیلدهای مرتبط

---

### `0003_item_full_item_code_alter_item_item_code.py`
**هدف**: اضافه کردن `full_item_code` به Item و تغییر `item_code`

**تغییرات**:
- اضافه کردن فیلد `full_item_code` به `Item`
- تغییر `item_code` (احتمالاً از CharField به ...)

---

### `0004_remove_issueconsignment_activated_at_and_more.py`
**هدف**: حذف فیلدهای `activated_at` و `activated_by` از IssueConsignment

**تغییرات**:
- حذف `activated_at` و `activated_by` از `IssueConsignment`

---

### `0005_issueconsignment_department_unit_and_more.py`
**هدف**: اضافه کردن `department_unit` به IssueConsignment

**تغییرات**:
- اضافه کردن ForeignKey `department_unit` به `IssueConsignment`

---

### `0006_issueconsignment_created_by_and_more.py`
**هدف**: اضافه کردن فیلدهای `created_by` و `edited_by` به IssueConsignment

**تغییرات**:
- اضافه کردن `created_by` و `edited_by` به `IssueConsignment`

---

### `0014_stocktaking_created_updated_by.py`
**هدف**: اضافه کردن فیلدهای `created_by` و `updated_by` به Stocktaking models

**تغییرات**:
- اضافه کردن `created_by` و `updated_by` به StocktakingDeficit, StocktakingSurplus, StocktakingRecord

---

### `0015_purchaserequest_is_locked_and_more.py`
**هدف**: اضافه کردن `is_locked` به PurchaseRequest

**تغییرات**:
- اضافه کردن فیلد `is_locked` به `PurchaseRequest`

---

### `0016_itemserial_remove_issueconsignment_updated_at_and_more.py`
**هدف**: حذف `updated_at` از IssueConsignment و تغییرات در ItemSerial

**تغییرات**:
- حذف `updated_at` از `IssueConsignment`
- تغییرات در `ItemSerial`

---

### `0017_remove_issueconsignment_consignment_receipt_and_more.py`
**هدف**: حذف `consignment_receipt` از IssueConsignment

**تغییرات**:
- حذف ForeignKey `consignment_receipt` از `IssueConsignment`

---

### `0018_add_entered_price_unit.py`
**هدف**: اضافه کردن `entered_price` و `entered_unit` به receipt lines

**تغییرات**:
- اضافه کردن `entered_price` و `entered_unit` به receipt line models

---

### `0019_make_consignment_receipt_optional.py`
**هدف**: اختیاری کردن `consignment_receipt` در IssueConsignment

**تغییرات**:
- تغییر `consignment_receipt` به `null=True, blank=True`

---

### `0020_change_stocktaking_users.py`
**هدف**: تغییر فیلدهای user در Stocktaking models

**تغییرات**:
- تغییر `created_by` و `updated_by` به `created_by` و `edited_by`

---

### `0021_alter_receiptpermanent_options_and_more.py`
**هدف**: تغییر options و فیلدهای ReceiptPermanent

**تغییرات**:
- تغییر Meta options در `ReceiptPermanent`
- تغییرات در فیلدهای مرتبط

---

### `0022_alter_purchaserequest_approver_and_more.py`
**هدف**: تغییر `approver` در PurchaseRequest

**تغییرات**:
- تغییر `approver` از ... به User ForeignKey

---

### `0023_remove_person_from_inventory.py`
**هدف**: حذف Person از ماژول Inventory (انتقال به Production)

**تغییرات**:
- حذف مدل `Person` از inventory
- انتقال به production module

---

### `0024_add_warehouse_request_to_issue_permanent.py`
**هدف**: اضافه کردن `warehouse_request` به IssuePermanent

**تغییرات**:
- اضافه کردن ForeignKey `warehouse_request` به `IssuePermanent`

---

### `0025_add_secondary_batch_and_serial_numbers.py`
**هدف**: اضافه کردن فیلدهای batch و serial number ثانویه

**تغییرات**:
- اضافه کردن `secondary_batch_number` و `secondary_serial_number` به receipt lines

---

### `0026_add_personnel_machines_to_workline.py`
**هدف**: اضافه کردن personnel و machines به WorkLine

**تغییرات**:
- اضافه کردن ManyToMany `personnel` و `machines` به `WorkLine`

---

### `0027_move_workline_to_production.py`
**هدف**: انتقال WorkLine از Inventory به Production (قسمت اول)

**تغییرات**:
- شروع انتقال `WorkLine` به production module

---

### `0028_move_workline_to_production.py`
**هدف**: انتقال WorkLine از Inventory به Production (قسمت دوم)

**تغییرات**:
- تکمیل انتقال `WorkLine` به production module

---

### `0029_add_purchase_request_line.py`
**هدف**: اضافه کردن مدل PurchaseRequestLine برای multi-line support

**تغییرات**:
- ایجاد مدل `PurchaseRequestLine`
- اضافه کردن ForeignKey به `PurchaseRequest`

---

### `0030_migrate_purchase_request_to_lines.py`
**هدف**: Migrate داده‌های موجود PurchaseRequest به PurchaseRequestLine

**تغییرات**:
- Data migration برای تبدیل receipt های تک‌خطی به چندخطی
- ایجاد `PurchaseRequestLine` records از داده‌های موجود

---

### `0031_add_receipt_temporary_line.py`
**هدف**: اضافه کردن مدل ReceiptTemporaryLine برای multi-line support

**تغییرات**:
- ایجاد مدل `ReceiptTemporaryLine`
- اضافه کردن ForeignKey به `ReceiptTemporary`

---

### `0032_add_notes_to_receipt_temporary.py`
**هدف**: اضافه کردن فیلد `notes` به ReceiptTemporary

**تغییرات**:
- اضافه کردن `notes` (TextField) به `ReceiptTemporary`

---

### `0033_add_warehouse_request_line.py`
**هدف**: اضافه کردن مدل WarehouseRequestLine برای multi-line support

**تغییرات**:
- ایجاد مدل `WarehouseRequestLine`
- حذف فیلدهای تک‌خطی از `WarehouseRequest` (item, quantity, etc.)
- اضافه کردن ForeignKey به `WarehouseRequest`

---

## Production Module Migrations

### `0001_initial.py`
**هدف**: ایجاد schema اولیه برای ماژول Production

**Models ایجاد شده**:
- BOM, BOMMaterial
- Process, ProcessStep
- WorkCenter, WorkLine
- ProductOrder
- TransferToLine
- PerformanceRecord

---

### `0002_alter_workcenter_public_code.py`
**هدف**: تغییر `public_code` در WorkCenter

**تغییرات**:
- تغییر `public_code` (احتمالاً از CharField به ...)

---

### `0003_remove_bommaterial_activated_at_and_more.py`
**هدف**: حذف فیلدهای `activated_at` و `activated_by` از BOMMaterial

**تغییرات**:
- حذف `activated_at` و `activated_by` از `BOMMaterial`

---

### `0004_remove_bommaterial_updated_at_and_more.py`
**هدف**: حذف `updated_at` از BOMMaterial

**تغییرات**:
- حذف `updated_at` از `BOMMaterial`

---

### `0005_person_processstep_machine_code_personassignment_and_more.py`
**هدف**: اضافه کردن Person, ProcessStep, Machine, PersonAssignment

**تغییرات**:
- ایجاد مدل `Person` (از inventory منتقل شده)
- ایجاد مدل `ProcessStep`
- ایجاد مدل `Machine`
- ایجاد مدل `PersonAssignment`

---

### `0006_bom_restructure.py`
**هدف**: بازسازی ساختار BOM

**تغییرات**:
- تغییرات عمده در ساختار `BOM` و `BOMMaterial`

---

### `0007_bom_company_code_bom_disabled_at_bom_disabled_by_and_more.py`
**هدف**: اضافه کردن فیلدهای company, code, disabled_at, disabled_by به BOM

**تغییرات**:
- اضافه کردن `company` ForeignKey
- اضافه کردن `bom_code`
- اضافه کردن `disabled_at` و `disabled_by`

---

### `0008_alter_bommaterial_material_type.py`
**هدف**: تغییر `material_type` در BOMMaterial

**تغییرات**:
- تغییر `material_type` (احتمالاً از CharField به ...)

---

### `0009_bom_material_type_to_fk.py`
**هدف**: تبدیل `material_type` به ForeignKey

**تغییرات**:
- تبدیل `material_type` از CharField به ForeignKey

---

### `0010_bom_unit_to_fk.py`
**هدف**: تبدیل `unit` به ForeignKey

**تغییرات**:
- تبدیل `unit` از CharField به ForeignKey

---

### `0011_bom_unit_back_to_char.py`
**هدف**: برگرداندن `unit` به CharField

**تغییرات**:
- برگرداندن `unit` از ForeignKey به CharField

---

### `0012_bom_remove_dates.py`
**هدف**: حذف فیلدهای تاریخ از BOM

**تغییرات**:
- حذف فیلدهای تاریخ (مثل `effective_from`, `effective_to`)

---

### `0013_move_workline_to_production.py`
**هدف**: تکمیل انتقال WorkLine از Inventory به Production

**تغییرات**:
- تکمیل انتقال `WorkLine` به production module

---

### `0014_update_process_model.py`
**هدف**: به‌روزرسانی مدل Process

**تغییرات**:
- تغییرات در ساختار `Process`

---

### `0015_remove_effective_dates_from_process.py`
**هدف**: حذف فیلدهای `effective_from` و `effective_to` از Process (قسمت اول)

**تغییرات**:
- شروع حذف فیلدهای تاریخ از `Process`

---

### `0016_remove_effective_dates_from_process.py`
**هدف**: حذف فیلدهای `effective_from` و `effective_to` از Process (قسمت دوم)

**تغییرات**:
- تکمیل حذف فیلدهای تاریخ از `Process`

---

### `0017_fix_process_revision_constraint.py`
**هدف**: اصلاح constraint مربوط به revision در Process

**تغییرات**:
- اصلاح unique constraint برای `revision`

---

### `0018_change_process_approved_by_to_user.py`
**هدف**: تغییر `approved_by` از ... به User ForeignKey

**تغییرات**:
- تغییر `approved_by` به User ForeignKey

---

### `0019_add_bom_and_approved_by_to_product_order.py`
**هدف**: اضافه کردن `bom` و `approved_by` به ProductOrder

**تغییرات**:
- اضافه کردن ForeignKey `bom` به `ProductOrder`
- اضافه کردن ForeignKey `approved_by` به `ProductOrder`

---

### `0020_update_transfer_to_line_model.py`
**هدف**: به‌روزرسانی مدل TransferToLine

**تغییرات**:
- تغییرات در ساختار `TransferToLine`

---

### `0021_performancerecord_performancerecordperson_and_more.py`
**هدف**: اضافه کردن PerformanceRecordPerson و تغییرات در PerformanceRecord

**تغییرات**:
- ایجاد مدل `PerformanceRecordPerson`
- تغییرات در `PerformanceRecord`

---

## QC Module Migrations

### `0001_initial.py`
**هدف**: ایجاد schema اولیه برای ماژول QC

**Models ایجاد شده**:
- ReceiptInspection

---

### `0002_remove_receiptinspection_activated_at_and_more.py`
**هدف**: حذف فیلدهای `activated_at` و `activated_by` از ReceiptInspection

**تغییرات**:
- حذف `activated_at` و `activated_by` از `ReceiptInspection`

---

### `0003_remove_receiptinspection_updated_at_and_more.py`
**هدف**: حذف `updated_at` از ReceiptInspection

**تغییرات**:
- حذف `updated_at` از `ReceiptInspection`

---

### `0004_alter_receiptinspection_approved_by_and_more.py`
**هدف**: تغییر `approved_by` در ReceiptInspection

**تغییرات**:
- تغییر `approved_by` (احتمالاً از ... به User)

---

### `0005_change_receipt_inspection_approved_by_to_user.py`
**هدف**: تغییر `approved_by` به User ForeignKey

**تغییرات**:
- تغییر `approved_by` به User ForeignKey

---

## Ticketing Module Migrations

### `0001_initial.py`
**هدف**: ایجاد schema اولیه برای ماژول Ticketing

**Models ایجاد شده**:
- TicketCategory, TicketSubcategory
- TicketTemplate, TicketTemplateField, TicketTemplatePermission
- Ticket, TicketComment, TicketAttachment
- TicketEvent

---

### `0002_add_template_events.py`
**هدف**: اضافه کردن Template Events

**تغییرات**:
- اضافه کردن مدل‌های مرتبط با Template Events

---

## Shared Module Migrations

### `0001_initial.py`
**هدف**: ایجاد schema اولیه برای ماژول Shared

**Models ایجاد شده**:
- Company, CompanyUnit
- User, UserCompanyAccess
- Group, GroupProfile
- AccessLevel, AccessLevelPermission
- Feature, FeaturePermission

---

### `0002_user_default_company.py`
**هدف**: اضافه کردن `default_company` به User

**تغییرات**:
- اضافه کردن ForeignKey `default_company` به `User`

---

### `0003_alter_company_public_code.py`
**هدف**: تغییر `public_code` در Company

**تغییرات**:
- تغییر `public_code` (احتمالاً از CharField به ...)

---

### `0004_alter_companyunit_public_code.py`
**هدف**: تغییر `public_code` در CompanyUnit

**تغییرات**:
- تغییر `public_code` (احتمالاً از CharField به ...)

---

### `0005_remove_accesslevel_activated_at_and_more.py`
**هدف**: حذف فیلدهای `activated_at` و `activated_by` از AccessLevel

**تغییرات**:
- حذف `activated_at` و `activated_by` از `AccessLevel`

---

### `0006_person_company_units.py`
**هدف**: اضافه کردن `company_units` به Person

**تغییرات**:
- اضافه کردن ManyToMany `company_units` به `Person`

---

### `0007_groupprofile.py`
**هدف**: ایجاد مدل GroupProfile

**تغییرات**:
- ایجاد مدل `GroupProfile` برای ارتباط با Django Group

---

### `0008_5_migrate_person_data.py`
**هدف**: Migrate داده‌های Person از Inventory به Production

**تغییرات**:
- Data migration برای انتقال Person records

---

### `0008_remove_accesslevel_updated_at_and_more.py`
**هدف**: حذف `updated_at` از AccessLevel

**تغییرات**:
- حذف `updated_at` از `AccessLevel`

---

### `0009_remove_personassignment_company_and_more.py`
**هدف**: حذف `company` از PersonAssignment

**تغییرات**:
- حذف ForeignKey `company` از `PersonAssignment`

---

### `0010_smtpserver.py`
**هدف**: ایجاد مدل SMTPServer

**تغییرات**:
- ایجاد مدل `SMTPServer` برای تنظیمات SMTP

---

### `0011_add_section_and_action_registry.py`
**هدف**: اضافه کردن Section و Action Registry

**تغییرات**:
- ایجاد مدل‌های `Section` و `Action` برای registry

---

### `0012_populate_section_and_action_registry.py`
**هدف**: Populate کردن Section و Action Registry با داده‌های اولیه

**تغییرات**:
- Data migration برای پر کردن registry با sections و actions

---

## UI Module Migrations

**نکته**: ماژول UI هیچ migration file ندارد (فقط `__init__.py`). این ماژول فقط برای templates و static files است و model ندارد.

---

## نکات مهم

1. **Migration Order**: Migrations باید به ترتیب شماره اجرا شوند
2. **Dependencies**: برخی migrations به migrations دیگر وابسته هستند
3. **Data Migrations**: برخی migrations (مثل `0030_migrate_purchase_request_to_lines`) data migration هستند
4. **Backward Compatibility**: برخی migrations (مثل `0010_bom_unit_to_fk` و `0011_bom_unit_back_to_char`) تغییرات را برگردانده‌اند
5. **Model Moves**: برخی migrations (مثل `0027`, `0028`, `0013`) مدل‌ها را بین ماژول‌ها منتقل کرده‌اند

---

## اجرای Migrations

### برای اولین بار
```bash
python manage.py migrate
```

### برای یک ماژول خاص
```bash
python manage.py migrate inventory
python manage.py migrate production
python manage.py migrate qc
python manage.py migrate ticketing
python manage.py migrate shared
```

### Rollback
```bash
python manage.py migrate inventory 0029  # Rollback به migration 0029
```

---

## ساخت Migration جدید

```bash
# بعد از تغییر models
python manage.py makemigrations inventory
python manage.py makemigrations production
# ...

# برای نام‌گذاری migration
python manage.py makemigrations inventory --name add_new_field
```

---

## Troubleshooting

### Migration Conflicts
اگر migration conflicts دارید:
1. `python manage.py makemigrations --merge`
2. یا migration را manually merge کنید

### Migration Errors
اگر migration خطا بدهد:
1. بررسی کنید که database schema با models هماهنگ است
2. بررسی کنید که dependencies درست هستند
3. ممکن است نیاز به manual fix داشته باشید

---

## آخرین به‌روزرسانی

**تاریخ**: 26 نوامبر 2024
**آخرین Migration**: `inventory/0033_add_warehouse_request_line.py`


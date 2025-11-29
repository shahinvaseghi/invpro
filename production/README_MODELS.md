# production/models.py - Production Models (Complete Documentation)

**هدف**: تمام model classes برای ماژول production

این فایل شامل 21 model class است که به دسته‌های زیر تقسیم می‌شوند:
- Base Models (Abstract)
- Core Resources (Work Centers, Work Lines, Machines)
- Personnel Management
- Bill of Materials (BOM)
- Process Definitions
- Production Orders
- Material Transfer
- Performance Records

---

## وابستگی‌ها

- `shared.models`: `ActivatableModel`, `CompanyScopedModel`, `EditableModel`, `LockableModel`, `MetadataModel`, `SortableModel`, `TimeStampedModel`, `CompanyUnit`, `NUMERIC_CODE_VALIDATOR`, `ENABLED_FLAG_CHOICES`
- `inventory.utils.codes`: `generate_sequential_code`
- `inventory.models`: `Warehouse` (optional dependency)
- `django.db.models`
- `django.core.validators`: `MinValueValidator`, `RegexValidator`
- `django.utils.timezone`
- `decimal.Decimal`

---

## Validators

### `POSITIVE_DECIMAL`
- `MinValueValidator(Decimal("0"))`: مقادیر مثبت یا صفر

---

## Base Models (Abstract)

### `ProductionBaseModel`
**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `MetadataModel`, `EditableModel`

**توضیح**: Base model برای تمام production models

**Fields** (از mixins):
- `company` (ForeignKey): Company scope
- `created_at`, `updated_at` (DateTime): Timestamps
- `is_enabled` (IntegerField): Activation flag
- `created_by`, `updated_by` (ForeignKey): Metadata
- `editing_by`, `editing_started_at`, `editing_session_key` (از EditableModel): Edit lock fields

---

### `ProductionSortableModel`
**Inheritance**: `ProductionBaseModel`, `SortableModel`

**توضیح**: Base model با sort_order

**Fields** (اضافی):
- `sort_order` (IntegerField): ترتیب نمایش

---

## Core Resources Models

### `WorkCenter`
**Inheritance**: `ProductionSortableModel`

**Fields**:
- `public_code` (CharField, max_length=5, validators=[NUMERIC_CODE_VALIDATOR]): کد عمومی (5 رقم)
- `name` (CharField, max_length=180): نام
- `name_en` (CharField, max_length=180, blank=True): نام انگلیسی
- `description` (CharField, max_length=255, blank=True): توضیحات
- `notes` (TextField, blank=True): یادداشت‌ها

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, name)`

**Ordering**: `("company", "sort_order", "public_code")`

---

### `WorkLine`
**Inheritance**: `ProductionSortableModel`

**Fields**:
- `public_code` (CharField, max_length=5): کد عمومی (5 رقم)
- `warehouse` (ForeignKey → Warehouse, null=True, blank=True): انبار (اختیاری - فقط اگر inventory module نصب باشد)
- `name` (CharField, max_length=150): نام
- `name_en` (CharField, max_length=150): نام انگلیسی
- `description` (CharField, max_length=255, blank=True): توضیحات
- `notes` (TextField, blank=True): یادداشت‌ها
- `personnel` (ManyToMany → Person): پرسنل اختصاص داده شده
- `machines` (ManyToMany → Machine): ماشین‌های اختصاص داده شده

**Constraints**:
- Unique: `(company, warehouse, public_code)` (اگر warehouse موجود باشد)
- Unique: `(company, public_code)` (اگر warehouse موجود نباشد)
- Unique: `(company, warehouse, name)` (اگر warehouse موجود باشد)
- Unique: `(company, name)` (اگر warehouse موجود نباشد)

**Methods**:
- `save()`: Auto-generate `public_code` (width=5) if not set

**نکات مهم**:
- می‌تواند با warehouse مرتبط باشد (اختیاری)
- در production module و inventory module (برای consumption issues) استفاده می‌شود

---

### `Machine`
**Inheritance**: `ProductionSortableModel`

**Fields**:
- `public_code` (CharField, max_length=10, editable=False): کد عمومی (10 رقم)
- `name` (CharField, max_length=180): نام
- `name_en` (CharField, max_length=180, blank=True): نام انگلیسی
- `machine_type` (CharField, max_length=30): نوع ماشین
- `work_center` (ForeignKey → WorkCenter, null=True, blank=True): مرکز کاری
- `work_center_code` (CharField, max_length=5, blank=True): کد مرکز کاری (cache)
- `manufacturer` (CharField, max_length=120, blank=True): سازنده
- `model_number` (CharField, max_length=60, blank=True): شماره مدل
- `serial_number` (CharField, max_length=60, unique=True, null=True, blank=True): شماره سریال
- `purchase_date` (DateField, null=True, blank=True): تاریخ خرید
- `installation_date` (DateField, null=True, blank=True): تاریخ نصب
- `capacity_specs` (JSONField, default=dict): مشخصات ظرفیت
- `maintenance_schedule` (JSONField, default=dict): برنامه نگهداری
- `last_maintenance_date` (DateField, null=True, blank=True): آخرین تاریخ نگهداری
- `next_maintenance_date` (DateField, null=True, blank=True): تاریخ نگهداری بعدی
- `status` (CharField): وضعیت (operational, maintenance, idle, broken, retired)
- `description` (CharField, max_length=255, blank=True): توضیحات
- `notes` (TextField, blank=True): یادداشت‌ها

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, name)`

**Methods**:
- `save()`: Auto-generate `public_code` (width=10) if not set, cache `work_center_code`

---

## Personnel Management Models

### `Person`
**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `SortableModel`, `MetadataModel`, `EditableModel`

**Fields**:
- `public_code` (CharField, max_length=8, editable=False): کد عمومی (8 رقم)
- `username` (CharField, max_length=150): نام کاربری
- `first_name` (CharField, max_length=120): نام
- `last_name` (CharField, max_length=120): نام خانوادگی
- `first_name_en` (CharField, max_length=120, blank=True): نام انگلیسی
- `last_name_en` (CharField, max_length=120, blank=True): نام خانوادگی انگلیسی
- `national_id` (CharField, max_length=20, unique=True, null=True, blank=True): کد ملی
- `personnel_code` (CharField, max_length=30, unique=True, null=True, blank=True): کد پرسنلی
- `email` (EmailField, unique=True, null=True, blank=True): ایمیل
- `phone_number` (CharField, max_length=30, blank=True): شماره تلفن
- `mobile_number` (CharField, max_length=30, blank=True): شماره موبایل
- `description` (CharField, max_length=255, blank=True): توضیحات
- `notes` (TextField, blank=True): یادداشت‌ها
- `user` (OneToOneField → User, null=True, blank=True): کاربر مرتبط
- `company_units` (ManyToMany → CompanyUnit): واحدهای سازمانی (چند واحد)

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, username)`

**Methods**:
- `save()`: Auto-generate `public_code` (width=8) if not set

**نکات مهم**:
- می‌تواند به User مرتبط باشد (اختیاری)
- می‌تواند عضو چند واحد سازمانی باشد (ManyToMany)

---

### `PersonAssignment`
**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `MetadataModel`

**Fields**:
- `person` (ForeignKey → Person)
- `work_center_id` (BigIntegerField): شناسه مرکز کاری
- `work_center_type` (CharField, max_length=30): نوع مرکز کاری
- `is_primary` (PositiveSmallIntegerField, choices=ENABLED_FLAG_CHOICES, default=0): انبار اصلی
- `assignment_start` (DateField, null=True, blank=True): تاریخ شروع
- `assignment_end` (DateField, null=True, blank=True): تاریخ پایان
- `notes` (TextField, blank=True): یادداشت‌ها

**Constraints**:
- Unique: `(company, person, work_center_id, work_center_type)`

**نکات مهم**:
- Generic assignment به work center (با work_center_id و work_center_type)

---

## Bill of Materials (BOM) Models

### `BOM`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `bom_code` (CharField, max_length=16, unique=True): کد BOM (16 رقم)
- `finished_item` (ForeignKey → Item): کالای نهایی
- `finished_item_code` (CharField, max_length=16): کد کالای نهایی (cache)
- `version` (CharField, max_length=10, default="1.0"): نسخه
- `is_enabled` (IntegerField): فعال/غیرفعال
- و فیلدهای دیگر...

**Constraints**:
- Unique: `(company, finished_item, version)`

**Methods**:
- `save()`: Auto-generate `bom_code` if not set, cache `finished_item_code`

---

### `BOMMaterial`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `bom` (ForeignKey → BOM, on_delete=CASCADE): BOM header
- `material_item` (ForeignKey → Item): کالای ماده اولیه
- `material_item_code` (CharField, editable=False): کد کالا (cache)
- `material_type` (ForeignKey → ItemType): نوع ماده (user-defined)
- `quantity_per_unit` (DecimalField): مقدار به ازای هر واحد
- `unit` (CharField): واحد (نام واحد)
- `scrap_allowance_percent` (DecimalField, default=0): درصد ضایعات
- `is_optional` (IntegerField, choices=ENABLED_FLAG_CHOICES, default=0): اختیاری (0=Required, 1=Optional)
- `line_number` (IntegerField): شماره خط
- `description` (TextField, blank=True): توضیحات

**Methods**:
- `save()`: Auto-fill `material_item_code` and `material_type` from material_item

**نکات مهم**:
- CASCADE delete when parent BOM is deleted

---

## Process Definition Models

### `Process`
**Inheritance**: `ProductionSortableModel`

**Fields**:
- `process_code` (CharField, max_length=16, unique=True): کد فرآیند
- `finished_item` (ForeignKey → Item): کالای نهایی
- `finished_item_code` (CharField, max_length=16, blank=True): کد کالای نهایی (cache)
- `bom` (ForeignKey → BOM, null=True, blank=True): BOM مرتبط
- `revision` (CharField, max_length=20, blank=True): نسخه (اختیاری)
- `work_lines` (ManyToMany → WorkLine): خطوط کاری
- `is_primary` (IntegerField): فرآیند اصلی
- `approved_by` (ForeignKey → User, null=True, blank=True): تایید کننده
- `approval_status` (CharField): وضعیت تایید
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-generate `process_code`, cache `finished_item_code` from BOM if provided

---

### `ProcessStep`
**Inheritance**: `ProductionSortableModel`

**Fields**:
- `process` (ForeignKey → Process): فرآیند
- `work_center` (ForeignKey → WorkCenter): مرکز کاری
- `work_center_code` (CharField, max_length=5, blank=True): کد مرکز کاری (cache)
- `machine` (ForeignKey → Machine, null=True, blank=True): ماشین
- `machine_code` (CharField, max_length=10, blank=True): کد ماشین (cache)
- `sequence` (IntegerField): ترتیب
- `labor_minutes` (DecimalField): دقیقه کار نیروی انسانی
- `machine_minutes` (DecimalField): دقیقه کار ماشین
- `setup_time_minutes` (DecimalField): زمان راه‌اندازی
- و فیلدهای دیگر...

**Methods**:
- `save()`: Cache `work_center_code` and `machine_code` if assigned

---

### `ProcessOperation`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `process` (ForeignKey → Process): فرآیند
- `operation_name` (CharField): نام عملیات
- `sequence` (IntegerField): ترتیب
- و فیلدهای دیگر...

---

### `ProcessOperationMaterial`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `operation` (ForeignKey → ProcessOperation): عملیات
- `material_item` (ForeignKey → Item): کالای ماده
- `quantity_per_unit` (DecimalField): مقدار به ازای هر واحد
- و فیلدهای دیگر...

---

## Production Order Models

### `ProductOrder`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `order_code` (CharField, max_length=8, unique=True): کد سفارش (8 رقم)
- `finished_item` (ForeignKey → Item): کالای نهایی
- `finished_item_code` (CharField, max_length=16, blank=True): کد کالای نهایی (cache)
- `bom` (ForeignKey → BOM, required): BOM انتخاب شده
- `process` (ForeignKey → Process, null=True, blank=True): فرآیند (اختیاری)
- `process_code` (CharField, max_length=16, blank=True): کد فرآیند (cache)
- `planned_quantity` (DecimalField): مقدار برنامه‌ریزی شده
- `approver` (ForeignKey → User, null=True, blank=True): تایید کننده
- `priority` (CharField): اولویت
- `due_date` (DateField, null=True, blank=True): تاریخ سررسید
- `customer_reference` (CharField, max_length=120, blank=True): مرجع مشتری
- `status` (CharField): وضعیت
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-generate `order_code`, cache codes from BOM and Process

---

### `OrderPerformance`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `order` (ForeignKey → ProductOrder): سفارش
- `order_code` (CharField, max_length=8, blank=True): کد سفارش (cache)
- `finished_item_code` (CharField, max_length=16, blank=True): کد کالای نهایی (cache)
- `performance_date` (DateField): تاریخ عملکرد
- `produced_quantity` (DecimalField): مقدار تولید شده
- `received_quantity` (DecimalField): مقدار دریافت شده
- `scrapped_quantity` (DecimalField): مقدار ضایعات
- `cycle_time_minutes` (DecimalField): زمان چرخه
- `labor_hours` (DecimalField): ساعت کار نیروی انسانی
- `machine_hours` (DecimalField): ساعت کار ماشین
- `shift` (CharField, max_length=20, blank=True): شیفت
- و فیلدهای دیگر...

**Constraints**:
- Unique: `(order, performance_date)`

**Methods**:
- `save()`: Cache `order_code` and `finished_item_code`

---

## Material Transfer Models

### `TransferToLine`
**Inheritance**: `ProductionBaseModel`, `LockableModel`

**Fields**:
- `transfer_code` (CharField, max_length=16, unique=True): کد انتقال
- `order` (ForeignKey → ProductOrder): سفارش
- `work_line` (ForeignKey → WorkLine): خط کاری
- `status` (CharField): وضعیت (draft, approved, rejected)
- `approver` (ForeignKey → User, null=True, blank=True): تایید کننده
- `approved_at` (DateTimeField, null=True, blank=True): تاریخ تایید
- `is_locked` (IntegerField): قفل شده
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-generate `transfer_code`

---

### `TransferToLineItem`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `transfer` (ForeignKey → TransferToLine): انتقال
- `material_item` (ForeignKey → Item): کالای ماده
- `material_item_code` (CharField, editable=False): کد کالا (cache)
- `quantity` (DecimalField): مقدار
- `unit` (CharField): واحد
- `warehouse` (ForeignKey → Warehouse): انبار
- `is_extra` (IntegerField, choices=ENABLED_FLAG_CHOICES, default=0): اضافی (0=From BOM, 1=Extra)
- `line_number` (IntegerField): شماره خط
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-fill `material_item_code` from material_item

---

## Performance Record Models

### `PerformanceRecord`
**Inheritance**: `ProductionBaseModel`, `LockableModel`

**Fields**:
- `performance_code` (CharField, max_length=16, unique=True): کد عملکرد
- `order` (ForeignKey → ProductOrder): سفارش
- `process` (ForeignKey → Process, null=True, blank=True): فرآیند
- `work_line` (ForeignKey → WorkLine): خط کاری
- `performance_date` (DateField): تاریخ عملکرد
- `produced_quantity` (DecimalField): مقدار تولید شده
- `status` (CharField): وضعیت (draft, approved, rejected)
- `approver` (ForeignKey → User, null=True, blank=True): تایید کننده
- `approved_at` (DateTimeField, null=True, blank=True): تاریخ تایید
- `is_locked` (IntegerField): قفل شده
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-generate `performance_code`

---

### `PerformanceRecordMaterial`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `performance_record` (ForeignKey → PerformanceRecord): سند عملکرد
- `material_item` (ForeignKey → Item): کالای ماده
- `material_item_code` (CharField, editable=False): کد کالا (cache)
- `quantity_used` (DecimalField): مقدار مصرف شده
- `unit` (CharField): واحد
- `line_number` (IntegerField): شماره خط
- و فیلدهای دیگر...

---

### `PerformanceRecordPerson`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `performance_record` (ForeignKey → PerformanceRecord): سند عملکرد
- `person` (ForeignKey → Person): شخص
- `hours_worked` (DecimalField): ساعت کار
- `line_number` (IntegerField): شماره خط
- و فیلدهای دیگر...

---

### `PerformanceRecordMachine`
**Inheritance**: `ProductionBaseModel`

**Fields**:
- `performance_record` (ForeignKey → PerformanceRecord): سند عملکرد
- `machine` (ForeignKey → Machine): ماشین
- `hours_used` (DecimalField): ساعت استفاده
- `line_number` (IntegerField): شماره خط
- و فیلدهای دیگر...

---

## نکات مهم

1. **Code Generation**: بسیاری از models کدها را به صورت خودکار generate می‌کنند (با `generate_sequential_code`)
2. **Caching**: برخی models کدهای مرتبط را cache می‌کنند
3. **Company Scoping**: تمام models از `CompanyScopedModel` استفاده می‌کنند
4. **Activation**: تمام models از `ActivatableModel` استفاده می‌کنند (`is_enabled`)
5. **Locking**: برخی models از `LockableModel` استفاده می‌کنند (`is_locked`)
6. **Edit Locking**: تمام models از `EditableModel` استفاده می‌کنند
7. **Optional Dependencies**: `Warehouse` از inventory module (optional)

---

## Related Files

- `production/README.md`: Overview کلی ماژول
- `production/views/`: Views برای این models
- `production/forms/`: Forms برای این models

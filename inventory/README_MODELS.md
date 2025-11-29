# inventory/models.py - Inventory Models (Complete Documentation)

**هدف**: تمام model classes برای ماژول inventory

این فایل شامل 43 model class است که به دسته‌های زیر تقسیم می‌شوند:
- Base Models (Abstract)
- Master Data Models
- Item Definition Models
- Supplier Relations Models
- Document Models (Receipts, Issues, Stocktaking)
- Request Models
- Traceability Models (Lots, Serials)

---

## وابستگی‌ها

- `shared.models`: `ActivatableModel`, `CompanyScopedModel`, `LockableModel`, `MetadataModel`, `SortableModel`, `TimeStampedModel`, `User`, `CompanyUnit`
- `inventory.utils.codes`: `generate_sequential_code`
- `django.db.models`
- `django.core.validators`: `MinValueValidator`, `RegexValidator`
- `django.utils.timezone`
- `decimal.Decimal`

---

## Validators و Constants

### `NUMERIC_CODE_VALIDATOR`
- `RegexValidator(regex=r"^\d+$")`: فقط کاراکترهای عددی مجاز

### `POSITIVE_DECIMAL`
- `MinValueValidator(Decimal("0"))`: مقادیر مثبت یا صفر

### `CURRENCY_CHOICES`
- `("IRT", "Toman")`
- `("IRR", "Rial")`
- `("USD", "US Dollar")`

---

## Base Models (Abstract)

### `InventoryBaseModel`
**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `MetadataModel`

**توضیح**: Base model برای تمام inventory models

**Fields** (از mixins):
- `company` (ForeignKey): Company scope
- `created_at`, `updated_at` (DateTime): Timestamps
- `is_enabled` (IntegerField): Activation flag
- `created_by`, `updated_by` (ForeignKey): Metadata

---

### `InventorySortableModel`
**Inheritance**: `InventoryBaseModel`, `SortableModel`

**توضیح**: Base model با sort_order

**Fields** (اضافی):
- `sort_order` (IntegerField): ترتیب نمایش

---

### `InventoryDocumentBase`
**Inheritance**: `InventoryBaseModel`, `LockableModel`

**توضیح**: Base model برای document-style models

**Fields**:
- `document_code` (CharField, max_length=30, unique=True): کد سند
- `document_date` (DateField, default=timezone.now): تاریخ سند
- `notes` (TextField, blank=True): یادداشت‌ها
- `is_locked` (IntegerField): Lock status (از LockableModel)
- `editing_by`, `editing_started_at`, `editing_session_key` (از LockableModel)

---

## Master Data Models

### `ItemType`
**Inheritance**: `InventorySortableModel`

**Fields**:
- `public_code` (CharField, max_length=3, validators=[NUMERIC_CODE_VALIDATOR]): کد عمومی
- `name` (CharField, max_length=120): نام فارسی
- `name_en` (CharField, max_length=120): نام انگلیسی
- `description` (CharField, max_length=255, blank=True): توضیحات
- `notes` (TextField, blank=True): یادداشت‌ها

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, name)`
- Unique: `(company, name_en)`

**Methods**:
- `save()`: Auto-generate `public_code` if not set

---

### `ItemCategory`
**Inheritance**: `InventorySortableModel`

**Fields**: مشابه `ItemType`

**Constraints**: مشابه `ItemType`

---

### `ItemSubcategory`
**Inheritance**: `InventorySortableModel`

**Fields**: مشابه `ItemType`

**Constraints**: مشابه `ItemType`

---

### `Warehouse`
**Inheritance**: `InventorySortableModel`

**Fields**:
- `public_code` (CharField, max_length=5): کد عمومی (5 رقم)
- `name` (CharField, max_length=120): نام
- `name_en` (CharField, max_length=120): نام انگلیسی
- `description` (CharField, max_length=255, blank=True): توضیحات
- `notes` (TextField, blank=True): یادداشت‌ها

**Constraints**:
- Unique: `(company, public_code)`
- Unique: `(company, name)`

**Methods**:
- `save()`: Auto-generate `public_code` (width=5) if not set

---

## Item Definition Models

### `Item`
**Inheritance**: `InventorySortableModel`

**Fields**:
- `type` (ForeignKey → ItemType)
- `category` (ForeignKey → ItemCategory)
- `subcategory` (ForeignKey → ItemSubcategory)
- `type_code`, `category_code`, `subcategory_code` (CharField, editable=False): کدهای cache شده
- `user_segment` (CharField, max_length=2): بخش کاربر (2 رقم)
- `sequence_segment` (CharField, max_length=5, editable=False): بخش ترتیب (5 رقم)
- `item_code` (CharField, max_length=7, blank=True): کد 7 رقمی: User(2) + Sequence(5)
- `full_item_code` (CharField, max_length=16, unique=True, blank=True): کد کامل 16 رقمی
- `batch_number` (CharField, max_length=20): شماره batch
- `secondary_batch_number` (CharField, max_length=50, blank=True): شماره batch ثانویه (user-defined)
- `name` (CharField, max_length=180, unique=True): نام
- `name_en` (CharField, max_length=180, unique=True): نام انگلیسی
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-generate codes based on type/category/subcategory and current month

---

### `ItemSpec`
**Inheritance**: `InventorySortableModel`

**Fields**:
- `item` (ForeignKey → Item)
- `item_code` (CharField, editable=False): کد cache شده
- `spec_data` (JSONField): JSON specification

---

### `ItemUnit`
**Inheritance**: `InventorySortableModel`

**Fields**:
- `item` (ForeignKey → Item)
- `item_code` (CharField, editable=False): کد cache شده
- `unit_name` (CharField): نام واحد
- `conversion_factor` (DecimalField): ضریب تبدیل

---

### `ItemWarehouse`
**Inheritance**: `InventoryBaseModel`

**Fields**:
- `item` (ForeignKey → Item)
- `warehouse` (ForeignKey → Warehouse)
- `is_primary` (IntegerField): انبار اصلی

---

### `ItemSubstitute`
**Inheritance**: `InventorySortableModel`

**Fields**:
- `source_item` (ForeignKey → Item)
- `target_item` (ForeignKey → Item)
- `source_item_code`, `target_item_code` (CharField, editable=False): کدهای cache شده
- `substitute_quantity` (DecimalField): مقدار جایگزین

---

## Supplier Relations Models

### `Supplier`
**Inheritance**: `InventorySortableModel`

**Fields**:
- `public_code` (CharField, max_length=5): کد عمومی
- `name` (CharField, max_length=120): نام
- `name_en` (CharField, max_length=120): نام انگلیسی
- و فیلدهای دیگر...

---

### `SupplierCategory`
**Inheritance**: `InventoryBaseModel`

**Fields**: مشابه `ItemCategory`

---

### `SupplierSubcategory`
**Inheritance**: `InventoryBaseModel`

**Fields**: مشابه `ItemCategory`

---

### `SupplierItem`
**Inheritance**: `InventoryBaseModel`

**Fields**:
- `supplier` (ForeignKey → Supplier)
- `item` (ForeignKey → Item)
- `supplier_item_code` (CharField): کد کالا در supplier
- و فیلدهای دیگر...

---

## Document Models

### Receipt Documents

#### `ReceiptTemporary`
**Inheritance**: `InventoryDocumentBase`

**Fields**: از `InventoryDocumentBase`

---

#### `ReceiptPermanent`
**Inheritance**: `InventoryDocumentBase`

**Fields**:
- `supplier` (ForeignKey → Supplier, null=True)
- `warehouse` (ForeignKey → Warehouse)
- و فیلدهای دیگر...

---

#### `ReceiptConsignment`
**Inheritance**: `InventoryDocumentBase`

**Fields**: مشابه `ReceiptPermanent`

---

### Receipt Line Models

#### `ReceiptLineBase`
**Inheritance**: `InventoryBaseModel`, `SortableModel`

**Fields**:
- `item` (ForeignKey → Item)
- `item_code` (CharField, editable=False): کد cache شده
- `quantity` (DecimalField): مقدار
- `unit` (CharField): واحد
- و فیلدهای دیگر...

---

#### `ReceiptPermanentLine`
**Inheritance**: `ReceiptLineBase`

**Fields**:
- `document` (ForeignKey → ReceiptPermanent)
- `supplier` (ForeignKey → Supplier, null=True)
- و فیلدهای دیگر...

---

#### `ReceiptConsignmentLine`
**Inheritance**: `ReceiptLineBase`

**Fields**:
- `document` (ForeignKey → ReceiptConsignment)
- و فیلدهای دیگر...

---

#### `ReceiptTemporaryLine`
**Inheritance**: `ReceiptLineBase`

**Fields**:
- `document` (ForeignKey → ReceiptTemporary)
- و فیلدهای دیگر...

---

### Issue Documents

#### `IssuePermanent`
**Inheritance**: `InventoryDocumentBase`

**Fields**:
- `warehouse` (ForeignKey → Warehouse)
- `department_unit` (ForeignKey → CompanyUnit, null=True)
- و فیلدهای دیگر...

---

#### `IssueConsumption`
**Inheritance**: `InventoryDocumentBase`

**Fields**:
- `warehouse` (ForeignKey → Warehouse)
- `work_line` (ForeignKey → WorkLine, null=True): از production module
- `department_unit` (ForeignKey → CompanyUnit, null=True)
- `cost_center_code` (CharField, blank=True)
- و فیلدهای دیگر...

---

#### `IssueConsignment`
**Inheritance**: `InventoryDocumentBase`

**Fields**: مشابه `IssuePermanent`

---

### Issue Line Models

#### `IssueLineBase`
**Inheritance**: `InventoryBaseModel`, `SortableModel`

**Fields**:
- `item` (ForeignKey → Item)
- `item_code` (CharField, editable=False): کد cache شده
- `quantity` (DecimalField): مقدار
- `unit` (CharField): واحد
- و فیلدهای دیگر...

---

#### `IssuePermanentLine`
**Inheritance**: `IssueLineBase`

**Fields**:
- `document` (ForeignKey → IssuePermanent)
- و فیلدهای دیگر...

---

#### `IssueConsumptionLine`
**Inheritance**: `IssueLineBase`

**Fields**:
- `document` (ForeignKey → IssueConsumption)
- و فیلدهای دیگر...

---

#### `IssueConsignmentLine`
**Inheritance**: `IssueLineBase`

**Fields**:
- `document` (ForeignKey → IssueConsignment)
- و فیلدهای دیگر...

---

## Stocktaking Models

### `StocktakingRecord`
**Inheritance**: `InventoryDocumentBase`

**Fields**:
- `warehouse` (ForeignKey → Warehouse)
- `approval_status` (CharField): وضعیت تایید
- `approver` (ForeignKey → User, null=True)
- `approved_at` (DateTimeField, null=True)
- و فیلدهای دیگر...

---

### `StocktakingDeficit`
**Inheritance**: `InventoryDocumentBase`

**Fields**:
- `warehouse` (ForeignKey → Warehouse)
- و فیلدهای دیگر...

---

### `StocktakingSurplus`
**Inheritance**: `InventoryDocumentBase`

**Fields**: مشابه `StocktakingDeficit`

---

### `StocktakingDeficitLine`
**Inheritance**: `InventoryBaseModel`, `SortableModel`

**Fields**:
- `document` (ForeignKey → StocktakingDeficit)
- `item` (ForeignKey → Item)
- `quantity_adjusted` (DecimalField): مقدار کسری
- و فیلدهای دیگر...

---

### `StocktakingSurplusLine`
**Inheritance**: `InventoryBaseModel`, `SortableModel`

**Fields**:
- `document` (ForeignKey → StocktakingSurplus)
- `item` (ForeignKey → Item)
- `quantity_adjusted` (DecimalField): مقدار مازاد
- و فیلدهای دیگر...

---

## Request Models

### `PurchaseRequest`
**Inheritance**: `InventoryBaseModel`, `LockableModel`

**Fields**:
- `request_code` (CharField, unique=True): کد درخواست
- `requested_by` (ForeignKey → User)
- `approver` (ForeignKey → User, null=True)
- `status` (CharField): وضعیت (DRAFT, APPROVED, etc.)
- و فیلدهای دیگر...

---

### `PurchaseRequestLine`
**Inheritance**: `InventoryBaseModel`, `SortableModel`

**Fields**:
- `document` (ForeignKey → PurchaseRequest)
- `item` (ForeignKey → Item)
- `quantity` (DecimalField): مقدار درخواستی
- و فیلدهای دیگر...

---

### `WarehouseRequest`
**Inheritance**: `InventoryBaseModel`, `LockableModel`

**Fields**:
- `request_code` (CharField, unique=True): کد درخواست
- `requester` (ForeignKey → User)
- `approver` (ForeignKey → User, null=True)
- `request_status` (CharField): وضعیت درخواست
- `warehouse` (ForeignKey → Warehouse)
- و فیلدهای دیگر...

---

### `WarehouseRequestLine`
**Inheritance**: `InventoryBaseModel`, `SortableModel`

**Fields**:
- `document` (ForeignKey → WarehouseRequest)
- `item` (ForeignKey → Item)
- `quantity` (DecimalField): مقدار درخواستی
- و فیلدهای دیگر...

---

## Traceability Models

### `ItemLot`
**Inheritance**: `InventoryBaseModel`

**Fields**:
- `item` (ForeignKey → Item)
- `lot_code` (CharField, unique=True): کد lot (فرمت: LOT-MMYY-XXXXXX)
- `warehouse` (ForeignKey → Warehouse)
- `quantity` (DecimalField): مقدار
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-generate `lot_code` if not set (format: LOT-MMYY-XXXXXX)

---

### `ItemSerial`
**Inheritance**: `InventoryBaseModel`

**Fields**:
- `item` (ForeignKey → Item)
- `serial_code` (CharField, unique=True): کد serial
- `secondary_serial_code` (CharField, max_length=50, blank=True): کد serial ثانویه (user-defined)
- `warehouse` (ForeignKey → Warehouse, null=True)
- `status` (CharField): وضعیت (AVAILABLE, RESERVED, ISSUED, etc.)
- `current_document_type` (CharField, blank=True): نوع سند فعلی
- `current_document_id` (IntegerField, null=True): شناسه سند فعلی
- و فیلدهای دیگر...

**Methods**:
- `save()`: Auto-generate `serial_code` if not set

---

### `ItemSerialHistory`
**Inheritance**: `InventoryBaseModel`

**Fields**:
- `serial` (ForeignKey → ItemSerial)
- `event_type` (CharField): نوع event (RESERVATION, RELEASE, ISSUE, CONSUMPTION, RETURN)
- `document_type` (CharField): نوع سند
- `document_id` (IntegerField): شناسه سند
- `warehouse` (ForeignKey → Warehouse, null=True)
- `notes` (TextField, blank=True): یادداشت‌ها

**نکات مهم**:
- Immutable audit log
- هر تغییر در serial یک record جدید ایجاد می‌کند

---

## QC Models

### `QCRejectionDetail`
**Inheritance**: `models.Model`

**Fields**:
- `receipt_line` (ForeignKey → ReceiptTemporaryLine)
- `item` (ForeignKey → Item)
- `quantity_rejected` (DecimalField): مقدار رد شده
- `rejection_reason` (TextField): دلیل رد
- و فیلدهای دیگر...

---

## نکات مهم

1. **Code Generation**: بسیاری از models کدها را به صورت خودکار generate می‌کنند (با `generate_sequential_code`)
2. **Caching**: برخی models کدهای مرتبط را cache می‌کنند (مثل `item_code` در line models)
3. **Company Scoping**: تمام models از `CompanyScopedModel` استفاده می‌کنند
4. **Activation**: تمام models از `ActivatableModel` استفاده می‌کنند (`is_enabled`)
5. **Locking**: Document models از `LockableModel` استفاده می‌کنند (`is_locked`)
6. **Sorting**: بسیاری از models از `SortableModel` استفاده می‌کنند (`sort_order`)

---

## Related Files

- `inventory/README.md`: Overview کلی ماژول
- `inventory/views/`: Views برای این models
- `inventory/forms/`: Forms برای این models
- `inventory/utils/codes.py`: Code generation utilities

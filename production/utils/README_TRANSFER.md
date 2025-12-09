# production/utils/transfer.py - Transfer Utility Functions

**هدف**: مستندات توابع کمکی برای درخواست‌های Transfer to Line

این فایل شامل توابع کمکی برای مدیریت انتقال مواد به خط تولید و ایجاد خودکار حواله‌های انتقال بین انبارها است.

---

## فهرست توابع

### Code Generation
- `generate_transfer_code()` - تولید کد متوالی برای transfer

### Order Status Tracking
- `get_transferred_materials_for_order()` - دریافت مواد منتقل شده برای یک order
- `get_transferred_operations_for_order()` - دریافت عملیات‌های منتقل شده برای یک order
- `is_full_order_transferred()` - بررسی اینکه آیا تمام مواد BOM برای order منتقل شده‌اند
- `get_available_operations_for_order()` - دریافت لیست عملیات‌های در دسترس برای order
- `get_operation_materials()` - دریافت تمام مواد یک عملیات خاص

### Warehouse Selection
- `get_warehouse_inventory_balance()` - دریافت موجودی یک کالا در یک انبار
- `select_source_warehouses_by_priority()` - انتخاب انبارهای منبع بر اساس اولویت و موجودی (پشتیبانی از چند انبار)
- `select_source_warehouse_by_priority()` - انتخاب یک انبار منبع (DEPRECATED - برای backward compatibility)

### Warehouse Transfer Creation
- `process_item_with_substitutes()` - پردازش یک کالا با منطق جایگزین‌ها (5 مرحله)
- `create_warehouse_transfer_for_transfer_to_line()` - ایجاد سند حواله انتقال بین انبارها برای transfer request

---

## توابع اصلی

### `generate_transfer_code()`

**هدف**: تولید کد متوالی برای transfer با prefix

**پارامترها**:
- `company_id` (int): شناسه شرکت
- `prefix` (str, optional): پیشوند کد (پیش‌فرض: 'TR')
- `width` (int, optional): عرض بخش عددی (پیش‌فرض: 8)

**بازگشت**: کد transfer به فرمت `prefix + zero-padded number` (مثلاً 'TR00000001')

**نکته**: این تابع باید در یک transaction فراخوانی شود تا atomicity تضمین شود.

---

### `get_transferred_materials_for_order()`

**هدف**: دریافت مجموعه شناسه‌های کالاهایی که برای یک order منتقل شده‌اند

**پارامترها**:
- `order` (ProductOrder): instance سفارش
- `exclude_scrap_replacement` (bool, optional): آیا transfers با `is_scrap_replacement=1` حذف شوند (پیش‌فرض: True)

**بازگشت**: مجموعه شناسه‌های کالاهای منتقل شده

---

### `get_transferred_operations_for_order()`

**هدف**: دریافت مجموعه شناسه‌های عملیات‌هایی که به طور کامل برای یک order منتقل شده‌اند

**منطق**: یک عملیات منتقل شده محسوب می‌شود اگر تمام مواد آن منتقل شده باشند.

**پارامترها**:
- `order` (ProductOrder): instance سفارش
- `exclude_scrap_replacement` (bool, optional): آیا transfers با `is_scrap_replacement=1` حذف شوند (پیش‌فرض: True)

**بازگشت**: مجموعه شناسه‌های عملیات‌های منتقل شده

---

### `is_full_order_transferred()`

**هدف**: بررسی اینکه آیا تمام مواد BOM برای یک order منتقل شده‌اند

**پارامترها**:
- `order` (ProductOrder): instance سفارش
- `exclude_scrap_replacement` (bool, optional): آیا transfers با `is_scrap_replacement=1` حذف شوند (پیش‌فرض: True)

**بازگشت**: `True` اگر تمام مواد BOM منتقل شده باشند، در غیر این صورت `False`

---

### `get_available_operations_for_order()`

**هدف**: دریافت لیست عملیات‌های در دسترس برای یک order

**پارامترها**:
- `order` (ProductOrder): instance سفارش
- `include_scrap_replacement` (bool, optional): آیا عملیات‌های منتقل شده برای scrap replacement مجاز باشند (deprecated)
- `scrap_replacement_mode` (bool, optional): 
  - `True`: فقط عملیات‌های منتقل شده را برگرداند
  - `False`: فقط عملیات‌های منتقل نشده را برگرداند (پیش‌فرض)

**بازگشت**: لیست dictionaries با اطلاعات عملیات:
```python
[
    {
        'id': operation.id,
        'name': operation.name,
        'sequence_order': operation.sequence_order,
        'description': operation.description,
    },
    ...
]
```

---

### `get_operation_materials()`

**هدف**: دریافت تمام مواد یک عملیات خاص

**پارامترها**:
- `operation` (ProcessOperation): instance عملیات
- `order` (ProductOrder): instance سفارش (برای محاسبه مقدار)

**بازگشت**: لیست `ProcessOperationMaterial` instances مرتب شده بر اساس `id`

---

### `get_warehouse_inventory_balance()`

**هدف**: دریافت موجودی یک کالا در یک انبار

**پارامترها**:
- `company_id` (int): شناسه شرکت
- `warehouse_id` (int): شناسه انبار
- `item_id` (int): شناسه کالا
- `as_of_date` (date, optional): تاریخ محاسبه موجودی

**بازگشت**: موجودی فعلی به صورت `Decimal`، یا `Decimal('0')` در صورت خطا

**نکته**: از `inventory.inventory_balance.calculate_item_balance()` استفاده می‌کند.

---

### `select_source_warehouses_by_priority()`

**هدف**: انتخاب انبارهای منبع بر اساس اولویت و موجودی

این تابع منطق مراحل 2 و 3 را پیاده‌سازی می‌کند:
- **مرحله 2**: اگر کل موجودی در یک انبار بود، همان انبار را برمی‌گرداند
- **مرحله 3**: اگر موجودی در چند انبار بود، از همه آن‌ها به ترتیب اولویت استفاده می‌کند

**پارامترها**:
- `company_id` (int): شناسه شرکت
- `item_id` (int): شناسه کالا
- `source_warehouses_list` (List[Dict]): لیست انبارها با اولویت
  - فرمت: `[{'warehouse_id': 1, 'warehouse_code': '001', 'priority': 1}, ...]`
- `quantity_required` (Decimal): مقدار مورد نیاز
- `as_of_date` (date, optional): تاریخ محاسبه موجودی

**بازگشت**: 
- `Tuple[List[Tuple[Warehouse, Decimal]], Optional[str]]`
- لیست tuples شامل `(warehouse, quantity)` برای هر انبار انتخاب شده
- در صورت خطا: `([], error_message)`

**منطق**:
1. انبارها را بر اساس اولویت مرتب می‌کند (1, 2, 3...)
2. برای هر انبار به ترتیب اولویت:
   - اگر موجودی کافی برای کل مقدار بود → همان انبار را برمی‌گرداند
   - در غیر این صورت، موجودی آن انبار را به لیست اضافه می‌کند
3. اگر مجموع موجودی از چند انبار کافی بود → همه آن‌ها را برمی‌گرداند

---

### `select_source_warehouse_by_priority()`

**هدف**: انتخاب یک انبار منبع (DEPRECATED)

**وضعیت**: ⚠️ **DEPRECATED** - از `select_source_warehouses_by_priority()` استفاده کنید

این تابع برای backward compatibility نگه داشته شده و فقط اولین انبار را برمی‌گرداند.

---

### `process_item_with_substitutes()`

**هدف**: پردازش یک کالا با منطق کامل جایگزین‌ها (5 مرحله)

این تابع منطق کامل ایجاد حواله را پیاده‌سازی می‌کند:

**پارامترها**:
- `company_id` (int): شناسه شرکت
- `main_item_id` (int): شناسه کالای اصلی
- `main_item_code` (str): کد کالای اصلی
- `quantity_required` (Decimal): مقدار مورد نیاز
- `unit` (str): واحد اندازه‌گیری
- `source_warehouses_list` (List[Dict]): لیست انبارهای مبدأ با اولویت
- `destination_warehouse` (Warehouse): انبار مقصد
- `as_of_date` (date, optional): تاریخ محاسبه موجودی
- `bom_material_id` (int, optional): شناسه BOM material (برای بررسی جایگزین‌ها)

**بازگشت**: 
- `Tuple[List[Dict], Optional[str]]`
- لیست dictionaries با اطلاعات خطوط حواله:
  ```python
  [
      {
          'item_id': int,
          'item_code': str,
          'source_warehouse': Warehouse,
          'destination_warehouse': Warehouse,
          'quantity': Decimal,
          'unit': str,
      },
      ...
  ]
  ```
- در صورت خطا: `([], error_message)`

**منطق 5 مرحله‌ای**:

#### مرحله 1: بررسی کالای اصلی
- بررسی کالای اصلی و انبارهای مبدأ به ترتیب اولویت

#### مرحله 2: اگر در یک انبار کل موجودی بود
- اگر در یکی از انبارهای مبدأ (به ترتیب اولویت) کل موجودی مورد نیاز موجود بود
- از همان انبار حواله صادر می‌شود

#### مرحله 3: اگر در چند انبار مجموعش بود
- اگر در یک انبار کافی نبود
- اما مجموع موجودی در چند انبار (به ترتیب اولویت) کافی بود
- از آن انبارها (به ترتیب اولویت) حواله صادر می‌شود تا کل موجودی را پوشش دهد

#### مرحله 5: بررسی جایگزین‌های با تیک ترکیب (اولویت اول)
- اگر کالای اصلی موجودی کافی نداشت (`main_item_available < quantity_required`)
- **ابتدا** جایگزین‌های با تیک ترکیب (`is_combinable == 1`) بررسی می‌شوند
- اگر کالای اصلی مقداری موجودی داشت:
  - از کالای اصلی برای موجودی آن استفاده می‌شود
  - باقیمانده از جایگزین با تیک ترکیب تأمین می‌شود
- اگر کالای اصلی موجودی نداشت:
  - از جایگزین با تیک ترکیب برای کل مقدار استفاده می‌شود

#### مرحله 4: بررسی جایگزین‌های بدون تیک ترکیب (اولویت دوم)
- **فقط** اگر جایگزین‌های با تیک ترکیب جواب ندادند
- به ترتیب اولویت جایگزین‌های بدون تیک ترکیب (`is_combinable == 0`) بررسی می‌شوند
- برای هر جایگزین منطق مرحله 1 و 2 اعمال می‌شود (بررسی انبارها به ترتیب اولویت)
- اگر یک جایگزین کل مقدار را تأمین کرد، از همان استفاده می‌شود

**ترتیب اجرا**:
1. ابتدا کالای اصلی (مراحل 1-3)
2. اگر کافی نبود، ابتدا جایگزین‌های با تیک ترکیب (مرحله 5)
3. اگر با ترکیب اصلی و جایگزین حل نشد، سپس جایگزین‌های بدون تیک ترکیب (مرحله 4)

---

### `create_warehouse_transfer_for_transfer_to_line()`

**هدف**: ایجاد سند حواله انتقال بین انبارها برای یک transfer request

این تابع اصلی است که برای هر item در transfer request، منطق 5 مرحله‌ای را اعمال می‌کند و سند `IssueWarehouseTransfer` را ایجاد می‌کند.

**پارامترها**:
- `transfer` (TransferToLine): instance transfer request
- `user` (User): کاربر ایجادکننده (برای audit fields)

**بازگشت**: 
- `Tuple[Optional[IssueWarehouseTransfer], Optional[str]]`
- در صورت موفقیت: `(warehouse_transfer_document, None)`
- در صورت خطا: `(None, error_message)`

**منطق**:
1. دریافت تمام items از transfer request
2. برای هر item:
   - دریافت انبار مقصد از `destination_work_center.warehouse`
   - دریافت لیست انبارهای مبدأ از BOM material (یا از item برای extra items)
   - فراخوانی `process_item_with_substitutes()` برای پردازش item با منطق 5 مرحله‌ای
   - جمع‌آوری خطوط حواله
3. ایجاد سند `IssueWarehouseTransfer` با:
   - کد سند خودکار (`WHT` prefix)
   - تاریخ transfer
   - لینک به `production_transfer`
4. ایجاد خطوط `IssueWarehouseTransferLine` برای هر خط حواله

**نکات مهم**:
- از `@transaction.atomic` استفاده می‌کند تا اطمینان حاصل شود که یا همه چیز ذخیره می‌شود یا هیچ چیز
- برای BOM items، `source_warehouses` از `BOMMaterial` دریافت می‌شود
- برای extra items، `source_warehouse` از خود item دریافت می‌شود
- اگر هیچ item معتبری پیدا نشد، خطا برمی‌گرداند

**خطاهای ممکن**:
- "Transfer request has no items."
- "Item {item_code}: No destination warehouse specified (WorkLine has no warehouse)."
- "Item {item_code}: No source warehouse found. Please configure ItemWarehouse or BOM source_warehouses."
- "Item {item_code}: Insufficient inventory for item and its substitutes"
- "No valid items found for warehouse transfer."

---

## وابستگی‌ها

### Models
- `production.models`: `TransferToLine`, `TransferToLineItem`, `ProductOrder`, `BOMMaterial`, `BOMMaterialAlternative`
- `inventory.models`: `IssueWarehouseTransfer`, `IssueWarehouseTransferLine`, `Warehouse`, `ItemWarehouse`, `Item`

### Services
- `inventory.inventory_balance`: `calculate_item_balance()`
- `inventory.forms.base`: `generate_document_code()`

---

## مثال استفاده

```python
from production.utils.transfer import create_warehouse_transfer_for_transfer_to_line
from production.models import TransferToLine

# ایجاد حواله انتقال بین انبارها برای یک transfer request
transfer = TransferToLine.objects.get(id=123)
warehouse_transfer, error = create_warehouse_transfer_for_transfer_to_line(
    transfer=transfer,
    user=request.user
)

if error:
    print(f"Error: {error}")
else:
    print(f"Created warehouse transfer: {warehouse_transfer.document_code}")
```

---

## نکات مهم

1. **اولویت انبارها**: انبارها باید در `source_warehouses` با فیلد `priority` مرتب شوند (1 = بالاترین اولویت)

2. **جایگزین‌ها**: جایگزین‌ها باید در `BOMMaterialAlternative` با فیلد `priority` مرتب شوند

3. **تیک ترکیب**: فیلد `is_combinable` در `BOMMaterialAlternative` تعیین می‌کند که آیا جایگزین می‌تواند با کالای اصلی ترکیب شود یا نه

4. **محاسبه موجودی**: موجودی بر اساس `as_of_date` (یا تاریخ امروز) محاسبه می‌شود

5. **Transaction Safety**: تمام عملیات در یک transaction انجام می‌شوند تا consistency تضمین شود

---

## تاریخچه تغییرات

- **2025-12-09**: پیاده‌سازی منطق کامل 5 مرحله‌ای برای ایجاد حواله
  - اضافه شدن پشتیبانی از چند انبار برای یک کالا
  - اضافه شدن منطق جایگزین‌ها با تیک ترکیب
  - اضافه شدن توابع `get_warehouse_inventory_balance()` و `select_source_warehouses_by_priority()`
  - بازنویسی `process_item_with_substitutes()` با منطق کامل
  - بازنویسی `create_warehouse_transfer_for_transfer_to_line()` برای استفاده از منطق جدید

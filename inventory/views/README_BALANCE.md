# inventory/views/balance.py - Inventory Balance Views (Complete Documentation)

**هدف**: Views برای نمایش و محاسبه موجودی انبار (Inventory Balance) در ماژول inventory

این فایل شامل 3 view class:
- InventoryBalanceView: نمایش موجودی انبار با فیلترها
- InventoryBalanceDetailsView: نمایش جزئیات تراکنش‌های یک کالا در انبار
- InventoryBalanceAPIView: API endpoint برای محاسبه موجودی

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`
- `inventory.models`: `Item`, `Warehouse`, `ItemType`, `ItemCategory`, `ReceiptPermanentLine`, `ReceiptConsignmentLine`, `IssuePermanentLine`, `IssueConsumptionLine`, `IssueConsignmentLine`
- `inventory.inventory_balance`: `calculate_warehouse_balances`, `calculate_item_balance`, `get_last_stocktaking_baseline`
- `inventory.utils.jalali`: `jalali_to_gregorian`
- `shared.models`: `CompanyUnit`
- `django.views.generic.TemplateView`
- `django.http.JsonResponse`
- `django.utils.translation.gettext_lazy`
- `datetime.date`

---

## InventoryBalanceView

**Type**: `InventoryBaseView, TemplateView`

**Template**: `inventory/inventory_balance.html`

**متدها**:

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: محاسبه و بازگشت موجودی انبار با فیلترها.

**Query Parameters**:
- `warehouse_id`: شناسه انبار (required برای محاسبه)
- `item_type_id`: فیلتر بر اساس نوع کالا (optional)
- `item_category_id`: فیلتر بر اساس دسته‌بندی (optional)
- `as_of_date`: تاریخ محاسبه (optional، format: YYYY-MM-DD یا YYYY/MM/DD)

**Context Variables**:
- `warehouses`: لیست انبارهای فعال
- `item_types`: لیست انواع کالا
- `item_categories`: لیست دسته‌بندی‌ها
- `selected_warehouse_id`: انبار انتخاب شده
- `selected_item_type_id`: نوع کالا انتخاب شده
- `selected_item_category_id`: دسته‌بندی انتخاب شده
- `as_of_date`: تاریخ محاسبه
- `balances`: لیست موجودی‌ها (اگر warehouse انتخاب شده باشد)
- `total_items`: تعداد کل کالاها
- `total_balance_value`: مجموع ارزش موجودی
- `error`: پیام خطا (در صورت وجود)

**منطق**:
1. Parse کردن تاریخ (Gregorian یا Jalali)
2. دریافت فیلترها از query parameters
3. محاسبه موجودی با `calculate_warehouse_balances()` اگر warehouse انتخاب شده باشد
4. محاسبه مجموع‌ها

**URL**: `/inventory/balance/`

---

## InventoryBalanceDetailsView

**Type**: `InventoryBaseView, TemplateView`

**Template**: `inventory/inventory_balance_details.html`

**URL Parameters**:
- `item_id`: شناسه کالا
- `warehouse_id`: شناسه انبار

**Query Parameters**:
- `as_of_date`: تاریخ محاسبه (optional)

**متدها**:

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: دریافت تاریخچه تراکنش‌های یک کالا در انبار.

**Context Variables**:
- `item`: کالا (Item instance)
- `warehouse`: انبار (Warehouse instance)
- `baseline`: اطلاعات baseline از آخرین انبارگردانی (dict شامل `baseline_quantity`, `baseline_date`, `baseline_value`)
- `baseline_date`: تاریخ baseline (date object)
- `as_of_date`: تاریخ محاسبه (date object)
- `transactions`: لیست تراکنش‌ها (list of dicts)
- `total_receipts`: مجموع receipts (float)
- `total_issues`: مجموع issues (float)
- `current_balance`: موجودی فعلی (float)
- `error`: پیام خطا (در صورت وجود)

**Transaction Structure**:
هر تراکنش در `transactions` یک dict با ساختار زیر است:
- `date`: تاریخ تراکنش (date object)
- `type`: نوع تراکنش (`'receipt'` یا `'issue'`)
- `type_label`: برچسب نوع تراکنش (مثلاً `'Permanent Receipt'`, `'Consumption Issue'`, `'مازاد انبارگردانی'`, `'کسری انبارگردانی'`)
- `document_code`: کد سند (string)
- `document_id`: شناسه سند (int)
- `document_type`: نوع سند (`'permanent_receipt'`, `'consignment_receipt'`, `'permanent_issue'`, `'consumption_issue'`, `'consignment_issue'`, `'stocktaking_surplus'`, `'stocktaking_deficit'`)
- `quantity`: مقدار (float)
- `unit`: واحد (string)
- `created_by`: نام کاربر ایجادکننده (string)
- `source_destination`: منبع/مقصد (string - نام supplier برای receipts، نام department_unit/work_line برای issues، `'—'` برای stocktaking)
- `running_balance`: موجودی پس از این تراکنش (float)

**منطق**:
1. Parse کردن تاریخ `as_of_date` (Gregorian یا Jalali) - در صورت خطا از `date.today()` استفاده می‌شود
2. دریافت `company_id` از session یا user access
3. دریافت `item` و `warehouse` از database (با فیلتر `company_id`)
4. دریافت baseline از آخرین انبارگردانی با `get_last_stocktaking_baseline(company_id, warehouse_id, item_id, as_of_date)`
5. دریافت تمام receipts (Permanent, Consignment) از `baseline_date` تا `as_of_date`:
   - `ReceiptPermanentLine`: با `select_related('document', 'document__created_by', 'supplier')`
   - `ReceiptConsignmentLine`: با `select_related('document', 'document__created_by', 'supplier')`
6. دریافت تمام issues (Permanent, Consumption, Consignment) از `baseline_date` تا `as_of_date`:
   - `IssuePermanentLine`: با `select_related('document', 'document__created_by', 'document__department_unit')`
   - `IssueConsumptionLine`: با `select_related('document', 'document__created_by', 'document__department_unit', 'work_line')`
   - `IssueConsignmentLine`: با `select_related('document', 'document__created_by', 'document__department_unit')`
7. دریافت stocktaking surplus lines (positive movements) از `baseline_date` تا `as_of_date`:
   - `StocktakingSurplusLine`: فقط documents با `is_locked=1` و `is_enabled=1`
   - با `select_related('document', 'document__created_by')`
8. دریافت stocktaking deficit lines (negative movements) از `baseline_date` تا `as_of_date`:
   - `StocktakingDeficitLine`: فقط documents با `is_locked=1` و `is_enabled=1`
   - با `select_related('document', 'document__created_by')`
9. ساخت transaction dicts برای هر receipt/issue/surplus/deficit:
   - برای receipts: `source_destination` از `supplier.name` (یا `'—'`)
   - برای issues: `source_destination` از `department_unit.name` یا `work_line.name` یا `destination_code`/`cost_center_code` (یا `'—'`)
   - برای stocktaking: `source_destination = '—'`
10. ترکیب تمام تراکنش‌ها در یک لیست
11. مرتب‌سازی تراکنش‌ها بر اساس `date` (ascending)
12. محاسبه running balance برای هر تراکنش:
    - شروع از `baseline['baseline_quantity']`
    - برای receipts: `running_balance += quantity`
    - برای issues: `running_balance -= quantity`
13. محاسبه موجودی فعلی: آخرین `running_balance` (یا `baseline_quantity` اگر تراکنشی نباشد)
14. محاسبه مجموع receipts و issues: `sum(quantity for type == 'receipt')` و `sum(quantity for type == 'issue')`

**URL**: `/inventory/balance/details/<item_id>/<warehouse_id>/`

---

## InventoryBalanceAPIView

**Type**: `InventoryBaseView, TemplateView`

**Method**: `GET`

**Query Parameters**:
- `warehouse_id`: شناسه انبار (required)
- `item_id`: شناسه کالا (required)
- `as_of_date`: تاریخ محاسبه (optional)

**متدها**:

#### `get(self, request, *args, **kwargs) -> JsonResponse`

**توضیح**: API endpoint برای محاسبه موجودی یک کالا در انبار.

**Response (Success)**:
```json
{
  "baseline_quantity": 100.0,
  "current_balance": 150.0,
  "baseline_date": "2024-01-01",
  ...
}
```

**Response (Error)**:
```json
{
  "error": "error message"
}
```

**منطق**:
1. بررسی required parameters
2. Parse کردن تاریخ
3. محاسبه موجودی با `calculate_item_balance()`
4. بازگشت JSON response

**URL**: `/inventory/balance/api/`

---

## نکات مهم

### 1. Date Parsing
- پشتیبانی از هر دو format: Gregorian (YYYY-MM-DD) و Jalali (YYYY/MM/DD)
- در صورت خطا، از `date.today()` استفاده می‌شود

### 2. Baseline Calculation
- Baseline از آخرین انبارگردانی محاسبه می‌شود
- تمام تراکنش‌ها از baseline_date تا as_of_date در نظر گرفته می‌شوند

### 3. Transaction Types
- **Receipts**: Permanent, Consignment
- **Issues**: Permanent, Consumption, Consignment
- **Stocktaking Surplus**: Positive movements (quantity_adjusted)
- **Stocktaking Deficit**: Negative movements (quantity_adjusted)

**Transaction Structure**:
- `date`: تاریخ تراکنش
- `type`: `'receipt'` یا `'issue'`
- `type_label`: نام فارسی نوع تراکنش
- `document_code`: کد سند
- `document_id`: شناسه سند
- `document_type`: نوع سند (permanent_receipt, consignment_receipt, permanent_issue, consumption_issue, consignment_issue, stocktaking_surplus, stocktaking_deficit)
- `quantity`: مقدار
- `unit`: واحد
- `created_by`: نام کاربر ایجادکننده
- `source_destination`: منبع/مقصد (supplier name برای receipts، department unit/work line name برای issues)
- `running_balance`: موجودی پس از این تراکنش

### 4. Running Balance
- برای هر تراکنش، running balance محاسبه می‌شود
- Receipts: `running_balance += quantity`
- Issues: `running_balance -= quantity`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Date Handling**: پشتیبانی از هر دو format تاریخ
3. **Error Handling**: خطاها در context یا JSON response نمایش داده می‌شوند

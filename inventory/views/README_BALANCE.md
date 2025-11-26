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
- `item`: کالا
- `warehouse`: انبار
- `baseline`: اطلاعات baseline از آخرین انبارگردانی
- `baseline_date`: تاریخ baseline
- `as_of_date`: تاریخ محاسبه
- `transactions`: لیست تراکنش‌ها (receipts و issues)
- `total_receipts`: مجموع receipts
- `total_issues`: مجموع issues
- `current_balance`: موجودی فعلی
- `error`: پیام خطا (در صورت وجود)

**منطق**:
1. دریافت baseline از آخرین انبارگردانی
2. دریافت تمام receipts (Permanent, Consignment)
3. دریافت تمام issues (Permanent, Consumption, Consignment)
4. ترکیب و مرتب‌سازی تراکنش‌ها بر اساس تاریخ
5. محاسبه running balance برای هر تراکنش
6. محاسبه موجودی فعلی

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

### 4. Running Balance
- برای هر تراکنش، running balance محاسبه می‌شود
- Receipts: `running_balance += quantity`
- Issues: `running_balance -= quantity`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Date Handling**: پشتیبانی از هر دو format تاریخ
3. **Error Handling**: خطاها در context یا JSON response نمایش داده می‌شوند

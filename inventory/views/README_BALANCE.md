# inventory/views/balance.py - Inventory Balance Views

**هدف**: Views برای نمایش و محاسبه موجودی انبار

این فایل شامل views برای:
- Inventory Balance List (فهرست موجودی)
- Inventory Balance Details (جزئیات موجودی)
- Inventory Balance API (API endpoint)

---

## Views

### `InventoryBalanceView`

**توضیح**: صفحه اصلی محاسبه و نمایش موجودی انبار

**Type**: `InventoryBaseView, TemplateView`

**Template**: `inventory/inventory_balance.html`

**Context Variables**:
- `warehouses`: لیست انبارها
- `item_types`: لیست انواع کالا
- `balances`: لیست موجودی‌ها (از `calculate_warehouse_balances()`)

**فیلترها**:
- `warehouse_id`: فیلتر بر اساس انبار
- `item_type_id`: فیلتر بر اساس نوع کالا
- `item_category_id`: فیلتر بر اساس دسته کالا
- `as_of_date`: تاریخ محاسبه

**URL**: `/inventory/balance/`

---

### `InventoryBalanceDetailsView`

**توضیح**: نمایش تاریخچه کامل تراکنش‌ها برای یک کالای خاص در یک انبار

**Type**: `InventoryBaseView, TemplateView`

**Template**: `inventory/inventory_balance_details.html`

**Context Variables**:
- `item`: شیء کالا
- `warehouse`: شیء انبار
- `balance`: اطلاعات موجودی (از `calculate_item_balance()`)
- `transactions`: لیست تمام تراکنش‌ها (رسیدها و حواله‌ها)

**Query Parameters**:
- `item_id` (required): شناسه کالا
- `warehouse_id` (required): شناسه انبار
- `as_of_date` (optional): تاریخ محاسبه

**URL**: `/inventory/balance/details/?item_id=<id>&warehouse_id=<id>&as_of_date=<date>`

---

### `InventoryBalanceAPIView`

**توضیح**: JSON API endpoint برای دسترسی برنامه‌نویسی به موجودی

**Type**: `InventoryBaseView, TemplateView`

**منطق**: JSON response با اطلاعات موجودی برمی‌گرداند

**Query Parameters**:
- `warehouse_id` (required): شناسه انبار
- `item_id` (required): شناسه کالا
- `as_of_date` (optional): تاریخ محاسبه

**Response Format**:
```json
{
  "company_code": "C001",
  "warehouse_code": "WH01",
  "item_code": "001-002-003-0001",
  "item_name": "Sample Item",
  "baseline_date": "2025-10-15",
  "baseline_quantity": 1000.0,
  "receipts_total": 250.0,
  "issues_total": 180.0,
  "current_balance": 1070.0,
  "last_calculated_at": "2025-11-09T10:30:00Z"
}
```

**URL**: `/inventory/api/balance/`

---

## وابستگی‌ها

- `inventory.inventory_balance`: `calculate_warehouse_balances()`, `calculate_item_balance()`
- `inventory.models`: تمام مدل‌های inventory

---

## نکات مهم

1. **On-demand Calculation**: موجودی به صورت on-demand محاسبه می‌شود
2. **Performance**: برای انبارهای بزرگ، محاسبه می‌تواند CPU-intensive باشد
3. **Date Filtering**: می‌توان موجودی را در تاریخ خاص محاسبه کرد


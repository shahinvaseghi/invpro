# inventory/inventory_balance.py - Inventory Balance Calculation Module

**هدف**: محاسبه موجودی انبار به صورت on-demand بر اساس آخرین شمارش و اسناد قفل شده بعد از آن

این ماژول موجودی را به صورت دینامیک محاسبه می‌کند تا دقت را تضمین کند و ممیزی را ساده‌تر کند.

---

## فرمول محاسبه موجودی

```
موجودی فعلی = Baseline (از آخرین شمارش)
            + رسیدها (دائم + مازاد)
            - حواله‌ها (دائم + مصرف + کسری)
```

---

## توابع

### `get_last_stocktaking_baseline(company_id, warehouse_id, item_id, as_of_date=None) -> Dict`

**توضیح**: Baseline موجودی را از آخرین سند شمارش تایید شده برمی‌گرداند.

**پارامترهای ورودی**:
- `company_id` (int): شناسه شرکت
- `warehouse_id` (int): شناسه انبار
- `item_id` (int): شناسه کالا
- `as_of_date` (Optional[date], default=None): تاریخ محاسبه baseline (اگر None باشد، امروز استفاده می‌شود)

**مقدار بازگشتی**:
```python
{
    'baseline_date': date or None,          # تاریخ baseline (date(1900, 1, 1) اگر StocktakingRecord پیدا شود، تاریخ اولین کسری/مازاد در غیر این صورت، یا None)
    'baseline_quantity': Decimal,            # همیشه 0 (تمام حرکات بعد از baseline محاسبه می‌شوند)
    'stocktaking_record_id': int or None,   # شناسه سند شمارش (اگر پیدا شود)
    'stocktaking_record_code': str or None,  # کد سند شمارش (اگر پیدا شود)
    'stocktaking_record_date': date or None  # تاریخ واقعی سند شمارش (اگر پیدا شود، برای مرجع)
}
```

**مثال استفاده**:
```python
from inventory.inventory_balance import get_last_stocktaking_baseline
from datetime import date

baseline = get_last_stocktaking_baseline(
    company_id=1,
    warehouse_id=5,
    item_id=123,
    as_of_date=date(2025, 11, 9)
)
# نتیجه: {'baseline_date': date(2025, 10, 15), 'baseline_quantity': Decimal('1000.0'), ...}
```

**منطق**:
1. ابتدا آخرین سند `StocktakingRecord` تایید شده و قفل شده قبل از `as_of_date` را پیدا می‌کند
   - اگر پیدا شود: `baseline_date=date(1900, 1, 1)` (شروع از ابتدا برای شامل کردن تمام حرکات) و `baseline_quantity=0` برمی‌گرداند
   - همچنین `stocktaking_record_id` و `stocktaking_record_code` را برای مرجع شامل می‌کند
   - تاریخ واقعی سند شمارش در `stocktaking_record_date` ذخیره می‌شود
2. اگر `StocktakingRecord` پیدا نشود، اولین اسناد کسری/مازاد قبل از `as_of_date` را بررسی می‌کند
   - اگر پیدا شود: از تاریخ اولین سند کسری/مازاد به عنوان `baseline_date` استفاده می‌کند، `baseline_quantity=0`
   - اسناد کسری/مازاد به عنوان حرکات بعد از این baseline محاسبه می‌شوند
3. اگر هیچ سند شمارشی وجود نداشته باشد: `baseline_date=None` و `baseline_quantity=0` برمی‌گرداند

**نکته مهم**: مقدار baseline همیشه `0` است زیرا تمام حرکات (شامل کسری/مازاد) به عنوان حرکات بعد از تاریخ baseline محاسبه می‌شوند. این امر یک audit trail کامل را تضمین می‌کند.

---

### `calculate_movements_after_baseline(company_id, warehouse_id, item_id, baseline_date, as_of_date=None) -> Dict`

**توضیح**: تمام حرکات موجودی (رسیدها و حواله‌ها) که بعد از تاریخ baseline رخ داده‌اند را محاسبه می‌کند.

**پارامترهای ورودی**:
- `company_id` (int): شناسه شرکت
- `warehouse_id` (int): شناسه انبار
- `item_id` (int): شناسه کالا
- `baseline_date` (Optional[date]): تاریخ شروع محاسبه حرکات
- `as_of_date` (Optional[date], default=None): تاریخ پایان (اگر None باشد، امروز استفاده می‌شود)

**مقدار بازگشتی**:
```python
{
    'receipts_total': Decimal,     # مجموع رسیدهای دائم + امانی + مازاد
    'issues_total': Decimal,       # مجموع حواله‌های دائم + مصرف + امانی + کسری
    'surplus_total': Decimal,      # فقط مازاد
    'deficit_total': Decimal       # فقط کسری
}
```

**مثال استفاده**:
```python
from inventory.inventory_balance import calculate_movements_after_baseline
from datetime import date

movements = calculate_movements_after_baseline(
    company_id=1,
    warehouse_id=5,
    item_id=123,
    baseline_date=date(2025, 10, 15),
    as_of_date=date(2025, 11, 9)
)
# نتیجه: {'receipts_total': Decimal('250.0'), 'issues_total': Decimal('180.0'), ...}
```

**نکات مهم**:
- رسیدها و حواله‌ها: فقط اسناد فعال (`is_enabled=1`) شامل می‌شوند
- شمارش (کسری/مازاد): هم `is_locked=1` و هم `is_enabled=1` لازم است
- رسیدهای امانی و حواله‌های امانی شامل می‌شوند (بر موجودی تأثیر می‌گذارند)
- رسیدهای موقت شامل نمی‌شوند (در کوئری‌ها وجود ندارند)
- مدیریت تاریخ: به صورت خودکار تاریخ‌های رشته‌ای را به date object تبدیل می‌کند، اگر `baseline_date` None باشد، از `date(1900, 1, 1)` استفاده می‌کند

---

### `calculate_item_balance(company_id, warehouse_id, item_id, as_of_date=None) -> Dict`

**توضیح**: موجودی کامل برای یک کالای خاص در یک انبار را محاسبه می‌کند.

**پارامترهای ورودی**:
- `company_id` (int): شناسه شرکت
- `warehouse_id` (int): شناسه انبار
- `item_id` (int): شناسه کالا
- `as_of_date` (Optional[date], default=None): تاریخ محاسبه (اگر None باشد، امروز استفاده می‌شود)

**مقدار بازگشتی**:
```python
{
    'company_id': int,
    'company_code': str,
    'warehouse_id': int,
    'warehouse_code': str,
    'warehouse_name': str,
    'item_id': int,
    'item_code': str,
    'item_name': str,
    'baseline_date': str (ISO format) or None,
    'baseline_quantity': float,
    'stocktaking_record_id': int or None,
    'stocktaking_record_code': str or None,
    'receipts_total': float,
    'issues_total': float,
    'surplus_total': float,
    'deficit_total': float,
    'current_balance': float,           # موجودی نهایی محاسبه شده
    'as_of_date': str (ISO format),
    'last_calculated_at': str (ISO timestamp)
}
```

**مثال استفاده**:
```python
from inventory.inventory_balance import calculate_item_balance
from datetime import date

balance = calculate_item_balance(
    company_id=1,
    warehouse_id=5,
    item_id=123,
    as_of_date=date(2025, 11, 9)
)
# نتیجه: {'item_code': '001002003010001', 'current_balance': 1070.0, ...}
```

**منطق**:
1. جزئیات کالا و انبار را دریافت می‌کند
2. Baseline را از `get_last_stocktaking_baseline()` دریافت می‌کند
3. حرکات را از `calculate_movements_after_baseline()` محاسبه می‌کند
4. محاسبه می‌کند: `current_balance = baseline + receipts - issues`
5. اطلاعات جامع موجودی را فرمت و برمی‌گرداند

---

### `calculate_warehouse_balances(company_id, warehouse_id, as_of_date=None, item_type_id=None, item_category_id=None) -> List[Dict]`

**توضیح**: موجودی تمام کالاها در یک انبار را محاسبه می‌کند (محاسبه bulk).

**پارامترهای ورودی**:
- `company_id` (int): شناسه شرکت
- `warehouse_id` (int): شناسه انبار
- `as_of_date` (Optional[date], default=None): تاریخ محاسبه
- `item_type_id` (Optional[int], default=None): فیلتر بر اساس نوع کالا
- `item_category_id` (Optional[int], default=None): فیلتر بر اساس دسته کالا

**مقدار بازگشتی**:
- `List[Dict]`: لیستی از دیکشنری‌های موجودی (هر کدام همان فرمت `calculate_item_balance()`)

**مثال استفاده**:
```python
from inventory.inventory_balance import calculate_warehouse_balances
from datetime import date

balances = calculate_warehouse_balances(
    company_id=1,
    warehouse_id=5,
    as_of_date=date(2025, 11, 9),
    item_type_id=2  # فقط کالاهای نوع 2
)
# نتیجه: [{item 1 balance}, {item 2 balance}, ...]
```

**منطق**:
1. تمام کالاهایی که فعالیت در انبار دارند را پیدا می‌کند:
   - کالاهایی با تخصیص انبار (`ItemWarehouse` که `warehouse_id` مطابقت دارد و `is_enabled=1`), یا
   - کالاهایی با تراکنش واقعی:
     * `ReceiptPermanentLine` (فقط اسناد فعال)
     * `ReceiptConsignmentLine` (فقط اسناد فعال)
     * `IssuePermanentLine` (فقط اسناد فعال)
     * `IssueConsumptionLine` (فقط اسناد فعال)
     * `IssueConsignmentLine` (فقط اسناد فعال)
     * `StocktakingSurplusLine` (فقط اسناد فعال)
     * `StocktakingDeficitLine` (فقط اسناد فعال)
2. **نکته مهم**: کالاهایی با تراکنش واقعی حتی اگر `is_enabled=0` باشند، شامل می‌شوند
   - این امر یک audit trail کامل را تضمین می‌کند
   - کالاهایی که فقط تخصیص انبار دارند، باید `is_enabled=1` باشند
3. فیلترهای اختیاری را اعمال می‌کند (`item_type_id`, `item_category_id`)
4. برای هر کالا `calculate_item_balance()` را فراخوانی می‌کند
5. **فیلتر کردن**: فقط کالاهایی که:
   - `current_balance != 0`, یا
   - `receipts_total > 0`, یا
   - `issues_total > 0`
   - این کالاهایی با موجودی صفر و بدون فعالیت را حذف می‌کند
6. مدیریت خطا: اگر محاسبه برای یک کالا ناموفق باشد، خطا را ثبت می‌کند و با کالاهای دیگر ادامه می‌دهد
7. لیست موجودی‌ها را برمی‌گرداند

---

### `get_low_stock_items(company_id, warehouse_id=None, threshold_quantity=None) -> List[Dict]`

**توضیح**: کالاهایی با موجودی زیر آستانه را شناسایی می‌کند (low stock alerts).

**وضعیت**: Placeholder function - هنوز پیاده‌سازی نشده است

**پارامترهای برنامه‌ریزی شده**:
- `company_id` (int): شناسه شرکت
- `warehouse_id` (Optional[int], default=None): شناسه انبار (یا تمام انبارها)
- `threshold_quantity` (Decimal): حداقل مقدار قابل قبول

**منطق برنامه‌ریزی شده**:
1. موجودی تمام کالاها را محاسبه می‌کند
2. کالاهایی که `current_balance < threshold_quantity` دارند را فیلتر می‌کند
3. لیست کالاهای low stock را با سطح هشدار برمی‌گرداند

---

## استفاده در Views

### InventoryBalanceView

**Template**: `templates/inventory/inventory_balance.html`

**جریان کار**:
1. کاربر انبار، نوع کالا، دسته و تاریخ را از طریق فرم فیلتر انتخاب می‌کند
2. View `calculate_warehouse_balances()` را با فیلترها فراخوانی می‌کند
3. نتایج در جدول داده نمایش داده می‌شوند:
   - کد و نام کالا
   - تاریخ و مقدار baseline
   - مجموع رسیدها و حواله‌ها
   - موجودی فعلی (رنگ‌بندی: قرمز برای منفی، سبز برای مثبت)
4. قابلیت export به Excel موجود است

**URL**: `/inventory/balance/`

---

### InventoryBalanceDetailsView

**Template**: `templates/inventory/inventory_balance_details.html`

**هدف**: نمایش تاریخچه کامل تراکنش‌ها برای یک کالای خاص در یک انبار

**ویژگی‌ها**:
- نمایش تمام رسیدها و حواله‌ها از تاریخ baseline تا تاریخ انتخاب شده
- نمایش محاسبه موجودی running برای هر تراکنش
- ستون منبع/مقصد:
  - برای رسیدها: نام تامین‌کننده
  - برای حواله‌ها: نام واحد سازمانی یا خط کاری
- کدهای سند قابل کلیک (لینک به صفحه ویرایش/مشاهده)

**URL**: `/inventory/balance/details/<item_id>/<warehouse_id>/?as_of_date=YYYY-MM-DD`

---

### InventoryBalanceAPIView

**هدف**: JSON API endpoint برای دسترسی برنامه‌نویسی

**URL**: `/inventory/api/balance/`

**پارامترها** (GET):
- `warehouse_id` (required)
- `item_id` (required)
- `as_of_date` (optional, ISO format)

**Response**:
```json
{
  "company_code": "C001",
  "warehouse_code": "WH01",
  "item_code": "001002003010001",
  "item_name": "Sample Item",
  "baseline_date": "2025-10-15",
  "baseline_quantity": 1000.0,
  "receipts_total": 250.0,
  "issues_total": 180.0,
  "current_balance": 1070.0,
  "last_calculated_at": "2025-11-09T10:30:00Z"
}
```

---

## بهینه‌سازی عملکرد

### Indexes پیشنهادی

```sql
-- اسناد رسید
CREATE INDEX idx_receipt_perm_company_wh_item_date 
ON inventory_receipt_permanent_line(company_id, warehouse_id, item_id, document__document_date, document__is_enabled);

-- اسناد حواله
CREATE INDEX idx_issue_perm_company_wh_item_date 
ON inventory_issue_permanent_line(company_id, warehouse_id, item_id, document__document_date, document__is_enabled);

-- شمارش
CREATE INDEX idx_stocktaking_def_company_wh_item_date 
ON inventory_stocktaking_deficit(company_id, warehouse_id, item_id, document_date, is_locked);
```

---

## وابستگی‌ها

- `django.db.models`: برای aggregation queries
- `django.utils.timezone`: برای تاریخ‌های دقیق
- `decimal.Decimal`: برای محاسبات دقیق مقدار
- `inventory.models`: برای تمام مدل‌های inventory

---

## استفاده در پروژه

این توابع در views و API endpoints استفاده می‌شوند:
- `inventory/views/balance.py`: برای نمایش موجودی
- API endpoints: برای دسترسی برنامه‌نویسی

---

## نکات مهم

1. **On-demand Calculation**: موجودی به صورت on-demand محاسبه می‌شود (هیچ جدول pre-computed وجود ندارد)
2. **Only Locked Documents**: فقط اسناد قفل شده (`is_locked=1`) در محاسبه استفاده می‌شوند
3. **Consignment Handling**: رسیدها و حواله‌های امانی در محاسبه استفاده می‌شوند
4. **Performance**: برای انبارهای بزرگ (100+ کالا)، محاسبه می‌تواند CPU-intensive باشد
5. **Caching**: در حال حاضر هیچ caching وجود ندارد (هر بار fresh محاسبه می‌شود)

---

## خطاها و استثناها

- **Missing stocktaking**: اگر شمارشی پیدا نشود، `baseline_quantity=0` برمی‌گرداند
- **Item not found**: `Item.DoesNotExist` را raise می‌کند
- **Warehouse not found**: `Warehouse.DoesNotExist` را raise می‌کند
- **Invalid dates**: `ValueError` را catch می‌کند و از default (امروز) استفاده می‌کند

---

## بهبودهای آینده

1. **Real-time updates**: WebSocket notifications هنگام تغییر موجودی
2. **Low stock alerts**: اعلان‌های خودکار هنگام رسیدن به آستانه
3. **Forecast**: پیش‌بینی موجودی آینده بر اساس روندهای تاریخی
4. **Multi-warehouse**: محاسبه موجودی کل در تمام انبارها
5. **Lot-level balances**: ردیابی موجودی در سطح lot code برای کالاهای قابل ردیابی
6. **Valuation**: شامل داده‌های هزینه/قیمت برای گزارش‌های مالی


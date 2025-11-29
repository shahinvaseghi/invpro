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
1. اگر `as_of_date` None باشد: `as_of_date = timezone.now().date()`
2. جستجوی آخرین `StocktakingRecord`:
   - Query: `StocktakingRecord.objects.filter(company_id=company_id, document_date__lte=as_of_date, approval_status='approved', is_locked=1, is_enabled=1).order_by('-document_date', '-id').first()`
   - اگر پیدا شود:
     - `baseline_date = date(1900, 1, 1)` (شروع از ابتدا برای شامل کردن تمام movements)
     - `baseline_quantity = Decimal('0')` (همیشه 0 - تمام movements بعد از baseline محاسبه می‌شوند)
     - `stocktaking_record_id = latest_record.id`
     - `stocktaking_record_code = latest_record.document_code`
     - `stocktaking_record_date = latest_record.document_date` (تاریخ واقعی stocktaking برای reference)
   - اگر پیدا نشد:
     - `baseline_date = None`
     - `baseline_quantity = Decimal('0')`
     - `stocktaking_record_id = None`
     - **نکته**: Deficit/surplus documents فقط اگر StocktakingRecord وجود داشته باشد به عنوان movements محاسبه می‌شوند

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

**منطق**:
1. اگر `as_of_date` None باشد: `as_of_date = timezone.now().date()`
2. **Date handling برای as_of_date**:
   - اگر `isinstance(as_of_date, date)` نیست:
     - اگر string باشد: `date.fromisoformat(as_of_date)`
     - در غیر این صورت: `timezone.now().date()`
     - اگر exception رخ دهد: `timezone.now().date()`
3. **Date handling برای baseline_date**:
   - اگر `baseline_date` None باشد: `baseline_date = date(1900, 1, 1)`
   - اگر `isinstance(baseline_date, date)` نیست:
     - اگر string باشد: `date.fromisoformat(baseline_date)`
     - در غیر این صورت: `date(1900, 1, 1)`
     - اگر exception رخ دهد: `date(1900, 1, 1)`
4. **محاسبه Receipts** (positive movements):
   - `ReceiptPermanentLine`: `filter(company_id, warehouse_id, item_id, document__document_date__gte=baseline_date, document__document_date__lte=as_of_date, document__is_enabled=1).aggregate(total=Sum('quantity'))`
   - `ReceiptConsignmentLine`: مشابه بالا
   - `StocktakingSurplusLine`: `filter(company_id, warehouse_id, item_id, document__document_date__gte=baseline_date, document__document_date__lte=as_of_date, document__is_locked=1, document__is_enabled=1).aggregate(total=Sum('quantity_adjusted'))`
   - `receipts_total = (receipts_perm['total'] or Decimal('0')) + (receipts_consignment['total'] or Decimal('0')) + (surplus['total'] or Decimal('0'))`
5. **محاسبه Issues** (negative movements):
   - `IssuePermanentLine`: `filter(company_id, warehouse_id, item_id, document__document_date__gte=baseline_date, document__document_date__lte=as_of_date, document__is_enabled=1).aggregate(total=Sum('quantity'))`
   - `IssueConsumptionLine`: مشابه بالا
   - `IssueConsignmentLine`: مشابه بالا
   - `StocktakingDeficitLine`: `filter(company_id, warehouse_id, item_id, document__document_date__gte=baseline_date, document__document_date__lte=as_of_date, document__is_locked=1, document__is_enabled=1).aggregate(total=Sum('quantity_adjusted'))`
   - `issues_total = (issues_permanent['total'] or Decimal('0')) + (issues_consumption['total'] or Decimal('0')) + (issues_consignment['total'] or Decimal('0')) + (deficit['total'] or Decimal('0'))`
6. بازگشت: `{'receipts_total': Decimal, 'issues_total': Decimal, 'surplus_total': Decimal, 'deficit_total': Decimal}`

**نکات مهم**:
- Receipts and Issues: Only enabled documents are included (`document__is_enabled=1`)
- Stocktaking (Deficit/Surplus): Both `document__is_locked=1` AND `document__is_enabled=1` are required
- Consignment receipts/issues ARE included (they affect inventory balance)
- Temporary receipts are excluded (not included in the queries)
- Date range: `document__document_date__gte=baseline_date` AND `document__document_date__lte=as_of_date`

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
1. اگر `as_of_date` None باشد: `as_of_date = timezone.now().date()`
2. **یافتن items با activity در warehouse**:
   - **Items با warehouse assignment**: `Item.objects.filter(company_id=company_id, is_enabled=1, warehouses__warehouse_id=warehouse_id, warehouses__is_enabled=1).values_list('id', flat=True)`
   - **Items با actual transactions** (فقط enabled documents و `document_date__lte=as_of_date`):
     * `ReceiptPermanentLine`: `filter(company_id, warehouse_id, document__is_enabled=1, document__document_date__lte=as_of_date).values_list('item_id', flat=True).distinct()`
     * `ReceiptConsignmentLine`: مشابه بالا
     * `IssuePermanentLine`: مشابه بالا
     * `IssueConsumptionLine`: مشابه بالا
     * `IssueConsignmentLine`: مشابه بالا
     * `StocktakingSurplusLine`: مشابه بالا (فقط `document__is_enabled=1`)
     * `StocktakingDeficitLine`: مشابه بالا (فقط `document__is_enabled=1`)
3. **ترکیب item IDs**:
   - `all_item_ids = set(items_with_assignment) | set(items_with_receipts) | set(items_with_consignment_receipts) | set(items_with_issues) | set(items_with_consumption) | set(items_with_consignment_issues) | set(items_with_surplus) | set(items_with_deficit)`
   - `items_with_transactions = set(items_with_receipts) | set(items_with_consignment_receipts) | set(items_with_issues) | set(items_with_consumption) | set(items_with_consignment_issues) | set(items_with_surplus) | set(items_with_deficit)`
4. **ساخت query**:
   - `items_query = Item.objects.filter(id__in=all_item_ids, company_id=company_id).filter(Q(id__in=items_with_transactions) | Q(is_enabled=1))`
   - **نکته مهم**: Items با actual transactions حتی اگر disabled باشند (`is_enabled=0`) شامل می‌شوند (برای audit trail)
   - Items با فقط warehouse assignment نیاز به `is_enabled=1` دارند
5. **اعمال optional filters**:
   - اگر `item_type_id` موجود باشد: `items_query = items_query.filter(type_id=item_type_id)`
   - اگر `item_category_id` موجود باشد: `items_query = items_query.filter(category_id=item_category_id)`
6. **محاسبه balance برای هر item**:
   - برای هر item در `items_query`:
     - فراخوانی `calculate_item_balance(company_id, warehouse_id, item.id, as_of_date)`
     - **فیلتر کردن**: فقط items با:
       * `current_balance != 0`، یا
       * `receipts_total > 0`، یا
       * `issues_total > 0`
     - اضافه کردن به `balances` list
     - **Error handling**: اگر exception رخ دهد:
       * Log error با `print()` و `traceback.format_exc()`
       * ادامه با item بعدی (`continue`)
7. بازگشت `balances` list

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


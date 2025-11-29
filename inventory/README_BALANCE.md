# Inventory Balance Calculation Module

## Overview

The `inventory_balance.py` module provides on-demand inventory balance calculations based on stocktaking baselines and subsequent document movements. Unlike traditional inventory systems that maintain running balance tables, this implementation calculates balances dynamically to ensure accuracy and simplify auditing.

## Core Concept

**Balance Formula**:
```
Current Balance = Baseline (from last stocktaking)
                + Receipts (permanent + surplus)
                - Issues (permanent + consumption + deficit)
```

## Module Location

`inventory/inventory_balance.py`

## Functions

### 1. `get_last_stocktaking_baseline()`

**Purpose**: Retrieve the baseline inventory quantity from the most recent approved stocktaking record.

**Parameters**:
- `company_id` (int): Company ID for multi-tenant filtering
- `warehouse_id` (int): Warehouse to check
- `item_id` (int): Item to check
- `as_of_date` (date, optional): Calculate baseline as of this date (default: today)

**Returns**:
```python
{
    'baseline_date': date or None,          # date(1900, 1, 1) if stocktaking found, None otherwise
    'baseline_quantity': Decimal('0'),      # Always 0 (all movements calculated after baseline)
    'stocktaking_record_id': int or None,   # Reference to stocktaking record
    'stocktaking_record_code': str or None, # Human-readable code
    'stocktaking_record_date': date or None # Actual stocktaking record date (for reference)
}
```

**Logic**:
1. اگر `as_of_date` None باشد: `as_of_date = timezone.now().date()`
2. جستجوی آخرین `StocktakingRecord`:
   - Query: `StocktakingRecord.objects.filter(company_id=company_id, document_date__lte=as_of_date, approval_status='approved', is_locked=1, is_enabled=1).order_by('-document_date', '-id').first()`
   - اگر پیدا شد:
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

**Important**: The baseline quantity is always `0` because all movements (including deficit/surplus) are calculated as movements after the baseline date. This ensures a complete audit trail.

**Example**:
```python
baseline = get_last_stocktaking_baseline(
    company_id=1,
    warehouse_id=5,
    item_id=123,
    as_of_date=date(2025, 11, 9)
)
# Returns: {'baseline_date': date(2025, 10, 15), 'baseline_quantity': Decimal('1000.0'), ...}
```

---

### 2. `calculate_movements_after_baseline()`

**Purpose**: Calculate all inventory movements (receipts and issues) that occurred after the baseline date.

**Parameters**:
- `company_id` (int): Company ID
- `warehouse_id` (int): Warehouse
- `item_id` (int): Item
- `baseline_date` (date or None): Start date for movement calculation
- `as_of_date` (date, optional): End date (default: today)

**Returns**:
```python
{
    'receipts_total': Decimal,     # Sum of permanent receipts + surplus
    'issues_total': Decimal,       # Sum of permanent + consumption issues + deficit
    'surplus_total': Decimal,      # Surplus adjustments only
    'deficit_total': Decimal        # Deficit adjustments only
}
```

**Queries**:
- `ReceiptPermanentLine` where `document__is_enabled=1` and `document_date` in range
- `ReceiptConsignmentLine` where `document__is_enabled=1` and `document_date` in range
- `StocktakingSurplusLine` where `document__is_locked=1` and `document__is_enabled=1` and `document_date` in range
- `IssuePermanentLine` where `document__is_enabled=1` and `document_date` in range
- `IssueConsumptionLine` where `document__is_enabled=1` and `document_date` in range
- `IssueConsignmentLine` where `document__is_enabled=1` and `document_date` in range
- `StocktakingDeficitLine` where `document__is_locked=1` and `document__is_enabled=1` and `document_date` in range

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

**Important Notes**:
- Receipts and Issues: Only enabled documents are included (`document__is_enabled=1`)
- Stocktaking (Deficit/Surplus): Both `document__is_locked=1` AND `document__is_enabled=1` are required
- Consignment receipts/issues ARE included (they affect inventory balance)
- Temporary receipts are excluded (not included in the queries)
- Date range: `document__document_date__gte=baseline_date` AND `document__document_date__lte=as_of_date`

**Example**:
```python
movements = calculate_movements_after_baseline(
    company_id=1,
    warehouse_id=5,
    item_id=123,
    baseline_date=date(2025, 10, 15),
    as_of_date=date(2025, 11, 9)
)
# Returns: {'receipts_total': Decimal('250.0'), 'issues_total': Decimal('180.0'), ...}
```

---

### 3. `calculate_item_balance()`

**Purpose**: Calculate complete inventory balance for a specific item in a warehouse.

**Parameters**:
- `company_id` (int): Company ID
- `warehouse_id` (int): Warehouse ID
- `item_id` (int): Item ID
- `as_of_date` (date, optional): Calculate balance as of this date (default: today)

**Returns**:
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
    'current_balance': float,           # Calculated final balance
    'as_of_date': str (ISO format),
    'last_calculated_at': str (ISO timestamp)
}
```

**Logic**:
1. Retrieve item and warehouse details
2. Get baseline from `get_last_stocktaking_baseline()`
3. Calculate movements from `calculate_movements_after_baseline()`
4. Compute: `current_balance = baseline + receipts - issues`
5. Format and return comprehensive balance information

**Use Cases**:
- Display balance for single item
- API endpoint for real-time balance check
- Audit reports for specific items

**Example**:
```python
balance = calculate_item_balance(
    company_id=1,
    warehouse_id=5,
    item_id=123,
    as_of_date=date(2025, 11, 9)
)
# Returns: {'item_code': '001002003010001', 'current_balance': 1070.0, ...}
```

---

### 4. `calculate_warehouse_balances()`

**Purpose**: Calculate balances for all items in a warehouse (bulk calculation).

**Parameters**:
- `company_id` (int): Company ID
- `warehouse_id` (int): Warehouse ID
- `as_of_date` (date, optional): Calculate balances as of this date (default: today)
- `item_type_id` (int, optional): Filter by item type
- `item_category_id` (int, optional): Filter by item category

**Returns**:
```python
[
    {balance_dict_1},
    {balance_dict_2},
    ...
]
```
(Each dict is same format as `calculate_item_balance()`)

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

**Performance**:
- Runs one query per item (N+1 pattern)
- Consider caching for frequently accessed warehouses
- Use filters to reduce item count

**Use Cases**:
- Warehouse inventory dashboard
- Periodic inventory reports
- Export to Excel for offline analysis

**Example**:
```python
balances = calculate_warehouse_balances(
    company_id=1,
    warehouse_id=5,
    as_of_date=date(2025, 11, 9),
    item_type_id=2  # Optional filter
)
# Returns: [{item 1 balance}, {item 2 balance}, ...]
```

---

### 5. `get_low_stock_items()` (TODO)

**Purpose**: Identify items with balances below a threshold (low stock alerts).

**Status**: Placeholder function - not yet implemented

**Planned Parameters**:
- `company_id` (int): Company ID
- `warehouse_id` (int, optional): Warehouse to check (or all warehouses)
- `threshold_quantity` (Decimal): Minimum acceptable quantity

**Planned Logic**:
1. Calculate balances for all items
2. Filter where `current_balance < threshold_quantity`
3. Return list of low-stock items with alert level

---

## Integration with Views

### InventoryBalanceView

Template: `templates/inventory/inventory_balance.html`

**Flow**:
1. User selects warehouse, item type, category, and date via filter form
2. View calls `calculate_warehouse_balances()` with filters
3. Results displayed in data table with:
   - Item code and name
   - Baseline date and quantity
   - Receipts and issues totals
   - Current balance (color-coded: red if negative, green if positive)
4. Export to Excel functionality available

**URL**: `/inventory/balance/`

---

### InventoryBalanceDetailsView

Template: `templates/inventory/inventory_balance_details.html`

**Purpose**: Display detailed transaction history for a specific item in a warehouse.

**Features**:
- Shows all receipts and issues from baseline date to selected date
- Displays running balance calculation for each transaction
- **Source/Destination Column**: 
  - For receipts: Shows supplier name (from line item's `supplier` field)
  - For issues: Shows department unit name or work line name (for consumption issues)
  - Only displays names, not codes, for better readability
- **Clickable Document Codes**: 
  - All document codes are clickable links
  - Links navigate directly to the document edit/view page
  - Styled with blue color and hover effects
- Transaction types displayed:
  - Permanent Receipt (رسید دائم)
  - Consignment Receipt (رسید امانی)
  - Permanent Issue (حواله دائم)
  - Consumption Issue (حواله مصرف)
  - Consignment Issue (حواله امانی)

**URL**: `/inventory/balance/details/<item_id>/<warehouse_id>/?as_of_date=YYYY-MM-DD`

**Access**: Via "Details" button in inventory balance list view

---

### InventoryBalanceAPIView

**Purpose**: JSON API endpoint for programmatic access

**URL**: `/inventory/api/balance/`

**Parameters** (GET):
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

## Database Indexes

For optimal performance, ensure these indexes exist:

```sql
-- Receipt documents
CREATE INDEX idx_receipt_perm_company_wh_item_date 
ON inventory_receipt_permanent(company_id, warehouse_id, item_id, document_date, is_locked);

-- Issue documents
CREATE INDEX idx_issue_perm_company_wh_item_date 
ON inventory_issue_permanent(company_id, warehouse_id, item_id, document_date, is_locked);

CREATE INDEX idx_issue_cons_company_wh_item_date 
ON inventory_issue_consumption(company_id, warehouse_id, item_id, document_date, is_locked);

-- Stocktaking
CREATE INDEX idx_stocktaking_def_company_wh_item_date 
ON inventory_stocktaking_deficit(company_id, warehouse_id, item_id, document_date, is_locked);

CREATE INDEX idx_stocktaking_sur_company_wh_item_date 
ON inventory_stocktaking_surplus(company_id, warehouse_id, item_id, document_date, is_locked);
```

---

## Performance Optimization

### Current Implementation
- **On-demand calculation**: No pre-computed balances stored
- **Query pattern**: Multiple aggregation queries per item
- **Caching**: None (calculated fresh each time)

### Optimization Strategies

1. **Request-level caching**:
   ```python
   @lru_cache(maxsize=1000)
   def calculate_item_balance(company_id, warehouse_id, item_id, as_of_date):
       # Cached for duration of request
   ```

2. **Materialized views** (for large datasets):
   ```sql
   CREATE MATERIALIZED VIEW inventory_balances AS
   SELECT company_id, warehouse_id, item_id, 
          calculated_balance, last_updated
   FROM ...;
   ```

3. **Background jobs**:
   - Pre-calculate balances nightly
   - Store in cache (Redis)
   - Serve from cache with timestamp

4. **Lazy loading**:
   - Load warehouse list first
   - Calculate balances on-demand when warehouse selected
   - Paginate results

---

## Testing

### Unit Tests

```python
def test_balance_calculation():
    # Create test data
    company = Company.objects.create(...)
    warehouse = Warehouse.objects.create(...)
    item = Item.objects.create(...)
    
    # Create stocktaking baseline
    StocktakingSurplus.objects.create(
        company=company,
        warehouse=warehouse,
        item=item,
        quantity_adjusted=Decimal('1000'),
        is_locked=1
    )
    
    # Add receipts
    ReceiptPermanent.objects.create(
        company=company,
        warehouse=warehouse,
        item=item,
        quantity=Decimal('100'),
        is_locked=1
    )
    
    # Calculate balance
    balance = calculate_item_balance(company.id, warehouse.id, item.id)
    
    assert balance['current_balance'] == 1100.0
```

---

## Error Handling

- **Missing stocktaking**: Returns baseline_quantity=0 if no stocktaking found
- **Item not found**: Raises `Item.DoesNotExist`
- **Warehouse not found**: Raises `Warehouse.DoesNotExist`
- **Invalid dates**: Catches `ValueError` and uses default (today)

---

## Future Enhancements

1. **Real-time updates**: WebSocket notifications when balance changes
2. **Low stock alerts**: Automated notifications when threshold reached
3. **Forecast**: Predict future balances based on historical trends
4. **Multi-warehouse**: Calculate total balance across all warehouses
5. **Lot-level balances**: Track balances per lot code for traceable items
6. **Valuation**: Include cost/price data for financial reporting

---

## Maintainer Notes

- Balance calculation is CPU-intensive for large warehouses (100+ items)
- Consider background job for generating reports
- Always test with realistic data volumes
- Monitor query performance using Django Debug Toolbar
- Document any changes to calculation logic in design plan

---

## Transaction History Display

### Overview

The transaction history detail page provides a complete audit trail of all inventory movements (receipts and issues) for a specific item in a warehouse.

### Features

1. **Source/Destination Column (مرکز مصرف/تامین)**:
   - **For Receipts**: Displays supplier name from the line item
   - **For Issues**: Displays department unit name or work line name (for consumption issues)
   - Only shows names (not codes) for better readability
   - Shows '—' if no source/destination information is available

2. **Clickable Document Codes**:
   - All document codes are clickable links
   - Links navigate directly to the document edit/view page
   - Styled with blue color (`#2563eb`) and hover effects
   - Supports all document types: Permanent Receipt, Consignment Receipt, Permanent Issue, Consumption Issue, Consignment Issue

3. **Transaction Data Structure**:
   ```python
   {
       'date': date,
       'type': 'receipt' | 'issue',
       'type_label': str,  # Localized label
       'document_code': str,
       'document_id': int,
       'document_type': str,  # 'permanent_receipt', 'consumption_issue', etc.
       'quantity': Decimal,
       'unit': str,
       'created_by': str,  # Username or '—'
       'source_destination': str,  # Supplier/department unit name
       'running_balance': Decimal
   }
   ```

### Source/Destination Logic

**For Receipts**:
- `ReceiptPermanentLine`: Shows `supplier.name` from line item
- `ReceiptConsignmentLine`: Shows `supplier.name` from line item

**For Issues**:
- **Permanent Issues**: Shows `document.department_unit.name` or resolves `destination_code` to department unit name
- **Consumption Issues**: Priority order:
  1. `work_line.name` (if work line is assigned)
  2. `document.department_unit.name` (if department unit is assigned)
  3. Resolves `cost_center_code` to department unit name via `CompanyUnit` lookup
  4. Falls back to `cost_center_code` as string
- **Consignment Issues**: Shows `document.department_unit.name` or resolves `destination_code` to department unit name

### Document Code Links

Document codes link to edit/view pages:
- `permanent_receipt` → `inventory:receipt_permanent_edit`
- `consignment_receipt` → `inventory:receipt_consignment_edit`
- `permanent_issue` → `inventory:issue_permanent_edit`
- `consumption_issue` → `inventory:issue_consumption_edit`
- `consignment_issue` → `inventory:issue_consignment_edit`

## Related Files

- `inventory/views/balance.py`: `InventoryBalanceView`, `InventoryBalanceDetailsView`, `InventoryBalanceAPIView`
- `templates/inventory/inventory_balance.html`: UI for balance display
- `templates/inventory/inventory_balance_details.html`: UI for transaction history details
- `inventory_module_db_design_plan.md`: Balance calculation specification
- `README.md`: Overall system documentation


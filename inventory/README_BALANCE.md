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
    'baseline_date': date or None,          # Date of last stocktaking
    'baseline_quantity': Decimal,            # Quantity from stocktaking
    'stocktaking_record_id': int or None,   # Reference to stocktaking record
    'stocktaking_record_code': str or None   # Human-readable code
}
```

**Logic**:
1. Find most recent approved `StocktakingRecord` before `as_of_date`
2. Sum surplus documents linked to that stocktaking
3. Subtract deficit documents linked to that stocktaking
4. Return net quantity as baseline

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
- `ReceiptPermanent` where `is_locked=1` and `document_date` in range
- `StocktakingSurplus` where `is_locked=1` and `document_date` in range
- `IssuePermanent` where `is_locked=1` and `document_date` in range
- `IssueConsumption` where `is_locked=1` and `document_date` in range
- `StocktakingDeficit` where `is_locked=1` and `document_date` in range

**Important Notes**:
- Only locked documents are included (`is_locked=1`)
- Consignment receipts/issues are excluded (don't affect owned inventory)
- Temporary receipts are excluded (not yet converted to permanent)

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

**Logic**:
1. Query all items in warehouse (with optional type/category filters)
2. Only include items with warehouse assignment (`ItemWarehouse`)
3. Calculate balance for each item using `calculate_item_balance()`
4. Filter out items with zero balance and no activity
5. Return list of balances

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

## Related Files

- `inventory/views.py`: `InventoryBalanceView`, `InventoryBalanceAPIView`
- `templates/inventory/inventory_balance.html`: UI for balance display
- `inventory_module_db_design_plan.md`: Balance calculation specification
- `README.md`: Overall system documentation


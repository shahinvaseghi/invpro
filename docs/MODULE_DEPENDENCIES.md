# Module Dependencies and Optional Features

This document describes the dependencies between modules and how optional features are handled.

## Overview

The invproj platform consists of multiple modules:
- **shared**: Core shared functionality (companies, users, access levels)
- **inventory**: Warehouse and inventory management
- **production**: Production planning and control
- **qc**: Quality control and inspection

## Dependency Rules

### Core Principle

**The inventory module must be able to run independently without the production module.**

This means:
- All dependencies from inventory to production must be **optional**
- If production is not installed, inventory should work without errors
- Optional features (like WorkLine selection) should be gracefully disabled

### Dependency Direction

```
shared (base)
  ├── inventory (can run standalone)
  │     └── production (optional dependency)
  ├── production (requires inventory)
  └── qc (requires inventory)
```

## Optional Dependencies

### Inventory → Production

The inventory module has the following optional dependencies on production:

#### 1. WorkLine in Consumption Issues

**Location**: `IssueConsumptionLine.work_line`

**Implementation**:
- Uses string reference: `"production.WorkLine"` (not direct import)
- Field is `null=True, blank=True` (optional)
- Import handled with `try/except ImportError` or `get_work_line_model()`

**Code Pattern**:
```python
from shared.utils.modules import get_work_line_model
WorkLine = get_work_line_model()

# In form __init__:
if WorkLine and 'work_line' in self.fields:
    self.fields['work_line'].queryset = WorkLine.objects.filter(...)
elif 'work_line' in self.fields:
    # Hide field if production not installed
    self.fields['work_line'].widget = forms.HiddenInput()
    self.fields['work_line'].required = False
```

**User Experience**:
- If production is installed: Users can select WorkLine as destination
- If production is NOT installed: WorkLine option is hidden/disabled

#### 2. API Endpoint for Work Lines

**Location**: `inventory/views/api.py::warehouse_work_lines`

**Implementation**:
```python
from shared.utils.modules import get_work_line_model
WorkLine = get_work_line_model()

if not WorkLine:
    return JsonResponse({'work_lines': [], 'count': 0})
```

**Behavior**:
- Returns empty list if production module is not installed
- No errors, graceful degradation

## Utility Functions

### `shared.utils.modules`

A utility module provides functions to check module availability:

```python
from shared.utils.modules import (
    is_production_installed,
    is_qc_installed,
    get_work_line_model,
    get_person_model,
)
```

**Functions**:
- `is_production_installed()`: Returns `True` if production module is installed
- `is_qc_installed()`: Returns `True` if QC module is installed
- `get_work_line_model()`: Returns `WorkLine` model class or `None`
- `get_person_model()`: Returns `Person` model class or `None`

**Usage**:
```python
from shared.utils.modules import get_work_line_model

WorkLine = get_work_line_model()
if WorkLine:
    # Production module is installed, use WorkLine
    queryset = WorkLine.objects.filter(...)
else:
    # Production module not installed, hide feature
    pass
```

## Migration Considerations

### Historical Migrations

Some old migrations reference `production.Person` or `production.WorkLine`:
- `inventory/migrations/0022_alter_purchaserequest_approver_and_more.py`
- `inventory/migrations/0026_add_personnel_machines_to_workline.py`
- `inventory/migrations/0028_move_workline_to_production.py`

**Note**: These migrations have `dependencies` that include production module. If you want to run inventory without production, you need to:
1. Ensure all migrations are applied before removing production
2. Or create conditional migrations that skip if production is not installed

### Current Model State

Current models use:
- `User` (from `shared`) for `PurchaseRequest.requested_by` and `approver`
- `User` (from `shared`) for `WarehouseRequest.requester` and `approver`
- String reference `"production.WorkLine"` for optional `IssueConsumptionLine.work_line`

## Testing Module Independence

### Test Inventory Without Production

1. **Remove production from INSTALLED_APPS**:
   ```python
   INSTALLED_APPS = [
       'shared',
       'inventory',
       # 'production',  # Commented out
       'qc',
       'ui',
   ]
   ```

2. **Run Django checks**:
   ```bash
   python manage.py check
   ```

3. **Test key features**:
   - Create consumption issue (should work without WorkLine option)
   - Create purchase request (should work)
   - Create warehouse request (should work)
   - API endpoint `/inventory/api/warehouse-work-lines/` (should return empty list)

### Expected Behavior

✅ **Should Work**:
- All inventory CRUD operations
- Consumption issues with CompanyUnit destination
- Purchase requests
- Warehouse requests
- All receipts and issues (except WorkLine-related features)

❌ **Should NOT Work** (gracefully disabled):
- WorkLine selection in consumption issues
- WorkLine API endpoint (returns empty list)

## Best Practices

### When Adding Optional Dependencies

1. **Use String References in Models**:
   ```python
   work_line = models.ForeignKey(
       "production.WorkLine",  # String reference, not direct import
       on_delete=models.SET_NULL,
       null=True,
       blank=True,
   )
   ```

2. **Use Utility Functions in Code**:
   ```python
   from shared.utils.modules import get_work_line_model
   WorkLine = get_work_line_model()
   if WorkLine:
       # Use WorkLine
   ```

3. **Hide Fields in Forms**:
   ```python
   if WorkLine:
       # Show and populate field
   else:
       # Hide field
       self.fields['work_line'].widget = forms.HiddenInput()
   ```

4. **Update Choices Dynamically**:
   ```python
   if WorkLine:
       # Add work_line option to choices
       choices = list(self.fields['destination_type_choice'].choices)
       choices.insert(-1, ('work_line', _('Work Line')))
       self.fields['destination_type_choice'].choices = choices
   ```

5. **Return Empty Results in APIs**:
   ```python
   if not WorkLine:
       return JsonResponse({'work_lines': [], 'count': 0})
   ```

## Future Considerations

### Potential Improvements

1. **Migration Conditional Logic**: Create migrations that check if production is installed before applying
2. **Feature Flags**: Use Django feature flags to enable/disable optional features
3. **Plugin Architecture**: Consider plugin-based architecture for optional modules

## Summary

- ✅ Inventory module can run independently
- ✅ All production dependencies are optional
- ✅ Graceful degradation when production is not installed
- ✅ No errors when production module is missing
- ✅ Features are hidden/disabled, not broken


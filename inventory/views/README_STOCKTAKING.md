# inventory/views/stocktaking.py - Stocktaking Views

**هدف**: Views برای مدیریت شمارش انبار (Stocktaking) در ماژول inventory

این فایل شامل views برای:
- Stocktaking Deficit (کسری شمارش)
- Stocktaking Surplus (مازاد شمارش)
- Stocktaking Record (سند شمارش)

---

## Stocktaking Deficit Views

### `StocktakingDeficitListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/stocktaking_deficit.html`
- **URL**: `/inventory/stocktaking/deficit/`

### `StocktakingDeficitCreateView`
- **Type**: `StocktakingFormMixin, CreateView`
- **Form**: `StocktakingDeficitForm`
- **URL**: `/inventory/stocktaking/deficit/create/`

### `StocktakingDeficitUpdateView`
- **Type**: `DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`
- **URL**: `/inventory/stocktaking/deficit/<pk>/edit/`

### `StocktakingDeficitDeleteView`
- **Type**: `DocumentDeleteViewBase`
- **Feature Code**: `inventory.stocktaking.deficit`
- **URL**: `/inventory/stocktaking/deficit/<pk>/delete/`

### `StocktakingDeficitLockView`
- **Type**: `DocumentLockView`
- **Model**: `StocktakingDeficit`
- **URL**: `/inventory/stocktaking/deficit/<pk>/lock/`

---

## Stocktaking Surplus Views

### `StocktakingSurplusListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/stocktaking_surplus.html`
- **URL**: `/inventory/stocktaking/surplus/`

### `StocktakingSurplusCreateView`
- **Type**: `StocktakingFormMixin, CreateView`
- **Form**: `StocktakingSurplusForm`
- **URL**: `/inventory/stocktaking/surplus/create/`

### `StocktakingSurplusUpdateView`
- **Type**: `DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`
- **URL**: `/inventory/stocktaking/surplus/<pk>/edit/`

### `StocktakingSurplusDeleteView`
- **Type**: `DocumentDeleteViewBase`
- **Feature Code**: `inventory.stocktaking.surplus`
- **URL**: `/inventory/stocktaking/surplus/<pk>/delete/`

### `StocktakingSurplusLockView`
- **Type**: `DocumentLockView`
- **Model**: `StocktakingSurplus`
- **URL**: `/inventory/stocktaking/surplus/<pk>/lock/`

---

## Stocktaking Record Views

### `StocktakingRecordListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/stocktaking_record.html`
- **URL**: `/inventory/stocktaking/record/`

### `StocktakingRecordCreateView`
- **Type**: `StocktakingFormMixin, CreateView`
- **Form**: `StocktakingRecordForm`
- **URL**: `/inventory/stocktaking/record/create/`

### `StocktakingRecordUpdateView`
- **Type**: `DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`
- **URL**: `/inventory/stocktaking/record/<pk>/edit/`

### `StocktakingRecordDeleteView`
- **Type**: `DocumentDeleteViewBase`
- **Feature Code**: `inventory.stocktaking.record`
- **URL**: `/inventory/stocktaking/record/<pk>/delete/`

### `StocktakingRecordLockView`
- **Type**: `DocumentLockView`
- **Model**: `StocktakingRecord`
- **URL**: `/inventory/stocktaking/record/<pk>/lock/`

---

## نکات مهم

1. **Baseline Calculation**: Deficit و Surplus در محاسبه موجودی به عنوان baseline استفاده می‌شوند
2. **Approval**: StocktakingRecord باید تایید شود (`approval_status = 'approved'`)
3. **Lock Protection**: تمام update/delete views از `DocumentLockProtectedMixin` استفاده می‌کنند


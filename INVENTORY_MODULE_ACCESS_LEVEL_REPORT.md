# گزارش کامل بررسی Access Level های ماژول Inventory

**تاریخ بررسی**: 2025-01-XX
**وضعیت**: 🔧 نیاز به اصلاحات

---

## خلاصه

ماژول Inventory دارای 11 feature_code استفاده شده در views است. اکثر آنها در `FEATURE_PERMISSION_MAP` تعریف شده‌اند، اما چند مشکل وجود دارد:

1. ✅ **یک مشکل اصلاح شد**: `inventory.master_data.item_subcategory` به `inventory.master.item_subcategories` تغییر یافت
2. ⚠️ **مشکل باقی‌مانده**: `InventoryBalanceView` از `FeaturePermissionRequiredMixin` استفاده نمی‌کند

---

## فهرست کامل Feature Codes در ماژول Inventory

### 1. Master Data (6 مورد)

#### ✅ `inventory.master.item_types` - Item Types
- **Views استفاده کننده**: `ItemTypeListView`, `ItemTypeCreateView`, `ItemTypeUpdateView`, `ItemTypeDeleteView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

#### ✅ `inventory.master.item_categories` - Item Categories
- **Views استفاده کننده**: `ItemCategoryListView`, `ItemCategoryCreateView`, `ItemCategoryUpdateView`, `ItemCategoryDeleteView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

#### ✅ `inventory.master.item_subcategories` - Item Subcategories
- **Views استفاده کننده**: `ItemSubcategoryListView`, `ItemSubcategoryCreateView`, `ItemSubcategoryUpdateView`, `ItemSubcategoryDeleteView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN
- **اصلاح شده**: ✅ `inventory.master_data.item_subcategory` به `inventory.master.item_subcategories` تغییر یافت

#### ✅ `inventory.master.items` - Items
- **Views استفاده کننده**: `ItemListView`, `ItemCreateView`, `ItemUpdateView`, `ItemDeleteView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

#### ✅ `inventory.master.item_serials` - Item Serials
- **Views استفاده کننده**: `ItemSerialListView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL (فقط نمایش)

#### ✅ `inventory.master.warehouses` - Warehouses
- **Views استفاده کننده**: `WarehouseListView`, `WarehouseCreateView`, `WarehouseUpdateView`, `WarehouseDeleteView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

---

### 2. Suppliers (2 مورد)

#### ✅ `inventory.suppliers.categories` - Supplier Categories
- **Views استفاده کننده**: `SupplierCategoryListView`, `SupplierCategoryCreateView`, `SupplierCategoryUpdateView`, `SupplierCategoryDeleteView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

#### ✅ `inventory.suppliers.list` - Suppliers
- **Views استفاده کننده**: `SupplierListView`, `SupplierCreateView`, `SupplierUpdateView`, `SupplierDeleteView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN

---

### 3. Receipts (3 مورد)

#### ✅ `inventory.receipts.temporary` - Temporary Receipts
- **Views استفاده کننده**: Multiple views در `receipts.py` و `requests.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER, CANCEL, CREATE_RECEIPT_FROM_PURCHASE_REQUEST

#### ✅ `inventory.receipts.permanent` - Permanent Receipts
- **Views استفاده کننده**: Multiple views در `receipts.py` و `requests.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER, APPROVE, REJECT, CANCEL, CREATE_RECEIPT_FROM_PURCHASE_REQUEST

#### ✅ `inventory.receipts.consignment` - Consignment Receipts
- **Views استفاده کننده**: Multiple views در `receipts.py` و `requests.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER, APPROVE, REJECT, CANCEL, CREATE_RECEIPT_FROM_PURCHASE_REQUEST

---

### 4. Issues (3 مورد)

#### ✅ `inventory.issues.permanent` - Permanent Issues
- **Views استفاده کننده**: Multiple views در `issues.py`, `issues_from_warehouse_request.py`, `create_issue_from_warehouse_request.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER, APPROVE, REJECT, CANCEL, CREATE_ISSUE_FROM_WAREHOUSE_REQUEST

#### ✅ `inventory.issues.consumption` - Consumption Issues
- **Views استفاده کننده**: Multiple views در `issues.py`, `issues_from_warehouse_request.py`, `create_issue_from_warehouse_request.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER, CANCEL, CREATE_ISSUE_FROM_WAREHOUSE_REQUEST

#### ✅ `inventory.issues.consignment` - Consignment Issues
- **Views استفاده کننده**: Multiple views در `issues.py`, `issues_from_warehouse_request.py`, `create_issue_from_warehouse_request.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER, APPROVE, REJECT, CANCEL, CREATE_ISSUE_FROM_WAREHOUSE_REQUEST

---

### 5. Requests (2 مورد)

#### ✅ `inventory.requests.purchase` - Purchase Requests
- **Views استفاده کننده**: Multiple views در `requests.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, APPROVE, REJECT, CANCEL, CREATE_RECEIPT_FROM_PURCHASE_REQUEST

#### ✅ `inventory.requests.warehouse` - Warehouse Requests
- **Views استفاده کننده**: Multiple views در `requests.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, APPROVE, REJECT, CANCEL, CREATE_ISSUE_FROM_WAREHOUSE_REQUEST

---

### 6. Stocktaking (3 مورد)

#### ✅ `inventory.stocktaking.deficit` - Stocktaking Deficit
- **Views استفاده کننده**: Views در `stocktaking.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER

#### ✅ `inventory.stocktaking.surplus` - Stocktaking Surplus
- **Views استفاده کننده**: Views در `stocktaking.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER

#### ✅ `inventory.stocktaking.records` - Stocktaking Records
- **Views استفاده کننده**: Views در `stocktaking.py`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, DELETE_OWN, DELETE_OTHER, LOCK_OWN, LOCK_OTHER, UNLOCK_OWN, UNLOCK_OTHER, APPROVE

---

### 7. Balance (1 مورد)

#### ⚠️ `inventory.balance` - Inventory Balance
- **Views استفاده کننده**: `InventoryBalanceView`, `InventoryBalanceDetailsView`, `InventoryBalanceAPIView`
- **تعریف شده در FEATURE_PERMISSION_MAP**: ✅ بله
- **Actions**: VIEW_OWN, VIEW_ALL (فقط نمایش)
- **مشکل**: ⚠️ `InventoryBalanceView` و `InventoryBalanceDetailsView` از `FeaturePermissionRequiredMixin` استفاده نمی‌کنند

---

## مشکلات شناسایی شده

### 1. ✅ اصلاح شده: نام اشتباه feature_code در ItemSubcategoryDeleteView

**مشکل**: 
```python
feature_code = 'inventory.master_data.item_subcategory'  # اشتباه
```

**اصلاح شده به**:
```python
feature_code = 'inventory.master.item_subcategories'  # درست
```

**فایل**: `inventory/views/master_data.py` خط 499

---

### 2. ⚠️ نیاز به اصلاح: InventoryBalanceView بدون FeaturePermissionRequiredMixin

**مشکل**: `InventoryBalanceView` و `InventoryBalanceDetailsView` از `FeaturePermissionRequiredMixin` استفاده نمی‌کنند، در حالی که `inventory.balance` در `FEATURE_PERMISSION_MAP` تعریف شده است.

**راه حل پیشنهادی**:
```python
from shared.mixins import FeaturePermissionRequiredMixin

class InventoryBalanceView(FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView):
    feature_code = 'inventory.balance'
    required_action = 'view_own'
    # ... rest of the code
```

**فایل**: `inventory/views/balance.py`

---

## خلاصه آمار

- **تعداد feature_code های استفاده شده**: 11
- **تعداد feature_code های تعریف شده در FEATURE_PERMISSION_MAP**: 11
- **مشکلات شناسایی شده**: 2
- **مشکلات اصلاح شده**: 1
- **مشکلات باقی‌مانده**: 1

---

## فایل‌های بررسی شده

- ✅ `inventory/views/master_data.py` (اصلاح شده)
- ✅ `inventory/views/receipts.py`
- ✅ `inventory/views/issues.py`
- ✅ `inventory/views/requests.py`
- ✅ `inventory/views/stocktaking.py`
- ⚠️ `inventory/views/balance.py` (نیاز به اصلاح)
- ✅ `inventory/views/issues_from_warehouse_request.py`
- ✅ `inventory/views/create_issue_from_warehouse_request.py`

---

## اقدامات انجام شده

1. ✅ اصلاح `feature_code` در `ItemSubcategoryDeleteView` از `inventory.master_data.item_subcategory` به `inventory.master.item_subcategories`

---

## اقدامات پیشنهادی

1. ⚠️ اضافه کردن `FeaturePermissionRequiredMixin` به `InventoryBalanceView` و `InventoryBalanceDetailsView`
2. ⚠️ اضافه کردن `feature_code = 'inventory.balance'` به این views
3. ⚠️ اضافه کردن `required_action = 'view_own'` به این views

---

**وضعیت نهایی**: ✅ اکثر موارد درست هستند، فقط یک مشکل باقی‌مانده است که نیاز به اصلاح دارد.


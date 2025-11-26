# inventory/views/requests.py - Request Views

**هدف**: Views برای مدیریت درخواست‌ها (Requests) در ماژول inventory

این فایل شامل views برای:
- Purchase Requests (درخواست‌های خرید)
- Warehouse Requests (درخواست‌های انبار)
- Receipt Creation from Purchase Requests

---

## Base Mixins

### `PurchaseRequestFormMixin`

**توضیح**: Helper mixin مشترک برای purchase request create/update views.

**Type**: `InventoryBaseView`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`
- **Returns**: context کامل برای template
- **Context Variables**:
  - `item_types`: لیست نوع کالاها برای فیلتر
  - `item_categories`: لیست دسته‌بندی‌های کالا برای فیلتر
  - `item_subcategories`: لیست زیر دسته‌بندی‌های کالا برای فیلتر
  - `current_item_type`: نوع کالای انتخاب شده در فیلتر (از `request.GET` یا `request.POST`)
  - `current_category`: دسته‌بندی انتخاب شده در فیلتر (از `request.GET` یا `request.POST`)
  - `current_subcategory`: زیر دسته‌بندی انتخاب شده در فیلتر (از `request.GET` یا `request.POST`)
  - `current_item_search`: عبارت جستجو در فیلتر (از `request.GET` یا `request.POST`)

---

### `WarehouseRequestFormMixin`

**توضیح**: Helper mixin مشترک برای warehouse request create/update views.

**Type**: `InventoryBaseView`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`
- **Returns**: context کامل برای template
- **Context Variables**:
  - `item_types`: لیست نوع کالاها برای فیلتر
  - `item_categories`: لیست دسته‌بندی‌های کالا برای فیلتر
  - `item_subcategories`: لیست زیر دسته‌بندی‌های کالا برای فیلتر
  - `current_item_type`: نوع کالای انتخاب شده در فیلتر (از `request.GET`)
  - `current_category`: دسته‌بندی انتخاب شده در فیلتر (از `request.GET`)
  - `current_subcategory`: زیر دسته‌بندی انتخاب شده در فیلتر (از `request.GET`)
  - `current_item_search`: عبارت جستجو در فیلتر (از `request.GET`)

---

## Purchase Request Views

### `PurchaseRequestListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/purchase_request.html`
- **URL**: `/inventory/requests/purchase/`

### `PurchaseRequestCreateView`
- **Type**: `LineFormsetMixin, PurchaseRequestFormMixin, CreateView`
- **Form**: `PurchaseRequestForm`
- **Formset**: `PurchaseRequestLineFormSet`
- **URL**: `/inventory/requests/purchase/create/`
- **Features**:
  - پشتیبانی از فیلتر و جستجوی کالا در line forms
  - محاسبه `quantity_requested` و `quantity_fulfilled` از مجموع line items

### `PurchaseRequestUpdateView`
- **Type**: `LineFormsetMixin, PurchaseRequestFormMixin, UpdateView`
- **URL**: `/inventory/requests/purchase/<pk>/edit/`
- **Features**:
  - پشتیبانی از فیلتر و جستجوی کالا در line forms
  - به‌روزرسانی `quantity_requested` از مجموع line items پس از ذخیره

### `PurchaseRequestApproveView`
- **Type**: `InventoryBaseView, View`
- **منطق**: درخواست را تایید می‌کند (`status = APPROVED`)
- **URL**: `/inventory/requests/purchase/<pk>/approve/`

---

## Warehouse Request Views

### `WarehouseRequestListView`
- **Type**: `InventoryBaseView, ListView`
- **Template**: `inventory/warehouse_request.html`
- **URL**: `/inventory/requests/warehouse/`

### `WarehouseRequestCreateView`
- **Type**: `WarehouseRequestFormMixin, CreateView`
- **Form**: `WarehouseRequestForm`
- **URL**: `/inventory/requests/warehouse/create/`
- **Features**:
  - پشتیبانی از فیلتر و جستجوی کالا در form

### `WarehouseRequestUpdateView`
- **Type**: `WarehouseRequestFormMixin, UpdateView`
- **URL**: `/inventory/requests/warehouse/<pk>/edit/`
- **Features**:
  - پشتیبانی از فیلتر و جستجوی کالا در form

### `WarehouseRequestApproveView`
- **Type**: `InventoryBaseView, View`
- **منطق**: درخواست را تایید می‌کند
- **URL**: `/inventory/requests/warehouse/<pk>/approve/`

---

## Receipt Creation Views

### `CreateReceiptFromPurchaseRequestView`
- **Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView`
- **Template**: `inventory/create_receipt_from_purchase_request.html`
- **منطق**: صفحه انتخاب نوع رسید (temporary/permanent/consignment)
- **URL**: `/inventory/requests/purchase/<purchase_request_id>/create-receipt/`

### `CreateTemporaryReceiptFromPurchaseRequestView`
- **Type**: `CreateReceiptFromPurchaseRequestView` (inherits)
- **منطق**: ایجاد رسید موقت از درخواست خرید

### `CreatePermanentReceiptFromPurchaseRequestView`
- **Type**: `CreateReceiptFromPurchaseRequestView` (inherits)
- **منطق**: ایجاد رسید دائم از درخواست خرید

### `CreateConsignmentReceiptFromPurchaseRequestView`
- **Type**: `CreateReceiptFromPurchaseRequestView` (inherits)
- **منطق**: ایجاد رسید امانی از درخواست خرید

---

## نکات مهم

1. **Approval Workflow**: درخواست‌ها باید تایید شوند قبل از تبدیل به رسید
2. **Line Conversion**: ردیف‌های درخواست خرید به ردیف‌های رسید تبدیل می‌شوند
3. **Status Management**: درخواست‌ها می‌توانند `DRAFT` یا `APPROVED` باشند
4. **Item Filtering and Search**: تمام request forms از فیلتر و جستجوی کالا پشتیبانی می‌کنند:
   - **PurchaseRequestFormMixin**: اضافه کردن `item_types`, `item_categories`, `item_subcategories` به context
   - **WarehouseRequestFormMixin**: اضافه کردن فیلترها به context
   - **PurchaseRequestLineForm**: فیلتر کردن item queryset بر اساس `request.GET` (item_type, category, subcategory, item_search)
   - **WarehouseRequestForm**: فیلتر کردن item queryset بر اساس `request.GET`
   - فیلترها و جستجو از طریق API endpoint `/inventory/api/filtered-items/` اعمال می‌شوند
   - جستجو در `name` و `item_code` کالا انجام می‌شود


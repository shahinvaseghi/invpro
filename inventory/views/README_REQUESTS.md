# inventory/views/requests.py - Request Views (Complete Documentation)

**هدف**: Views برای مدیریت درخواست‌ها (Requests) در ماژول inventory

این فایل شامل **14 کلاس view**:
- **2 Base Mixins**: `PurchaseRequestFormMixin`, `WarehouseRequestFormMixin`
- **5 Purchase Request Views**: List, Create, Update, Approve
- **4 Warehouse Request Views**: List, Create, Update, Approve
- **4 Create Receipt from Purchase Request Views**: 1 base + 3 subclass

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`, `LineFormsetMixin`
- `inventory.models`: `PurchaseRequest`, `PurchaseRequestLine`, `WarehouseRequest`, `Item`, `ItemUnit`, `ItemType`, `ItemCategory`, `ItemSubcategory`
- `inventory.forms`: `PurchaseRequestForm`, `PurchaseRequestLineFormSet`, `WarehouseRequestForm`, `get_purchase_request_approvers`, `get_feature_approvers`, `UNIT_CHOICES`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `View`, `TemplateView`
- `django.http`: `HttpResponseRedirect`, `Http404`
- `django.urls`: `reverse`, `reverse_lazy`
- `django.shortcuts`: `get_object_or_404`
- `django.utils`: `timezone`
- `django.utils.translation`: `gettext_lazy`
- `django.utils.safestring`: `mark_safe`
- `django.contrib.messages`
- `django.db.models.Q`
- `decimal.Decimal`, `InvalidOperation`
- `json`
- `logging`

---

## Base Mixins

### PurchaseRequestFormMixin

**Type**: `InventoryBaseView`

**Attributes**:
- `template_name`: `'inventory/purchase_request_form.html'`
- `form_title`: `''` (override در subclasses)

**متدها**:

#### `get_form_kwargs() -> Dict[str, Any]`
- اضافه کردن `company_id` و `request_user` به form

#### `get_context_data(**kwargs) -> Dict[str, Any]`
**Context Variables**:
- `form_title`, `fieldsets`, `used_fields`, `list_url`, `is_edit`, `purchase_request`
- `unit_options_json`: JSON map از item_id به allowed units
- `unit_placeholder`: placeholder برای unit field
- `item_types`, `item_categories`, `item_subcategories`: برای فیلتر
- `current_item_type`, `current_category`, `current_subcategory`, `current_item_search`: مقادیر فعلی فیلتر (از GET یا POST)

#### `get_fieldsets() -> list`
- باید در subclasses override شود

---

### WarehouseRequestFormMixin

**Type**: `InventoryBaseView`

**Attributes**:
- `template_name`: `'inventory/warehouse_request_form.html'`
- `form_title`: `''` (override در subclasses)

**متدها**:

#### `get_form_kwargs() -> Dict[str, Any]`
- اضافه کردن `company_id` و `request_user` به form

#### `get_context_data(**kwargs) -> Dict[str, Any]`
**Context Variables**:
- `form_title`, `fieldsets`, `used_fields`, `list_url`, `is_edit`, `warehouse_request`
- `item_types`, `item_categories`, `item_subcategories`: برای فیلتر
- `current_item_type`, `current_category`, `current_subcategory`, `current_item_search`: مقادیر فعلی فیلتر (از GET)

#### `get_fieldsets() -> list`
- باید در subclasses override شود

---

## Purchase Request Views

### PurchaseRequestListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/purchase_requests.html`

**Attributes**:
- `model`: `PurchaseRequest`
- `context_object_name`: `'purchase_requests'`
- `paginate_by`: `50`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با فیلتر permissions، search، status و priority آماده می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده و مرتب شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.requests.purchase', 'requested_by')`
3. `select_related('requested_by', 'approver')` و `prefetch_related('lines__item')` را اعمال می‌کند
4. مرتب‌سازی بر اساس `-id`, `-request_date`, `request_code`
5. فیلتر بر اساس `status` از `request.GET.get('status')` (اگر موجود باشد)
6. فیلتر بر اساس `priority` از `request.GET.get('priority')` (اگر موجود باشد)
7. جستجو در `request_code`, `item__name`, `item_code` از `request.GET.get('search')` (اگر موجود باشد)

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables شامل statistics، filter context و approver permissions را اضافه می‌کند.

**Context Variables اضافه شده**:
- `total_count`, `draft_count`, `approved_count`, `ordered_count`, `fulfilled_count`: آمار از queryset
- `create_url`: `reverse_lazy('inventory:purchase_request_create')`
- `edit_url_name`: `'inventory:purchase_request_edit'`
- `approve_url_name`: `'inventory:purchase_request_approve'`
- `status_filter`, `priority_filter`, `search_term`: مقادیر فعلی فیلترها از GET
- `approver_user_ids`: لیست user IDs که می‌توانند approve کنند (از `get_purchase_request_approvers`)
- `can_current_user_edit`, `can_current_user_approve`: برای هر purchase request در queryset (محاسبه شده در loop)

**Query Parameters**:
- `status`: فیلتر بر اساس status
- `priority`: فیلتر بر اساس priority
- `search`: جستجو در request_code, item name, item_code

**Context Variables**:
- `total_count`, `draft_count`, `approved_count`, `ordered_count`, `fulfilled_count`
- `create_url`, `edit_url_name`, `approve_url_name`
- `status_filter`, `priority_filter`, `search_term`
- `approver_user_ids`: لیست user IDs که می‌توانند approve کنند
- `can_current_user_edit`, `can_current_user_approve`: برای هر purchase request

**URL**: `/inventory/requests/purchase/`

---

### PurchaseRequestCreateView

**Type**: `LineFormsetMixin, PurchaseRequestFormMixin, CreateView`

**Form**: `PurchaseRequestForm`

**Formset**: `PurchaseRequestLineFormSet`

**Success URL**: `inventory:purchase_requests`

**Attributes**:
- `form_title`: `_('ایجاد درخواست خرید')`

**متدها**:
- `form_valid()`:
  1. تنظیم `company_id`, `requested_by`, `request_date`, `status = DRAFT`
  2. Build و validate line formset
  3. استخراج first item و unit از valid lines
  4. تنظیم legacy fields (`item`, `item_code`, `unit`, `quantity_requested = 0`, `quantity_fulfilled = 0`)
  5. ذخیره document با `_skip_legacy_sync = True`
  6. Validate و save formset
  7. محاسبه `total_quantity` از lines
  8. به‌روزرسانی `quantity_requested` و `quantity_fulfilled`
  9. نمایش پیام موفقیت

**Fieldsets**:
- `[(_('زمان بندی و اولویت'), ['needed_by_date', 'priority']), (_('تایید و توضیحات'), ['approver', 'reason_code'])]`

**نکات مهم**:
- Legacy fields برای backward compatibility
- `quantity_requested` از مجموع line items محاسبه می‌شود
- `_skip_legacy_sync` برای جلوگیری از sync در model.save()

**URL**: `/inventory/requests/purchase/create/`

---

### PurchaseRequestUpdateView

**Type**: `LineFormsetMixin, PurchaseRequestFormMixin, UpdateView`

**Form**: `PurchaseRequestForm`

**Formset**: `PurchaseRequestLineFormSet`

**Success URL**: `inventory:purchase_requests`

**Attributes**:
- `form_title`: `_('ویرایش درخواست خرید')`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را فیلتر می‌کند تا فقط DRAFT requests created by current user را شامل شود.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. `select_related('requested_by', 'approver')` و `prefetch_related('lines__item')` را اعمال می‌کند
3. فیلتر می‌کند: `status = DRAFT` و `requested_by = request.user`

**نکته**: این view فقط اجازه ویرایش DRAFT requests که توسط کاربر فعلی ایجاد شده‌اند را می‌دهد.

---

#### `form_valid(self, form) -> HttpResponseRedirect`
  1. تنظیم `company_id`, `edited_by`
  2. ذخیره document
  3. Validate و save formset
  4. محاسبه `total_quantity` از lines
  5. به‌روزرسانی `quantity_requested`
  6. نمایش پیام موفقیت

**Fieldsets**: مشابه CreateView

**نکات مهم**:
- فقط DRAFT requests قابل ویرایش هستند
- فقط requests created by current user

**URL**: `/inventory/requests/purchase/<pk>/edit/`

---

### PurchaseRequestApproveView

**Type**: `InventoryBaseView, View`

**Method**: `POST`

**متدها**:
- `post()`:
  1. بررسی `active_company_id`
  2. دریافت purchase request
  3. بررسی status (نباید APPROVED باشد)
  4. بررسی `approver_id` (باید تنظیم شده باشد)
  5. بررسی `approver_id == request.user.id`
  6. بررسی permission (باید در `get_purchase_request_approvers` باشد)
  7. Approve: `status = APPROVED`, `approved_at = now`, `is_locked = 1`, `locked_at = now`, `locked_by = request.user`
  8. نمایش پیام موفقیت

**نکات مهم**:
- فقط approver تعیین شده می‌تواند approve کند
- بعد از approve، request قفل می‌شود

**URL**: `/inventory/requests/purchase/<pk>/approve/`

---

## Warehouse Request Views

### WarehouseRequestListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/warehouse_requests.html`

**Attributes**:
- `model`: `WarehouseRequest`
- `context_object_name`: `'requests'`
- `paginate_by`: `50`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با فیلتر permissions، search، status و priority آماده می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.requests.warehouse', 'requester')`
3. `select_related('item', 'warehouse', 'requester', 'approver')` را اعمال می‌کند
4. فیلتر بر اساس `request_status` از `request.GET.get('status')` (اگر موجود باشد)
5. فیلتر بر اساس `priority` از `request.GET.get('priority')` (اگر موجود باشد)
6. جستجو در `request_code`, `item__name`, `item_code` از `request.GET.get('search')` (اگر موجود باشد)

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables شامل statistics، filter context و approver permissions را اضافه می‌کند.

**Context Variables اضافه شده**:
- `total_count`, `draft_count`, `approved_count`, `issued_count`: آمار از queryset
- `create_url`: `reverse_lazy('inventory:warehouse_request_create')`
- `edit_url_name`: `'inventory:warehouse_request_edit'`
- `approve_url_name`: `'inventory:warehouse_request_approve'`
- `status_filter`, `priority_filter`, `search_term`: مقادیر فعلی فیلترها از GET
- `approver_user_ids`: لیست user IDs که می‌توانند approve کنند (از `get_feature_approvers`)
- `can_current_user_edit`, `can_current_user_approve`: برای هر warehouse request در queryset (محاسبه شده در loop)

**Query Parameters**: مشابه `PurchaseRequestListView`

**Context Variables**: مشابه `PurchaseRequestListView`

**URL**: `/inventory/requests/warehouse/`

---

### WarehouseRequestCreateView

**Type**: `LineFormsetMixin, WarehouseRequestFormMixin, CreateView`

**Form**: `WarehouseRequestForm`

**Formset**: `WarehouseRequestLineFormSet`

**Success URL**: `inventory:warehouse_requests`

**Attributes**:
- `form_title`: `_('ایجاد درخواست انبار')`

**متدها**:
- `form_valid()`:
  1. تنظیم `company_id`, `requester`, `request_date`, `request_status = 'draft'`
  2. Build و validate line formset
  3. استخراج first item, unit, و warehouse از valid lines
  4. تنظیم legacy fields (`item`, `item_code`, `unit`, `warehouse`, `warehouse_code`, `quantity_requested = 0`)
  5. ذخیره document
  6. Validate و save formset
  7. محاسبه `total_quantity` از lines
  8. به‌روزرسانی `quantity_requested`
  9. نمایش پیام موفقیت
- `get_fieldsets()`: `[(_('اطلاعات درخواست'), ['department_unit']), (_('زمان‌بندی و اولویت'), ['needed_by_date', 'priority']), (_('تایید و توضیحات'), ['approver', 'purpose'])]`

**نکات مهم**:
- Legacy fields برای backward compatibility
- `quantity_requested` از مجموع line items محاسبه می‌شود
- هر خط شامل: item, unit, quantity_requested, warehouse, line_notes

**URL**: `/inventory/requests/warehouse/create/`

---

### WarehouseRequestUpdateView

**Type**: `LineFormsetMixin, WarehouseRequestFormMixin, UpdateView`

**Form**: `WarehouseRequestForm`

**Formset**: `WarehouseRequestLineFormSet`

**Success URL**: `inventory:warehouse_requests`

**Attributes**:
- `form_title`: `_('ویرایش درخواست انبار')`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را فیلتر می‌کند تا فقط 'draft' requests created by current user را شامل شود.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. `select_related('requester', 'approver')` و `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
3. فیلتر می‌کند: `request_status = 'draft'` و `requester = request.user`

**نکته**: این view فقط اجازه ویرایش draft requests که توسط کاربر فعلی ایجاد شده‌اند را می‌دهد.

---

#### `form_valid(self, form) -> HttpResponseRedirect`
  1. تنظیم `company_id`, `edited_by`
  2. ذخیره document
  3. Validate و save formset
  4. محاسبه `total_quantity` از lines
  5. به‌روزرسانی `quantity_requested` و legacy fields از first valid line
  6. نمایش پیام موفقیت
- `get_fieldsets()`: مشابه CreateView

**نکات مهم**:
- فقط 'draft' requests قابل ویرایش هستند
- فقط requests created by current user
- Legacy fields از first valid line به‌روزرسانی می‌شوند

**URL**: `/inventory/requests/warehouse/<pk>/edit/`

---

### WarehouseRequestApproveView

**Type**: `InventoryBaseView, View`

**Method**: `POST`

**متدها**:
- `post()`: مشابه `PurchaseRequestApproveView`
  - بررسی `active_company_id`
  - دریافت warehouse request
  - بررسی status (نباید 'approved' باشد)
  - بررسی `approver_id`
  - بررسی `approver_id == request.user.id`
  - بررسی permission (باید در `get_feature_approvers` باشد)
  - Approve: `request_status = 'approved'`, `approved_at = now`, `is_locked = 1`, `locked_at = now`, `locked_by = request.user`

**URL**: `/inventory/requests/warehouse/<pk>/approve/`

---

## Create Receipt from Purchase Request Views

### CreateReceiptFromPurchaseRequestView

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView`

**Template**: `inventory/create_receipt_from_purchase_request.html`

**Attributes**:
- `receipt_type`: `None` (باید در subclass تنظیم شود: `'temporary'`, `'permanent'`, `'consignment'`)
- `required_action`: `'create_receipt_from_purchase_request'`

**متدها**:

#### `get_purchase_request(self, pk: int) -> PurchaseRequest`
- دریافت purchase request با فیلتر: `company_id`, `status = APPROVED`, `is_enabled = 1`

#### `get_context_data(**kwargs) -> Dict[str, Any]`
**Context Variables**:
- `purchase_request`: purchase request object
- `lines`: لیست lines (فیلتر شده با `is_enabled=1`)
- `receipt_type`: نوع receipt
- `receipt_type_name`: نام فارسی نوع receipt

#### `post(self, request, *args, **kwargs) -> HttpResponseRedirect`
**منطق**:
1. دریافت selected lines از POST (checkbox `selected_{line_id}` و `quantity_{line_id}`)
2. Parse کردن quantity به Decimal
3. بررسی quantity > 0 و quantity <= remaining
4. ذخیره selected lines در session:
   - Key: `purchase_request_{pk}_receipt_{receipt_type}_lines`
   - Data: `[{'line_id': pk, 'quantity': str(quantity)}, ...]`
5. Redirect به receipt creation view

**Redirect URLs**:
- Temporary: `inventory:receipt_temporary_create_from_request`
- Permanent: `inventory:receipt_permanent_create_from_request`
- Consignment: `inventory:receipt_consignment_create_from_request`

**Error Handling**:
- اگر هیچ line انتخاب نشده باشد: error message
- اگر quantity > remaining: adjust به remaining

---

### CreateTemporaryReceiptFromPurchaseRequestView

**Type**: `CreateReceiptFromPurchaseRequestView`

**Attributes**:
- `receipt_type`: `'temporary'`
- `feature_code`: `'inventory.receipts.temporary'`

**URL**: `/inventory/requests/purchase/<pk>/create-temporary-receipt/`

---

### CreatePermanentReceiptFromPurchaseRequestView

**Type**: `CreateReceiptFromPurchaseRequestView`

**Attributes**:
- `receipt_type`: `'permanent'`
- `feature_code`: `'inventory.receipts.permanent'`

**URL**: `/inventory/requests/purchase/<pk>/create-permanent-receipt/`

---

### CreateConsignmentReceiptFromPurchaseRequestView

**Type**: `CreateReceiptFromPurchaseRequestView`

**Attributes**:
- `receipt_type`: `'consignment'`
- `feature_code`: `'inventory.receipts.consignment'`

**URL**: `/inventory/requests/purchase/<pk>/create-consignment-receipt/`

---

## نکات مهم

### 1. Purchase Request Legacy Fields
- `item`, `item_code`, `unit`, `quantity_requested`, `quantity_fulfilled` برای backward compatibility
- از first valid line populate می‌شوند
- `quantity_requested` از مجموع line items محاسبه می‌شود
- `_skip_legacy_sync` برای جلوگیری از sync در model.save()

### 2. Warehouse Request Multi-line
- Warehouse Request حالا یک multi-line document است (مثل Purchase Request)
- از `WarehouseRequestLineFormSet` برای مدیریت خطوط استفاده می‌کند
- هر خط شامل: item, unit, quantity_requested, warehouse, line_notes
- Legacy fields (`item`, `item_code`, `unit`, `warehouse`, `warehouse_code`, `quantity_requested`) از first valid line populate می‌شوند

### 3. Approval Workflow
- درخواست‌ها باید تایید شوند قبل از استفاده در receipts
- فقط approver تعیین شده می‌تواند approve کند
- بعد از approve، request قفل می‌شود

### 4. Session Management
- Selected lines در session ذخیره می‌شوند
- Session key format: `purchase_request_{pk}_receipt_{receipt_type}_lines`
- Session بعد از successful receipt creation پاک می‌شود

### 5. Quantity Fulfillment
- `quantity_fulfilled` در purchase request lines به‌روزرسانی می‌شود
- `quantity_fulfilled` نمی‌تواند بیشتر از `quantity_requested` باشد

### 6. Item Filtering and Search
- تمام request forms از فیلتر و جستجو پشتیبانی می‌کنند
- فیلترها: `item_type`, `category`, `subcategory`
- جستجو: `item_search` (در name و item_code)
- فیلترها و جستجو از طریق API endpoint `/inventory/api/filtered-items/` اعمال می‌شوند

### 7. Ordering
- Purchase requests به ترتیب `-id`, `-request_date`, `request_code` مرتب می‌شوند (جدیدترین اول)

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌شود
3. **Formset Management**: Purchase Request از `LineFormsetMixin` استفاده می‌کند
4. **Error Handling**: خطاها با messages نمایش داده می‌شوند
5. **Session Management**: از session برای انتقال selected lines استفاده می‌شود

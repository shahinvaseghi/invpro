# inventory/views/issues_from_warehouse_request.py - Issue Creation from Warehouse Request (Complete Documentation)

**هدف**: Views برای ایجاد مستقیم Issue documents از Warehouse Request

این فایل شامل 3 view class:
- IssuePermanentCreateFromWarehouseRequestView: ایجاد permanent issue
- IssueConsumptionCreateFromWarehouseRequestView: ایجاد consumption issue
- IssueConsignmentCreateFromWarehouseRequestView: ایجاد consignment issue

**نکته**: این views مستقیماً issue را ایجاد می‌کنند (بدون intermediate selection page). داده‌ها از session (که توسط `CreateIssueFromWarehouseRequestView` تنظیم شده) استفاده می‌شوند.

---

## وابستگی‌ها

- `inventory.views.base`: `LineFormsetMixin`
- `inventory.views.receipts`: `ReceiptFormMixin`
- `inventory.models`: `WarehouseRequest`, `IssuePermanent`, `IssueConsumption`, `IssueConsignment`
- `inventory.forms`: `IssuePermanentForm`, `IssueConsumptionForm`, `IssueConsignmentForm`, `IssuePermanentLineFormSet`, `IssueConsumptionLineFormSet`, `IssueConsignmentLineFormSet`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic.CreateView`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.shortcuts.get_object_or_404`
- `django.utils.translation.gettext_lazy`
- `django.contrib.messages`
- `decimal.Decimal`

---

## IssuePermanentCreateFromWarehouseRequestView

**Type**: `FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `IssuePermanentForm`

**Formset**: `IssuePermanentLineFormSet`

**Success URL**: `inventory:issue_permanent`

**Attributes**:
- `model`: `IssuePermanent`
- `form_class`: `IssuePermanentForm`
- `formset_class`: `IssuePermanentLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_permanent')`
- `form_title`: `_('ایجاد حواله دائم از درخواست انبار')`
- `receipt_variant`: `'issue_permanent'`
- `list_url_name`: `'inventory:issue_permanent'`
- `lock_url_name`: `'inventory:issue_permanent_lock'`
- `feature_code`: `'inventory.issues.permanent'`
- `required_action`: `'create'`

**متدها**:

#### `get_warehouse_request(self) -> WarehouseRequest`

**توضیح**: دریافت warehouse request از URL.

**مقدار بازگشتی**:
- `WarehouseRequest`: warehouse request object

**منطق**:
- دریافت از `self.kwargs['pk']`
- فیلتر: `company_id`, `request_status='approved'`, `is_enabled=1`

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن warehouse request به context و populate کردن formset با initial data از session.

**Context Variables**:
- `warehouse_request`: warehouse request object
- `lines_formset`: formset با initial data از warehouse request
- `form`: form با initial data از warehouse request

**منطق**:
1. دریافت warehouse request
2. دریافت quantity و notes از session:
   - Session key: `warehouse_request_{pk}_issue_permanent_data`
   - Fallback: `quantity_requested` از warehouse request
3. ساخت initial data برای line:
   - `item`: از warehouse request
   - `warehouse`: از warehouse request
   - `unit`: از warehouse request
   - `quantity`: از session
   - `line_notes`: از session
   - `destination_type`, `destination_id`, `destination_code`: از warehouse request
4. Populate کردن formset با initial data
5. Pre-fill کردن form با warehouse request data

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره document و line formset، linking به warehouse request.

**منطق**:
1. دریافت warehouse request
2. تنظیم `company_id`, `created_by`, `edited_by`, `warehouse_request`
3. تنظیم `department_unit` از warehouse request
4. ذخیره document
5. Validate کردن formset
6. بررسی valid lines (باید حداقل یک line با item وجود داشته باشد)
7. اگر valid lines = 0:
   - حذف document
   - نمایش error
8. ذخیره formset
9. پاک کردن session data
10. نمایش پیام موفقیت
11. Redirect به success URL

**نکات مهم**:
- اگر هیچ valid line وجود نداشته باشد، document حذف می‌شود
- Session data بعد از successful creation پاک می‌شود

---

#### `get_fieldsets(self) -> list`

**توضیح**: بازگشت fieldsets configuration.

**مقدار بازگشتی**:
- `list`: `[(_('Document Info'), ['document_code'])]`

---

## IssueConsumptionCreateFromWarehouseRequestView

**Type**: `FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html`

**Form**: `IssueConsumptionForm`

**Formset**: `IssueConsumptionLineFormSet`

**Success URL**: `inventory:issue_consumption`

**Attributes**:
- `model`: `IssueConsumption`
- `form_class`: `IssueConsumptionForm`
- `formset_class`: `IssueConsumptionLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_consumption')`
- `form_title`: `_('ایجاد حواله مصرف از درخواست انبار')`
- `receipt_variant`: `'issue_consumption'`
- `list_url_name`: `'inventory:issue_consumption'`
- `lock_url_name`: `'inventory:issue_consumption_lock'`
- `feature_code`: `'inventory.issues.consumption'`
- `required_action`: `'create'`

**متدها**:

#### `get_warehouse_request(self) -> WarehouseRequest`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`
- **تفاوت**: Initial data شامل `consumption_type` و `destination_type_choice` است
- `consumption_type` بر اساس `department_unit` تعیین می‌شود

#### `form_valid(self, form) -> HttpResponseRedirect`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`
- **تفاوت**: `warehouse_request` به issue link نمی‌شود (فقط `department_unit`)

#### `get_fieldsets(self) -> list`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`

**تفاوت‌ها**:
- Session key: `warehouse_request_{pk}_issue_consumption_data`
- Initial data شامل: `consumption_type`, `destination_type_choice`
- `consumption_type` بر اساس `department_unit` تعیین می‌شود
- `warehouse_request` به issue document link نمی‌شود

---

## IssueConsignmentCreateFromWarehouseRequestView

**Type**: `FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html`

**Form**: `IssueConsignmentForm`

**Formset**: `IssueConsignmentLineFormSet`

**Success URL**: `inventory:issue_consignment`

**Attributes**:
- `model`: `IssueConsignment`
- `form_class`: `IssueConsignmentForm`
- `formset_class`: `IssueConsignmentLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_consignment')`
- `form_title`: `_('ایجاد حواله امانی از درخواست انبار')`
- `receipt_variant`: `'issue_consignment'`
- `list_url_name`: `'inventory:issue_consignment'`
- `lock_url_name`: `'inventory:issue_consignment_lock'`
- `feature_code`: `'inventory.issues.consignment'`
- `required_action`: `'create'`

**متدها**:

#### `get_warehouse_request(self) -> WarehouseRequest`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`

#### `form_valid(self, form) -> HttpResponseRedirect`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`
- **تفاوت**: `warehouse_request` به issue link نمی‌شود (فقط `department_unit`)

#### `get_fieldsets(self) -> list`
- مشابه `IssuePermanentCreateFromWarehouseRequestView`

**تفاوت‌ها**:
- Session key: `warehouse_request_{pk}_issue_consignment_data`
- `warehouse_request` به issue document link نمی‌شود

---

## نکات مهم

### 1. Session Data
- داده‌ها از session خوانده می‌شوند (که توسط `CreateIssueFromWarehouseRequestView` تنظیم شده)
- Session key format: `warehouse_request_{pk}_issue_{issue_type}_data`
- Session data شامل: `warehouse_request_id`, `quantity`, `notes`
- بعد از successful creation، session data پاک می‌شود

### 2. Initial Data Population
- Formset با initial data از warehouse request populate می‌شود
- Form با warehouse request data pre-fill می‌شود
- Quantity از session استفاده می‌شود (نه از warehouse request)

### 3. Warehouse Request Linking
- **Permanent Issue**: `warehouse_request` به issue document link می‌شود
- **Consumption/Consignment Issue**: `warehouse_request` link نمی‌شود (فقط `department_unit` کپی می‌شود)
- `department_unit` از warehouse request کپی می‌شود

### 4. Validation
- Formset باید valid باشد
- باید حداقل یک valid line با item وجود داشته باشد
- اگر valid lines = 0، document حذف می‌شود

### 5. Workflow
1. User در `CreateIssueFromWarehouseRequestView` quantity را انتخاب می‌کند
2. Data در session ذخیره می‌شود
3. Redirect به این view
4. این view از session data استفاده می‌کند
5. Issue ایجاد می‌شود
6. Session data پاک می‌شود

---

## الگوهای مشترک

1. **Mixin Usage**: از `LineFormsetMixin` و `ReceiptFormMixin` استفاده می‌کنند
2. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Company Filtering**: تمام queries بر اساس `active_company_id` فیلتر می‌شوند
4. **Session Management**: از session برای انتقال data استفاده می‌کنند
5. **Error Handling**: خطاها با messages نمایش داده می‌شوند

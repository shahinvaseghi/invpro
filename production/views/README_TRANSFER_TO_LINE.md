# production/views/transfer_to_line.py - Transfer to Line Views (Complete Documentation)

**هدف**: Views برای مدیریت درخواست‌های انتقال به خط تولید در ماژول production

این فایل شامل views برای:
- TransferToLineListView: فهرست درخواست‌های انتقال
- TransferToLineCreateView: ایجاد درخواست انتقال جدید
- TransferToLineUpdateView: ویرایش درخواست انتقال (فقط extra items)
- TransferToLineDetailView: نمایش جزئیات درخواست انتقال
- TransferToLineDeleteView: حذف درخواست انتقال
- TransferToLineApproveView: تایید درخواست انتقال
- TransferToLineRejectView: رد درخواست انتقال
- TransferToLineQCApproveView: تایید QC برای درخواست انتقال (scrap replacement)
- TransferToLineQCRejectView: رد QC برای درخواست انتقال (scrap replacement)
- TransferToLineCreateWarehouseTransferView: ایجاد دستی warehouse transfer
- TransferToLineUnlockView: باز کردن قفل درخواست انتقال

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `inventory.utils.codes`: `generate_sequential_code`
- `production.forms`: `TransferToLineForm`, `TransferToLineItemFormSet`
- `production.models`: `TransferToLine`, `TransferToLineItem`, `ProductOrder`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.views.View`
- `django.contrib.messages`
- `django.db.transaction`
- `django.http.HttpResponseRedirect`, `JsonResponse`
- `django.urls.reverse_lazy`
- `django.utils.timezone`
- `django.utils.translation.gettext_lazy`

---

## TransferToLineListView

**Type**: `BaseDocumentListView` (از `shared.views.base`)

**Template**: `production/transfer_to_line_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `TransferToLine`
- `template_name`: `'production/transfer_to_line_list.html'`
- `context_object_name`: `'transfers'`
- `paginate_by`: `50`
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'view_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، select_related، و prefetch_related برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `TransferToLine.objects.none()` برمی‌گرداند
3. فیلتر: `TransferToLine.objects.filter(company_id=active_company_id)`
4. **select_related**: `'order'`, `'order__bom'`, `'order__finished_item'`, `'approved_by'`
5. **prefetch_related**: `'items'`
6. مرتب‌سازی: `order_by('-transfer_date', 'transfer_code')` (جدیدترین اول)
7. queryset را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/transfer-requests/`

---

## TransferToLineCreateView

**Type**: `BaseMultipleDocumentCreateView` (از `shared.views.base_additional`)

**Template**: `production/transfer_to_line_form.html`

**Form**: `TransferToLineForm`

**Formset**: `TransferToLineItemFormSet`

**Success URL**: `production:transfer_requests`

**Attributes**:
- `model`: `TransferToLine`
- `form_class`: `TransferToLineForm`
- `template_name`: `'production/transfer_to_line_form.html'`
- `success_url`: `reverse_lazy('production:transfer_requests')`
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `request.session.get('active_company_id')` اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title` و `formset`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `form_title = _('Create Transfer Request')`
3. **ساخت formset**:
   - دریافت `instance` (در CreateView، `self.object` ممکن است None باشد)
   - اگر `request.POST`: از POST data
   - در غیر این صورت: empty formset
   - `form_kwargs={'company_id': active_company_id}`
4. اضافه کردن `formset` به context
5. context را برمی‌گرداند

#### `form_valid(self, form: TransferToLineForm) -> HttpResponseRedirect`

**توضیح**: ذخیره transfer request و ایجاد items از BOM.

**پارامترهای ورودی**:
- `form`: فرم معتبر `TransferToLineForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. بررسی `active_company_id` (اگر وجود نداشته باشد، error و `form_invalid` برمی‌گرداند)
2. تنظیم `form.instance.company_id`, `created_by`, `status = PENDING_APPROVAL`
3. تولید `transfer_code`:
   - اگر `transfer_code` وجود نداشته باشد:
     - استفاده از `generate_sequential_code()` با prefix `'TR'` و width `8`
4. ذخیره transfer header با `super().form_valid(form)`
5. ساخت formset از POST data با instance
6. ذخیره extra items از formset:
   - اگر formset valid باشد:
     - برای هر item form:
       - اگر valid و not deleted باشد:
         - ذخیره با `commit=False`
         - تنظیم `transfer`, `company_id`, `is_extra = 1`, `created_by`
         - ذخیره item
7. ایجاد items از BOM:
   - اگر `order` و `order.bom` موجود باشند:
     - برای هر `BOMMaterial`:
       - محاسبه `quantity_required = quantity_planned × quantity_per_unit`
       - پیدا کردن `source_warehouse` از `ItemWarehouse` (اولین allowed warehouse)
       - اگر warehouse پیدا نشد:
         - نمایش warning message
         - skip کردن item
       - تلاش برای پیدا کردن `destination_work_center` از process (فعلاً None)
       - ایجاد `TransferToLineItem`:
         - تنظیم `material_item`, `material_item_code`
         - تنظیم `quantity_required`, `unit`
         - تنظیم `source_warehouse`, `source_warehouse_code`
         - تنظیم `material_scrap_allowance` از BOM
         - تنظیم `is_extra = 0` (از BOM)
8. نمایش پیام موفقیت
9. بازگشت response

**نکات مهم**:
- از `@transaction.atomic` decorator استفاده می‌کند
- Items از BOM به صورت خودکار ایجاد می‌شوند (`is_extra = 0`)
- Extra items از formset ذخیره می‌شوند (`is_extra = 1`)
- اگر warehouse برای item پیدا نشد، warning نمایش می‌دهد و item را skip می‌کند

**URL**: `/production/transfer-requests/create/`

---

## TransferToLineUpdateView

**Type**: `BaseFormsetUpdateView, EditLockProtectedMixin` (از `shared.views.base`)

**Template**: `production/transfer_to_line_form.html`

**Form**: `TransferToLineForm`

**Formset**: `TransferToLineItemFormSet` (فقط extra items)

**Success URL**: `production:transfer_requests`

**Attributes**:
- `model`: `TransferToLine`
- `form_class`: `TransferToLineForm`
- `template_name`: `'production/transfer_to_line_form.html'`
- `success_url`: `reverse_lazy('production:transfer_requests')`
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` از session

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `request.session.get('active_company_id')` اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند (فقط extra items در formset).

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title`, `formset`, `bom_items`, و `is_locked`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `form_title = _('Edit Transfer Request')`
3. **ساخت formset**:
   - اگر `request.POST`: از POST data
   - در غیر این صورت: از instance
   - `form_kwargs={'company_id': active_company_id}`
4. **فیلتر formset queryset**: `formset.queryset = formset.queryset.filter(is_extra=1)` (فقط extra items)
5. اضافه کردن `formset` به context
6. اضافه کردن `bom_items = object.items.filter(is_extra=0)` (BOM items - read-only)
7. اضافه کردن `is_locked = object.is_locked == 1`
8. context را برمی‌گرداند

**Context Variables اضافه شده**:
- `form_title`: `_('Edit Transfer Request')`
- `formset`: `TransferToLineItemFormSet` (فقط extra items با `is_extra=1`)
- `bom_items`: QuerySet از BOM items (read-only، `is_extra=0`)
- `is_locked`: Boolean (آیا transfer قفل شده است)

---

#### `form_valid(self, form: TransferToLineForm) -> HttpResponseRedirect`

**توضیح**: ذخیره transfer request و extra items (فقط اگر قابل ویرایش باشد).

**پارامترهای ورودی**:
- `form`: فرم معتبر `TransferToLineForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. بررسی `is_locked`:
   - اگر `is_locked == 1` باشد:
     - نمایش error message
     - redirect به success URL (بدون ذخیره)
2. بررسی `status`:
   - اگر `status != PENDING_APPROVAL` باشد:
     - نمایش error message
     - redirect به success URL (بدون ذخیره)
3. تنظیم `form.instance.edited_by = request.user`
4. ذخیره transfer header با `super().form_valid(form)`
5. ساخت formset از POST data:
   - فیلتر queryset به فقط `is_extra=1`
6. ذخیره formset:
   - اگر formset valid باشد:
     - فراخوانی `formset.save()`
7. نمایش پیام موفقیت
8. بازگشت response

**نکات مهم**:
- فقط extra items قابل ویرایش هستند (`is_extra=1`)
- BOM items read-only هستند (`is_extra=0`)
- فقط اگر `status=PENDING_APPROVAL` باشد قابل ویرایش است
- اگر `is_locked=1` باشد، قابل ویرایش نیست
- از `@transaction.atomic` decorator استفاده می‌کند

**URL**: `/production/transfer-requests/<pk>/edit/`

---

## TransferToLineDetailView

### `TransferToLineDetailView`

**توضیح**: نمایش جزئیات Transfer to Line Request (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `TransferToLine`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**Context Variables**:
- `object`: TransferToLine instance
- `detail_title`: `_('View Transfer Request')`
- `info_banner`: لیست اطلاعات اصلی (transfer_code, transfer_date, status, qc_status اگر موجود باشد)
- `detail_sections`: لیست sections برای نمایش:
  - Request Information: product_order (با finished_item اگر موجود باشد), approved_by (اگر موجود باشد), notes (اگر موجود باشد)
  - Transfer Items: table با headers (Material Item, Quantity Required, Unit, Source Warehouse, Scrap Allowance, Extra) و data rows
  - Notes: اگر notes موجود باشد
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Transfer قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related و prefetch_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. اعمال `select_related('order', 'order__bom', 'order__finished_item', 'approved_by', 'qc_approved_by', 'created_by', 'edited_by')`
  3. اعمال `prefetch_related('items__material_item', 'items__source_warehouse', 'items__destination_work_center')`
  4. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Transfer Code (type: 'code')
     - Transfer Date
     - Status
     - QC Status (اگر موجود باشد)
  3. ساخت `detail_sections`:
     - **Request Information**: product_order (با finished_item اگر موجود باشد), approved_by (اگر موجود باشد), notes (اگر موجود باشد)
     - **Transfer Items**: اگر `items.exists()` باشد:
       - ساخت table با headers: Material Item, Quantity Required, Unit, Source Warehouse, Scrap Allowance, Extra
       - ساخت data rows از `items.all()`
       - اضافه کردن section با type='table'
     - **Notes**: اگر notes موجود باشد
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Transfer Requests

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Transfer Request

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Transfer قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/production/transfer-requests/<pk>/`

---

## TransferToLineDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:transfer_requests`

**Attributes**:
- `model`: `TransferToLine`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:transfer_requests')`
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. اعمال `select_related('order')`
  3. بازگشت queryset

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: TransferToLine را حذف می‌کند (بعد از بررسی is_locked).

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. دریافت object: `self.object = self.get_object()`
2. بررسی `is_locked`:
   - اگر `is_locked == 1`:
     - خطا: "This transfer request is locked and cannot be deleted."
     - redirect به `success_url` (بدون حذف)
3. فراخوانی `super().delete(request, *args, **kwargs)` (که TransferToLine را حذف می‌کند و redirect می‌کند)

**نکات مهم**:
- اگر `is_locked=1` باشد، قابل حذف نیست

**URL**: `/production/transfer-requests/<pk>/delete/`

---

## TransferToLineApproveView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'approve'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> JsonResponse`

**توضیح**: تایید transfer request و قفل کردن آن.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args, **kwargs`: آرگومان‌های اضافی (شامل `pk`)

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با success یا error message

**منطق**:
1. دریافت `transfer_id` از `kwargs.get('pk')`
2. بررسی `active_company_id`:
   - اگر وجود نداشته باشد:
     - بازگشت `JsonResponse` با error و status `400`
3. دریافت transfer object:
   - اگر پیدا نشد:
     - بازگشت `JsonResponse` با error و status `404`
4. بررسی authorization:
   - اگر `transfer.approved_by != request.user`:
     - بازگشت `JsonResponse` با error و status `403`
5. بررسی status:
   - اگر `status == APPROVED`:
     - بازگشت `JsonResponse` با error و status `400`
   - اگر `status == REJECTED`:
     - بازگشت `JsonResponse` با error و status `400`
6. Approve در `transaction.atomic()`:
   - **بررسی scrap replacement**:
     - اگر `is_scrap_replacement == 1`:
       - تنظیم `status = PENDING_QC_APPROVAL`
       - تنظیم `qc_status = PENDING_APPROVAL`
       - ذخیره transfer
       - نمایش پیام: "Transfer request approved. Waiting for QC approval."
     - در غیر این صورت (regular approval):
       - تنظیم `status = APPROVED`
       - تنظیم `is_locked = 1`
       - تنظیم `locked_at = timezone.now()`
       - تنظیم `locked_by = request.user`
       - ذخیره transfer
       - **ایجاد IssueConsumption document**:
         - ساخت IssueConsumption header با `generate_document_code`
         - ساخت IssueConsumptionLine برای هر TransferToLineItem
         - تنظیم `consumption_type='production_transfer'`
         - تنظیم `production_transfer_id` و `production_transfer_code`
         - تنظیم `work_line` از `destination_work_center`
       - **ایجاد Warehouse Transfer document**:
         - فراخوانی `create_warehouse_transfer_for_transfer_to_line()`
         - اگر موفق باشد، نمایش پیام موفقیت
         - اگر خطا باشد، نمایش warning (بدون fail کردن approval)
7. بازگشت `JsonResponse` با success message و warehouse_transfer info (اگر ایجاد شده باشد)

**Error Responses**:
- `400`: Company not selected یا already approved/rejected
- `403`: User not authorized
- `404`: Transfer not found

**نکات مهم**:
- از `transaction.atomic()` استفاده می‌کند
- **Scrap Replacement Workflow**: اگر `is_scrap_replacement=1` باشد، status به `PENDING_QC_APPROVAL` تغییر می‌کند و نیاز به QC approval دارد
- **Regular Approval**: بعد از approve، transfer قفل می‌شود (`is_locked=1`) و IssueConsumption و Warehouse Transfer ایجاد می‌شوند
- فقط `approved_by` می‌تواند approve کند
- ایجاد IssueConsumption و Warehouse Transfer ممکن است fail شود (warning نمایش داده می‌شود اما approval موفق است)

**URL**: `/production/transfer-requests/<pk>/approve/`

---

## TransferToLineRejectView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'reject'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> JsonResponse`

**توضیح**: رد transfer request.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args, **kwargs`: آرگومان‌های اضافی (شامل `pk`)

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با success یا error message

**منطق**:
1. دریافت `transfer_id` از `kwargs.get('pk')`
2. بررسی `active_company_id`:
   - اگر وجود نداشته باشد:
     - بازگشت `JsonResponse` با error و status `400`
3. دریافت transfer object:
   - اگر پیدا نشد:
     - بازگشت `JsonResponse` با error و status `404`
4. بررسی authorization:
   - اگر `transfer.approved_by != request.user`:
     - بازگشت `JsonResponse` با error و status `403`
5. بررسی status:
   - اگر `status == APPROVED`:
     - بازگشت `JsonResponse` با error و status `400`
   - اگر `status == REJECTED`:
     - بازگشت `JsonResponse` با error و status `400`
6. Reject در `transaction.atomic()`:
   - تنظیم `status = REJECTED`
   - ذخیره transfer
7. نمایش پیام موفقیت
8. بازگشت `JsonResponse` با success message

**Error Responses**:
- `400`: Company not selected یا already approved/rejected
- `403`: User not authorized
- `404`: Transfer not found

**نکات مهم**:
- از `transaction.atomic()` استفاده می‌کند
- بعد از reject، transfer قفل نمی‌شود (برخلاف approve)
- فقط `approved_by` می‌تواند reject کند

**URL**: `/production/transfer-requests/<pk>/reject/`

---

## TransferToLineQCApproveView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.transfer_requests.qc_approval'`
- `required_action`: `'approve'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> JsonResponse`
- **Parameters**: `request`, `*args`, `**kwargs` (شامل `pk`)
- **Returns**: `JsonResponse` با success یا error message
- **Logic**:
  1. دریافت `transfer_id` از `kwargs.get('pk')`
  2. بررسی `active_company_id` (اگر وجود نداشته باشد، return error 400)
  3. دریافت transfer object (اگر پیدا نشد، return error 404)
  4. بررسی scrap replacement: اگر `is_scrap_replacement != 1` باشد، return error 400
  5. بررسی authorization: اگر `transfer.qc_approved_by != request.user` باشد، return error 403
  6. بررسی QC status: اگر already approved/rejected باشد، return error 400
  7. بررسی status: اگر `status != PENDING_QC_APPROVAL` باشد، return error 400
  8. Approve QC در `transaction.atomic()`:
     - تنظیم `qc_status = APPROVED`
     - تنظیم `status = APPROVED`
     - تنظیم `is_locked = 1`
     - تنظیم `locked_at = timezone.now()`
     - تنظیم `locked_by = request.user`
     - ذخیره transfer
     - **ایجاد IssueConsumption document** (مشابه regular approval)
     - **ایجاد Warehouse Transfer document** (مشابه regular approval)
  9. بازگشت `JsonResponse` با success message

**Error Responses**:
- `400`: Company not selected، not scrap replacement، already QC approved/rejected، یا status not pending QC approval
- `403`: User not authorized
- `404`: Transfer not found

**نکات مهم**:
- فقط برای scrap replacement transfers (`is_scrap_replacement=1`)
- فقط `qc_approved_by` می‌تواند QC approve کند
- بعد از QC approve، transfer قفل می‌شود و IssueConsumption و Warehouse Transfer ایجاد می‌شوند

**URL**: `/production/transfer-requests/<pk>/qc-approve/`

---

## TransferToLineQCRejectView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.transfer_requests.qc_approval'`
- `required_action`: `'reject'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> JsonResponse`
- **Parameters**: `request`, `*args`, `**kwargs` (شامل `pk`)
- **Returns**: `JsonResponse` با success یا error message
- **Logic**:
  1. دریافت `transfer_id` از `kwargs.get('pk')`
  2. بررسی `active_company_id` (اگر وجود نداشته باشد، return error 400)
  3. دریافت transfer object (اگر پیدا نشد، return error 404)
  4. بررسی scrap replacement: اگر `is_scrap_replacement != 1` باشد، return error 400
  5. بررسی authorization: اگر `transfer.qc_approved_by != request.user` باشد، return error 403
  6. بررسی QC status: اگر already approved/rejected باشد، return error 400
  7. Reject QC در `transaction.atomic()`:
     - تنظیم `qc_status = REJECTED`
     - تنظیم `status = REJECTED`
     - ذخیره transfer
  8. بازگشت `JsonResponse` با success message

**Error Responses**:
- `400`: Company not selected، not scrap replacement، یا already QC approved/rejected
- `403`: User not authorized
- `404`: Transfer not found

**نکات مهم**:
- فقط برای scrap replacement transfers (`is_scrap_replacement=1`)
- فقط `qc_approved_by` می‌تواند QC reject کند
- بعد از QC reject، transfer status به REJECTED تغییر می‌کند

**URL**: `/production/transfer-requests/<pk>/qc-reject/`

---

## TransferToLineCreateWarehouseTransferView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'approve'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> JsonResponse`
- **Parameters**: `request`, `*args`, `**kwargs` (شامل `pk`)
- **Returns**: `JsonResponse` با success یا error message
- **Logic**:
  1. دریافت `transfer_id` از `kwargs.get('pk')`
  2. بررسی `active_company_id` (اگر وجود نداشته باشد، return error 400)
  3. دریافت transfer object (اگر پیدا نشد， return error 404)
  4. بررسی status: اگر `status != APPROVED` باشد، return error 400
  5. بررسی existing warehouse transfer: اگر active warehouse transfer موجود باشد، return error 400 با warehouse_transfer_code و warehouse_transfer_url
  6. ایجاد Warehouse Transfer:
     - فراخوانی `create_warehouse_transfer_for_transfer_to_line()`
     - اگر موفق باشد، return success با warehouse_transfer_code و warehouse_transfer_url
     - اگر خطا باشد، return error 400/500
  7. بازگشت `JsonResponse` با success message

**Error Responses**:
- `400`: Company not selected، status not approved، یا warehouse transfer already exists
- `404`: Transfer not found
- `500`: Error creating warehouse transfer

**نکات مهم**:
- فقط برای approved transfers (`status=APPROVED`)
- فقط یک active warehouse transfer می‌تواند وجود داشته باشد
- برای ایجاد دستی warehouse transfer استفاده می‌شود (اگر در approve ایجاد نشده باشد)

**URL**: `/production/transfer-requests/<pk>/create-warehouse-transfer/`

---

## TransferToLineUnlockView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'unlock'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> JsonResponse`
- **Parameters**: `request`, `*args`, `**kwargs` (شامل `pk`)
- **Returns**: `JsonResponse` با success یا error message
- **Logic**:
  1. دریافت `transfer_id` از `kwargs.get('pk')`
  2. بررسی `active_company_id` (اگر وجود نداشته باشد، return error 400)
  3. دریافت transfer object (اگر پیدا نشد، return error 404)
  4. بررسی lock status: اگر `is_locked != 1` باشد، return error 400
  5. Unlock transfer در `transaction.atomic()`:
     - تنظیم `is_locked = 0`
     - تنظیم `locked_at = None`
     - تنظیم `locked_by = None`
     - ذخیره transfer
  6. بازگشت `JsonResponse` با success message

**Error Responses**:
- `400`: Company not selected یا transfer not locked
- `404`: Transfer not found

**نکات مهم**:
- فقط برای locked transfers (`is_locked=1`)
- بعد از unlock، transfer قابل ویرایش می‌شود

**URL**: `/production/transfer-requests/<pk>/unlock/`

---

## نکات مهم

### 1. BOM Items vs Extra Items
- BOM items (`is_extra=0`): از BOM به صورت خودکار ایجاد می‌شوند، read-only
- Extra items (`is_extra=1`): از formset ایجاد می‌شوند، قابل ویرایش

### 2. Status Management
- `PENDING_APPROVAL`: قابل ویرایش
- `APPROVED`: قفل شده، قابل ویرایش نیست
- `REJECTED`: قابل ویرایش نیست

### 3. Lock Mechanism
- بعد از approve، transfer قفل می‌شود (`is_locked=1`)
- قفل شده قابل ویرایش یا حذف نیست

### 4. Authorization
- فقط `approved_by` می‌تواند approve/reject کند

### 5. Code Generation
- `transfer_code` به صورت خودکار با prefix `'TR'` تولید می‌شود

---

## Generic Templates

تمام templates به generic templates منتقل شده‌اند:

### Transfer to Line List
- **Template**: `production/transfer_to_line_list.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `page_title`: عنوان صفحه
  - `breadcrumb_extra`: مسیر breadcrumb
  - `page_actions`: دکمه Create
  - `table_headers`: هدرهای جدول
  - `table_rows`: ردیف‌های جدول با status badges و action buttons
  - `pagination`: صفحه‌بندی
  - `extra_scripts`: JavaScript برای approve/reject functions و warehouse transfer creation

#### JavaScript Functions

**CSRF Token Management**:
- `getCSRFToken()`: تابع کمکی برای دریافت CSRF token از سه منبع:
  1. Cookie (اولویت اول - قابل اعتمادترین روش)
  2. Hidden input با نام `csrfmiddlewaretoken` (fallback)
  3. Meta tag با نام `csrf-token` (آخرین راه حل)
- **نکته مهم**: این تابع باید در یک تگ `<script>` جداگانه تعریف شود و قبل از لود شدن فایل `approval-actions.js` قرار گیرد تا در scope global در دسترس باشد.

**Approval/Rejection Functions**:
- `approveTransfer(transferId)`: تایید transfer request
- `rejectTransfer(transferId)`: رد transfer request
- `approveQCTransfer(transferId)`: تایید QC برای scrap replacement transfers
- `rejectQCTransfer(transferId)`: رد QC برای scrap replacement transfers
- این توابع از `approval-actions.js` استفاده می‌کنند و با `useFetch: true` از fetch API استفاده می‌کنند.

**Warehouse Transfer Functions**:
- `createWarehouseTransfer(transferId)`: ایجاد دستی warehouse transfer برای یک transfer request
  - بررسی confirmation از کاربر
  - دریافت CSRF token با `getCSRFToken()`
  - ارسال POST request به `/production/transfer-requests/<pk>/create-warehouse-transfer/`
  - نمایش پیام موفقیت/خطا
  - Reload صفحه در صورت موفقیت
- `unlockTransfer(transferId)`: باز کردن قفل transfer request
  - بررسی confirmation از کاربر
  - دریافت CSRF token با `getCSRFToken()`
  - ارسال POST request به `/production/transfer-requests/<pk>/unlock/`
  - Reload صفحه در صورت موفقیت

**Script Loading Order**:
1. تعریف `getCSRFToken()` در یک تگ `<script>` جداگانه
2. بستن تگ `<script>` قبل از لود شدن فایل‌های خارجی
3. لود شدن `approval-actions.js`
4. تعریف wrapper functions در تگ `<script>` بعدی

**نکات مهم**:
- تگ `<script>` که `getCSRFToken()` را تعریف می‌کند باید به درستی بسته شود تا تابع در scope global در دسترس باشد
- اگر تگ `<script>` بسته نشود، خطای `ReferenceError: getCSRFToken is not defined` رخ می‌دهد
- تمام توابع از fetch API استفاده می‌کنند و JSON response را پردازش می‌کنند

### Transfer to Line Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات transfer (Transfer Code, Product Order, Transfer Date, Status, Total Items)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Transfer to Line Form
- **Template**: `shared/generic/generic_form.html` (extended by `production/transfer_to_line_form.html`)
- **Blocks Overridden**:
  - `breadcrumb_extra`: اضافه کردن مسیر Production و Transfer to Line Requests
  - `before_form`: نمایش info banner برای transfer_code، transfer_date، status، و lock status
  - `form_sections`: فیلدهای اصلی فرم (order, transfer_date, approved_by, notes)
  - `form_extra`: بخش BOM Items (read-only table) و Extra Request Items (formset با cascading filters)
  - `extra_styles`: CSS برای table-responsive و formset table
  - `form_scripts`: JavaScript برای Jalali DatePicker، formset management، و cascading filters (Type → Category → Subcategory → Item → Unit)
- **Context Variables**:
  - `form_title`: عنوان فرم ("Create Transfer Request" یا "Edit Transfer Request")
  - `breadcrumbs`: مسیر breadcrumb
  - `cancel_url`: URL برای لغو
  - `form_id`: 'transfer-form'
  - `formset`: TransferToLineItemFormSet برای extra items
  - `bom_items`: لیست BOM items (read-only) - فقط در edit mode
  - `is_locked`: وضعیت قفل بودن transfer

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Transaction Management**: از `@transaction.atomic` برای atomic operations استفاده می‌شود
4. **BOM Integration**: Items از BOM به صورت خودکار ایجاد می‌شوند

---

## Troubleshooting

### مشکل: `ReferenceError: getCSRFToken is not defined`

**علت**: تگ `<script>` که تابع `getCSRFToken()` را تعریف می‌کند به درستی بسته نشده است.

**علائم**:
- خطای `Uncaught ReferenceError: getCSRFToken is not defined` در console
- دکمه‌های "Issue Transfer" و "Create Purchase Request" کار نمی‌کنند
- خطای `SyntaxError: Unexpected token '<'` در console

**راه حل**:
1. اطمینان حاصل کنید که تگ `<script>` که `getCSRFToken()` را تعریف می‌کند به درستی بسته شده است:
```html
<script>
function getCSRFToken() {
  // ... function code ...
}
</script>  <!-- این تگ باید بسته شود -->
```

2. ترتیب لود شدن اسکریپت‌ها باید به این صورت باشد:
   - ابتدا تعریف `getCSRFToken()` و بستن تگ `<script>`
   - سپس لود شدن `approval-actions.js`
   - در نهایت تعریف wrapper functions

**مثال صحیح**:
```html
{% block extra_scripts %}
{% csrf_token %}
<script>
function getCSRFToken() {
  // ... function code ...
}
</script>

{% load static %}
<script src="{% static 'js/approval-actions.js' %}"></script>
<script>
function createWarehouseTransfer(transferId) {
  const csrfToken = getCSRFToken();  // حالا در دسترس است
  // ... rest of function ...
}
</script>
{% endblock %}
```

### مشکل: دکمه‌های Approve/Reject کار نمی‌کنند

**علت**: فایل `approval-actions.js` لود نشده یا توابع `approveObject`/`rejectObject` در دسترس نیستند.

**راه حل**:
1. بررسی کنید که فایل `approval-actions.js` در مسیر `static/js/approval-actions.js` وجود دارد
2. بررسی کنید که تگ `<script src="...">` به درستی لود می‌شود
3. در console مرورگر بررسی کنید که آیا خطای 404 برای فایل JavaScript وجود دارد


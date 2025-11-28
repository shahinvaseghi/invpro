# production/views/transfer_to_line.py - Transfer to Line Views (Complete Documentation)

**هدف**: Views برای مدیریت درخواست‌های انتقال به خط تولید در ماژول production

این فایل شامل views برای:
- TransferToLineListView: فهرست درخواست‌های انتقال
- TransferToLineCreateView: ایجاد درخواست انتقال جدید
- TransferToLineUpdateView: ویرایش درخواست انتقال (فقط extra items)
- TransferToLineDeleteView: حذف درخواست انتقال
- TransferToLineApproveView: تایید درخواست انتقال
- TransferToLineRejectView: رد درخواست انتقال

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

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/transfer_to_line_list.html`

**Attributes**:
- `model`: `TransferToLine`
- `template_name`: `'production/transfer_to_line_list.html'`
- `context_object_name`: `'transfers'`
- `paginate_by`: `50`
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'view_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company، `select_related('order', 'order__bom', 'order__finished_item', 'approved_by')`، `prefetch_related('items')`، مرتب بر اساس `-transfer_date`, `transfer_code`
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/transfer-requests/`

---

## TransferToLineCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

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

#### `get_form_kwargs() -> Dict[str, Any]`
- اضافه کردن `company_id` به form

#### `get_context_data(**kwargs) -> Dict[str, Any]`
- اضافه کردن `formset` (با instance=None در create mode)

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

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

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

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن formset (فقط extra items) و bom_items (read-only) به context.

**Context Variables**:
- `form_title`: `_('Edit Transfer Request')`
- `formset`: `TransferToLineItemFormSet` (فقط extra items با `is_extra=1`)
- `bom_items`: QuerySet از BOM items (read-only، `is_extra=0`)
- `is_locked`: Boolean (آیا transfer قفل شده است)

**منطق**:
1. دریافت context از `super().get_context_data()`
2. اضافه کردن `form_title`
3. ساخت formset:
   - اگر POST: از POST data
   - اگر GET: از instance
4. فیلتر کردن formset queryset به فقط `is_extra=1`
5. اضافه کردن `bom_items` از `object.items.filter(is_extra=0)`
6. اضافه کردن `is_locked` از `object.is_locked == 1`
7. بازگشت context

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

## TransferToLineDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/transfer_to_line_confirm_delete.html`

**Success URL**: `production:transfer_requests`

**Attributes**:
- `model`: `TransferToLine`
- `template_name`: `'production/transfer_to_line_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:transfer_requests')`
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'delete_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: بررسی `is_locked` قبل از حذف

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
6. Approve و lock در `transaction.atomic()`:
   - تنظیم `status = APPROVED`
   - تنظیم `is_locked = 1`
   - تنظیم `locked_at = timezone.now()`
   - تنظیم `locked_by = request.user`
   - ذخیره transfer
7. نمایش پیام موفقیت
8. بازگشت `JsonResponse` با success message

**Error Responses**:
- `400`: Company not selected یا already approved/rejected
- `403`: User not authorized
- `404`: Transfer not found

**نکات مهم**:
- از `transaction.atomic()` استفاده می‌کند
- بعد از approve، transfer قفل می‌شود (`is_locked=1`)
- فقط `approved_by` می‌تواند approve کند

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

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Transaction Management**: از `@transaction.atomic` برای atomic operations استفاده می‌شود
4. **BOM Integration**: Items از BOM به صورت خودکار ایجاد می‌شوند


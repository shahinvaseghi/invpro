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

#### `form_valid(form: TransferToLineForm) -> HttpResponseRedirect`
**منطق**:
1. تنظیم `company_id`, `created_by`, `status=PENDING_APPROVAL`
2. تولید `transfer_code` با prefix `'TR'`
3. ذخیره transfer header
4. ذخیره extra items از formset (`is_extra=1`)
5. ایجاد items از BOM:
   - محاسبه `quantity_required = quantity_planned × quantity_per_unit`
   - پیدا کردن `source_warehouse` از `ItemWarehouse`
   - ایجاد `TransferToLineItem` برای هر BOM material (`is_extra=0`)

**نکات مهم**:
- از `@transaction.atomic` استفاده می‌کند
- Items از BOM به صورت خودکار ایجاد می‌شوند
- Extra items از formset ذخیره می‌شوند

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

#### `get_context_data(**kwargs) -> Dict[str, Any]`
- اضافه کردن `formset` (فقط extra items با `is_extra=1`)
- اضافه کردن `bom_items` (read-only، `is_extra=0`)
- اضافه کردن `is_locked`

#### `form_valid(form: TransferToLineForm) -> HttpResponseRedirect`
**منطق**:
1. بررسی `is_locked` و `status` (فقط `PENDING_APPROVAL` قابل ویرایش)
2. تنظیم `edited_by`
3. ذخیره transfer header
4. ذخیره extra items از formset

**نکات مهم**:
- فقط extra items قابل ویرایش هستند
- BOM items read-only هستند
- فقط اگر `status=PENDING_APPROVAL` باشد قابل ویرایش است

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

#### `post(request, *args, **kwargs) -> JsonResponse`
**منطق**:
1. دریافت `transfer_id` از kwargs
2. بررسی `active_company_id`
3. دریافت transfer object
4. بررسی authorization (user باید `approved_by` باشد)
5. بررسی status (نباید approved یا rejected باشد)
6. Approve و lock:
   - `status = APPROVED`
   - `is_locked = 1`
   - `locked_at = timezone.now()`
   - `locked_by = request.user`
7. بازگشت `JsonResponse` با success message

**نکات مهم**:
- از `transaction.atomic` استفاده می‌کند
- بعد از approve، transfer قفل می‌شود

**URL**: `/production/transfer-requests/<pk>/approve/`

---

## TransferToLineRejectView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.transfer_requests'`
- `required_action`: `'reject'`

**متدها**:

#### `post(request, *args, **kwargs) -> JsonResponse`
**منطق**:
1. دریافت `transfer_id` از kwargs
2. بررسی `active_company_id`
3. دریافت transfer object
4. بررسی authorization (user باید `approved_by` باشد)
5. بررسی status (نباید approved یا rejected باشد)
6. Reject:
   - `status = REJECTED`
7. بازگشت `JsonResponse` با success message

**نکات مهم**:
- از `transaction.atomic` استفاده می‌کند
- بعد از reject، transfer قفل نمی‌شود

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


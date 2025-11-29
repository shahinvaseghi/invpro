# production/views/performance_record.py - Performance Record Views (Complete Documentation)

**هدف**: Views برای مدیریت ثبت عملکرد تولید در ماژول production

این فایل شامل views برای:
- PerformanceRecordListView: فهرست ثبت‌های عملکرد
- PerformanceRecordCreateView: ایجاد ثبت عملکرد جدید
- PerformanceRecordUpdateView: ویرایش ثبت عملکرد
- PerformanceRecordDeleteView: حذف ثبت عملکرد
- PerformanceRecordApproveView: تایید ثبت عملکرد
- PerformanceRecordRejectView: رد ثبت عملکرد
- PerformanceRecordCreateReceiptView: ایجاد receipt از ثبت عملکرد تایید شده

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`
- `inventory.utils.codes`: `generate_sequential_code`
- `production.forms`: `PerformanceRecordForm`, `PerformanceRecordMaterialFormSet`, `PerformanceRecordPersonFormSet`, `PerformanceRecordMachineFormSet`
- `production.models`: `PerformanceRecord`, `PerformanceRecordMaterial`, `PerformanceRecordPerson`, `PerformanceRecordMachine`, `ProductOrder`, `TransferToLine`, `TransferToLineItem`, `Process`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.views.View`
- `django.contrib.messages`
- `django.db.transaction`
- `django.http.HttpResponseRedirect`, `JsonResponse`
- `django.shortcuts.get_object_or_404`, `redirect`
- `django.urls.reverse_lazy`
- `django.utils.timezone`
- `django.utils.translation.gettext_lazy`

---

## PerformanceRecordListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/performance_record_list.html`

**Attributes**:
- `model`: `PerformanceRecord`
- `template_name`: `'production/performance_record_list.html'`
- `context_object_name`: `'performance_records'`
- `paginate_by`: `50`
- `feature_code`: `'production.performance_records'`
- `required_action`: `'view_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، select_related، prefetch_related، و permission-based filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations و permission filtering

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `PerformanceRecord.objects.none()` برمی‌گرداند
3. فیلتر: `PerformanceRecord.objects.filter(company_id=active_company_id)`
4. **select_related**: `'order'`, `'order__bom'`, `'order__finished_item'`, `'order__process'`, `'transfer'`, `'approved_by'`
5. **prefetch_related**: `'materials'`, `'persons'`, `'machines'`
6. مرتب‌سازی: `order_by('-performance_date', 'performance_code')` (جدیدترین اول)
7. **Permission-based filtering**:
   - بررسی permission `view_all` با `has_feature_permission()`
   - اگر permission ندارد: فیلتر `queryset.filter(created_by=request.user)` (فقط records خودش)
8. queryset را برمی‌گرداند

**نکات مهم**:
- اگر user permission `view_all` نداشته باشد، فقط records خودش را می‌بیند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/performance-records/`

---

## PerformanceRecordCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/performance_record_form.html`

**Form**: `PerformanceRecordForm`

**Formsets**: `PerformanceRecordMaterialFormSet`, `PerformanceRecordPersonFormSet`, `PerformanceRecordMachineFormSet`

**Success URL**: `production:performance_records`

**Attributes**:
- `model`: `PerformanceRecord`
- `form_class`: `PerformanceRecordForm`
- `template_name`: `'production/performance_record_form.html'`
- `success_url`: `reverse_lazy('production:performance_records')`
- `feature_code`: `'production.performance_records'`
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

**توضیح**: context variables را برای template اضافه می‌کند (با 3 formsets).

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title`, `active_module`, و 3 formsets

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `form_title = _('Create Performance Record')`
3. اضافه کردن `active_module = 'production'`
4. دریافت `instance` (در CreateView، `self.object` ممکن است None باشد)
5. دریافت `active_company_id` از session
6. **ساخت 3 formsets**:
   - اگر `request.POST`: از POST data
   - در غیر این صورت: empty formsets
   - `material_formset`: `form_kwargs={'company_id': active_company_id}`, prefix='materials'
   - `person_formset`: `form_kwargs={'company_id': active_company_id, 'process_id': None}`, prefix='persons' (process_id از order تنظیم می‌شود)
   - `machine_formset`: `form_kwargs={'company_id': active_company_id, 'process_id': None}`, prefix='machines' (process_id از order تنظیم می‌شود)
7. اضافه کردن formsets به context
8. context را برمی‌گرداند

**Context Variables اضافه شده**:
- `form_title`: `_('Create Performance Record')`
- `active_module`: `'production'`
- `material_formset`: `PerformanceRecordMaterialFormSet`
- `person_formset`: `PerformanceRecordPersonFormSet`
- `machine_formset`: `PerformanceRecordMachineFormSet`

#### `form_valid(form: PerformanceRecordForm) -> HttpResponseRedirect`
**منطق**:
1. تنظیم `company_id`, `created_by`
2. تولید `performance_code` با prefix `'PR-'`
3. Auto-populate از order: `quantity_planned`, `finished_item`, `unit`
4. ذخیره performance record header
5. اگر transfer انتخاب شده باشد:
   - حذف materials موجود
   - ایجاد materials از transfer items
6. اگر transfer انتخاب نشده باشد:
   - ذخیره materials از formset
7. ذخیره persons و machines از formsets
8. نمایش پیام موفقیت

**نکات مهم**:
- از `@transaction.atomic` استفاده می‌کند
- اگر transfer انتخاب شود، materials از transfer auto-populate می‌شوند
- `process_id` برای person و machine formsets از order تنظیم می‌شود

**URL**: `/production/performance-records/create/`

---

## PerformanceRecordUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/performance_record_form.html`

**Form**: `PerformanceRecordForm`

**Formsets**: `PerformanceRecordMaterialFormSet`, `PerformanceRecordPersonFormSet`, `PerformanceRecordMachineFormSet`

**Success URL**: `production:performance_records`

**Attributes**:
- `model`: `PerformanceRecord`
- `form_class`: `PerformanceRecordForm`
- `template_name`: `'production/performance_record_form.html'`
- `success_url`: `reverse_lazy('production:performance_records')`
- `feature_code`: `'production.performance_records'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering و permission-based filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با permission filtering

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `PerformanceRecord.objects.none()` برمی‌گرداند
3. فیلتر: `PerformanceRecord.objects.filter(company_id=active_company_id)`
4. **Permission-based filtering**:
   - بررسی permission `edit_other` با `has_feature_permission()`
   - اگر permission ندارد: فیلتر `queryset.filter(created_by=request.user)` (فقط records خودش)
5. queryset را برمی‌گرداند

**نکات مهم**:
- اگر user permission `edit_other` نداشته باشد، فقط records خودش را می‌بیند

---

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

**توضیح**: context variables را برای template اضافه می‌کند (با 3 formsets).

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title`, `active_module`, و 3 formsets

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `form_title = _('Edit Performance Record')`
3. اضافه کردن `active_module = 'production'`
4. دریافت `active_company_id` از session
5. دریافت `process_id` از `self.object.order.process_id` (اگر موجود باشد)
6. **ساخت 3 formsets**:
   - اگر `request.POST`: از POST data
   - در غیر این صورت: از instance
   - `material_formset`: `form_kwargs={'company_id': active_company_id}`, prefix='materials'
   - `person_formset`: `form_kwargs={'company_id': active_company_id, 'process_id': process_id}`, prefix='persons'
   - `machine_formset`: `form_kwargs={'company_id': active_company_id, 'process_id': process_id}`, prefix='machines'
7. اضافه کردن formsets به context
8. context را برمی‌گرداند

#### `form_valid(form: PerformanceRecordForm) -> HttpResponseRedirect`
**منطق**:
1. بررسی `is_locked` (اگر قفل شده باشد، قابل ویرایش نیست)
2. تنظیم `edited_by`
3. ذخیره performance record header
4. ذخیره تمام formsets

**نکات مهم**:
- فقط اگر `is_locked=False` باشد قابل ویرایش است
- `process_id` برای person و machine formsets از order تنظیم می‌شود

**URL**: `/production/performance-records/<pk>/edit/`

---

## PerformanceRecordDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/performance_record_confirm_delete.html`

**Success URL**: `production:performance_records`

**Attributes**:
- `model`: `PerformanceRecord`
- `template_name`: `'production/performance_record_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:performance_records')`
- `feature_code`: `'production.performance_records'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset() -> QuerySet`
- فیلتر بر اساس company
- اگر user permission `delete_other` نداشته باشد، فقط records خودش را نمایش می‌دهد

#### `delete(request, *args, **kwargs) -> HttpResponseRedirect`
**منطق**:
1. بررسی `is_locked` (اگر قفل شده باشد، قابل حذف نیست)
2. بررسی `status` (فقط `pending_approval` قابل حذف است)
3. حذف record

**URL**: `/production/performance-records/<pk>/delete/`

---

## PerformanceRecordApproveView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.performance_records'`
- `required_action`: `'approve'`

**متدها**:

#### `post(request, *args, **kwargs) -> HttpResponseRedirect`
**منطق**:
1. بررسی `active_company_id`
2. دریافت performance record
3. بررسی status (باید `pending_approval` باشد)
4. بررسی `is_locked` (نباید قفل شده باشد)
5. Approve و lock:
   - `status = 'approved'`
   - `approved_by = request.user`
   - `is_locked = True`
   - `locked_at = timezone.now()`
   - `locked_by = request.user`
6. نمایش پیام موفقیت

**نکات مهم**:
- بعد از approve، record قفل می‌شود

**URL**: `/production/performance-records/<pk>/approve/`

---

## PerformanceRecordRejectView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.performance_records'`
- `required_action`: `'reject'`

**متدها**:

#### `post(request, *args, **kwargs) -> HttpResponseRedirect`
**منطق**:
1. بررسی `active_company_id`
2. دریافت performance record
3. بررسی status (باید `pending_approval` باشد)
4. Reject:
   - `status = 'rejected'`
   - `approved_by = request.user`
5. نمایش پیام موفقیت

**نکات مهم**:
- بعد از reject، record قفل نمی‌شود (می‌تواند ویرایش و resubmit شود)

**URL**: `/production/performance-records/<pk>/reject/`

---

## PerformanceRecordCreateReceiptView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `POST`

**Attributes**:
- `feature_code`: `'production.performance_records'`
- `required_action`: `'create_receipt'`

**متدها**:

#### `post(request, *args, **kwargs) -> HttpResponseRedirect`
**منطق**:
1. بررسی `active_company_id`
2. دریافت performance record
3. بررسی status (باید `approved` باشد)
4. تعیین نوع receipt:
   - از POST data (`receipt_type`)
   - یا از `finished_item.requires_temporary_receipt`
5. پیدا کردن warehouse:
   - از transfer items (اگر transfer وجود دارد)
   - یا اولین enabled warehouse
6. ایجاد receipt:
   - اگر `temporary`: ایجاد `ReceiptTemporary`
   - اگر `permanent`: ایجاد `ReceiptPermanent` و `ReceiptPermanentLine`
7. Redirect به receipt detail page

**نکات مهم**:
- از `transaction.atomic` استفاده می‌کند
- فقط approved records می‌توانند receipt ایجاد کنند
- نوع receipt بر اساس `requires_temporary_receipt` تعیین می‌شود

**URL**: `/production/performance-records/<pk>/create-receipt/`

---

## نکات مهم

### 1. Permission-based Filtering
- `ListView`: اگر `view_all` permission نداشته باشد، فقط own records
- `UpdateView`: اگر `edit_other` permission نداشته باشد، فقط own records
- `DeleteView`: اگر `delete_other` permission نداشته باشد، فقط own records

### 2. Transfer Auto-population
- اگر transfer انتخاب شود، materials از transfer items auto-populate می‌شوند
- Materials موجود حذف می‌شوند و از transfer ایجاد می‌شوند

### 3. Process-based Filtering
- `person_formset` و `machine_formset` با `process_id` از order فیلتر می‌شوند
- فقط work lines مربوط به process نمایش داده می‌شوند

### 4. Lock Mechanism
- بعد از approve، record قفل می‌شود (`is_locked=True`)
- قفل شده قابل ویرایش یا حذف نیست
- بعد از reject، record قفل نمی‌شود

### 5. Status Management
- `pending_approval`: قابل ویرایش و حذف
- `approved`: قفل شده، قابل ویرایش نیست
- `rejected`: قابل ویرایش (می‌تواند resubmit شود)

### 6. Code Generation
- `performance_code` به صورت خودکار با prefix `'PR-'` تولید می‌شود

### 7. Receipt Creation
- فقط approved records می‌توانند receipt ایجاد کنند
- نوع receipt بر اساس `requires_temporary_receipt` تعیین می‌شود

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Transaction Management**: از `@transaction.atomic` برای atomic operations استفاده می‌شود
4. **Multi-formset Handling**: 3 formsets (materials, persons, machines) مدیریت می‌شوند
5. **Auto-population**: از order و transfer برای auto-populate استفاده می‌شود


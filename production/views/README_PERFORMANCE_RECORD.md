# production/views/performance_record.py - Performance Record Views (Complete Documentation)

**هدف**: Views برای مدیریت ثبت عملکرد تولید در ماژول production

این فایل شامل views برای:
- PerformanceRecordListView: فهرست ثبت‌های عملکرد
- PerformanceRecordCreateView: ایجاد ثبت عملکرد جدید
- PerformanceRecordUpdateView: ویرایش ثبت عملکرد
- PerformanceRecordDetailView: نمایش جزئیات ثبت عملکرد
- PerformanceRecordDeleteView: حذف ثبت عملکرد
- PerformanceRecordApproveView: تایید ثبت عملکرد
- PerformanceRecordRejectView: رد ثبت عملکرد
- PerformanceRecordCreateReceiptView: ایجاد receipt از ثبت عملکرد تایید شده
- PerformanceRecordGetOperationsView: AJAX view برای دریافت operations یک order

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

**Type**: `BaseDocumentListView` (از `shared.views.base`)

**Template**: `production/performance_record_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `PerformanceRecord`
- `template_name`: `'production/performance_record_list.html'`
- `context_object_name`: `'object_list'`
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
- **Returns**: context با show_filters و user_feature_permissions
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. اضافه کردن `show_filters = False`
  3. **اضافه کردن user_feature_permissions**:
     - دریافت `active_company_id` از session
     - اگر موجود باشد:
       - فراخوانی `get_user_feature_permissions(request.user, active_company_id)`
       - اضافه کردن به context
  4. بازگشت context

**URL**: `/production/performance-records/`

---

## PerformanceRecordCreateView

**Type**: `BaseMultipleFormsetCreateView` (از `shared.views.base_additional`)

**Template**: `production/performance_record_form.html` (extends `shared/generic/generic_form.html`)

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
- **Returns**: context با form_id، user_feature_permissions، document_type، و is_general_document
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. اضافه کردن `form_id = 'performance-form'`
  3. **اضافه کردن user_feature_permissions**:
     - دریافت `active_company_id` از session
     - اگر موجود باشد:
       - فراخوانی `get_user_feature_permissions(request.user, active_company_id)`
       - اضافه کردن به context
  4. **تعیین document_type**:
     - اگر `request.POST`: از POST data
     - در غیر این صورت: از form cleaned_data
     - در غیر این صورت: default `OPERATIONAL`
  5. اضافه کردن `document_type` و `is_general_document = (document_type == GENERAL)`
  6. بازگشت context

#### `form_valid(form: PerformanceRecordForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `PerformanceRecordForm`
- **Returns**: redirect به `success_url`
- **Logic** (در `@transaction.atomic`):
  1. بررسی `active_company_id` (اگر وجود نداشته باشد، return error)
  2. تنظیم `company_id`, `created_by`
  3. تولید `performance_code` با prefix `'PR-'` (اگر موجود نباشد)
  4. دریافت `order` و `document_type` از form cleaned_data
  5. **بررسی General Document Requirements** (اگر `document_type == GENERAL`):
     - بررسی که تمام operations با `requires_qc=1` دارای approved QC status باشند
     - اگر نه، return error
  6. Auto-populate از order:
     - `finished_item = order.finished_item`
     - `unit = order.unit`
     - اگر `document_type == GENERAL`: `quantity_planned = order.quantity_planned`
  7. ذخیره performance record header با `super().form_valid(form)`
  8. **Custom formsets handling**:
     - `process_formset()`: برای materials، return [] (skip default saving)
     - `validate_formsets()`: فقط persons و machines را برای operational documents validate می‌کند
     - `save_formsets()`: فقط persons و machines را برای operational documents save می‌کند
  9. **after_formsets_save()** - منطق custom:
     - **برای OPERATIONAL documents**:
       - جمع‌آوری materials از تمام approved transfers برای order
       - حذف materials موجود و ایجاد جدید از transfer items
       - ایجاد `OperationQCStatus` اگر operation `requires_qc=1` باشد
     - **برای GENERAL documents**:
       - اگر transfer انتخاب شده باشد: ایجاد materials از transfer items
       - در غیر این صورت: استفاده از material formset
       - جمع‌آوری و aggregate کردن persons، machines، و materials از تمام operational records برای order
       - ایجاد aggregated records

**نکات مهم**:
- از `@transaction.atomic` استفاده می‌کند
- **Document Types**: OPERATIONAL (برای یک operation) و GENERAL (aggregate از تمام operations)
- برای GENERAL documents، تمام QC-required operations باید approved باشند
- `process_id` برای person و machine formsets از order تنظیم می‌شود (در `get_formset_kwargs()`)

**URL**: `/production/performance-records/create/`

---

## PerformanceRecordUpdateView

**Type**: `BaseMultipleFormsetUpdateView, EditLockProtectedMixin` (از `shared.views.base_additional` و `shared.views.base`)

**Template**: `production/performance_record_form.html` (extends `shared/generic/generic_form.html`)

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

## PerformanceRecordDetailView

### `PerformanceRecordDetailView`

**توضیح**: نمایش جزئیات Performance Record (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `PerformanceRecord`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.performance_records'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**Context Variables**:
- `object`: PerformanceRecord instance
- `detail_title`: `_('View Performance Record')`
- `info_banner`: لیست اطلاعات اصلی (performance_code, performance_date, status)
- `detail_sections`: لیست sections برای نمایش:
  - Order Information: product_order (با finished_item اگر موجود باشد), transfer_request (اگر موجود باشد)
  - Production Quantities: quantity_produced, quantity_received, quantity_scrapped
  - Time Information: unit_cycle_minutes, total_run_minutes, machine_usage_minutes
  - Material Usage: table با headers (Material Item, Quantity Used, Unit, Scrap Quantity) و data rows
  - Personnel Usage: table با headers (Person, Minutes) و data rows
  - Machine Usage: table با headers (Machine, Minutes) و data rows
  - Approval Information: approved_by (اگر موجود باشد), approved_at (اگر موجود باشد)
  - Notes: اگر notes موجود باشد
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Performance Record قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related و prefetch_related
- **Logic**:
  1. دریافت queryset از `super().get_queryset()`
  2. اعمال `select_related('order', 'order__bom', 'order__finished_item', 'order__process', 'transfer', 'approved_by', 'created_by', 'edited_by')`
  3. اعمال `prefetch_related('materials__material_item', 'persons__person', 'machines__machine')`
  4. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Performance Code (type: 'code')
     - Performance Date
     - Status
  3. ساخت `detail_sections`:
     - **Order Information**: product_order (با finished_item اگر موجود باشد), transfer_request (اگر موجود باشد)
     - **Production Quantities**: quantity_produced, quantity_received, quantity_scrapped
     - **Time Information**: unit_cycle_minutes, total_run_minutes, machine_usage_minutes
     - **Material Usage**: اگر `materials.exists()` باشد:
       - ساخت table با headers: Material Item, Quantity Used, Unit, Scrap Quantity
       - ساخت data rows از `materials.all()`
       - اضافه کردن section با type='table'
     - **Personnel Usage**: اگر `persons.exists()` باشد:
       - ساخت table با headers: Person, Minutes
       - ساخت data rows از `persons.all()`
       - اضافه کردن section با type='table'
     - **Machine Usage**: اگر `machines.exists()` باشد:
       - ساخت table با headers: Machine, Minutes
       - ساخت data rows از `machines.all()`
       - اضافه کردن section با type='table'
     - **Approval Information**: اگر approved_by موجود باشد:
       - approved_by (با `get_full_name()` یا `username`)
       - approved_at (اگر موجود باشد)
     - **Notes**: اگر notes موجود باشد
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Performance Records

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Performance Record

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Performance Record قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/production/performance-records/<pk>/`

---

## PerformanceRecordDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:performance_records`

**Attributes**:
- `model`: `PerformanceRecord`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
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

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template اضافه می‌کند.

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Performance Record')`
- `confirmation_message`: پیام تأیید حذف
- `object_details`: لیست جزئیات performance record (code, order, date, status, quantities)
- `warning_message`: هشدار در مورد materials, persons, machines (اگر وجود داشته باشند)
- `cancel_url`: URL برای cancel
- `breadcrumbs`: لیست breadcrumbs

**URL**: `/production/performance-records/<pk>/delete/`

---

## PerformanceRecordGetOperationsView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `GET` (AJAX)

**Attributes**:
- `feature_code`: `'production.performance_records'`
- `required_action`: `'view_own'`

**متدها**:

#### `get(self, request, *args, **kwargs) -> JsonResponse`
- **Parameters**: `request` (با `order_id` در GET params)
- **Returns**: `JsonResponse` با لیست operations
- **Logic**:
  1. بررسی `active_company_id` (اگر وجود نداشته باشد، return error 400)
  2. دریافت `order_id` از `request.GET.get('order_id')`
  3. اگر `order_id` موجود نباشد، return error 400
  4. دریافت order object
  5. اگر order موجود نباشد، return error 404
  6. دریافت operations از `order.process.operations.filter(company_id=active_company_id, is_enabled=1).order_by('sequence_order')`
  7. ساخت JSON response با لیست operations (id, name, sequence_order)
  8. بازگشت `JsonResponse`

**Error Responses**:
- `400`: Company not selected یا order_id not provided
- `404`: Order not found

**نکات مهم**:
- برای AJAX requests استفاده می‌شود
- operations بر اساس `sequence_order` مرتب می‌شوند

**URL**: `/production/performance-records/get-operations/?order_id=<order_id>`

---

## PerformanceRecordGetOperationDataView

**Type**: `FeaturePermissionRequiredMixin, View`

**Method**: `GET` (AJAX)

**Attributes**:
- `feature_code`: `'production.performance_records'`
- `required_action`: `'view_own'`

**متدها**:

#### `get(self, request, *args, **kwargs) -> JsonResponse`
- **Parameters**: `request` (با `operation_id` و `order_id` در GET params)
- **Returns**: `JsonResponse` با materials، personnel، machines، work_line، operation، و order data
- **Logic**:
  1. بررسی `active_company_id` (اگر وجود نداشته باشد، return error 400)
  2. دریافت `operation_id` و `order_id` از `request.GET`
  3. اگر `operation_id` یا `order_id` موجود نباشد، return error 400
  4. دریافت operation object با `select_related('work_line', 'work_line__warehouse')`
  5. اگر operation موجود نباشد، return error 404
  6. دریافت order object
  7. اگر order موجود نباشد， return error 404
  8. **جمع‌آوری materials**:
     - از `IssueWarehouseTransferLine` برای approved transfers مربوط به order
     - فیلتر بر اساس `destination_warehouse` از operation's work_line
     - گروه‌بندی بر اساس item و جمع کردن quantities
  9. **جمع‌آوری personnel**:
     - از `operation.work_line.personnel` (فیلتر شده با company و is_enabled)
     - شامل id، code (public_code)، و name
  10. **جمع‌آوری machines**:
     - از `operation.work_line.machines` (فیلتر شده با company و is_enabled)
     - شامل id، code (public_code)، و name
  11. **اضافه کردن work_line info**:
     - id، code، name، و warehouse_id
  12. **اضافه کردن operation info** (جدید):
     - id
     - `labor_minutes_per_unit`: برای محاسبه خودکار work minutes پرسنل
     - `machine_minutes_per_unit`: برای محاسبه خودکار work minutes ماشین‌ها
  13. **اضافه کردن order info** (جدید):
     - `quantity_planned`: برای محاسبه خودکار work minutes بر اساس مقدار سفارش
  14. بازگشت `JsonResponse` با تمام داده‌ها

**Response Structure**:
```json
{
  "materials": [
    {
      "item_id": 1,
      "item_code": "MAT-001",
      "item_name": "Material Name",
      "quantity_required": 10.5,
      "unit": "kg"
    }
  ],
  "personnel": [
    {
      "id": 1,
      "code": "PER-00001",
      "name": "John Doe"
    }
  ],
  "machines": [
    {
      "id": 1,
      "code": "MCH-00000001",
      "name": "Machine Name"
    }
  ],
  "work_line": {
    "id": 1,
    "code": "WL-001",
    "name": "Work Line Name",
    "warehouse_id": 5
  },
  "operation": {
    "id": 1,
    "labor_minutes_per_unit": 2.5,
    "machine_minutes_per_unit": 1.8
  },
  "order": {
    "quantity_planned": 100.0
  }
}
```

**Error Responses**:
- `400`: Company not selected، operation_id not provided، یا order_id not provided
- `404`: Operation not found یا Order not found

**نکات مهم**:
- برای AJAX requests استفاده می‌شود
- Materials از approved transfer documents جمع‌آوری می‌شوند
- Personnel و machines از work_line مربوط به operation جمع‌آوری می‌شوند
- **عملکرد جدید**: operation info (labor_minutes_per_unit, machine_minutes_per_unit) و order info (quantity_planned) برای محاسبه خودکار work minutes در frontend اضافه شده‌اند
- Work minutes به صورت خودکار محاسبه می‌شود: `labor_minutes_per_unit * quantity_planned` برای پرسنل و `machine_minutes_per_unit * quantity_planned` برای ماشین‌ها

**URL**: `/production/performance-records/get-operation-data/?operation_id=<operation_id>&order_id=<order_id>`

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
6. **Generic Templates**: تمام templates به generic templates منتقل شده‌اند:
   - Performance Record List از `shared/generic/generic_list.html` extends می‌کند
   - Performance Record Form از `shared/generic/generic_form.html` extends می‌کند (با 3 formsets پیچیده: materials, persons, machines)
   - Performance Record Delete از `shared/generic/generic_confirm_delete.html` استفاده می‌کند

---

## Template و JavaScript Functionality

### performance_record_form.html

**Template**: `production/performance_record_form.html`

**Extends**: `shared/generic/generic_form.html`

**ویژگی‌های UI و JavaScript**:

#### 1. Operation-based Data Loading
- با انتخاب operation، داده‌های materials، personnel، و machines به صورت خودکار از `PerformanceRecordGetOperationDataView` بارگذاری می‌شوند
- JavaScript function `loadOperationData(operationId, orderId)` مسئول بارگذاری داده‌هاست
- داده‌ها در `window.currentOperationData` ذخیره می‌شوند برای استفاده در محاسبات

#### 2. Personnel و Machines Selection (تغییرات جدید)
- **قبل**: دکمه‌های "Add Person" و "Add Machine" برای اضافه کردن دستی
- **حالا**: 
  - لیست کامل personnel و machines از work_line operation به صورت خودکار نمایش داده می‌شود
  - هر ردیف دارای یک checkbox "Used" است
  - فقط ردیف‌های checked در فرم submit می‌شوند
  - دکمه‌های "Add Person" و "Add Machine" حذف شده‌اند

#### 3. Automatic Work Minutes Calculation
- **برای Personnel**: 
  - Work minutes به صورت خودکار محاسبه می‌شود: `labor_minutes_per_unit * quantity_planned`
  - فیلد work_minutes readonly است و به صورت خودکار پر می‌شود
  - مقدار از `operation.labor_minutes_per_unit` و `order.quantity_planned` استفاده می‌کند
- **برای Machines**:
  - Work minutes به صورت خودکار محاسبه می‌شود: `machine_minutes_per_unit * quantity_planned`
  - فیلد work_minutes readonly است و به صورت خودکار پر می‌شود
  - مقدار از `operation.machine_minutes_per_unit` و `order.quantity_planned` استفاده می‌کند

#### 4. Materials Formset
- **Template Row**: اگر formset خالی باشد، یک template row مخفی برای JavaScript اضافه می‌شود
- با انتخاب operation، materials از approved transfer documents به صورت خودکار populate می‌شوند
- JavaScript function `populateMaterials(materials)` مسئول پر کردن materials است

#### 5. Form Submission Handling
- قبل از submit، JavaScript ردیف‌های unchecked را disable می‌کند
- فقط ردیف‌های checked در فرم submit می‌شوند
- `TOTAL_FORMS` به صورت خودکار بر اساس تعداد checked items تنظیم می‌شود

#### 6. JavaScript Functions
- `loadOperationData(operationId, orderId)`: بارگذاری داده‌های operation
- `clearOperationData()`: پاک کردن تمام داده‌ها
- `populateMaterials(materials)`: پر کردن materials formset
- `populatePersonnel(personnel)`: پر کردن personnel table
- `populateMachines(machines)`: پر کردن machines table
- `togglePersonRowFields(row, enabled)`: فعال/غیرفعال کردن فیلدهای یک ردیف personnel
- `toggleMachineRowFields(row, enabled)`: فعال/غیرفعال کردن فیلدهای یک ردیف machine
- `updatePersonWorkMinutes(row)`: به‌روزرسانی work minutes برای یک personnel
- `updateMachineWorkMinutes(row)`: به‌روزرسانی work minutes برای یک machine
- `updateAllWorkMinutes()`: به‌روزرسانی work minutes برای تمام checked items

#### 7. Event Listeners
- `operationSelect.change`: بارگذاری داده‌های operation هنگام تغییر
- `orderSelect.change`: پاک کردن operation و داده‌ها هنگام تغییر order
- `documentTypeSelect.change`: مدیریت نمایش/مخفی کردن sections بر اساس document type
- `person-used-checkbox.change`: toggle کردن فیلدهای personnel row
- `machine-used-checkbox.change`: toggle کردن فیلدهای machine row
- `quantity_actual.input/change`: به‌روزرسانی work minutes برای general documents

#### 8. UI Changes Summary
- **Personnel Section**:
  - اضافه شدن ستون "Used" با checkbox
  - حذف ستون "Actions" و دکمه DELETE
  - حذف دکمه "Add Person"
  - نمایش نام personnel به صورت read-only span
  - Work minutes به صورت خودکار محاسبه و readonly
  
- **Machines Section**:
  - اضافه شدن ستون "Used" با checkbox
  - حذف ستون "Actions" و دکمه DELETE
  - حذف دکمه "Add Machine"
  - نمایش نام machine به صورت read-only span
  - Work minutes به صورت خودکار محاسبه و readonly

- **Materials Section**:
  - اضافه شدن template row برای JavaScript (اگر formset خالی باشد)
  - Auto-population از transfer documents

**نکات مهم**:
- برای operational documents، personnel و machines از work_line operation جمع‌آوری می‌شوند
- Work minutes به صورت خودکار بر اساس `labor_minutes_per_unit` / `machine_minutes_per_unit` و `quantity_planned` محاسبه می‌شود
- فقط checked personnel و machines در فرم submit می‌شوند
- برای general documents، quantity_actual می‌تواند برای محاسبه work minutes استفاده شود


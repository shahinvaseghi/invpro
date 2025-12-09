# production/views/process.py - Process Views (Complete Documentation)

**هدف**: Views برای مدیریت فرآیندهای تولید در ماژول production

این فایل شامل views برای:
- ProcessListView: فهرست فرآیندها
- ProcessCreateView: ایجاد فرآیند جدید
- ProcessUpdateView: ویرایش فرآیند
- ProcessDetailView: مشاهده جزئیات فرآیند (read-only)
- ProcessDeleteView: حذف فرآیند

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.views.base`: `BaseListView`, `BaseDetailView`, `BaseDeleteView`, `BaseFormsetCreateView`, `BaseFormsetUpdateView`, `EditLockProtectedMixin`
- `production.models`: `WorkLine` (برای personnel, machines, warehouse)
- `production.forms`: `ProcessForm`, `ProcessOperationFormSet`, `ProcessOperationMaterialFormSet`
- `production.models`: `Process`, `ProcessOperation`, `ProcessOperationMaterial`, `BOMMaterial`, `WorkLine`
- `django.contrib.messages`
- `django.db.transaction`: `transaction.atomic`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## Helper Functions

### `save_operation_materials_from_post(request, operation, operation_index, company_id, bom_id=None)`

**توضیح**: ذخیره materials برای یک operation با پارس کردن manual POST data.

**Parameters**:
- `request`: HTTP request object
- `operation`: ProcessOperation instance
- `operation_index`: index operation در formset
- `company_id`: شناسه شرکت
- `bom_id`: شناسه BOM (اختیاری)

**Returns**: `bool` (True اگر موفق باشد)

**Format در POST**: `materials-{operation_index}-{material_index}-{field_name}`

**Logic**:
1. **پارس کردن POST data**:
   - جمع‌آوری تمام keys که با `materials-{operation_index}-` شروع می‌شوند
   - استخراج `material_index` و `field_name` از key
   - ساخت `materials_data` dictionary
2. **Track kept materials**: `kept_material_ids = set()`
3. **ذخیره materials**:
   - برای هر material در `materials_data`:
     - دریافت `bom_material_id` و `quantity_used`
     - اگر هر دو موجود باشند:
       - دریافت `BOMMaterial` از database
       - **اگر `material_id` موجود باشد**:
         - دریافت existing material از database
         - Update fields: `bom_material`, `material_item`, `material_item_code`, `quantity_used`, `unit`, `is_enabled`, `edited_by`
         - `material.save()`
       - **در غیر این صورت**:
         - Create new material با تمام fields
       - اضافه کردن `material.id` به `kept_material_ids`
     - اگر خطا رخ دهد: error message و return False
4. **حذف materials حذف شده**:
   - دریافت تمام existing material IDs
   - حذف materials که در `kept_material_ids` نیستند
5. بازگشت True

**نکات مهم**:
- Materials که در POST نیستند، hard delete می‌شوند
- Fields از `bom_material` auto-populate می‌شوند

---

## ProcessListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/processes.html`

**Attributes**:
- `model`: `Process`
- `template_name`: `'production/processes.html'`
- `context_object_name`: `'processes'`
- `paginate_by`: `50`
- `feature_code`: `'production.processes'`
- `required_action`: `'view_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، select_related، prefetch_related، و table existence check برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Process.objects.none()` برمی‌گرداند
3. فیلتر: `Process.objects.filter(company_id=active_company_id)`
4. **select_related**: `'finished_item'`, `'bom'`, `'approved_by'` (FK to User)
5. **prefetch_related**: `'work_lines'`
6. **Table existence check** (برای `ProcessOperation`):
   - بررسی وجود جدول `production_processoperation` با SQL query
   - اگر جدول وجود دارد:
     - **prefetch_related**: 
       - `'operations'`
       - `'operations__operation_materials'`
       - `'operations__operation_materials__bom_material'`
       - `'operations__operation_materials__material_item'`
       - `'operations__work_line'`
       - `'operations__work_line__warehouse'`
       - `'operations__work_line__personnel'`
       - `'operations__work_line__machines'`
   - اگر خطا رخ دهد (مثلاً migration اجرا نشده)، skip می‌کند
7. مرتب‌سازی: `order_by('finished_item__name', 'revision', 'sort_order')`
8. queryset را برمی‌گرداند

**نکات مهم**:
- Table existence check برای جلوگیری از خطا در صورت عدم اجرای migration
- `approved_by` یک FK به User است (نه Person)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/processes/`

---

## ProcessCreateView

**Type**: `BaseFormsetCreateView` (از `shared.views.base`)

**Template**: `production/process_form.html`

**Form**: `ProcessForm`

**Success URL**: `production:processes`

**Attributes**:
- `model`: `Process`
- `form_class`: `ProcessForm`
- `template_name`: `'production/process_form.html'`
- `success_url`: `reverse_lazy('production:processes')`
- `feature_code`: `'production.processes'`
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

#### `get_formset_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای formset
- **Logic**:
  1. دریافت `company_id` از session
  2. دریافت `bom_id`:
     - از `form.cleaned_data.get('bom')` (اگر form validated شده)
     - یا از `request.POST.get('bom')` (اگر POST request)
  3. اضافه کردن `form_kwargs` با `bom_id` و `company_id`

#### `process_formset_instance(self, instance) -> Optional[ProcessOperation]`
- **Parameters**: `instance`: ProcessOperation instance
- **Returns**: instance پردازش شده یا None (اگر validation fail شود)
- **Logic**:
  1. **Validation**: بررسی `name` یا `sequence_order` (اگر هیچکدام وجود ندارد، return None)
  2. تنظیم `instance.process = self.object`
  3. تنظیم `instance.company_id = active_company_id`
  4. تنظیم `instance.created_by = request.user`
  5. بازگشت instance

#### `form_valid(self, form: ProcessForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `ProcessForm`
- **Returns**: redirect به `success_url`
- **Decorator**: `@transaction.atomic`
- **Logic**:
  1. دریافت `active_company_id` از session
  2. اگر `active_company_id` وجود ندارد:
     - error message: "Please select a company first."
     - return `self.form_invalid(form)`
  3. تنظیم `form.instance.company_id = active_company_id`
  4. تنظیم `form.instance.created_by = request.user`
  5. **تنظیم `finished_item` از BOM**:
     - `bom = form.cleaned_data.get('bom')`
     - اگر `bom` موجود باشد: `form.instance.finished_item = bom.finished_item`
  6. **ذخیره Process**: `self.object = form.save()`
  7. **ذخیره M2M relationships**: `form.save_m2m()` (برای `work_lines`)
  8. **دریافت BOM ID**: `bom_id = bom.id if bom else None`
  9. **ساخت operations formset**:
     - `ProcessOperationFormSet(self.request.POST, instance=self.object, prefix='operations', **self.get_formset_kwargs())`
  10. **Validate operations formset**:
      - اگر معتبر است:
        - **ذخیره operations**:
          - برای هر `operation_form`:
            - بررسی `cleaned_data` و `DELETE` flag
            - بررسی `name` یا `sequence_order`
            - اگر وجود دارد:
              - `operation = operation_form.save(commit=False)`
              - فراخوانی `self.process_formset_instance(operation)`
              - اگر operation معتبر است: `operation.save()`
              - اضافه به لیست `operations`
        - **ذخیره materials برای هر operation** (custom nested logic):
          - برای هر `operation_form` (با `operation_index`):
            - فراخوانی `save_operation_materials_from_post()`:
              - پارس کردن POST data با format: `materials-{operation_index}-{material_index}-{field_name}`
              - برای هر material:
                - دریافت `bom_material_id` و `quantity_used`
                - اگر `material_id` موجود باشد: update existing
                - در غیر این صورت: create new
                - تنظیم fields از `bom_material`
                - حذف materials که در POST نیستند
      - اگر معتبر نیست:
        - نمایش خطاهای `non_form_errors()`
        - نمایش خطاهای هر field در هر operation form (با format: "❌ Operation {i+1} - {field_label}: {error}")
        - return `self.form_invalid(form)`
  11. success message: "Process created successfully."
  12. return `HttpResponseRedirect(self.get_success_url())`

**نکات مهم**:
- از `BaseFormsetCreateView` استفاده می‌کند که منطق formset را خودکار مدیریت می‌کند
- `process_formset_instance` برای هر operation فراخوانی می‌شود
- Materials به صورت manual از POST data پارس و ذخیره می‌شوند (با `save_operation_materials_from_post`)
- تمام عملیات در یک `@transaction.atomic` انجام می‌شود

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با work_lines و process_id
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **اضافه کردن work_lines** (برای JavaScript):
     - دریافت `active_company_id` از session
     - اگر موجود باشد:
       - فیلتر `WorkLine.objects.filter(company_id=active_company_id, is_enabled=1).order_by('name')`
       - ساخت لیست dictionaries با `id`, `name`, `public_code`
     - در غیر این صورت: لیست خالی
  3. اضافه کردن `process_id` (اگر object موجود باشد)
  4. اضافه کردن `form_id = 'process-form'`
  5. بازگشت context

**URL**: `/production/processes/create/`

---

## ProcessUpdateView

**Type**: `BaseFormsetUpdateView, EditLockProtectedMixin` (از `shared.views.base`)

**Template**: `production/process_form.html`

**Form**: `ProcessForm`

**Success URL**: `production:processes`

**Attributes**:
- `model`: `Process`
- `form_class`: `ProcessForm`
- `template_name`: `'production/process_form.html'`
- `success_url`: `reverse_lazy('production:processes')`
- `feature_code`: `'production.processes'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` از `object.company_id`

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `self.object.company_id` اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Process.objects.none()` برمی‌گرداند
3. فیلتر: `Process.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `get_formset_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای formset
- **Logic**:
  1. دریافت `bom_id`:
     - از `self.object.bom_id` (اگر object موجود است)
     - یا از `request.POST.get('bom')` (اگر POST request)
  2. اضافه کردن `form_kwargs` با `bom_id` و `company_id` از `self.object.company_id`

#### `process_formset_instance(self, instance) -> Optional[ProcessOperation]`
- **Parameters**: `instance`: ProcessOperation instance
- **Returns**: instance پردازش شده یا None (اگر validation fail شود)
- **Logic**:
  1. **Validation**: بررسی `name` یا `sequence_order` (اگر هیچکدام وجود ندارد، return None)
  2. تنظیم `instance.process = self.object`
  3. تنظیم `instance.edited_by = request.user`
  4. بازگشت instance

#### `form_valid(self, form: ProcessForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `ProcessForm`
- **Returns**: redirect به `success_url`
- **Decorator**: `@transaction.atomic`
- **Logic**:
  1. دریافت `active_company_id` از session
  2. اگر `active_company_id` وجود ندارد:
     - error message: "Please select a company first."
     - return `self.form_invalid(form)`
  3. تنظیم `form.instance.edited_by = request.user`
  4. **تنظیم `finished_item` از BOM**:
     - `bom = form.cleaned_data.get('bom')`
     - اگر `bom` موجود باشد: `form.instance.finished_item = bom.finished_item`
  5. **ذخیره Process**: `self.object = form.save()`
  6. **ذخیره M2M relationships**: `form.save_m2m()` (برای `work_lines`)
  7. **دریافت BOM ID**: `bom_id = bom.id if bom else (self.object.bom_id if self.object else None)`
  8. **ساخت operations formset**:
     - `ProcessOperationFormSet(self.request.POST, instance=self.object, prefix='operations', **self.get_formset_kwargs())`
  9. **Validate operations formset**:
     - اگر معتبر است:
       - **دریافت existing operations**: `ProcessOperation.objects.filter(process=self.object).values_list('id', flat=True)`
       - **ذخیره operations** (update/create):
         - برای هر `operation_form`:
           - بررسی `cleaned_data` و `DELETE` flag
           - بررسی `name` یا `sequence_order`
           - اگر وجود دارد:
             - **بررسی operation_id از POST**: `self.request.POST.get(f'{operation_form.prefix}-id')`
             - اگر `operation_id` موجود باشد:
               - **Update existing**: دریافت operation از DB، update fields (`name`, `description`, `sequence_order`, `labor_minutes_per_unit`, `machine_minutes_per_unit`, `work_line`, `notes`)، `operation.edited_by = request.user`، `operation.save()`
               - حذف از `existing_operation_ids`
             - در غیر این صورت:
               - **Create new**: `operation = operation_form.save(commit=False)`، فراخوانی `self.process_formset_instance(operation)`، `operation.save()`
             - اضافه به لیست `operations`
       - **حذف operations حذف شده**: `ProcessOperation.objects.filter(id__in=existing_operation_ids, process=self.object).delete()`
       - **ذخیره materials برای هر operation** (custom nested logic):
         - برای هر `operation_form` (با `operation_index`):
           - فراخوانی `save_operation_materials_from_post()`:
             - پارس کردن POST data با format: `materials-{operation_index}-{material_index}-{field_name}`
             - برای هر material:
               - دریافت `bom_material_id` و `quantity_used`
               - اگر `material_id` موجود باشد: update existing
               - در غیر این صورت: create new
               - تنظیم fields از `bom_material`
               - حذف materials که در POST نیستند
     - اگر معتبر نیست:
       - نمایش خطاهای `non_form_errors()`
       - نمایش خطاهای هر field در هر operation form (با format: "❌ Operation {i+1} - {field_label}: {error}")
       - return `self.form_invalid(form)`
  10. success message: "Process updated successfully."
  11. return `HttpResponseRedirect(self.get_success_url())`

**نکات مهم**:
- از `BaseFormsetUpdateView` استفاده می‌کند که منطق formset را خودکار مدیریت می‌کند
- `process_formset_instance` برای هر operation جدید فراخوانی می‌شود
- Operations می‌توانند update، create، یا delete شوند
- Materials به صورت manual از POST data پارس و ذخیره می‌شوند (با `save_operation_materials_from_post`)
- تمام عملیات در یک `@transaction.atomic` انجام می‌شود

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با operations_formset، existing_operations_data، و work_lines
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. اضافه کردن `form_title`, `breadcrumbs`, `cancel_url`, `form_id`
  3. **دریافت BOM ID**:
     - از `self.object.bom_id` (اولویت)
     - یا از `form.cleaned_data.get('bom')` (اگر form validated شده)
     - یا از `request.POST.get('bom')` (اگر POST request)
  4. **ساخت operations formset**:
     - اگر `request.POST`:
       - ساخت formset از POST data
       - `existing_operations_data = None`
       - `operation_id_to_index = {}`
     - در غیر این صورت:
       - **بارگذاری existing operations**: `ProcessOperation.objects.filter(process=self.object, is_enabled=1).order_by('sequence_order', 'id')`
       - ساخت `initial_data` از existing operations (با تمام fields)
       - ساخت `operation_id_to_index` mapping
       - ساخت formset با `initial=initial_data`
       - **بارگذاری existing materials**: برای هر operation، `ProcessOperationMaterial.objects.filter(operation=op, is_enabled=1).select_related('bom_material', 'material_item').order_by('id')`
       - ساخت `existing_operations_data` با operation و materials (با `id`, `bom_material_id`, `quantity_used`, `unit`)
  5. اضافه کردن `operations_formset`, `existing_operations_data`, `operation_id_to_index`, `process_id` به context
  6. **اضافه کردن work_lines** (برای JavaScript):
     - دریافت `active_company_id` از session
     - فیلتر `WorkLine.objects.filter(company_id=active_company_id, is_enabled=1).order_by('name')`
     - ساخت لیست dictionaries با `id`, `name`, `public_code`
  7. بازگشت context

**URL**: `/production/processes/<pk>/edit/`

---

## ProcessDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:processes`

**Attributes**:
- `model`: `Process`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:processes')`
- `feature_code`: `'production.processes'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Process.objects.none()` برمی‌گرداند
3. فیلتر: `Process.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: Process را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Process deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که Process را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/processes/<pk>/delete/`

---

## ProcessDetailView

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html` (extended by `production/process_detail.html`)

**Attributes**:
- `model`: `Process`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.processes'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering و query optimizations برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با select_related و prefetch_related

**منطق**:
1. دریافت queryset از `super().get_queryset()`
2. **select_related**: 
   - `'finished_item'`
   - `'bom'`
   - `'approved_by'`
   - `'created_by'`
   - `'edited_by'`
3. **prefetch_related**:
   - `'work_lines'`
   - `'operations'`
   - `'operations__operation_materials'`
   - `'operations__operation_materials__bom_material'`
   - `'operations__operation_materials__material_item'`
   - `'operations__work_line'`
   - `'operations__work_line__warehouse'`
   - `'operations__work_line__personnel'`
   - `'operations__work_line__machines'`
4. queryset را برمی‌گرداند

**نکات مهم**:
- تمام relationships برای نمایش operations details بهینه‌سازی شده‌اند
- Personnel و Machines از WorkLine prefetch می‌شوند
- Warehouse از WorkLine prefetch می‌شود

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic detail template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `detail_sections` شامل operations با جزئیات کامل

**Context Variables**:
- `detail_title`: `_('View Process')`
- `info_banner`: لیست اطلاعات اصلی (Process Code, Revision, Status, Primary)
- `detail_sections`: لیست sections برای نمایش:
  - **Basic Information**: Finished Item, BOM, Description
  - **Work Lines**: لیست خطوط کار
  - **Operations** (type: `'operations_detail'`): لیست operations با جزئیات کامل:
    - برای هر operation:
      - `operation`: ProcessOperation instance
      - `materials`: لیست ProcessOperationMaterial (مواد BOM استفاده شده)
      - `personnel`: لیست Person (پرسنل مرتبط با work_line)
      - `machines`: لیست Machine (ماشین‌های مرتبط با work_line)
      - `warehouse`: Warehouse instance (انبار مرتبط با work_line)
  - **Approval Information**: Approved By, Approved At
  - **Notes**: یادداشت‌های فرآیند

**منطق**:
1. دریافت process از `self.object`
2. ساخت `info_banner` با Process Code, Revision, Status, Primary
3. ساخت `detail_sections`:
   - **Basic Information**: Finished Item, BOM, Description
   - **Work Lines**: اگر work_lines وجود دارد
   - **Operations**: ساخت لیست operations با جزئیات:
     - برای هر operation:
       - دریافت materials از `operation.operation_materials.all()`
       - دریافت personnel از `operation.work_line.personnel.all()` (اگر work_line موجود باشد)
       - دریافت machines از `operation.work_line.machines.all()` (اگر work_line موجود باشد)
       - دریافت warehouse از `operation.work_line.warehouse` (اگر work_line موجود باشد)
   - **Approval Information**: اگر approved_by موجود باشد
   - **Notes**: اگر notes موجود باشد
4. بازگشت context

**URL**: `/production/processes/<pk>/`

---

## Generic Templates

تمام templates به generic templates منتقل شده‌اند:

### Process List
- **Template**: `production/processes.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Expand button, Code, Finished Item, BOM, Revision, Operations, Work Lines, Status
  - `table_rows`: نمایش processes با expandable rows برای operations details
  - `after_table`: CSS و JavaScript برای toggle operations
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**:
  - `page_title`: "Processes"
  - `breadcrumbs`: Production > Processes
  - `create_url`: URL برای ایجاد Process جدید
  - `table_headers`: [] (overridden in template)
  - `show_actions`: True
  - `edit_url_name`: 'production:process_edit'
  - `delete_url_name`: 'production:process_delete'
  - `empty_state_title`: "No Processes Found"
  - `empty_state_message`: "Start by creating your first process."
  - `empty_state_icon`: "⚙️"
- **Features**:
  - Expandable rows برای نمایش operations details
  - نمایش operations count و materials used برای هر operation
  - نمایش Work Line و Warehouse برای هر operation
  - نمایش Personnel و Machines مرتبط با Work Line هر operation
  - JavaScript function `toggleOperations()` برای show/hide operations

### Process Detail
- **Template**: `production/process_detail.html` extends `shared/generic/generic_detail.html`
- **Blocks Overridden**: 
  - `detail_sections`: Override برای نمایش operations با جزئیات کامل
- **Context Variables**:
  - `detail_title`: "View Process"
  - `info_banner`: Process Code, Revision, Status, Primary
  - `detail_sections`: لیست sections شامل:
    - Basic Information (Finished Item, BOM, Description)
    - Work Lines
    - Operations (type: `'operations_detail'`) با جزئیات کامل:
      - برای هر operation: نام، ترتیب، زمان کار/ماشین، Work Line، Warehouse، Materials، Personnel، Machines
    - Approval Information
    - Notes
- **Features**:
  - نمایش کامل اطلاعات هر operation شامل:
    - **Materials**: مواد BOM استفاده شده با کد، نام و مقدار
    - **Personnel**: پرسنل مرتبط با Work Line (از ManyToMany)
    - **Machines**: ماشین‌های مرتبط با Work Line (از ManyToMany)
    - **Warehouse**: انبار مرتبط با Work Line (از ForeignKey)
  - استفاده از prefetch_related برای بهینه‌سازی query
  - نمایش زیبا و سازمان‌یافته با card-based layout

### Process Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات فرآیند (Code, Finished Item, BOM, Revision, Work Lines)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Process Form
- **Template**: `shared/generic/generic_form.html` (extended by `production/process_form.html`)
- **Blocks Overridden**:
  - `breadcrumb_extra`: اضافه کردن مسیر Production و Processes
  - `before_form`: نمایش info banner برای process_code و finished_item
  - `form_sections`: فیلدهای اصلی فرم (BOM, work_lines, revision, is_primary, approved_by, description, notes, sort_order, is_enabled)
  - `form_extra`: بخش Operations با nested materials formset
  - `extra_styles`: CSS برای operations و materials tables
  - `form_scripts`: JavaScript پیچیده برای مدیریت operations و materials formsets، load کردن BOM materials، و dynamic formset management
- **Context Variables**:
  - `form_title`: عنوان فرم ("Create Process" یا "Edit Process")
  - `breadcrumbs`: مسیر breadcrumb
  - `cancel_url`: URL برای لغو
  - `form_id`: 'process-form'
  - `operations_formset`: ProcessOperationFormSet برای operations
  - `existing_operations_data`: داده‌های موجود operations برای edit mode

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `work_lines` با `save_m2m()` ذخیره می‌شود
4. **Auto-set finished_item**: `finished_item` به صورت خودکار از `bom.finished_item` تنظیم می‌شود
5. **Query Optimization**: استفاده از `select_related` و `prefetch_related` برای بهینه‌سازی نمایش operations details:
   - Operations با materials, work_line, warehouse, personnel, machines prefetch می‌شوند
   - این بهینه‌سازی در `ProcessListView` و `ProcessDetailView` اعمال شده است
6. **Operations Details Display**: در لیست و جزئیات، برای هر operation نمایش داده می‌شود:
   - مواد BOM استفاده شده (از `ProcessOperationMaterial`)
   - پرسنل مرتبط (از `WorkLine.personnel` ManyToMany)
   - ماشین‌های مرتبط (از `WorkLine.machines` ManyToMany)
   - انبار مرتبط (از `WorkLine.warehouse` ForeignKey)


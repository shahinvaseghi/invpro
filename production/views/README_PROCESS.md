# production/views/process.py - Process Views (Complete Documentation)

**هدف**: Views برای مدیریت فرآیندهای تولید در ماژول production

این فایل شامل views برای:
- ProcessListView: فهرست فرآیندها
- ProcessCreateView: ایجاد فرآیند جدید
- ProcessUpdateView: ویرایش فرآیند
- ProcessDeleteView: حذف فرآیند

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `ProcessForm`
- `production.models`: `Process`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

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
     - **prefetch_related**: `'operations'`, `'operations__operation_materials'`, `'operations__operation_materials__bom_material'`
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

**Type**: `FeaturePermissionRequiredMixin, CreateView`

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

#### `form_valid(self, form: ProcessForm) -> HttpResponseRedirect`

**توضیح**: Process، M2M relationships، operations، و materials را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `ProcessForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**Decorator**: `@transaction.atomic` (تمام عملیات در یک transaction)

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد:
   - خطا: "Please select a company first."
   - `form_invalid()` برمی‌گرداند
3. تنظیم `form.instance.company_id = active_company_id`
4. تنظیم `form.instance.created_by = request.user`
5. **تنظیم `finished_item` از BOM**:
   - `bom = form.cleaned_data.get('bom')`
   - اگر `bom` وجود دارد: `form.instance.finished_item = bom.finished_item`
6. **ذخیره Process**: `response = super().form_valid(form)`
7. **ذخیره M2M relationships**: `form.save_m2m()` (برای `work_lines`)
8. **دریافت BOM ID**: `bom_id = bom.id if bom else None`
9. **ساخت operations formset**:
   - `ProcessOperationFormSet(self.request.POST, prefix='operations', form_kwargs={'bom_id': bom_id})`
10. **Validate operations formset**:
    - اگر معتبر است:
      - **ذخیره operations**:
        - برای هر `operation_form`:
          - بررسی `cleaned_data` و `DELETE` flag
          - بررسی `name` یا `sequence_order`
          - اگر وجود دارد:
            - `operation = operation_form.save(commit=False)`
            - تنظیم `operation.process = self.object`
            - تنظیم `operation.company_id = active_company_id`
            - تنظیم `operation.created_by = request.user`
            - `operation.save()`
            - اضافه به لیست `operations`
      - **ذخیره materials برای هر operation**:
        - برای هر `operation_form` (با index):
          - ساخت `ProcessOperationMaterialFormSet` با prefix `f'materials-{operation_index}'`
          - اگر formset معتبر است: `materials_formset.save()`
          - اگر معتبر نیست: نمایش خطاها
    - اگر معتبر نیست:
      - نمایش خطاهای `non_form_errors()`
      - نمایش خطاهای هر field در هر operation form
11. پیام موفقیت: "Process created successfully."
12. بازگشت `response`

**نکات مهم**:
- تمام عملیات در یک `@transaction.atomic` انجام می‌شود
- `finished_item` به صورت خودکار از `bom.finished_item` تنظیم می‌شود
- Operations و materials به صورت nested formsets ذخیره می‌شوند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`, `form_title`, و `operations_formset`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `active_module = 'production'`
3. اضافه کردن `form_title = _('Create Process')`
4. **دریافت BOM ID**:
   - از `form.cleaned_data.get('bom')` (اگر form validated شده)
   - یا از `request.POST.get('bom')` (اگر POST request)
5. **ساخت operations formset**:
   - اگر `request.POST`: از POST data
   - در غیر این صورت: formset خالی
   - `form_kwargs={'bom_id': bom_id}`
6. اضافه کردن `operations_formset` به context
7. context را برمی‌گرداند

**نکات مهم**:
- `finished_item` به صورت خودکار از `bom.finished_item` تنظیم می‌شود
- `save_m2m()` برای ذخیره `work_lines` فراخوانی می‌شود

**URL**: `/production/processes/create/`

---

## ProcessUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

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

#### `form_valid(self, form: ProcessForm) -> HttpResponseRedirect`

**توضیح**: Process، M2M relationships، operations (با update/create/delete)، و materials را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `ProcessForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**Decorator**: `@transaction.atomic` (تمام عملیات در یک transaction)

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد:
   - خطا: "Please select a company first."
   - `form_invalid()` برمی‌گرداند
3. تنظیم `form.instance.edited_by = request.user`
4. **تنظیم `finished_item` از BOM** (اگر تغییر کرده باشد):
   - `bom = form.cleaned_data.get('bom')`
   - اگر `bom` وجود دارد: `form.instance.finished_item = bom.finished_item`
5. **ذخیره Process**: `response = super().form_valid(form)`
6. **ذخیره M2M relationships**: `form.save_m2m()` (برای `work_lines`)
7. **دریافت BOM ID**: `bom_id = bom.id if bom else (self.object.bom_id if self.object else None)`
8. **ساخت operations formset**:
   - `ProcessOperationFormSet(self.request.POST, prefix='operations', form_kwargs={'bom_id': bom_id})`
9. **Validate operations formset**:
   - اگر معتبر است:
     - **دریافت existing operations**: `ProcessOperation.objects.filter(process=self.object).values_list('id', flat=True)`
     - **ذخیره operations** (update/create):
       - برای هر `operation_form`:
         - بررسی `cleaned_data` و `DELETE` flag
         - بررسی `name` یا `sequence_order`
         - اگر وجود دارد:
           - **بررسی operation_id از POST**: `self.request.POST.get(f'{operation_form.prefix}-id')`
           - اگر `operation_id` وجود دارد:
             - **Update existing**: دریافت operation از DB، update fields، `operation.edited_by = request.user`، `operation.save()`
             - حذف از `existing_operation_ids`
           - در غیر این صورت:
             - **Create new**: `operation = operation_form.save(commit=False)`، تنظیم `process`, `company_id`, `created_by`، `operation.save()`
           - اضافه به لیست `operations`
     - **حذف operations حذف شده**: `ProcessOperation.objects.filter(id__in=existing_operation_ids).delete()`
     - **ذخیره materials برای هر operation**:
       - برای هر `operation_form` (با index):
         - ساخت `ProcessOperationMaterialFormSet` با prefix `f'materials-{operation_index}'`
         - اگر formset معتبر است: `materials_formset.save()`
         - اگر معتبر نیست: نمایش خطاها
   - اگر معتبر نیست:
     - نمایش خطاهای `non_form_errors()`
     - نمایش خطاهای هر field در هر operation form
10. پیام موفقیت: "Process updated successfully."
11. بازگشت `response`

**نکات مهم**:
- تمام عملیات در یک `@transaction.atomic` انجام می‌شود
- Operations می‌توانند update، create، یا delete شوند
- `finished_item` به صورت خودکار از `bom.finished_item` تنظیم می‌شود (اگر تغییر کرده باشد)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`, `form_title`, `operations_formset`, و `existing_operations_data`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `active_module = 'production'`
3. اضافه کردن `form_title = _('Edit Process')`
4. **دریافت BOM ID**:
   - از `self.object.bom_id` (اگر object موجود است)
   - یا از `form.cleaned_data.get('bom')` (اگر form validated شده)
   - یا از `request.POST.get('bom')` (اگر POST request)
5. **ساخت operations formset**:
   - اگر `request.POST`: از POST data
   - در غیر این صورت:
     - **بارگذاری existing operations**: `ProcessOperation.objects.filter(process=self.object, is_enabled=1).order_by('sequence_order', 'id')`
     - ساخت `initial_data` از existing operations
     - ساخت formset با `initial=initial_data`
     - **بارگذاری existing materials**: برای هر operation، `ProcessOperationMaterial.objects.filter(operation=op, is_enabled=1).select_related('bom_material', 'material_item').order_by('id')`
     - ساخت `existing_operations_data` با operation و materials
     - اضافه کردن `existing_operations_data` به context
6. اضافه کردن `operations_formset` به context
7. context را برمی‌گرداند

**URL**: `/production/processes/<pk>/edit/`

---

## ProcessDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/process_confirm_delete.html`

**Success URL**: `production:processes`

**Attributes**:
- `model`: `Process`
- `template_name`: `'production/process_confirm_delete.html'`
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

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `work_lines` با `save_m2m()` ذخیره می‌شود
4. **Auto-set finished_item**: `finished_item` به صورت خودکار از `bom.finished_item` تنظیم می‌شود


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
- `get_queryset()`: فیلتر بر اساس company، `select_related('finished_item', 'bom', 'approved_by')`، `prefetch_related('work_lines')`، مرتب بر اساس `finished_item__name`, `revision`, `sort_order`
- `get_context_data()`: اضافه کردن `active_module`

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
- `get_form_kwargs()`: اضافه کردن `company_id` به form
- `form_valid()`: تنظیم `company_id`, `created_by`, `finished_item` از BOM، ذخیره M2M relationships
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

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
- `get_form_kwargs()`: اضافه کردن `company_id` از `object.company_id`
- `get_queryset()`: فیلتر بر اساس company
- `form_valid()`: تنظیم `edited_by`, `finished_item` از BOM (اگر تغییر کرده باشد)، ذخیره M2M relationships
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

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
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/processes/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `work_lines` با `save_m2m()` ذخیره می‌شود
4. **Auto-set finished_item**: `finished_item` به صورت خودکار از `bom.finished_item` تنظیم می‌شود


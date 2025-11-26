# production/views/machine.py - Machine Views (Complete Documentation)

**هدف**: Views برای مدیریت ماشین‌آلات در ماژول production

این فایل شامل views برای:
- MachineListView: فهرست ماشین‌آلات
- MachineCreateView: ایجاد ماشین جدید
- MachineUpdateView: ویرایش ماشین
- MachineDeleteView: حذف ماشین

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `MachineForm`
- `production.models`: `Machine`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## MachineListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/machines.html`

**Attributes**:
- `model`: `Machine`
- `template_name`: `'production/machines.html'`
- `context_object_name`: `'machines'`
- `paginate_by`: `50`
- `feature_code`: `'production.machines'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company و `is_enabled=1`، `select_related('work_center')` (با try-except)، مرتب بر اساس `public_code`
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/machines/`

---

## MachineCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/machine_form.html`

**Form**: `MachineForm`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `form_class`: `MachineForm`
- `template_name`: `'production/machine_form.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
- `required_action`: `'create'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `company_id` به form
- `form_valid()`: تنظیم `company_id`, `created_by`، نمایش پیام موفقیت
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

**URL**: `/production/machines/create/`

---

## MachineUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/machine_form.html`

**Form**: `MachineForm`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `form_class`: `MachineForm`
- `template_name`: `'production/machine_form.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
- `required_action`: `'edit_own'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `company_id` از `object.company_id`
- `get_queryset()`: فیلتر بر اساس company
- `form_valid()`: تنظیم `edited_by`، نمایش پیام موفقیت
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

**URL**: `/production/machines/<pk>/edit/`

---

## MachineDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/machine_confirm_delete.html`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `template_name`: `'production/machine_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
- `required_action`: `'delete_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/machines/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Optional select_related**: `select_related('work_center')` با try-except برای جلوگیری از خطا


# production/views/work_line.py - Work Line Views (Complete Documentation)

**هدف**: Views برای مدیریت خطوط کاری در ماژول production

این فایل شامل views برای:
- WorkLineListView: فهرست خطوط کاری
- WorkLineCreateView: ایجاد خط کاری جدید
- WorkLineUpdateView: ویرایش خط کاری
- WorkLineDeleteView: حذف خط کاری

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `WorkLineForm`
- `production.models`: `WorkLine`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## WorkLineListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/work_lines.html`

**Attributes**:
- `model`: `WorkLine`
- `template_name`: `'production/work_lines.html'`
- `context_object_name`: `'work_lines'`
- `paginate_by`: `50`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'view_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company، `select_related('warehouse')` (با try-except)، `prefetch_related('personnel', 'machines')`، مرتب بر اساس `warehouse__name`, `sort_order`, `public_code`
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/work-lines/`

---

## WorkLineCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/work_line_form.html`

**Form**: `WorkLineForm`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `form_class`: `WorkLineForm`
- `template_name`: `'production/work_line_form.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'create'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `company_id` به form
- `form_valid()`: تنظیم `company_id`, `created_by`، ذخیره M2M relationships با `save_m2m()`، نمایش پیام موفقیت
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

**نکات مهم**:
- `save_m2m()` برای ذخیره `personnel` و `machines` (ManyToMany) فراخوانی می‌شود

**URL**: `/production/work-lines/create/`

---

## WorkLineUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/work_line_form.html`

**Form**: `WorkLineForm`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `form_class`: `WorkLineForm`
- `template_name`: `'production/work_line_form.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'edit_own'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `company_id` از `object.company_id`
- `get_queryset()`: فیلتر بر اساس company
- `form_valid()`: تنظیم `edited_by`، ذخیره M2M relationships با `save_m2m()`، نمایش پیام موفقیت
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

**URL**: `/production/work-lines/<pk>/edit/`

---

## WorkLineDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/work_line_confirm_delete.html`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `template_name`: `'production/work_line_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'delete_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/work-lines/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `personnel` و `machines` با `save_m2m()` ذخیره می‌شوند
4. **Optional select_related**: `select_related('warehouse')` با try-except برای جلوگیری از خطا (اگر inventory module نصب نباشد)


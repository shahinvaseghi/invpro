# production/views/personnel.py - Personnel Views (Complete Documentation)

**هدف**: Views برای مدیریت پرسنل در ماژول production

این فایل شامل views برای:
- PersonnelListView: فهرست پرسنل
- PersonCreateView: ایجاد پرسنل جدید
- PersonUpdateView: ویرایش پرسنل
- PersonDeleteView: حذف پرسنل

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `PersonForm`
- `production.models`: `Person`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.contrib.auth.mixins.LoginRequiredMixin`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## PersonnelListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/personnel.html`

**Attributes**:
- `model`: `Person`
- `template_name`: `'production/personnel.html'`
- `context_object_name`: `'personnel'`
- `paginate_by`: `50`
- `feature_code`: `'production.personnel'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company و `is_enabled=1`، `select_related('company')`، `prefetch_related('company_units')`، مرتب بر اساس `public_code`
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/personnel/`

---

## PersonCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/person_form.html`

**Form**: `PersonForm`

**Success URL**: `production:personnel`

**Attributes**:
- `model`: `Person`
- `form_class`: `PersonForm`
- `template_name`: `'production/person_form.html'`
- `success_url`: `reverse_lazy('production:personnel')`
- `feature_code`: `'production.personnel'`
- `required_action`: `'create'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `company_id` به form
- `form_valid()`: تنظیم `company_id`, `created_by`، نمایش پیام موفقیت
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

**URL**: `/production/personnel/create/`

---

## PersonUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/person_form.html`

**Form**: `PersonForm`

**Success URL**: `production:personnel`

**Attributes**:
- `model`: `Person`
- `form_class`: `PersonForm`
- `template_name`: `'production/person_form.html'`
- `success_url`: `reverse_lazy('production:personnel')`
- `feature_code`: `'production.personnel'`
- `required_action`: `'edit_own'`

**متدها**:
- `get_form_kwargs()`: اضافه کردن `company_id` از `object.company_id`
- `get_queryset()`: فیلتر بر اساس company
- `form_valid()`: تنظیم `edited_by`، نمایش پیام موفقیت
- `get_context_data()`: اضافه کردن `active_module` و `form_title`

**URL**: `/production/personnel/<pk>/edit/`

---

## PersonDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/person_confirm_delete.html`

**Success URL**: `production:personnel`

**Attributes**:
- `model`: `Person`
- `template_name`: `'production/person_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:personnel')`
- `feature_code`: `'production.personnel'`
- `required_action`: `'delete_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `active_module`

**URL**: `/production/personnel/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `company_units` با `prefetch_related` در list view نمایش داده می‌شود


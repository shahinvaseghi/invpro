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

#### `get_form_kwargs(self) -> Dict[str, Any]`
- اضافه کردن `company_id` از session به form kwargs

#### `form_valid(self, form: PersonForm) -> HttpResponseRedirect`
**منطق**:
1. بررسی `active_company_id`:
   - اگر وجود نداشته باشد:
     - نمایش error message
     - بازگشت `form_invalid(form)`
2. تنظیم `form.instance.company_id = active_company_id`
3. تنظیم `form.instance.created_by = self.request.user`
4. نمایش پیام موفقیت
5. فراخوانی `super().form_valid(form)`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- اضافه کردن `active_module = 'production'`
- اضافه کردن `form_title = _('Create Person')`

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

#### `get_form_kwargs(self) -> Dict[str, Any]`
- اضافه کردن `company_id` از `object.company_id` به form kwargs

#### `get_queryset(self) -> QuerySet`
- فیلتر بر اساس `active_company_id` از session
- اگر `active_company_id` وجود نداشته باشد، return empty queryset

#### `form_valid(self, form: PersonForm) -> HttpResponseRedirect`
**منطق**:
1. تنظیم `form.instance.edited_by = self.request.user`
2. نمایش پیام موفقیت
3. فراخوانی `super().form_valid(form)`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- اضافه کردن `active_module = 'production'`
- اضافه کردن `form_title = _('Edit Person')`

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

#### `get_queryset(self) -> QuerySet`
- فیلتر بر اساس `active_company_id` از session
- اگر `active_company_id` وجود نداشته باشد، return empty queryset

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`
**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().delete()` برای حذف

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- اضافه کردن `active_module = 'production'`

**URL**: `/production/personnel/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `company_units` با `prefetch_related` در list view نمایش داده می‌شود


# ticketing/views/categories.py - Ticket Category Views (Complete Documentation)

**هدف**: Views برای مدیریت ticket categories در ماژول ticketing

این فایل شامل views برای:
- TicketCategoryListView: فهرست categories
- TicketCategoryCreateView: ایجاد category جدید
- TicketCategoryUpdateView: ویرایش category
- TicketCategoryDeleteView: حذف category

---

## وابستگی‌ها

- `ticketing.models`: `TicketCategory`
- `ticketing.forms.categories`: `TicketCategoryForm`, `TicketCategoryPermissionFormSet`
- `ticketing.views.base`: `TicketingBaseView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.db.models.Q`
- `django.shortcuts.get_object_or_404`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## TicketCategoryListView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, ListView`

**Template**: `ticketing/categories_list.html`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/categories_list.html'`
- `context_object_name`: `'categories'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'view_all'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company، search (name, name_en, public_code)، parent_filter (main/sub)
- `get_context_data()`: اضافه کردن `page_title`, `search_term`, `parent_filter`

**Query Parameters**:
- `search`: جستجو در name, name_en, public_code
- `parent_filter`: `'main'` (بدون parent) یا `'sub'` (با parent)

**URL**: `/ticketing/categories/`

---

## TicketCategoryCreateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, CreateView`

**Template**: `ticketing/category_form.html`

**Form**: `TicketCategoryForm`

**Formset**: `TicketCategoryPermissionFormSet`

**Success URL**: `ticketing:categories`

**Attributes**:
- `model`: `TicketCategory`
- `form_class`: `TicketCategoryForm`
- `template_name`: `'ticketing/category_form.html'`
- `success_url`: `reverse_lazy('ticketing:categories')`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`
- اضافه کردن `request` به form (از طریق ایجاد form instance و تنظیم `form.request`)

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- اضافه کردن `page_title = _('Create Category')`
- ساخت `permission_formset`:
  - اگر POST: از POST data
  - اگر GET: empty formset
  - تنظیم `request` روی تمام forms در formset

#### `form_valid(self, form: TicketCategoryForm) -> HttpResponseRedirect`
**منطق**:
1. تنظیم `company_id` از session به `form.instance.company_id`
2. ذخیره category با `super().form_valid(form)`
3. ساخت `permission_formset` از POST data با instance
4. تنظیم `request` روی تمام forms در formset
5. اگر formset valid باشد:
   - فراخوانی `permission_formset.save(commit=False)`
   - برای هر permission:
     - تنظیم `company_id`
     - تنظیم `category_code` از `category.public_code`
     - ذخیره permission
6. اگر formset invalid باشد:
   - بازگشت `form_invalid(form)`
7. نمایش پیام موفقیت
8. بازگشت response

**URL**: `/ticketing/categories/create/`

---

## TicketCategoryUpdateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, UpdateView`

**Template**: `ticketing/category_form.html`

**Form**: `TicketCategoryForm`

**Formset**: `TicketCategoryPermissionFormSet`

**Success URL**: `ticketing:categories`

**Attributes**:
- `model`: `TicketCategory`
- `form_class`: `TicketCategoryForm`
- `template_name`: `'ticketing/category_form.html'`
- `success_url`: `reverse_lazy('ticketing:categories')`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`
- اضافه کردن `request` به form (از طریق ایجاد form instance و تنظیم `form.request`)

#### `get_queryset(self) -> QuerySet`
- فیلتر بر اساس `active_company_id` از session

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- اضافه کردن `page_title = _('Edit Category')`
- ساخت `permission_formset`:
  - اگر POST: از POST data
  - اگر GET: از instance
  - تنظیم `request` روی تمام forms در formset

#### `form_valid(self, form: TicketCategoryForm) -> HttpResponseRedirect`
**منطق**:
1. ذخیره category با `super().form_valid(form)`
2. ساخت `permission_formset` از POST data با instance
3. تنظیم `request` روی تمام forms در formset
4. اگر formset valid باشد:
   - دریافت `company_id` از session
   - فراخوانی `permission_formset.save(commit=False)`
   - برای هر permission:
     - تنظیم `company_id`
     - تنظیم `category_code` از `category.public_code`
     - ذخیره permission
   - فراخوانی `permission_formset.save()` برای حذف deleted items
5. اگر formset invalid باشد:
   - بازگشت `form_invalid(form)`
6. نمایش پیام موفقیت
7. بازگشت response

**URL**: `/ticketing/categories/<pk>/edit/`

---

## TicketCategoryDeleteView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView`

**Template**: `ticketing/category_confirm_delete.html`

**Success URL**: `ticketing:categories`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/category_confirm_delete.html'`
- `success_url`: `reverse_lazy('ticketing:categories')`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'delete_own'`

**متدها**:
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `page_title`

**URL**: `/ticketing/categories/<pk>/delete/`

---

## نکات مهم

1. **Permission Formset**: تمام views از `TicketCategoryPermissionFormSet` استفاده می‌کنند
2. **Request Context**: `request` به تمام forms در formset پاس داده می‌شود
3. **Company Filtering**: تمام queryset ها بر اساس company فیلتر می‌شوند
4. **Parent Category**: می‌تواند parent category داشته باشد (hierarchical structure)

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Formset Management**: Permission formset در create و update views مدیریت می‌شود


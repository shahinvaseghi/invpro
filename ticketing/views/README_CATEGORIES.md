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

**Template**: `ticketing/categories_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/categories_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'view_all'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، search، و parent filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketCategory.objects.filter(company_id=company_id)`
3. **Search filtering** (اگر `search` در query parameter وجود دارد):
   - فیلتر با `Q(name__icontains=search) | Q(name_en__icontains=search) | Q(public_code__icontains=search)`
4. **Parent filtering** (اگر `parent_filter` در query parameter وجود دارد):
   - اگر `parent_filter == 'main'`: `queryset.filter(parent_category__isnull=True)` (فقط main categories)
   - اگر `parent_filter == 'sub'`: `queryset.filter(parent_category__isnull=False)` (فقط subcategories)
5. مرتب‌سازی: `order_by('sort_order', 'public_code', 'name')`
6. queryset را برمی‌گرداند

**Query Parameters**:
- `search`: جستجو در name، name_en، public_code
- `parent_filter`: `'main'` (بدون parent) یا `'sub'` (با parent)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`, `search_term`, `parent_filter`

**Context Variables اضافه شده**:
- `page_title`: `_('Ticket Categories')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `create_url`: URL برای ایجاد category جدید
- `create_button_text`: متن دکمه ایجاد
- `show_filters`: `True` برای نمایش فیلترها
- `parent_filter_value`: مقدار `parent_filter` از query parameter
- `search_placeholder`: placeholder برای فیلد جستجو
- `clear_filter_url`: URL برای پاک کردن فیلترها
- `show_actions`: `True` برای نمایش دکمه‌های action
- `edit_url_name`: نام URL برای ویرایش
- `delete_url_name`: نام URL برای حذف
- `empty_state_title`, `empty_state_message`, `empty_state_icon`: پیام‌های empty state

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
- `template_name`: `'ticketing/category_form.html'` (extends `shared/generic/generic_form.html`)
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

**توضیح**: Category و permissions را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `TicketCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. دریافت `company_id` از session
2. اگر `company_id` وجود دارد:
   - تنظیم `form.instance.company_id = company_id`
3. ذخیره category: `response = super().form_valid(form)`
4. **ساخت permission formset**:
   - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object)`
5. **تنظیم request روی تمام forms**:
   - برای هر `perm_form` در `permission_formset.forms`:
     - `perm_form.request = self.request`
6. **Validate و save formset**:
   - اگر `permission_formset.is_valid()`:
     - `permission_formset.save()` (برای حذف deleted items)
     - `permission_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `permission`:
       - تنظیم `permission.company_id = company_id`
       - اگر `permission.category` موجود است:
         - تنظیم `permission.category_code = permission.category.public_code`
       - `permission.save()`
   - اگر formset invalid باشد:
     - بازگشت `form_invalid(form)`
7. نمایش پیام موفقیت: "Category created successfully."
8. بازگشت `response`

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
- `template_name`: `'ticketing/category_form.html'` (extends `shared/generic/generic_form.html`)
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

**توضیح**: Category و permissions را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `TicketCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. ذخیره category: `response = super().form_valid(form)`
2. **ساخت permission formset**:
   - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object)`
3. **تنظیم request روی تمام forms**:
   - برای هر `perm_form` در `permission_formset.forms`:
     - `perm_form.request = self.request`
4. **Validate و save formset**:
   - اگر `permission_formset.is_valid()`:
     - دریافت `company_id` از session
     - `permission_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `permission`:
       - تنظیم `permission.company_id = company_id`
       - اگر `permission.category` موجود است:
         - تنظیم `permission.category_code = permission.category.public_code`
       - `permission.save()`
     - `permission_formset.save()` (برای حذف deleted items)
   - اگر formset invalid باشد:
     - بازگشت `form_invalid(form)`
5. نمایش پیام موفقیت: "Category updated successfully."
6. بازگشت `response`

**URL**: `/ticketing/categories/<pk>/edit/`

---

## TicketCategoryDeleteView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `ticketing:categories`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('ticketing:categories')`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketCategory.objects.filter(company_id=company_id)`
3. queryset را برمی‌گرداند

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: TicketCategory را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Category deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که TicketCategory را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Category')`
- `confirmation_message`: پیام تأیید حذف
- `object_details`: جزئیات category برای نمایش (name, code, description)
- `warning_message`: هشدار در مورد subcategories (اگر وجود داشته باشند)
- `cancel_url`: URL برای cancel
- `breadcrumbs`: لیست breadcrumbs

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


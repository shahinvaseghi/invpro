# ticketing/views/categories.py - Ticket Category Views (Complete Documentation)

**هدف**: Views برای مدیریت ticket categories در ماژول ticketing

این فایل شامل views برای:
- TicketCategoryListView: فهرست categories
- TicketCategoryCreateView: ایجاد category جدید
- TicketCategoryUpdateView: ویرایش category
- TicketCategoryDetailView: نمایش جزئیات category
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

**Type**: `BaseListView` (از `shared.views.base`)

**Template**: `ticketing/categories_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/categories_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'view_all'`

**متدها**:

#### `get_base_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده بر اساس company
- **Logic**:
  1. دریافت `company_id` از session
  2. فیلتر: `TicketCategory.objects.filter(company_id=company_id)`
  3. بازگشت queryset

#### `get_search_fields(self) -> list`
- **Returns**: لیست fields برای search
- **Logic**:
  - بازگشت `['name', 'name_en', 'public_code']`

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده با search و parent filtering
- **Logic**:
  1. دریافت queryset از `super().get_queryset()` (که search را اعمال می‌کند)
  2. **Parent filtering** (اگر `parent_filter` در query parameter وجود دارد):
     - اگر `parent_filter == 'main'`: `queryset.filter(parent_category__isnull=True)` (فقط main categories)
     - اگر `parent_filter == 'sub'`: `queryset.filter(parent_category__isnull=False)` (فقط subcategories)
  3. مرتب‌سازی: `order_by('sort_order', 'public_code', 'name')`
  4. بازگشت queryset

**Query Parameters**:
- `search`: جستجو در name، name_en، public_code (از base class)
- `parent_filter`: `'main'` (بدون parent) یا `'sub'` (با parent)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با parent_filter_value
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. اضافه کردن `parent_filter_value = request.GET.get('parent_filter', '')`
  3. بازگشت context

**URL**: `/ticketing/categories/`

---

## TicketCategoryCreateView

**Type**: `BaseFormsetCreateView` (از `shared.views.base`)

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

#### `get_formset_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای formset
- **Logic**:
  1. دریافت kwargs از `super().get_formset_kwargs()`
  2. اگر `instance` موجود نباشد:
     - تنظیم `instance = TicketCategory()` (temporary instance)
  3. بازگشت kwargs

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با formset که request روی forms تنظیم شده
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **تنظیم request روی تمام forms در formset**:
     - اگر `formset` در context موجود باشد:
       - برای هر `form` در `formset.forms`:
         - `form.request = self.request`
  3. بازگشت context

#### `process_formset_instance(self, instance) -> Any`
- **Parameters**: `instance`: instance از formset
- **Returns**: instance پردازش شده
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود باشد: `instance.company_id = company_id`
  3. اگر `instance.category` موجود باشد:
     - `instance.category_code = instance.category.public_code`
  4. بازگشت instance

#### `form_valid(self, form: TicketCategoryForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `TicketCategoryForm`
- **Returns**: redirect به `success_url`
- **Logic** (در `@transaction.atomic`):
  1. دریافت `company_id` از session
  2. اگر موجود باشد: `form.instance.company_id = company_id`
  3. **ذخیره main object**:
     - `self.object = form.save()`
  4. **ساخت permission formset**:
     - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object, prefix=self.formset_prefix)`
  5. **تنظیم request روی تمام forms**:
     - برای هر `perm_form` در `formset.forms`:
       - `perm_form.request = self.request`
  6. **Validate و save formset**:
     - اگر `formset.is_valid()`:
       - برای هر `permission` در `formset.save(commit=False)`:
         - فراخوانی `self.process_formset_instance(permission)`
         - `permission.save()`
       - `formset.save()` (برای حذف deleted items)
     - اگر formset invalid باشد:
       - بازگشت `self.form_invalid(form)`
  7. بازگشت `HttpResponseRedirect(self.get_success_url())`

**URL**: `/ticketing/categories/create/`

---

## TicketCategoryUpdateView

**Type**: `BaseFormsetUpdateView, EditLockProtectedMixin` (از `shared.views.base`)

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
- **Returns**: context با formset که request روی forms تنظیم شده
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **تنظیم request روی تمام forms در formset**:
     - اگر `formset` در context موجود باشد:
       - برای هر `form` در `formset.forms`:
         - `form.request = self.request`
  3. بازگشت context

#### `process_formset_instance(self, instance) -> Any`
- **Parameters**: `instance`: instance از formset
- **Returns**: instance پردازش شده
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود باشد: `instance.company_id = company_id`
  3. اگر `instance.category` موجود باشد:
     - `instance.category_code = instance.category.public_code`
  4. بازگشت instance

#### `form_valid(self, form: TicketCategoryForm) -> HttpResponseRedirect`
- **Parameters**: `form`: فرم معتبر `TicketCategoryForm`
- **Returns**: redirect به `success_url`
- **Logic** (در `@transaction.atomic`):
  1. **ذخیره main object**:
     - `self.object = form.save()`
  2. **ساخت permission formset**:
     - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object, prefix=self.formset_prefix)`
  3. **تنظیم request روی تمام forms**:
     - برای هر `perm_form` در `formset.forms`:
       - `perm_form.request = self.request`
  4. **Validate و save formset**:
     - اگر `formset.is_valid()`:
       - برای هر `permission` در `formset.save(commit=False)`:
         - فراخوانی `self.process_formset_instance(permission)`
         - `permission.save()`
       - `formset.save()` (برای حذف deleted items)
     - اگر formset invalid باشد:
       - بازگشت `self.form_invalid(form)`
  5. بازگشت `HttpResponseRedirect(self.get_success_url())`

**URL**: `/ticketing/categories/<pk>/edit/`

---

## TicketCategoryDetailView

### `TicketCategoryDetailView`

**توضیح**: نمایش جزئیات Ticket Category (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'ticketing.management.categories'`
- `required_action`: `'view_all'`
- `active_module`: `'ticketing'`

**Context Variables**:
- `object`: TicketCategory instance
- `detail_title`: `_('View Ticket Category')`
- `info_banner`: لیست اطلاعات اصلی (code, status)
- `detail_sections`: لیست sections برای نمایش:
  - Basic Information: name, name_en (اگر موجود باشد), parent_category (اگر موجود باشد), description (اگر موجود باشد)
  - Subcategories: اگر subcategories موجود باشد (comma-separated list)
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Category قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related و prefetch_related
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود نباشد: `TicketCategory.objects.none()`
  3. فیلتر: `TicketCategory.objects.filter(company_id=company_id)`
  4. اعمال `select_related('parent_category', 'created_by', 'edited_by')`
  5. اعمال `prefetch_related('subcategories')`
  6. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Code (type: 'code')
     - Status (type: 'badge')
  3. ساخت `detail_sections`:
     - **Basic Information**: name, name_en (اگر موجود باشد), parent_category (اگر موجود باشد), description (اگر موجود باشد)
     - **Subcategories**: اگر `subcategories.exists()` باشد:
       - ساخت comma-separated text از `subcat.name` برای هر subcategory
       - اضافه کردن section
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Categories

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Category

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Category قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/ticketing/categories/<pk>/`

---

## TicketCategoryDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

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
- **Returns**: context با warning_message (اگر subcategories موجود باشد)
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **اضافه کردن warning_message**:
     - اگر `self.object.subcategories.exists()`:
       - `warning_message = _('This category has {count} subcategory(ies). They will also be deleted.').format(count=self.object.subcategories.count())`
       - اضافه کردن به context
  3. بازگشت context

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


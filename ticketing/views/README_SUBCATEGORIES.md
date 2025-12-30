# ticketing/views/subcategories.py - Ticket Subcategory Views (Complete Documentation)

**هدف**: Views برای مدیریت ticket subcategories در ماژول ticketing

**نکته**: Subcategories در واقع `TicketCategory` instances با `parent_category` تنظیم شده هستند.

این فایل شامل views برای:
- TicketSubcategoryListView: فهرست subcategories
- TicketSubcategoryCreateView: ایجاد subcategory جدید
- TicketSubcategoryUpdateView: ویرایش subcategory
- TicketSubcategoryDetailView: نمایش جزئیات subcategory
- TicketSubcategoryDeleteView: حذف subcategory

---

## وابستگی‌ها

- `ticketing.models`: `TicketCategory`
- `ticketing.forms.categories`: `TicketCategoryForm`, `TicketCategoryPermissionFormSet`
- `ticketing.views.base`: `TicketingBaseView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.db.models.Q`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## TicketSubcategoryListView

**Type**: `BaseListView` (از `shared.views.base`)

**Template**: `ticketing/subcategories_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/subcategories_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.subcategories'`
- `required_action`: `'view_all'`

**متدها**:

#### `get_base_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده بر اساس company (فقط subcategories)
- **Logic**:
  1. دریافت `company_id` از session
  2. فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=False)` (فقط subcategories)
  3. بازگشت queryset

#### `get_search_fields(self) -> list`
- **Returns**: لیست fields برای search
- **Logic**:
  - بازگشت `['name', 'name_en', 'public_code']`

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده با search و parent filtering
- **Logic**:
  1. دریافت queryset از `super().get_queryset()` (که search را اعمال می‌کند)
  2. **Parent filter** (اگر `parent` در query parameter وجود دارد):
     - فیلتر: `queryset.filter(parent_category_id=parent_id)`
  3. مرتب‌سازی: `order_by('parent_category__name', 'sort_order', 'public_code', 'name')`
  4. بازگشت queryset

**Query Parameters**:
- `search`: جستجو در name، name_en، public_code (از base class)
- `parent`: فیلتر بر اساس parent category ID

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با parent_categories
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **اضافه کردن parent_categories**:
     - دریافت `company_id` از session
     - اگر موجود باشد:
       - فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=True, is_enabled=1)`
       - مرتب‌سازی: `order_by('name')`
       - اضافه کردن به context
  3. بازگشت context

**URL**: `/ticketing/subcategories/`

---

## TicketSubcategoryCreateView

**Type**: `BaseFormsetCreateView` (از `shared.views.base`)

**Template**: `ticketing/subcategory_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `TicketCategoryForm`

**Formset**: `TicketCategoryPermissionFormSet`

**Success URL**: `ticketing:subcategories`

**Attributes**:
- `model`: `TicketCategory`
- `form_class`: `TicketCategoryForm`
- `template_name`: `'ticketing/subcategory_form.html'`
- `success_url`: `reverse_lazy('ticketing:subcategories')`
- `feature_code`: `'ticketing.management.subcategories'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای form
- **Logic**:
  1. دریافت kwargs از `super().get_form_kwargs()`
  2. ایجاد form instance برای تنظیم `form.request = self.request`
  3. بازگشت kwargs (بدون تغییر)

#### `get_formset_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای formset
- **Logic**:
  1. دریافت kwargs از `super().get_formset_kwargs()`
  2. اگر `instance` موجود نباشد:
     - تنظیم `instance = TicketCategory()` (temporary instance)
  3. بازگشت kwargs

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با formset که request روی forms تنظیم شده و parent_categories
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **تنظیم request روی تمام forms در formset**:
     - اگر `formset` در context موجود باشد:
       - برای هر `form` در `formset.forms`:
         - `form.request = self.request`
  3. **اضافه کردن parent_categories**:
     - دریافت `company_id` از session
     - اگر موجود باشد:
       - فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=True, is_enabled=1)`
       - مرتب‌سازی: `order_by('name')`
       - اضافه کردن به context
  4. بازگشت context

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
  1. **بررسی parent_category** (subcategory requirement):
     - اگر `form.instance.parent_category_id` تنظیم نشده باشد:
       - `form.add_error("parent_category", _("Subcategory must have a parent category."))`
       - بازگشت `self.form_invalid(form)`
  2. دریافت `company_id` از session
  3. اگر موجود باشد: `form.instance.company_id = company_id`
  4. **ذخیره main object**:
     - `self.object = form.save()`
  5. **ساخت permission formset**:
     - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object, prefix=self.formset_prefix)`
  6. **تنظیم request روی تمام forms**:
     - برای هر `perm_form` در `formset.forms`:
       - `perm_form.request = self.request`
  7. **Validate و save formset**:
     - اگر `formset.is_valid()`:
       - برای هر `permission` در `formset.save(commit=False)`:
         - فراخوانی `self.process_formset_instance(permission)`
         - `permission.save()`
       - `formset.save()` (برای حذف deleted items)
     - اگر formset invalid باشد:
       - بازگشت `self.form_invalid(form)`
  8. بازگشت `HttpResponseRedirect(self.get_success_url())`

**نکات مهم**:
- `parent_category` required است (subcategory requirement)
- اگر `parent_category` تنظیم نشده باشد، form invalid می‌شود

**URL**: `/ticketing/subcategories/create/`

---

## TicketSubcategoryUpdateView

**Type**: `BaseFormsetUpdateView, EditLockProtectedMixin` (از `shared.views.base`)

**Template**: `ticketing/subcategory_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `TicketCategoryForm`

**Formset**: `TicketCategoryPermissionFormSet`

**Success URL**: `ticketing:subcategories`

**Attributes**:
- `model`: `TicketCategory`
- `form_class`: `TicketCategoryForm`
- `template_name`: `'ticketing/subcategory_form.html'`
- `success_url`: `reverse_lazy('ticketing:subcategories')`
- `feature_code`: `'ticketing.management.subcategories'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`
- **Returns**: kwargs برای form
- **Logic**:
  1. دریافت kwargs از `super().get_form_kwargs()`
  2. ایجاد form instance برای تنظیم `form.request = self.request`
  3. بازگشت kwargs (بدون تغییر)

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده (فقط subcategories)
- **Logic**:
  1. دریافت `company_id` از session
  2. فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=False)` (فقط subcategories)
  3. بازگشت queryset

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با formset که request روی forms تنظیم شده و parent_categories
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. **تنظیم request روی تمام forms در formset**:
     - اگر `formset` در context موجود باشد:
       - برای هر `form` در `formset.forms`:
         - `form.request = self.request`
  3. **اضافه کردن parent_categories**:
     - دریافت `company_id` از session
     - اگر موجود باشد:
       - فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=True, is_enabled=1)`
       - مرتب‌سازی: `order_by('name')`
       - اضافه کردن به context
  4. بازگشت context

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
  1. **بررسی parent_category** (subcategory requirement):
     - اگر `form.instance.parent_category_id` تنظیم نشده باشد:
       - `form.add_error("parent_category", _("Subcategory must have a parent category."))`
       - بازگشت `self.form_invalid(form)`
  2. **ذخیره main object**:
     - `self.object = form.save()`
  3. **ساخت permission formset**:
     - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object, prefix=self.formset_prefix)`
  4. **تنظیم request روی تمام forms**:
     - برای هر `perm_form` در `formset.forms`:
       - `perm_form.request = self.request`
  5. **Validate و save formset**:
     - اگر `formset.is_valid()`:
       - برای هر `permission` در `formset.save(commit=False)`:
         - فراخوانی `self.process_formset_instance(permission)`
         - `permission.save()`
       - `formset.save()` (برای حذف deleted items)
     - اگر formset invalid باشد:
       - بازگشت `self.form_invalid(form)`
  6. بازگشت `HttpResponseRedirect(self.get_success_url())`

**نکات مهم**:
- `parent_category` required است (subcategory requirement)
- اگر `parent_category` تنظیم نشده باشد، form invalid می‌شود

**URL**: `/ticketing/subcategories/<pk>/edit/`

---

## TicketSubcategoryDetailView

### `TicketSubcategoryDetailView`

**توضیح**: نمایش جزئیات Ticket Subcategory (read-only)

**Type**: `BaseDetailView` (از `shared.views.base`)

**Template**: `shared/generic/generic_detail.html`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'ticketing.management.subcategories'`
- `required_action`: `'view_all'`
- `active_module`: `'ticketing'`

**Context Variables**:
- `object`: TicketCategory instance (subcategory)
- `detail_title`: `_('View Ticket Subcategory')`
- `info_banner`: لیست اطلاعات اصلی (code, status)
- `detail_sections`: لیست sections برای نمایش:
  - Basic Information: name, name_en (اگر موجود باشد), parent_category (required برای subcategory), description (اگر موجود باشد)
- `list_url`, `edit_url`: URLs برای navigation
- `can_edit_object`: بررسی اینکه آیا Subcategory قفل است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset بهینه شده با select_related (فقط subcategories)
- **Logic**:
  1. دریافت `company_id` از session
  2. اگر موجود نباشد: `TicketCategory.objects.none()`
  3. فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=False)` (فقط subcategories)
  4. اعمال `select_related('parent_category', 'created_by', 'edited_by')`
  5. بازگشت queryset

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`
- **Returns**: context با detail sections
- **Logic**:
  1. دریافت context از `super().get_context_data()`
  2. ساخت `info_banner`:
     - Code (type: 'code')
     - Status (type: 'badge')
  3. ساخت `detail_sections`:
     - **Basic Information**: name, name_en (اگر موجود باشد), parent_category (required برای subcategory), description (اگر موجود باشد)
  4. بازگشت context

#### `get_list_url(self) -> str`
- **Returns**: URL برای لیست Subcategories

#### `get_edit_url(self) -> str`
- **Returns**: URL برای ویرایش Subcategory

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`
- **Returns**: True اگر Subcategory قفل نباشد
- **Logic**:
  - بررسی `is_locked` attribute
  - اگر `is_locked=True` باشد، return False

**URL**: `/ticketing/subcategories/<pk>/`

---

## TicketSubcategoryDeleteView

**Type**: `BaseDeleteView` (از `shared.views.base`)

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `ticketing:subcategories`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/subcategory_confirm_delete.html'`
- `success_url`: `reverse_lazy('ticketing:subcategories')`
- `feature_code`: `'ticketing.management.subcategories'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`
- **Returns**: queryset فیلتر شده (فقط subcategories)
- **Logic**:
  1. دریافت `company_id` از session
  2. فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=False)` (فقط subcategories)
  3. بازگشت queryset

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`
- **Parameters**: `request`, `*args`, `**kwargs`
- **Returns**: redirect به `success_url`
- **Logic**:
  - فراخوانی `super().delete()` که Subcategory را حذف می‌کند و پیام موفقیت نمایش می‌دهد

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- **Returns**: context با delete title، confirmation message، object details، و breadcrumbs
- **Logic**:
  - از base class استفاده می‌کند که تمام context variables لازم را اضافه می‌کند

**URL**: `/ticketing/subcategories/<pk>/delete/`

---

## نکات مهم

1. **Parent Category Required**: Subcategory باید `parent_category` داشته باشد
2. **Model**: از همان model `TicketCategory` استفاده می‌کند (فقط با `parent_category__isnull=False` فیلتر می‌شود)
3. **Permission Formset**: مشابه categories views

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Parent Category Filter**: queryset با `parent_category__isnull=False` فیلتر می‌شود
3. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند


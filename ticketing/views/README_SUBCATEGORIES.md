# ticketing/views/subcategories.py - Ticket Subcategory Views (Complete Documentation)

**هدف**: Views برای مدیریت ticket subcategories در ماژول ticketing

**نکته**: Subcategories در واقع `TicketCategory` instances با `parent_category` تنظیم شده هستند.

این فایل شامل views برای:
- TicketSubcategoryListView: فهرست subcategories
- TicketSubcategoryCreateView: ایجاد subcategory جدید
- TicketSubcategoryUpdateView: ویرایش subcategory
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

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, ListView`

**Template**: `ticketing/subcategories_list.html`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/subcategories_list.html'`
- `context_object_name`: `'subcategories'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.subcategories'`
- `required_action`: `'view_all'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، parent category filtering، search، و parent filter برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده (فقط subcategories)

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=False)` (فقط subcategories)
3. **Search filtering** (اگر `search` در query parameter وجود دارد):
   - فیلتر با `Q(name__icontains=search) | Q(name_en__icontains=search) | Q(public_code__icontains=search)`
4. **Parent filter** (اگر `parent` در query parameter وجود دارد):
   - فیلتر: `queryset.filter(parent_category_id=parent_id)`
5. مرتب‌سازی: `order_by('parent_category__name', 'sort_order', 'public_code', 'name')`
6. queryset را برمی‌گرداند

**Query Parameters**:
- `search`: جستجو در name، name_en، public_code
- `parent`: فیلتر بر اساس parent category ID

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`, `parent_categories`, `search_term`, `selected_parent`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `page_title = _('Ticket Subcategories')`
3. **دریافت parent categories برای filter dropdown**:
   - دریافت `company_id` از session
   - اگر `company_id` موجود است:
     - فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=True, is_enabled=1)`
     - مرتب‌سازی: `order_by('name')`
     - اضافه کردن `parent_categories` به context
4. اضافه کردن `search_term = request.GET.get('search', '')`
5. اضافه کردن `selected_parent = request.GET.get('parent', '')`
6. context را برمی‌گرداند

**Context Variables اضافه شده**:
- `page_title`: `_('Ticket Subcategories')`
- `parent_categories`: QuerySet از parent categories (برای filter dropdown)
- `search_term`: مقدار `search` از query parameter
- `selected_parent`: مقدار `parent` از query parameter

**Query Parameters**:
- `search`: جستجو در name, name_en, public_code
- `parent`: فیلتر بر اساس parent category

**URL**: `/ticketing/subcategories/`

---

## TicketSubcategoryCreateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, CreateView`

**Template**: `ticketing/subcategory_form.html`

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
- اضافه کردن `request` به form (از طریق ایجاد form instance و تنظیم `form.request`)

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- اضافه کردن `page_title = _('Create Subcategory')`
- ساخت `permission_formset`:
  - اگر POST: از POST data
  - اگر GET: empty formset
  - تنظیم `request` روی تمام forms در formset
- دریافت `parent_categories` برای dropdown:
  - فیلتر: `company_id`, `parent_category__isnull=True`, `is_enabled=1`
  - مرتب‌سازی بر اساس `name`

#### `form_valid(self, form: TicketCategoryForm) -> HttpResponseRedirect`

**توضیح**: Subcategory و permissions را ذخیره می‌کند (با بررسی parent_category).

**پارامترهای ورودی**:
- `form`: فرم معتبر `TicketCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. **بررسی parent_category** (subcategory requirement):
   - اگر `form.instance.parent_category_id` تنظیم نشده باشد:
     - اضافه کردن error: `form.add_error("parent_category", _("Subcategory must have a parent category."))`
     - بازگشت `form_invalid(form)`
2. دریافت `company_id` از session
3. اگر `company_id` موجود است:
   - تنظیم `form.instance.company_id = company_id`
4. ذخیره subcategory: `response = super().form_valid(form)`
5. **ساخت permission formset**:
   - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object)`
6. **تنظیم request روی تمام forms**:
   - برای هر `perm_form` در `permission_formset.forms`:
     - `perm_form.request = self.request`
7. **Validate و save formset**:
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
8. نمایش پیام موفقیت: "Subcategory created successfully."
9. بازگشت `response`

**نکات مهم**:
- `parent_category` required است (subcategory requirement)
- اگر `parent_category` تنظیم نشده باشد، form invalid می‌شود

**نکات مهم**:
- `parent_category` required است (subcategory requirement)
- اگر `parent_category` تنظیم نشده باشد، form invalid می‌شود

**URL**: `/ticketing/subcategories/create/`

---

## TicketSubcategoryUpdateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, UpdateView`

**Template**: `ticketing/subcategory_form.html`

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
- اضافه کردن `request` به form (از طریق ایجاد form instance و تنظیم `form.request`)

#### `get_queryset(self) -> QuerySet`
- فیلتر بر اساس `active_company_id` از session
- فیلتر: `parent_category__isnull=False` (فقط subcategories)

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`
- اضافه کردن `page_title = _('Edit Subcategory')`
- ساخت `permission_formset`:
  - اگر POST: از POST data
  - اگر GET: از instance
  - تنظیم `request` روی تمام forms در formset
- دریافت `parent_categories` برای dropdown:
  - فیلتر: `company_id`, `parent_category__isnull=True`, `is_enabled=1`
  - مرتب‌سازی بر اساس `name`

#### `form_valid(self, form: TicketCategoryForm) -> HttpResponseRedirect`

**توضیح**: Subcategory و permissions را ذخیره می‌کند (با بررسی parent_category).

**پارامترهای ورودی**:
- `form`: فرم معتبر `TicketCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. **بررسی parent_category** (subcategory requirement):
   - اگر `form.instance.parent_category_id` تنظیم نشده باشد:
     - اضافه کردن error: `form.add_error("parent_category", _("Subcategory must have a parent category."))`
     - بازگشت `form_invalid(form)`
2. ذخیره subcategory: `response = super().form_valid(form)`
3. **ساخت permission formset**:
   - `TicketCategoryPermissionFormSet(self.request.POST, instance=self.object)`
4. **تنظیم request روی تمام forms**:
   - برای هر `perm_form` در `permission_formset.forms`:
     - `perm_form.request = self.request`
5. **Validate و save formset**:
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
6. نمایش پیام موفقیت: "Subcategory updated successfully."
7. بازگشت `response`

**نکات مهم**:
- `parent_category` required است (subcategory requirement)
- اگر `parent_category` تنظیم نشده باشد، form invalid می‌شود

**URL**: `/ticketing/subcategories/<pk>/edit/`

---

## TicketSubcategoryDeleteView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView`

**Template**: `ticketing/subcategory_confirm_delete.html`

**Success URL**: `ticketing:subcategories`

**Attributes**:
- `model`: `TicketCategory`
- `template_name`: `'ticketing/subcategory_confirm_delete.html'`
- `success_url`: `reverse_lazy('ticketing:subcategories')`
- `feature_code`: `'ticketing.management.subcategories'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering و parent category filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده (فقط subcategories)

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketCategory.objects.filter(company_id=company_id, parent_category__isnull=False)` (فقط subcategories)
3. queryset را برمی‌گرداند

**نکات مهم**:
- فقط subcategories (با `parent_category__isnull=False`) برگردانده می‌شوند

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: TicketSubcategory را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Subcategory deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که TicketSubcategory را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`

**Context Variables اضافه شده**:
- `page_title`: `_('Delete Subcategory')`

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


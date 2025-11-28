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
- `get_queryset()`: فیلتر بر اساس company و `parent_category__isnull=False`، search، parent filter
- `get_context_data()`: اضافه کردن `parent_categories` برای filter dropdown

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
**منطق**:
1. بررسی `parent_category`:
   - اگر `parent_category_id` تنظیم نشده باشد:
     - اضافه کردن error به form: `form.add_error("parent_category", _("Subcategory must have a parent category."))`
     - بازگشت `form_invalid(form)`
2. تنظیم `company_id` از session به `form.instance.company_id`
3. ذخیره subcategory با `super().form_valid(form)`
4. ساخت `permission_formset` از POST data با instance
5. تنظیم `request` روی تمام forms در formset
6. اگر formset valid باشد:
   - فراخوانی `permission_formset.save(commit=False)`
   - برای هر permission:
     - تنظیم `company_id`
     - تنظیم `category_code` از `category.public_code`
     - ذخیره permission
7. اگر formset invalid باشد:
   - بازگشت `form_invalid(form)`
8. نمایش پیام موفقیت
9. بازگشت response

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
**منطق**:
1. بررسی `parent_category`:
   - اگر `parent_category_id` تنظیم نشده باشد:
     - اضافه کردن error به form
     - بازگشت `form_invalid(form)`
2. ذخیره subcategory با `super().form_valid(form)`
3. ساخت `permission_formset` از POST data با instance
4. تنظیم `request` روی تمام forms در formset
5. اگر formset valid باشد:
   - دریافت `company_id` از session
   - فراخوانی `permission_formset.save(commit=False)`
   - برای هر permission:
     - تنظیم `company_id`
     - تنظیم `category_code` از `category.public_code`
     - ذخیره permission
   - فراخوانی `permission_formset.save()` برای حذف deleted items
6. اگر formset invalid باشد:
   - بازگشت `form_invalid(form)`
7. نمایش پیام موفقیت
8. بازگشت response

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
- `get_queryset()`: فیلتر بر اساس company و `parent_category__isnull=False`
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `page_title`

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


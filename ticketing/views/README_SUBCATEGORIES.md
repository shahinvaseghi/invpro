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
- `get_form_kwargs()`: اضافه کردن `request` به form
- `get_context_data()`: اضافه کردن `permission_formset` و `parent_categories`
- `form_valid()`: بررسی `parent_category` (required)، ذخیره subcategory و permissions

**نکات مهم**:
- `parent_category` required است (subcategory requirement)

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
- `get_form_kwargs()`: اضافه کردن `request` به form
- `get_queryset()`: فیلتر بر اساس company و `parent_category__isnull=False`
- `get_context_data()`: اضافه کردن `permission_formset` و `parent_categories`
- `form_valid()`: بررسی `parent_category` (required)، ذخیره subcategory و permissions

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


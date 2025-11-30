# shared/views/groups.py - Group Management Views (Complete Documentation)

**هدف**: Views برای مدیریت Groups (گروه‌های کاربری) در ماژول shared

این فایل شامل **4 کلاس view**:
- `GroupListView`: فهرست تمام groups
- `GroupCreateView`: ایجاد group جدید
- `GroupUpdateView`: ویرایش group موجود
- `GroupDeleteView`: حذف group

---

## وابستگی‌ها

- `shared.forms`: `GroupForm`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.contrib.auth.models`: `Group`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `django.urls`: `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `django.contrib.messages`
- `typing`: `Any`, `Dict`, `Optional`

---

## GroupListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `shared/groups_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `Group` (Django's built-in Group model)
- `template_name`: `'shared/groups_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `20`
- `feature_code`: `'shared.groups'`

**متدها**:

#### `get_queryset() -> QuerySet`

**توضیح**: فیلتر کردن groups بر اساس search و status.

**مقدار بازگشتی**:
- `QuerySet`: queryset groups فیلتر شده

**منطق**:
1. دریافت تمام groups
2. مرتب‌سازی بر اساس `name`
3. `prefetch_related('user_set', 'profile__access_levels')` برای بهینه‌سازی
4. فیلتر بر اساس `search` (در `name`)
5. فیلتر بر اساس `status` ('active' یا 'inactive') - از `profile__is_enabled`

**Query Parameters**:
- `search`: جستجو در name
- `status`: 'active' یا 'inactive' (بر اساس `profile.is_enabled`)

**نکات مهم**:
- از Django's built-in `Group` model استفاده می‌کند
- Status از `GroupProfile.is_enabled` استخراج می‌شود

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و filter values به context.

**Context Variables**:
- `object_list`: queryset groups (paginated، از `page_obj.object_list`)
- `active_module`: `'shared'`
- `page_title`: `_('Groups')`
- `breadcrumbs`: لیست breadcrumbs
- `create_url`: URL برای ایجاد group جدید
- `show_filters`: `True`
- `status_filter_value`: مقدار status از GET
- `search_placeholder`: `_('Group name')`
- `show_actions`: `True`
- `edit_url_name`: `'shared:group_edit'`
- `delete_url_name`: `'shared:group_delete'`
- `empty_state_title`, `empty_state_message`, `empty_state_icon`: برای empty state

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با filter values

**URL**: `/shared/groups/`

---

## GroupCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `shared/group_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `GroupForm`

**Success URL**: `shared:groups`

**Attributes**:
- `feature_code`: `'shared.groups'`
- `required_action`: `'create'`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `GroupForm`
- `active_module`: `'shared'`
- `form_title`: `_('Create Group')`
- `page_title`: `_('Create Group')`
- `is_create`: `True`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel (back to groups list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

---

#### `form_valid(self, form: GroupForm) -> Any`

**توضیح**: نمایش پیام موفقیت بعد از ایجاد group.

**پارامترهای ورودی**:
- `form`: `GroupForm` validated

**مقدار بازگشتی**:
- `Any`: HttpResponseRedirect

**منطق**:
1. فراخوانی `super().form_valid(form)` برای ذخیره group
2. نمایش پیام موفقیت
3. بازگشت response

**URL**: `/shared/groups/create/`

---

## GroupUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `shared/group_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `GroupForm`

**Success URL**: `shared:groups`

**Attributes**:
- `feature_code`: `'shared.groups'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `GroupForm`
- `object`: group object (از `get_object()`)
- `active_module`: `'shared'`
- `form_title`: `_('Edit Group')`
- `page_title`: `_('Edit Group')`
- `is_create`: `False`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel (back to groups list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

---

#### `form_valid(self, form: GroupForm) -> Any`

**توضیح**: نمایش پیام موفقیت بعد از به‌روزرسانی group.

**پارامترهای ورودی**:
- `form`: `GroupForm` validated

**مقدار بازگشتی**:
- `Any`: HttpResponseRedirect

**منطق**:
1. فراخوانی `super().form_valid(form)` برای ذخیره group
2. نمایش پیام موفقیت
3. بازگشت response

**URL**: `/shared/groups/<pk>/edit/`

---

## GroupDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `shared:groups`

**Attributes**:
- `feature_code`: `'shared.groups'`
- `required_action`: `'delete_own'`

**متدها**:

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> Any`

**توضیح**: حذف group و نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Any`: HttpResponseRedirect

**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().delete()` برای حذف group

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `object`: group object (از `get_object()`)
- `active_module`: `'shared'`
- `delete_title`: `_('Delete Group')`
- `confirmation_message`: پیام تایید حذف با group name
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `object_details`: لیست جزئیات group برای نمایش (name, members count)
- `cancel_url`: URL برای cancel (back to groups list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/groups/<pk>/delete/`

---

## نکات مهم

### 1. Django Group Model
- از Django's built-in `Group` model استفاده می‌کند
- Groups می‌توانند users و permissions داشته باشند
- از `GroupProfile` برای extended information استفاده می‌شود

### 2. GroupProfile Integration
- Status از `GroupProfile.is_enabled` استخراج می‌شود
- `prefetch_related('profile__access_levels')` برای بهینه‌سازی

### 3. Permission Checking
- از `FeaturePermissionRequiredMixin` استفاده می‌کند
- `feature_code = 'shared.groups'`
- Actions: `'view'`, `'create'`, `'edit_own'`, `'delete_own'`

### 4. Search and Filter
- Search در `name`
- Status filter: 'active' یا 'inactive' (بر اساس `profile.is_enabled`)

### 5. Prefetch Optimization
- `prefetch_related('user_set', 'profile__access_levels')` برای جلوگیری از N+1 queries

### 6. Simple CRUD
- این views ساده‌تر از access levels هستند
- فقط group name را مدیریت می‌کنند
- Extended information (access levels) در `GroupProfile` است

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Error Handling**: خطاها با messages نمایش داده می‌شوند
3. **Context Management**: `active_module` در تمام views اضافه می‌شود
4. **Simple Structure**: ساختار ساده CRUD بدون complex logic

---

## استفاده در پروژه

این views در URLs ماژول shared ثبت شده‌اند:

```python
# shared/urls.py
path('groups/', GroupListView.as_view(), name='groups'),
path('groups/create/', GroupCreateView.as_view(), name='group_create'),
path('groups/<int:pk>/edit/', GroupUpdateView.as_view(), name='group_edit'),
path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='group_delete'),
```

---

## ارتباط با سایر ماژول‌ها

### Django Auth
- از Django's built-in `Group` model استفاده می‌کند
- Groups می‌توانند users و permissions داشته باشند

### Shared Models
- از `GroupProfile` برای extended information استفاده می‌شود
- `GroupProfile` می‌تواند access levels داشته باشد

### Shared Forms
- از `GroupForm` برای create و update استفاده می‌کند

---

## Migration to Generic Templates

این views در migration به template های generic منتقل شده‌اند:

### List Template
- **Template**: `shared/groups_list.html` (extends `shared/generic/generic_list.html`)
- **Changes**: 
  - `context_object_name` از `'groups'` به `'object_list'` تغییر یافت
  - Context variables برای generic template اضافه شد (breadcrumbs, page_title, create_url, etc.)

### Form Template
- **Template**: `shared/group_form.html` (extends `shared/generic/generic_form.html`)
- **Changes**:
  - Template از `base.html` به `generic_form.html` منتقل شد
  - Blocks override شده: `form_sections`, `form_actions_extra`
  - Context variables اضافه شد: `breadcrumbs`, `cancel_url`, `form_title`

### Delete Template
- **Template**: `shared/generic/generic_confirm_delete.html` (مستقیم استفاده می‌شود)
- **Changes**:
  - Template اختصاصی حذف شد
  - `get_context_data` به‌روزرسانی شد تا context variables مناسب را ارسال کند


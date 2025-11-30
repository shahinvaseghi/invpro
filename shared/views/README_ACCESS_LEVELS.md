# shared/views/access_levels.py - Access Level Management Views (Complete Documentation)

**هدف**: Views برای مدیریت Access Levels (سطح دسترسی) در ماژول shared

این فایل شامل **4 کلاس view**:
- `AccessLevelListView`: فهرست تمام access levels
- `AccessLevelCreateView`: ایجاد access level جدید
- `AccessLevelUpdateView`: ویرایش access level موجود
- `AccessLevelDeleteView`: حذف access level

---

## وابستگی‌ها

- `shared.views.base`: `AccessLevelPermissionMixin`
- `shared.models`: `AccessLevel`
- `shared.forms`: `AccessLevelForm`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `django.urls`: `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `django.contrib.messages`
- `django.db.models`: `Q`
- `typing`: `Any`, `Dict`, `Optional`

---

## AccessLevelListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `shared/access_levels_list.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `AccessLevel`
- `template_name`: `'shared/access_levels_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `20`
- `feature_code`: `'shared.access_levels'`

**متدها**:

#### `get_queryset() -> QuerySet`

**توضیح**: فیلتر کردن access levels بر اساس search و status.

**مقدار بازگشتی**:
- `QuerySet`: queryset access levels فیلتر شده

**منطق**:
1. دریافت تمام access levels
2. مرتب‌سازی بر اساس `code`
3. `prefetch_related('permissions')` برای بهینه‌سازی
4. فیلتر بر اساس `search` (در `code` یا `name`)
5. فیلتر بر اساس `status` ('active' یا 'inactive')

**Query Parameters**:
- `search`: جستجو در code و name
- `status`: 'active' یا 'inactive'

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و filter values به context.

**Context Variables**:
- `object_list`: queryset access levels (paginated، از `page_obj.object_list`)
- `active_module`: `'shared'`
- `page_title`: `_('Access Levels')`
- `breadcrumbs`: لیست breadcrumbs
- `create_url`: URL برای ایجاد access level جدید
- `show_filters`: `True`
- `status_filter_value`: مقدار status از GET
- `search_placeholder`: `_('Code or name')`
- `show_actions`: `True`
- `edit_url_name`: `'shared:access_level_edit'`
- `delete_url_name`: `'shared:access_level_delete'`
- `empty_state_title`, `empty_state_message`, `empty_state_icon`: برای empty state

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با filter values

**URL**: `/shared/access-levels/`

---

## AccessLevelCreateView

**Type**: `FeaturePermissionRequiredMixin, AccessLevelPermissionMixin, CreateView`

**Template**: `shared/access_level_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `AccessLevelForm`

**Success URL**: `shared:access_levels`

**Attributes**:
- `feature_code`: `'shared.access_levels'`
- `required_action`: `'create'`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module, form title, و feature permissions به context.

**Context Variables**:
- `form`: `AccessLevelForm`
- `active_module`: `'shared'`
- `form_title`: `_('Create Access Level')`
- `page_title`: `_('Create Access Level')`
- `is_create`: `True`
- `feature_permissions`: لیست feature permissions (از `_prepare_feature_context()`)
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel (back to access levels list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با feature_permissions

**نکات مهم**:
- از `AccessLevelPermissionMixin._prepare_feature_context()` برای آماده‌سازی feature permissions استفاده می‌کند
- Feature permissions برای نمایش checkbox‌های permissions در template استفاده می‌شوند

---

#### `form_valid(self, form: AccessLevelForm) -> Any`

**توضیح**: ذخیره access level و permissions.

**پارامترهای ورودی**:
- `form`: `AccessLevelForm` validated

**مقدار بازگشتی**:
- `Any`: HttpResponseRedirect

**منطق**:
1. فراخوانی `super().form_valid(form)` برای ذخیره access level
2. `refresh_from_db()` برای اطمینان از latest data
3. فراخوانی `_save_permissions(form)` برای ذخیره permissions از POST data
4. نمایش پیام موفقیت
5. بازگشت response

**نکات مهم**:
- از `AccessLevelPermissionMixin._save_permissions()` برای ذخیره permissions استفاده می‌کند
- Permissions از POST data استخراج و ذخیره می‌شوند

**URL**: `/shared/access-levels/create/`

---

## AccessLevelUpdateView

**Type**: `FeaturePermissionRequiredMixin, AccessLevelPermissionMixin, UpdateView`

**Template**: `shared/access_level_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `AccessLevelForm`

**Success URL**: `shared:access_levels`

**Attributes**:
- `feature_code`: `'shared.access_levels'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module, form title, و feature permissions به context.

**Context Variables**:
- `form`: `AccessLevelForm`
- `object`: access level object (از `get_object()`)
- `active_module`: `'shared'`
- `form_title`: `_('Edit Access Level')`
- `page_title`: `_('Edit Access Level')`
- `is_create`: `False`
- `feature_permissions`: لیست feature permissions (از `_prepare_feature_context(self.object)`)
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel (back to access levels list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با feature_permissions

**نکات مهم**:
- `_prepare_feature_context(self.object)` برای populate کردن existing permissions

---

#### `form_valid(self, form: AccessLevelForm) -> Any`

**توضیح**: ذخیره access level و permissions.

**پارامترهای ورودی**:
- `form`: `AccessLevelForm` validated

**مقدار بازگشتی**:
- `Any`: HttpResponseRedirect

**منطق**:
1. فراخوانی `super().form_valid(form)` برای ذخیره access level
2. فراخوانی `_save_permissions(form)` برای ذخیره permissions از POST data
3. نمایش پیام موفقیت
4. بازگشت response

**URL**: `/shared/access-levels/<pk>/edit/`

---

## AccessLevelDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `shared:access_levels`

**Attributes**:
- `feature_code`: `'shared.access_levels'`
- `required_action`: `'delete_own'`

**متدها**:

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> Any`

**توضیح**: حذف access level و نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Any`: HttpResponseRedirect

**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().delete()` برای حذف access level

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `object`: access level object (از `get_object()`)
- `active_module`: `'shared'`
- `delete_title`: `_('Delete Access Level')`
- `confirmation_message`: پیام تایید حذف با access level name
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `object_details`: لیست جزئیات access level برای نمایش (code, name, is_global)
- `cancel_url`: URL برای cancel (back to access levels list)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/access-levels/<pk>/delete/`

---

## AccessLevelPermissionMixin

**Type**: Mixin (از `shared.views.base`)

**توضیح**: Mixin برای مدیریت feature permissions در access level forms.

**متدها**:

#### `_prepare_feature_context(self, instance: Optional[Any] = None) -> list`

**توضیح**: آماده‌سازی feature permissions context برای template.

**پارامترهای ورودی**:
- `instance`: Optional AccessLevel instance (برای populate existing permissions)

**مقدار بازگشتی**:
- `list`: لیست dictionaries با feature permissions grouped by module

**منطق**:
1. استخراج existing permissions از instance (اگر موجود باشد)
2. برای هر feature در `FEATURE_PERMISSION_MAP`:
   - استخراج `view_scope` از metadata یا fallback به legacy fields
   - استخراج checked actions از metadata
   - ساخت feature data با code, label, view_scope, actions
3. Group features by module
4. Return module list با features

**Context Structure**:
```python
[
    {
        'code': 'inventory',
        'label': 'Inventory',
        'features': [
            {
                'code': 'inventory.items',
                'html_id': 'inventory__items',
                'label': 'Items',
                'view_scope': 'all',
                'actions': [
                    {'code': 'create', 'label': 'Create', 'checked': True},
                    ...
                ]
            },
            ...
        ]
    },
    ...
]
```

---

#### `_save_permissions(self, form: Any) -> None`

**توضیح**: ذخیره permissions از form POST data.

**پارامترهای ورودی**:
- `form`: Form object (استفاده نمی‌شود، از `self.request.POST` استفاده می‌شود)

**منطق**:
1. برای هر feature در `FEATURE_PERMISSION_MAP`:
   - دریافت `view_scope` از POST (`perm-{html_key}-view`)
   - دریافت selected actions از POST checkboxes
   - اگر `view_scope == 'none'` و هیچ action انتخاب نشده باشد:
     - حذف existing permission (اگر موجود باشد)
   - در غیر این صورت:
     - `get_or_create` permission
     - تنظیم legacy boolean fields (`can_view`, `can_create`, etc.)
     - ساخت `metadata.actions` dictionary
     - ذخیره permission
2. حذف stale permissions (که دیگر در POST نیستند)

**POST Data Format**:
- `perm-{html_key}-view`: 'none', 'own', یا 'all'
- `perm-{html_key}-{action}`: 'on' (checkbox checked)

**نکات مهم**:
- از `metadata.actions` برای ذخیره granular permissions استفاده می‌کند
- Legacy boolean fields برای backward compatibility حفظ می‌شوند

---

## نکات مهم

### 1. Permission Management
- Access levels می‌توانند permissions برای multiple features داشته باشند
- Permissions در `AccessLevelPermission` model ذخیره می‌شوند
- از `metadata.actions` برای granular permissions استفاده می‌شود

### 2. Feature Permissions Context
- `_prepare_feature_context` برای آماده‌سازی permissions در template استفاده می‌شود
- Features grouped by module می‌شوند
- View scope و actions به صورت checkbox نمایش داده می‌شوند

### 3. Permission Saving
- `_save_permissions` permissions را از POST data استخراج و ذخیره می‌کند
- Stale permissions (که دیگر انتخاب نشده‌اند) حذف می‌شوند
- Legacy boolean fields برای backward compatibility حفظ می‌شوند

### 4. Permission Checking
- از `FeaturePermissionRequiredMixin` استفاده می‌کند
- `feature_code = 'shared.access_levels'`
- Actions: `'view'`, `'create'`, `'edit_own'`, `'delete_own'`

### 5. Search and Filter
- Search در `code` و `name`
- Status filter: 'active' یا 'inactive'

### 6. Prefetch Optimization
- `prefetch_related('permissions')` برای جلوگیری از N+1 queries

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Permission Management**: از `AccessLevelPermissionMixin` برای مدیریت permissions استفاده می‌کند
3. **Error Handling**: خطاها با messages نمایش داده می‌شوند
4. **Context Management**: `active_module` در تمام views اضافه می‌شود

---

## استفاده در پروژه

این views در URLs ماژول shared ثبت شده‌اند:

```python
# shared/urls.py
path('access-levels/', AccessLevelListView.as_view(), name='access_levels'),
path('access-levels/create/', AccessLevelCreateView.as_view(), name='access_level_create'),
path('access-levels/<int:pk>/edit/', AccessLevelUpdateView.as_view(), name='access_level_edit'),
path('access-levels/<int:pk>/delete/', AccessLevelDeleteView.as_view(), name='access_level_delete'),
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `AccessLevel` model استفاده می‌کند
- از `AccessLevelPermission` برای ذخیره permissions استفاده می‌کند

### Shared Forms
- از `AccessLevelForm` برای create و update استفاده می‌کند

### Shared Base Views
- از `AccessLevelPermissionMixin` برای مدیریت permissions استفاده می‌کند

### Shared Permissions
- از `FEATURE_PERMISSION_MAP` برای feature definitions استفاده می‌کند
- از `PermissionAction` برای action definitions استفاده می‌کند

---

## Migration to Generic Templates

این views در migration به template های generic منتقل شده‌اند:

### List Template
- **Template**: `shared/access_levels_list.html` (extends `shared/generic/generic_list.html`)
- **Changes**: 
  - `context_object_name` از `'access_levels'` به `'object_list'` تغییر یافت
  - Context variables برای generic template اضافه شد (breadcrumbs, page_title, create_url, etc.)

### Form Template
- **Template**: `shared/access_level_form.html` (extends `shared/generic/generic_form.html`)
- **Changes**:
  - Template از `base.html` به `generic_form.html` منتقل شد
  - Blocks override شده: `form_sections`, `form_extra` (برای feature permissions), `form_scripts`
  - JavaScript و CSS برای accordion permissions حفظ شد
  - Context variables اضافه شد: `breadcrumbs`, `cancel_url`, `form_title`

### Delete Template
- **Template**: `shared/generic/generic_confirm_delete.html` (مستقیم استفاده می‌شود)
- **Changes**:
  - Template اختصاصی حذف شد
  - `get_context_data` به‌روزرسانی شد تا context variables مناسب را ارسال کند


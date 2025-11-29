# shared/views/base.py - Base Views and Mixins

**هدف**: کلاس‌های پایه و mixin‌های قابل استفاده مجدد برای views ماژول shared

---

## Mixins

### `UserAccessFormsetMixin`

**توضیح**: Helper mixin برای مدیریت `UserCompanyAccess` formsets در views ایجاد/ویرایش کاربر.

**متدها**:

#### `get_access_formset(self, form: Optional[Any] = None) -> UserCompanyAccessFormSet`

**توضیح**: دریافت یا ایجاد `UserCompanyAccess` formset برای یک کاربر.

**پارامترهای ورودی**:
- `form` (Optional[Any]): فرم کاربر (اختیاری)

**مقدار بازگشتی**:
- `UserCompanyAccessFormSet`: formset instance

**منطق**:
1. تعیین instance از `form.instance` یا `self.object`
2. اگر instance وجود نداشته باشد، یک `User()` جدید ایجاد می‌کند
3. ساخت formset با POST data (اگر request method POST باشد) یا None
4. بازگشت formset

---

### `AccessLevelPermissionMixin`

**توضیح**: Mixin برای مدیریت permissions در views ایجاد/ویرایش access level.

**Attributes**:
- `template_name`: `'shared/access_level_form.html'`
- `action_labels`: Dictionary از action labels (در `__init__` تنظیم می‌شود)

**متدها**:

#### `__init__(self, *args: Any, **kwargs: Any) -> None`

**توضیح**: Initialize action labels dictionary.

**منطق**:
- ساخت `action_labels` dictionary با ترجمه‌های فارسی برای تمام `PermissionAction` values

---

#### `_feature_key(self, code: str) -> str`

**توضیح**: تبدیل feature code به HTML-safe key.

**پارامترهای ورودی**:
- `code` (str): Feature code (مثلاً `'inventory.items'`)

**مقدار بازگشتی**:
- `str`: Normalized key (مثلاً `'inventory__items'`)

**منطق**:
- جایگزینی `.` با `__` برای استفاده در templates

---

#### `_prepare_feature_context(self, instance: Optional[Any] = None) -> list`

**توضیح**: آماده‌سازی context برای feature permissions در template.

**پارامترهای ورودی**:
- `instance` (Optional[Any]): AccessLevel instance (اختیاری)

**مقدار بازگشتی**:
- `list`: لیست dictionaries با اطلاعات features و permissions، grouped by module

**منطق**:
1. اگر instance موجود باشد، permissions موجود را از database می‌خواند
2. برای هر feature در `FEATURE_PERMISSION_MAP`:
   - ساخت dictionary با code, label, actions, view_scope
   - بررسی permissions موجود و تنظیم checked states
3. Group کردن features بر اساس module code
4. ساخت module_list با module labels (شامل ماژول‌های جدید: accounting, sales, hr, office_automation, transportation, procurement)
5. بازگشت module_list

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
                'module_code': 'inventory',
                'view_supported': True,
                'view_scope': 'all',  # 'none', 'own', 'all'
                'actions': [
                    {
                        'code': 'create',
                        'label': 'Create',
                        'checked': True
                    },
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

**توضیح**: ذخیره permissions از POST data.

**پارامترهای ورودی**:
- `form`: فرم access level

**منطق**:
1. برای هر feature در `FEATURE_PERMISSION_MAP`:
   - خواندن `view_scope` از POST (`perm-{html_key}-view`)
   - خواندن selected actions از POST checkboxes
   - اگر `view_scope == 'none'` و هیچ action انتخاب نشده باشد:
     - حذف permission موجود (اگر وجود داشته باشد)
   - در غیر این صورت:
     - ایجاد یا به‌روزرسانی `AccessLevelPermission`
     - تنظیم `can_view`, `can_create`, `can_edit`, `can_delete`, `can_approve`
     - ساخت `metadata` با `actions` dictionary
     - ذخیره permission
2. حذف permissions که دیگر در POST data نیستند (stale permissions)

---

## وابستگی‌ها

- `shared.models`: `User`, `UserCompanyAccess`, `AccessLevel`, `AccessLevelPermission`
- `shared.forms`: `UserCompanyAccessFormSet`
- `shared.permissions`: `FEATURE_PERMISSION_MAP`

---

## استفاده در پروژه

این mixin‌ها در views کاربر و access level استفاده می‌شوند:

```python
from shared.views.base import UserAccessFormsetMixin

class UserCreateView(UserAccessFormsetMixin, CreateView):
    model = User
    form_class = UserCreateForm
```

---

## نکات مهم

1. **Formset Management**: از mixin‌ها برای مدیریت formset‌های پیچیده استفاده می‌شود
2. **Permission Matrix**: ماتریس permission بر اساس `FEATURE_PERMISSION_MAP` ساخته می‌شود
3. **Primary Access**: یک دسترسی شرکت باید به عنوان primary تنظیم شود


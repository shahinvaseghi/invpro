# shared/views/base.py - Base Views and Mixins

**هدف**: کلاس‌های پایه و mixin‌های قابل استفاده مجدد برای views ماژول shared

---

## Mixins

### `UserAccessFormsetMixin`

**توضیح**: مدیریت formset دسترسی شرکت کاربر در views ایجاد/ویرایش کاربر.

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: formset دسترسی شرکت را به context اضافه می‌کند.

**مقدار بازگشتی**:
- Context با `access_formset` اضافه شده

---

#### `form_valid(form)`

**توضیح**: فرم و formset دسترسی شرکت را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم کاربر

**منطق**:
1. فرم کاربر را ذخیره می‌کند
2. formset دسترسی شرکت را ذخیره می‌کند
3. یک دسترسی را به عنوان primary تنظیم می‌کند

---

#### `_save_access_formset(formset) -> None`

**توضیح**: instance های formset دسترسی شرکت را ذخیره می‌کند.

**پارامترهای ورودی**:
- `formset`: `UserCompanyAccessFormSet`

**منطق**:
1. دسترسی‌های valid را ذخیره می‌کند
2. دسترسی‌های حذف شده را حذف می‌کند
3. یک دسترسی را به عنوان primary تنظیم می‌کند

---

### `AccessLevelPermissionMixin`

**توضیح**: مدیریت ماتریس permission در views ایجاد/ویرایش access level.

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: ماتریس permission را به context اضافه می‌کند.

**مقدار بازگشتی**:
- Context با `feature_permissions` و `permission_matrix` اضافه شده

---

#### `form_valid(form)`

**توضیح**: فرم access level و permissions را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم access level

**منطق**:
1. فرم access level را ذخیره می‌کند
2. permissions را از POST data ذخیره می‌کند

---

#### `_save_permissions(access_level, post_data) -> None`

**توضیح**: permissions را از POST data ذخیره می‌کند.

**پارامترهای ورودی**:
- `access_level`: شیء `AccessLevel`
- `post_data`: داده‌های POST

**منطق**:
1. permissions قبلی را حذف می‌کند
2. permissions جدید را از POST data ایجاد می‌کند
3. metadata (actions) را ذخیره می‌کند

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


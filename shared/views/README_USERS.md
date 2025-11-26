# shared/views/users.py - User Management Views (Complete Documentation)

**هدف**: Views برای مدیریت کاربران (CRUD operations) در ماژول shared

این فایل شامل **4 کلاس view**:
- `UserListView`: فهرست تمام کاربران
- `UserCreateView`: ایجاد کاربر جدید
- `UserUpdateView`: ویرایش کاربر موجود
- `UserDeleteView`: حذف کاربر

---

## وابستگی‌ها

- `shared.views.base`: `UserAccessFormsetMixin`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.forms`: `UserCreateForm`, `UserUpdateForm`
- `django.contrib.auth`: `get_user_model`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `django.db`: `transaction`
- `django.db.models`: `Q`
- `typing`: `Any`, `Dict`, `Optional`

---

## UserListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `shared/users_list.html`

**Attributes**:
- `model`: `User` (از `get_user_model()`)
- `template_name`: `'shared/users_list.html'`
- `context_object_name`: `'users'`
- `paginate_by`: `20`
- `feature_code`: `'shared.users'`

**متدها**:

#### `get_queryset() -> QuerySet`

**توضیح**: فیلتر کردن کاربران بر اساس search و status.

**مقدار بازگشتی**:
- `QuerySet`: queryset کاربران فیلتر شده

**منطق**:
1. دریافت تمام users
2. مرتب‌سازی بر اساس `username`
3. `prefetch_related('groups', 'company_accesses__company', 'company_accesses__access_level')`
4. فیلتر بر اساس `search` (در username, email, first_name, last_name)
5. فیلتر بر اساس `status` ('active' یا 'inactive')

**Query Parameters**:
- `search`: جستجو در username, email, first_name, last_name
- `status`: 'active' یا 'inactive'

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و filter values به context.

**Context Variables**:
- `users`: queryset کاربران (paginated)
- `active_module`: `'shared'`
- `search_term`: مقدار search از GET
- `status_filter`: مقدار status از GET

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با filter values

**URL**: `/shared/users/`

---

## UserCreateView

**Type**: `FeaturePermissionRequiredMixin, UserAccessFormsetMixin, CreateView`

**Template**: `shared/user_form.html`

**Form**: `UserCreateForm`

**Success URL**: `shared:users`

**Attributes**:
- `feature_code`: `'shared.users'`
- `required_action`: `'create'`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن access formset و active module به context.

**Context Variables**:
- `form`: `UserCreateForm`
- `access_formset`: `UserCompanyAccessFormSet` (از `get_access_formset()`)
- `active_module`: `'shared'`
- `page_title`: `_('Create User')`
- `is_create`: `True`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با access formset

---

#### `form_valid(self, form: UserCreateForm) -> HttpResponseRedirect`

**توضیح**: ذخیره user و company access formset.

**پارامترهای ورودی**:
- `form`: `UserCreateForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. دریافت `access_formset` از `get_access_formset(form)`
2. بررسی validation formset
3. در `transaction.atomic()`:
   - ذخیره user (شامل role toggles و groups)
   - تنظیم `access_formset.instance = self.object`
   - ذخیره access formset
4. نمایش پیام موفقیت
5. Redirect به success URL

**نکات مهم**:
- از `transaction.atomic()` برای atomicity استفاده می‌کند
- User و company accesses در یک transaction ذخیره می‌شوند

**URL**: `/shared/users/create/`

---

## UserUpdateView

**Type**: `FeaturePermissionRequiredMixin, UserAccessFormsetMixin, UpdateView`

**Template**: `shared/user_form.html`

**Form**: `UserUpdateForm`

**Success URL**: `shared:users`

**Attributes**:
- `feature_code`: `'shared.users'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن access formset و active module به context.

**Context Variables**:
- `form`: `UserUpdateForm`
- `access_formset`: `UserCompanyAccessFormSet` (از `get_access_formset()`)
- `active_module`: `'shared'`
- `page_title`: `_('Edit User')`
- `is_create`: `False`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با access formset

---

#### `form_valid(self, form: UserUpdateForm) -> HttpResponseRedirect`

**توضیح**: ذخیره user و company access formset.

**پارامترهای ورودی**:
- `form`: `UserUpdateForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. دریافت `access_formset` از `get_access_formset(form)`
2. بررسی validation formset
3. در `transaction.atomic()`:
   - ذخیره user (core data)
   - تنظیم `access_formset.instance = self.object`
   - ذخیره access formset
4. نمایش پیام موفقیت
5. Redirect به success URL

**نکات مهم**:
- مشابه `UserCreateView` اما برای update
- از `transaction.atomic()` برای atomicity استفاده می‌کند

**URL**: `/shared/users/<pk>/edit/`

---

## UserDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/user_confirm_delete.html`

**Success URL**: `shared:users`

**Attributes**:
- `feature_code`: `'shared.users'`
- `required_action`: `'delete_own'`

**متدها**:

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: حذف user و نمایش پیام موفقیت.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. نمایش پیام موفقیت
2. فراخوانی `super().delete()` برای حذف user

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `user`: user object (از `get_object()`)
- `active_module`: `'shared'`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/users/<pk>/delete/`

---

## UserAccessFormsetMixin

**Type**: Mixin (از `shared.views.base`)

**توضیح**: Helper mixin برای مدیریت `UserCompanyAccess` formsets.

**متدها**:

#### `get_access_formset(self, form: Optional[Any] = None) -> UserCompanyAccessFormSet`

**توضیح**: دریافت یا ایجاد `UserCompanyAccess` formset برای یک user.

**پارامترهای ورودی**:
- `form`: Optional form object

**مقدار بازگشتی**:
- `UserCompanyAccessFormSet`: formset برای company accesses

**منطق**:
1. دریافت instance از form یا self.object
2. اگر instance وجود نداشته باشد، ایجاد `User()` جدید
3. ایجاد `UserCompanyAccessFormSet` با POST data (اگر POST) یا None
4. بازگشت formset

**استفاده**:
- در `UserCreateView` و `UserUpdateView` استفاده می‌شود
- برای مدیریت دسترسی‌های company-level کاربران

---

## نکات مهم

### 1. Company Access Management
- هر user می‌تواند دسترسی به چندین company داشته باشد
- دسترسی‌ها از طریق `UserCompanyAccess` model مدیریت می‌شوند
- از `UserCompanyAccessFormSet` برای مدیریت multiple accesses استفاده می‌شود

### 2. Transaction Safety
- تمام تغییرات در `transaction.atomic()` انجام می‌شوند
- User و company accesses در یک transaction ذخیره می‌شوند
- در صورت خطا، تغییرات rollback می‌شوند

### 3. Permission Checking
- از `FeaturePermissionRequiredMixin` استفاده می‌کند
- `feature_code = 'shared.users'`
- Actions: `'view'`, `'create'`, `'edit_own'`, `'delete_own'`

### 4. Search Functionality
- جستجو در `username`, `email`, `first_name`, `last_name`
- از `Q` objects برای OR conditions استفاده می‌کند
- Case-insensitive search (`icontains`)

### 5. Status Filtering
- فیلتر بر اساس `is_active` (active/inactive)
- Query parameter: `status` ('active' یا 'inactive')

### 6. Prefetch Optimization
- `prefetch_related('groups', 'company_accesses__company', 'company_accesses__access_level')`
- برای جلوگیری از N+1 queries

### 7. Formset Integration
- از `UserAccessFormsetMixin` برای مدیریت access formset استفاده می‌کند
- Formset در context اضافه می‌شود
- Validation و save در `form_valid` انجام می‌شود

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Transaction Safety**: تمام تغییرات در `transaction.atomic()` انجام می‌شوند
3. **Formset Management**: از `UserAccessFormsetMixin` برای مدیریت company accesses استفاده می‌کند
4. **Error Handling**: خطاها با messages نمایش داده می‌شوند
5. **Context Management**: `active_module` در تمام views اضافه می‌شود

---

## استفاده در پروژه

این views در URLs ماژول shared ثبت شده‌اند:

```python
# shared/urls.py
path('users/', UserListView.as_view(), name='users'),
path('users/create/', UserCreateView.as_view(), name='user_create'),
path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
```

---

## ارتباط با سایر ماژول‌ها

### Shared Forms
- از `UserCreateForm` و `UserUpdateForm` استفاده می‌کند
- از `UserCompanyAccessFormSet` برای مدیریت company accesses استفاده می‌کند

### Shared Base Views
- از `UserAccessFormsetMixin` برای مدیریت access formset استفاده می‌کند

### Django Auth
- از `get_user_model()` برای دریافت User model استفاده می‌کند
- با Django's built-in User model کار می‌کند


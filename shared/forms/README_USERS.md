# shared/forms/users.py - User Forms (Complete Documentation)

**هدف**: Forms برای مدیریت کاربران و دسترسی‌های company-level در ماژول shared

این فایل شامل:
- **3 Form Classes**: `UserBaseForm`, `UserCreateForm`, `UserUpdateForm`
- **1 Formset Class**: `UserCompanyAccessForm`
- **1 Formset Factory**: `UserCompanyAccessFormSet`

---

## وابستگی‌ها

- `shared.models`: `Company`, `AccessLevel`, `UserCompanyAccess`, `ENABLED_FLAG_CHOICES`
- `django.contrib.auth`: `get_user_model`
- `django.contrib.auth.models`: `Group`
- `django.forms`: `BaseInlineFormSet`, `inlineformset_factory`
- `django.utils.translation`: `gettext_lazy`
- `typing`: `Optional`, `List`

---

## UserBaseForm

**Type**: `BaseModelForm` (از `shared.forms.base`)

**Model**: `User` (از `get_user_model()`)

**توضیح**: Base form برای ایجاد و ویرایش کاربران.

**Fields**:
- `username`: نام کاربری
- `email`: ایمیل
- `first_name`, `last_name`: نام و نام خانوادگی (فارسی)
- `first_name_en`, `last_name_en`: نام و نام خانوادگی (انگلیسی)
- `phone_number`, `mobile_number`: شماره تلفن و موبایل
- `is_active`, `is_staff`, `is_superuser`: boolean flags
- `default_company`: شرکت پیش‌فرض
- `groups`: گروه‌های کاربری (M2M field)
- `primary_groups`: گروه‌های اصلی کاربری (M2M field) - برای same-group permissions

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Initialize form با groups queryset و company filtering.

**منطق**:
1. حذف `company_id` از kwargs (users company-scoped نیستند)
2. فراخوانی `super().__init__()`
3. تنظیم `_pending_groups = None` و `_pending_primary_groups = None`
4. فیلتر `default_company` queryset: فقط enabled companies (`is_enabled=1`)
5. تنظیم `groups` queryset: تمام groups مرتب شده بر اساس name
6. تنظیم `primary_groups` queryset: تمام groups مرتب شده بر اساس name
7. اگر instance موجود باشد:
   - set initial `groups` از `instance.groups.all()`
   - set initial `primary_groups` از `instance.primary_groups.all()`
8. Override `is_active`, `is_staff`, `is_superuser` به BooleanField با checkbox widget (BaseModelForm به صورت خودکار 'form-check-input' class اضافه می‌کند)

---

#### `_store_groups(self) -> None`

**توضیح**: ذخیره groups و primary_groups به user instance.

**منطق**:
- اگر `_pending_groups` موجود باشد: `self.instance.groups.set(self._pending_groups)`
- اگر `_pending_primary_groups` موجود باشد: `self.instance.primary_groups.set(self._pending_primary_groups)`

---

#### `save(self, commit: bool = True) -> User`

**توضیح**: ذخیره user با groups.

**پارامترهای ورودی**:
- `commit`: آیا باید در database ذخیره شود

**مقدار بازگشتی**:
- `User`: user object

**منطق**:
1. استخراج groups از cleaned_data و ذخیره در `_pending_groups`
2. استخراج primary_groups از cleaned_data و ذخیره در `_pending_primary_groups`
3. فراخوانی `super().save(commit=commit)`
4. اگر commit=True: فراخوانی `_store_groups()`

---

#### `save_m2m(self) -> None`

**توضیح**: ذخیره many-to-many relationships (groups و primary_groups).

**منطق**:
1. **استخراج groups**:
   - اگر `_pending_groups` موجود باشد: استفاده از آن
   - در غیر این صورت: استفاده از `cleaned_data['groups']`
   - تبدیل QuerySet به list of IDs (برای جلوگیری از stale queryset issues)
2. **استخراج primary_groups**:
   - اگر `_pending_primary_groups` موجود باشد: استفاده از آن
   - در غیر این صورت: استفاده از `cleaned_data['primary_groups']`
   - تبدیل QuerySet به list of IDs
3. **Set groups و primary_groups**:
   - اگر `groups_to_set` موجود باشد: `self.instance.groups.set(groups_to_set)`
   - اگر `primary_groups_to_set` موجود باشد: `self.instance.primary_groups.set(primary_groups_to_set)`

**نکات مهم**:
- `super().save_m2m()` فراخوانی نمی‌شود چون `groups` و `primary_groups` در `Meta.fields` نیستند
- از list of IDs برای جلوگیری از stale queryset issues استفاده می‌شود
- Groups و primary_groups به صورت مستقیم set می‌شوند

---

## UserCreateForm

**Type**: `UserBaseForm`

**توضیح**: Form برای ایجاد کاربر جدید.

**Additional Fields**:
- `password1`: رمز عبور
- `password2`: تأیید رمز عبور

**متدها**:

#### `clean(self) -> dict`

**توضیح**: Validate password match.

**مقدار بازگشتی**:
- `dict`: cleaned_data

**منطق**:
- بررسی match بودن `password1` و `password2`
- اگر match نباشند: raise `ValidationError`

---

#### `save(self, commit: bool = True) -> User`

**توضیح**: ذخیره user با password.

**پارامترهای ورودی**:
- `commit`: آیا باید در database ذخیره شود

**مقدار بازگشتی**:
- `User`: user object

**منطق**:
1. فراخوانی `super().save(commit=False)`
2. Set password با `user.set_password(self.cleaned_data['password1'])`
3. اگر commit=True: save user و فراخوانی `save_m2m()`

---

## UserUpdateForm

**Type**: `UserBaseForm`

**توضیح**: Form برای ویرایش کاربر موجود.

**Additional Fields**:
- `new_password1`: رمز عبور جدید (optional)
- `new_password2`: تأیید رمز عبور جدید (optional)

**متدها**:

#### `clean(self) -> dict`

**توضیح**: Validate new password match.

**مقدار بازگشتی**:
- `dict`: cleaned_data

**منطق**:
- اگر `new_password1` یا `new_password2` موجود باشد:
  - بررسی match بودن
  - اگر match نباشند: raise `ValidationError`

---

#### `save(self, commit: bool = True) -> User`

**توضیح**: ذخیره user با optional password change.

**پارامترهای ورودی**:
- `commit`: آیا باید در database ذخیره شود

**مقدار بازگشتی**:
- `User`: user object

**منطق**:
1. **Ensure `_pending_groups` و `_pending_primary_groups` are set**:
   - اگر `_pending_groups` موجود نباشد یا None باشد:
     - تنظیم `_pending_groups = self.cleaned_data.get('groups')`
   - اگر `_pending_primary_groups` موجود نباشد یا None باشد:
     - تنظیم `_pending_primary_groups = self.cleaned_data.get('primary_groups')`
2. فراخوانی `super().save(commit=False)` (ذخیره user بدون commit)
3. **بررسی password**:
   - اگر `new_password1` موجود باشد:
     - فراخوانی `user.set_password(new_password)`
4. اگر `commit=True`:
   - ذخیره user با `user.save()`
   - **Set groups و primary_groups directly**:
     - اگر `_pending_groups` موجود باشد:
       - تبدیل به list of IDs
       - فراخوانی `user.groups.set(groups_to_set)`
     - اگر `_pending_primary_groups` موجود باشد:
       - تبدیل به list of IDs
       - فراخوانی `user.primary_groups.set(primary_groups_to_set)`
   - فراخوانی `self.save_m2m()` برای سایر M2M fields
5. اگر `commit=False`:
   - **Ensure `_pending_groups` و `_pending_primary_groups` are set** برای استفاده بعدی در `save_m2m()`
6. بازگشت user

**نکات مهم**:
- Groups و primary_groups به صورت مستقیم set می‌شوند (نه از طریق `save_m2m()`)
- Password فقط اگر `new_password1` موجود باشد تغییر می‌کند
- `_pending_groups` و `_pending_primary_groups` باید قبل از `super().save()` تنظیم شوند

---

## UserCompanyAccessForm

**Type**: `forms.ModelForm` (BaseModelForm به صورت خودکار 'form-control' class اضافه می‌کند)

**Model**: `UserCompanyAccess`

**توضیح**: Form برای user company access (استفاده در formset).

**Fields**:
- `company`: شرکت
- `access_level`: سطح دسترسی
- `is_primary`: آیا primary company است
- `is_enabled`: وضعیت

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Initialize form با filtered querysets.

**منطق**:
1. فیلتر `company` queryset: فقط enabled companies
2. فیلتر `access_level` queryset: فقط enabled access levels
3. تنظیم choices برای `is_primary` و `is_enabled` از `ENABLED_FLAG_CHOICES`

---

## BaseUserCompanyAccessFormSet

**Type**: `BaseInlineFormSet`

**توضیح**: Base formset برای user company access با validation.

**متدها**:

#### `clean(self) -> None`

**توضیح**: Validate که فقط یک primary company انتخاب شده باشد.

**منطق**:
1. فراخوانی `super().clean()` برای validation اولیه
2. **شمارش تعداد primary companies**:
   - `primary_count = 0`
   - برای هر form در `self.forms`:
     - اگر `form.cleaned_data.get('DELETE')` باشد: continue (skip deleted forms)
     - اگر `form.cleaned_data.get('company')` موجود نباشد: continue (skip empty forms)
     - اگر `form.cleaned_data.get('is_primary') == 1` باشد: `primary_count += 1`
3. **Validation**:
   - اگر `primary_count > 1`:
     - raise `forms.ValidationError(_('Only one primary company may be selected per user.'))`
     - اگر `is_primary == 1`: افزایش `primary_count`
3. اگر `primary_count > 1`:
   - raise `ValidationError(_('Only one primary company may be selected per user.'))`

**نکات مهم**:
- فقط یک primary company per user مجاز است
- Deleted forms در نظر گرفته نمی‌شوند
- Forms بدون company در نظر گرفته نمی‌شوند

---

## UserCompanyAccessFormSet

**Type**: `inlineformset_factory`

**توضیح**: Formset factory برای user company access.

**Configuration**:
- `model`: `User`
- `related_model`: `UserCompanyAccess`
- `form`: `UserCompanyAccessForm`
- `formset`: `BaseUserCompanyAccessFormSet`
- `fk_name`: `'user'`
- `extra`: `1`
- `can_delete`: `True`

**استفاده**:
```python
formset = UserCompanyAccessFormSet(
    request.POST if request.method == 'POST' else None,
    instance=user,
)
```

---

## نکات مهم

### 1. Groups Management
- Groups به صورت M2M field مدیریت می‌شوند
- از `_pending_groups` برای store کردن groups قبل از save استفاده می‌شود
- `save_m2m()` groups را مستقیماً set می‌کند (بدون فراخوانی super)

### 2. Password Handling
- در create: password الزامی است
- در update: password optional است (فقط اگر تغییر کند)

### 3. Company Access Management
- از `UserCompanyAccessFormSet` برای مدیریت multiple company accesses استفاده می‌شود
- فقط یک primary company per user مجاز است

### 4. Formset Validation
- `BaseUserCompanyAccessFormSet.clean()` بررسی می‌کند که فقط یک primary company انتخاب شده باشد

### 5. Queryset Filtering
- Companies: فقط enabled ones
- Access Levels: فقط enabled ones
- Groups: تمام groups

---

## استفاده در پروژه

### در Views
```python
from shared.forms import UserCreateForm, UserUpdateForm, UserCompanyAccessFormSet

# Create
form = UserCreateForm(request.POST)
formset = UserCompanyAccessFormSet(request.POST, instance=form.instance)

# Update
form = UserUpdateForm(request.POST, instance=user)
formset = UserCompanyAccessFormSet(request.POST, instance=user)
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `User`, `Company`, `AccessLevel`, `UserCompanyAccess` استفاده می‌کند

### Shared Views
- در `shared/views/users.py` استفاده می‌شود

### Django Auth
- از Django's built-in `User` و `Group` models استفاده می‌کند


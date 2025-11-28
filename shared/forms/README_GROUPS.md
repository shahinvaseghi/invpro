# shared/forms/groups.py - Group Forms (Complete Documentation)

**هدف**: Forms برای مدیریت Groups (گروه‌های کاربری) در ماژول shared

این فایل شامل **1 Form Class**:
- `GroupForm`: Form برای ایجاد و ویرایش groups با GroupProfile

---

## وابستگی‌ها

- `shared.models`: `AccessLevel`, `GroupProfile`, `ENABLED_FLAG_CHOICES`
- `django.contrib.auth.models`: `Group`
- `django.forms`
- `django.utils.translation`: `gettext_lazy`
- `typing`: `Optional`

---

## GroupForm

**Type**: `forms.ModelForm`

**Model**: `Group` (Django's built-in Group model)

**توضیح**: Form برای ایجاد و ویرایش groups با extended information در GroupProfile.

**Fields**:
- `name`: نام group (از Group model)
- `description`: توضیحات (از GroupProfile)
- `is_enabled`: وضعیت (از GroupProfile)
- `access_levels`: access levels (M2M از GroupProfile)

**Additional Fields**:
- `description`: `CharField` (not in Group model)
- `is_enabled`: `ChoiceField` (not in Group model)
- `access_levels`: `ModelMultipleChoiceField` (not in Group model)

**Widgets**:
- Text input برای name
- Textarea برای description (3 rows)
- Select برای is_enabled
- CheckboxSelectMultiple برای access_levels

**Labels**:
- تمام labels با `gettext_lazy` ترجمه شده‌اند

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Initialize form با profile data.

**منطق**:
1. دریافت `profile` از `self.instance.profile` (اگر موجود باشد)
2. تنظیم `access_levels` queryset: فقط enabled access levels
3. اگر profile موجود باشد:
   - Set initial values برای `description`, `is_enabled`, `access_levels` از profile
4. در غیر این صورت:
   - Set `is_enabled` initial به 1

**نکات مهم**:
- از `GroupProfile` برای extended information استفاده می‌شود
- اگر profile موجود نباشد، initial values تنظیم می‌شوند

---

#### `save(self, commit: bool = True) -> Group`

**توضیح**: ذخیره group با profile.

**پارامترهای ورودی**:
- `commit`: آیا باید در database ذخیره شود

**مقدار بازگشتی**:
- `Group`: group object

**منطق**:
1. فراخوانی `super().save(commit=commit)` برای ذخیره group
2. دریافت یا ایجاد `GroupProfile`:
   - استفاده از `getattr(group, 'profile', None)`
   - اگر profile موجود نباشد: ایجاد `GroupProfile(group=group)`
3. تنظیم profile fields:
   - `description` از `cleaned_data.get('description', '')`
   - `is_enabled` از `cleaned_data.get('is_enabled', 1)` (convert to int)
4. اگر `commit=True`:
   - ذخیره profile با `profile.save()`
   - Set access_levels M2M: `profile.access_levels.set(cleaned_data.get('access_levels') or [])`
5. اگر `commit=False`:
   - Store profile در `self._post_save_profile` برای later use در `save_m2m()`
6. بازگشت group

---

#### `save_m2m(self) -> None`

**توضیح**: ذخیره many-to-many relationships (access levels).

**منطق**:
1. فراخوانی `super().save_m2m()` برای سایر M2M fields
2. بررسی `_post_save_profile`:
   - اگر `_post_save_profile` موجود باشد (از `commit=False` در `save()`):
     - ذخیره profile با `profile.save()`
     - Set access_levels M2M: `profile.access_levels.set(cleaned_data.get('access_levels') or [])`

**نکات مهم**:
- `_post_save_profile` فقط زمانی تنظیم می‌شود که `commit=False` در `save()` باشد
- Access levels در `save_m2m()` ذخیره می‌شوند (برای compatibility با Django's form workflow)
   - Set access_levels M2M

**نکات مهم**:
- `save_m2m()` برای handle کردن commit=False case استفاده می‌شود
- Access levels در profile ذخیره می‌شوند (نه در group)

---

## نکات مهم

### 1. GroupProfile Integration
- از `GroupProfile` برای extended information استفاده می‌شود
- `description`, `is_enabled`, `access_levels` در profile ذخیره می‌شوند

### 2. Access Levels Management
- Access levels به صورت M2M field در GroupProfile مدیریت می‌شوند
- فقط enabled access levels در queryset نمایش داده می‌شوند

### 3. Save Logic
- Group و GroupProfile در یک transaction ذخیره می‌شوند
- از `_post_save_profile` برای handle کردن commit=False استفاده می‌شود

### 4. Django Group Model
- از Django's built-in `Group` model استفاده می‌کند
- Extended information در `GroupProfile` است

---

## استفاده در پروژه

### در Views
```python
from shared.forms import GroupForm

form = GroupForm(request.POST, instance=group)
if form.is_valid():
    form.save()  # Saves both Group and GroupProfile
    form.save_m2m()  # Saves access_levels M2M
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `GroupProfile` و `AccessLevel` models استفاده می‌کند

### Django Auth
- از Django's built-in `Group` model استفاده می‌کند

### Shared Views
- در `shared/views/groups.py` استفاده می‌شود


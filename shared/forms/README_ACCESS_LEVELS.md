# shared/forms/access_levels.py - Access Level Forms (Complete Documentation)

**هدف**: Forms برای مدیریت Access Levels در ماژول shared

این فایل شامل **1 Form Class**:
- `AccessLevelForm`: Form برای ایجاد و ویرایش access levels

---

## وابستگی‌ها

- `shared.models`: `AccessLevel`, `ENABLED_FLAG_CHOICES`
- `django.forms`
- `django.utils.translation`: `gettext_lazy`

---

## AccessLevelForm

**Type**: `BaseModelForm` (از `shared.forms.base`)

**Model**: `AccessLevel`

**توضیح**: Form برای ایجاد و ویرایش access levels.

**Fields**:
- `name`: نام access level
- `description`: توضیحات
- `is_enabled`: وضعیت
- `is_global`: آیا global role است

**Note**: `code` field در Meta.fields نیست (auto-generated از name)

**Widgets**:
- BaseModelForm به صورت خودکار `form-control` class اضافه می‌کند
- Text input برای name
- Textarea برای description (3 rows)
- Select برای is_enabled و is_global

**Labels**:
- تمام labels با `gettext_lazy` ترجمه شده‌اند

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Initialize form با choices و read-only code field.

**منطق**:
1. حذف `company_id` از kwargs (AccessLevels company-scoped نیستند)
2. فراخوانی `super().__init__()`
3. تنظیم choices برای `is_enabled` و `is_global` از `ENABLED_FLAG_CHOICES`
4. اگر instance موجود باشد و `instance.pk` موجود باشد (editing):
   - اضافه کردن `code` field به صورت read-only:
     - `forms.CharField` با `required=False`
     - `widget=forms.TextInput(attrs={'readonly': True})`
     - `initial=self.instance.code`
     - `help_text=_('Auto-generated from name. Cannot be changed.')`

**نکات مهم**:
- `code` field فقط در edit mode نمایش داده می‌شود (read-only)
- `code` از `name` به صورت خودکار generate می‌شود (در model)
- در create mode، `code` field نمایش داده نمی‌شود

---

## نکات مهم

### 1. Auto-Generated Code
- `code` field از `name` به صورت خودکار generate می‌شود
- در edit mode، `code` به صورت read-only نمایش داده می‌شود
- در create mode، `code` field وجود ندارد

### 2. Global Roles
- `is_global` flag برای تعیین global roles استفاده می‌شود
- Global roles می‌توانند در multiple companies استفاده شوند

### 3. Enabled Flag Choices
- از `ENABLED_FLAG_CHOICES` برای status choices استفاده می‌شود

---

## استفاده در پروژه

### در Views
```python
from shared.forms import AccessLevelForm

form = AccessLevelForm(request.POST, instance=access_level)
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `AccessLevel` model استفاده می‌کند

### Shared Views
- در `shared/views/access_levels.py` استفاده می‌شود
- Permissions در view level مدیریت می‌شوند (نه در form)


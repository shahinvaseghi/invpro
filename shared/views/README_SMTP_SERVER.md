# shared/views/smtp_server.py - SMTP Server Management Views (Complete Documentation)

**هدف**: Views برای مدیریت SMTP Server configurations در ماژول shared

این فایل شامل **4 کلاس view**:
- `SMTPServerListView`: فهرست تمام SMTP server configurations
- `SMTPServerCreateView`: ایجاد SMTP server configuration جدید
- `SMTPServerUpdateView`: ویرایش SMTP server configuration موجود
- `SMTPServerDeleteView`: حذف SMTP server configuration

---

## وابستگی‌ها

- `shared.models`: `SMTPServer`
- `shared.forms`: `SMTPServerForm`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse_lazy`
- `django.utils.translation`: `gettext_lazy`
- `django.contrib.messages`
- `typing`: `Any`, `Dict`

---

## SMTPServerListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `shared/smtp_server_list.html`

**Attributes**:
- `model`: `SMTPServer`
- `template_name`: `'shared/smtp_server_list.html'`
- `context_object_name`: `'smtp_servers'`
- `paginate_by`: `50`
- `feature_code`: `'shared.smtp_servers'`
- `required_action`: `'view_own'`

**متدها**:

#### `get_queryset() -> QuerySet`

**توضیح**: دریافت تمام SMTP server configurations.

**مقدار بازگشتی**:
- `QuerySet`: queryset SMTP servers مرتب شده بر اساس `name`

**منطق**:
- دریافت تمام SMTP servers
- مرتب‌سازی بر اساس `name`

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `smtp_servers`: queryset SMTP servers (paginated)
- `active_module`: `'shared'`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/smtp-servers/`

---

## SMTPServerCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `shared/smtp_server_form.html`

**Form**: `SMTPServerForm`

**Success URL**: `shared:smtp_servers`

**Attributes**:
- `feature_code`: `'shared.smtp_servers'`
- `required_action`: `'create'`

**متدها**:

#### `form_valid(self, form: SMTPServerForm) -> HttpResponseRedirect`

**توضیح**: تنظیم خودکار `created_by` و `edited_by`.

**پارامترهای ورودی**:
- `form`: `SMTPServerForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. تنظیم `form.instance.created_by = self.request.user`
2. تنظیم `form.instance.edited_by = self.request.user`
3. نمایش پیام موفقیت
4. فراخوانی `super().form_valid(form)` برای ذخیره

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `SMTPServerForm`
- `active_module`: `'shared'`
- `form_title`: `_('Create SMTP Server')`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

**URL**: `/shared/smtp-servers/create/`

---

## SMTPServerUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `shared/smtp_server_form.html`

**Form**: `SMTPServerForm`

**Success URL**: `shared:smtp_servers`

**Attributes**:
- `feature_code`: `'shared.smtp_servers'`
- `required_action`: `'edit_own'`

**متدها**:

#### `form_valid(self, form: SMTPServerForm) -> HttpResponseRedirect`

**توضیح**: تنظیم خودکار `edited_by` و handle کردن password.

**پارامترهای ورودی**:
- `form`: `SMTPServerForm` validated

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. تنظیم `form.instance.edited_by = self.request.user`
2. **Password handling**:
   - اگر password در cleaned_data خالی باشد (user password را تغییر نداده):
     - حفظ password موجود: `form.instance.password = self.object.password`
3. نمایش پیام موفقیت
4. فراخوانی `super().form_valid(form)` برای ذخیره

**نکات مهم**:
- اگر password در form خالی باشد، password موجود حفظ می‌شود
- این برای جلوگیری از overwrite کردن password در صورت عدم تغییر است

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module و form title به context.

**Context Variables**:
- `form`: `SMTPServerForm`
- `smtp_server`: SMTP server object (از `get_object()`)
- `active_module`: `'shared'`
- `form_title`: `_('Edit SMTP Server')`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با form_title

**URL**: `/shared/smtp-servers/<pk>/edit/`

---

## SMTPServerDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/smtp_server_confirm_delete.html`

**Success URL**: `shared:smtp_servers`

**Attributes**:
- `feature_code`: `'shared.smtp_servers'`
- `required_action`: `'delete_own'`
- `context_object_name`: `'smtp_server'`

**متدها**:

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module به context.

**Context Variables**:
- `smtp_server`: SMTP server object (از `get_object()`)
- `active_module`: `'shared'`

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با active_module

**URL**: `/shared/smtp-servers/<pk>/delete/`

---

## نکات مهم

### 1. Password Handling
- در update، اگر password خالی باشد، password موجود حفظ می‌شود
- این برای جلوگیری از overwrite کردن password در صورت عدم تغییر است

### 2. Permission Checking
- از `FeaturePermissionRequiredMixin` استفاده می‌کند
- `feature_code = 'shared.smtp_servers'`
- Actions: `'view_own'`, `'create'`, `'edit_own'`, `'delete_own'`

### 3. Auto Field Setting
- `created_by` و `edited_by` به صورت خودکار تنظیم می‌شوند

### 4. Simple CRUD
- ساختار ساده CRUD بدون complex logic
- فقط SMTP server configurations را مدیریت می‌کند

### 5. No Filtering
- List view فیلتر ندارد (نمایش تمام servers)
- مرتب‌سازی بر اساس `name`

---

## الگوهای مشترک

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کند
2. **Auto Field Setting**: `created_by` و `edited_by` به صورت خودکار تنظیم می‌شوند
3. **Error Handling**: خطاها با messages نمایش داده می‌شوند
4. **Context Management**: `active_module` در تمام views اضافه می‌شود

---

## استفاده در پروژه

این views در URLs ماژول shared ثبت شده‌اند:

```python
# shared/urls.py
path('smtp-servers/', SMTPServerListView.as_view(), name='smtp_servers'),
path('smtp-servers/create/', SMTPServerCreateView.as_view(), name='smtp_server_create'),
path('smtp-servers/<int:pk>/edit/', SMTPServerUpdateView.as_view(), name='smtp_server_edit'),
path('smtp-servers/<int:pk>/delete/', SMTPServerDeleteView.as_view(), name='smtp_server_delete'),
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `SMTPServer` model استفاده می‌کند

### Shared Forms
- از `SMTPServerForm` برای create و update استفاده می‌کند

### Shared Utils
- SMTP servers در `shared.utils.email` برای ارسال email استفاده می‌شوند


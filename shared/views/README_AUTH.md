# shared/views/auth.py - Authentication Views (Complete Documentation)

**هدف**: Views برای authentication و session management در ماژول shared

این فایل شامل **3 function-based view**:
- `set_active_company`: تنظیم شرکت فعال در session
- `custom_login`: صفحه login سفارشی
- `mark_notification_read`: علامت‌گذاری notification به عنوان خوانده شده

---

## وابستگی‌ها

- `shared.models`: `UserCompanyAccess`
- `django.contrib.auth`: `authenticate`, `login as auth_login`
- `django.contrib.auth.decorators`: `login_required`
- `django.http`: `HttpResponseRedirect`, `HttpRequest`
- `django.shortcuts`: `render`, `redirect`
- `django.utils.translation`: `get_language`
- `django.views.decorators.http`: `require_POST`
- `typing`: `Optional`

---

## set_active_company

**Type**: Function-based view

**Decorators**: `@login_required`, `@require_POST`

**Method**: `POST`

**توضیح**: تنظیم شرکت فعال برای session کاربر فعلی.

**Request POST Data**:
- `company_id`: شناسه شرکت (required)
- `next`: URL برای redirect بعد از تنظیم (optional)

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `next` یا `/`

**منطق**:
1. دریافت `company_id` از POST
2. Parse کردن به integer
3. بررسی دسترسی کاربر به company:
   - بررسی `UserCompanyAccess` برای user و company
   - فیلتر: `is_enabled=1`
4. اگر دسترسی داشته باشد:
   - تنظیم `request.session['active_company_id'] = company_id_int`
5. Redirect به `next` (از POST) یا `/`

**Error Handling**:
- اگر `company_id` معتبر نباشد (ValueError, TypeError): ignore
- اگر کاربر دسترسی نداشته باشد: ignore (company تنظیم نمی‌شود)

**نکات مهم**:
- فقط companies که کاربر به آن‌ها دسترسی دارد قابل انتخاب هستند
- از `UserCompanyAccess` برای بررسی دسترسی استفاده می‌شود

**URL**: `/shared/set-active-company/`

---

## custom_login

**Type**: Function-based view

**Method**: `GET`, `POST`

**Template**: `login.html`

**توضیح**: صفحه login سفارشی با UI زیبا.

**Request Data**:
- `username`: نام کاربری (POST)
- `password`: رمز عبور (POST)
- `next`: URL برای redirect بعد از login (GET یا POST)

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به dashboard یا `next` (در صورت موفقیت)
- `HttpResponse`: render login template (در صورت خطا یا GET)

**منطق**:

#### GET Request:
1. اگر user authenticated است: redirect به `ui:dashboard`
2. دریافت `next` از GET
3. دریافت `current_lang` از `get_language()`
4. Render `login.html` با `next` و `LANGUAGE_CODE`

#### POST Request:
1. اگر user authenticated است: redirect به `ui:dashboard`
2. دریافت `username` و `password` از POST
3. Authenticate کردن user با `authenticate(request, username=username, password=password)`
4. اگر user معتبر باشد:
   - Login کردن user با `auth_login(request, user)`
   - دریافت `next` از POST یا GET یا default به `ui:dashboard`
   - Redirect به `next`
5. اگر user معتبر نباشد:
   - Render `login.html` با error flag و `next`

**Context Variables** (برای template):
- `form`: dictionary با `errors` flag (در صورت خطا)
- `next`: URL برای redirect
- `LANGUAGE_CODE`: کد زبان فعلی

**نکات مهم**:
- از Django's built-in `authenticate` و `login` استفاده می‌کند
- اگر user قبلاً authenticated باشد، redirect می‌شود
- Error handling برای invalid credentials

**URL**: `/login/`

---

## mark_notification_read

**Type**: Function-based view

**Decorators**: `@login_required`, `@require_POST`

**Method**: `POST`

**توضیح**: علامت‌گذاری notification به عنوان خوانده شده در session.

**Request POST Data**:
- `notification_key`: کلید notification (required)
- `next`: URL برای redirect بعد از علامت‌گذاری (optional)

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `next` یا `/`

**منطق**:
1. دریافت `notification_key` از POST
2. اگر `notification_key` موجود باشد:
   - دریافت `read_notifications` از session (default: empty set)
   - تبدیل به set (اگر list باشد)
   - اضافه کردن `notification_key` به set
   - ذخیره در session به عنوان list
   - تنظیم `request.session.modified = True`
3. Redirect به `next` (از POST) یا `/`

**Session Structure**:
- `read_notifications`: list of notification keys

**نکات مهم**:
- Notifications در session ذخیره می‌شوند (not in database)
- از set برای جلوگیری از duplicates استفاده می‌شود
- در session به عنوان list ذخیره می‌شود

**URL**: `/shared/mark-notification-read/`

---

## نکات مهم

### 1. Session Management
- `active_company_id` در session ذخیره می‌شود
- `read_notifications` در session ذخیره می‌شوند
- Session-based (not database)

### 2. Access Control
- `set_active_company` فقط companies که کاربر به آن‌ها دسترسی دارد را می‌پذیرد
- از `UserCompanyAccess` برای بررسی دسترسی استفاده می‌شود

### 3. Authentication
- از Django's built-in authentication استفاده می‌کند
- Custom login page با UI زیبا

### 4. Notification Management
- Notifications در session ذخیره می‌شوند
- از set برای جلوگیری از duplicates استفاده می‌شود

### 5. Redirect Handling
- از `next` parameter برای redirect بعد از action استفاده می‌شود
- Fallback به default URLs (`/` یا `ui:dashboard`)

---

## الگوهای مشترک

1. **Login Required**: از `@login_required` برای protected views استفاده می‌شود
2. **POST Only**: از `@require_POST` برای POST-only views استفاده می‌شود
3. **Error Handling**: خطاها به صورت graceful handle می‌شوند
4. **Redirect Handling**: از `next` parameter برای redirect استفاده می‌شود

---

## استفاده در پروژه

این views در URLs ماژول shared ثبت شده‌اند:

```python
# shared/urls.py
path('set-active-company/', set_active_company, name='set_active_company'),
path('mark-notification-read/', mark_notification_read, name='mark_notification_read'),

# Main urls.py
path('login/', custom_login, name='login'),
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `UserCompanyAccess` برای بررسی دسترسی به company استفاده می‌کند

### Django Auth
- از Django's built-in `authenticate` و `login` استفاده می‌کند

### UI Module
- Redirect به `ui:dashboard` بعد از login


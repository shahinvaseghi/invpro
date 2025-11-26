# ticketing/views/debug.py - Debug Views (Complete Documentation)

**هدف**: Debug views برای ماژول ticketing

این فایل شامل:
- `debug_log_view`: Function-based view برای دریافت debug logs از browser

---

## وابستگی‌ها

- `django.http.JsonResponse`
- `django.views.decorators.csrf.csrf_exempt`
- `django.views.decorators.http.require_http_methods`
- `json`
- `logging`

---

## debug_log_view

### `debug_log_view(request) -> JsonResponse`

**توضیح**: دریافت debug logs از browser و نمایش در server console

**Type**: Function-based view

**Decorators**:
- `@csrf_exempt`: غیرفعال کردن CSRF protection
- `@require_http_methods(["POST"])`: فقط POST method

**Method**: `POST`

**Request Body (JSON)**:
- `level` (str): سطح log (default: `'LOG'`)
- `message` (str): پیام log
- `data` (dict): داده‌های اضافی
- `url` (str): URL صفحه
- `timestamp` (str): زمان log

**مقدار بازگشتی**:
- `JsonResponse`: `{'status': 'ok'}` در صورت موفقیت، `{'status': 'error', 'message': str(e)}` در صورت خطا

**منطق**:
1. Parse کردن JSON از `request.body`
2. ساخت log message با format: `[{timestamp}] [{level}] {message} | URL: {url} | Data: {json_data}`
3. Print کردن به console (terminal)
4. Log کردن به Django logger (error یا info بر اساس level)
5. بازگشت `JsonResponse` با status

**نکات مهم**:
- CSRF exempt است (برای debug)
- فقط POST method
- Logs را هم در console و هم در Django logger ذخیره می‌کند

**URL**: `/ticketing/debug/log/`

---

## استفاده در پروژه

### در JavaScript
```javascript
fetch('/ticketing/debug/log/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        level: 'ERROR',
        message: 'Something went wrong',
        data: { field: 'value' },
        url: window.location.href,
        timestamp: new Date().toISOString()
    })
});
```

---

## نکات مهم

1. **CSRF Exempt**: برای debug استفاده می‌شود
2. **Console Logging**: Logs در terminal نمایش داده می‌شوند
3. **Django Logger**: Logs در Django logger هم ذخیره می‌شوند


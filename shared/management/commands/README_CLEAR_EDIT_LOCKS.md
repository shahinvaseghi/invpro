# shared/management/commands/clear_edit_locks.py - Clear Edit Locks Command

**هدف**: Management command برای پاک کردن edit locks قدیمی (stale) یا تمام edit locks

این command برای پاک کردن edit locks که به دلیل crash، timeout، یا مشکلات دیگر باقی مانده‌اند استفاده می‌شود.

---

## استفاده

```bash
# پاک کردن edit locks قدیمی‌تر از 5 دقیقه (default)
python manage.py clear_edit_locks

# پاک کردن edit locks قدیمی‌تر از 10 دقیقه
python manage.py clear_edit_locks --timeout 10

# پاک کردن تمام edit locks (بدون توجه به زمان)
python manage.py clear_edit_locks --all
```

---

## کلاس `Command`

**Base Class**: `django.core.management.base.BaseCommand`

**Help Text**: `'Clear all stale edit locks (older than 5 minutes)'`

---

## متدها

### `add_arguments(self, parser)`

**توضیح**: اضافه کردن command-line arguments

**Arguments**:
- `--all` (flag): پاک کردن تمام edit locks (نه فقط stale ones)
- `--timeout` (int, default=5): Timeout به دقیقه (default: 5 دقیقه)

---

### `handle(self, *args, **options)`

**توضیح**: منطق اصلی command

**پارامترهای ورودی**:
- `*args`: positional arguments
- `**options`: keyword arguments (شامل `all` و `timeout`)

**منطق**:

1. **دریافت options**:
   - `clear_all = options['all']` (boolean)
   - `timeout_minutes = options['timeout']` (int, default=5)

2. **تعیین timeout threshold**:
   - اگر `clear_all` True باشد:
     - `timeout_threshold = timezone.now()` (همه locks)
     - نمایش warning: "Clearing ALL edit locks..."
   - در غیر این صورت:
     - `timeout_threshold = timezone.now() - timedelta(minutes=timeout_minutes)`
     - نمایش message: "Clearing edit locks older than {timeout_minutes} minutes..."

3. **مقداردهی اولیه**:
   - `total_cleaned = 0` (شمارنده کل locks پاک شده)

4. **یافتن و پاک کردن edit locks**:
   - دریافت تمام app configs: `apps.get_app_configs()`
   - برای هر app:
     - دریافت تمام models: `app_config.get_models()`
     - برای هر model:
       - **بررسی EditableModel mixin**:
         - اگر model دارای `editing_by` و `editing_started_at` fields باشد (نشان‌دهنده EditableModel mixin):
           - **اگر `clear_all` True باشد**:
             - Query: `model.objects.filter(editing_by__isnull=False)`
             - Update: `editing_by=None`, `editing_started_at=None`, `editing_session_key=''`
           - **در غیر این صورت** (فقط stale locks):
             - Query: `model.objects.filter(editing_by__isnull=False, editing_started_at__isnull=False, editing_started_at__lt=timeout_threshold)`
             - Update: `editing_by=None`, `editing_started_at=None`, `editing_session_key=''`
           - اگر `count > 0`:
             - `total_cleaned += count`
             - نمایش success message: "Cleared {count} edit locks from {model.__name__}"
           - **Error handling**: اگر exception رخ دهد:
             - نمایش error message: "Error clearing locks for {model.__name__}: {e}"

5. **نمایش نتیجه**:
   - اگر `total_cleaned > 0`:
     - نمایش success: "Total: {total_cleaned} edit locks cleared."
   - در غیر این صورت:
     - نمایش success: "No edit locks to clear."

---

## Edit Lock Fields

این command فیلدهای زیر را در models با `EditableModel` mixin پاک می‌کند:
- `editing_by`: کاربری که در حال ویرایش است (None می‌شود)
- `editing_started_at`: زمان شروع ویرایش (None می‌شود)
- `editing_session_key`: session key ویرایش (empty string می‌شود)

---

## EditableModel Detection

Command به صورت خودکار models با `EditableModel` mixin را تشخیص می‌دهد با بررسی وجود fields:
- `editing_by`
- `editing_started_at`

---

## نکات مهم

1. **Stale Locks**: به صورت پیش‌فرض فقط locks قدیمی‌تر از 5 دقیقه پاک می‌شوند
2. **All Locks**: با flag `--all` تمام locks پاک می‌شوند (بدون توجه به زمان)
3. **Timeout Customization**: می‌توان timeout را با `--timeout` تغییر داد
4. **Automatic Detection**: به صورت خودکار تمام models با EditableModel mixin را پیدا می‌کند
5. **Error Handling**: اگر پاک کردن برای یک model ناموفق باشد، error نمایش داده می‌شود و با models دیگر ادامه می‌دهد
6. **Bulk Update**: از `update()` استفاده می‌کند (efficient برای تعداد زیاد)

---

## مثال خروجی

```
Clearing edit locks older than 5 minutes...
Cleared 3 edit locks from ReceiptPermanent
Cleared 1 edit locks from IssueConsumption
Cleared 2 edit locks from StocktakingRecord

Total: 6 edit locks cleared.
```

یا:

```
⚠️  Clearing ALL edit locks...
Cleared 10 edit locks from ReceiptPermanent
Cleared 5 edit locks from IssueConsumption
Cleared 8 edit locks from StocktakingRecord

Total: 23 edit locks cleared.
```

---

## وابستگی‌ها

- `django.core.management.base.BaseCommand`
- `django.utils.timezone`
- `datetime.timedelta`
- `django.apps.apps`

---

## استفاده در Production

این command معمولاً برای:
- پاک کردن edit locks قدیمی که به دلیل crash یا timeout باقی مانده‌اند
- Reset کردن locks بعد از مشکلات سیستم
- Maintenance دوره‌ای

استفاده می‌شود.

**نکته**: در production، معمولاً فقط stale locks پاک می‌شوند (بدون `--all` flag).

---

## Cron Job Example

می‌توان این command را به صورت دوره‌ای اجرا کرد:

```bash
# هر 30 دقیقه یک بار
*/30 * * * * cd /path/to/project && python manage.py clear_edit_locks --timeout 5
```

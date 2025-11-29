# shared/management/commands/clear_all_data.py - Clear All Data Command

**هدف**: Management command برای حذف تمام داده‌ها به جز Users، Groups، Companies، Access Levels، Company Units، و User Company Access

این command برای پاک کردن محیط development و testing استفاده می‌شود و داده‌های اصلی سیستم (کاربران، شرکت‌ها، دسترسی‌ها) را حفظ می‌کند.

---

## استفاده

```bash
python manage.py clear_all_data --confirm
```

**نکته مهم**: بدون flag `--confirm`، command فقط warning نمایش می‌دهد و هیچ داده‌ای حذف نمی‌کند.

---

## کلاس `Command`

**Base Class**: `django.core.management.base.BaseCommand`

**Help Text**: `'Delete all data except Users, Groups, Companies, Access Levels, Company Units, and User Company Access'`

---

## متدها

### `add_arguments(self, parser)`

**توضیح**: اضافه کردن command-line arguments

**Arguments**:
- `--confirm` (flag): تایید حذف (required برای حذف واقعی)

---

### `handle(self, *args, **options)`

**توضیح**: منطق اصلی command

**پارامترهای ورودی**:
- `*args`: positional arguments
- `**options`: keyword arguments (شامل `confirm`)

**منطق**:

1. **بررسی confirm flag**:
   - اگر `options['confirm']` موجود نیست:
     - نمایش warning message با لیست داده‌های حفظ شده
     - نمایش دستورالعمل برای اجرا با `--confirm`
     - بازگشت (بدون حذف)

2. **تعریف models برای حفظ**:
   ```python
   keep_models = {
       User,
       Group,
       Company,
       CompanyUnit,
       AccessLevel,
       AccessLevelPermission,
       UserCompanyAccess,
   }
   ```

3. **یافتن تمام models برای حذف**:
   - دریافت تمام app configs: `apps.get_app_configs()`
   - Skip کردن Django built-in apps (`django.*`, `admin.*`)
   - برای هر app:
     - دریافت تمام models: `app_config.get_models()`
     - Skip کردن abstract models (`model._meta.abstract`)
     - Skip کردن proxy models (`model._meta.proxy`)
     - Skip کردن models در `keep_models`
     - اضافه کردن به `all_models` list

4. **نمایش warning**:
   - نمایش تعداد models که حذف خواهند شد

5. **حذف داده‌ها** (در `transaction.atomic()`):
   - **PostgreSQL constraint deferral**:
     - `cursor.execute("SET CONSTRAINTS ALL DEFERRED")` برای defer کردن foreign key constraints
   - **حذف با multiple passes** (برای handle کردن dependencies):
     - `models_to_delete = all_models.copy()`
     - `max_iterations = 10` (برای جلوگیری از infinite loop)
     - **برای هر iteration**:
       - برای هر model در `models_to_delete`:
         - **تلاش حذف با ORM**:
           - `count = model.objects.count()`
           - اگر `count > 0`:
             - `model.objects.all().delete()`
             - اضافه کردن به `deleted_models`
             - نمایش success message
         - **اگر exception رخ دهد** (foreign key constraint):
           - اضافه کردن به `remaining_models`
           - **Fallback: TRUNCATE CASCADE با SQL**:
             - `table_name = model._meta.db_table`
             - `cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')`
             - اگر موفق بود: حذف از `remaining_models`
     - **اگر هنوز models باقی مانده** و `iteration >= 3`:
       - برای هر model باقی مانده:
         - تلاش `TRUNCATE TABLE ... CASCADE` با SQL
         - اگر موفق بود: حذف از `models_to_delete`
     - `models_to_delete = remaining_models` (برای iteration بعدی)

6. **نمایش نتیجه**:
   - نمایش تعداد کل records حذف شده
   - نمایش تعداد models حذف شده
   - نمایش لیست داده‌های حفظ شده

---

## Models حفظ شده

این models **حذف نمی‌شوند**:
- `User` (کاربران)
- `Group` (گروه‌های کاربری)
- `Company` (شرکت‌ها)
- `CompanyUnit` (واحدهای سازمانی)
- `AccessLevel` (سطح‌های دسترسی)
- `AccessLevelPermission` (مجوزهای سطح دسترسی)
- `UserCompanyAccess` (دسترسی کاربران به شرکت‌ها)

---

## نکات مهم

1. **Dangerous Command**: این command تمام داده‌ها را حذف می‌کند (به جز models حفظ شده)
2. **Transaction**: تمام عملیات در یک transaction انجام می‌شود
3. **Constraint Handling**: از `SET CONSTRAINTS ALL DEFERRED` برای PostgreSQL استفاده می‌کند
4. **Multiple Passes**: برای handle کردن foreign key dependencies، چندین pass انجام می‌شود
5. **SQL Fallback**: اگر ORM delete ناموفق باشد، از `TRUNCATE CASCADE` با SQL استفاده می‌کند
6. **Max Iterations**: حداکثر 10 iteration برای جلوگیری از infinite loop
7. **Abstract/Proxy Models**: Abstract و proxy models skip می‌شوند
8. **Django Apps**: Django built-in apps skip می‌شوند

---

## Error Handling

- **Exception در ORM delete**: Fallback به SQL `TRUNCATE CASCADE`
- **Exception در SQL**: Model در `remaining_models` باقی می‌ماند برای iteration بعدی
- **Infinite Loop Prevention**: `max_iterations = 10` برای محدود کردن iterations

---

## مثال خروجی

```
⚠️  WARNING: About to delete data from 45 models!

✓ Deleted 120 records from inventory.Item
✓ Deleted 50 records from inventory.Warehouse
✓ Deleted 200 records from inventory.ReceiptPermanent
...

✅ Successfully deleted 5000 total records from 45 models.
Preserved: Users, Groups, Companies, Access Levels, Company Units, User Company Access
```

---

## وابستگی‌ها

- `django.core.management.base.BaseCommand`
- `django.apps.apps`
- `django.contrib.auth.models.Group`
- `django.db.transaction`
- `django.db.connection`
- `shared.models`: `User`, `Company`, `CompanyUnit`, `AccessLevel`, `AccessLevelPermission`, `UserCompanyAccess`

---

## استفاده در Development

این command معمولاً برای:
- پاک کردن محیط development
- Reset کردن database برای testing
- حذف داده‌های test

استفاده می‌شود.

**هشدار**: هرگز در production استفاده نکنید!

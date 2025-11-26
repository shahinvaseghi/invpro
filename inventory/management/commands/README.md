# inventory/management/commands/ - Management Commands

این پوشه شامل دستورات مدیریتی (management commands) Django برای ماژول inventory است.

## فایل‌ها

### cleanup_test_receipts.py

**هدف**: پاک کردن داده‌های تست یا نمایش اطلاعات رسیدها برای debugging

---

## Command Class

### `Command(BaseCommand)`

**نام دستور**: `cleanup_test_receipts`

**توضیح**: این دستور برای پاک کردن تمام رسیدهای تست و ردیف‌های آن‌ها یا نمایش اطلاعات رسیدها استفاده می‌شود.

---

## Methods

### `add_arguments(parser)`

**توضیح**: آرگومان‌های command line را تعریف می‌کند.

**پارامترهای ورودی**:
- `parser`: ArgumentParser Django

**آرگومان‌ها**:
- `--show` (flag): به جای حذف، اطلاعات رسیدها را نمایش می‌دهد

**مثال استفاده**:
```bash
# حذف تمام رسیدهای تست
python manage.py cleanup_test_receipts

# نمایش اطلاعات رسیدها
python manage.py cleanup_test_receipts --show
```

---

### `handle(*args, **options)`

**توضیح**: منطق اصلی command را اجرا می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های اضافی
- `**options`: گزینه‌های command line

**منطق**:
- اگر `options['show']` برابر `True` باشد، `_show_data()` را فراخوانی می‌کند
- در غیر این صورت، `_delete_all()` را فراخوانی می‌کند

---

### `_show_data()`

**توضیح**: اطلاعات رسیدها را در console نمایش می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد (خروجی به stdout می‌رود)

**خروجی**:
1. **جدول ReceiptPermanent**: نمایش 20 رسید اخیر با جزئیات:
   - ID
   - Code
   - Date
   - Company ID
   - Created By
   - Lines Count

2. **جدول ReceiptPermanentLine**: نمایش 30 ردیف اخیر با جزئیات:
   - ID
   - Receipt ID و Code
   - Item ID و Name
   - Quantity و Unit
   - Entered Quantity و Entered Unit
   - Warehouse ID

3. **رسیدهای اخیر با ردیف‌ها**: نمایش 5 رسید اخیر به همراه تمام ردیف‌های آن‌ها

**مثال خروجی**:
```
================================================================================
RECEIPTPERMANENT TABLE
================================================================================
Total receipts: 150

ID: 123
  Code: PRM-202511-000001
  Date: 2025-11-15
  Company ID: 1
  Created By: 5
  Lines Count: 3

================================================================================
RECEIPTPERMANENTLINE TABLE
================================================================================
Total lines: 450

ID: 456
  Receipt ID: 123
  Receipt Code: PRM-202511-000001
  Item ID: 789
  Item Name: Sample Item
  Quantity: 10.000000
  Unit: EA
  Entered Quantity: 10.000000
  Entered Unit: EA
  Warehouse ID: 1
```

---

### `_delete_all()`

**توضیح**: تمام رسیدهای تست و ردیف‌های آن‌ها را حذف می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد (پیام موفقیت به stdout می‌رود)

**منطق**:
1. تعداد ردیف‌های `ReceiptPermanentLine` را می‌شمارد
2. تمام ردیف‌ها را حذف می‌کند
3. تعداد رسیدهای `ReceiptPermanent` را می‌شمارد
4. تمام رسیدها را حذف می‌کند
5. پیام موفقیت با تعداد حذف شده نمایش می‌دهد

**مثال خروجی**:
```
Successfully deleted 150 receipts and 450 receipt lines.
```

**هشدار**: این دستور تمام داده‌های رسید را به صورت دائمی حذف می‌کند! در production با احتیاط استفاده کنید.

---

## استفاده در پروژه

### Development/Testing

```bash
# نمایش اطلاعات برای debugging
python manage.py cleanup_test_receipts --show

# پاک کردن داده‌های تست بعد از تست
python manage.py cleanup_test_receipts
```

### Production

⚠️ **هشدار**: این دستور نباید در production استفاده شود مگر در موارد خاص (مثل migration یا cleanup دستی).

---

## وابستگی‌ها

- `django.core.management.base`: `BaseCommand`
- `inventory.models`: `ReceiptPermanent`, `ReceiptPermanentLine`

---

## نکات مهم

1. **Data Loss**: دستور delete تمام داده‌ها را به صورت دائمی حذف می‌کند
2. **CASCADE**: حذف رسیدها به صورت خودکار ردیف‌ها را حذف می‌کند (CASCADE)
3. **Explicit Deletion**: برای اطمینان، ابتدا ردیف‌ها و سپس رسیدها حذف می‌شوند
4. **Show Mode**: برای debugging و بررسی ساختار داده مفید است

---

## بهبودهای آینده

- اضافه کردن فیلتر برای حذف فقط رسیدهای یک شرکت خاص
- اضافه کردن confirmation prompt قبل از حذف
- اضافه کردن backup قبل از حذف
- اضافه کردن فیلتر تاریخ برای حذف فقط رسیدهای قدیمی


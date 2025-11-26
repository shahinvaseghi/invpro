# inventory/management/commands/cleanup_test_receipts.py - Cleanup Test Receipts Command

**هدف**: Management command برای حذف یا نمایش داده‌های test receipts

این command برای development و testing استفاده می‌شود تا تمام receipts و receipt lines را از دیتابیس حذف کند یا اطلاعات آن‌ها را نمایش دهد.

---

## استفاده

### حذف تمام Receipts

```bash
python manage.py cleanup_test_receipts
```

این command تمام `ReceiptPermanent` و `ReceiptPermanentLine` records را از دیتابیس حذف می‌کند.

### نمایش اطلاعات Receipts

```bash
python manage.py cleanup_test_receipts --show
```

این command اطلاعات receipts و receipt lines را در console نمایش می‌دهد.

---

## کلاس Command

### `Command(BaseCommand)`

**هدف**: Django management command برای cleanup test receipts

**Methods**:

#### `add_arguments(parser)`

**هدف**: اضافه کردن command-line arguments

**پارامترها**:
- `parser`: ArgumentParser object

**Arguments**:
- `--show` (flag): اگر set شود، اطلاعات را نمایش می‌دهد به جای حذف

**مثال**:
```python
parser.add_argument(
    '--show',
    action='store_true',
    help='Show receipt data instead of deleting',
)
```

---

#### `handle(*args, **options)`

**هدف**: اجرای اصلی command

**پارامترها**:
- `*args`: Positional arguments
- `**options`: Keyword arguments (از `add_arguments`)

**منطق کار**:
1. اگر `options['show']` برابر `True` باشد:
   - `_show_data()` را فراخوانی می‌کند
2. در غیر این صورت:
   - `_delete_all()` را فراخوانی می‌کند

---

#### `_show_data()`

**هدف**: نمایش اطلاعات receipts و receipt lines در console

**منطق کار**:
1. **ReceiptPermanent Table**:
   - 20 receipt اخیر را نمایش می‌دهد
   - برای هر receipt: ID, Code, Date, Company ID, Created By, Lines Count
   - تعداد کل receipts را نمایش می‌دهد

2. **ReceiptPermanentLine Table**:
   - 30 receipt line اخیر را نمایش می‌دهد
   - برای هر line: ID, Receipt ID, Receipt Code, Item ID, Item Name, Quantity, Unit, Entered Quantity, Entered Unit, Warehouse ID
   - تعداد کل receipt lines را نمایش می‌دهد

3. **Recent Receipts with Lines**:
   - 5 receipt اخیر را با تمام lines آن‌ها نمایش می‌دهد
   - اگر receipt خطی نداشته باشد، warning نمایش می‌دهد

**خروجی مثال**:
```
================================================================================
RECEIPTPERMANENT TABLE
================================================================================
Total receipts: 15

ID: 10
  Code: REC-20241126-000001
  Date: 2024-11-26
  Company ID: 1
  Created By: 1
  Lines Count: 3

...

================================================================================
RECEIPTPERMANENTLINE TABLE
================================================================================
Total lines: 45

ID: 30
  Receipt ID: 10
  Receipt Code: REC-20241126-000001
  Item ID: 5
  Item Name: Item Name
  Quantity: 10.000
  Unit: EA
  Entered Quantity: 10.000
  Entered Unit: EA
  Warehouse ID: 1

...
```

---

#### `_delete_all()`

**هدف**: حذف تمام receipts و receipt lines از دیتابیس

**منطق کار**:
1. تعداد receipt lines را می‌شمارد
2. تمام `ReceiptPermanentLine` records را حذف می‌کند
3. تعداد receipts را می‌شمارد
4. تمام `ReceiptPermanent` records را حذف می‌کند
5. پیام موفقیت را نمایش می‌دهد با تعداد records حذف شده

**خروجی مثال**:
```
Successfully deleted 15 receipts and 45 receipt lines.
```

**نکات**:
- ابتدا receipt lines حذف می‌شوند (اگرچه CASCADE این کار را انجام می‌دهد، اما explicit بهتر است)
- سپس receipts حذف می‌شوند
- از `self.style.SUCCESS()` برای رنگ سبز استفاده می‌شود

---

## وابستگی‌ها

- `django.core.management.base.BaseCommand`: Base class برای management commands
- `inventory.models.ReceiptPermanent`: مدل receipt
- `inventory.models.ReceiptPermanentLine`: مدل receipt line

---

## استفاده در پروژه

### در Development

```bash
# حذف تمام test receipts
python manage.py cleanup_test_receipts

# نمایش اطلاعات قبل از حذف
python manage.py cleanup_test_receipts --show
```

### در Testing

```python
# در test setup
from django.core.management import call_command

def setUp(self):
    # حذف receipts قبل از test
    call_command('cleanup_test_receipts')
    
    # ... create test data ...
```

---

## نکات مهم

1. **Dangerous Operation**: این command تمام receipts را حذف می‌کند - فقط در development/testing استفاده شود
2. **No Confirmation**: این command confirmation نمی‌خواهد - مستقیماً حذف می‌کند
3. **CASCADE Handling**: اگرچه CASCADE این کار را انجام می‌دهد، اما explicit deletion بهتر است
4. **Output Formatting**: از `self.stdout.write()` و `self.style.SUCCESS()` برای formatting استفاده می‌شود
5. **Limited Display**: در `--show` mode، فقط 20 receipt و 30 line اخیر نمایش داده می‌شوند

---

## مثال‌های کامل

### حذف و نمایش

```bash
# 1. نمایش اطلاعات
python manage.py cleanup_test_receipts --show

# 2. حذف
python manage.py cleanup_test_receipts
```

### در Test Script

```python
from django.core.management import call_command
from django.test import TestCase

class ReceiptTestCase(TestCase):
    def setUp(self):
        # حذف receipts قبل از test
        call_command('cleanup_test_receipts')
        
    def test_create_receipt(self):
        # ... test code ...
        pass
```

---

## Security Considerations

1. **Production Warning**: این command نباید در production استفاده شود
2. **Backup**: قبل از حذف، backup بگیرید
3. **Confirmation**: در آینده می‌توان confirmation اضافه کرد

**پیشنهاد برای آینده**:
```python
def add_arguments(self, parser):
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm deletion (required for deletion)',
    )
```

---

## Extensions

می‌توان این command را برای سایر models نیز extend کرد:

```python
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['receipts', 'issues', 'requests'],
            default='receipts',
            help='Model to cleanup',
        )
```


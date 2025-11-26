# inventory/utils/codes.py - Code Generation Utilities

**هدف**: توابع کمکی برای تولید کدهای متوالی عددی برای مدل‌های مختلف

این فایل شامل یک تابع اصلی برای تولید کدهای متوالی است که در تمام ماژول‌های پروژه استفاده می‌شود.

---

## توابع

### `generate_sequential_code(model, *, company_id, field, width, extra_filters) -> str`

**هدف**: تولید کد متوالی عددی برای یک مدل خاص

**پارامترهای ورودی**:
- `model` (Django Model class): مدلی که می‌خواهیم کد برایش تولید کنیم
- `company_id` (Optional[int]): شناسه شرکت (برای scoping)
- `field` (str, default="public_code"): نام فیلدی که کد در آن ذخیره می‌شود
- `width` (int, default=3): عرض کد (تعداد ارقام، با صفر پر می‌شود)
- `extra_filters` (Optional[Dict], default=None): فیلترهای اضافی برای scoping (مثل category, warehouse)

**مقدار بازگشتی**:
- `str`: کد متوالی تولید شده (مثل "001", "002", ...)

**منطق کار**:
1. ابتدا فیلترها را آماده می‌کند:
   - اگر `company_id` داده شده و مدل فیلد `company` دارد، `company_id` به فیلترها اضافه می‌شود
   - فیلترهای اضافی (`extra_filters`) نیز اضافه می‌شوند
2. در یک transaction atomic:
   - آخرین کد موجود را پیدا می‌کند (مرتب‌سازی بر اساس `field` به صورت نزولی)
   - اگر کد موجود باشد و عددی باشد، مقدار بعدی را محاسبه می‌کند (last_code + 1)
   - اگر کد موجود نباشد، از 1 شروع می‌کند
3. یک حلقه while برای اطمینان از یکتایی:
   - کد کاندید را با `zfill(width)` تولید می‌کند
   - بررسی می‌کند که آیا این کد قبلاً استفاده شده یا نه
   - اگر استفاده شده باشد، مقدار را افزایش می‌دهد و دوباره بررسی می‌کند
   - تا زمانی که یک کد یکتا پیدا شود

**مثال استفاده**:
```python
from inventory.utils.codes import generate_sequential_code
from inventory.models import Item

# تولید کد برای یک item جدید
code = generate_sequential_code(
    Item,
    company_id=1,
    field="item_code",
    width=6,
)
# نتیجه: "000001", "000002", ...

# تولید کد با فیلتر اضافی (مثل category)
code = generate_sequential_code(
    Item,
    company_id=1,
    field="item_code",
    width=6,
    extra_filters={"category_id": 5},
)
```

**نکات مهم**:
- از `transaction.atomic()` استفاده می‌کند تا از race condition جلوگیری شود
- کدها به صورت عددی و با صفر پر می‌شوند (zero-padded)
- اگر آخرین کد عددی نباشد، از 1 شروع می‌کند
- اگر کد تکراری باشد، به صورت خودکار مقدار بعدی را امتحان می‌کند

**وابستگی‌ها**:
- `django.db.transaction`: برای atomic transactions
- `typing`: برای type hints

---

## استفاده در پروژه

این تابع در تمام ماژول‌های پروژه برای تولید کدهای متوالی استفاده می‌شود:

- **Inventory**: برای تولید `item_code`, `warehouse_code`, `supplier_code`, و غیره
- **Production**: برای تولید کدهای BOM، Process، و غیره
- **Ticketing**: برای تولید کدهای Ticket و Template (با استفاده از نسخه‌های خاص)

**مثال در Model.save()**:
```python
from inventory.utils.codes import generate_sequential_code

class Item(InventoryBaseModel):
    item_code = models.CharField(max_length=16, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = generate_sequential_code(
                Item,
                company_id=self.company_id,
                field="item_code",
                width=6,
            )
        super().save(*args, **kwargs)
```

---

## نکات پیاده‌سازی

1. **Thread Safety**: استفاده از `transaction.atomic()` باعث می‌شود که در محیط‌های multi-threaded نیز درست کار کند
2. **Performance**: Query برای پیدا کردن آخرین کد بهینه است (فقط یک record برمی‌گرداند)
3. **Flexibility**: با `extra_filters` می‌توان کدها را بر اساس معیارهای مختلف scope کرد (مثل category, warehouse)
4. **Error Handling**: اگر کد موجود عددی نباشد، از 1 شروع می‌کند (fail-safe)

---

## تفاوت با `ticketing/utils/codes.py`

این فایل (`inventory/utils/codes.py`) یک تابع عمومی برای تولید کدهای متوالی عددی است.

فایل `ticketing/utils/codes.py` علاوه بر `generate_sequential_code`، دو تابع خاص نیز دارد:
- `generate_template_code()`: برای تولید کدهای template با فرمت `TMP-YYYYMMDD-XXXXXX`
- `generate_ticket_code()`: برای تولید کدهای ticket با فرمت `TKT-YYYYMMDD-XXXXXX`

این توابع خاص از تاریخ در کد استفاده می‌کنند و برای ticketing module طراحی شده‌اند.


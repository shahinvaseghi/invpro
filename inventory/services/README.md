# inventory/services/ - Service Functions

این پوشه شامل توابع سرویس (service functions) برای ماژول inventory است که منطق پیچیده کسب‌وکار را مدیریت می‌کنند.

## فایل‌ها

### serials.py

**هدف**: مدیریت کامل چرخه حیات سریال‌ها (Serial Numbers) برای کالاهای قابل ردیابی

این فایل شامل دو بخش است:
1. **Single-line Serial Management**: برای رسیدها و حواله‌های قدیمی (single-item documents)
2. **Line-based Serial Management**: برای رسیدها و حواله‌های جدید با پشتیبانی multi-line

---

## Exception Classes

### `SerialTrackingError`

**توضیح**: کلاس پایه برای خطاهای مربوط به ردیابی سریال

**مثال استفاده**:
```python
raise SerialTrackingError("خطا در تولید کد سریال")
```

---

### `SerialQuantityMismatch(SerialTrackingError)`

**توضیح**: زمانی که مقدار سند نمی‌تواند به سریال‌های مجزا تبدیل شود (مثلاً مقدار اعشاری برای کالای قابل ردیابی)

**مثال استفاده**:
```python
raise SerialQuantityMismatch("مقدار باید عدد صحیح باشد")
```

---

## Single-Line Serial Management Functions

### `generate_receipt_serials(receipt, user=None) -> int`

**توضیح**: تمام سریال‌های مورد نیاز برای یک رسید را ایجاد می‌کند (برای رسیدهای قدیمی single-item).

**پارامترهای ورودی**:
- `receipt`: شیء رسید (ReceiptTemporary, ReceiptPermanent, یا ReceiptConsignment)
- `user` (Optional[User], default=None): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `int`: تعداد سریال‌های ایجاد شده (0 اگر کالا قابل ردیابی نباشد یا سریال‌ها از قبل وجود داشته باشند)

**مثال استفاده**:
```python
from inventory.services.serials import generate_receipt_serials

created_count = generate_receipt_serials(receipt, user=request.user)
# نتیجه: 10 (اگر 10 سریال ایجاد شده باشد)
```

**نکات مهم**:
- فقط برای کالاهایی با `has_lot_tracking=1` کار می‌کند
- مقدار باید عدد صحیح باشد
- از transaction استفاده می‌کند
- اگر سریال‌ها از قبل وجود داشته باشند، فقط سریال‌های جدید ایجاد می‌کند
- یک رکورد در `ItemSerialHistory` برای هر سریال ایجاد می‌کند

---

### `sync_issue_serials(issue, previous_serial_ids, user=None) -> None`

**توضیح**: سریال‌ها را برای یک حواله رزرو یا آزاد می‌کند (قبل از نهایی‌سازی).

**پارامترهای ورودی**:
- `issue`: شیء حواله (IssuePermanent, IssueConsumption, یا IssueConsignment)
- `previous_serial_ids` (Sequence[int]): لیست ID سریال‌های قبلی
- `user` (Optional[User], default=None): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**: ندارد (`None`)

**مثال استفاده**:
```python
from inventory.services.serials import sync_issue_serials

# در view، قبل از ذخیره
previous_ids = list(issue.serials.values_list("id", flat=True))
# ... تغییرات در issue.serials
sync_issue_serials(issue, previous_ids, user=request.user)
```

**نکات مهم**:
- سریال‌های اضافه شده را رزرو می‌کند (RESERVED)
- سریال‌های حذف شده را آزاد می‌کند (AVAILABLE)
- فقط برای کالاهایی با `has_lot_tracking=1` کار می‌کند

---

### `finalize_issue_serials(issue, user=None) -> None`

**توضیح**: سریال‌ها را زمانی که سند حواله قفل می‌شود به‌روزرسانی می‌کند.

**پارامترهای ورودی**:
- `issue`: شیء حواله (IssuePermanent, IssueConsumption, یا IssueConsignment)
- `user` (Optional[User], default=None): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**: ندارد (`None`)

**مثال استفاده**:
```python
from inventory.services.serials import finalize_issue_serials

# در lock view
finalize_issue_serials(issue, user=request.user)
```

**نکات مهم**:
- وضعیت نهایی را بر اساس نوع حواله تعیین می‌کند:
  - `IssueConsumption` → `CONSUMED`
  - سایر حواله‌ها → `ISSUED`
- یک رکورد در `ItemSerialHistory` برای هر سریال ایجاد می‌کند

---

### `_reserve_serials(serial_ids, issue, user=None) -> None` (Private)

**توضیح**: سریال‌های مشخص شده را برای یک حواله رزرو می‌کند.

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `issue`: شیء حواله
- `user` (Optional[User], default=None): کاربر

**مقدار بازگشتی**: ندارد

**نکات مهم**: این تابع private است و نباید مستقیماً فراخوانی شود. از `sync_issue_serials` استفاده کنید.

---

### `_release_serials(serial_ids, issue, user=None) -> None` (Private)

**توضیح**: سریال‌های مشخص شده را از رزرو آزاد می‌کند.

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `issue`: شیء حواله
- `user` (Optional[User], default=None): کاربر

**مقدار بازگشتی**: ندارد

**نکات مهم**: این تابع private است و نباید مستقیماً فراخوانی شود. از `sync_issue_serials` استفاده کنید.

---

## Line-based Serial Management Functions

### `generate_receipt_line_serials(receipt_line, user=None) -> int`

**توضیح**: تمام سریال‌های مورد نیاز برای یک ردیف رسید را ایجاد می‌کند (برای رسیدهای جدید multi-line).

**پارامترهای ورودی**:
- `receipt_line`: شیء ردیف رسید (ReceiptPermanentLine, ReceiptConsignmentLine)
- `user` (Optional[User], default=None): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `int`: تعداد سریال‌های ایجاد شده

**مثال استفاده**:
```python
from inventory.services.serials import generate_receipt_line_serials

# برای هر ردیف رسید
for line in receipt.lines.all():
    if line.item and line.item.has_lot_tracking == 1:
        created = generate_receipt_line_serials(line, user=request.user)
```

**نکات مهم**:
- مشابه `generate_receipt_serials` اما برای ردیف‌ها
- از `receipt_line_reference` برای ردیابی سریال‌ها استفاده می‌کند
- کد سریال به فرمت `{document_code}-L{line_id}-{sequence}` است

---

### `sync_issue_line_serials(line, previous_serial_ids, user=None) -> None`

**توضیح**: سریال‌ها را برای یک ردیف حواله رزرو یا آزاد می‌کند (قبل از نهایی‌سازی).

**پارامترهای ورودی**:
- `line`: شیء ردیف حواله (IssuePermanentLine, IssueConsumptionLine, IssueConsignmentLine)
- `previous_serial_ids` (Sequence[int]): لیست ID سریال‌های قبلی
- `user` (Optional[User], default=None): کاربر

**مقدار بازگشتی**: ندارد

**مثال استفاده**:
```python
from inventory.services.serials import sync_issue_line_serials

# در view، قبل از ذخیره
previous_ids = list(line.serials.values_list("id", flat=True))
# ... تغییرات در line.serials
sync_issue_line_serials(line, previous_ids, user=request.user)
```

---

### `finalize_issue_line_serials(line, user=None) -> None`

**توضیح**: سریال‌ها را زمانی که سند حواله قفل می‌شود به‌روزرسانی می‌کند (برای ردیف‌ها).

**پارامترهای ورودی**:
- `line`: شیء ردیف حواله
- `user` (Optional[User], default=None): کاربر

**مقدار بازگشتی**: ندارد

**مثال استفاده**:
```python
from inventory.services.serials import finalize_issue_line_serials

# در lock view، برای هر ردیف
for line in issue.lines.all():
    if line.item and line.item.has_lot_tracking == 1:
        finalize_issue_line_serials(line, user=request.user)
```

---

### `_reserve_line_serials(serial_ids, line, user=None) -> None` (Private)

**توضیح**: سریال‌های مشخص شده را برای یک ردیف حواله رزرو می‌کند.

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `line`: شیء ردیف حواله
- `user` (Optional[User], default=None): کاربر

**مقدار بازگشتی**: ندارد

---

### `_release_line_serials(serial_ids, line, user=None) -> None` (Private)

**توضیح**: سریال‌های مشخص شده را از رزرو آزاد می‌کند (برای ردیف‌ها).

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `line`: شیء ردیف حواله
- `user` (Optional[User], default=None): کاربر

**مقدار بازگشتی**: ندارد

---

## Helper Functions (Private)

### `_build_serial_code(receipt, sequence) -> str`

**توضیح**: کد سریال را برای یک رسید می‌سازد (فرمت: `{document_code}-{sequence:04d}`).

**پارامترهای ورودی**:
- `receipt`: شیء رسید
- `sequence` (int): شماره متوالی

**مقدار بازگشتی**:
- `str`: کد سریال (مثل `PRM-202411-0001`)

---

### `_build_serial_code_for_line(line, sequence) -> str`

**توضیح**: کد سریال را برای یک ردیف می‌سازد (فرمت: `{document_code}-L{line_id}-{sequence:04d}`).

**پارامترهای ورودی**:
- `line`: شیء ردیف
- `sequence` (int): شماره متوالی

**مقدار بازگشتی**:
- `str`: کد سریال (مثل `PRM-202411-L123-0001`)

---

### `_determine_final_status(issue) -> str`

**توضیح**: وضعیت نهایی سریال را بر اساس نوع حواله تعیین می‌کند.

**پارامترهای ورودی**:
- `issue`: شیء حواله

**مقدار بازگشتی**:
- `str`: وضعیت نهایی (`ItemSerial.Status.CONSUMED` یا `ItemSerial.Status.ISSUED`)

---

### `_determine_final_status_for_line(line) -> str`

**توضیح**: وضعیت نهایی سریال را بر اساس نوع ردیف حواله تعیین می‌کند.

**پارامترهای ورودی**:
- `line`: شیء ردیف حواله

**مقدار بازگشتی**:
- `str`: وضعیت نهایی

---

### `_history_event_for_status(status) -> str`

**توضیح**: نوع رویداد تاریخچه را بر اساس وضعیت سریال تعیین می‌کند.

**پارامترهای ورودی**:
- `status` (str): وضعیت سریال

**مقدار بازگشتی**:
- `str`: نوع رویداد (`ItemSerialHistory.EventType`)

---

## Serial Statuses

سریال‌ها می‌توانند وضعیت‌های زیر را داشته باشند:

- `AVAILABLE`: در دسترس (در انبار)
- `RESERVED`: رزرو شده (برای حواله)
- `ISSUED`: صادر شده (حواله دائم یا امانی)
- `CONSUMED`: مصرف شده (حواله مصرف)
- `RETURNED`: برگشت شده
- `DAMAGED`: آسیب دیده

---

## Serial History

هر تغییر در وضعیت سریال در `ItemSerialHistory` ثبت می‌شود که شامل:
- نوع رویداد (CREATED, RESERVED, RELEASED, ISSUED, CONSUMED, RETURNED)
- وضعیت قبلی و جدید
- انبار قبلی و جدید
- واحد سازمانی قبلی و جدید
- سند مرجع
- زمان رویداد
- کاربر ایجادکننده

---

## وابستگی‌ها

- `django.db.transaction`: برای atomic transactions
- `django.utils.timezone`: برای زمان‌های دقیق
- `decimal.Decimal`: برای محاسبات دقیق مقدار
- `inventory.models`: برای مدل‌های ItemSerial و ItemSerialHistory

---

## استفاده در پروژه

این توابع در views و signals استفاده می‌شوند:
- در `lock` views برای نهایی‌سازی سریال‌ها
- در `save` متدهای forms برای همگام‌سازی سریال‌ها
- در `after_lock` hooks برای تولید سریال‌ها

---

## نکات مهم

1. **Thread Safety**: تمام توابع از transaction استفاده می‌کنند
2. **Atomic Operations**: تغییرات سریال‌ها atomic هستند
3. **History Tracking**: تمام تغییرات در تاریخچه ثبت می‌شوند
4. **Status Management**: وضعیت سریال‌ها به صورت خودکار مدیریت می‌شود
5. **Line-based Support**: از نسخه‌های line-based برای رسیدها و حواله‌های جدید استفاده کنید


# inventory/services/serials.py - Serial Tracking Service

**هدف**: مدیریت و ردیابی سریال‌های کالاها (Item Serials) در سیستم

این فایل شامل توابع و کلاس‌های کمکی برای مدیریت کامل چرخه حیات سریال‌های کالا است، از ایجاد در receipt تا رزرو، صادر کردن، و مصرف در issue.

---

## کلاس‌های Exception

### `SerialTrackingError`

**هدف**: Base exception برای خطاهای مربوط به serial tracking

**توضیح**: تمام exception های مربوط به serial tracking از این کلاس ارث‌بری می‌کنند.

---

### `SerialQuantityMismatch(SerialTrackingError)`

**هدف**: Exception برای زمانی که quantity نمی‌تواند به سریال‌های مجزا map شود

**مثال استفاده**:
```python
raise SerialQuantityMismatch("Quantity must be a whole number when tracking serials.")
```

---

## توابع Helper (Private)

### `_build_serial_code(receipt, sequence) -> str`

**هدف**: ساخت کد سریال برای یک receipt

**پارامترهای ورودی**:
- `receipt`: Receipt object (باید `document_code` داشته باشد)
- `sequence` (int): شماره ترتیب سریال

**مقدار بازگشتی**:
- `str`: کد سریال با فرمت `{document_code}-{sequence:04d}` (مثل `REC-0001-0001`)

**منطق کار**:
- از `document_code` receipt به عنوان prefix استفاده می‌کند
- اگر `document_code` وجود نداشته باشد، از `"SER"` استفاده می‌کند
- sequence را با 4 رقم و صفر پر می‌کند

---

### `_build_serial_code_for_line(line, sequence) -> str`

**هدف**: ساخت کد سریال برای یک receipt line

**پارامترهای ورودی**:
- `line`: Receipt line object
- `sequence` (int): شماره ترتیب سریال

**مقدار بازگشتی**:
- `str`: کد سریال با فرمت `{document_code}-L{line_id}-{sequence:04d}` (مثل `REC-0001-L5-0001`)

**منطق کار**:
- از `document_code` document به عنوان prefix استفاده می‌کند
- ID خط را در کد قرار می‌دهد (`L{line_id}`)
- sequence را با 4 رقم و صفر پر می‌کند

---

### `_determine_final_status(issue) -> str`

**هدف**: تعیین وضعیت نهایی سریال‌ها بر اساس نوع issue

**پارامترهای ورودی**:
- `issue`: Issue document object

**مقدار بازگشتی**:
- `str`: وضعیت نهایی (`ItemSerial.Status.CONSUMED` یا `ItemSerial.Status.ISSUED`)

**منطق کار**:
- اگر نوع issue `IssueConsumption` باشد: `CONSUMED`
- در غیر این صورت: `ISSUED`

---

### `_determine_final_status_for_line(line) -> str`

**هدف**: تعیین وضعیت نهایی سریال‌ها بر اساس نوع issue line

**پارامترهای ورودی**:
- `line`: Issue line object

**مقدار بازگشتی**:
- `str`: وضعیت نهایی (`ItemSerial.Status.CONSUMED` یا `ItemSerial.Status.ISSUED`)

**منطق کار**:
- اگر نام کلاس line شامل `"Consumption"` باشد: `CONSUMED`
- در غیر این صورت: `ISSUED`

---

### `_history_event_for_status(status) -> str`

**هدف**: تبدیل وضعیت سریال به نوع event برای history

**پارامترهای ورودی**:
- `status` (str): وضعیت سریال

**مقدار بازگشتی**:
- `str`: نوع event (`ItemSerialHistory.EventType`)

**منطق کار**:
- `CONSUMED` → `ItemSerialHistory.EventType.CONSUMED`
- `RETURNED` → `ItemSerialHistory.EventType.RETURNED`
- سایر موارد → `ItemSerialHistory.EventType.ISSUED`

---

## توابع اصلی (Receipt-based - Legacy)

### `generate_receipt_serials(receipt, user) -> int`

**هدف**: ایجاد سریال‌های مورد نیاز برای یک receipt (برای receipt های تک‌خطی)

**پارامترهای ورودی**:
- `receipt`: Receipt object (باید `item`, `quantity`, `company`, `warehouse` داشته باشد)
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `int`: تعداد سریال‌های ایجاد شده

**منطق کار**:
1. بررسی می‌کند که `item` وجود داشته باشد و `has_lot_tracking=1` باشد
2. بررسی می‌کند که `quantity` وجود داشته باشد
3. `quantity` را به `Decimal` تبدیل می‌کند و بررسی می‌کند که عدد صحیح باشد
4. تعداد سریال‌های موجود را می‌شمارد (بر اساس `receipt_document`)
5. اگر تعداد موجود کافی باشد، `0` برمی‌گرداند
6. برای هر سریال مورد نیاز:
   - یک کد یکتا پیدا می‌کند (با حلقه while و max 100 تلاش)
   - یک `ItemSerial` ایجاد می‌کند با:
     - `current_status=AVAILABLE`
     - `current_warehouse` و `current_warehouse_code` از receipt
     - `receipt_document` و `receipt_document_code`
   - اگر receipt فیلد `serials` داشته باشد، به ManyToMany اضافه می‌کند
   - یک `ItemSerialHistory` با `EventType.CREATED` ایجاد می‌کند

**Exception ها**:
- `SerialQuantityMismatch`: اگر quantity عدد نباشد یا عدد صحیح نباشد

**مثال استفاده**:
```python
from inventory.services.serials import generate_receipt_serials

created_count = generate_receipt_serials(receipt, user=request.user)
```

---

### `sync_issue_serials(issue, previous_serial_ids, user) -> None`

**هدف**: همگام‌سازی سریال‌های issue (رزرو یا آزاد کردن) قبل از finalize شدن

**پارامترهای ورودی**:
- `issue`: Issue document object
- `previous_serial_ids` (Sequence[int]): لیست ID سریال‌های قبلی
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
1. بررسی می‌کند که issue فیلد `serials` داشته باشد
2. بررسی می‌کند که `item` وجود داشته باشد و `has_lot_tracking=1` باشد
3. سریال‌های اضافه شده و حذف شده را پیدا می‌کند:
   - `added = current_ids - previous_ids`
   - `removed = previous_ids - current_ids`
4. سریال‌های حذف شده را آزاد می‌کند (`_release_serials`)
5. سریال‌های اضافه شده را رزرو می‌کند (`_reserve_serials`)

**مثال استفاده**:
```python
from inventory.services.serials import sync_issue_serials

# در form_valid قبل از save
previous_serial_ids = list(issue.serials.values_list('id', flat=True))
# ... تغییرات در issue.serials ...
sync_issue_serials(issue, previous_serial_ids, user=request.user)
```

---

### `finalize_issue_serials(issue, user) -> None`

**هدف**: به‌روزرسانی سریال‌ها زمانی که issue document lock می‌شود

**پارامترهای ورودی**:
- `issue`: Issue document object
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
1. بررسی می‌کند که issue فیلد `serials` داشته باشد
2. بررسی می‌کند که `item` وجود داشته باشد و `has_lot_tracking=1` باشد
3. وضعیت نهایی را تعیین می‌کند (`_determine_final_status`)
4. در یک transaction atomic:
   - تمام سریال‌ها را با `select_for_update()` lock می‌کند
   - برای هر سریال:
     - وضعیت قدیمی را ذخیره می‌کند
     - وضعیت جدید را تنظیم می‌کند (`CONSUMED` یا `ISSUED`)
     - `current_document_type`, `current_document_id`, `current_document_code` را تنظیم می‌کند
     - `current_warehouse` را `None` می‌کند (چون از انبار خارج شده)
     - اگر `CONSUMED` یا `ISSUED` و `department_unit` وجود داشته باشد، آن را تنظیم می‌کند
     - سریال را save می‌کند
     - یک `ItemSerialHistory` ایجاد می‌کند

**مثال استفاده**:
```python
from inventory.services.serials import finalize_issue_serials

# در lock view
if issue.is_locked == 0:
    issue.is_locked = 1
    issue.save()
    finalize_issue_serials(issue, user=request.user)
```

---

### `_reserve_serials(serial_ids, issue, user) -> None`

**هدف**: رزرو سریال‌ها برای یک issue (private function)

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `issue`: Issue document object
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
1. در یک transaction atomic:
   - تمام سریال‌ها را با `select_for_update()` lock می‌کند
   - برای هر سریال:
     - وضعیت قدیمی را ذخیره می‌کند
     - `current_status` را `RESERVED` تنظیم می‌کند
     - `current_document_type`, `current_document_id`, `current_document_code` را تنظیم می‌کند
     - `current_warehouse` و `current_warehouse_code` را از issue می‌گیرد
     - اگر `department_unit` وجود داشته باشد، آن را تنظیم می‌کند
     - سریال را save می‌کند
     - یک `ItemSerialHistory` با `EventType.RESERVED` ایجاد می‌کند

---

### `_release_serials(serial_ids, issue, user) -> None`

**هدف**: آزاد کردن سریال‌ها از یک issue (private function)

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `issue`: Issue document object
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
1. در یک transaction atomic:
   - تمام سریال‌ها را با `select_for_update()` lock می‌کند
   - برای هر سریال:
     - وضعیت قدیمی را ذخیره می‌کند
     - `current_status` را `AVAILABLE` تنظیم می‌کند
     - `current_document_type`, `current_document_id`, `current_document_code` را پاک می‌کند
     - `current_warehouse` و `current_warehouse_code` را از issue می‌گیرد (یا از خود سریال)
     - `current_company_unit` را پاک می‌کند
     - سریال را save می‌کند
     - یک `ItemSerialHistory` با `EventType.RELEASED` ایجاد می‌کند

---

## توابع اصلی (Line-based - Multi-line Support)

### `generate_receipt_line_serials(receipt_line, user) -> int`

**هدف**: ایجاد سریال‌های مورد نیاز برای یک receipt line (برای receipt های چندخطی)

**پارامترهای ورودی**:
- `receipt_line`: Receipt line object (باید `item`, `quantity`, `company`, `warehouse`, `document` داشته باشد)
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `int`: تعداد سریال‌های ایجاد شده

**منطق کار**:
مشابه `generate_receipt_serials` اما:
- از `receipt_line_reference` برای شمارش سریال‌های موجود استفاده می‌کند
- از `_build_serial_code_for_line` برای ساخت کد استفاده می‌کند
- `receipt_line_reference` را با فرمت `"{line_class}:{line_id}"` تنظیم می‌کند
- سریال را به `receipt_line.serials` (ManyToMany) اضافه می‌کند

**مثال استفاده**:
```python
from inventory.services.serials import generate_receipt_line_serials

for line in receipt.lines.all():
    created_count = generate_receipt_line_serials(line, user=request.user)
```

---

### `sync_issue_line_serials(line, previous_serial_ids, user) -> None`

**هدف**: همگام‌سازی سریال‌های issue line (رزرو یا آزاد کردن) قبل از finalize شدن

**پارامترهای ورودی**:
- `line`: Issue line object
- `previous_serial_ids` (Sequence[int]): لیست ID سریال‌های قبلی
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
مشابه `sync_issue_serials` اما برای line:
- از `_release_line_serials` و `_reserve_line_serials` استفاده می‌کند

---

### `finalize_issue_line_serials(line, user) -> None`

**هدف**: به‌روزرسانی سریال‌ها زمانی که issue line's document lock می‌شود

**پارامترهای ورودی**:
- `line`: Issue line object
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
مشابه `finalize_issue_serials` اما برای line:
- از `_determine_final_status_for_line` استفاده می‌کند
- `current_document_type` را از نام کلاس line می‌گیرد
- `current_document_code` را از `document.document_code` می‌گیرد
- `department_unit` را از `document.department_unit` می‌گیرد

---

### `_reserve_line_serials(serial_ids, line, user) -> None`

**هدف**: رزرو سریال‌ها برای یک issue line (private function)

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `line`: Issue line object
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
مشابه `_reserve_serials` اما برای line:
- `current_document_type` را از نام کلاس line می‌گیرد
- `current_document_id` را از `line.pk` می‌گیرد
- `current_document_code` را از `document.document_code` می‌گیرد
- `current_warehouse` و `current_warehouse_code` را از `line.warehouse` می‌گیرد
- `department_unit` را از `document.department_unit` می‌گیرد

---

### `_release_line_serials(serial_ids, line, user) -> None`

**هدف**: آزاد کردن سریال‌ها از یک issue line (private function)

**پارامترهای ورودی**:
- `serial_ids` (Iterable[int]): لیست ID سریال‌ها
- `line`: Issue line object
- `user` (optional): کاربری که عملیات را انجام می‌دهد

**مقدار بازگشتی**:
- `None`

**منطق کار**:
مشابه `_release_serials` اما برای line:
- `current_warehouse` و `current_warehouse_code` را از `line.warehouse` می‌گیرد
- `reference_document_code` را از `document.document_code` می‌گیرد
- `reference_document_id` را از `line.pk` می‌گیرد

---

## وابستگی‌ها

- `decimal.Decimal`, `decimal.InvalidOperation`: برای مدیریت quantity
- `django.db.transaction`: برای atomic transactions
- `django.utils.timezone`: برای timestamps
- `django.utils.translation.gettext_lazy`: برای ترجمه پیام‌های خطا
- `inventory.models.ItemSerial`: مدل سریال
- `inventory.models.ItemSerialHistory`: مدل تاریخچه سریال

---

## استفاده در پروژه

### در Receipt Views

```python
from inventory.services.serials import generate_receipt_serials, generate_receipt_line_serials

class ReceiptCreateView(CreateView):
    def form_valid(self, form):
        receipt = form.save()
        
        # برای receipt های تک‌خطی
        if hasattr(receipt, 'item'):
            generate_receipt_serials(receipt, user=self.request.user)
        
        # برای receipt های چندخطی
        for line in receipt.lines.all():
            generate_receipt_line_serials(line, user=self.request.user)
        
        return super().form_valid(form)
```

### در Issue Views

```python
from inventory.services.serials import sync_issue_serials, finalize_issue_serials

class IssueUpdateView(UpdateView):
    def form_valid(self, form):
        issue = form.save(commit=False)
        previous_serial_ids = list(issue.serials.values_list('id', flat=True))
        
        # ... تغییرات در issue.serials ...
        
        sync_issue_serials(issue, previous_serial_ids, user=self.request.user)
        issue.save()
        return super().form_valid(form)

class IssueLockView(View):
    def post(self, request, *args, **kwargs):
        issue = get_object_or_404(Issue, pk=kwargs['pk'])
        if issue.is_locked == 0:
            issue.is_locked = 1
            issue.save()
            finalize_issue_serials(issue, user=request.user)
```

---

## وضعیت‌های سریال (ItemSerial.Status)

- `AVAILABLE`: سریال در انبار موجود است
- `RESERVED`: سریال برای یک issue رزرو شده است (قبل از lock)
- `ISSUED`: سریال صادر شده است (بعد از lock issue permanent/consignment)
- `CONSUMED`: سریال مصرف شده است (بعد از lock issue consumption)
- `RETURNED`: سریال برگشت داده شده است

---

## نکات مهم

1. **Transaction Safety**: تمام توابع اصلی از `@transaction.atomic` استفاده می‌کنند
2. **Select For Update**: برای جلوگیری از race condition، از `select_for_update()` استفاده می‌شود
3. **History Tracking**: تمام تغییرات در `ItemSerialHistory` ثبت می‌شوند
4. **Legacy Support**: توابع receipt-based برای backward compatibility نگه داشته شده‌اند
5. **Multi-line Support**: توابع line-based برای receipt/issue های چندخطی طراحی شده‌اند
6. **Quantity Validation**: quantity باید عدد صحیح باشد (نه اعشاری)
7. **Unique Serial Codes**: کدهای سریال باید یکتا باشند (با حلقه while و max 100 تلاش)

---

## تفاوت بین Receipt-based و Line-based

### Receipt-based (Legacy)
- برای receipt های تک‌خطی (مثل `ReceiptTemporary`)
- از `receipt_document` برای شمارش سریال‌ها استفاده می‌کند
- کد سریال: `{document_code}-{sequence}`

### Line-based (Multi-line)
- برای receipt/issue های چندخطی (مثل `ReceiptPermanentLine`)
- از `receipt_line_reference` برای شمارش سریال‌ها استفاده می‌کند
- کد سریال: `{document_code}-L{line_id}-{sequence}`
- سریال‌ها به `line.serials` (ManyToMany) اضافه می‌شوند


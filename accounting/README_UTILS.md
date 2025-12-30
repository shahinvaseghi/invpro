# accounting/utils.py - Utility Functions (Complete Documentation)

**هدف**: توابع utility برای ماژول accounting

این فایل شامل **1 function** است:
- `get_available_fiscal_years()`: دریافت لیست سال‌های مالی که اسناد دارند

---

## وابستگی‌ها

- `django.db.models`: `QuerySet`, `Q`, `Exists`, `OuterRef`
- `accounting.models`: `FiscalYear`, `AccountingDocument`
- `inventory.models`: (optional) Receipt models, Issue models, StocktakingRecord, PurchaseRequest, WarehouseRequest
- `sales.models`: (optional) Invoice, Order

---

## Functions

### `get_available_fiscal_years(company_id: int) -> QuerySet[FiscalYear]`

**توضیح**: دریافت لیست سال‌های مالی که اسناد دارند (حسابداری، انبار، یا فروش). اگر هیچ سندی وجود نداشته باشد، فقط سال مالی جاری را برمی‌گرداند.

**پارامترهای ورودی**:
- `company_id` (int): شناسه شرکت برای فیلتر multi-tenant

**مقدار بازگشتی**:
- `QuerySet[FiscalYear]`: QuerySet از اشیاء FiscalYear مرتب شده بر اساس `-fiscal_year_code`

**منطق**:
1. بررسی اسناد حسابداری:
   - استفاده از `Exists` برای بررسی وجود `AccountingDocument` با `fiscal_year_id`
2. بررسی اسناد انبار (در صورت نصب ماژول inventory):
   - بررسی 9 نوع سند: ReceiptTemporary, ReceiptPermanent, ReceiptConsignment, IssuePermanent, IssueConsumption, IssueConsignment, StocktakingRecord, PurchaseRequest, WarehouseRequest
   - در صورت عدم نصب ماژول، از `Q(pk__isnull=True)` استفاده می‌کند (False condition)
3. بررسی اسناد فروش (در صورت نصب ماژول sales):
   - بررسی Invoice و Order
   - در صورت عدم نصب ماژول، از `Q(pk__isnull=True)` استفاده می‌کند (False condition)
4. فیلتر کردن سال‌های مالی:
   - فیلتر بر اساس `company_id` و `is_enabled=1`
   - فیلتر بر اساس اینکه اسناد داشته باشند یا `is_current=1`
   - `distinct()` برای حذف تکراری‌ها
   - مرتب‌سازی بر اساس `-fiscal_year_code` (جدیدترین اول)

---

## استفاده در پروژه

### Import Function

```python
from accounting.utils import get_available_fiscal_years
```

### استفاده در View ها

```python
# دریافت سال‌های مالی در دسترس برای یک شرکت
fiscal_years = get_available_fiscal_years(company_id=request.session.get('active_company_id'))
```

### استفاده در Context Processor

این تابع در `accounting.context_processors.active_fiscal_year()` استفاده می‌شود برای نمایش سال‌های مالی در دسترس در تمام template ها.

---

## نکات مهم

1. **Module Dependency**: این تابع به صورت اختیاری با ماژول‌های `inventory` و `sales` کار می‌کند
2. **Performance**: از `Exists` استفاده می‌کند که برای performance بهتر است
3. **Current Fiscal Year**: سال مالی جاری (`is_current=1`) همیشه در لیست قرار می‌گیرد
4. **Company Scoping**: تمام فیلترها بر اساس `company_id` هستند

---

**Last Updated**: 2025-12-02


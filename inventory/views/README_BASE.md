# inventory/views/base.py - Base Views and Mixins

**هدف**: کلاس‌های پایه و mixin‌های قابل استفاده مجدد برای تمام views ماژول inventory

این فایل شامل کلاس‌های پایه و mixin‌هایی است که در تمام views ماژول inventory استفاده می‌شوند.

---

## Base Classes

### `InventoryBaseView(LoginRequiredMixin)`

**توضیح**: کلاس پایه با context و فیلتر شرکت مشترک برای تمام views ماژول inventory.

**متدها**:

#### `get_queryset()`

**توضیح**: queryset را بر اساس شرکت فعال فیلتر می‌کند.

**پارامترهای ورودی**: ندارد (از `self.request` استفاده می‌کند)

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس `active_company_id` از session

**منطق**:
- `active_company_id` را از `request.session` می‌خواند
- اگر مدل فیلد `company` داشته باشد، queryset را فیلتر می‌کند

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: context مشترک را به تمام templates اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: context variables اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module = 'inventory'` اضافه شده

---

#### `add_delete_permissions_to_context(context, feature_code) -> Dict[str, Any]`

**توضیح**: بررسی‌های مجوز حذف را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `context` (Dict[str, Any]): context فعلی
- `feature_code` (str): کد feature (مثل `'inventory.receipts.permanent'`)

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `can_delete_own` و `can_delete_other` اضافه شده

**متغیرهای اضافه شده**:
- `can_delete_own` (bool): آیا کاربر می‌تواند رکوردهای خود را حذف کند
- `can_delete_other` (bool): آیا کاربر می‌تواند رکوردهای دیگران را حذف کند
- `user` (User): کاربر فعلی

**مثال استفاده**:
```python
class ReceiptListView(InventoryBaseView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_delete_permissions_to_context(
            context,
            'inventory.receipts.permanent'
        )
        return context
```

---

### `DocumentLockProtectedMixin`

**توضیح**: از تغییر اسناد قفل شده موجودی جلوگیری می‌کند.

**Attributes**:
- `lock_redirect_url_name` (str): نام URL برای redirect هنگام قفل بودن
- `lock_error_message` (str): پیام خطا برای اسناد قفل (default: پیام فارسی)
- `owner_field` (str): نام فیلد مالک (default: `'created_by'`)
- `owner_error_message` (str): پیام خطا برای عدم تطابق مالک
- `protected_methods` (tuple): متدهای HTTP برای محافظت (default: همه)

**متدها**:

#### `dispatch(request, *args, **kwargs)`

**توضیح**: متد HTTP را intercept می‌کند و بررسی قفل/مالک را انجام می‌دهد.

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response یا redirect با پیام خطا

**منطق**:
1. object را از `get_object()` دریافت می‌کند
2. بررسی می‌کند که `is_locked == 1` نباشد
3. اگر `owner_field` تنظیم شده باشد، بررسی می‌کند که کاربر مالک باشد
4. اگر هر کدام fail شود، redirect با پیام خطا برمی‌گرداند

---

#### `_get_lock_redirect_url() -> str`

**توضیح**: URL redirect را هنگام قفل بودن برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: URL برای redirect

**منطق**:
1. اگر `lock_redirect_url_name` تنظیم شده باشد، از آن استفاده می‌کند
2. در غیر این صورت، از `list_url_name` استفاده می‌کند
3. در غیر این صورت، به `inventory:inventory_balance` redirect می‌کند

---

### `DocumentLockView(LoginRequiredMixin, View)`

**توضیح**: view عمومی برای قفل کردن اسناد موجودی.

**Attributes**:
- `model`: کلاس مدل برای قفل (required)
- `success_url_name`: نام URL برای redirect بعد از قفل (required)
- `success_message`: پیام موفقیت (default: پیام فارسی)
- `already_locked_message`: پیام اگر از قبل قفل باشد
- `lock_field`: نام فیلد قفل (default: `'is_locked'`)

**متدها**:

#### `before_lock(obj, request) -> bool`

**توضیح**: Hook که قبل از قفل اجرا می‌شود. اگر `False` برگرداند، قفل لغو می‌شود.

**پارامترهای ورودی**:
- `obj`: شیء برای قفل
- `request`: درخواست HTTP

**مقدار بازگشتی**:
- `bool`: `True` برای ادامه، `False` برای لغو

---

#### `after_lock(obj, request) -> None`

**توضیح**: Hook که بعد از قفل اجرا می‌شود.

**پارامترهای ورودی**:
- `obj`: شیء قفل شده
- `request`: درخواست HTTP

**مقدار بازگشتی**: ندارد

---

#### `post(request, *args, **kwargs)`

**توضیح**: منطق قفل را اجرا می‌کند.

**منطق**:
1. object را پیدا می‌کند
2. اگر از قبل قفل باشد، پیام info نمایش می‌دهد
3. `before_lock()` را فراخوانی می‌کند
4. `is_locked = 1` را تنظیم می‌کند
5. `locked_at` و `locked_by` را به‌روزرسانی می‌کند
6. `after_lock()` را فراخوانی می‌کند
7. پیام موفقیت نمایش می‌دهد
8. redirect می‌کند

---

## Mixins

### `LineFormsetMixin`

**توضیح**: مدیریت ایجاد و ذخیره line formset برای اسناد multi-line.

**Attributes**:
- `formset_class`: کلاس formset (باید توسط subclass تنظیم شود)
- `formset_prefix`: پیشوند فیلدهای formset (default: `'lines'`)

**متدها**:

#### `build_line_formset(data, instance, company_id)`

**توضیح**: line formset را با پارامترهای داده شده می‌سازد.

**پارامترهای ورودی**:
- `data` (Optional[QueryDict]): داده‌های POST
- `instance`: instance سند
- `company_id` (Optional[int]): شناسه شرکت

**مقدار بازگشتی**:
- Formset instance

---

#### `get_line_formset(data)`

**توضیح**: line formset را برای request فعلی برمی‌گرداند.

**پارامترهای ورودی**:
- `data` (Optional[QueryDict]): داده‌های POST

**مقدار بازگشتی**:
- Formset instance

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: line formset را به context اضافه می‌کند.

**مقدار بازگشتی**:
- Context با `lines_formset` اضافه شده

---

#### `form_invalid(form)`

**توضیح**: فرم نامعتبر را با formset handle می‌کند.

**پارامترهای ورودی**:
- `form`: فرم نامعتبر

**مقدار بازگشتی**:
- `HttpResponse`: response با فرم و formset

---

#### `_save_line_formset(formset) -> None`

**توضیح**: instance های line formset را ذخیره می‌کند و serial assignment را handle می‌کند.

**پارامترهای ورودی**:
- `formset`: formset برای ذخیره

**منطق**:
1. فرم‌های valid را ذخیره می‌کند
2. فرم‌های marked for deletion را حذف می‌کند
3. serial assignment را برای issue lines handle می‌کند
4. serials را reserve می‌کند

---

### `ItemUnitFormsetMixin`

**توضیح**: مدیریت ایجاد و ذخیره unit formset برای items.

**Attributes**:
- `formset_prefix`: پیشوند فیلدهای formset (default: `'units'`)

**متدها**:

#### `build_unit_formset(data, instance, company_id)`

**توضیح**: unit formset را می‌سازد.

**پارامترهای ورودی**:
- `data` (Optional[QueryDict]): داده‌های POST
- `instance`: instance item
- `company_id` (Optional[int]): شناسه شرکت

**مقدار بازگشتی**:
- `ItemUnitFormSet` instance

---

#### `_save_unit_formset(formset) -> None`

**توضیح**: instance های unit formset را ذخیره می‌کند.

**پارامترهای ورودی**:
- `formset`: formset برای ذخیره

**منطق**:
1. واحدهای valid را ذخیره می‌کند
2. کدهای واحد را برای واحدهای جدید تولید می‌کند
3. واحدهای حذف شده را حذف می‌کند

---

#### `_sync_item_warehouses(item, warehouses, user) -> None`

**توضیح**: روابط item-warehouse را همگام‌سازی می‌کند.

**پارامترهای ورودی**:
- `item`: شیء Item
- `warehouses`: لیست warehouse objects
- `user`: کاربر

**منطق**:
1. warehouse های حذف شده را حذف می‌کند
2. warehouse های جدید را ایجاد می‌کند
3. اولین warehouse را به عنوان primary تنظیم می‌کند

---

#### `_get_ordered_warehouses(form)`

**توضیح**: warehouse ها را به ترتیب انتخاب شده برمی‌گرداند.

**پارامترهای ورودی**:
- `form`: فرم item

**مقدار بازگشتی**:
- `List[Warehouse]`: لیست warehouse ها به ترتیب انتخاب

---

## وابستگی‌ها

- `django.contrib.auth.mixins`: `LoginRequiredMixin`
- `django.views.generic`: `View`
- `django.contrib import messages`
- `django.http`: `HttpResponseRedirect`
- `django.urls`: `reverse`
- `django.utils`: `timezone`
- `inventory.models`: تمام مدل‌های inventory
- `inventory.forms`: تمام formset classes
- `inventory.services.serials`: برای مدیریت serials

---

## استفاده در پروژه

این کلاس‌ها و mixin‌ها در تمام views ماژول inventory استفاده می‌شوند:

```python
from inventory.views.base import (
    InventoryBaseView,
    DocumentLockProtectedMixin,
    LineFormsetMixin
)

class ReceiptCreateView(LineFormsetMixin, InventoryBaseView, CreateView):
    model = ReceiptPermanent
    formset_class = ReceiptPermanentLineFormSet
```

---

## نکات مهم

1. **MRO (Method Resolution Order)**: `InventoryBaseView` باید اول در MRO باشد
2. **Company Filtering**: تمام views به صورت خودکار بر اساس شرکت فعال فیلتر می‌شوند
3. **Lock Protection**: از `DocumentLockProtectedMixin` برای views ویرایش/حذف استفاده کنید
4. **Formset Handling**: از `LineFormsetMixin` برای اسناد multi-line استفاده کنید


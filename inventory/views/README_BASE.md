# inventory/views/base.py - Base Views and Mixins (Complete Documentation)

**هدف**: Base classes و mixins قابل استفاده مجدد برای تمام inventory views

این فایل شامل 6 کلاس:
- `InventoryBaseView`: Base view با context مشترک
- `DocumentLockProtectedMixin`: محافظت از سندهای قفل شده (فقط برای modification methods)
- `DocumentLockView`: View برای lock کردن سندها
- `DocumentUnlockView`: View برای unlock کردن سندها با permission checking
- `LineFormsetMixin`: Mixin برای مدیریت line formsets
- `ItemUnitFormsetMixin`: Mixin برای مدیریت item unit formsets

---

## وابستگی‌ها

- `inventory.models`: `Item`, `ItemUnit`, `ItemSerial`, `ItemWarehouse`
- `inventory.forms`: `ItemUnitFormSet`
- `inventory.services.serials`: `sync_issue_line_serials`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`
- `django.contrib.auth.mixins.LoginRequiredMixin`
- `django.views.generic.View`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse`
- `django.utils.timezone`
- `django.utils.translation.gettext_lazy`
- `django.shortcuts.get_object_or_404`
- `django.contrib.messages`

---

## InventoryBaseView

### `InventoryBaseView(LoginRequiredMixin)`

**توضیح**: Base view با context مشترک برای ماژول inventory

**Inheritance**: `LoginRequiredMixin`

**Attributes**:
- `login_url`: `'/admin/login/'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: فیلتر queryset بر اساس company فعال.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس `active_company_id`

**منطق**:
1. دریافت queryset از `super().get_queryset()`
2. اگر model field `company` داشته باشد، فیلتر بر اساس `active_company_id`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن context data مشترک.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module = 'inventory'`

---

#### `add_delete_permissions_to_context(self, context: Dict[str, Any], feature_code: str) -> Dict[str, Any]`

**توضیح**: اضافه کردن permission checks برای delete به context.

**پارامترهای ورودی**:
- `context`: context dictionary
- `feature_code`: کد feature برای permission check

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `can_delete_own`, `can_delete_other`, `user` اضافه شده

**Context Variables اضافه شده**:
- `can_delete_own`: آیا user می‌تواند own records را حذف کند
- `can_delete_other`: آیا user می‌تواند other records را حذف کند
- `user`: user object

**منطق**:
1. دریافت permissions از `get_user_feature_permissions()`
2. بررسی `delete_own` و `delete_other` permissions
3. Superuser همیشه می‌تواند حذف کند

---

#### `filter_queryset_by_permissions(self, queryset, feature_code: str, owner_field: str = 'created_by') -> QuerySet`

**توضیح**: فیلتر queryset بر اساس permissions کاربر.

**پارامترهای ورودی**:
- `queryset`: queryset برای فیلتر
- `feature_code`: کد feature برای permission checking (مثلاً `'inventory.receipts.temporary'`)
- `owner_field`: نام فیلد owner/creator (پیش‌فرض: `'created_by'`)

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. اگر کاربر superuser باشد، queryset را بدون تغییر برمی‌گرداند
2. دریافت permissions از `get_user_feature_permissions()`
3. بررسی `view_all` permission (اگر داشته باشد، queryset را بدون تغییر برمی‌گرداند)
4. بررسی `view_own` permission (اگر داشته باشد، queryset را بر اساس `owner_field` فیلتر می‌کند)
5. اگر هیچ permission نداشته باشد، empty queryset برمی‌گرداند

---

## DocumentLockProtectedMixin

### `DocumentLockProtectedMixin`

**توضیح**: جلوگیری از ویرایش یا حذف سندهای قفل شده (نه مشاهده)

**Attributes**:
- `lock_redirect_url_name`: `''` (override در subclasses)
- `lock_error_message`: `_('سند قفل شده و قابل ویرایش یا حذف نیست.')`
- `owner_field`: `'created_by'` (field برای بررسی owner)
- `owner_error_message`: `_('فقط ایجاد کننده می‌تواند این سند را ویرایش کند.')`
- `protected_methods`: `('post', 'put', 'patch', 'delete')` - **GET شامل نمی‌شود**

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی lock status و owner قبل از dispatch.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: redirect اگر قفل شده یا owner نیست، در غیر این صورت `super().dispatch()`

**منطق**:
1. اگر method در `protected_methods` باشد:
   - دریافت object
   - بررسی `is_locked` (اگر قفل شده باشد، redirect)
   - بررسی owner (اگر owner_field تنظیم شده باشد و owner نباشد، redirect)
2. فراخوانی `super().dispatch()`

---

#### `_get_lock_redirect_url(self) -> str`

**توضیح**: دریافت URL برای redirect وقتی سند قفل شده است.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `str`: URL برای redirect

**منطق**:
1. اگر `lock_redirect_url_name` تنظیم شده باشد، از آن استفاده می‌کند
2. اگر `list_url_name` در view موجود باشد، از آن استفاده می‌کند
3. در غیر این صورت، `inventory:inventory_balance`

---

## DocumentLockView

### `DocumentLockView(LoginRequiredMixin, View)`

**توضیح**: View عمومی برای lock کردن سندهای inventory

**Inheritance**: `LoginRequiredMixin, View`

**Attributes**:
- `model`: `None` (باید در subclass تنظیم شود)
- `success_url_name`: `''` (باید در subclass تنظیم شود)
- `success_message`: `_('سند با موفقیت قفل شد و دیگر قابل ویرایش نیست.')`
- `already_locked_message`: `_('این سند قبلاً قفل شده است.')`
- `lock_field`: `'is_locked'`

**متدها**:

#### `post(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: Lock کردن سند

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url_name`

**منطق**:
1. بررسی `model` و `success_url_name`
2. دریافت object
3. بررسی `is_locked` (اگر قفل شده باشد، پیام info)
4. فراخوانی `before_lock()` (اگر `False` برگرداند، لغو)
5. تنظیم `is_locked = 1`, `locked_at = timezone.now()`, `locked_by = request.user`
6. فراخوانی `after_lock()`
7. نمایش پیام موفقیت
8. Redirect به `success_url_name`

**Hooks**:
- `before_lock(obj, request) -> bool`: Hook که قبل از lock اجرا می‌شود. اگر `False` برگرداند، lock لغو می‌شود.
- `after_lock(obj, request) -> None`: Hook برای subclasses برای انجام actions اضافی بعد از lock.

---

## DocumentUnlockView

### `DocumentUnlockView(LoginRequiredMixin, View)`

**توضیح**: View برای unlock کردن سندها با permission checking

**Attributes**:
- `model`: مدل سند (باید در subclass تنظیم شود)
- `success_url_name`: نام URL برای redirect بعد از unlock
- `success_message`: پیام موفقیت
- `already_unlocked_message`: پیام برای سندهای قبلاً unlock شده
- `lock_field`: نام فیلد lock (پیش‌فرض: `'is_locked'`)
- `feature_code`: کد feature برای permission checking
- `required_action`: action مورد نیاز (پیش‌فرض: `'unlock_own'`)

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از unlock

**Logic**:
- **Superuser bypass**: اگر کاربر superuser باشد، اجازه داده می‌شود
- بررسی `unlock_own` برای اسناد خود کاربر
- بررسی `unlock_other` برای اسناد سایر کاربران
- اگر permission نداشته باشد، `PermissionDenied` می‌دهد

#### `post(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: Unlock کردن سند

**Logic**:
- بررسی اینکه سند قبلاً unlock نشده باشد
- تنظیم `is_locked = 0`
- پاک کردن `locked_at` و `locked_by` (اگر وجود داشته باشند)
- ذخیره سند
- نمایش پیام موفقیت
- Redirect به `success_url_name`

**نکته**: این view از `shared.utils.permissions` برای بررسی دسترسی‌ها استفاده می‌کند.

---

## DocumentUnlockView

### `DocumentUnlockView(LoginRequiredMixin, View)`

**توضیح**: View عمومی برای unlock کردن سندهای inventory با permission checking

**Inheritance**: `LoginRequiredMixin, View`

**Attributes**:
- `model`: `None` (باید در subclass تنظیم شود)
- `success_url_name`: `''` (باید در subclass تنظیم شود)
- `success_message`: `_('سند با موفقیت از قفل خارج شد و قابل ویرایش است.')`
- `already_unlocked_message`: `_('این سند قبلاً از قفل خارج شده است.')`
- `lock_field`: `'is_locked'`
- `feature_code`: `''` (باید در subclass تنظیم شود)
- `required_action`: `'unlock_own'` (action برای permission checking)

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از unlock

**منطق**:
- **Superuser bypass**: اگر کاربر superuser باشد، اجازه داده می‌شود
- بررسی `unlock_own` برای اسناد خود کاربر
- بررسی `unlock_other` برای اسناد سایر کاربران
- اگر permission نداشته باشد، `PermissionDenied` می‌دهد

#### `post(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: Unlock کردن سند

**منطق**:
1. بررسی `model` و `success_url_name`
2. دریافت object
3. بررسی `is_locked` (اگر unlock شده باشد، پیام info)
4. فراخوانی `before_unlock()` (اگر `False` برگرداند، لغو)
5. تنظیم `is_locked = 0`, `locked_at = None`, `locked_by = None`
6. فراخوانی `after_unlock()`
7. نمایش پیام موفقیت
8. Redirect به `success_url_name`

**Hooks**:
- `before_unlock(obj, request) -> bool`: Hook که قبل از unlock اجرا می‌شود. اگر `False` برگرداند، unlock لغو می‌شود.
- `after_unlock(obj, request) -> None`: Hook برای subclasses برای انجام actions اضافی بعد از unlock.

---

## LineFormsetMixin

### `LineFormsetMixin`

**توضیح**: Mixin برای مدیریت line formset creation و saving برای multi-line documents

**Attributes**:
- `formset_class`: `None` (باید در subclass تنظیم شود)
- `formset_prefix`: `'lines'`

**متدها**:

#### `build_line_formset(self, data=None, instance=None, company_id: Optional[int] = None, request=None) -> FormSet`

**توضیح**: ساخت line formset برای document.

**پارامترهای ورودی**:
- `data`: POST data (optional)
- `instance`: document instance (optional)
- `company_id`: شناسه شرکت (optional)
- `request`: HTTP request (optional)

**مقدار بازگشتی**:
- `FormSet`: formset instance

**منطق**:
1. تعیین instance (از `self.object` یا parameter)
2. تعیین company_id (از instance یا session)
3. تعیین request (از `self.request` یا parameter)
4. ساخت formset با kwargs

---

#### `get_line_formset(self, data=None) -> FormSet`

**توضیح**: دریافت line formset برای request فعلی.

**پارامترهای ورودی**:
- `data`: POST data (optional)

**مقدار بازگشتی**:
- `FormSet`: formset instance

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن line formset به context.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `lines_formset` اضافه شده

---

#### `form_invalid(self, form) -> HttpResponse`

**توضیح**: Handle کردن invalid form با formset.

**پارامترهای ورودی**:
- `form`: form instance

**مقدار بازگشتی**:
- `HttpResponse`: response با form و formset errors

---

#### `_save_line_formset(self, formset) -> None`

**توضیح**: ذخیره line formset instances.

**پارامترهای ورودی**:
- `formset`: formset instance

**مقدار بازگشتی**: ندارد

**منطق**:
1. برای هر form در formset:
   - بررسی `cleaned_data` (اگر وجود ندارد، skip)
   - بررسی `DELETE` (اگر True باشد، حذف)
   - بررسی `item` (اگر وجود ندارد، skip)
   - بررسی errors (اگر وجود دارد، skip)
   - ذخیره instance
   - ذخیره M2M relationships (serials)
   - Handle selected serials از hidden input (برای new issue lines)

**نکات مهم**:
- Serial assignment برای issue lines
- Serial reservation با `sync_issue_line_serials()`

---

## ItemUnitFormsetMixin

### `ItemUnitFormsetMixin`

**توضیح**: Mixin برای مدیریت item unit formset creation و saving

**Attributes**:
- `formset_prefix`: `'units'`

**متدها**:

#### `build_unit_formset(self, data=None, instance=None, company_id: Optional[int] = None) -> FormSet`

**توضیح**: ساخت unit formset برای item.

**پارامترهای ورودی**:
- `data`: POST data (optional)
- `instance`: item instance (optional)
- `company_id`: شناسه شرکت (optional)

**مقدار بازگشتی**:
- `FormSet`: `ItemUnitFormSet` instance

---

#### `get_unit_formset(self, data=None) -> FormSet`

**توضیح**: دریافت unit formset برای request فعلی.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن unit formset به context.

**Context Variables اضافه شده**:
- `units_formset`: formset instance
- `units_formset_empty`: empty form برای JavaScript cloning

---

#### `form_invalid(self, form) -> HttpResponse`

**توضیح**: Handle کردن invalid form با unit formset.

---

#### `_generate_unit_code(self, company) -> str`

**توضیح**: تولید sequential unit code.

**پارامترهای ورودی**:
- `company`: company instance

**مقدار بازگشتی**:
- `str`: unit code (6 digits)

**منطق**:
1. دریافت آخرین code
2. Increment و zero-pad به 6 digits

---

#### `_save_unit_formset(self, formset) -> None`

**توضیح**: ذخیره unit formset instances.

**منطق**:
1. برای هر unit:
   - بررسی `from_unit` و `to_unit` (اگر وجود ندارد، skip)
   - تنظیم `company`, `item`, `item_code`
   - تولید `public_code` اگر وجود ندارد
   - ذخیره
2. حذف deleted objects

---

#### `_sync_item_warehouses(self, item, warehouses, user) -> None`

**توضیح**: همگام‌سازی روابط item-warehouse.

**پارامترهای ورودی**:
- `item`: item instance
- `warehouses`: لیست warehouse instances
- `user`: user instance

**مقدار بازگشتی**: ندارد

**منطق**:
1. حذف warehouses حذف شده
2. برای هر warehouse:
   - تعیین `is_primary` (اولین warehouse primary است)
   - اگر موجود است، به‌روزرسانی
   - اگر موجود نیست، ایجاد

---

#### `_get_ordered_warehouses(self, form) -> list`

**توضیح**: دریافت warehouses به ترتیب انتخاب شده.

**پارامترهای ورودی**:
- `form`: form instance

**مقدار بازگشتی**:
- `list`: لیست warehouses به ترتیب انتخاب

**منطق**:
1. دریافت warehouses از `cleaned_data`
2. دریافت order از POST data
3. مرتب‌سازی بر اساس order

---

## نکات مهم

### 1. Company Filtering
- تمام mixins بر اساس `active_company_id` فیلتر می‌کنند

### 2. Lock Mechanism
- `DocumentLockProtectedMixin` از ویرایش/حذف قفل شده جلوگیری می‌کند (اما GET مجاز است)
- `DocumentLockView` برای lock کردن استفاده می‌شود
- `DocumentUnlockView` برای unlock کردن با permission checking استفاده می‌شود

### 3. Formset Management
- `LineFormsetMixin` برای multi-line documents
- `ItemUnitFormsetMixin` برای item unit conversions

### 4. Serial Management
- `_save_line_formset` serial assignment و reservation را handle می‌کند

---

## الگوهای مشترک

1. **Company Filtering**: تمام mixins بر اساس `active_company_id` فیلتر می‌کنند
2. **Error Handling**: خطاها با messages نمایش داده می‌شوند
3. **Permission Checking**: از `shared.utils.permissions` استفاده می‌شود
4. **Formset Handling**: Formsets به صورت dynamic ساخته و ذخیره می‌شوند

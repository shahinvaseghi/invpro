# inventory/views/stocktaking.py - Stocktaking Views (Complete Documentation)

**هدف**: Views برای مدیریت انبارگردانی (Stocktaking) در ماژول inventory

این فایل شامل views برای:
- Stocktaking Deficit (کسری انبارگردانی)
- Stocktaking Surplus (مازاد انبارگردانی)
- Stocktaking Record (سند نهایی انبارگردانی)

**جمعاً: 16 کلاس view** (1 Mixin + 15 view classes)

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`, `DocumentLockProtectedMixin`, `DocumentLockView`
- `inventory.views.receipts`: `DocumentDeleteViewBase`
- `inventory.models`: `StocktakingDeficit`, `StocktakingSurplus`, `StocktakingRecord`
- `inventory.forms`: `StocktakingDeficitForm`, `StocktakingSurplusForm`, `StocktakingRecordForm`, `UNIT_CHOICES`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse`, `reverse_lazy`
- `django.utils.translation.gettext_lazy`
- `django.utils.safestring.mark_safe`
- `json`

---

## StocktakingFormMixin

### `StocktakingFormMixin(InventoryBaseView)`

**توضیح**: Shared helpers برای stocktaking create/update views

**Inheritance**: `InventoryBaseView`

**Attributes**:
- `template_name`: `'inventory/stocktaking_form.html'`
- `form_title`: `''` (override در subclasses)
- `list_url_name`: `''` (override در subclasses)
- `lock_url_name`: `''` (override در subclasses)

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` و `user` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` و `user` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `request.session.get('active_company_id')` اضافه می‌کند
3. `user` را از `request.user` اضافه می‌کند (برای permission checks)
4. kwargs را برمی‌گرداند

---

#### `get_fieldsets(self) -> list`

**توضیح**: Fieldsets configuration را برمی‌گرداند. باید در subclasses override شود.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples با format `(title, [field_names])`

**منطق**:
- در base class، empty list برمی‌گرداند
- باید در subclasses override شود

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: Context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `form_title`: عنوان فرم
- `fieldsets`: لیست fieldsets برای نمایش در template
- `used_fields`: لیست فیلدهای استفاده شده در fieldsets
- `list_url`: URL برای لیست
- `is_edit`: آیا در edit mode هستیم
- `unit_options_json`: JSON map از item_id به allowed units
- `unit_placeholder`: placeholder برای unit field
- `warehouse_options_json`: JSON map از item_id به allowed warehouses
- `warehouse_placeholder`: placeholder برای warehouse field
- `document_instance`: instance document
- `document_is_locked`: آیا document قفل شده است
- `lock_url`: URL برای lock کردن document (اگر قفل نشده باشد)

**منطق**:
1. `form_title`, `list_url`, `is_edit` را اضافه می‌کند
2. Fieldsets را از `get_fieldsets()` می‌سازد
3. `unit_options_json` و `warehouse_options_json` را از form می‌سازد
4. Lock status و lock URL را بررسی می‌کند

---

## Stocktaking Deficit Views

### StocktakingDeficitListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/stocktaking_deficit.html`

**Attributes**:
- `model`: `StocktakingDeficit`
- `template_name`: `'inventory/stocktaking_deficit.html'`
- `context_object_name`: `'records'`
- `paginate_by`: `50`

**Context Variables**:
- `create_url`: URL برای ایجاد
- `edit_url_name`: نام URL برای ویرایش
- `delete_url_name`: نام URL برای حذف
- `lock_url_name`: نام URL برای lock
- Delete permissions (از `add_delete_permissions_to_context`)

**URL**: `/inventory/stocktaking/deficit/`

---

### StocktakingDeficitCreateView

**Type**: `StocktakingFormMixin, CreateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingDeficitForm`

**Success URL**: `inventory:stocktaking_deficit`

**Attributes**:
- `model`: `StocktakingDeficit`
- `form_class`: `StocktakingDeficitForm`
- `template_name`: `'inventory/stocktaking_form.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_deficit')`
- `form_title`: `_('ایجاد سند کسری انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_deficit'`
- `lock_url_name`: `'inventory:stocktaking_deficit_lock'`

**متدها**:
- `form_valid()`: تنظیم `company_id`, `created_by`، نمایش پیام موفقیت
- `get_fieldsets()`: بازگشت fieldsets configuration

**Fieldsets**:
1. اطلاعات سند: `stocktaking_session_id`, `item`, `warehouse`, `unit`
2. مقادیر: `quantity_expected`, `quantity_counted`, `quantity_adjusted`
3. ارزش‌گذاری: `valuation_method`, `unit_cost`, `total_cost`
4. جزئیات اضافه: `reason_code`, `investigation_reference`

**URL**: `/inventory/stocktaking/deficit/create/`

---

### StocktakingDeficitUpdateView

**Type**: `DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingDeficitForm`

**Success URL**: `inventory:stocktaking_deficit`

**Attributes**:
- `model`: `StocktakingDeficit`
- `form_class`: `StocktakingDeficitForm`
- `template_name`: `'inventory/stocktaking_form.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_deficit')`
- `form_title`: `_('ویرایش سند کسری انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_deficit'`
- `lock_url_name`: `'inventory:stocktaking_deficit_lock'`

**متدها**:
- `form_valid()`: تنظیم `edited_by`، اگر `created_by` وجود ندارد تنظیم می‌کند، نمایش پیام موفقیت
- `get_fieldsets()`: مشابه CreateView

**نکات مهم**:
- از `DocumentLockProtectedMixin` استفاده می‌کند (قفل شده قابل ویرایش نیست)

**URL**: `/inventory/stocktaking/deficit/<pk>/edit/`

---

### StocktakingDeficitDeleteView

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/stocktaking_deficit_confirm_delete.html`

**Success URL**: `inventory:stocktaking_deficit`

**Attributes**:
- `model`: `StocktakingDeficit`
- `template_name`: `'inventory/stocktaking_deficit_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_deficit')`
- `feature_code`: `'inventory.stocktaking.deficit'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('سند کسری موجودی با موفقیت حذف شد.')`

**URL**: `/inventory/stocktaking/deficit/<pk>/delete/`

---

### StocktakingDeficitLockView

**Type**: `DocumentLockView`

**Success URL**: `inventory:stocktaking_deficit`

**Attributes**:
- `model`: `StocktakingDeficit`
- `success_url_name`: `'inventory:stocktaking_deficit'`
- `success_message`: `_('سند کسری شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')`

**URL**: `/inventory/stocktaking/deficit/<pk>/lock/`

---

## Stocktaking Surplus Views

### StocktakingSurplusListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/stocktaking_surplus.html`

**Attributes**:
- `model`: `StocktakingSurplus`
- `template_name`: `'inventory/stocktaking_surplus.html'`
- `context_object_name`: `'records'`
- `paginate_by`: `50`

**Context Variables**: مشابه `StocktakingDeficitListView`

**URL**: `/inventory/stocktaking/surplus/`

---

### StocktakingSurplusCreateView

**Type**: `StocktakingFormMixin, CreateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingSurplusForm`

**Success URL**: `inventory:stocktaking_surplus`

**Attributes**:
- `model`: `StocktakingSurplus`
- `form_class`: `StocktakingSurplusForm`
- `template_name`: `'inventory/stocktaking_form.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_surplus')`
- `form_title`: `_('ایجاد سند مازاد انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_surplus'`
- `lock_url_name`: `'inventory:stocktaking_surplus_lock'`

**متدها**: مشابه `StocktakingDeficitCreateView`

**Fieldsets**: مشابه `StocktakingDeficitCreateView`

**URL**: `/inventory/stocktaking/surplus/create/`

---

### StocktakingSurplusUpdateView

**Type**: `DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingSurplusForm`

**Success URL**: `inventory:stocktaking_surplus`

**Attributes**:
- `model`: `StocktakingSurplus`
- `form_class`: `StocktakingSurplusForm`
- `template_name`: `'inventory/stocktaking_form.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_surplus')`
- `form_title`: `_('ویرایش سند مازاد انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_surplus'`
- `lock_url_name`: `'inventory:stocktaking_surplus_lock'`

**متدها**: مشابه `StocktakingDeficitUpdateView`

**URL**: `/inventory/stocktaking/surplus/<pk>/edit/`

---

### StocktakingSurplusDeleteView

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/stocktaking_surplus_confirm_delete.html`

**Success URL**: `inventory:stocktaking_surplus`

**Attributes**:
- `model`: `StocktakingSurplus`
- `template_name`: `'inventory/stocktaking_surplus_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_surplus')`
- `feature_code`: `'inventory.stocktaking.surplus'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('سند مازاد موجودی با موفقیت حذف شد.')`

**URL**: `/inventory/stocktaking/surplus/<pk>/delete/`

---

### StocktakingSurplusLockView

**Type**: `DocumentLockView`

**Success URL**: `inventory:stocktaking_surplus`

**Attributes**:
- `model`: `StocktakingSurplus`
- `success_url_name`: `'inventory:stocktaking_surplus'`
- `success_message`: `_('سند مازاد شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')`

**URL**: `/inventory/stocktaking/surplus/<pk>/lock/`

---

## Stocktaking Record Views

### StocktakingRecordListView

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/stocktaking_records.html`

**Attributes**:
- `model`: `StocktakingRecord`
- `template_name`: `'inventory/stocktaking_records.html'`
- `context_object_name`: `'records'`
- `paginate_by`: `50`

**Context Variables**: مشابه `StocktakingDeficitListView`

**URL**: `/inventory/stocktaking/records/`

---

### StocktakingRecordCreateView

**Type**: `StocktakingFormMixin, CreateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingRecordForm`

**Success URL**: `inventory:stocktaking_records`

**Attributes**:
- `model`: `StocktakingRecord`
- `form_class`: `StocktakingRecordForm`
- `template_name`: `'inventory/stocktaking_form.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_records')`
- `form_title`: `_('ایجاد سند نهایی انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_records'`
- `lock_url_name`: `'inventory:stocktaking_record_lock'`

**متدها**:
- `form_valid()`: تنظیم `company_id`, `created_by`، نمایش پیام موفقیت
- `get_fieldsets()`: بازگشت fieldsets configuration

**Fieldsets**:
1. اطلاعات سند: `stocktaking_session_id`
2. تأیید موجودی: `confirmed_by`, `confirmation_notes`
3. وضعیت تایید: `approver`, `approval_status`, `approver_notes`
4. خلاصه موجودی: `final_inventory_value`

**URL**: `/inventory/stocktaking/records/create/`

---

### StocktakingRecordUpdateView

**Type**: `DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingRecordForm`

**Success URL**: `inventory:stocktaking_records`

**Attributes**:
- `model`: `StocktakingRecord`
- `form_class`: `StocktakingRecordForm`
- `template_name`: `'inventory/stocktaking_form.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_records')`
- `form_title`: `_('ویرایش سند نهایی انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_records'`
- `lock_url_name`: `'inventory:stocktaking_record_lock'`

**متدها**: مشابه `StocktakingDeficitUpdateView`

**Fieldsets**: مشابه `StocktakingRecordCreateView`

**URL**: `/inventory/stocktaking/records/<pk>/edit/`

---

### StocktakingRecordDeleteView

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/stocktaking_record_confirm_delete.html`

**Success URL**: `inventory:stocktaking_records`

**Attributes**:
- `model`: `StocktakingRecord`
- `template_name`: `'inventory/stocktaking_record_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_records')`
- `feature_code`: `'inventory.stocktaking.records'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('سند شمارش موجودی با موفقیت حذف شد.')`

**URL**: `/inventory/stocktaking/records/<pk>/delete/`

---

### StocktakingRecordLockView

**Type**: `DocumentLockView`

**Success URL**: `inventory:stocktaking_records`

**Attributes**:
- `model`: `StocktakingRecord`
- `success_url_name`: `'inventory:stocktaking_records'`
- `success_message`: `_('سند شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')`

**URL**: `/inventory/stocktaking/records/<pk>/lock/`

---

## نکات مهم

### 1. Fieldsets
- Fieldsets برای سازماندهی فیلدها در template استفاده می‌شوند
- هر view می‌تواند fieldsets خودش را تعریف کند
- Fieldsets در `get_context_data()` پردازش می‌شوند

### 2. Unit and Warehouse Options
- `unit_options_json` و `warehouse_options_json` برای dynamic dropdowns استفاده می‌شوند
- از `form._get_item_allowed_units()` و `form._get_item_allowed_warehouses()` استفاده می‌شود

### 3. Lock Mechanism
- از `DocumentLockProtectedMixin` برای محافظت از قفل شده استفاده می‌شود
- از `DocumentLockView` برای lock کردن استفاده می‌شود
- قفل شده قابل ویرایش نیست

### 4. Delete Permissions
- از `add_delete_permissions_to_context()` برای اضافه کردن delete permissions استفاده می‌شود

### 5. Document Types
- **Deficit**: کسری انبارگردانی (quantity_counted < quantity_expected)
- **Surplus**: مازاد انبارگردانی (quantity_counted > quantity_expected)
- **Record**: سند نهایی انبارگردانی (خلاصه و تأیید)

---

## الگوهای مشترک

1. **Company Filtering**: تمام forms با `company_id` initialize می‌شوند
2. **Lock Protection**: Update views از `DocumentLockProtectedMixin` استفاده می‌کنند
3. **Fieldsets**: Fieldsets برای سازماندهی فیلدها استفاده می‌شوند
4. **Dynamic Options**: Unit و warehouse options به صورت dynamic از form استخراج می‌شوند
5. **Permission Checking**: Delete views از `DocumentDeleteViewBase` استفاده می‌کنند

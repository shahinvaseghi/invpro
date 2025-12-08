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

**Template**: `inventory/stocktaking_deficit.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/stocktaking_deficit.html` extends `shared/generic/generic_list.html`
  - Overrides: `breadcrumb_extra`, `page_actions`, `before_table` (styles), `table_headers`, `table_rows` (with rowspan for multi-line documents), `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `StocktakingDeficit`
- `template_name`: `'inventory/stocktaking_deficit.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions آماده می‌کند.

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.deficit', 'created_by')`
3. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
4. `select_related('created_by')` را اعمال می‌کند
5. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template آماده می‌کند.

**Context Variables برای Generic Template**:
- `page_title`: `_('Deficit Records')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `create_url`: `reverse_lazy('inventory:stocktaking_deficit_create')`
- `create_button_text`: `_('Create Deficit Record')`
- `show_actions`: `True`

**Context Variables برای Stocktaking Deficit-Specific Features**:
- `edit_url_name`: `'inventory:stocktaking_deficit_edit'`
- `delete_url_name`: `'inventory:stocktaking_deficit_delete'`
- `lock_url_name`: `'inventory:stocktaking_deficit_lock'`
- `empty_state_title`: `_('No Deficit Records Found')`
- `empty_state_message`: `_('Deficit records are created during stocktaking when counted quantity is less than expected.')`
- `empty_state_icon`: `'📉'`

**Context Variables برای Permissions**:
- `can_delete_own`, `can_delete_other`: از `add_delete_permissions_to_context()`
- `user`: کاربر فعلی (برای permission checks در template)

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

**Type**: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingDeficitForm`

**Formset**: `StocktakingDeficitLineFormSet`

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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions آماده می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده و بهینه شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.deficit', 'created_by')`
3. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
4. `select_related('created_by')` را اعمال می‌کند
5. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: تنظیم `edited_by`، اگر `created_by` وجود ندارد تنظیم می‌کند، نمایش پیام موفقیت.

#### `get_fieldsets(self) -> list`

**توضیح**: مشابه CreateView - fieldsets configuration را برمی‌گرداند.

**نکات مهم**:
- از `DocumentLockProtectedMixin` استفاده می‌کند (قفل شده قابل ویرایش نیست)

**URL**: `/inventory/stocktaking/deficit/<pk>/edit/`

---

### StocktakingDeficitDeleteView

**Type**: `InventoryBaseView, BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:stocktaking_deficit`

**Attributes**:
- `model`: `StocktakingDeficit`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_deficit')`
- `feature_code`: `'inventory.stocktaking.deficit'`
- `success_message`: `_('سند کسری موجودی با موفقیت حذف شد.')`
- `owner_field`: `'created_by'`

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از اجازه دادن به حذف.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا `PermissionDenied` exception

**منطق**: مشابه `IssuePermanentDeleteView.dispatch()` با feature code `'inventory.stocktaking.deficit'`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Deficit Record')`
- `confirmation_message`: `_('Do you really want to delete this deficit record?')`
- `object_details`: لیست جزئیات record (Document Code, Document Date, Created By)
- `cancel_url`: `reverse_lazy('inventory:stocktaking_deficit')`
- `breadcrumbs`: لیست breadcrumbs برای navigation

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

**Template**: `inventory/stocktaking_surplus.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/stocktaking_surplus.html` extends `shared/generic/generic_list.html`
  - Overrides: `breadcrumb_extra`, `page_actions`, `before_table` (styles), `table_headers`, `table_rows` (with rowspan for multi-line documents), `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `StocktakingSurplus`
- `template_name`: `'inventory/stocktaking_surplus.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions آماده می‌کند.

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.surplus', 'created_by')`
3. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
4. `select_related('created_by')` را اعمال می‌کند
5. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template آماده می‌کند.

**Context Variables برای Generic Template**:
- `page_title`: `_('Surplus Records')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `create_url`: `reverse_lazy('inventory:stocktaking_surplus_create')`
- `create_button_text`: `_('Create Surplus Record')`
- `show_actions`: `True`

**Context Variables برای Stocktaking Surplus-Specific Features**:
- `edit_url_name`: `'inventory:stocktaking_surplus_edit'`
- `delete_url_name`: `'inventory:stocktaking_surplus_delete'`
- `lock_url_name`: `'inventory:stocktaking_surplus_lock'`
- `empty_state_title`: `_('No Surplus Records Found')`
- `empty_state_message`: `_('Surplus records are created during stocktaking when counted quantity is more than expected.')`
- `empty_state_icon`: `'📈'`

**Context Variables برای Permissions**:
- `can_delete_own`, `can_delete_other`: از `add_delete_permissions_to_context()`
- `user`: کاربر فعلی (برای permission checks در template)

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

**Type**: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`

**Template**: `inventory/stocktaking_form.html`

**Form**: `StocktakingSurplusForm`

**Formset**: `StocktakingSurplusLineFormSet`

**Success URL**: `inventory:stocktaking_surplus`

**Attributes**:
- `model`: `StocktakingSurplus`
- `form_class`: `StocktakingSurplusForm`
- `template_name`: `'inventory/stocktaking_form.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_surplus')`
- `form_title`: `_('ویرایش سند مازاد انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_surplus'`
- `lock_url_name`: `'inventory:stocktaking_surplus_lock'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions آماده می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده و بهینه شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.surplus', 'created_by')`
3. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
4. `select_related('created_by')` را اعمال می‌کند
5. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: تنظیم `edited_by`، اگر `created_by` وجود ندارد تنظیم می‌کند، نمایش پیام موفقیت.

#### `get_fieldsets(self) -> list`

**توضیح**: مشابه CreateView - fieldsets configuration را برمی‌گرداند.

**URL**: `/inventory/stocktaking/surplus/<pk>/edit/`

---

### StocktakingSurplusDeleteView

**Type**: `InventoryBaseView, BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:stocktaking_surplus`

**Attributes**:
- `model`: `StocktakingSurplus`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_surplus')`
- `feature_code`: `'inventory.stocktaking.surplus'`
- `success_message`: `_('سند مازاد موجودی با موفقیت حذف شد.')`
- `owner_field`: `'created_by'`

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از اجازه دادن به حذف.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا `PermissionDenied` exception

**منطق**: مشابه `IssuePermanentDeleteView.dispatch()` با feature code `'inventory.stocktaking.surplus'`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Surplus Record')`
- `confirmation_message`: `_('Do you really want to delete this surplus record?')`
- `object_details`: لیست جزئیات record (Document Code, Document Date, Created By)
- `cancel_url`: `reverse_lazy('inventory:stocktaking_surplus')`
- `breadcrumbs`: لیست breadcrumbs برای navigation

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

**Template**: `inventory/stocktaking_records.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/stocktaking_records.html` extends `shared/generic/generic_list.html`
  - Overrides: `breadcrumb_extra`, `page_actions`, `before_table` (styles), `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `StocktakingRecord`
- `template_name`: `'inventory/stocktaking_records.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با فیلتر permissions و prefetch آماده می‌کند.

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.records', 'created_by')`
3. `select_related('confirmed_by', 'created_by')` را اعمال می‌کند
4. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template آماده می‌کند.

**Context Variables برای Generic Template**:
- `page_title`: `_('Stocktaking Records')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `create_url`: `reverse_lazy('inventory:stocktaking_record_create')`
- `create_button_text`: `_('Create Stocktaking Record')`
- `show_actions`: `True`

**Context Variables برای Stocktaking Record-Specific Features**:
- `edit_url_name`: `'inventory:stocktaking_record_edit'`
- `delete_url_name`: `'inventory:stocktaking_record_delete'`
- `lock_url_name`: `'inventory:stocktaking_record_lock'`
- `empty_state_title`: `_('No Stocktaking Records Found')`
- `empty_state_message`: `_('Stocktaking records confirm the accuracy of inventory counts.')`
- `empty_state_icon`: `'📋'`

**Context Variables برای Permissions**:
- `can_delete_own`, `can_delete_other`: از `add_delete_permissions_to_context()`
- `user`: کاربر فعلی (برای permission checks در template)

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
- `feature_code`: `'inventory.stocktaking.records'`
- `success_message`: `_('سند نهایی انبارگردانی با موفقیت بروزرسانی شد.')`
- `form_title`: `_('ویرایش سند نهایی انبارگردانی')`
- `list_url_name`: `'inventory:stocktaking_records'`
- `lock_url_name`: `'inventory:stocktaking_record_lock'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.records', 'created_by')`
3. نتیجه فیلتر شده را برمی‌گرداند

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند را ذخیره می‌کند و `created_by` را تنظیم می‌کند اگر تنظیم نشده باشد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `StocktakingRecordForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. بررسی می‌کند که آیا `form.instance.created_by_id` تنظیم شده است یا نه
2. اگر تنظیم نشده باشد، `form.instance.created_by` را به `request.user` تنظیم می‌کند
3. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**Fieldsets**:
- `(_('اطلاعات سند'), ['stocktaking_session_id'])`
- `(_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes'])`
- `(_('وضعیت تایید'), ['approver', 'approval_status', 'approver_notes'])`
- `(_('خلاصه موجودی'), ['final_inventory_value'])`

**URL**: `/inventory/stocktaking/records/<pk>/edit/`

---

### StocktakingRecordDeleteView

**Type**: `InventoryBaseView, BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:stocktaking_records`

**Attributes**:
- `model`: `StocktakingRecord`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:stocktaking_records')`
- `feature_code`: `'inventory.stocktaking.records'`
- `success_message`: `_('سند شمارش موجودی با موفقیت حذف شد.')`
- `owner_field`: `'created_by'`

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از اجازه دادن به حذف.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا `PermissionDenied` exception

**منطق**: مشابه `IssuePermanentDeleteView.dispatch()` با feature code `'inventory.stocktaking.records'`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Stocktaking Record')`
- `confirmation_message`: `_('Do you really want to delete this stocktaking record?')`
- `object_details`: لیست جزئیات record (Document Code, Document Date, Session ID, Created By)
- `cancel_url`: `reverse_lazy('inventory:stocktaking_records')`
- `breadcrumbs`: لیست breadcrumbs برای navigation

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

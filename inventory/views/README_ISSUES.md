# inventory/views/issues.py - Issue Views (Complete Documentation)

**هدف**: Views برای مدیریت حواله‌ها (Issues) در ماژول inventory

این فایل شامل views برای:
- Permanent Issues (حواله‌های دائم)
- Consumption Issues (حواله‌های مصرف)
- Consignment Issues (حواله‌های امانی)
- Warehouse Transfer Issues (حواله‌های انتقال بین انبارها)
- Serial Assignment (اختصاص سریال)

---

## فهرست مطالب

### Permanent Issue Views
- `IssuePermanentListView` - فهرست حواله‌های دائم
- `IssuePermanentDetailView` - نمایش جزئیات حواله دائم
- `IssuePermanentCreateView` - ایجاد حواله دائم جدید
- `IssuePermanentUpdateView` - ویرایش حواله دائم
- `IssuePermanentDeleteView` - حذف حواله دائم
- `IssuePermanentLockView` - قفل کردن حواله دائم

### Consumption Issue Views
- `IssueConsumptionListView` - فهرست حواله‌های مصرف
- `IssueConsumptionDetailView` - نمایش جزئیات حواله مصرف
- `IssueConsumptionCreateView` - ایجاد حواله مصرف جدید
- `IssueConsumptionUpdateView` - ویرایش حواله مصرف
- `IssueConsumptionDeleteView` - حذف حواله مصرف
- `IssueConsumptionLockView` - قفل کردن حواله مصرف

### Consignment Issue Views
- `IssueConsignmentListView` - فهرست حواله‌های امانی
- `IssueConsignmentDetailView` - نمایش جزئیات حواله امانی
- `IssueConsignmentCreateView` - ایجاد حواله امانی جدید
- `IssueConsignmentUpdateView` - ویرایش حواله امانی
- `IssueConsignmentDeleteView` - حذف حواله امانی
- `IssueConsignmentLockView` - قفل کردن حواله امانی

### Warehouse Transfer Issue Views
- `IssueWarehouseTransferListView` - فهرست حواله‌های انتقال بین انبارها
- `IssueWarehouseTransferCreateView` - ایجاد حواله انتقال بین انبارها جدید
- `IssueWarehouseTransferUpdateView` - ویرایش حواله انتقال بین انبارها
- `IssueWarehouseTransferDetailView` - نمایش جزئیات حواله انتقال بین انبارها
- `IssueWarehouseTransferLockView` - قفل کردن حواله انتقال بین انبارها
- `IssueWarehouseTransferUnlockView` - باز کردن قفل حواله انتقال بین انبارها

### Serial Assignment Views
- `IssueLineSerialAssignmentBaseView` - کلاس پایه برای اختصاص سریال
- `IssuePermanentLineSerialAssignmentView` - اختصاص سریال برای حواله دائم
- `IssueConsumptionLineSerialAssignmentView` - اختصاص سریال برای حواله مصرف
- `IssueConsignmentLineSerialAssignmentView` - اختصاص سریال برای حواله امانی

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`, `DocumentLockProtectedMixin`, `DocumentLockView`, `LineFormsetMixin`
- `inventory.views.receipts`: `DocumentDeleteViewBase`, `ReceiptFormMixin`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `inventory.models`: تمام مدل‌های Issue و Line
- `inventory.forms`: تمام form های Issue
- `inventory.services.serials`: `serial_service` برای مدیریت سریال‌ها

---

## Permanent Issue Views

### `IssuePermanentListView`

**توضیح**: فهرست حواله‌های دائم

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/issue_permanent.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/issue_permanent.html` extends `shared/generic/generic_list.html`
  - Overrides: `breadcrumb_extra`, `page_actions`, `before_table` (stats cards), `filter_fields`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `models.IssuePermanent`
- `template_name`: `'inventory/issue_permanent.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `ordering`: `['-id']` (جدیدترین اول)

**Context Variables**:
- `issues`: queryset حواله‌های دائم (paginated)
- `create_url`: `reverse_lazy('inventory:issue_permanent_create')`
- `edit_url_name`: `'inventory:issue_permanent_edit'`
- `delete_url_name`: `'inventory:issue_permanent_delete'`
- `lock_url_name`: `'inventory:issue_permanent_lock'`
- `detail_url_name`: `'inventory:issue_permanent_detail'` (از کد)
- `create_label`: `_('Permanent Issue')`
- `show_warehouse_request`: `True` (نمایش لینک درخواست انبار)
- `warehouse_request_url_name`: `'inventory:warehouse_request_edit'`
- `serial_url_name`: `None`
- `can_delete_own`: `bool` - آیا کاربر می‌تواند حواله‌های خودش را حذف کند (از `add_delete_permissions_to_context()`)
- `can_delete_all`: `bool` - آیا کاربر می‌تواند همه حواله‌ها را حذف کند (از `add_delete_permissions_to_context()`)
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_select_related(self) -> List[str]`

**توضیح**: فیلدهای select_related را برای بهینه‌سازی query برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: `['created_by', 'department_unit', 'warehouse_request']`

---

#### `get_prefetch_related(self) -> List[str]`

**توضیح**: فیلدهای prefetch_related را برای بهینه‌سازی query برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: `['lines__item', 'lines__warehouse']`

---

#### `apply_custom_filters(self, queryset) -> QuerySet`

**توضیح**: فیلترهای posted status و search را اعمال می‌کند.

**پارامترهای ورودی**:
- `queryset`: queryset برای فیلتر کردن

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. ابتدا `super().apply_custom_filters(queryset)` را فراخوانی می‌کند
2. **فیلتر Posted Status**: 
   - اگر `posted=1` باشد، فقط issues با `is_locked=1`
   - اگر `posted=0` باشد، فقط issues با `is_locked=0`
3. **فیلتر Search**: جستجو در `document_code`, `lines__item__name`, `lines__item__item_code`
4. `distinct()` را اعمال می‌کند و queryset را برمی‌گرداند

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Permanent Issues')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}]`

---

#### `get_create_url(self) -> str`

**توضیح**: URL ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_permanent_create')`

---

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Create Permanent Issue')`

---

#### `get_detail_url_name(self) -> str`

**توضیح**: نام URL جزئیات را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_permanent_detail'`

---

#### `get_edit_url_name(self) -> str`

**توضیح**: نام URL ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_permanent_edit'`

---

#### `get_delete_url_name(self) -> str`

**توضیح**: نام URL حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_permanent_delete'`

---

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('No Issues Found')`

---

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Start by creating your first issue document.')`

---

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'📤'`

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query و فیلترها برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related` و فیلترها

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')`
3. `select_related('created_by', 'department_unit', 'warehouse_request')` را اعمال می‌کند (از `get_select_related()`)
4. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند (از `get_prefetch_related()`)
5. فیلترهای custom را با `apply_custom_filters()` اعمال می‌کند
6. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_stats(self) -> Dict[str, int]`

**توضیح**: آمار کلی برای کارت‌های بالای صفحه محاسبه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, int]`: شامل `total`, `posted`, `draft`

**منطق**:
1. اگر `company_id` در session وجود نداشته باشد، stats خالی برمی‌گرداند
2. base queryset را بر اساس `company_id` می‌سازد
3. `total`: تعداد کل issues
4. `posted`: issues با `is_locked=1`
5. `draft`: issues با `is_locked=0`
6. stats را برمی‌گرداند

---

#### `get_stats_labels(self) -> Dict[str, str]`

**توضیح**: برچسب‌های stats را برمی‌گرداند.

**مقدار بازگشتی**:
- `Dict[str, str]`: شامل `{'total': _('Total'), 'posted': _('Posted'), 'draft': _('Draft')}`

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables برای Generic Template**:
- `page_title`: `_('Permanent Issues')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `create_url`: `reverse_lazy('inventory:issue_permanent_create')`
- `create_button_text`: `_('Create Permanent Issue')`
- `show_filters`: `True`
- `print_enabled`: `True`
- `show_actions`: `True`

**Context Variables برای Issue-Specific Features**:
- `create_label`: `_('Permanent Issue')`
- `edit_url_name`: `'inventory:issue_permanent_edit'`
- `delete_url_name`: `'inventory:issue_permanent_delete'`
- `lock_url_name`: `'inventory:issue_permanent_lock'`
- `detail_url_name`: `'inventory:issue_permanent_detail'`
- `show_warehouse_request`: `True`
- `warehouse_request_url_name`: `'inventory:warehouse_request_edit'`
- `empty_state_title`: `_('No Issues Found')`
- `empty_state_message`: `_('Start by creating your first issue document.')`
- `empty_state_icon`: `'📤'`

**Context Variables برای Permissions**:
- `can_delete_own`, `can_delete_other`: از `add_delete_permissions_to_context()` (از `DocumentDeleteViewBase`)

**Context Variables دیگر**:
- `stats`: آمار از `get_stats()` (برای stats cards)
- `search_query`: مقدار فعلی جستجو
- `user`: کاربر فعلی (برای permission checks در template)

**URL**: `/inventory/issues/permanent/`

---

### `IssuePermanentDetailView`

**توضیح**: نمایش جزئیات حواله دائم (فقط خواندنی)

**Type**: `InventoryBaseView, DetailView`

**Template**: `inventory/issue_detail.html`

**Attributes**:
- `model`: `models.IssuePermanent`
- `template_name`: `'inventory/issue_detail.html'`
- `context_object_name`: `'issue'`
- `feature_code`: `'inventory.issues.permanent'`
- `permission_field`: `'created_by'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related`

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. فیلتر بر اساس `company_id` از session (اگر موجود باشد)
3. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')`
4. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
5. `select_related('created_by', 'warehouse_request', 'department_unit')` را اعمال می‌کند
6. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('View Permanent Issue')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Permanent Issues, View

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}, {'label': _('Permanent Issues'), 'url': reverse_lazy('inventory:issue_permanent')}, {'label': _('View'), 'url': None}]` را برمی‌گرداند

---

#### `get_list_url(self) -> str`

**توضیح**: URL لیست حواله‌های دائم را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_permanent')`

---

#### `get_edit_url(self) -> str`

**توضیح**: URL ویرایش حواله را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('inventory:issue_permanent_edit', kwargs={'pk': self.object.pk})`

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `issue`: instance حواله دائم
- `active_module`: `'inventory'`
- `issue_variant`: `'permanent'`
- `detail_title`: از `get_page_title()`
- `info_banner`: لیست خالی برای enable کردن `info_banner_extra` block

**منطق**:
1. context را از `super().get_context_data(**kwargs)` دریافت می‌کند
2. `active_module`, `issue_variant`, `detail_title`, `info_banner` را اضافه می‌کند
3. context را برمی‌گرداند

**URL**: `/inventory/issues/permanent/<pk>/`

---

### `IssuePermanentCreateView`

**توضیح**: ایجاد حواله دائم جدید

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssuePermanentForm`

**Formset**: `forms.IssuePermanentLineFormSet`

**Success URL**: `inventory:issue_permanent`

**Attributes**:
- `model`: `models.IssuePermanent`
- `form_class`: `forms.IssuePermanentForm`
- `formset_class`: `forms.IssuePermanentLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_permanent')`
- `form_title`: `_('ایجاد حواله دائم')`
- `receipt_variant`: `'issue_permanent'`
- `list_url_name`: `'inventory:issue_permanent'`
- `lock_url_name`: `'inventory:issue_permanent_lock'`

**Context Variables** (از `ReceiptFormMixin`):
- `form`: instance فرم `IssuePermanentForm`
- `lines_formset`: instance formset `IssuePermanentLineFormSet`
- `form_title`: `_('ایجاد حواله دائم')`
- `item_types`: لیست انواع کالا برای فیلتر
- `item_categories`: لیست دسته‌های کالا برای فیلتر
- `item_subcategories`: لیست زیردسته‌های کالا برای فیلتر
- `current_item_type`: نوع کالای انتخاب شده (از query parameter)
- `current_category`: دسته کالای انتخاب شده (از query parameter)
- `current_subcategory`: زیردسته کالای انتخاب شده (از query parameter)
- `current_item_search`: عبارت جستجو (از query parameter)
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation پیشرفته ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssuePermanentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. در `transaction.atomic()`:
   - یک instance موقت برای validation formset ایجاد می‌کند (بدون save)
   - formset را با instance موقت validate می‌کند
   - اگر formset نامعتبر باشد، formset را با `instance=None` rebuild می‌کند و response برمی‌گرداند
   - تعداد خطوط معتبر را شمارش می‌کند (خطوطی که `item` دارند، `DELETE` نشده‌اند و خطا ندارند)
   - اگر هیچ خط معتبری وجود ندارد:
     - خطا به formset اضافه می‌کند
     - formset را با `instance=None` rebuild می‌کند
     - response برمی‌گرداند
   - سند را با `BaseCreateView.form_valid()` ذخیره می‌کند (برای skip کردن formset.save() در BaseFormsetCreateView)
   - formset را با instance ذخیره شده rebuild می‌کند
   - اگر formset نامعتبر باشد، سند را حذف می‌کند و response برمی‌گرداند
   - formset را با `_save_line_formset()` ذخیره می‌کند
2. redirect می‌کند

**نکات مهم**:
- Validation قبل از save انجام می‌شود
- اگر هیچ خط معتبری وجود نداشته باشد، سند ایجاد نمی‌شود
- از `BaseCreateView.form_valid()` استفاده می‌کند تا formset.save() را skip کند
- از `transaction.atomic()` استفاده می‌کند تا اطمینان حاصل شود که یا همه چیز ذخیره می‌شود یا هیچ چیز

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**منطق**:
- یک fieldset با عنوان "Document Info" و فیلد `document_code` برمی‌گرداند
- `document_date` به صورت خودکار تولید می‌شود و در template مخفی است

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Create Permanent Issue

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_permanent')}, {'label': _('Create Permanent Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_permanent')`

---

**URL**: `/inventory/issues/permanent/create/`

---

### `IssuePermanentUpdateView`

**توضیح**: ویرایش حواله دائم

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssuePermanentForm`

**Formset**: `forms.IssuePermanentLineFormSet`

**Success URL**: `inventory:issue_permanent`

**Attributes**:
- `model`: `models.IssuePermanent`
- `form_class`: `forms.IssuePermanentForm`
- `formset_class`: `forms.IssuePermanentLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_permanent')`
- `form_title`: `_('ویرایش حواله دائم')`
- `receipt_variant`: `'issue_permanent'`
- `list_url_name`: `'inventory:issue_permanent'`
- `lock_url_name`: `'inventory:issue_permanent_lock'`
- `lock_redirect_url_name`: `'inventory:issue_permanent'`

**Context Variables** (از `ReceiptFormMixin`):
- مشابه `IssuePermanentCreateView` اما با `object` برای ویرایش

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related` و فیلتر permissions

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. queryset را بر اساس permissions با `filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')` فیلتر می‌کند
3. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
4. `select_related('created_by', 'warehouse_request', 'department_unit')` را اعمال می‌کند
5. queryset را برمی‌گرداند

---

#### `get_formset_kwargs(self) -> Dict[str, Any]`

**توضیح**: kwargs برای formset را برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs شامل `company_id` و `request`

**منطق**:
1. kwargs را از `super().get_formset_kwargs()` دریافت می‌کند
2. `company_id` را از instance (اگر موجود باشد) یا session دریافت می‌کند
3. `kwargs['company_id']` و `kwargs['request']` را اضافه می‌کند
4. kwargs را برمی‌گرداند

**نکته**: این متد `company_id` و `request` را به formset پاس می‌دهد تا formset بتواند فیلترهای مناسب را اعمال کند.

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation پیشرفته ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssuePermanentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. در `transaction.atomic()`:
   - سند را با `BaseUpdateView.form_valid()` ذخیره می‌کند (برای skip کردن formset.save() در BaseFormsetUpdateView)
   - formset را با instance ذخیره شده build می‌کند
   - اگر formset نامعتبر باشد، response برمی‌گرداند
   - تعداد خطوط معتبر را شمارش می‌کند (خطوطی که `item` دارند، `DELETE` نشده‌اند و خطا ندارند)
   - اگر هیچ خط معتبری وجود ندارد:
     - خطا به formset اضافه می‌کند
     - response برمی‌گرداند
   - formset را با `_save_line_formset()` ذخیره می‌کند
2. redirect می‌کند

**نکات مهم**:
- از `DocumentLockProtectedMixin` استفاده می‌کند که از ویرایش سند قفل‌شده جلوگیری می‌کند
- از `BaseUpdateView.form_valid()` استفاده می‌کند تا formset.save() را skip کند
- Validation قبل از save انجام می‌شود

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**منطق**:
- مشابه `IssuePermanentCreateView`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Edit Permanent Issue

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_permanent')}, {'label': _('Edit Permanent Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_permanent')`

---

**URL**: `/inventory/issues/permanent/<pk>/edit/`

---

### `IssuePermanentDeleteView`

**توضیح**: حذف حواله دائم

**Type**: `DocumentLockProtectedMixin, InventoryBaseView, BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:issue_permanent`

**Attributes**:
- `model`: `models.IssuePermanent`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:issue_permanent')`
- `feature_code`: `'inventory.issues.permanent'`
- `success_message`: `_('حواله دائم با موفقیت حذف شد.')`
- `lock_redirect_url_name`: `'inventory:issue_permanent'`
- `owner_field`: `'created_by'`

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از اجازه دادن به حذف.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا `PermissionDenied` exception

**منطق**:
1. اگر کاربر superuser باشد، اجازه می‌دهد و `super().dispatch()` را فراخوانی می‌کند
2. object را با `self.get_object()` دریافت می‌کند
3. `company_id` را از session دریافت می‌کند
4. permissions کاربر را با `get_user_feature_permissions()` دریافت می‌کند
5. بررسی می‌کند که آیا کاربر owner است یا نه (`obj.created_by == request.user`)
6. بررسی می‌کند که آیا کاربر `delete_own` permission دارد (اگر owner است) یا `delete_other` permission دارد (اگر owner نیست)
7. اگر permission نداشته باشد، `PermissionDenied` exception می‌اندازد با پیام مناسب:
   - اگر owner است اما `delete_own` ندارد: "شما اجازه حذف اسناد خود را ندارید."
   - اگر owner نیست اما `delete_other` ندارد: "شما اجازه حذف اسناد سایر کاربران را ندارید."
8. اگر permission داشته باشد، `super().dispatch()` را فراخوانی می‌کند

**نکته**: این متد permission checking را قبل از `delete()` انجام می‌دهد تا اطمینان حاصل شود که کاربر فقط می‌تواند اسناد خود را حذف کند (اگر `delete_own` دارد) یا اسناد سایر کاربران را (اگر `delete_other` دارد).

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.issues.permanent'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

---

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Delete Permanent Issue')`

---

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تایید حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Do you really want to delete this permanent issue?')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Permanent Issues, Delete

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}, {'label': _('Permanent Issues'), 'url': reverse_lazy('inventory:issue_permanent')}, {'label': _('Delete'), 'url': None}]` را برمی‌گرداند

---

#### `get_object_details(self) -> List[Dict]`

**توضیح**: جزئیات object را برای نمایش در صفحه تایید حذف برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست dictionaries شامل label و value برای هر فیلد

**منطق**:
- لیستی از dictionaries برمی‌گرداند شامل:
  - `{'label': _('Document Code'), 'value': self.object.document_code}`
  - `{'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'}`
  - `{'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'}`

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_permanent')`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables برای Generic Template**:
- `delete_title`: از `get_delete_title()`
- `confirmation_message`: از `get_confirmation_message()`
- `object_details`: از `get_object_details()`
- `cancel_url`: از `get_cancel_url()`
- `breadcrumbs`: از `get_breadcrumbs()`

**URL**: `/inventory/issues/permanent/<pk>/delete/`

---

### `IssuePermanentLockView`

**توضیح**: قفل کردن حواله دائم با validation سریال

**Type**: `DocumentLockView`

**Model**: `models.IssuePermanent`

**Success URL**: `inventory:issue_permanent`

**Attributes**:
- `model`: `models.IssuePermanent`
- `success_url_name`: `'inventory:issue_permanent'`
- `success_message`: `_('حواله دائم قفل شد و دیگر قابل ویرایش نیست.')`

**متدها**:

#### `before_lock(self, obj: IssuePermanent, request: HttpRequest) -> bool`

**توضیح**: قبل از قفل کردن، سریال‌های تمام خطوط با کالاهای lot-tracked را validate می‌کند.

**پارامترهای ورودی**:
- `obj`: instance `IssuePermanent` برای قفل کردن
- `request`: درخواست HTTP

**مقدار بازگشتی**:
- `bool`: `True` اگر validation موفق باشد، `False` در غیر این صورت

**منطق**:
1. تمام خطوط فعال (`is_enabled=1`) را دریافت می‌کند
2. برای هر خط:
   - اگر کالا `has_lot_tracking == 1` دارد:
     - `quantity` را به عدد صحیح تبدیل می‌کند
     - اگر تبدیل موفق نبود، خطا نمایش می‌دهد و `False` برمی‌گرداند
     - اگر `quantity` عدد صحیح نیست، خطا نمایش می‌دهد و `False` برمی‌گرداند
     - تعداد سریال‌های انتخاب شده را شمارش می‌کند
     - اگر تعداد سریال‌ها با `quantity` برابر نیست، خطا نمایش می‌دهد و `False` برمی‌گرداند
3. اگر همه validation ها موفق باشند، `True` برمی‌گرداند

---

#### `after_lock(self, obj: IssuePermanent, request: HttpRequest) -> None`

**توضیح**: بعد از قفل کردن، سریال‌های تمام خطوط را finalize می‌کند.

**پارامترهای ورودی**:
- `obj`: instance `IssuePermanent` که قفل شده
- `request`: درخواست HTTP

**مقدار بازگشتی**: ندارد

**منطق**:
1. تمام خطوط فعال (`is_enabled=1`) را دریافت می‌کند
2. برای هر خط:
   - `serial_service.finalize_issue_line_serials(line, user=request.user)` را فراخوانی می‌کند
   - اگر `SerialTrackingError` رخ دهد، خطا را نمایش می‌دهد

**URL**: `/inventory/issues/permanent/<pk>/lock/`

---

## Consumption Issue Views

### `IssueConsumptionListView`

**توضیح**: فهرست حواله‌های مصرف

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/issue_consumption.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/issue_consumption.html` extends `shared/generic/generic_list.html`
  - Overrides: `breadcrumb_extra`, `page_actions`, `before_table` (stats cards), `filter_fields`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `models.IssueConsumption`
- `template_name`: `'inventory/issue_consumption.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `ordering`: `['-id']` (جدیدترین اول)

**متدها**:

#### `get_select_related(self) -> List[str]`

**توضیح**: فیلدهای select_related را برای بهینه‌سازی query برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: `['created_by', 'department_unit']`

---

#### `get_prefetch_related(self) -> List[str]`

**توضیح**: فیلدهای prefetch_related را برای بهینه‌سازی query برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: `['lines__item', 'lines__warehouse']`

---

#### `apply_custom_filters(self, queryset) -> QuerySet`

**توضیح**: فیلترهای posted status و search را اعمال می‌کند.

**پارامترهای ورودی**:
- `queryset`: queryset برای فیلتر کردن

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**: مشابه `IssuePermanentListView.apply_custom_filters()`

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Consumption Issues')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}]`

---

#### `get_create_url(self) -> str`

**توضیح**: URL ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consumption_create')`

---

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Create Consumption Issue')`

---

#### `get_detail_url_name(self) -> str`

**توضیح**: نام URL جزئیات را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_consumption_detail'`

---

#### `get_edit_url_name(self) -> str`

**توضیح**: نام URL ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_consumption_edit'`

---

#### `get_delete_url_name(self) -> str`

**توضیح**: نام URL حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_consumption_delete'`

---

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('No Issues Found')`

---

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Start by creating your first consumption issue document.')`

---

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'📤'`

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query و فیلترها برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related` و فیلترها

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')`
3. `select_related('created_by', 'department_unit')` را اعمال می‌کند (از `get_select_related()`)
4. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند (از `get_prefetch_related()`)
5. فیلترهای custom را با `apply_custom_filters()` اعمال می‌کند
6. queryset را برمی‌گرداند

---

#### `get_stats(self) -> Dict[str, int]`

**توضیح**: آمار کلی برای کارت‌های بالای صفحه محاسبه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, int]`: شامل `total`, `posted`, `draft`

**منطق**: مشابه `IssuePermanentListView.get_stats()` اما با model `IssueConsumption`

---

#### `get_stats_labels(self) -> Dict[str, str]`

**توضیح**: برچسب‌های stats را برمی‌گرداند.

**مقدار بازگشتی**:
- `Dict[str, str]`: شامل `{'total': _('Total'), 'posted': _('Posted'), 'draft': _('Draft')}`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template آماده می‌کند.

**Context Variables برای Generic Template**:
- `page_title`: `_('Consumption Issues')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `create_url`: `reverse_lazy('inventory:issue_consumption_create')`
- `create_button_text`: `_('Create Consumption Issue')`
- `show_filters`: `True`
- `print_enabled`: `True`
- `show_actions`: `True`

**Context Variables برای Issue-Specific Features**:
- `create_label`: `_('Consumption Issue')`
- `edit_url_name`: `'inventory:issue_consumption_edit'`
- `delete_url_name`: `'inventory:issue_consumption_delete'`
- `lock_url_name`: `'inventory:issue_consumption_lock'`
- `detail_url_name`: `'inventory:issue_consumption_detail'`
- `empty_state_title`: `_('No Issues Found')`
- `empty_state_message`: `_('Start by creating your first issue document.')`
- `empty_state_icon`: `'📤'`

**Context Variables برای Permissions**:
- `can_delete_own`, `can_delete_other`: از `add_delete_permissions_to_context()`

**Context Variables دیگر**:
- `stats`: آمار از `get_stats()` (برای stats cards)
- `search_query`: مقدار فعلی جستجو
- `user`: کاربر فعلی (برای permission checks در template)

**URL**: `/inventory/issues/consumption/`

---

### `IssueConsumptionDetailView`

**توضیح**: نمایش جزئیات حواله مصرف (فقط خواندنی)

**Type**: `InventoryBaseView, DetailView`

**Template**: `inventory/issue_detail.html`

**Attributes**:
- `model`: `models.IssueConsumption`
- `template_name`: `'inventory/issue_detail.html'`
- `context_object_name`: `'issue'`
- `feature_code`: `'inventory.issues.consumption'`
- `permission_field`: `'created_by'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query برمی‌گرداند.

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. فیلتر بر اساس `company_id` از session (اگر موجود باشد)
3. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')`
4. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
5. `select_related('created_by', 'department_unit')` را اعمال می‌کند
6. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('View Consumption Issue')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Consumption Issues, View

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}, {'label': _('Consumption Issues'), 'url': reverse_lazy('inventory:issue_consumption')}, {'label': _('View'), 'url': None}]` را برمی‌گرداند

---

#### `get_list_url(self) -> str`

**توضیح**: URL لیست حواله‌های مصرف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consumption')`

---

#### `get_edit_url(self) -> str`

**توضیح**: URL ویرایش حواله را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('inventory:issue_consumption_edit', kwargs={'pk': self.object.pk})`

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `issue`: instance حواله مصرف
- `active_module`: `'inventory'`
- `issue_variant`: `'consumption'`
- `detail_title`: از `get_page_title()`
- `info_banner`: لیست خالی برای enable کردن `info_banner_extra` block

**منطق**:
1. context را از `super().get_context_data(**kwargs)` دریافت می‌کند
2. `active_module`, `issue_variant`, `detail_title`, `info_banner` را اضافه می‌کند
3. context را برمی‌گرداند

**URL**: `/inventory/issues/consumption/<pk>/`

---

### `IssueConsumptionCreateView`

**توضیح**: ایجاد حواله مصرف جدید

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssueConsumptionForm`

**Formset**: `forms.IssueConsumptionLineFormSet`

**Success URL**: `inventory:issue_consumption`

**Attributes**:
- `model`: `models.IssueConsumption`
- `form_class`: `forms.IssueConsumptionForm`
- `formset_class`: `forms.IssueConsumptionLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_consumption')`
- `form_title`: `_('ایجاد حواله مصرف')`
- `receipt_variant`: `'issue_consumption'`
- `list_url_name`: `'inventory:issue_consumption'`
- `lock_url_name`: `'inventory:issue_consumption_lock'`

**Context Variables** (از `ReceiptFormMixin`):
- مشابه `IssuePermanentCreateView`

**متدها**:

#### `form_invalid(self, form) -> HttpResponse`

**توضیح**: در صورت نامعتبر بودن form، response را برمی‌گرداند.

**پارامترهای ورودی**:
- `form`: فرم نامعتبر

**مقدار بازگشتی**:
- `HttpResponse`: response با form و formset

**منطق**:
- `super().form_invalid(form)` را فراخوانی می‌کند

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation پیشرفته ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsumptionForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. در `transaction.atomic()`:
   - یک instance موقت برای validation formset ایجاد می‌کند (بدون save)
   - formset را با instance موقت validate می‌کند
   - اگر formset نامعتبر باشد، formset را با `instance=None` rebuild می‌کند و response برمی‌گرداند
   - تعداد خطوط معتبر را شمارش می‌کند (خطوطی که `item` دارند، `DELETE` نشده‌اند و خطا ندارند)
   - اگر هیچ خط معتبری وجود ندارد:
     - خطا به form اضافه می‌کند
     - formset را با `instance=None` rebuild می‌کند
     - response برمی‌گرداند
   - سند را با `BaseCreateView.form_valid()` ذخیره می‌کند (برای skip کردن formset.save() در BaseFormsetCreateView)
   - formset را با instance ذخیره شده rebuild می‌کند
   - اگر formset نامعتبر باشد، سند را حذف می‌کند و response برمی‌گرداند
   - formset را با `_save_line_formset()` ذخیره می‌کند
2. redirect می‌کند

**نکات مهم**:
- Validation قبل از save انجام می‌شود
- اگر هیچ خط معتبری وجود نداشته باشد، سند ایجاد نمی‌شود
- از `BaseCreateView.form_valid()` استفاده می‌کند تا formset.save() را skip کند
- از `transaction.atomic()` استفاده می‌کند تا اطمینان حاصل شود که یا همه چیز ذخیره می‌شود یا هیچ چیز

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**منطق**:
- مشابه `IssuePermanentCreateView`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Create Consumption Issue

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consumption')}, {'label': _('Create Consumption Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consumption')`

---

**URL**: `/inventory/issues/consumption/create/`

---

### `IssueConsumptionUpdateView`

**توضیح**: ویرایش حواله مصرف

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssueConsumptionForm`

**Formset**: `forms.IssueConsumptionLineFormSet`

**Success URL**: `inventory:issue_consumption`

**Attributes**:
- `model`: `models.IssueConsumption`
- `form_class`: `forms.IssueConsumptionForm`
- `formset_class`: `forms.IssueConsumptionLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_consumption')`
- `form_title`: `_('ویرایش حواله مصرف')`
- `receipt_variant`: `'issue_consumption'`
- `list_url_name`: `'inventory:issue_consumption'`
- `lock_url_name`: `'inventory:issue_consumption_lock'`
- `lock_redirect_url_name`: `'inventory:issue_consumption'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related` و فیلتر permissions

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. queryset را بر اساس permissions با `filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')` فیلتر می‌کند
3. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
4. `select_related('created_by', 'department_unit')` را اعمال می‌کند
5. queryset را برمی‌گرداند

---

#### `get_formset_kwargs(self) -> Dict[str, Any]`

**توضیح**: kwargs برای formset را برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs شامل `company_id` و `request`

**منطق**: مشابه `IssuePermanentUpdateView.get_formset_kwargs()` اما با feature code `'inventory.issues.consumption'`

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsumptionForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. در `transaction.atomic()`:
   - سند را با `BaseUpdateView.form_valid()` ذخیره می‌کند (برای skip کردن formset.save() در BaseFormsetUpdateView)
   - formset را با instance ذخیره شده build می‌کند
   - اگر formset نامعتبر باشد، response برمی‌گرداند
   - formset را با `_save_line_formset()` ذخیره می‌کند
2. redirect می‌کند

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Edit Consumption Issue

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consumption')}, {'label': _('Edit Consumption Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consumption')`

---

**URL**: `/inventory/issues/consumption/<pk>/edit/`

---

### `IssueConsumptionDeleteView`

**توضیح**: حذف حواله مصرف

**Type**: `DocumentLockProtectedMixin, InventoryBaseView, BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:issue_consumption`

**Attributes**:
- `model`: `models.IssueConsumption`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:issue_consumption')`
- `feature_code`: `'inventory.issues.consumption'`
- `success_message`: `_('حواله مصرفی با موفقیت حذف شد.')`
- `lock_redirect_url_name`: `'inventory:issue_consumption'`
- `owner_field`: `'created_by'`

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از اجازه دادن به حذف.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا `PermissionDenied` exception

**منطق**: مشابه `IssuePermanentDeleteView.dispatch()`

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**: مشابه `IssuePermanentDeleteView.get_queryset()` با feature code `'inventory.issues.consumption'`

---

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Delete Consumption Issue')`

---

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تایید حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Do you really want to delete this consumption issue?')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Consumption Issues, Delete

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}, {'label': _('Consumption Issues'), 'url': reverse_lazy('inventory:issue_consumption')}, {'label': _('Delete'), 'url': None}]` را برمی‌گرداند

---

#### `get_object_details(self) -> List[Dict]`

**توضیح**: جزئیات object را برای نمایش در صفحه تایید حذف برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست dictionaries شامل label و value برای هر فیلد

**منطق**:
- لیستی از dictionaries برمی‌گرداند شامل:
  - `{'label': _('Document Code'), 'value': self.object.document_code}`
  - `{'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'}`
  - `{'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'}`

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consumption')`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables برای Generic Template**:
- `delete_title`: از `get_delete_title()`
- `confirmation_message`: از `get_confirmation_message()`
- `object_details`: از `get_object_details()`
- `cancel_url`: از `get_cancel_url()`
- `breadcrumbs`: از `get_breadcrumbs()`

**URL**: `/inventory/issues/consumption/<pk>/delete/`

---

### `IssueConsumptionLockView`

**توضیح**: قفل کردن حواله مصرف با validation سریال

**Type**: `DocumentLockView`

**Model**: `models.IssueConsumption`

**Success URL**: `inventory:issue_consumption`

**Attributes**:
- `model`: `models.IssueConsumption`
- `success_url_name`: `'inventory:issue_consumption'`
- `success_message`: `_('حواله مصرفی قفل شد و دیگر قابل ویرایش نیست.')`

**متدها**:

#### `before_lock(self, obj: IssueConsumption, request: HttpRequest) -> bool`

**توضیح**: قبل از قفل کردن، سریال‌های تمام خطوط با کالاهای lot-tracked را validate می‌کند.

**پارامترهای ورودی**:
- `obj`: instance `IssueConsumption` برای قفل کردن
- `request`: درخواست HTTP

**مقدار بازگشتی**:
- `bool`: `True` اگر validation موفق باشد، `False` در غیر این صورت

**منطق**:
- مشابه `IssuePermanentLockView.before_lock()`

---

#### `after_lock(self, obj: IssueConsumption, request: HttpRequest) -> None`

**توضیح**: بعد از قفل کردن، سریال‌های تمام خطوط را finalize می‌کند و status را به `CONSUMED` تغییر می‌دهد.

**پارامترهای ورودی**:
- `obj`: instance `IssueConsumption` که قفل شده
- `request`: درخواست HTTP

**مقدار بازگشتی**: ندارد

**منطق**:
- مشابه `IssuePermanentLockView.after_lock()` اما سریال‌ها به status `CONSUMED` تغییر می‌کنند

**URL**: `/inventory/issues/consumption/<pk>/lock/`

---

## Consignment Issue Views

### `IssueConsignmentListView`

**توضیح**: فهرست حواله‌های امانی

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/issue_consignment.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/issue_consignment.html` extends `shared/generic/generic_list.html`
  - Overrides: `breadcrumb_extra`, `page_actions`, `before_table` (stats cards), `filter_fields`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `models.IssueConsignment`
- `template_name`: `'inventory/issue_consignment.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `ordering`: `['-id']` (جدیدترین اول)

**متدها**:

#### `get_select_related(self) -> List[str]`

**توضیح**: فیلدهای select_related را برای بهینه‌سازی query برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: `['created_by', 'department_unit']`

---

#### `get_prefetch_related(self) -> List[str]`

**توضیح**: فیلدهای prefetch_related را برای بهینه‌سازی query برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: `['lines__item', 'lines__warehouse', 'lines__supplier']`

**نکته**: شامل `lines__supplier` است که مخصوص consignment issues است.

---

#### `apply_custom_filters(self, queryset) -> QuerySet`

**توضیح**: فیلترهای posted status و search را اعمال می‌کند.

**پارامترهای ورودی**:
- `queryset`: queryset برای فیلتر کردن

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**: مشابه `IssuePermanentListView.apply_custom_filters()`

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Consignment Issues')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}]`

---

#### `get_create_url(self) -> str`

**توضیح**: URL ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consignment_create')`

---

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Create Consignment Issue')`

---

#### `get_detail_url_name(self) -> str`

**توضیح**: نام URL جزئیات را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_consignment_detail'`

---

#### `get_edit_url_name(self) -> str`

**توضیح**: نام URL ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_consignment_edit'`

---

#### `get_delete_url_name(self) -> str`

**توضیح**: نام URL حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_consignment_delete'`

---

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('No Issues Found')`

---

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Start by creating your first consignment issue document.')`

---

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'📤'`

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query و فیلترها برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related` و فیلترها

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')`
3. `select_related('created_by', 'department_unit')` را اعمال می‌کند (از `get_select_related()`)
4. `prefetch_related('lines__item', 'lines__warehouse', 'lines__supplier')` را اعمال می‌کند (از `get_prefetch_related()`)
5. فیلترهای custom را با `apply_custom_filters()` اعمال می‌کند
6. queryset را برمی‌گرداند

---

#### `get_stats(self) -> Dict[str, int]`

**توضیح**: آمار کلی برای کارت‌های بالای صفحه محاسبه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, int]`: شامل `total`, `posted`, `draft`

**منطق**: مشابه `IssuePermanentListView.get_stats()` اما با model `IssueConsignment`

---

#### `get_stats_labels(self) -> Dict[str, str]`

**توضیح**: برچسب‌های stats را برمی‌گرداند.

**مقدار بازگشتی**:
- `Dict[str, str]`: شامل `{'total': _('Total'), 'posted': _('Posted'), 'draft': _('Draft')}`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template آماده می‌کند.

**Context Variables برای Generic Template**:
- `page_title`: `_('Consignment Issues')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `create_url`: `reverse_lazy('inventory:issue_consignment_create')`
- `create_button_text`: `_('Create Consignment Issue')`
- `show_filters`: `True`
- `print_enabled`: `True`
- `show_actions`: `True`

**Context Variables برای Issue-Specific Features**:
- `create_label`: `_('Consignment Issue')`
- `edit_url_name`: `'inventory:issue_consignment_edit'`
- `delete_url_name`: `'inventory:issue_consignment_delete'`
- `lock_url_name`: `'inventory:issue_consignment_lock'`
- `detail_url_name`: `'inventory:issue_consignment_detail'`
- `empty_state_title`: `_('No Issues Found')`
- `empty_state_message`: `_('Start by creating your first issue document.')`
- `empty_state_icon`: `'📤'`

**Context Variables برای Permissions**:
- `can_delete_own`, `can_delete_other`: از `add_delete_permissions_to_context()`

**Context Variables دیگر**:
- `stats`: آمار از `get_stats()` (برای stats cards)
- `search_query`: مقدار فعلی جستجو
- `user`: کاربر فعلی (برای permission checks در template)

**URL**: `/inventory/issues/consignment/`

---

### `IssueConsignmentDetailView`

**توضیح**: نمایش جزئیات حواله امانی (فقط خواندنی)

**Type**: `InventoryBaseView, DetailView`

**Template**: `inventory/issue_detail.html`

**Attributes**:
- `model`: `models.IssueConsignment`
- `template_name`: `'inventory/issue_detail.html'`
- `context_object_name`: `'issue'`
- `feature_code`: `'inventory.issues.consignment'`
- `permission_field`: `'created_by'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query برمی‌گرداند.

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. فیلتر بر اساس `company_id` از session (اگر موجود باشد)
3. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')`
4. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
5. `select_related('created_by', 'department_unit')` را اعمال می‌کند
6. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('View Consignment Issue')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Consignment Issues, View

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}, {'label': _('Consignment Issues'), 'url': reverse_lazy('inventory:issue_consignment')}, {'label': _('View'), 'url': None}]` را برمی‌گرداند

---

#### `get_list_url(self) -> str`

**توضیح**: URL لیست حواله‌های امانی را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consignment')`

---

#### `get_edit_url(self) -> str`

**توضیح**: URL ویرایش حواله را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse('inventory:issue_consignment_edit', kwargs={'pk': self.object.pk})`

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `issue`: instance حواله امانی
- `active_module`: `'inventory'`
- `issue_variant`: `'consignment'`
- `detail_title`: از `get_page_title()`
- `info_banner`: لیست خالی برای enable کردن `info_banner_extra` block

**منطق**:
1. context را از `super().get_context_data(**kwargs)` دریافت می‌کند
2. `active_module`, `issue_variant`, `detail_title`, `info_banner` را اضافه می‌کند
3. context را برمی‌گرداند

**URL**: `/inventory/issues/consignment/<pk>/`

---

### `IssueConsignmentCreateView`

**توضیح**: ایجاد حواله امانی جدید

**Type**: `LineFormsetMixin, ReceiptFormMixin, CreateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssueConsignmentForm`

**Formset**: `forms.IssueConsignmentLineFormSet`

**Success URL**: `inventory:issue_consignment`

**Attributes**:
- `model`: `models.IssueConsignment`
- `form_class`: `forms.IssueConsignmentForm`
- `formset_class`: `forms.IssueConsignmentLineFormSet`
- `success_url`: `reverse_lazy('inventory:issue_consignment')`
- `form_title`: `_('ایجاد حواله امانی')`
- `receipt_variant`: `'issue_consignment'`
- `list_url_name`: `'inventory:issue_consignment'`
- `lock_url_name`: `'inventory:issue_consignment_lock'`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation پیشرفته ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsignmentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**: مشابه `IssuePermanentCreateView.form_valid()`

**نکات مهم**:
- Validation قبل از save انجام می‌شود
- اگر هیچ خط معتبری وجود نداشته باشد، سند ایجاد نمی‌شود
- از `BaseCreateView.form_valid()` استفاده می‌کند تا formset.save() را skip کند
- از `transaction.atomic()` استفاده می‌کند تا اطمینان حاصل شود که یا همه چیز ذخیره می‌شود یا هیچ چیز

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**منطق**:
- مشابه `IssuePermanentCreateView`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Create Consignment Issue

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consignment')}, {'label': _('Create Consignment Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consignment')`

---

**URL**: `/inventory/issues/consignment/create/`

---

### `IssueConsignmentUpdateView`

**توضیح**: ویرایش حواله امانی

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssueConsignmentForm`

**Formset**: `forms.IssueConsignmentLineFormSet`

**Success URL**: `inventory:issue_consignment`

**Attributes**:
- مشابه `IssueConsumptionUpdateView` اما برای consignment

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related` و فیلتر permissions

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. queryset را بر اساس permissions با `filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')` فیلتر می‌کند
3. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
4. `select_related('created_by', 'department_unit')` را اعمال می‌کند
5. queryset را برمی‌گرداند

---

#### `get_formset_kwargs(self) -> Dict[str, Any]`

**توضیح**: kwargs برای formset را برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs شامل `company_id` و `request`

**منطق**: مشابه `IssuePermanentUpdateView.get_formset_kwargs()` اما با feature code `'inventory.issues.consignment'`

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsignmentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. در `transaction.atomic()`:
   - سند را با `BaseUpdateView.form_valid()` ذخیره می‌کند (برای skip کردن formset.save() در BaseFormsetUpdateView)
   - formset را با instance ذخیره شده build می‌کند
   - اگر formset نامعتبر باشد، response برمی‌گرداند
   - formset را با `_save_line_formset()` ذخیره می‌کند
2. redirect می‌کند

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Edit Consignment Issue

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consignment')}, {'label': _('Edit Consignment Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consignment')`

---

**URL**: `/inventory/issues/consignment/<pk>/edit/`

---

### `IssueConsignmentDeleteView`

**توضیح**: حذف حواله امانی

**Type**: `DocumentLockProtectedMixin, InventoryBaseView, BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:issue_consignment`

**Attributes**:
- `model`: `models.IssueConsignment`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:issue_consignment')`
- `feature_code`: `'inventory.issues.consignment'`
- `success_message`: `_('حواله امانی با موفقیت حذف شد.')`
- `lock_redirect_url_name`: `'inventory:issue_consignment'`
- `owner_field`: `'created_by'`

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از اجازه دادن به حذف.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا `PermissionDenied` exception

**منطق**: مشابه `IssuePermanentDeleteView.dispatch()`

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**: مشابه `IssuePermanentDeleteView.get_queryset()` با feature code `'inventory.issues.consignment'`

---

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Delete Consignment Issue')`

---

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تایید حذف را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Do you really want to delete this consignment issue?')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برای navigation برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs شامل Inventory, Issues, Consignment Issues, Delete

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}, {'label': _('Consignment Issues'), 'url': reverse_lazy('inventory:issue_consignment')}, {'label': _('Delete'), 'url': None}]` را برمی‌گرداند

---

#### `get_object_details(self) -> List[Dict]`

**توضیح**: جزئیات object را برای نمایش در صفحه تایید حذف برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست dictionaries شامل label و value برای هر فیلد

**منطق**:
- لیستی از dictionaries برمی‌گرداند شامل:
  - `{'label': _('Document Code'), 'value': self.object.document_code}`
  - `{'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'}`
  - `{'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'}`

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو (بازگشت به لیست) را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_consignment')`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables برای Generic Template**:
- `delete_title`: از `get_delete_title()`
- `confirmation_message`: از `get_confirmation_message()`
- `object_details`: از `get_object_details()`
- `cancel_url`: از `get_cancel_url()`
- `breadcrumbs`: از `get_breadcrumbs()`

**URL**: `/inventory/issues/consignment/<pk>/delete/`

---

### `IssueConsignmentLockView`

**توضیح**: قفل کردن حواله امانی با validation سریال

**Type**: `DocumentLockView`

**Model**: `models.IssueConsignment`

**Success URL**: `inventory:issue_consignment`

**Attributes**:
- `model`: `models.IssueConsignment`
- `success_url_name`: `'inventory:issue_consignment'`
- `success_message`: `_('حواله امانی قفل شد و دیگر قابل ویرایش نیست.')`

**متدها**:

#### `before_lock(self, obj: IssueConsignment, request: HttpRequest) -> bool`

**توضیح**: قبل از قفل کردن، سریال‌های تمام خطوط با کالاهای lot-tracked را validate می‌کند.

**پارامترهای ورودی**:
- `obj`: instance `IssueConsignment` برای قفل کردن
- `request`: درخواست HTTP

**مقدار بازگشتی**:
- `bool`: `True` اگر validation موفق باشد، `False` در غیر این صورت

**منطق**:
- مشابه `IssuePermanentLockView.before_lock()`

---

#### `after_lock(self, obj: IssueConsignment, request: HttpRequest) -> None`

**توضیح**: بعد از قفل کردن، سریال‌های تمام خطوط را finalize می‌کند.

**پارامترهای ورودی**:
- `obj`: instance `IssueConsignment` که قفل شده
- `request`: درخواست HTTP

**مقدار بازگشتی**: ندارد

**منطق**:
- مشابه `IssuePermanentLockView.after_lock()`

**URL**: `/inventory/issues/consignment/<pk>/lock/`

---

## Issue Line Serial Assignment Views

### `IssueLineSerialAssignmentBaseView`

**توضیح**: کلاس پایه برای اختصاص سریال به یک ردیف حواله

**Type**: `FeaturePermissionRequiredMixin, FormView`

**Template**: `inventory/issue_serial_assignment.html`

**Form**: `forms.IssueLineSerialAssignmentForm`

**Attributes**:
- `template_name`: `'inventory/issue_serial_assignment.html'`
- `form_class`: `forms.IssueLineSerialAssignmentForm`
- `line_model`: `None` (باید در subclass تنظیم شود)
- `document_model`: `None` (باید در subclass تنظیم شود)
- `feature_code`: `None` (باید در subclass تنظیم شود)
- `serial_url_name`: `''` (باید در subclass تنظیم شود)
- `list_url_name`: `''` (باید در subclass تنظیم شود)
- `edit_url_name`: `''` (باید در subclass تنظیم شود)
- `lock_url_name`: `''` (باید در subclass تنظیم شود)

**Context Variables**:
- `line`: instance خط حواله
- `document`: instance سند حواله
- `form`: instance فرم `IssueLineSerialAssignmentForm`
- `list_url`: URL لیست حواله‌ها
- `edit_url`: URL ویرایش سند
- `lock_url`: URL قفل کردن سند (یا `None`)
- `required_serials`: تعداد سریال‌های مورد نیاز (از `quantity` به عدد صحیح)
- `selected_serials_count`: تعداد سریال‌های انتخاب شده
- `available_serials_count`: تعداد سریال‌های موجود
- `available_serials`: queryset سریال‌های موجود

**متدها**:

#### `dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse`

**توضیح**: قبل از dispatch، بررسی می‌کند که کالا نیاز به سریال دارد و سند قفل نشده است.

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response یا redirect

**منطق**:
1. `self.document` و `self.line` را با `get_document()` و `get_line()` دریافت می‌کند
2. اگر کالا `has_lot_tracking != 1` دارد:
   - پیام info نمایش می‌دهد
   - به صفحه ویرایش سند redirect می‌کند
3. اگر سند قفل شده است (`is_locked == 1`):
   - پیام info نمایش می‌دهد
   - به صفحه لیست redirect می‌کند
4. `super().dispatch()` را فراخوانی می‌کند

---

#### `get_document(self) -> Model`

**توضیح**: instance سند را از database دریافت می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Model`: instance سند (از `document_model`)

**منطق**:
1. queryset را از `document_model.objects.all()` دریافت می‌کند
2. اگر `company_id` در session وجود دارد و مدل `company_id` دارد، queryset را فیلتر می‌کند
3. با `get_object_or_404()` instance را از `kwargs['pk']` دریافت می‌کند
4. instance را برمی‌گرداند

---

#### `get_line(self) -> Model`

**توضیح**: instance خط را از database دریافت می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Model`: instance خط (از `line_model`)

**منطق**:
1. queryset را از `line_model.objects.filter(document=self.document)` دریافت می‌کند
2. اگر `company_id` در session وجود دارد و مدل `company_id` دارد، queryset را فیلتر می‌کند
3. با `get_object_or_404()` instance را از `kwargs['line_id']` دریافت می‌کند
4. instance را برمی‌گرداند

---

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `line` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `line` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `kwargs['line'] = self.line` را اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: اختصاص سریال‌ها را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueLineSerialAssignmentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `get_success_url()`

**منطق**:
1. `form.save(user=self.request.user)` را فراخوانی می‌کند
2. پیام موفقیت را نمایش می‌دهد
3. redirect به `get_success_url()` می‌کند

---

#### `get_success_url(self) -> str`

**توضیح**: URL موفقیت را برمی‌گرداند (صفحه ویرایش سند).

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `str`: URL صفحه ویرایش سند

**منطق**:
- `reverse(self.edit_url_name, args=[self.document.pk])` را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**منطق**:
1. context را از `super().get_context_data(**kwargs)` دریافت می‌کند
2. متغیرهای زیر را اضافه می‌کند:
   - `line`: `self.line` - instance خط حواله
   - `document`: `self.document` - instance سند حواله
   - `list_url`: `reverse(self.list_url_name)` - URL لیست
   - `edit_url`: `reverse(self.edit_url_name, args=[self.document.pk])` - URL ویرایش
   - `lock_url`: `reverse(self.lock_url_name, args=[self.document.pk])` اگر `lock_url_name` وجود دارد، در غیر این صورت `None`
   - `required_serials`: تعداد سریال‌های مورد نیاز (از `int(Decimal(self.line.quantity))` یا `None` در صورت خطا)
   - `selected_serials_count`: `self.line.serials.count()` - تعداد سریال‌های انتخاب شده
   - `available_serials_count`: تعداد سریال‌های موجود در queryset فرم
   - `available_serials`: queryset سریال‌های موجود
3. context را برمی‌گرداند

**Context Variables اضافه شده**:
- `line`: instance خط حواله
- `document`: instance سند حواله
- `form`: instance فرم `IssueLineSerialAssignmentForm`
- `list_url`: URL لیست حواله‌ها
- `edit_url`: URL ویرایش سند
- `lock_url`: URL قفل کردن سند (یا `None`)
- `required_serials`: تعداد سریال‌های مورد نیاز (از `quantity` به عدد صحیح)
- `selected_serials_count`: تعداد سریال‌های انتخاب شده
- `available_serials_count`: تعداد سریال‌های موجود
- `available_serials`: queryset سریال‌های موجود

---

### `IssuePermanentLineSerialAssignmentView`

**توضیح**: اختصاص سریال برای ردیف حواله دائم

**Type**: `IssueLineSerialAssignmentBaseView`

**Attributes**:
- `line_model`: `models.IssuePermanentLine`
- `document_model`: `models.IssuePermanent`
- `feature_code`: `'inventory.issues.permanent'`
- `serial_url_name`: `'inventory:issue_permanent_line_serials'`
- `list_url_name`: `'inventory:issue_permanent'`
- `edit_url_name`: `'inventory:issue_permanent_edit'`
- `lock_url_name`: `'inventory:issue_permanent_lock'`

**URL**: `/inventory/issues/permanent/line/<line_id>/assign-serials/`

---

### `IssueConsumptionLineSerialAssignmentView`

**توضیح**: اختصاص سریال برای ردیف حواله مصرف

**Type**: `IssueLineSerialAssignmentBaseView`

**Attributes**:
- `line_model`: `models.IssueConsumptionLine`
- `document_model`: `models.IssueConsumption`
- `feature_code`: `'inventory.issues.consumption'`
- `serial_url_name`: `'inventory:issue_consumption_line_serials'`
- `list_url_name`: `'inventory:issue_consumption'`
- `edit_url_name`: `'inventory:issue_consumption_edit'`
- `lock_url_name`: `'inventory:issue_consumption_lock'`

**URL**: `/inventory/issues/consumption/line/<line_id>/assign-serials/`

---

### `IssueConsignmentLineSerialAssignmentView`

**توضیح**: اختصاص سریال برای ردیف حواله امانی

**Type**: `IssueLineSerialAssignmentBaseView`

**Attributes**:
- `line_model`: `models.IssueConsignmentLine`
- `document_model`: `models.IssueConsignment`
- `feature_code`: `'inventory.issues.consignment'`
- `serial_url_name`: `'inventory:issue_consignment_line_serials'`
- `list_url_name`: `'inventory:issue_consignment'`
- `edit_url_name`: `'inventory:issue_consignment_edit'`
- `lock_url_name`: `'inventory:issue_consignment_lock'`

**URL**: `/inventory/issues/consignment/line/<line_id>/assign-serials/`

---

## Warehouse Transfer Issue Views

### `IssueWarehouseTransferListView`

**توضیح**: فهرست حواله‌های انتقال بین انبارها

**Type**: `InventoryBaseView, BaseDocumentListView`

**Template**: `inventory/issue_warehouse_transfer.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/issue_warehouse_transfer.html` extends `shared/generic/generic_list.html`
  - Overrides: `breadcrumb_extra`, `page_actions`, `before_table` (stats cards), `filter_fields`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `models.IssueWarehouseTransfer`
- `template_name`: `'inventory/issue_warehouse_transfer.html'`
- `feature_code`: `'inventory.issues.warehouse_transfer'`
- `permission_field`: `'created_by'`
- `search_fields`: `['document_code']`
- `default_status_filter`: `False` (status filtering به صورت دستی انجام می‌شود)
- `default_order_by`: `['-id']` (جدیدترین اول)
- `paginate_by`: `50`
- `stats_enabled`: `True`

**متدها**:

#### `get_base_queryset(self) -> QuerySet`

**توضیح**: queryset پایه را با شامل کردن انتقال‌های production برمی‌گرداند.

**مقدار بازگشتی**:
- `QuerySet`: queryset شامل warehouse transfers و production transfers

**منطق**:
1. queryset را از `super().get_base_queryset()` دریافت می‌کند
2. queryset را بر اساس permissions با `filter_queryset_by_permissions(queryset, 'inventory.issues.warehouse_transfer', 'created_by')` فیلتر می‌کند
3. **همیشه انتقال‌های ایجاد شده از `TransferToLine` را شامل می‌کند** (این‌ها بخشی از workflow تولید هستند و باید قابل مشاهده باشند)
4. اگر `company_id` در session وجود دارد:
   - queryset انتقال‌های production را با `production_transfer__isnull=False` و `company_id` فیلتر می‌کند
   - هر دو queryset را با union ترکیب می‌کند (duplicates حذف می‌شوند)
5. queryset را برمی‌گرداند

**نکته مهم**: این view انتقال‌های ایجاد شده از production workflow را همیشه شامل می‌کند، حتی اگر کاربر permission view نداشته باشد.

---

#### `get_select_related(self) -> List[str]`

**توضیح**: select_related objects را برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: لیست فیلدهای select_related

**منطق**:
- `['created_by', 'production_transfer']` را برمی‌گرداند

---

#### `get_prefetch_related(self) -> List[str]`

**توضیح**: prefetch_related objects را برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: لیست فیلدهای prefetch_related

**منطق**:
- `['lines__item', 'lines__source_warehouse', 'lines__destination_warehouse']` را برمی‌گرداند

---

#### `apply_custom_filters(self, queryset) -> QuerySet`

**توضیح**: فیلترهای posted status و search را اعمال می‌کند.

**پارامترهای ورودی**:
- `queryset`: queryset برای فیلتر کردن

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. ابتدا `super().apply_custom_filters(queryset)` را فراخوانی می‌کند
2. **فیلتر Posted Status**: 
   - اگر `posted=1` باشد، فقط issues با `is_locked=1`
   - اگر `posted=0` باشد، فقط issues با `is_locked=0`
3. **فیلتر Search**: جستجو در `document_code`, `lines__item__name`, `lines__item__item_code`
4. `distinct()` را اعمال می‌کند و queryset را برمی‌گرداند

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Warehouse Transfer Issues')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}]` را برمی‌گرداند

---

#### `get_create_url(self) -> str`

**توضیح**: URL ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_warehouse_transfer_create')`

---

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Create Warehouse Transfer Issue')`

---

#### `get_detail_url_name(self) -> str`

**توضیح**: نام URL جزئیات را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_warehouse_transfer_detail'`

---

#### `get_edit_url_name(self) -> str`

**توضیح**: نام URL ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'inventory:issue_warehouse_transfer_edit'`

---

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('No Issues Found')`

---

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('Start by creating your first warehouse transfer issue document.')`

---

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون empty state را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `'📤'`

---

#### `get_stats(self) -> Dict[str, int]`

**توضیح**: آمار کلی برای کارت‌های بالای صفحه محاسبه می‌کند.

**مقدار بازگشتی**:
- `Dict[str, int]`: شامل `total`, `posted`, `draft`

**منطق**: مشابه `IssuePermanentListView.get_stats()` اما با model `IssueWarehouseTransfer`

---

#### `get_stats_labels(self) -> Dict[str, str]`

**توضیح**: برچسب‌های stats را برمی‌گرداند.

**مقدار بازگشتی**:
- `Dict[str, str]`: شامل `{'total': _('Total'), 'posted': _('Posted'), 'draft': _('Draft')}`

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables**:
- `create_label`: `_('Warehouse Transfer Issue')`
- `print_enabled`: `True`
- `delete_url_name`: `None` (حذف هنوز پیاده‌سازی نشده است)

---

**URL**: `/inventory/issues/warehouse-transfer/`

---

### `IssueWarehouseTransferCreateView`

**توضیح**: ایجاد حواله انتقال بین انبارها جدید

**Type**: `LineFormsetMixin, ReceiptFormMixin, BaseDocumentCreateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssueWarehouseTransferForm`

**Formset**: `forms.IssueWarehouseTransferLineFormSet`

**Success URL**: `inventory:issue_warehouse_transfer`

**Attributes**:
- `model`: `models.IssueWarehouseTransfer`
- `form_class`: `forms.IssueWarehouseTransferForm`
- `formset_class`: `forms.IssueWarehouseTransferLineFormSet`
- `formset_prefix`: `'lines'`
- `success_url`: `reverse_lazy('inventory:issue_warehouse_transfer')`
- `feature_code`: `'inventory.issues.warehouse_transfer'`
- `form_title`: `_('ایجاد حواله انتقال بین انبارها')`
- `receipt_variant`: `'issue_warehouse_transfer'`
- `list_url_name`: `'inventory:issue_warehouse_transfer'`
- `lock_url_name`: `'inventory:issue_warehouse_transfer_lock'`
- `success_message`: `_('حواله انتقال بین انبارها با موفقیت ایجاد شد.')`

**Context Variables** (از `ReceiptFormMixin`):
- مشابه سایر Create views

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation پیشرفته ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueWarehouseTransferForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. در `transaction.atomic()`:
   - یک instance موقت برای validation formset ایجاد می‌کند (بدون save)
   - formset را با instance موقت validate می‌کند
   - اگر formset نامعتبر باشد، formset را با `instance=None` rebuild می‌کند و response برمی‌گرداند
   - تعداد خطوط معتبر را شمارش می‌کند (خطوطی که `item` دارند، `DELETE` نشده‌اند و خطا ندارند)
   - اگر هیچ خط معتبری وجود ندارد:
     - خطا به form اضافه می‌کند
     - formset را با `instance=None` rebuild می‌کند
     - response برمی‌گرداند
   - سند را با `BaseCreateView.form_valid()` ذخیره می‌کند (برای skip کردن formset.save() در BaseFormsetCreateView)
   - formset را با instance ذخیره شده rebuild می‌کند
   - اگر formset نامعتبر باشد، سند را حذف می‌کند و response برمی‌گرداند
   - formset را با `_save_line_formset()` ذخیره می‌کند
2. redirect می‌کند

**نکات مهم**:
- Validation قبل از save انجام می‌شود
- اگر هیچ خط معتبری وجود نداشته باشد، سند ایجاد نمی‌شود
- از `BaseCreateView.form_valid()` استفاده می‌کند تا formset.save() را skip کند

---

#### `get_fieldsets(self) -> List[Tuple]`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Tuple]`: لیست tuples شامل (title, fields)

**منطق**:
- `[(_('Document Info'), ['document_code'])]` را برمی‌گرداند
- `document_date` مخفی است و به صورت خودکار تولید می‌شود

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_warehouse_transfer')}, {'label': _('Create Warehouse Transfer Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_warehouse_transfer')`

---

**URL**: `/inventory/issues/warehouse-transfer/create/`

---

### `IssueWarehouseTransferUpdateView`

**توضیح**: ویرایش حواله انتقال بین انبارها

**Type**: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`

**Template**: `inventory/receipt_form.html` (از `ReceiptFormMixin`)

**Form**: `forms.IssueWarehouseTransferForm`

**Formset**: `forms.IssueWarehouseTransferLineFormSet`

**Success URL**: `inventory:issue_warehouse_transfer`

**Attributes**:
- `model`: `models.IssueWarehouseTransfer`
- `form_class`: `forms.IssueWarehouseTransferForm`
- `formset_class`: `forms.IssueWarehouseTransferLineFormSet`
- `formset_prefix`: `'lines'`
- `success_url`: `reverse_lazy('inventory:issue_warehouse_transfer')`
- `feature_code`: `'inventory.issues.warehouse_transfer'`
- `success_message`: `_('حواله انتقال بین انبارها با موفقیت به‌روزرسانی شد.')`
- `form_title`: `_('ویرایش حواله انتقال بین انبارها')`
- `receipt_variant`: `'issue_warehouse_transfer'`
- `list_url_name`: `'inventory:issue_warehouse_transfer'`
- `lock_url_name`: `'inventory:issue_warehouse_transfer_lock'`

**متدها**:

#### `get_formset_kwargs(self) -> Dict[str, Any]`

**توضیح**: kwargs برای formset را برمی‌گرداند.

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs شامل `company_id` و `request`

**منطق**:
1. kwargs را از `super().get_formset_kwargs()` دریافت می‌کند
2. `company_id` را از instance یا session دریافت می‌کند
3. `kwargs['company_id']` و `kwargs['request']` را اضافه می‌کند
4. kwargs را برمی‌گرداند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch و فیلتر permissions برمی‌گرداند.

**مقدار بازگشتی**:
- `QuerySet`: queryset شامل production transfers

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. **شامل انتقال‌های production**: 
   - queryset را بر اساس permissions فیلتر می‌کند
   - انتقال‌های production را با `production_transfer__isnull=False` و `company_id` فیلتر می‌کند
   - هر دو queryset را با union ترکیب می‌کند
3. `prefetch_related('lines__item', 'lines__source_warehouse', 'lines__destination_warehouse')` را اعمال می‌کند
4. `select_related('created_by', 'production_transfer')` را اعمال می‌کند
5. queryset را برمی‌گرداند

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را با validation ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueWarehouseTransferForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. در `transaction.atomic()`:
   - سند را با `BaseUpdateView.form_valid()` ذخیره می‌کند (برای skip کردن formset.save() در BaseFormsetUpdateView)
   - formset را با instance ذخیره شده build می‌کند
   - اگر formset نامعتبر باشد، response برمی‌گرداند
   - تعداد خطوط معتبر را شمارش می‌کند
   - اگر هیچ خط معتبری وجود ندارد:
     - خطا به formset اضافه می‌کند
     - response برمی‌گرداند
   - formset را با `_save_line_formset()` ذخیره می‌کند
2. redirect می‌کند

---

#### `get_fieldsets(self) -> List[Tuple]`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Tuple]`: لیست tuples شامل (title, fields)

**منطق**:
- `[(_('Document Info'), ['document_code'])]` را برمی‌گرداند
- `document_date` مخفی است و به صورت خودکار تولید می‌شود

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_warehouse_transfer')}, {'label': _('Edit Warehouse Transfer Issue'), 'url': None}]` را برمی‌گرداند

---

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_warehouse_transfer')`

---

**URL**: `/inventory/issues/warehouse-transfer/<pk>/edit/`

---

### `IssueWarehouseTransferDetailView`

**توضیح**: نمایش جزئیات حواله انتقال بین انبارها (فقط خواندنی)

**Type**: `InventoryBaseView, BaseDetailView`

**Template**: `inventory/issue_warehouse_transfer_detail.html`

**Attributes**:
- `model`: `models.IssueWarehouseTransfer`
- `template_name`: `'inventory/issue_warehouse_transfer_detail.html'`
- `context_object_name`: `'warehouse_transfer'`
- `feature_code`: `'inventory.issues.warehouse_transfer'`
- `permission_field`: `'created_by'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با فیلتر company و شامل کردن production transfers برمی‌گرداند.

**مقدار بازگشتی**:
- `QuerySet`: queryset شامل production transfers

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. اگر `company_id` در session وجود دارد:
   - queryset را بر اساس permissions فیلتر می‌کند
   - انتقال‌های production را با `production_transfer__isnull=False` و `company_id` فیلتر می‌کند
   - هر دو queryset را با union ترکیب می‌کند
3. در غیر این صورت، queryset خالی برمی‌گرداند
4. `prefetch_related('lines__item', 'lines__source_warehouse', 'lines__destination_warehouse')` را اعمال می‌کند
5. `select_related('created_by', 'production_transfer')` را اعمال می‌کند
6. queryset را برمی‌گرداند

---

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `_('View Warehouse Transfer Issue')`

---

#### `get_breadcrumbs(self) -> List[Dict]`

**توضیح**: breadcrumbs را برمی‌گرداند.

**مقدار بازگشتی**:
- `List[Dict]`: لیست breadcrumbs

**منطق**:
- `[{'label': _('Inventory'), 'url': None}, {'label': _('Issues'), 'url': None}, {'label': _('Warehouse Transfer Issues'), 'url': reverse_lazy('inventory:issue_warehouse_transfer')}, {'label': _('View'), 'url': None}]` را برمی‌گرداند

---

#### `get_list_url(self) -> str`

**توضیح**: URL لیست را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_warehouse_transfer')`

---

#### `get_edit_url(self) -> str`

**توضیح**: URL ویرایش را برمی‌گرداند.

**مقدار بازگشتی**:
- `str`: `reverse_lazy('inventory:issue_warehouse_transfer_edit', kwargs={'pk': self.object.pk})`

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic_detail.html اضافه می‌کند.

**Context Variables اضافه شده**:
- `detail_title`: از `get_page_title()`
- `info_banner`: لیست خالی برای enable کردن `info_banner_extra` block

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `detail_title` و `info_banner`

---

**URL**: `/inventory/issues/warehouse-transfer/<pk>/`

---

### `IssueWarehouseTransferLockView`

**توضیح**: قفل کردن حواله انتقال بین انبارها

**Type**: `DocumentLockView`

**Model**: `models.IssueWarehouseTransfer`

**Success URL**: `inventory:issue_warehouse_transfer`

**Attributes**:
- `model`: `models.IssueWarehouseTransfer`
- `success_url_name`: `'inventory:issue_warehouse_transfer'`
- `success_message`: `_('حواله انتقال بین انبارها قفل شد و دیگر قابل ویرایش نیست.')`

**منطق**:
- مشابه سایر Lock views
- از `DocumentLockView` استفاده می‌کند که lock کردن سند را انجام می‌دهد

**URL**: `/inventory/issues/warehouse-transfer/<pk>/lock/`

---

### `IssueWarehouseTransferUnlockView`

**توضیح**: باز کردن قفل حواله انتقال بین انبارها

**Type**: `DocumentUnlockView`

**Model**: `models.IssueWarehouseTransfer`

**Success URL**: `inventory:issue_warehouse_transfer`

**Attributes**:
- `model`: `models.IssueWarehouseTransfer`
- `success_url_name`: `'inventory:issue_warehouse_transfer'`
- `success_message`: `_('حواله انتقال بین انبارها از قفل خارج شد و قابل ویرایش است.')`
- `feature_code`: `'inventory.issues.warehouse_transfer'`
- `required_action`: `'unlock_own'`

**منطق**:
- از `DocumentUnlockView` استفاده می‌کند که unlock کردن سند را انجام می‌دهد
- نیاز به permission `unlock_own` دارد

**URL**: `/inventory/issues/warehouse-transfer/<pk>/unlock/`

---

## نکات مهم

### 1. Item Filtering and Search
تمام Create/Update views از `ReceiptFormMixin` استفاده می‌کنند که شامل:
- فیلترهای اختیاری بر اساس نوع، دسته، و زیردسته کالا
- جستجوی مستقیم بر اساس نام یا کد کالا (بدون نیاز به فیلتر)
- API endpoint: `/inventory/api/filtered-items/?type_id=<id>&category_id=<id>&subcategory_id=<id>&search=<term>`

### 2. Serial Management
- تمام Lock views (`before_lock` و `after_lock`) از `serial_service` استفاده می‌کنند
- `before_lock`: validation سریال‌ها (تعداد باید با `quantity` برابر باشد)
- `after_lock`: finalize کردن سریال‌ها (تغییر status به `ISSUED` یا `CONSUMED`)
- Consumption issues سریال‌ها را به `CONSUMED` تغییر می‌دهند

### 3. Multi-line Support
- تمام Create/Update views از `LineFormsetMixin` استفاده می‌کنند
- حداقل یک خط معتبر (با `item`) لازم است
- اگر هیچ خط معتبری وجود نداشته باشد، سند حذف می‌شود (در Create)

### 4. Document Locking
- تمام Update views از `DocumentLockProtectedMixin` استفاده می‌کنند
- Lock views از `DocumentLockView` استفاده می‌کنند
- بعد از قفل شدن، سند دیگر قابل ویرایش نیست

### 5. Permission Checking
- Delete views از `DocumentDeleteViewBase` استفاده می‌کنند که permission checking دارد
- Serial assignment views از `FeaturePermissionRequiredMixin` استفاده می‌کنند

### 6. Error Handling
- `IssueConsumptionCreateView` error handling پیشرفته‌تری دارد (نمایش خطاهای هر خط)
- تمام views خطاهای validation را به صورت user-friendly نمایش می‌دهند

---

## استفاده در پروژه

### URL Patterns
```python
# Permanent Issues
path('issues/permanent/', IssuePermanentListView.as_view(), name='issue_permanent'),
path('issues/permanent/<int:pk>/', IssuePermanentDetailView.as_view(), name='issue_permanent_detail'),
path('issues/permanent/create/', IssuePermanentCreateView.as_view(), name='issue_permanent_create'),
path('issues/permanent/<int:pk>/edit/', IssuePermanentUpdateView.as_view(), name='issue_permanent_edit'),
path('issues/permanent/<int:pk>/delete/', IssuePermanentDeleteView.as_view(), name='issue_permanent_delete'),
path('issues/permanent/<int:pk>/lock/', IssuePermanentLockView.as_view(), name='issue_permanent_lock'),
path('issues/permanent/line/<int:line_id>/assign-serials/', IssuePermanentLineSerialAssignmentView.as_view(), name='issue_permanent_line_serials'),

# Consumption Issues
path('issues/consumption/', IssueConsumptionListView.as_view(), name='issue_consumption'),
path('issues/consumption/<int:pk>/', IssueConsumptionDetailView.as_view(), name='issue_consumption_detail'),
path('issues/consumption/create/', IssueConsumptionCreateView.as_view(), name='issue_consumption_create'),
path('issues/consumption/<int:pk>/edit/', IssueConsumptionUpdateView.as_view(), name='issue_consumption_edit'),
path('issues/consumption/<int:pk>/delete/', IssueConsumptionDeleteView.as_view(), name='issue_consumption_delete'),
path('issues/consumption/<int:pk>/lock/', IssueConsumptionLockView.as_view(), name='issue_consumption_lock'),
path('issues/consumption/line/<int:line_id>/assign-serials/', IssueConsumptionLineSerialAssignmentView.as_view(), name='issue_consumption_line_serials'),

# Consignment Issues
path('issues/consignment/', IssueConsignmentListView.as_view(), name='issue_consignment'),
path('issues/consignment/<int:pk>/', IssueConsignmentDetailView.as_view(), name='issue_consignment_detail'),
path('issues/consignment/create/', IssueConsignmentCreateView.as_view(), name='issue_consignment_create'),
path('issues/consignment/<int:pk>/edit/', IssueConsignmentUpdateView.as_view(), name='issue_consignment_edit'),
path('issues/consignment/<int:pk>/delete/', IssueConsignmentDeleteView.as_view(), name='issue_consignment_delete'),
path('issues/consignment/<int:pk>/lock/', IssueConsignmentLockView.as_view(), name='issue_consignment_lock'),
path('issues/consignment/line/<int:line_id>/assign-serials/', IssueConsignmentLineSerialAssignmentView.as_view(), name='issue_consignment_line_serials'),

# Warehouse Transfer Issues
path('issues/warehouse-transfer/', IssueWarehouseTransferListView.as_view(), name='issue_warehouse_transfer'),
path('issues/warehouse-transfer/create/', IssueWarehouseTransferCreateView.as_view(), name='issue_warehouse_transfer_create'),
path('issues/warehouse-transfer/<int:pk>/edit/', IssueWarehouseTransferUpdateView.as_view(), name='issue_warehouse_transfer_edit'),
path('issues/warehouse-transfer/<int:pk>/', IssueWarehouseTransferDetailView.as_view(), name='issue_warehouse_transfer_detail'),
path('issues/warehouse-transfer/<int:pk>/lock/', IssueWarehouseTransferLockView.as_view(), name='issue_warehouse_transfer_lock'),
path('issues/warehouse-transfer/<int:pk>/unlock/', IssueWarehouseTransferUnlockView.as_view(), name='issue_warehouse_transfer_unlock'),
```

### Templates
- `inventory/issue_permanent.html` - لیست حواله‌های دائم
- `inventory/issue_consumption.html` - لیست حواله‌های مصرف
- `inventory/issue_consignment.html` - لیست حواله‌های امانی
- `inventory/issue_warehouse_transfer.html` - لیست حواله‌های انتقال بین انبارها
- `inventory/issue_detail.html` - جزئیات حواله‌ها (برای Permanent, Consumption, Consignment)
- `inventory/issue_warehouse_transfer_detail.html` - جزئیات حواله انتقال بین انبارها
- `inventory/receipt_form.html` - فرم ایجاد/ویرایش (از `ReceiptFormMixin`)
- `inventory/issue_serial_assignment.html` - فرم اختصاص سریال

---

## الگوهای مشترک

1. **Base Classes**: تمام views از `InventoryBaseView` برای company filtering استفاده می‌کنند
2. **Formset Handling**: تمام Create/Update views از `LineFormsetMixin` برای مدیریت خطوط استفاده می‌کنند
3. **Form Context**: تمام Create/Update views از `ReceiptFormMixin` برای context مشترک استفاده می‌کنند
4. **Lock Protection**: تمام Update views از `DocumentLockProtectedMixin` استفاده می‌کنند
5. **Serial Validation**: تمام Lock views validation و finalization سریال‌ها را انجام می‌دهند
6. **Unlock Support**: `IssueWarehouseTransferUnlockView` از `DocumentUnlockView` استفاده می‌کند و نیاز به permission `unlock_own` دارد
7. **Production Transfers**: Warehouse Transfer views همیشه انتقال‌های ایجاد شده از production workflow (`TransferToLine`) را شامل می‌کنند، حتی اگر کاربر permission view نداشته باشد

---

## خلاصه

این فایل شامل مستندات کامل برای تمام viewهای مربوط به مدیریت حواله‌ها در ماژول inventory است. تمام viewها شامل:

- **ListView**: برای نمایش فهرست اسناد با فیلترها، جستجو، و آمار
- **DetailView**: برای نمایش جزئیات سند (فقط خواندنی)
- **CreateView**: برای ایجاد سند جدید با formset برای خطوط
- **UpdateView**: برای ویرایش سند با formset برای خطوط
- **DeleteView**: برای حذف سند با permission checking
- **LockView**: برای قفل کردن سند با validation سریال
- **Serial Assignment Views**: برای اختصاص سریال به خطوط

تمام viewها از الگوهای مشترک استفاده می‌کنند و شامل permission checking، company filtering، و error handling هستند.

---

## آمار مستندات

این فایل شامل مستندات کامل برای:

- **28 view** مستند شده
- **6 نوع Issue**: Permanent, Consumption, Consignment, Warehouse Transfer
- **تمام متدها** با توضیحات کامل
- **تمام attributes** و context variables
- **تمام URL patterns** و templates
- **الگوهای مشترک** و نکات مهم

---

## تاریخچه تغییرات

- **تاریخ ایجاد**: مستندات کامل برای تمام viewهای Issue
- **آخرین به‌روزرسانی**: تکمیل تمام متدها و attributes

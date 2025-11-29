# inventory/views/issues.py - Issue Views (Complete Documentation)

**هدف**: Views برای مدیریت حواله‌ها (Issues) در ماژول inventory

این فایل شامل views برای:
- Permanent Issues (حواله‌های دائم)
- Consumption Issues (حواله‌های مصرف)
- Consignment Issues (حواله‌های امانی)
- Serial Assignment (اختصاص سریال)

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

**Template**: `inventory/issue_permanent.html`

**Attributes**:
- `model`: `models.IssuePermanent`
- `template_name`: `'inventory/issue_permanent.html'`
- `context_object_name`: `'issues'`
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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related` و `prefetch_related`

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')`
3. `select_related('created_by', 'department_unit', 'warehouse_request')` را اعمال می‌کند
4. `prefetch_related('lines__item', 'lines__warehouse')` را اعمال می‌کند
5. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `create_url`: `reverse_lazy('inventory:issue_permanent_create')`
- `edit_url_name`: `'inventory:issue_permanent_edit'`
- `delete_url_name`: `'inventory:issue_permanent_delete'`
- `lock_url_name`: `'inventory:issue_permanent_lock'`
- `create_label`: `_('Permanent Issue')`
- `show_warehouse_request`: `True`
- `warehouse_request_url_name`: `'inventory:warehouse_request_edit'`
- `serial_url_name`: `None`
- `can_delete_own`, `can_delete_all`: از `add_delete_permissions_to_context()` (از `DocumentDeleteViewBase`)

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
- `list_url`: URL لیست حواله‌های دائم
- `edit_url`: URL ویرایش حواله
- `can_edit`: `bool` - آیا حواله قفل نشده است

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

**توضیح**: سند و line formset را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssuePermanentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.company_id` را از `request.session.get('active_company_id')` تنظیم می‌کند
2. `form.instance.created_by` را به `request.user` تنظیم می‌کند
3. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
4. سند را ذخیره می‌کند (`self.object = form.save()`)
5. line formset را با `build_line_formset()` می‌سازد
6. اگر formset معتبر نیست، response با form و formset برمی‌گرداند
7. تعداد خطوط معتبر را شمارش می‌کند (خطوطی که `item` دارند و `DELETE` نشده‌اند)
8. اگر هیچ خط معتبری وجود ندارد:
   - سند را حذف می‌کند
   - خطا به formset اضافه می‌کند
   - response با form و formset برمی‌گرداند
9. formset را با `_save_line_formset()` ذخیره می‌کند
10. پیام موفقیت را نمایش می‌دهد
11. redirect می‌کند

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**منطق**:
- یک fieldset با عنوان "Document Info" و فیلد `document_code` برمی‌گرداند
- `document_date` به صورت خودکار تولید می‌شود و در template مخفی است

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

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssuePermanentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. اگر `form.instance.created_by_id` وجود ندارد، آن را به `request.user` تنظیم می‌کند
2. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
3. سند را ذخیره می‌کند (`self.object = form.save()`)
4. line formset را با `build_line_formset()` می‌سازد
5. اگر formset معتبر نیست، response با form و formset برمی‌گرداند
6. تعداد خطوط معتبر را شمارش می‌کند
7. اگر هیچ خط معتبری وجود ندارد، خطا به formset اضافه می‌کند و response برمی‌گرداند
8. formset را با `_save_line_formset()` ذخیره می‌کند
9. پیام موفقیت را نمایش می‌دهد
10. redirect می‌کند

**نکات مهم**:
- از `DocumentLockProtectedMixin` استفاده می‌کند که از ویرایش سند قفل‌شده جلوگیری می‌کند

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**منطق**:
- مشابه `IssuePermanentCreateView`

**URL**: `/inventory/issues/permanent/<pk>/edit/`

---

### `IssuePermanentDeleteView`

**توضیح**: حذف حواله دائم

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/issue_permanent_confirm_delete.html`

**Success URL**: `inventory:issue_permanent`

**Attributes**:
- `model`: `models.IssuePermanent`
- `template_name`: `'inventory/issue_permanent_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:issue_permanent')`
- `feature_code`: `'inventory.issues.permanent'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('حواله دائم با موفقیت حذف شد.')`

**متدها**:
- از متدهای `DocumentDeleteViewBase` استفاده می‌کند که شامل permission checking و error handling است

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

**Template**: `inventory/issue_consumption.html`

**Attributes**:
- `model`: `models.IssueConsumption`
- `template_name`: `'inventory/issue_consumption.html'`
- `context_object_name`: `'issues'`
- `paginate_by`: `50`
- `ordering`: `['-id']` (جدیدترین اول)

**Context Variables**:
- `issues`: queryset حواله‌های مصرف (paginated)
- `create_url`: URL برای ایجاد حواله جدید
- `edit_url_name`: نام URL pattern برای ویرایش
- `delete_url_name`: نام URL pattern برای حذف
- `lock_url_name`: نام URL pattern برای قفل کردن
- `create_label`: `_('Consumption Issue')`
- `serial_url_name`: `None`
- `can_delete_own`, `can_delete_all`: از `add_delete_permissions_to_context()`
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related('created_by')`

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')`
3. `select_related('created_by')` را اعمال می‌کند
4. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `create_url`: `reverse_lazy('inventory:issue_consumption_create')`
- `edit_url_name`: `'inventory:issue_consumption_edit'`
- `delete_url_name`: `'inventory:issue_consumption_delete'`
- `lock_url_name`: `'inventory:issue_consumption_lock'`
- `detail_url_name`: `'inventory:issue_consumption_detail'`
- `create_label`: `_('Consumption Issue')`
- `serial_url_name`: `None`
- `can_delete_own`, `can_delete_other`: از `add_delete_permissions_to_context()`

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

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**Context Variables اضافه شده**:
- `active_module`: `'inventory'`
- `issue_variant`: `'consumption'`
- `list_url`: URL لیست issues
- `edit_url`: URL ویرایش issue
- `can_edit`: `bool` - آیا issue قفل نشده است (`not object.is_locked`)
- `active_module`: `'inventory'`
- `issue_variant`: `'consumption'`
- `list_url`: URL لیست حواله‌های مصرف
- `edit_url`: URL ویرایش حواله
- `can_edit`: `bool` - آیا حواله قفل نشده است

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

**توضیح**: سند و line formset را ذخیره می‌کند با error handling پیشرفته.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsumptionForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.company_id` را از `request.session.get('active_company_id')` تنظیم می‌کند
2. `form.instance.created_by` و `edited_by` را به `request.user` تنظیم می‌کند
3. سند را ذخیره می‌کند
4. line formset را با `build_line_formset()` می‌سازد
5. اگر formset معتبر نیست:
   - خطاهای formset را به form اضافه می‌کند
   - خطاهای هر خط را به form اضافه می‌کند (با شماره خط)
   - response با form و formset برمی‌گرداند
6. خطوط معتبر را شناسایی می‌کند (خطوطی که `item` دارند، `DELETE` نشده‌اند و خطا ندارند)
7. خطاهای validation را جمع‌آوری می‌کند
8. اگر هیچ خط معتبری وجود ندارد:
   - سند را حذف می‌کند
   - خطاها را به form اضافه می‌کند
   - formset را دوباره می‌سازد (با `instance=None`)
   - response با form و formset برمی‌گرداند
9. formset را با `_save_line_formset()` ذخیره می‌کند
10. پیام موفقیت را نمایش می‌دهد
11. redirect می‌کند

**نکات مهم**:
- Error handling پیشرفته‌تر از `IssuePermanentCreateView` دارد
- خطاهای هر خط را به صورت جداگانه نمایش می‌دهد

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

**منطق**:
- مشابه `IssuePermanentCreateView`

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

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsumptionForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. اگر `form.instance.created_by_id` وجود ندارد، آن را به `request.user` تنظیم می‌کند
2. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
3. سند را ذخیره می‌کند
4. line formset را با `build_line_formset()` می‌سازد
5. اگر formset معتبر نیست، response با form و formset برمی‌گرداند
6. formset را با `_save_line_formset()` ذخیره می‌کند
7. پیام موفقیت را نمایش می‌دهد
8. redirect می‌کند

**URL**: `/inventory/issues/consumption/<pk>/edit/`

---

### `IssueConsumptionDeleteView`

**توضیح**: حذف حواله مصرف

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/issue_consumption_confirm_delete.html`

**Success URL**: `inventory:issue_consumption`

**Attributes**:
- `model`: `models.IssueConsumption`
- `template_name`: `'inventory/issue_consumption_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:issue_consumption')`
- `feature_code`: `'inventory.issues.consumption'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('حواله مصرفی با موفقیت حذف شد.')`

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

**Template**: `inventory/issue_consignment.html`

**Attributes**:
- `model`: `models.IssueConsignment`
- `template_name`: `'inventory/issue_consignment.html'`
- `context_object_name`: `'issues'`
- `paginate_by`: `50`
- `ordering`: `['-id']` (جدیدترین اول)

**Context Variables**:
- مشابه `IssueConsumptionListView`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با prefetch برای بهینه‌سازی query برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset با `select_related('created_by')`

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. فیلتر بر اساس permissions با `self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')`
3. `select_related('created_by')` را اعمال می‌کند
4. queryset را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- مشابه `IssueConsumptionListView.get_context_data()` اما با URL های مربوط به consignment

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

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**Context Variables اضافه شده**:
- `active_module`: `'inventory'`
- `issue_variant`: `'consignment'`
- `list_url`: URL لیست issues
- `edit_url`: URL ویرایش issue
- `can_edit`: `bool` - آیا issue قفل نشده است (`not object.is_locked`)
- `active_module`: `'inventory'`
- `issue_variant`: `'consignment'`
- `list_url`: URL لیست حواله‌های امانی
- `edit_url`: URL ویرایش حواله
- `can_edit`: `bool` - آیا حواله قفل نشده است

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

**توضیح**: سند و line formset را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsignmentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
- مشابه `IssuePermanentCreateView.form_valid()` اما بدون validation خطوط معتبر (چون در formset validation انجام می‌شود)

---

#### `get_fieldsets(self) -> list`

**توضیح**: تنظیمات fieldsets را برای template برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list`: لیست tuples شامل (title, fields)

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

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: سند و line formset را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `IssueConsignmentForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
- مشابه `IssueConsumptionUpdateView.form_valid()`

**URL**: `/inventory/issues/consignment/<pk>/edit/`

---

### `IssueConsignmentDeleteView`

**توضیح**: حذف حواله امانی

**Type**: `DocumentDeleteViewBase`

**Template**: `inventory/issue_consignment_confirm_delete.html`

**Success URL**: `inventory:issue_consignment`

**Attributes**:
- `model`: `models.IssueConsignment`
- `template_name`: `'inventory/issue_consignment_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:issue_consignment')`
- `feature_code`: `'inventory.issues.consignment'`
- `required_action`: `'delete_own'`
- `allow_own_scope`: `True`
- `success_message`: `_('حواله امانی با موفقیت حذف شد.')`

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

**Context Variables اضافه شده**:
- `line`: `self.line` - instance خط حواله
- `document`: `self.document` - instance سند حواله
- `list_url`: `reverse(self.list_url_name)` - URL لیست
- `edit_url`: `reverse(self.edit_url_name, args=[self.document.pk])` - URL ویرایش
- `lock_url`: `reverse(self.lock_url_name, args=[self.document.pk])` اگر `lock_url_name` وجود دارد، در غیر این صورت `None`
- `required_serials`: تعداد سریال‌های مورد نیاز (از `int(Decimal(self.line.quantity))` یا `None` در صورت خطا)
- `selected_serials_count`: `self.line.serials.count()` - تعداد سریال‌های انتخاب شده
- `available_serials_count`: تعداد سریال‌های موجود در queryset فرم
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
path('issues/permanent/create/', IssuePermanentCreateView.as_view(), name='issue_permanent_create'),
path('issues/permanent/<int:pk>/edit/', IssuePermanentUpdateView.as_view(), name='issue_permanent_edit'),
path('issues/permanent/<int:pk>/delete/', IssuePermanentDeleteView.as_view(), name='issue_permanent_delete'),
path('issues/permanent/<int:pk>/lock/', IssuePermanentLockView.as_view(), name='issue_permanent_lock'),
path('issues/permanent/line/<int:line_id>/assign-serials/', IssuePermanentLineSerialAssignmentView.as_view(), name='issue_permanent_line_serials'),

# Consumption Issues
path('issues/consumption/', IssueConsumptionListView.as_view(), name='issue_consumption'),
path('issues/consumption/create/', IssueConsumptionCreateView.as_view(), name='issue_consumption_create'),
path('issues/consumption/<int:pk>/edit/', IssueConsumptionUpdateView.as_view(), name='issue_consumption_edit'),
path('issues/consumption/<int:pk>/delete/', IssueConsumptionDeleteView.as_view(), name='issue_consumption_delete'),
path('issues/consumption/<int:pk>/lock/', IssueConsumptionLockView.as_view(), name='issue_consumption_lock'),
path('issues/consumption/line/<int:line_id>/assign-serials/', IssueConsumptionLineSerialAssignmentView.as_view(), name='issue_consumption_line_serials'),

# Consignment Issues
path('issues/consignment/', IssueConsignmentListView.as_view(), name='issue_consignment'),
path('issues/consignment/create/', IssueConsignmentCreateView.as_view(), name='issue_consignment_create'),
path('issues/consignment/<int:pk>/edit/', IssueConsignmentUpdateView.as_view(), name='issue_consignment_edit'),
path('issues/consignment/<int:pk>/delete/', IssueConsignmentDeleteView.as_view(), name='issue_consignment_delete'),
path('issues/consignment/<int:pk>/lock/', IssueConsignmentLockView.as_view(), name='issue_consignment_lock'),
path('issues/consignment/line/<int:line_id>/assign-serials/', IssueConsignmentLineSerialAssignmentView.as_view(), name='issue_consignment_line_serials'),
```

### Templates
- `inventory/issue_permanent.html` - لیست حواله‌های دائم
- `inventory/issue_consumption.html` - لیست حواله‌های مصرف
- `inventory/issue_consignment.html` - لیست حواله‌های امانی
- `inventory/receipt_form.html` - فرم ایجاد/ویرایش (از `ReceiptFormMixin`)
- `inventory/issue_serial_assignment.html` - فرم اختصاص سریال

---

## الگوهای مشترک

1. **Base Classes**: تمام views از `InventoryBaseView` برای company filtering استفاده می‌کنند
2. **Formset Handling**: تمام Create/Update views از `LineFormsetMixin` برای مدیریت خطوط استفاده می‌کنند
3. **Form Context**: تمام Create/Update views از `ReceiptFormMixin` برای context مشترک استفاده می‌کنند
4. **Lock Protection**: تمام Update views از `DocumentLockProtectedMixin` استفاده می‌کنند
5. **Serial Validation**: تمام Lock views validation و finalization سریال‌ها را انجام می‌دهند

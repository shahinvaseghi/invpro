# production/views/rework.py - Rework Document Views

**هدف**: مدیریت viewهای سند بازکاری (Rework Document) برای عملیات‌های بدون سند عملکرد یا عملیات‌های با سند عملکرد رد شده توسط QC

این فایل شامل viewهای زیر است:
- `ReworkDocumentListView` - لیست اسناد بازکاری
- `ReworkDocumentCreateView` - ایجاد سند بازکاری
- `ReworkDocumentUpdateView` - ویرایش سند بازکاری
- `ReworkDocumentDetailView` - مشاهده جزئیات سند بازکاری
- `ReworkDocumentDeleteView` - حذف سند بازکاری
- `ReworkDocumentApproveView` - تأیید سند بازکاری
- `ReworkDocumentRejectView` - رد سند بازکاری
- `ReworkOrderSelectForm` - فرم انتخاب سفارش تولید

---

## کلاس‌ها

### `ReworkOrderSelectForm`

**توضیح**: فرم انتخاب سفارش تولید برای ایجاد سند بازکاری

**Type**: `forms.Form`

**Fields**:
- `order` (ModelChoiceField): انتخاب سفارش تولید
  - Widget: `forms.Select`
  - Label: `'Production Order'`
  - Required: `True`
  - Queryset: `ProductOrder.objects.none()` (در view تنظیم می‌شود)

---

### `ReworkDocumentListView`

**توضیح**: نمایش لیست اسناد بازکاری برای شرکت فعال

**Type**: `BaseDocumentListView`

**Template**: `production/rework_document_list.html`

**Attributes**:
- `model`: `ReworkDocument`
- `template_name`: `'production/rework_document_list.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'production.rework'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`
- `default_status_filter`: `False`
- `default_order_by`: `['-rework_date', 'rework_code']`

**متدها**:

#### `get_select_related(self) -> List[str]`

**توضیح**: لیست فیلدهای مربوطه برای select_related

**مقدار بازگشتی**:
- `List[str]`: لیست فیلدها شامل `['order', 'order__finished_item', 'operation', 'original_performance', 'approved_by']`

#### `get_queryset(self) -> QuerySet`

**توضیح**: فیلتر کردن اسناد بازکاری بر اساس شرکت فعال و permissions

**منطق**:
1. queryset پایه را از `super().get_queryset()` دریافت می‌کند
2. `active_company_id` را از session دریافت می‌کند
3. permissions کاربر را با `get_user_feature_permissions()` دریافت می‌کند
4. اگر کاربر `view_all` permission نداشته باشد، فقط رکوردهای خودش را نمایش می‌دهد (`created_by=self.request.user`)
5. queryset فیلتر شده را برمی‌گرداند

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه

**مقدار بازگشتی**:
- `str`: `_('Rework Documents')`

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs شامل `[{'label': _('Production'), 'url': None}, {'label': _('Rework'), 'url': None}]`

#### `get_create_url(self) -> Optional[str]`

**توضیح**: URL ایجاد اگر کاربر permission داشته باشد

**منطق**:
1. `active_company_id` را از session دریافت می‌کند
2. permissions کاربر را بررسی می‌کند
3. اگر کاربر `create` permission داشته باشد یا superuser باشد، URL ایجاد را برمی‌گرداند
4. در غیر این صورت `None` برمی‌گرداند

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد

**مقدار بازگشتی**:
- `str`: `_('Create Rework Document +')`

#### `get_detail_url_name(self) -> Optional[str]`

**توضیح**: نام URL جزئیات

**مقدار بازگشتی**:
- `str`: `'production:rework_document_detail'`

#### `get_edit_url_name(self) -> Optional[str]`

**توضیح**: نام URL ویرایش

**مقدار بازگشتی**:
- `str`: `'production:rework_document_edit'`

#### `get_delete_url_name(self) -> Optional[str]`

**توضیح**: نام URL حذف

**مقدار بازگشتی**:
- `str`: `'production:rework_document_delete'`

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان حالت خالی

**مقدار بازگشتی**:
- `str`: `_('No Rework Documents Found')`

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام حالت خالی

**مقدار بازگشتی**:
- `str`: `_('Create your first rework document to get started.')`

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون حالت خالی

**مقدار بازگشتی**:
- `str`: `'🔄'`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن context برای template

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل `show_filters=False` و `user_feature_permissions`

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `show_filters` را `False` تنظیم می‌کند
3. `user_feature_permissions` را برای template اضافه می‌کند

---

### `ReworkDocumentCreateView`

**توضیح**: ایجاد سند بازکاری. ابتدا فرم انتخاب سفارش نمایش داده می‌شود، سپس دو لیست عملیات بعد از انتخاب سفارش نمایش داده می‌شود

**Type**: `BaseCreateView`

**Template**: `production/rework_document_form.html`

**Attributes**:
- `model`: `ReworkDocument`
- `template_name`: `'production/rework_document_form.html'`
- `feature_code`: `'production.rework'`
- `required_action`: `'create'`
- `active_module`: `'production'`
- `success_url`: `reverse_lazy('production:rework_document_list')`
- `success_message`: `_('Rework document created successfully.')`
- `fields`: `['order', 'operation', 'original_performance', 'reason', 'notes', 'approved_by']`

**متدها**:

#### `get_form(self, form_class=None) -> forms.ModelForm`

**توضیح**: دریافت form با querysetهای محدود به شرکت

**منطق**:
1. form پایه را از `super().get_form()` دریافت می‌کند
2. `active_company_id` را از session دریافت می‌کند
3. اگر `active_company_id` وجود داشته باشد:
   - `order` queryset را فیلتر می‌کند: `ProductOrder.objects.filter(company_id=active_company_id, process__isnull=False).select_related('finished_item', 'process')`
   - `operation` queryset را فیلتر می‌کند: `ProcessOperation.objects.filter(company_id=active_company_id, is_enabled=1).select_related('process', 'work_line')`
   - `original_performance` queryset را فیلتر می‌کند: `PerformanceRecord.objects.filter(company_id=active_company_id, document_type=PerformanceRecord.DocumentType.OPERATIONAL)`
   - `approved_by` queryset را فیلتر می‌کند: کاربرانی که `approve` permission برای `production.rework` دارند یا superuser هستند
4. form را برمی‌گرداند

#### `get_initial(self) -> Dict[str, Any]`

**توضیح**: تنظیم مقادیر اولیه

**منطق**:
1. initial پایه را از `super().get_initial()` دریافت می‌کند
2. `order_id` را از GET parameter دریافت می‌کند
3. اگر `order_id` وجود داشته باشد، order را پیدا می‌کند و به initial اضافه می‌کند
4. initial را برمی‌گرداند

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs شامل `[{'label': _('Production'), 'url': None}, {'label': _('Rework'), 'url': reverse_lazy('production:rework_document_list')}, {'label': _('Create'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو

**مقدار بازگشتی**:
- `str`: `reverse_lazy('production:rework_document_list')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم

**مقدار بازگشتی**:
- `str`: `_('Create Rework Document')`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن context برای template

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل `form_id`, `selected_order`, `list1_operations`, `list2_operations`

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `form_id` را `'rework-form'` تنظیم می‌کند
3. `selected_order` را از form یا GET parameter دریافت می‌کند
4. اگر order انتخاب شده باشد، لیست‌های عملیات را با `get_operations_lists()` دریافت می‌کند:
   - `list1_operations`: عملیات‌های بدون سند عملکرد
   - `list2_operations`: عملیات‌های با سند عملکرد رد شده توسط QC
5. context را برمی‌گرداند

#### `get_operations_lists(self, order: ProductOrder) -> Dict[str, List[Any]]`

**توضیح**: دریافت دو لیست عملیات برای سفارش انتخاب شده

**پارامترهای ورودی**:
- `order`: سفارش تولید

**مقدار بازگشتی**:
- `Dict[str, List[Any]]`: دیکشنری شامل `list1_operations` و `list2_operations`

**منطق**:
1. اگر order یا process وجود نداشته باشد، لیست‌های خالی برمی‌گرداند
2. عملیات‌های process را با فیلتر `company_id` و `is_enabled=1` دریافت می‌کند
3. **List 1**: عملیات‌های بدون سند عملکرد:
   - برای هر عملیات، بررسی می‌کند که آیا سند عملکرد `OPERATIONAL` وجود دارد یا نه
   - اگر وجود نداشته باشد، به `list1_operations` اضافه می‌کند
4. **List 2**: عملیات‌های با سند عملکرد رد شده توسط QC:
   - برای هر عملیات، بررسی می‌کند که آیا `OperationQCStatus` با `qc_status=REJECTED` وجود دارد یا نه
   - اگر وجود داشته باشد، به `list2_operations` اضافه می‌کند (با `operation`, `qc_status`, `performance`)
5. دیکشنری شامل هر دو لیست را برمی‌گرداند

#### `form_valid(self, form: forms.ModelForm) -> HttpResponseRedirect`

**توضیح**: تولید کد بازکاری و ذخیره

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق** (با `@transaction.atomic`):
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود نداشته باشد، خطا اضافه می‌کند و `form_invalid` برمی‌گرداند
3. `operation_id` را از POST (از radio button selection) دریافت می‌کند
4. اگر `operation_id` وجود داشته باشد:
   - operation را پیدا می‌کند و به `form.instance.operation` تنظیم می‌کند
   - اگر operation سند عملکرد رد شده QC داشته باشد، `original_performance` را تنظیم می‌کند
5. اگر `rework_code` وجود نداشته باشد، کد را با `generate_sequential_code()` تولید می‌کند (prefix='RW', width=8)
6. `company_id` و `created_by` را تنظیم می‌کند
7. پیام موفقیت را نمایش می‌دهد
8. `super().form_valid(form)` را فراخوانی می‌کند

---

### `ReworkDocumentDetailView`

**توضیح**: مشاهده جزئیات سند بازکاری

**Type**: `BaseDetailView`

**Template**: `production/rework_document_detail.html`

**Attributes**:
- `model`: `ReworkDocument`
- `template_name`: `'production/rework_document_detail.html'`
- `context_object_name`: `'object'`
- `feature_code`: `'production.rework'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`

**متدها**:

#### `get_list_url(self) -> str`

**توضیح**: URL لیست

**مقدار بازگشتی**:
- `str`: `reverse_lazy('production:rework_document_list')`

#### `get_edit_url(self) -> str`

**توضیح**: URL ویرایش

**مقدار بازگشتی**:
- `str`: `reverse_lazy('production:rework_document_edit', kwargs={'pk': self.object.pk})`

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`

**توضیح**: بررسی اینکه آیا object قابل ویرایش است

**پارامترهای ورودی**:
- `obj`: object (اختیاری)
- `feature_code`: feature code (اختیاری)

**مقدار بازگشتی**:
- `bool`: `True` اگر object قفل نباشد، در غیر این صورت `False`

**منطق**:
1. اگر `obj` ارائه نشده باشد، از `self.object` استفاده می‌کند
2. اگر object دارای `is_locked` باشد، بررسی می‌کند که قفل نباشد
3. در غیر این صورت `True` برمی‌گرداند

---

### `ReworkDocumentUpdateView`

**توضیح**: ویرایش سند بازکاری موجود

**Type**: `BaseUpdateView, EditLockProtectedMixin`

**Template**: `production/rework_document_form.html`

**Attributes**:
- `model`: `ReworkDocument`
- `template_name`: `'production/rework_document_form.html'`
- `success_url`: `reverse_lazy('production:rework_document_list')`
- `feature_code`: `'production.rework'`
- `required_action`: `'edit_own'`
- `active_module`: `'production'`
- `success_message`: `_('Rework document updated successfully.')`
- `fields`: `['order', 'operation', 'original_performance', 'reason', 'notes', 'approved_by']`

**متدها**:

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs شامل `[{'label': _('Production'), 'url': None}, {'label': _('Rework'), 'url': reverse_lazy('production:rework_document_list')}, {'label': _('Edit'), 'url': None}]`

#### `get_cancel_url(self) -> str`

**توضیح**: URL لغو

**مقدار بازگشتی**:
- `str`: `reverse_lazy('production:rework_document_list')`

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم

**مقدار بازگشتی**:
- `str`: `_('Edit Rework Document')`

#### `get_form(self, form_class=None) -> forms.ModelForm`

**توضیح**: دریافت form با querysetهای محدود به شرکت (مشابه CreateView)

**منطق**: مشابه `ReworkDocumentCreateView.get_form()`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن context برای template

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `form_id` را `'rework-form'` تنظیم می‌کند
3. `selected_order` را از `self.object.order` دریافت می‌کند
4. اگر order وجود داشته باشد، لیست‌های عملیات را با `get_operations_lists()` دریافت می‌کند
5. context را برمی‌گرداند

#### `get_operations_lists(self, order: ProductOrder) -> Dict[str, List[Any]]`

**توضیح**: دریافت دو لیست عملیات (مشابه CreateView)

**منطق**: مشابه `ReworkDocumentCreateView.get_operations_lists()`

---

### `ReworkDocumentDeleteView`

**توضیح**: حذف سند بازکاری

**Type**: `BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Attributes**:
- `model`: `ReworkDocument`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:rework_document_list')`
- `feature_code`: `'production.rework'`
- `required_action`: `'delete_own'`
- `active_module`: `'production'`
- `success_message`: `_('Rework document deleted successfully.')`

**متدها**:

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف

**مقدار بازگشتی**:
- `str`: `_('Delete Rework Document')`

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تأیید

**مقدار بازگشتی**:
- `str`: `_('Are you sure you want to delete this rework document?')`

#### `get_object_details(self) -> List[Dict[str, str]]`

**توضیح**: جزئیات object برای نمایش در صفحه تأیید

**مقدار بازگشتی**:
- `List[Dict[str, str]]`: لیست جزئیات شامل `rework_code`, `order_code`, `rework_date` (به شمسی)، `status`

**منطق**:
1. `rework_code` را به صورت `<code>` اضافه می‌کند
2. `order_code` را اضافه می‌کند
3. اگر `rework_date` وجود داشته باشد، آن را به شمسی تبدیل می‌کند و اضافه می‌کند
4. `status` را با `get_status_display()` اضافه می‌کند
5. لیست جزئیات را برمی‌گرداند

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs شامل `[{'label': _('Production'), 'url': None}, {'label': _('Rework'), 'url': reverse_lazy('production:rework_document_list')}, {'label': _('Delete'), 'url': None}]`

---

### `ReworkDocumentApproveView`

**توضیح**: تأیید سند بازکاری

**Type**: `FeaturePermissionRequiredMixin, View`

**Attributes**:
- `feature_code`: `'production.rework'`
- `required_action`: `'approve'`

**متدها**:

#### `post(self, request: HttpRequest, pk: int) -> JsonResponse`

**توضیح**: تأیید سند بازکاری

**پارامترهای ورودی**:
- `request`: HTTP request
- `pk`: ID سند بازکاری

**مقدار بازگشتی**:
- `JsonResponse`: پاسخ JSON با success یا error

**منطق**:
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود نداشته باشد، خطا برمی‌گرداند
3. سند بازکاری را پیدا می‌کند
4. بررسی می‌کند که قبلاً تأیید یا رد نشده باشد
5. بررسی می‌کند که کاربر approver باشد (`approved_by == request.user`)
6. status را `APPROVED` تنظیم می‌کند و ذخیره می‌کند
7. پیام موفقیت را نمایش می‌دهد
8. پاسخ JSON موفقیت را برمی‌گرداند

---

### `ReworkDocumentRejectView`

**توضیح**: رد سند بازکاری

**Type**: `FeaturePermissionRequiredMixin, View`

**Attributes**:
- `feature_code`: `'production.rework'`
- `required_action`: `'reject'`

**متدها**:

#### `post(self, request: HttpRequest, pk: int) -> JsonResponse`

**توضیح**: رد سند بازکاری

**پارامترهای ورودی**:
- `request`: HTTP request
- `pk`: ID سند بازکاری

**مقدار بازگشتی**:
- `JsonResponse`: پاسخ JSON با success یا error

**منطق**:
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود نداشته باشد، خطا برمی‌گرداند
3. سند بازکاری را پیدا می‌کند
4. بررسی می‌کند که قبلاً تأیید یا رد نشده باشد
5. بررسی می‌کند که کاربر approver باشد (`approved_by == request.user`)
6. `qc_notes` را از POST دریافت می‌کند (اختیاری)
7. status را `REJECTED` تنظیم می‌کند و ذخیره می‌کند
8. اگر `qc_notes` وجود داشته باشد، آن را ذخیره می‌کند
9. پیام موفقیت را نمایش می‌دهد
10. پاسخ JSON موفقیت را برمی‌گرداند

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.views.base`: `BaseDocumentListView`, `BaseCreateView`, `BaseUpdateView`, `BaseDetailView`, `BaseDeleteView`, `EditLockProtectedMixin`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`
- `inventory.utils.codes`: `generate_sequential_code`
- `production.models`: `ReworkDocument`, `ProductOrder`, `ProcessOperation`, `PerformanceRecord`, `OperationQCStatus`

---

## استفاده در پروژه

### URL Patterns

```python
urlpatterns = [
    path('rework/', ReworkDocumentListView.as_view(), name='rework_document_list'),
    path('rework/create/', ReworkDocumentCreateView.as_view(), name='rework_document_create'),
    path('rework/<int:pk>/', ReworkDocumentDetailView.as_view(), name='rework_document_detail'),
    path('rework/<int:pk>/edit/', ReworkDocumentUpdateView.as_view(), name='rework_document_edit'),
    path('rework/<int:pk>/delete/', ReworkDocumentDeleteView.as_view(), name='rework_document_delete'),
    path('rework/<int:pk>/approve/', ReworkDocumentApproveView.as_view(), name='rework_document_approve'),
    path('rework/<int:pk>/reject/', ReworkDocumentRejectView.as_view(), name='rework_document_reject'),
]
```

---

## نکات مهم

1. **Permission System**: تمام viewها از سیستم permission استفاده می‌کنند و بر اساس `feature_code='production.rework'` و `required_action` دسترسی را بررسی می‌کنند

2. **Company Scoping**: تمام querysetها بر اساس `active_company_id` از session فیلتر می‌شوند

3. **Operations Lists**: در CreateView و UpdateView، دو لیست عملیات نمایش داده می‌شود:
   - **List 1**: عملیات‌های بدون سند عملکرد
   - **List 2**: عملیات‌های با سند عملکرد رد شده توسط QC

4. **Code Generation**: کد بازکاری به صورت خودکار با `generate_sequential_code()` تولید می‌شود (prefix='RW', width=8)

5. **Approval Workflow**: سند بازکاری باید توسط `approved_by` تأیید یا رد شود

6. **Edit Lock Protection**: UpdateView از `EditLockProtectedMixin` استفاده می‌کند تا از ویرایش همزمان جلوگیری کند

7. **Transaction Safety**: `form_valid()` در CreateView با `@transaction.atomic` محافظت می‌شود

8. **JSON Responses**: ApproveView و RejectView پاسخ JSON برمی‌گردانند برای استفاده در AJAX requests

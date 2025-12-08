# production/views/qc_operations.py - QC Operations Views

**هدف**: مدیریت viewهای عملیات کنترل کیفیت (QC Operations) برای عملیات‌هایی که نیاز به بازرسی QC دارند و سند عملکرد دارند

این فایل شامل viewهای زیر است:
- `QCOperationsListView` - لیست عملیات‌هایی که نیاز به QC دارند و performance document دارند
- `QCOperationApproveView` - تأیید عملیات QC
- `QCOperationRejectView` - رد عملیات QC

---

## کلاس‌ها

### `QCOperationsListView`

**توضیح**: نمایش لیست عملیات‌هایی که نیاز به QC دارند و سند عملکرد دارند. فقط عملیات‌هایی نمایش داده می‌شوند که:
- `requires_qc = 1`
- سند عملکرد برای عملیات وجود دارد

**Type**: `BaseListView`

**Template**: `production/qc_operations_list.html`

**Attributes**:
- `model`: `OperationQCStatus`
- `template_name`: `'production/qc_operations_list.html'`
- `context_object_name`: `'qc_operations'`
- `paginate_by`: `50`
- `feature_code`: `'production.qc_operations'`
- `required_action`: `'view_own'`
- `active_module`: `'production'`
- `default_status_filter`: `False`
- `default_order_by`: `['qc_status', '-qc_status_date', '-created_at', 'order', 'operation']` (PENDING first, then APPROVED, then REJECTED)

**متدها**:

#### `get_base_queryset(self) -> QuerySet`

**توضیح**: دریافت queryset پایه با فیلترهای عملیات QC

**مقدار بازگشتی**:
- `QuerySet`: queryset شامل `OperationQCStatus.objects.filter(operation__requires_qc=1, performance__isnull=False)`

**منطق**:
1. فقط `OperationQCStatus` هایی که عملیات آن‌ها `requires_qc=1` دارند را فیلتر می‌کند
2. فقط مواردی که `performance` وجود دارد را فیلتر می‌کند

#### `get_select_related(self) -> List[str]`

**توضیح**: لیست فیلدهای مربوطه برای select_related

**مقدار بازگشتی**:
- `List[str]`: لیست فیلدها شامل `['order', 'order__finished_item', 'operation', 'operation__process', 'performance', 'qc_approved_by']`

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه

**مقدار بازگشتی**:
- `str`: `_('QC Operations')`

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs شامل `[{'label': _('Production'), 'url': None}, {'label': _('QC Operations'), 'url': None}]`

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان حالت خالی

**مقدار بازگشتی**:
- `str`: `_('No QC Operations Found')`

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام حالت خالی

**مقدار بازگشتی**:
- `str`: `_('No operations require QC inspection at this time.')`

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون حالت خالی

**مقدار بازگشتی**:
- `str`: `'✅'`

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن context برای template

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل `show_filters`, `show_actions`, `can_approve`, `can_reject`

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `show_filters` را `False` تنظیم می‌کند
3. `show_actions` را `False` تنظیم می‌کند (actions در template مدیریت می‌شوند)
4. `active_company_id` را از session دریافت می‌کند
5. permissions کاربر را بررسی می‌کند:
   - `can_approve`: آیا کاربر `approve` permission دارد یا superuser است
   - `can_reject`: آیا کاربر `reject` permission دارد یا superuser است
6. context را برمی‌گرداند

---

### `QCOperationApproveView`

**توضیح**: تأیید QC برای یک عملیات

**Type**: `FeaturePermissionRequiredMixin, View`

**Attributes**:
- `feature_code`: `'production.qc_operations'`
- `required_action`: `'approve'`

**متدها**:

#### `post(self, request: HttpRequest, pk: int) -> JsonResponse`

**توضیح**: تأیید QC برای عملیات

**پارامترهای ورودی**:
- `request`: HTTP request
- `pk`: ID عملیات QC status

**مقدار بازگشتی**:
- `JsonResponse`: پاسخ JSON با success یا error

**منطق**:
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود نداشته باشد، خطا برمی‌گرداند (`status=400`)
3. `OperationQCStatus` را پیدا می‌کند با `company_id` filter
4. بررسی می‌کند که قبلاً تأیید نشده باشد (`qc_status == APPROVED`)
5. بررسی می‌کند که قبلاً رد نشده باشد (`qc_status == REJECTED`)
6. `qc_status` را `APPROVED` تنظیم می‌کند
7. `qc_approved_by` را `request.user` تنظیم می‌کند
8. `qc_status_date` را `timezone.now()` تنظیم می‌کند
9. ذخیره می‌کند
10. پیام موفقیت را نمایش می‌دهد
11. پاسخ JSON موفقیت را برمی‌گرداند

---

### `QCOperationRejectView`

**توضیح**: رد QC برای یک عملیات

**Type**: `FeaturePermissionRequiredMixin, View`

**Attributes**:
- `feature_code`: `'production.qc_operations'`
- `required_action`: `'reject'`

**متدها**:

#### `post(self, request: HttpRequest, pk: int) -> JsonResponse`

**توضیح**: رد QC برای عملیات

**پارامترهای ورودی**:
- `request`: HTTP request
- `pk`: ID عملیات QC status

**مقدار بازگشتی**:
- `JsonResponse`: پاسخ JSON با success یا error

**منطق**:
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود نداشته باشد، خطا برمی‌گرداند (`status=400`)
3. `OperationQCStatus` را پیدا می‌کند با `company_id` filter
4. بررسی می‌کند که قبلاً تأیید نشده باشد (`qc_status == APPROVED`)
5. بررسی می‌کند که قبلاً رد نشده باشد (`qc_status == REJECTED`)
6. `qc_notes` را از POST دریافت می‌کند (اختیاری، با `.strip()`)
7. `qc_status` را `REJECTED` تنظیم می‌کند
8. `qc_approved_by` را `request.user` تنظیم می‌کند
9. `qc_status_date` را `timezone.now()` تنظیم می‌کند
10. اگر `qc_notes` وجود داشته باشد، آن را ذخیره می‌کند
11. ذخیره می‌کند
12. پیام موفقیت را نمایش می‌دهد
13. پاسخ JSON موفقیت را برمی‌گرداند

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.views.base`: `BaseListView`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`
- `production.models`: `OperationQCStatus`, `ProductOrder`, `ProcessOperation`, `PerformanceRecord`

---

## استفاده در پروژه

### URL Patterns

```python
urlpatterns = [
    path('qc-operations/', QCOperationsListView.as_view(), name='qc_operations_list'),
    path('qc-operations/<int:pk>/approve/', QCOperationApproveView.as_view(), name='qc_operation_approve'),
    path('qc-operations/<int:pk>/reject/', QCOperationRejectView.as_view(), name='qc_operation_reject'),
]
```

---

## نکات مهم

1. **Permission System**: تمام viewها از سیستم permission استفاده می‌کنند و بر اساس `feature_code='production.qc_operations'` و `required_action` دسترسی را بررسی می‌کنند

2. **Company Scoping**: تمام querysetها بر اساس `active_company_id` از session فیلتر می‌شوند

3. **Filtering Logic**: فقط عملیات‌هایی نمایش داده می‌شوند که:
   - `requires_qc = 1`
   - سند عملکرد (`performance`) وجود دارد

4. **Ordering**: لیست بر اساس `qc_status` مرتب می‌شود (PENDING اول، سپس APPROVED، سپس REJECTED)

5. **JSON Responses**: ApproveView و RejectView پاسخ JSON برمی‌گردانند برای استفاده در AJAX requests

6. **QC Notes**: در RejectView، `qc_notes` اختیاری است و از POST دریافت می‌شود

7. **Status Tracking**: `qc_status_date` و `qc_approved_by` برای ردیابی تاریخ و کاربر تأیید/رد کننده تنظیم می‌شوند

8. **Error Handling**: تمام خطاها به صورت JSON با status code مناسب برمی‌گردانند

# shared/views/base.py - Base Views and Mixins

**هدف**: کلاس‌های پایه و mixin‌های قابل استفاده مجدد برای views تمام ماژول‌ها

این فایل شامل کلاس‌های زیر است:
- **Mixins**: `UserAccessFormsetMixin`, `AccessLevelPermissionMixin`, `EditLockProtectedMixin`
- **Base Views**: `BaseListView`, `BaseCreateView`, `BaseUpdateView`, `BaseDeleteView`, `BaseDetailView`
- **Formset Views**: `BaseFormsetCreateView`, `BaseFormsetUpdateView`
- **Document Views**: `BaseDocumentListView`, `BaseDocumentCreateView`, `BaseDocumentUpdateView`
- **Nested Formset Views**: `BaseNestedFormsetCreateView`, `BaseNestedFormsetUpdateView`

---

## Mixins

### `UserAccessFormsetMixin`

**توضیح**: Helper mixin برای مدیریت `UserCompanyAccess` formsets در views ایجاد/ویرایش کاربر

**متدها**:

#### `get_access_formset(self, form: Optional[Any] = None) -> UserCompanyAccessFormSet`

**توضیح**: دریافت یا ایجاد `UserCompanyAccess` formset برای یک کاربر

**پارامترهای ورودی**:
- `form` (Optional[Any]): فرم کاربر (اختیاری)

**مقدار بازگشتی**:
- `UserCompanyAccessFormSet`: formset instance

**منطق**:
1. instance را از `form.instance` یا `self.object` تعیین می‌کند
2. اگر instance وجود نداشته باشد، یک `User()` جدید ایجاد می‌کند
3. formset را با POST data (اگر request method POST باشد) یا None ایجاد می‌کند
4. formset را برمی‌گرداند

---

### `AccessLevelPermissionMixin`

**توضیح**: Mixin برای مدیریت permissions در views ایجاد/ویرایش access level

**Attributes**:
- `template_name`: `'shared/access_level_form.html'`
- `_action_labels_cache`: Dictionary از action labels (cached)

**متدها**:

#### `get_action_labels(self) -> Dict[str, str]`

**توضیح**: دریافت dictionary از action labels (cached)

**مقدار بازگشتی**:
- `Dict[str, str]`: Dictionary mapping action codes به labels

**منطق**:
1. اگر cache وجود نداشته باشد:
   - `_action_labels_cache` را با ترجمه‌های فارسی برای تمام `PermissionAction` values ایجاد می‌کند
   - شامل: VIEW_OWN, VIEW_ALL, VIEW_SAME_GROUP, CREATE, EDIT_OWN, EDIT_OTHER, EDIT_SAME_GROUP, DELETE_OWN, DELETE_OTHER, DELETE_SAME_GROUP, LOCK_OWN, LOCK_OTHER, LOCK_SAME_GROUP, UNLOCK_OWN, UNLOCK_OTHER, UNLOCK_SAME_GROUP, APPROVE, REJECT, CANCEL, CREATE_TRANSFER_FROM_ORDER, CREATE_RECEIPT, CREATE_RECEIPT_FROM_PURCHASE_REQUEST, CREATE_ISSUE_FROM_WAREHOUSE_REQUEST
2. cache را برمی‌گرداند

#### `_feature_key(self, code: str) -> str`

**توضیح**: تبدیل feature code به HTML-safe key

**پارامترهای ورودی**:
- `code` (str): Feature code (مثلاً `'inventory.items'`)

**مقدار بازگشتی**:
- `str`: Normalized key (مثلاً `'inventory__items'`)

**منطق**:
- جایگزینی `.` با `__` برای استفاده در templates

#### `_prepare_feature_context(self, instance: Optional[Any] = None) -> list`

**توضیح**: آماده‌سازی context برای feature permissions در template

**پارامترهای ورودی**:
- `instance` (Optional[Any]): AccessLevel instance (اختیاری)

**مقدار بازگشتی**:
- `list`: لیست dictionaries با اطلاعات features و permissions، grouped by module

**منطق**:
1. اگر instance موجود باشد، permissions موجود را از database می‌خواند
2. برای هر feature در `FEATURE_PERMISSION_MAP`:
   - ساخت dictionary با code, html_id, label, module_code, view_supported, view_scope, actions
   - بررسی permissions موجود و تنظیم checked states
3. Group کردن features بر اساس module code
4. ساخت module_list با module labels (شامل: shared, production, inventory, qc, ticketing, accounting, sales, hr, office_automation, transportation, procurement)
5. بازگشت module_list

**Context Structure**:
```python
[
    {
        'code': 'inventory',
        'label': 'Inventory',
        'features': [
            {
                'code': 'inventory.items',
                'html_id': 'inventory__items',
                'label': 'Items',
                'module_code': 'inventory',
                'view_supported': True,
                'view_scope': 'all',  # 'none', 'own', 'all'
                'actions': [
                    {
                        'code': 'create',
                        'label': 'Create',
                        'checked': True
                    },
                    ...
                ]
            },
            ...
        ]
    },
    ...
]
```

#### `_save_permissions(self, form: Any) -> None`

**توضیح**: ذخیره permissions از POST data

**پارامترهای ورودی**:
- `form`: فرم access level

**منطق**:
1. برای هر feature در `FEATURE_PERMISSION_MAP`:
   - `view_scope` را از POST دریافت می‌کند (`perm-{html_key}-view`)
   - selected actions را از POST checkboxes دریافت می‌کند
   - اگر `view_scope == 'none'` و هیچ action انتخاب نشده باشد:
     - permission موجود را حذف می‌کند (اگر وجود داشته باشد)
   - در غیر این صورت:
     - `AccessLevelPermission` را ایجاد یا به‌روزرسانی می‌کند
     - `can_view`, `can_create`, `can_edit`, `can_delete`, `can_approve` را تنظیم می‌کند
     - `metadata` را با `actions` dictionary می‌سازد
     - permission را ذخیره می‌کند
2. permissions که دیگر در POST data نیستند را حذف می‌کند (stale permissions)

---

### `EditLockProtectedMixin`

**توضیح**: Mixin برای جلوگیری از ویرایش همزمان رکوردها

این mixin بررسی می‌کند که آیا یک رکورد در حال ویرایش توسط کاربر دیگری است یا نه هنگام باز کردن فرم ویرایش (GET request). اگر باشد، دسترسی را مسدود می‌کند و پیام خطا نمایش می‌دهد.

**Attributes**:
- `edit_lock_timeout_minutes`: `5` - Timeout برای edit locks (دقیقه)
- `edit_lock_error_message`: پیام خطا برای edit lock
- `edit_lock_redirect_url_name`: نام URL برای redirect (اختیاری)

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی edit lock قبل از اجازه دادن به دسترسی به فرم ویرایش

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا redirect

**منطق**:
1. فقط برای GET requests بررسی می‌کند (باز کردن فرم)
2. object را با `get_object()` دریافت می‌کند
3. اگر object دارای `EditableModel` mixin نباشد، `super().dispatch()` را فراخوانی می‌کند
4. object را از DB refresh می‌کند
5. بررسی می‌کند که آیا lock stale است (قدیمی‌تر از timeout):
   - اگر باشد، lock را clear می‌کند
6. بررسی می‌کند که آیا رکورد در حال ویرایش توسط کاربر/session دیگری است:
   - اگر باشد، پیام خطا نمایش می‌دهد و redirect می‌کند
7. اگر lock وجود نداشته باشد یا متعلق به کاربر فعلی باشد:
   - edit lock را برای کاربر فعلی تنظیم می‌کند (`editing_by`, `editing_started_at`, `editing_session_key`)
   - `super().dispatch()` را فراخوانی می‌کند

#### `form_valid(self, form) -> HttpResponse`

**توضیح**: Clear کردن edit lock بعد از ذخیره موفق

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().form_valid()`

**منطق**:
1. `super().form_valid()` را فراخوانی می‌کند
2. `_clear_edit_lock()` را فراخوانی می‌کند
3. نتیجه را برمی‌گرداند

#### `form_invalid(self, form) -> HttpResponse`

**توضیح**: نگه داشتن edit lock در صورت خطای validation (کاربر هنوز در حال ویرایش است)

**پارامترهای ورودی**:
- `form`: فرم نامعتبر

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().form_invalid()`

#### `_clear_edit_lock(self) -> None`

**توضیح**: Clear کردن edit lock برای object فعلی

**منطق**:
1. اگر `self.object` وجود داشته باشد و دارای `clear_edit_lock()` method باشد:
   - `clear_edit_lock()` را فراخوانی می‌کند

#### `_get_edit_lock_redirect_url(self) -> str`

**توضیح**: دریافت URL برای redirect زمانی که edit lock فعال است

**مقدار بازگشتی**:
- `str`: URL برای redirect

**منطق** (اولویت‌بندی):
1. اگر `edit_lock_redirect_url_name` تنظیم شده باشد، از آن استفاده می‌کند
2. اگر `list_url_name` وجود داشته باشد، از آن استفاده می‌کند
3. اگر `success_url` وجود داشته باشد، از آن استفاده می‌کند (با handle کردن reverse_lazy)
4. اگر `get_success_url()` method وجود داشته باشد، از آن استفاده می‌کند
5. اگر object دارای `get_absolute_url()` باشد، از آن استفاده می‌کند
6. در غیر این صورت، `/` را برمی‌گرداند

---

## Base View Classes

### `BaseListView`

**توضیح**: Base ListView با قابلیت‌های مشترک برای تمام ماژول‌ها

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- Automatic search filtering
- Status filtering
- Company filtering
- Permission filtering
- Standard context setup
- Pagination

**Type**: `FeaturePermissionRequiredMixin, PermissionFilterMixin, CompanyScopedViewMixin, ListView`

**Attributes**:
- `model`: Model class (باید در subclass تنظیم شود)
- `feature_code`: Feature code برای permission checking
- `search_fields`: لیست فیلدها برای search
- `filter_fields`: لیست فیلدها برای filtering
- `permission_field`: نام فیلد برای permission checking (پیش‌فرض: `'created_by'`)
- `default_status_filter`: آیا status filter فعال باشد (پیش‌فرض: `True`)
- `default_order_by`: لیست فیلدها برای ordering
- `paginate_by`: تعداد items در هر صفحه (پیش‌فرض: `50`)
- `template_name`: `'shared/generic/generic_list.html'`
- `context_object_name`: `'object_list'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: ساخت queryset با filters، search، و permissions

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. queryset پایه را با `get_base_queryset()` دریافت می‌کند
2. company filter را اعمال می‌کند
3. permission filtering را اعمال می‌کند (اگر `feature_code` و `permission_field` تنظیم شده باشند)
4. prefetch_related و select_related را اعمال می‌کند
5. search را اعمال می‌کند (اگر `search_query` و `search_fields` وجود داشته باشند)
6. status filter را اعمال می‌کند (اگر `default_status_filter=True` باشد)
7. custom filters را با `apply_custom_filters()` اعمال می‌کند
8. ordering را اعمال می‌کند (اگر `default_order_by` تنظیم شده باشد)
9. queryset را برمی‌گرداند

#### `get_base_queryset(self) -> QuerySet`

**توضیح**: دریافت queryset پایه. باید در subclass override شود برای custom filtering

**مقدار بازگشتی**:
- `QuerySet`: `self.model.objects.all()`

#### `get_prefetch_related(self) -> List[str]`

**توضیح**: لیست فیلدها برای prefetch. باید در subclass override شود

**مقدار بازگشتی**:
- `List[str]`: لیست خالی (پیش‌فرض)

#### `get_select_related(self) -> List[str]`

**توضیح**: لیست فیلدها برای select_related. باید در subclass override شود

**مقدار بازگشتی**:
- `List[str]`: لیست خالی (پیش‌فرض)

#### `apply_custom_filters(self, queryset: QuerySet) -> QuerySet`

**توضیح**: اعمال custom filters. باید در subclass override شود

**پارامترهای ورودی**:
- `queryset`: queryset برای فیلتر کردن

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق پیش‌فرض**:
1. اگر `filter_fields` تنظیم شده باشد:
   - filter_map را ایجاد می‌کند
   - `apply_multi_field_filter()` را فراخوانی می‌کند
2. queryset را برمی‌گرداند

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: تنظیم context استاندارد برای list view

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل page_title, breadcrumbs, create_url, filters, actions, empty_state, stats

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `page_title` را با `get_page_title()` اضافه می‌کند
3. `breadcrumbs` را با `get_breadcrumbs()` اضافه می‌کند
4. `create_url` و `create_button_text` را اضافه می‌کند
5. filter configuration را اضافه می‌کند (`show_filters`, `status_filter`, `search_placeholder`, `clear_filter_url`)
6. actions configuration را اضافه می‌کند (`show_actions`, `feature_code`, `detail_url_name`, `edit_url_name`, `delete_url_name`)
7. empty state را اضافه می‌کند (`empty_state_title`, `empty_state_message`, `empty_state_icon`)
8. stats را اضافه می‌کند (اگر `get_stats()` مقدار برگرداند)
9. context را برمی‌گرداند

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `self.model._meta.verbose_name_plural` (پیش‌فرض)

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs. باید در subclass override شود

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs پیش‌فرض شامل Dashboard و page title

#### `get_create_url(self) -> Optional[str]`

**توضیح**: URL ایجاد. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `None` (پیش‌فرض)

#### `get_create_button_text(self) -> str`

**توضیح**: متن دکمه ایجاد. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('Create')` (پیش‌فرض)

#### `get_search_placeholder(self) -> str`

**توضیح**: placeholder برای search. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('Search...')` (پیش‌فرض)

#### `get_clear_filter_url(self) -> str`

**توضیح**: URL برای clear کردن filters. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: URL name فعلی (پیش‌فرض)

#### `get_detail_url_name(self) -> Optional[str]`

**توضیح**: نام URL جزئیات. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `None` (پیش‌فرض)

#### `get_edit_url_name(self) -> Optional[str]`

**توضیح**: نام URL ویرایش. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `None` (پیش‌فرض)

#### `get_delete_url_name(self) -> Optional[str]`

**توضیح**: نام URL حذف. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `None` (پیش‌فرض)

#### `get_empty_state_title(self) -> str`

**توضیح**: عنوان حالت خالی. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('No items found')` (پیش‌فرض)

#### `get_empty_state_message(self) -> str`

**توضیح**: پیام حالت خالی. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('Start by creating your first item.')` (پیش‌فرض)

#### `get_empty_state_icon(self) -> str`

**توضیح**: آیکون حالت خالی. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `'📋'` (پیش‌فرض)

#### `get_stats(self) -> Optional[Dict[str, int]]`

**توضیح**: Dictionary از stats. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[Dict[str, int]]`: `None` (پیش‌فرض)

#### `get_stats_labels(self) -> Dict[str, str]`

**توضیح**: Dictionary از stats labels. باید در subclass override شود

**مقدار بازگشتی**:
- `Dict[str, str]`: `{}` (پیش‌فرض)

---

### `BaseCreateView`

**توضیح**: Base CreateView با قابلیت‌های مشترک برای تمام ماژول‌ها

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- Automatic company_id و created_by setting
- Success message display
- Standard context setup
- Form kwargs با company_id

**Type**: `FeaturePermissionRequiredMixin, AutoSetFieldsMixin, SuccessMessageMixin, CompanyScopedViewMixin, CreateView`

**Attributes**:
- `model`: Model class (باید در subclass تنظیم شود)
- `form_class`: Form class (باید در subclass تنظیم شود)
- `success_url`: URL برای redirect بعد از ایجاد موفق
- `feature_code`: Feature code برای permission checking
- `template_name`: `'shared/generic/generic_form.html'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: اضافه کردن company_id به form kwargs

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs شامل `company_id` (اگر وجود داشته باشد)

**منطق**:
1. kwargs پایه را از `super().get_form_kwargs()` دریافت می‌کند
2. `active_company_id` را از session دریافت می‌کند
3. اگر `company_id` وجود داشته باشد، آن را به kwargs اضافه می‌کند
4. kwargs را برمی‌گرداند

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: تنظیم context استاندارد برای create view

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل form_title, breadcrumbs, cancel_url

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `form_title` را با `get_form_title()` اضافه می‌کند
3. `breadcrumbs` را با `get_breadcrumbs()` اضافه می‌کند
4. `cancel_url` را با `get_cancel_url()` اضافه می‌کند
5. context را برمی‌گرداند

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('Create {model}')` (پیش‌فرض)

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs. باید در subclass override شود

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs پیش‌فرض شامل Dashboard، model verbose_name_plural، و Create

#### `get_cancel_url(self) -> Optional[str]`

**توضیح**: URL لغو. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `self.success_url` (پیش‌فرض)

---

### `BaseUpdateView`

**توضیح**: Base UpdateView با قابلیت‌های مشترک برای تمام ماژول‌ها

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- Edit lock protection
- Automatic edited_by setting
- Success message display
- Standard context setup
- Form kwargs با company_id

**Type**: `EditLockProtectedMixin, FeaturePermissionRequiredMixin, AutoSetFieldsMixin, SuccessMessageMixin, CompanyScopedViewMixin, UpdateView`

**Attributes**:
- `model`: Model class (باید در subclass تنظیم شود)
- `form_class`: Form class (باید در subclass تنظیم شود)
- `success_url`: URL برای redirect بعد از ویرایش موفق
- `feature_code`: Feature code برای permission checking
- `template_name`: `'shared/generic/generic_form.html'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: اضافه کردن company_id به form kwargs (مشابه BaseCreateView)

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: تنظیم context استاندارد برای update view (مشابه BaseCreateView)

#### `get_form_title(self) -> str`

**توضیح**: عنوان فرم. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('Edit {model}')` (پیش‌فرض)

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs. باید در subclass override شود

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs پیش‌فرض شامل Dashboard، model verbose_name_plural، و Edit

#### `get_cancel_url(self) -> Optional[str]`

**توضیح**: URL لغو. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `self.success_url` (پیش‌فرض)

---

### `BaseDeleteView`

**توضیح**: Base DeleteView با قابلیت‌های مشترک برای تمام ماژول‌ها

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- Success message display
- Standard context setup
- Object details display

**Type**: `FeaturePermissionRequiredMixin, SuccessMessageMixin, CompanyScopedViewMixin, DeleteView`

**Attributes**:
- `model`: Model class (باید در subclass تنظیم شود)
- `success_url`: URL برای redirect بعد از حذف موفق
- `feature_code`: Feature code برای permission checking
- `template_name`: `'shared/generic/generic_confirm_delete.html'`

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: تنظیم context استاندارد برای delete view

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل delete_title, confirmation_message, breadcrumbs, object_details, cancel_url

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `delete_title` را با `get_delete_title()` اضافه می‌کند
3. `confirmation_message` را با `get_confirmation_message()` اضافه می‌کند
4. `breadcrumbs` را با `get_breadcrumbs()` اضافه می‌کند
5. `object_details` را با `get_object_details()` اضافه می‌کند
6. `cancel_url` را با `get_cancel_url()` اضافه می‌کند
7. context را برمی‌گرداند

#### `get_delete_title(self) -> str`

**توضیح**: عنوان صفحه حذف. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('Delete {model}')` (پیش‌فرض)

#### `get_confirmation_message(self) -> str`

**توضیح**: پیام تأیید. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `_('Are you sure you want to delete this {model}? This action cannot be undone.')` (پیش‌فرض)

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs. باید در subclass override شود

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs پیش‌فرض شامل Dashboard، model verbose_name_plural، و Delete

#### `get_object_details(self) -> List[Dict[str, Any]]`

**توضیح**: جزئیات object برای نمایش. باید در subclass override شود

**مقدار بازگشتی**:
- `List[Dict[str, Any]]`: لیست جزئیات پیش‌فرض شامل `public_code` (اگر وجود داشته باشد) و `name` (اگر وجود داشته باشد)

**منطق پیش‌فرض**:
1. لیست `details` را ایجاد می‌کند
2. اگر object دارای `public_code` باشد، آن را اضافه می‌کند
3. اگر object دارای `name` باشد، آن را اضافه می‌کند
4. لیست را برمی‌گرداند

#### `get_cancel_url(self) -> Optional[str]`

**توضیح**: URL لغو. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `self.success_url` (پیش‌فرض)

#### `validate_deletion(self) -> tuple[bool, Optional[str]]`

**توضیح**: اعتبارسنجی اینکه آیا object می‌تواند حذف شود. باید در subclass override شود

**مقدار بازگشتی**:
- `tuple[bool, Optional[str]]`: Tuple شامل (is_valid, error_message)

**منطق پیش‌فرض**:
- `(True, None)` برمی‌گرداند

---

### `BaseDetailView`

**توضیح**: Base DetailView با قابلیت‌های مشترک برای تمام ماژول‌ها

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- Permission filtering
- Standard context setup
- Edit permission check

**Type**: `FeaturePermissionRequiredMixin, PermissionFilterMixin, CompanyScopedViewMixin, DetailView`

**Attributes**:
- `model`: Model class (باید در subclass تنظیم شود)
- `feature_code`: Feature code برای permission checking
- `template_name`: `'shared/generic/generic_detail.html'`
- `context_object_name`: `'object'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: فیلتر queryset بر اساس permissions

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. queryset پایه را از `super().get_queryset()` دریافت می‌کند
2. اگر `feature_code` و `permission_field` تنظیم شده باشند:
   - permission filtering را با `filter_queryset_by_permissions()` اعمال می‌کند
3. queryset را برمی‌گرداند

#### `permission_field` (property) -> str

**توضیح**: نام فیلد برای permission checking. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `'created_by'` (پیش‌فرض)

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: تنظیم context استاندارد برای detail view

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل page_title, breadcrumbs, list_url, edit_url, can_edit, feature_code

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. `page_title` را با `get_page_title()` اضافه می‌کند
3. `breadcrumbs` را با `get_breadcrumbs()` اضافه می‌کند
4. `list_url` را با `get_list_url()` اضافه می‌کند
5. `edit_url` را با `get_edit_url()` اضافه می‌کند
6. `can_edit` را با `can_edit_object()` اضافه می‌کند
7. `feature_code` را اضافه می‌کند
8. context را برمی‌گرداند

#### `get_page_title(self) -> str`

**توضیح**: عنوان صفحه. باید در subclass override شود

**مقدار بازگشتی**:
- `str`: `str(self.object)` (پیش‌فرض)

#### `get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]`

**توضیح**: لیست breadcrumbs. باید در subclass override شود

**مقدار بازگشتی**:
- `List[Dict[str, Optional[str]]]`: لیست breadcrumbs پیش‌فرض شامل Dashboard، model verbose_name_plural، و View

#### `get_list_url(self) -> Optional[str]`

**توضیح**: URL لیست. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `None` (پیش‌فرض)

#### `get_edit_url(self) -> Optional[str]`

**توضیح**: URL ویرایش. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[str]`: `None` (پیش‌فرض)

#### `can_edit_object(self, obj=None, feature_code=None) -> bool`

**توضیح**: بررسی اینکه آیا object می‌تواند ویرایش شود. باید در subclass override شود

**پارامترهای ورودی**:
- `obj`: Object برای بررسی (اختیاری، پیش‌فرض: `self.object`)
- `feature_code`: Feature code (اختیاری، پیش‌فرض: `self.feature_code`)

**مقدار بازگشتی**:
- `bool`: `True` اگر object قابل ویرایش باشد

**منطق پیش‌فرض**:
1. از `obj` یا `self.object` استفاده می‌کند
2. اگر object دارای `is_locked` باشد، بررسی می‌کند که قفل نباشد
3. در غیر این صورت `True` برمی‌گرداند

---

## Formset View Classes

### `BaseFormsetCreateView`

**توضیح**: Base CreateView با پشتیبانی از formset

این کلاس `BaseCreateView` را گسترش می‌دهد تا formset را برای related objects مدیریت کند.

**Type**: `BaseCreateView`

**Attributes**:
- `formset_class`: Formset class (باید در subclass تنظیم شود)
- `formset_prefix`: Prefix برای formset (پیش‌فرض: `'formset'`)

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن formset به context

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل formset

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. اگر request method POST باشد:
   - formset را با POST data ایجاد می‌کند
3. در غیر این صورت:
   - formset خالی ایجاد می‌کند
4. formset را به context با نام `'formset'` اضافه می‌کند
5. context را برمی‌گرداند

#### `get_formset_kwargs(self) -> Dict[str, Any]`

**توضیح**: برگرداندن kwargs برای formset. باید در subclass override شود

**مقدار بازگشتی**:
- `Dict[str, Any]`: Dictionary از kwargs برای formset

**منطق پیش‌فرض**:
1. اگر `self.object` وجود داشته باشد، `{'instance': self.object}` را برمی‌گرداند
2. در غیر این صورت، `{}` را برمی‌گرداند

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره form و formset

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق** (با `@transaction.atomic`):
1. object اصلی را با `super().form_valid()` ذخیره می‌کند
2. formset را با instance جدید دوباره ایجاد می‌کند
3. اگر formset معتبر باشد:
   - formset را ذخیره می‌کند
4. در غیر این صورت:
   - `form_invalid` برمی‌گرداند
5. redirect به success_url برمی‌گرداند

---

### `BaseFormsetUpdateView`

**توضیح**: Base UpdateView با پشتیبانی از formset

این کلاس `BaseUpdateView` را گسترش می‌دهد تا formset را برای related objects مدیریت کند.

**Type**: `BaseUpdateView`

**Attributes**:
- `formset_class`: Formset class (باید در subclass تنظیم شود)
- `formset_prefix`: Prefix برای formset (پیش‌فرض: `'formset'`)

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن formset به context (مشابه BaseFormsetCreateView)

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. اگر request method POST باشد:
   - formset را با POST data و `instance=self.object` ایجاد می‌کند
3. در غیر این صورت:
   - formset را با `instance=self.object` ایجاد می‌کند
4. formset را به context اضافه می‌کند
5. context را برمی‌گرداند

#### `get_formset_kwargs(self) -> Dict[str, Any]`

**توضیح**: برگرداندن kwargs برای formset. باید در subclass override شود

**مقدار بازگشتی**:
- `Dict[str, Any]`: `{}` (پیش‌فرض)

**منطق پیش‌فرض**:
- Dictionary خالی برمی‌گرداند (باید در subclass override شود برای اضافه کردن kwargs مورد نیاز)

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره form و formset (مشابه BaseFormsetCreateView)

**منطق** (با `@transaction.atomic`):
1. object اصلی را با `super().form_valid()` ذخیره می‌کند
2. formset را با instance دوباره ایجاد می‌کند
3. اگر formset معتبر باشد:
   - formset را ذخیره می‌کند
4. در غیر این صورت:
   - `form_invalid` برمی‌گرداند
5. redirect به success_url برمی‌گرداند

---

## Document View Classes

### `BaseDocumentListView`

**توضیح**: Base ListView برای documents با lines (Receipts, Issues, etc.)

این کلاس `BaseListView` را گسترش می‌دهد تا:
- Prefetch lines و related objects
- Stats calculation

**Type**: `BaseListView`

**Attributes**:
- `prefetch_lines`: آیا lines را prefetch کند (پیش‌فرض: `True`)
- `stats_enabled`: آیا stats را محاسبه کند (پیش‌فرض: `True`)

**متدها**:

#### `get_prefetch_related(self) -> List[str]`

**توضیح**: Prefetch lines و related objects

**مقدار بازگشتی**:
- `List[str]`: لیست فیلدها برای prefetch

**منطق**:
1. prefetch پایه را از `super().get_prefetch_related()` دریافت می‌کند
2. اگر `prefetch_lines=True` باشد:
   - سعی می‌کند relationship lines را پیدا کند:
     - `'lines'`
     - `'line_set'`
     - `'{model_name}_line_set'`
     - `'{model_name}line_set'`
   - اولین relationship موجود را به prefetch اضافه می‌کند
3. prefetch را برمی‌گرداند

#### `get_stats(self) -> Optional[Dict[str, int]]`

**توضیح**: محاسبه stats برای documents. باید در subclass override شود

**مقدار بازگشتی**:
- `Optional[Dict[str, int]]`: Dictionary از stats یا `None`

**منطق پیش‌فرض**:
1. اگر `stats_enabled=False` باشد، `None` برمی‌گرداند
2. `active_company_id` را از session دریافت می‌کند
3. اگر `company_id` وجود نداشته باشد، `None` برمی‌گرداند
4. base queryset را با company filter دریافت می‌کند
5. stats را با `{'total': count}` ایجاد می‌کند
6. اگر model دارای `status` field باشد:
   - status-based stats را با `Count` اضافه می‌کند
7. stats را برمی‌گرداند

#### `get_stats_labels(self) -> Dict[str, str]`

**توضیح**: برگرداندن stats labels. باید در subclass override شود

**مقدار بازگشتی**:
- `Dict[str, str]`: `{}` (پیش‌فرض)

---

### `BaseDocumentCreateView`

**توضیح**: Base CreateView برای documents با lines

این کلاس `BaseFormsetCreateView` را گسترش می‌دهد تا document headers و lines را مدیریت کند.

**Type**: `BaseFormsetCreateView`

**متدها**:

#### `save_lines_formset(self, formset) -> None`

**توضیح**: ذخیره lines formset. باید در subclass override شود برای custom logic

**پارامترهای ورودی**:
- `formset`: formset برای ذخیره

**منطق پیش‌فرض**:
1. اگر formset معتبر باشد:
   - formset را ذخیره می‌کند
2. در غیر این صورت:
   - `ValueError` می‌اندازد

---

### `BaseDocumentUpdateView`

**توضیح**: Base UpdateView برای documents با lines

این کلاس `BaseFormsetUpdateView` را گسترش می‌دهد تا document headers و lines را مدیریت کند.

**Type**: `BaseFormsetUpdateView`

**متدها**:

#### `save_lines_formset(self, formset) -> None`

**توضیح**: ذخیره lines formset (مشابه BaseDocumentCreateView)

---

## Nested Formset View Classes

### `BaseNestedFormsetCreateView`

**توضیح**: Base CreateView با پشتیبانی از nested formset

این کلاس `BaseFormsetCreateView` را گسترش می‌دهد تا nested formsets را مدیریت کند (مثلاً BOM materials با alternative materials).

**Type**: `BaseFormsetCreateView`

**Attributes**:
- `nested_formset_class`: Nested formset class (باید در subclass تنظیم شود)
- `nested_formset_prefix_template`: Template برای prefix (پیش‌فرض: `'nested_{parent_pk}'`)

**متدها**:

#### `get_nested_formset_kwargs(self, parent_instance) -> Dict[str, Any]`

**توضیح**: برگرداندن kwargs برای nested formset. باید در subclass override شود

**پارامترهای ورودی**:
- `parent_instance`: Parent instance برای nested formset

**مقدار بازگشتی**:
- `Dict[str, Any]`: `{}` (پیش‌فرض)

#### `get_nested_formset_prefix(self, parent_instance) -> str`

**توضیح**: برگرداندن prefix برای nested formset

**پارامترهای ورودی**:
- `parent_instance`: Parent instance

**مقدار بازگشتی**:
- `str`: prefix با `parent_pk` (اگر وجود داشته باشد) یا `'nested'`

**منطق**:
1. اگر `parent_instance` دارای `pk` باشد:
   - prefix را با `nested_formset_prefix_template.format(parent_pk=parent_instance.pk)` ایجاد می‌کند
2. در غیر این صورت:
   - `'nested'` را برمی‌گرداند

#### `save_nested_formsets(self, parent_instances: List[Any]) -> None`

**توضیح**: ذخیره nested formsets برای هر parent instance

**پارامترهای ورودی**:
- `parent_instances`: لیست parent instances که نیاز به nested formsets دارند

**منطق**:
1. اگر `nested_formset_class` تنظیم نشده باشد، return می‌کند
2. برای هر parent_instance:
   - اگر `pk` وجود نداشته باشد، skip می‌کند
   - prefix را با `get_nested_formset_prefix()` دریافت می‌کند
   - nested formset را با POST data ایجاد می‌کند
   - اگر formset معتبر باشد:
     - formset را ذخیره می‌کند
   - در غیر این صورت:
     - warning message نمایش می‌دهد

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره form، formset، و nested formsets

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق** (با `@transaction.atomic`):
1. object اصلی را با `form.save()` ذخیره می‌کند
2. formset را با instance جدید ایجاد می‌کند
3. اگر formset معتبر باشد:
   - instances را با `formset.save(commit=False)` دریافت می‌کند
   - برای هر instance:
     - `process_formset_instance()` را فراخوانی می‌کند
     - اگر instance برگردانده شود، آن را ذخیره می‌کند
   - deleted objects را حذف می‌کند
   - nested formsets را با `save_nested_formsets()` ذخیره می‌کند
4. در غیر این صورت:
   - `form_invalid` برمی‌گرداند
5. redirect به success_url برمی‌گرداند

#### `process_formset_instance(self, instance) -> Optional[Any]`

**توضیح**: پردازش formset instance قبل از ذخیره. باید در subclass override شود

**پارامترهای ورودی**:
- `instance`: Instance برای پردازش

**مقدار بازگشتی**:
- `Optional[Any]`: Instance برای ذخیره، یا `None` برای skip

**منطق پیش‌فرض**:
- instance را بدون تغییر برمی‌گرداند

---

### `BaseNestedFormsetUpdateView`

**توضیح**: Base UpdateView با پشتیبانی از nested formset

این کلاس `BaseFormsetUpdateView` را گسترش می‌دهد تا nested formsets را مدیریت کند.

**Type**: `BaseFormsetUpdateView`

**Attributes**:
- `nested_formset_class`: Nested formset class (باید در subclass تنظیم شود)
- `nested_formset_prefix_template`: Template برای prefix (پیش‌فرض: `'nested_{parent_pk}'`)

**متدها**:

#### `get_nested_formset_kwargs(self, parent_instance) -> Dict[str, Any]`

**توضیح**: برگرداندن kwargs برای nested formset (مشابه BaseNestedFormsetCreateView)

#### `get_nested_formset_prefix(self, parent_instance) -> str`

**توضیح**: برگرداندن prefix برای nested formset (مشابه BaseNestedFormsetCreateView)

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن nested formsets به context

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل nested_formsets

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. اگر `nested_formset_class` و `self.object` وجود داشته باشند:
   - سعی می‌کند parent relationship را پیدا کند (`materials`, `lines`, یا `items`)
   - برای هر parent instance:
     - nested formset را ایجاد می‌کند (با POST data اگر POST باشد)
     - nested formset را به dictionary با key `parent_instance.pk` اضافه می‌کند
   - `nested_formsets` را به context اضافه می‌کند
3. context را برمی‌گرداند

#### `save_nested_formsets(self, nested_formsets: Dict[int, Any]) -> None`

**توضیح**: ذخیره nested formsets

**پارامترهای ورودی**:
- `nested_formsets`: Dictionary از nested formsets با key parent instance pk

**منطق**:
1. برای هر nested formset:
   - اگر formset معتبر باشد:
     - formset را ذخیره می‌کند
   - در غیر این صورت:
     - warning message نمایش می‌دهد

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره form، formset، و nested formsets

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق** (با `@transaction.atomic`):
1. object اصلی را با `form.save()` ذخیره می‌کند
2. formset را با instance ایجاد می‌کند
3. اگر formset معتبر باشد:
   - instances را با `formset.save(commit=False)` دریافت می‌کند
   - برای هر instance:
     - `process_formset_instance()` را فراخوانی می‌کند
     - اگر instance برگردانده شود، آن را ذخیره می‌کند
   - deleted objects را حذف می‌کند
   - nested formsets را از context دریافت می‌کند
   - nested formsets را با `save_nested_formsets()` ذخیره می‌کند
4. در غیر این صورت:
   - `form_invalid` برمی‌گرداند
5. redirect به success_url برمی‌گرداند

#### `process_formset_instance(self, instance) -> Optional[Any]`

**توضیح**: پردازش formset instance قبل از ذخیره (مشابه BaseNestedFormsetCreateView)

---

## وابستگی‌ها

- `shared.models`: `User`, `UserCompanyAccess`, `AccessLevel`, `AccessLevelPermission`
- `shared.forms`: `UserCompanyAccessFormSet`
- `shared.permissions`: `FEATURE_PERMISSION_MAP`, `PermissionAction`
- `shared.mixins`: `FeaturePermissionRequiredMixin`, `PermissionFilterMixin`, `CompanyScopedViewMixin`, `AutoSetFieldsMixin`, `SuccessMessageMixin`
- `shared.filters`: `apply_search`, `apply_status_filter`, `apply_company_filter`, `apply_multi_field_filter`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`, `DetailView`
- `django.db.models`: `QuerySet`, `Prefetch`
- `django.urls`: `reverse_lazy`, `reverse`
- `django.utils`: `timezone`
- `django.utils.translation`: `gettext_lazy as _`
- `django.contrib`: `messages`
- `django.http`: `HttpResponseRedirect`, `HttpResponse`
- `django.db`: `transaction`

---

## استفاده در پروژه

### استفاده از Base Views

```python
from shared.views.base import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code', 'name_en']
    filter_fields = ['is_enabled']
    feature_code = 'inventory.master.item_types'
    permission_field = 'created_by'
    default_order_by = ['public_code']
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Item Types'), 'url': None},
        ]

class ItemTypeCreateView(BaseCreateView):
    model = ItemType
    form_class = ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item type created successfully.')

class ItemTypeUpdateView(BaseUpdateView):
    model = ItemType
    form_class = ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item type updated successfully.')

class ItemTypeDeleteView(BaseDeleteView):
    model = ItemType
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item type deleted successfully.')
```

### استفاده از Formset Views

```python
from shared.views.base import BaseFormsetCreateView, BaseFormsetUpdateView

class BOMCreateView(BaseFormsetCreateView):
    model = BOM
    form_class = BOMForm
    formset_class = BOMMaterialLineFormSet
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    
    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

### استفاده از Document Views

```python
from shared.views.base import BaseDocumentListView, BaseDocumentCreateView, BaseDocumentUpdateView

class ReceiptPermanentListView(BaseDocumentListView):
    model = ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    prefetch_lines = True
    stats_enabled = True
    
    def get_stats(self):
        stats = super().get_stats()
        # Add custom stats
        return stats

class ReceiptPermanentCreateView(BaseDocumentCreateView):
    model = ReceiptPermanent
    form_class = ReceiptPermanentForm
    formset_class = ReceiptPermanentLineFormSet
    success_url = reverse_lazy('inventory:receipt_permanent')
    feature_code = 'inventory.receipts.permanent'
```

### استفاده از Nested Formset Views

```python
from shared.views.base import BaseNestedFormsetCreateView

class BOMCreateView(BaseNestedFormsetCreateView):
    model = BOM
    form_class = BOMForm
    formset_class = BOMMaterialLineFormSet
    nested_formset_class = BOMMaterialAlternativeFormSet
    nested_formset_prefix_template = 'alternatives_{parent_pk}'
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    
    def get_nested_formset_kwargs(self, parent_instance):
        return {
            'company_id': self.request.session.get('active_company_id'),
            'bom_material_id': parent_instance.pk
        }
```

---

## نکات مهم

1. **Permission System**: تمام Base views از سیستم permission استفاده می‌کنند و بر اساس `feature_code` و `permission_field` دسترسی را بررسی می‌کنند

2. **Company Scoping**: تمام Base views به صورت خودکار queryset را بر اساس `active_company_id` از session فیلتر می‌کنند

3. **Edit Lock Protection**: `BaseUpdateView` از `EditLockProtectedMixin` استفاده می‌کند تا از ویرایش همزمان جلوگیری کند

4. **Transaction Safety**: تمام متدهای `form_valid()` در Formset views با `@transaction.atomic` محافظت می‌شوند

5. **Hook Methods**: تمام Base views دارای hook methods هستند که می‌توانند در subclass override شوند برای custom behavior

6. **Template Configuration**: تمام Base views از generic templates استفاده می‌کنند که در `shared/generic/` قرار دارند

7. **Context Standardization**: تمام Base views context استاندارد را تنظیم می‌کنند که برای generic templates استفاده می‌شود

8. **Formset Prefixes**: هنگام استفاده از چند formset، باید prefixهای مختلف استفاده شود

9. **Nested Formsets**: `BaseNestedFormsetCreateView` و `BaseNestedFormsetUpdateView` از prefix template استفاده می‌کنند برای nested formsets

10. **Stats Calculation**: `BaseDocumentListView` به صورت خودکار stats را محاسبه می‌کند اگر `stats_enabled=True` باشد

11. **Prefetch Optimization**: `BaseDocumentListView` به صورت خودکار lines را prefetch می‌کند اگر `prefetch_lines=True` باشد

12. **Error Handling**: تمام Base views به صورت graceful با errors برخورد می‌کنند و messages مناسب نمایش می‌دهند

13. **Formset Validation**: در `BaseFormsetCreateView` و `BaseFormsetUpdateView`، اگر formset معتبر نباشد، `form_invalid()` فراخوانی می‌شود و فرم با خطاهای formset نمایش داده می‌شود

14. **Nested Formset Context**: در `BaseNestedFormsetUpdateView`، nested formsets در context با key `nested_formsets` (dictionary با key parent instance pk) اضافه می‌شوند

15. **Instance Processing**: در `BaseNestedFormsetCreateView` و `BaseNestedFormsetUpdateView`، می‌توانید `process_formset_instance()` را override کنید برای پردازش custom قبل از ذخیره هر instance

16. **Transaction Management**: تمام عملیات ذخیره در Formset views و Nested Formset views در یک transaction انجام می‌شوند تا consistency داده‌ها حفظ شود

17. **Edit Lock Timeout**: در `EditLockProtectedMixin`، edit locks قدیمی‌تر از 5 دقیقه به صورت خودکار clear می‌شوند

18. **Permission Field**: در `BaseDetailView`، `permission_field` به صورت property تعریف شده و می‌تواند در subclass override شود

19. **Stats Labels**: در `BaseListView` و `BaseDocumentListView`، می‌توانید `get_stats_labels()` را override کنید برای ترجمه labels stats

20. **Custom Queryset**: در تمام Base views، می‌توانید `get_base_queryset()` را override کنید برای custom base filtering قبل از اعمال filters دیگر

---

## Best Practices

### 1. Override Hook Methods به جای Override متدهای اصلی

**خوب**:
```python
class ItemListView(BaseListView):
    def get_page_title(self):
        return _('Item Catalog')
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Items'), 'url': None},
        ]
```

**بد**:
```python
class ItemListView(BaseListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Item Catalog')  # Avoid this
        return context
```

### 2. استفاده از `get_base_queryset()` برای Custom Filtering

```python
class ItemListView(BaseListView):
    def get_base_queryset(self):
        # Custom base filtering
        return super().get_base_queryset().filter(is_active=True)
```

### 3. استفاده از `apply_custom_filters()` برای Query Parameters

```python
class ItemListView(BaseListView):
    filter_fields = ['category', 'supplier']
    
    def apply_custom_filters(self, queryset):
        queryset = super().apply_custom_filters(queryset)
        # Additional custom filters
        if self.request.GET.get('low_stock'):
            queryset = queryset.filter(quantity__lt=F('min_quantity'))
        return queryset
```

### 4. Prefetch Optimization

```python
class ReceiptListView(BaseDocumentListView):
    def get_prefetch_related(self):
        prefetch = super().get_prefetch_related()
        prefetch.append('lines__item')
        prefetch.append('created_by')
        return prefetch
    
    def get_select_related(self):
        select = super().get_select_related()
        select.append('warehouse')
        select.append('supplier')
        return select
```

### 5. Custom Stats

```python
class ReceiptListView(BaseDocumentListView):
    def get_stats(self):
        stats = super().get_stats()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            stats['pending_qc'] = ReceiptTemporary.objects.filter(
                company_id=company_id,
                status='pending_qc'
            ).count()
        return stats
    
    def get_stats_labels(self):
        labels = super().get_stats_labels()
        labels['pending_qc'] = _('Pending QC')
        return labels
```

### 6. Formset با Custom Logic

```python
class BOMCreateView(BaseFormsetCreateView):
    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        # Custom validation before saving
        if not self._validate_bom_structure():
            return self.form_invalid(form)
        return super().form_valid(form)
```

### 7. Nested Formset با Custom Processing

```python
class BOMCreateView(BaseNestedFormsetCreateView):
    def process_formset_instance(self, instance):
        # Custom processing before saving
        if instance.quantity <= 0:
            return None  # Skip invalid instances
        instance.calculate_total_cost()
        return instance
```

---

## Troubleshooting

### مشکل: Permission Denied در List View

**علت**: `feature_code` تنظیم نشده یا permission وجود ندارد

**راه حل**:
```python
class ItemListView(BaseListView):
    feature_code = 'inventory.master.items'  # باید تنظیم شود
    permission_field = 'created_by'  # یا فیلد مناسب
```

### مشکل: Company Filter کار نمی‌کند

**علت**: `active_company_id` در session تنظیم نشده

**راه حل**: مطمئن شوید که `CompanyScopedViewMixin` استفاده شده و company در session تنظیم شده است

### مشکل: Edit Lock همیشه فعال است

**علت**: Edit lock clear نشده یا timeout قدیمی است

**راه حل**: 
- بررسی کنید که `form_valid()` یا `form_invalid()` به درستی فراخوانی می‌شود
- Timeout را در `edit_lock_timeout_minutes` تنظیم کنید

### مشکل: Formset Validation Failed

**علت**: Formset معتبر نیست یا POST data ناقص است

**راه حل**:
```python
def form_valid(self, form):
    formset = self.formset_class(
        self.request.POST,
        instance=self.object,
        prefix=self.formset_prefix,
        **self.get_formset_kwargs()
    )
    
    if not formset.is_valid():
        # Debug: بررسی خطاها
        print(formset.errors)
        print(formset.non_form_errors())
        return self.form_invalid(form)
    
    return super().form_valid(form)
```

### مشکل: Nested Formset در Context نیست

**علت**: در `BaseNestedFormsetUpdateView`، parent relationship پیدا نشده

**راه حل**: مطمئن شوید که relationship name درست است (`materials`, `lines`, یا `items`)

### مشکل: Stats نمایش داده نمی‌شود

**علت**: `stats_enabled=False` یا `get_stats()` مقدار `None` برمی‌گرداند

**راه حل**:
```python
class MyListView(BaseDocumentListView):
    stats_enabled = True  # باید True باشد
    
    def get_stats(self):
        stats = super().get_stats()
        if stats is None:
            return {}  # حداقل dictionary خالی برگردانید
        return stats
```

---

## Advanced Examples

### مثال 1: List View با Multiple Filters و Custom Search

```python
class ItemListView(BaseListView):
    model = Item
    search_fields = ['name', 'public_code', 'name_en', 'description']
    filter_fields = ['category', 'supplier', 'is_active']
    feature_code = 'inventory.master.items'
    permission_field = 'created_by'
    default_order_by = ['public_code']
    
    def apply_custom_filters(self, queryset):
        queryset = super().apply_custom_filters(queryset)
        
        # Custom date range filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Custom price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    def get_stats(self):
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return None
        
        base_qs = self.model.objects.filter(company_id=company_id)
        
        return {
            'total': base_qs.count(),
            'active': base_qs.filter(is_active=True).count(),
            'inactive': base_qs.filter(is_active=False).count(),
            'low_stock': base_qs.filter(quantity__lt=F('min_quantity')).count(),
        }
    
    def get_stats_labels(self):
        return {
            'total': _('Total Items'),
            'active': _('Active'),
            'inactive': _('Inactive'),
            'low_stock': _('Low Stock'),
        }
```

### مثال 2: Document Create View با Custom Line Processing

```python
class ReceiptCreateView(BaseDocumentCreateView):
    model = ReceiptPermanent
    form_class = ReceiptPermanentForm
    formset_class = ReceiptPermanentLineFormSet
    feature_code = 'inventory.receipts.permanent'
    
    def save_lines_formset(self, formset):
        """Custom line saving with validation."""
        if not formset.is_valid():
            raise ValueError("Formset is not valid")
        
        instances = formset.save(commit=False)
        for instance in instances:
            # Custom processing
            instance.calculate_line_total()
            instance.update_item_stock()
            instance.save()
        
        # Delete marked instances
        for obj in formset.deleted_objects:
            obj.delete()
```

### مثال 3: Nested Formset با Complex Logic

```python
class BOMCreateView(BaseNestedFormsetCreateView):
    model = BOM
    form_class = BOMForm
    formset_class = BOMMaterialLineFormSet
    nested_formset_class = BOMMaterialAlternativeFormSet
    nested_formset_prefix_template = 'alternatives_{parent_pk}'
    
    def process_formset_instance(self, instance):
        """Process material line before saving."""
        # Validate quantity
        if instance.quantity <= 0:
            messages.error(self.request, _('Quantity must be positive'))
            return None
        
        # Calculate cost
        instance.calculate_cost()
        
        # Validate availability
        if not instance.is_available():
            messages.warning(self.request, _('Material not available'))
        
        return instance
    
    def get_nested_formset_kwargs(self, parent_instance):
        """Custom kwargs for nested formset."""
        return {
            'company_id': self.request.session.get('active_company_id'),
            'bom_material_id': parent_instance.pk,
            'item_id': parent_instance.item_id,
        }
    
    def form_valid(self, form):
        """Custom validation before saving."""
        # Validate BOM structure
        if not self._validate_bom_structure():
            return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def _validate_bom_structure(self):
        """Custom BOM validation logic."""
        # Add your validation logic here
        return True
```

### مثال 4: Update View با Custom Deletion Validation

```python
class ItemDeleteView(BaseDeleteView):
    model = Item
    success_url = reverse_lazy('inventory:items')
    feature_code = 'inventory.master.items'
    
    def validate_deletion(self):
        """Check if item can be deleted."""
        # Check if item is used in receipts
        if self.object.receipt_lines.exists():
            return False, _('Item is used in receipts and cannot be deleted')
        
        # Check if item is used in issues
        if self.object.issue_lines.exists():
            return False, _('Item is used in issues and cannot be deleted')
        
        # Check if item has stock
        if self.object.quantity > 0:
            return False, _('Item has stock and cannot be deleted')
        
        return True, None
    
    def get_object_details(self):
        """Custom object details."""
        details = super().get_object_details()
        details.extend([
            {'label': _('Quantity'), 'value': self.object.quantity},
            {'label': _('Category'), 'value': self.object.category.name if self.object.category else '-'},
            {'label': _('Supplier'), 'value': self.object.supplier.name if self.object.supplier else '-'},
        ])
        return details
```

---

## Common Patterns

### Pattern 1: List View با Status Filter

```python
class DocumentListView(BaseDocumentListView):
    model = ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    default_status_filter = True  # فعال کردن status filter
    
    def get_stats(self):
        stats = super().get_stats()
        # Stats به صورت خودکار بر اساس status محاسبه می‌شود
        return stats
```

### Pattern 2: Create View با Auto-generated Code

```python
class ItemCreateView(BaseCreateView):
    model = Item
    form_class = ItemForm
    feature_code = 'inventory.master.items'
    
    def form_valid(self, form):
        # Generate code before saving
        if not form.instance.public_code:
            form.instance.public_code = self._generate_code()
        return super().form_valid(form)
    
    def _generate_code(self):
        # Custom code generation logic
        return f"ITEM-{timezone.now().strftime('%Y%m%d%H%M%S')}"
```

### Pattern 3: Update View با Conditional Fields

```python
class DocumentUpdateView(BaseUpdateView):
    model = ReceiptPermanent
    form_class = ReceiptPermanentForm
    feature_code = 'inventory.receipts.permanent'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['can_edit'] = not self.object.is_locked
        return kwargs
```

### Pattern 4: Detail View با Custom Actions

```python
class ReceiptDetailView(BaseDetailView):
    model = ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add custom actions
        context['custom_actions'] = []
        if self.object.can_approve():
            context['custom_actions'].append({
                'label': _('Approve'),
                'url': reverse('inventory:approve_receipt', args=[self.object.pk]),
            })
        
        return context
```

---

## Quick Reference

### Mixins

| Mixin | Purpose | Key Methods |
|-------|---------|-------------|
| `UserAccessFormsetMixin` | مدیریت UserCompanyAccess formsets | `get_access_formset()` |
| `AccessLevelPermissionMixin` | مدیریت access level permissions | `get_action_labels()`, `_prepare_feature_context()`, `_save_permissions()` |
| `EditLockProtectedMixin` | جلوگیری از ویرایش همزمان | `dispatch()`, `form_valid()`, `_clear_edit_lock()` |

### Base Views

| View | Purpose | Key Attributes | Key Methods |
|------|---------|----------------|-------------|
| `BaseListView` | List view با filtering و pagination | `model`, `feature_code`, `search_fields`, `filter_fields` | `get_queryset()`, `get_context_data()`, `get_stats()` |
| `BaseCreateView` | Create view با auto-set fields | `model`, `form_class`, `success_url`, `feature_code` | `get_form_kwargs()`, `get_context_data()` |
| `BaseUpdateView` | Update view با edit lock protection | `model`, `form_class`, `success_url`, `feature_code` | `get_form_kwargs()`, `get_context_data()` |
| `BaseDeleteView` | Delete view با validation | `model`, `success_url`, `feature_code` | `validate_deletion()`, `get_object_details()` |
| `BaseDetailView` | Detail view با permission check | `model`, `feature_code` | `get_queryset()`, `can_edit_object()` |

### Formset Views

| View | Purpose | Key Attributes | Key Methods |
|------|---------|----------------|-------------|
| `BaseFormsetCreateView` | Create view با formset | `formset_class`, `formset_prefix` | `get_formset_kwargs()`, `form_valid()` |
| `BaseFormsetUpdateView` | Update view با formset | `formset_class`, `formset_prefix` | `get_formset_kwargs()`, `form_valid()` |

### Document Views

| View | Purpose | Key Attributes | Key Methods |
|------|---------|----------------|-------------|
| `BaseDocumentListView` | List view برای documents | `prefetch_lines`, `stats_enabled` | `get_prefetch_related()`, `get_stats()` |
| `BaseDocumentCreateView` | Create view برای documents | - | `save_lines_formset()` |
| `BaseDocumentUpdateView` | Update view برای documents | - | `save_lines_formset()` |

### Nested Formset Views

| View | Purpose | Key Attributes | Key Methods |
|------|---------|----------------|-------------|
| `BaseNestedFormsetCreateView` | Create view با nested formset | `nested_formset_class`, `nested_formset_prefix_template` | `get_nested_formset_kwargs()`, `save_nested_formsets()`, `process_formset_instance()` |
| `BaseNestedFormsetUpdateView` | Update view با nested formset | `nested_formset_class`, `nested_formset_prefix_template` | `get_nested_formset_kwargs()`, `save_nested_formsets()`, `process_formset_instance()` |

### Common Hook Methods

| Method | Purpose | Return Type | Override When |
|--------|---------|-------------|---------------|
| `get_page_title()` | عنوان صفحه | `str` | نیاز به عنوان custom |
| `get_breadcrumbs()` | لیست breadcrumbs | `List[Dict]` | نیاز به breadcrumbs custom |
| `get_base_queryset()` | Queryset پایه | `QuerySet` | نیاز به custom filtering |
| `apply_custom_filters()` | اعمال custom filters | `QuerySet` | نیاز به filters اضافی |
| `get_prefetch_related()` | لیست فیلدها برای prefetch | `List[str]` | نیاز به optimization |
| `get_select_related()` | لیست فیلدها برای select_related | `List[str]` | نیاز به optimization |
| `get_stats()` | محاسبه stats | `Optional[Dict[str, int]]` | نیاز به stats custom |
| `get_stats_labels()` | Labels برای stats | `Dict[str, str]` | نیاز به ترجمه labels |
| `get_form_title()` | عنوان فرم | `str` | نیاز به عنوان custom |
| `get_cancel_url()` | URL لغو | `Optional[str]` | نیاز به URL custom |
| `get_object_details()` | جزئیات object | `List[Dict]` | نیاز به نمایش جزئیات بیشتر |
| `validate_deletion()` | اعتبارسنجی حذف | `tuple[bool, Optional[str]]` | نیاز به validation custom |
| `can_edit_object()` | بررسی امکان ویرایش | `bool` | نیاز به logic custom |
| `get_formset_kwargs()` | Kwargs برای formset | `Dict[str, Any]` | نیاز به kwargs اضافی |
| `process_formset_instance()` | پردازش instance قبل از ذخیره | `Optional[Any]` | نیاز به پردازش custom |

### Template Variables

#### List View Context
- `object_list`: لیست objects
- `page_title`: عنوان صفحه
- `breadcrumbs`: لیست breadcrumbs
- `create_url`: URL ایجاد
- `create_button_text`: متن دکمه ایجاد
- `show_filters`: نمایش filters
- `status_filter`: فعال بودن status filter
- `search_placeholder`: placeholder برای search
- `stats`: Dictionary از stats
- `stats_labels`: Dictionary از labels stats
- `empty_state_title`: عنوان حالت خالی
- `empty_state_message`: پیام حالت خالی
- `empty_state_icon`: آیکون حالت خالی

#### Form View Context (Create/Update)
- `form`: فرم Django
- `form_title`: عنوان فرم
- `breadcrumbs`: لیست breadcrumbs
- `cancel_url`: URL لغو
- `formset`: Formset (اگر استفاده شود)
- `nested_formsets`: Dictionary از nested formsets (اگر استفاده شود)

#### Detail View Context
- `object`: Object مورد نظر
- `page_title`: عنوان صفحه
- `breadcrumbs`: لیست breadcrumbs
- `list_url`: URL لیست
- `edit_url`: URL ویرایش
- `can_edit`: امکان ویرایش
- `feature_code`: Feature code برای permissions

#### Delete View Context
- `object`: Object مورد نظر
- `delete_title`: عنوان صفحه حذف
- `confirmation_message`: پیام تأیید
- `breadcrumbs`: لیست breadcrumbs
- `object_details`: لیست جزئیات object
- `cancel_url`: URL لغو

---

## Changelog

### Version 1.0
- مستندسازی کامل تمام Mixins
- مستندسازی کامل تمام Base Views
- مستندسازی کامل Formset Views
- مستندسازی کامل Document Views
- مستندسازی کامل Nested Formset Views
- اضافه شدن Best Practices
- اضافه شدن Troubleshooting Guide
- اضافه شدن Advanced Examples
- اضافه شدن Common Patterns
- اضافه شدن Quick Reference

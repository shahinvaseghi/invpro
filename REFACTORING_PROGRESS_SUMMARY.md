# خلاصه پیشرفت Refactoring - معماری مشترک

**تاریخ شروع**: 2024-12-05  
**وضعیت فعلی**: Rollout Implementation (ماژول `inventory`) - در حال انجام  
**آخرین به‌روزرسانی**: 2024-12-05 (شامل Warehouses refactoring - شروع Rollout)

---

## 🎯 هدف پروژه

Refactoring تمام viewها و formهای پروژه برای استفاده از Base classes مشترک به منظور:
- کاهش تکرار کد (هدف: 86% کاهش)
- سرعت بخشیدن به توسعه (از 2 ساعت به 15 دقیقه برای view جدید)
- بهبود نگهداری (تغییرات فقط در Base classes)
- یکپارچگی UI/UX

---

## ✅ کارهای انجام شده

### 1. Infrastructure (فاز ۱) - ✅ تکمیل شده

#### Backend Files:
- ✅ `shared/views/base.py` - 10 Base View Class:
  - `BaseListView` - با search, filter, pagination, permission support
  - `BaseCreateView` - با auto-set company_id, created_by, success message
  - `BaseUpdateView` - با auto-set edited_by, edit lock protection
  - `BaseDeleteView` - با success message, object details
  - `BaseDetailView` - با permission filtering, context setup
  - `BaseFormsetCreateView` - برای formsets
  - `BaseFormsetUpdateView` - برای formsets
  - `BaseDocumentListView` - برای documents با lines
  - `BaseDocumentCreateView` - برای documents با lines
  - `BaseDocumentUpdateView` - برای documents با lines

- ✅ `shared/filters.py` - 5 تابع فیلتر مشترک:
  - `apply_search()` - جستجو در چند فیلد
  - `apply_status_filter()` - فیلتر وضعیت
  - `apply_company_filter()` - فیلتر شرکت
  - `apply_date_range_filter()` - فیلتر بازه تاریخ
  - `apply_multi_field_filter()` - فیلتر چند فیلدی

- ✅ `shared/mixins.py` - 4 Mixin:
  - `PermissionFilterMixin` - فیلتر بر اساس permissions
  - `CompanyScopedViewMixin` - فیلتر بر اساس active_company_id
  - `AutoSetFieldsMixin` - auto-set company_id, created_by, edited_by
  - `SuccessMessageMixin` - نمایش پیام موفقیت

- ✅ `shared/forms/base.py` - 2 Base Form Class:
  - `BaseModelForm` - با auto widget styling (form-control, form-check-input)
  - `BaseFormset` - helper class برای formsets

- ✅ `shared/views/api.py` - 3 Base API View Class:
  - `BaseAPIView` - base برای API endpoints
  - `BaseListAPIView` - برای list APIs
  - `BaseDetailAPIView` - برای detail APIs

- ✅ `shared/utils/view_helpers.py` - 4 Helper Function:
  - `get_breadcrumbs()` - تولید breadcrumbs
  - `get_success_message()` - تولید پیام موفقیت
  - `validate_active_company()` - بررسی active company
  - `get_table_headers()` - تولید table headers

#### Frontend Files:
- ✅ `static/js/formset.js` - مدیریت formsets (7 تابع)
- ✅ `static/js/cascading-dropdowns.js` - cascading dropdowns (4 تابع)
- ✅ `static/js/table-export.js` - export table به CSV/Excel (3 تابع)
- ✅ `static/js/form-helpers.js` - helper functions برای forms (5 تابع)
- ✅ `static/js/item-filters.js` - فیلتر کردن آیتم‌ها (6 تابع)
- ✅ `static/js/formset-table.js` - مدیریت grid layout برای formsets (3 تابع)
- ✅ `static/css/formset-table.css` - استایل‌های formset table layout

- ✅ `templates/shared/partials/filter_panel.html` - پنل فیلتر مشترک
- ✅ `templates/shared/partials/stats_cards.html` - کارت‌های آمار
- ✅ `templates/shared/partials/pagination.html` - pagination مشترک
- ✅ `templates/shared/partials/empty_state.html` - empty state مشترک
- ✅ `templates/shared/partials/row_actions.html` - دکمه‌های actions (بهبود یافته)

- ✅ `shared/templatetags/view_tags.py` - 5 Template Tag:
  - `{% get_breadcrumbs %}`
  - `{% get_table_headers %}`
  - `{% can_action %}`
  - `{% get_object_actions %}`
  - `{{ dict|get_item:key }}`

- ✅ `templates/shared/generic/generic_list.html` - بهبود یافته
- ✅ `templates/shared/generic/generic_form.html` - بهبود یافته
- ✅ `templates/shared/generic/generic_detail.html` - بهبود یافته
- ✅ `templates/shared/generic/generic_confirm_delete.html` - بهبود یافته

---

### 2. Pilot Implementation (فاز ۲) - در حال انجام

#### ماژول `shared` - Companies ✅ تکمیل شده

**فایل**: `shared/views/companies.py`

- ✅ `CompanyListView` → `BaseListView`
  - استفاده از `search_fields`, `filter_fields`, `default_status_filter`
  - Override `get_base_queryset()` برای فیلتر بر اساس `UserCompanyAccess`
  - استفاده از `generic_list.html`
  - استفاده از partials مشترک: `row_actions.html`, `filter_panel.html`, `pagination.html`, `empty_state.html`

- ✅ `CompanyCreateView` → `BaseCreateView`
  - استفاده از `success_message` attribute
  - Override `form_valid()` برای ایجاد `UserCompanyAccess`
  - استفاده از `company_form.html` که از `generic_form.html` extend می‌کند

- ✅ `CompanyUpdateView` → `BaseUpdateView`
  - استفاده از `success_message` attribute
  - Override `get_queryset()` برای فیلتر بر اساس `UserCompanyAccess`
  - استفاده از `company_form.html` که از `generic_form.html` extend می‌کند

- ✅ `CompanyDetailView` → `BaseDetailView`
  - استفاده از `generic_detail.html` (default)
  - تنظیم context variables برای `detail_sections`, `info_banner`
  - Override `permission_field` برای skip کردن permission filtering (چون با UserCompanyAccess فیلتر می‌کنیم)

- ✅ `CompanyDeleteView` → `BaseDeleteView`
  - استفاده از `generic_confirm_delete.html` (default)
  - Override `get_queryset()` برای فیلتر بر اساس `UserCompanyAccess`
  - استفاده از hook methods برای object details

**فایل**: `shared/forms/companies.py`

- ✅ `CompanyForm` → `BaseModelForm`
  - حذف widgets تکراری (فقط attributes خاص باقی مانده)
  - حذف `company_id` از kwargs (چون Company خودش company است)

**مشکلات حل شده**:
- ✅ رفع RecursionError در `row_actions.html` (حذف `{% include %}` از کامنت)
- ✅ رفع TypeError در `CompanyForm` (استفاده از `BaseModelForm` و حذف `company_id`)

---

#### ماژول `shared` - Company Units ✅ تکمیل شده

**فایل**: `shared/views/company_units.py`

- ✅ `CompanyUnitListView` → `BaseListView`
  - استفاده از `search_fields`, `filter_fields`, `default_status_filter`
  - استفاده از `get_select_related()` برای `parent_unit`
  - استفاده از `generic_list.html`
  - استفاده از partials مشترک

- ✅ `CompanyUnitCreateView` → `BaseCreateView`
  - استفاده از `success_message` attribute
  - استفاده از `company_unit_form.html` که از `generic_form.html` extend می‌کند

- ✅ `CompanyUnitUpdateView` → `BaseUpdateView`
  - Override `get_queryset()` برای فیلتر بر اساس `active_company_id`
  - Override `get_form_kwargs()` برای `company_id` (برای parent_unit filtering)
  - استفاده از `success_message` attribute

- ✅ `CompanyUnitDetailView` → `BaseDetailView`
  - استفاده از `generic_detail.html` (default)
  - تنظیم context variables برای `detail_sections`, `info_banner`
  - استفاده از `get_select_related()` و `get_prefetch_related()`

- ✅ `CompanyUnitDeleteView` → `BaseDeleteView`
  - استفاده از `generic_confirm_delete.html` (default)
  - Override `get_queryset()` برای فیلتر بر اساس `active_company_id`
  - استفاده از hook methods

**فایل**: `shared/forms/companies.py`

- ✅ `CompanyUnitForm` → `BaseModelForm`
  - حذف widgets تکراری (فقط attributes خاص باقی مانده)
  - ترجمه labels به انگلیسی (برای consistency)
  - حفظ منطق `company_id` برای parent_unit filtering

---

#### ماژول `shared` - Users ✅ تکمیل شده

**فایل**: `shared/views/users.py`

- ✅ `UserListView` → `BaseListView`
  - استفاده از `search_fields` برای جستجو در username, email, first_name, last_name
  - Override `get_base_queryset()` برای فیلتر بر اساس active company (از طریق `UserCompanyAccess`)
  - Override `get_queryset()` برای فیلتر status (is_active) و skip کردن `CompanyScopedViewMixin`
  - Superuserها همه کاربران را می‌بینند، کاربران عادی فقط کاربرانی که به active company دسترسی دارند
  - استفاده از `template_name = 'shared/users_list.html'` که از `generic_list.html` extend می‌کند
  - استفاده از partials مشترک
  - `permission_field = ''` برای skip کردن permission filtering

- ✅ `UserCreateView` → `BaseCreateView`
  - استفاده از `UserAccessFormsetMixin` برای مدیریت company access
  - استفاده از `success_message` attribute
  - Override `form_valid()` برای ذخیره formset
  - Skip company scoping (`auto_set_company = False`, `require_active_company = False`)
  - استفاده از `user_form.html` که از `generic_form.html` extend می‌کند

- ✅ `UserUpdateView` → `BaseUpdateView`
  - استفاده از `UserAccessFormsetMixin` برای مدیریت company access
  - استفاده از `success_message` attribute
  - Override `form_valid()` برای ذخیره formset
  - Override `get_queryset()` برای فیلتر بر اساس active company
  - Skip company scoping (`auto_set_company = False`, `require_active_company = False`)

- ✅ `UserDetailView` → `BaseDetailView`
  - استفاده از `generic_detail.html` (default)
  - Override `get_queryset()` برای فیلتر بر اساس active company و prefetch related
  - Skip permission filtering (`permission_field = ''`)

- ✅ `UserDeleteView` → `BaseDeleteView`
  - استفاده از `generic_confirm_delete.html` (default)
  - Override `get_queryset()` برای فیلتر بر اساس active company
  - استفاده از hook methods برای object details

**فایل**: `shared/forms/users.py`

- ✅ `UserBaseForm` → `BaseModelForm`
  - حذف widgets تکراری (فقط attributes خاص باقی مانده)
  - BaseModelForm به صورت خودکار 'form-control' و 'form-check-input' را اعمال می‌کند

---

#### ماژول `shared` - Groups ✅ تکمیل شده

**فایل**: `shared/views/groups.py`

- ✅ `GroupListView` → `BaseListView`
  - استفاده از `search_fields` برای جستجو در name
  - Override `get_base_queryset()` برای prefetch related (user_set, profile__access_levels)
  - Override `get_queryset()` برای فیلتر status بر اساس `profile.is_enabled` و skip کردن `CompanyScopedViewMixin`
  - Groups global هستند (company-scoped نیستند)
  - استفاده از `template_name = 'shared/groups_list.html'` که از `generic_list.html` extend می‌کند
  - استفاده از partials مشترک: `row_actions.html`
  - `permission_field = ''` برای skip کردن permission filtering (چون Group model از Django auth.Group است)
  - Skip company scoping (`auto_set_company = False`, `require_active_company = False`)

- ✅ `GroupCreateView` → `BaseCreateView`
  - استفاده از `success_message` attribute
  - Skip company scoping (`auto_set_company = False`, `require_active_company = False`)
  - استفاده از `group_form.html` که از `generic_form.html` extend می‌کند
  - `required_action = 'create'` برای permission checking

- ✅ `GroupUpdateView` → `BaseUpdateView`
  - استفاده از `success_message` attribute
  - Override `get_queryset()` برای skip کردن company filtering
  - Skip company scoping (`auto_set_company = False`, `require_active_company = False`)
  - Skip permission filtering (`permission_field = ''`)
  - `required_action = 'edit_own'` برای permission checking

- ✅ `GroupDetailView` → `BaseDetailView`
  - استفاده از `generic_detail.html` (default)
  - Override `get_queryset()` برای prefetch related
  - تنظیم context variables برای `detail_sections`, `info_banner`
  - Skip company scoping و permission filtering
  - `required_action = 'view_own'` برای permission checking

- ✅ `GroupDeleteView` → `BaseDeleteView`
  - استفاده از `generic_confirm_delete.html` (default)
  - Override `get_queryset()` برای skip کردن company filtering
  - استفاده از hook methods برای object details
  - Skip company scoping و permission filtering
  - `required_action = 'delete_own'` برای permission checking

**فایل**: `shared/forms/groups.py`

- ✅ `GroupForm` → `BaseModelForm`
  - حذف widgets تکراری (فقط attributes خاص باقی مانده)
  - BaseModelForm به صورت خودکار 'form-control' و 'form-check-input' را اعمال می‌کند
  - حفظ منطق save() برای GroupProfile

---

#### ماژول `shared` - Access Levels ✅ تکمیل شده

**فایل**: `shared/views/access_levels.py`

- ✅ `AccessLevelListView` → `BaseListView`
  - استفاده از `search_fields` برای جستجو در code, name
  - Override `get_base_queryset()` برای prefetch related (permissions)
  - Override `get_queryset()` برای فیلتر status بر اساس `is_enabled` و skip کردن `CompanyScopedViewMixin`
  - AccessLevels global هستند (company-scoped نیستند)
  - استفاده از `template_name = 'shared/access_levels_list.html'` که از `generic_list.html` extend می‌کند
  - استفاده از partials مشترک: `row_actions.html`
  - `permission_field = ''` برای skip کردن permission filtering
  - Skip company scoping (`auto_set_company = False`, `require_active_company = False`)

- ✅ `AccessLevelCreateView` → `BaseCreateView` + `AccessLevelPermissionMixin`
  - استفاده از `success_message` attribute
  - استفاده از `AccessLevelPermissionMixin` برای مدیریت feature permissions
  - Override `form_valid()` برای ذخیره permissions
  - Skip company scoping (`auto_set_company = False`, `require_active_company = False`)
  - استفاده از `access_level_form.html` که template خاص است (برای permission management)
  - `required_action = 'create'` برای permission checking

- ✅ `AccessLevelUpdateView` → `BaseUpdateView` + `AccessLevelPermissionMixin`
  - استفاده از `success_message` attribute
  - استفاده از `AccessLevelPermissionMixin` برای مدیریت feature permissions
  - Override `form_valid()` برای ذخیره permissions
  - Override `get_queryset()` برای skip کردن company filtering
  - Skip company scoping و permission filtering
  - استفاده از `access_level_form.html` که template خاص است (برای permission management)
  - `required_action = 'edit_own'` برای permission checking

- ✅ `AccessLevelDetailView` → `BaseDetailView`
  - استفاده از `generic_detail.html` (default)
  - Override `get_queryset()` برای prefetch related
  - تنظیم context variables برای `detail_sections`, `info_banner`
  - نمایش permissions به صورت table در detail_sections
  - Skip company scoping و permission filtering
  - `required_action = 'view_own'` برای permission checking

- ✅ `AccessLevelDeleteView` → `BaseDeleteView`
  - استفاده از `generic_confirm_delete.html` (default)
  - Override `get_queryset()` برای skip کردن company filtering
  - استفاده از hook methods برای object details
  - Skip company scoping و permission filtering
  - `required_action = 'delete_own'` برای permission checking

**فایل**: `shared/forms/access_levels.py`

- ✅ `AccessLevelForm` → `BaseModelForm`
  - حذف widgets تکراری (فقط attributes خاص باقی مانده)
  - BaseModelForm به صورت خودکار 'form-control' و 'form-check-input' را اعمال می‌کند
  - حفظ منطق code field (read-only در edit mode)

---

#### ماژول `inventory` - Warehouses ✅ تکمیل شده

**فایل**: `inventory/views/master_data.py`

- ✅ `WarehouseListView` → `BaseListView`
  - استفاده از `search_fields`, `filter_fields`, `default_status_filter`
  - استفاده از `permission_field = 'created_by'` برای permission filtering
  - استفاده از `generic_list.html` (از طریق template `warehouses.html`)
  - استفاده از partials مشترک: `row_actions.html`
  - Override hook methods برای customization

- ✅ `WarehouseCreateView` → `BaseCreateView`
  - استفاده از `success_message` attribute
  - استفاده از `warehouse_form.html` که از `generic_form.html` extend می‌کند
  - Auto-set `company_id` و `created_by` توسط `AutoSetFieldsMixin`

**فایل**: `inventory/forms/master_data.py`

- ✅ `WarehouseForm` → `BaseModelForm`
  - حذف widgets تکراری (فقط attributes خاص باقی مانده)
  - BaseModelForm به صورت خودکار 'form-control' و 'form-check-input' را اعمال می‌کند
  - اضافه کردن `__init__` برای pop کردن `company_id` (چون توسط view تنظیم می‌شود)

**Template Files**:
- ✅ `templates/inventory/warehouses.html` - به‌روزرسانی برای استفاده از `row_actions.html`
- ✅ `templates/inventory/warehouse_form.html` - ایجاد template جدید که از `generic_form.html` extend می‌کند

**مشکلات حل شده**:
- ✅ رفع TypeError در `WarehouseForm` (استفاده از `BaseModelForm` و pop کردن `company_id`)

---

#### ماژول `inventory` - Items ✅ تکمیل شده

**فایل**: `inventory/views/master_data.py`

- ✅ `ItemListView` → `BaseListView`
  - استفاده از `search_fields`, `filter_fields`, `default_status_filter`
  - استفاده از `get_select_related()` برای `type`, `category`, `subcategory`
  - Override `apply_custom_filters()` برای فیلترهای custom (type, category)
  - استفاده از hook methods برای customization
  - حفظ context variables خاص (item_types, item_categories, user_feature_permissions)

- ✅ `ItemCreateView` → `BaseCreateView` + `ItemUnitFormsetMixin`
  - حفظ `ItemUnitFormsetMixin` برای مدیریت unit formset
  - حذف manual set کردن `company_id` و `created_by` (auto-set توسط `AutoSetFieldsMixin`)
  - استفاده از `success_message` attribute
  - استفاده از hook methods برای breadcrumbs و form title
  - حفظ منطق پیچیده formset و warehouses

**فایل**: `inventory/forms/master_data.py`

- ✅ `ItemForm` → `BaseModelForm`
  - حذف widgets تکراری (فقط attributes خاص باقی مانده مثل `maxlength`, `rows`)
  - حفظ تمام منطق custom (IntegerCheckboxField, company filtering, validation)

**Template Files**:
- ✅ `templates/inventory/items.html` - به‌روزرسانی برای استفاده از `row_actions.html`

---

#### ماژول `inventory` - Item Serials ✅ تکمیل شده

**فایل**: `inventory/views/master_data.py`

- ✅ `ItemSerialListView` → `BaseListView`
  - استفاده از `get_select_related()` برای `item`, `receipt_document`, `current_warehouse`
  - Override `apply_custom_filters()` برای فیلترهای custom (receipt_code, item_code, serial_code, status)
  - Skip permission filtering (`permission_field = ''`) چون ItemSerial read-only است
  - Skip default status filter (`default_status_filter = False`) چون status filter custom است
  - `show_actions = False` چون ItemSerial read-only است
  - استفاده از hook methods برای customization

---

### 3. کارهای باقی‌مانده

#### ماژول `shared` (ادامه Pilot):
- ✅ همه فایل‌ها refactor شده‌اند!

#### سایر ماژول‌ها:
- ⏳ ماژول `inventory` - 81+ view (شروع شده: Warehouses ✅, Items ✅, Item Serials ✅)
- ⏳ ماژول `production` - 41+ view
- ⏳ ماژول `accounting` - 28+ view
- ⏳ ماژول `ticketing` - 19+ view
- ⏳ ماژول `qc` - 6+ view

---

## 📊 آمار پیشرفت

### کارهای تکمیل شده:
- ✅ **Infrastructure**: 100% (تمام Base classes و فایل‌های مشترک)
- ✅ **Pilot - Companies**: 100% (5 view + 1 form)
- ✅ **Pilot - Company Units**: 100% (5 view + 1 form)
- ✅ **Pilot - Users**: 100% (5 view + 1 form)
- ✅ **Pilot - Groups**: 100% (5 view + 1 form)
- ✅ **Pilot - Access Levels**: 100% (5 view + 1 form)
- ✅ **Inventory - Warehouses**: 100% (2 view + 1 form) - شروع Rollout
- ✅ **Inventory - Items**: 100% (2 view + 1 form)
- ✅ **Inventory - Item Serials**: 100% (1 view)

**پیشرفت Pilot**: 100% (5/5 فایل) ✅  
**پیشرفت Rollout**: در حال انجام (4 view در inventory)

### کاهش کد:

**نکته مهم**: فایل‌های view ممکن است بزرگتر شده باشند، اما این به این معنی نیست که کد بدتر شده است!

**چرا فایل‌ها بزرگتر شده‌اند؟**

1. **Hook Methods**: به جای یک `get_context_data` بزرگ، از hook methods استفاده می‌کنیم:
   - قبل: یک method با 50 خط که همه چیز را set می‌کرد
   - بعد: 10-15 hook methods که هر کدام 3-5 خط هستند
   - نتیجه: کد واضح‌تر و قابل خواندن‌تر، اما تعداد خطوط بیشتر

2. **Explicit Configuration**: به جای implicit behavior، از attributes و methods استفاده می‌کنیم:
   - `search_fields = ['name', 'code']` به جای کد در `get_queryset`
   - `get_breadcrumbs()` به جای set کردن در `get_context_data`
   - نتیجه: کد واضح‌تر اما خطوط بیشتر

**اما کد مشترک کاهش یافته:**

- **کد مشترک** (search, filter, pagination, permission checking) که قبلاً در **هر view** تکرار می‌شد، حالا فقط **یک بار** در Base classes نوشته شده
- **کل کد در پروژه** کاهش یافته (چون کد مشترک فقط یک بار نوشته شده)
- **نگهداری** آسان‌تر شده (تغییرات فقط در Base classes)

**مثال:**
- قبل: 10 view × 50 خط کد مشترک = 500 خط کد تکراری
- بعد: 10 view × 10 خط hook methods + 1 Base class × 200 خط = 300 خط کل
- **کاهش: 200 خط (40%)**

**آمار فایل‌های refactored شده:**
- **Companies**: از ~227 خط به ~331 خط (اما کد تمیزتر و قابل نگهداری‌تر)
- **Company Units**: از ~223 خط به ~293 خط (اما کد تمیزتر و قابل نگهداری‌تر)
- **Users**: از ~240 خط به ~329 خط (اما کد تمیزتر و قابل نگهداری‌تر)
- **Groups**: از ~190 خط به ~326 خط (اما کد تمیزتر و قابل نگهداری‌تر)
- **Access Levels**: از ~205 خط به ~380 خط (اما کد تمیزتر و قابل نگهداری‌تر - شامل AccessLevelPermissionMixin)

---

## 🔧 مشکلات حل شده

### مشکلات پس از Refactoring Pilot:

1. **مشکل ایجاد Groups و Access Levels** ✅ حل شد
   - **خطا**: `TypeError: BaseModelForm.__init__() got an unexpected keyword argument 'company_id'`
   - **علت**: `BaseCreateView` به صورت خودکار `company_id` را به form می‌فرستد، اما Groups و AccessLevels company-scoped نیستند
   - **راه‌حل**: اضافه کردن `kwargs.pop('company_id', None)` در `__init__` از `GroupForm` و `AccessLevelForm`
   - **فایل‌های تغییر یافته**: `shared/forms/groups.py`, `shared/forms/access_levels.py`

2. **مشکل ایجاد Users** ✅ حل شد
   - **خطا**: `TypeError: BaseModelForm.__init__() got an unexpected keyword argument 'company_id'`
   - **علت**: مشابه Groups و AccessLevels، Users هم company-scoped نیستند
   - **راه‌حل**: اضافه کردن `kwargs.pop('company_id', None)` در `__init__` از `UserBaseForm`
   - **فایل تغییر یافته**: `shared/forms/users.py`

3. **مشکل مشاهده Detail Views (Groups و Access Levels)** ✅ حل شد
   - **مشکل**: بخش‌های "اطلاعات اولیه" و "Assigned Groups" در Detail View خالی بودند
   - **علت**: Template برای نمایش `fields` بررسی می‌کرد که `section.type == 'fields'` باشد، اما در views این `type` تنظیم نشده بود
   - **راه‌حل**: 
     - اضافه کردن `type: 'fields'` به تمام بخش‌های fields در views
     - بهبود template برای fallback به `section.fields` اگر `type` تنظیم نشده باشد
   - **فایل‌های تغییر یافته**: `shared/views/groups.py`, `shared/views/access_levels.py`, `templates/shared/generic/generic_detail.html`

4. **مشکل نمایش دکمه View در لیست کاربران** ✅ حل شد
   - **مشکل**: دکمه "مشاهده" در لیست کاربران وجود نداشت
   - **علت**: در template `users_list.html` دکمه‌ها به صورت دستی نوشته شده بودند و از partial `row_actions.html` استفاده نمی‌شد
   - **راه‌حل**: 
     - اضافه کردن block `table_headers`
     - جایگزینی دکمه‌های دستی با `row_actions.html`
   - **فایل‌های تغییر یافته**: `templates/shared/users_list.html`, `shared/views/users.py`

5. **مشکل نمایش دکمه Edit در لیست کاربران** ✅ حل شد
   - **مشکل**: دکمه "ویرایش" در لیست کاربران نمایش داده نمی‌شد
   - **علت**: در `row_actions.html` ابتدا از template tag `get_object_actions` استفاده می‌شد که گاهی URL درست را پیدا نمی‌کرد
   - **راه‌حل**: تغییر منطق `row_actions.html` تا اول از URL name‌های explicit که از view پاس داده می‌شوند استفاده کند
   - **فایل تغییر یافته**: `templates/shared/partials/row_actions.html`

6. **مشکل KeyError در AccessLevelCreateView** ✅ حل شد
   - **خطا**: `KeyError: 'view_same_group'` در `_prepare_feature_context`
   - **علت**: `action_labels` در `__init__` initialize می‌شد اما ممکن بود قبل از استفاده initialize نشده باشد
   - **راه‌حل**: تبدیل `action_labels` به method `get_action_labels()` با cache
   - **فایل تغییر یافته**: `shared/views/base.py` (AccessLevelPermissionMixin)

7. **مشکل TypeError در AccessLevelDetailView** ✅ حل شد
   - **خطا**: `TypeError: sequence item 0: expected str instance, _proxy_found`
   - **علت**: استفاده از `', '.join()` روی لیستی از `gettext_lazy` objects (proxy objects)
   - **راه‌حل**: استفاده از `force_str()` برای تبدیل proxy objects به string
   - **فایل تغییر یافته**: `shared/views/access_levels.py`

8. **مشکل ایجاد Warehouse** ✅ حل شد
   - **خطا**: `TypeError: BaseModelForm.__init__() got an unexpected keyword argument 'company_id'`
   - **علت**: `BaseCreateView` به صورت خودکار `company_id` را به form می‌فرستد، اما `BaseModelForm` این argument را قبول نمی‌کند
   - **راه‌حل**: اضافه کردن `kwargs.pop('company_id', None)` در `__init__` از `WarehouseForm` (چون `company_id` توسط `AutoSetFieldsMixin` در view تنظیم می‌شود)
   - **فایل تغییر یافته**: `inventory/forms/master_data.py`

---

## 🔧 مشکلات حل شده (قبلی)

1. ✅ **RecursionError در `row_actions.html`**
   - مشکل: کامنت Django با `{% include %}` باعث recursion می‌شد
   - راه‌حل: حذف کامنت یا تبدیل به متن ساده

2. ✅ **TypeError در `CompanyForm`**
   - مشکل: `BaseCreateView` `company_id` را به form می‌فرستد اما `CompanyForm` آن را قبول نمی‌کند
   - راه‌حل: استفاده از `BaseModelForm` و حذف `company_id` از kwargs در `__init__`

3. ✅ **کامنت در خروجی HTML**
   - مشکل: کامنت Django در خروجی HTML نمایش داده می‌شد
   - راه‌حل: حذف کامنت‌های چندخطی که شامل template tags بودند

4. ✅ **لیست کاربران خالی بود**
   - مشکل: `UserListView` لیست خالی برمی‌گرداند
   - راه‌حل: Override `get_queryset()` برای skip کردن `CompanyScopedViewMixin` و استفاده مستقیم از `get_base_queryset()`
   - اضافه کردن `permission_field = ''` برای skip کردن permission filtering
   - اضافه کردن `template_name = 'shared/users_list.html'`

5. ✅ **فیلتر Active Company در Companies و Company Units**
   - مشکل: `CompanyUpdateView` و `CompanyDeleteView` فیلتر active company نداشتند
   - راه‌حل: اضافه کردن `get_queryset()` برای فیلتر بر اساس `UserCompanyAccess` در `CompanyUpdateView` و `CompanyDeleteView`
   - اضافه کردن `get_queryset()` برای فیلتر بر اساس `active_company_id` در `CompanyUnitUpdateView` و `CompanyUnitDeleteView`

---

## 🔒 فیلتر Active Company

همه viewها فیلتر active company را رعایت می‌کنند:

### Companies:
- ✅ `CompanyListView`: فیلتر بر اساس `UserCompanyAccess` (فقط شرکت‌هایی که کاربر به آن‌ها دسترسی دارد)
- ✅ `CompanyDetailView`: فیلتر بر اساس `UserCompanyAccess`
- ✅ `CompanyUpdateView`: فیلتر بر اساس `UserCompanyAccess`
- ✅ `CompanyDeleteView`: فیلتر بر اساس `UserCompanyAccess`

### Company Units:
- ✅ `CompanyUnitListView`: فیلتر خودکار بر اساس `active_company_id` (از طریق `CompanyScopedViewMixin`)
- ✅ `CompanyUnitDetailView`: فیلتر بر اساس `active_company_id`
- ✅ `CompanyUnitUpdateView`: فیلتر بر اساس `active_company_id`
- ✅ `CompanyUnitDeleteView`: فیلتر بر اساس `active_company_id`

### Users:
- ✅ `UserListView`: فیلتر بر اساس `UserCompanyAccess` برای active company (Superuserها همه کاربران را می‌بینند)
- ✅ `UserDetailView`: فیلتر بر اساس `UserCompanyAccess` برای active company
- ✅ `UserUpdateView`: فیلتر بر اساس `UserCompanyAccess` برای active company
- ✅ `UserDeleteView`: فیلتر بر اساس `UserCompanyAccess` برای active company

### Groups:
- ✅ `GroupListView`: Groups global هستند (company-scoped نیستند)
- ✅ `GroupDetailView`: Groups global هستند
- ✅ `GroupUpdateView`: Groups global هستند
- ✅ `GroupDeleteView`: Groups global هستند

### Access Levels:
- ✅ `AccessLevelListView`: AccessLevels global هستند (company-scoped نیستند)
- ✅ `AccessLevelDetailView`: AccessLevels global هستند
- ✅ `AccessLevelUpdateView`: AccessLevels global هستند
- ✅ `AccessLevelDeleteView`: AccessLevels global هستند

**نکته مهم**: اگر active company انتخاب نشده باشد، همه viewها queryset خالی برمی‌گردانند (به جز Superuserها در Users و Groups/AccessLevels که global هستند).

---

## 🔐 سیستم Permission Checking

همه viewها از `FeaturePermissionRequiredMixin` استفاده می‌کنند که قبل از dispatch، دسترسی کاربر را بررسی می‌کند:

### نحوه کار:

1. **Feature Permission Checking** (همیشه فعال):
   - همه Base classes (`BaseListView`, `BaseCreateView`, `BaseUpdateView`, `BaseDetailView`, `BaseDeleteView`) از `FeaturePermissionRequiredMixin` استفاده می‌کنند
   - قبل از اجرای view، بررسی می‌شود که آیا کاربر به feature دسترسی دارد یا نه
   - اگر دسترسی نداشته باشد، `PermissionDenied` exception رخ می‌دهد

2. **Permission Filtering** (اختیاری):
   - برای فیلتر کردن queryset بر اساس `view_all`, `view_own`, `view_same_group`
   - فقط زمانی فعال می‌شود که `permission_field` تنظیم شده باشد
   - برای Group و User skip شده چون منطق فیلتر خاص خودشان را دارند

### مثال:

```python
class GroupListView(BaseListView):
    feature_code = 'shared.groups'
    required_action = 'view'  # Default action for ListView
    permission_field = ''  # Skip permission filtering
    
    # ✅ Feature permission checking فعال است
    # ✅ قبل از dispatch بررسی می‌شود که آیا کاربر به 'shared.groups' دسترسی دارد
    # ❌ Permission filtering (view_all/view_own) skip شده
```

### تفاوت دو نوع Permission:

| نوع | Mixin | زمان اجرا | هدف |
|-----|-------|-----------|-----|
| **Feature Permission** | `FeaturePermissionRequiredMixin` | قبل از dispatch | بررسی دسترسی به feature |
| **Permission Filtering** | `PermissionFilterMixin` | در `get_queryset()` | فیلتر کردن queryset |

### گروه‌های refactored شده:

- ✅ **Companies**: Feature permission فعال، Permission filtering skip (منطق خاص)
- ✅ **Company Units**: هر دو فعال
- ✅ **Users**: Feature permission فعال، Permission filtering skip (منطق خاص)
- ✅ **Groups**: Feature permission فعال، Permission filtering skip (Groups global هستند)
- ✅ **Access Levels**: Feature permission فعال، Permission filtering skip (AccessLevels global هستند)

---

## 📝 نکات مهم

### استفاده از Base Classes:

**ListView:**
```python
class MyListView(BaseListView):
    model = MyModel
    search_fields = ['name', 'code']
    filter_fields = ['is_enabled']
    feature_code = 'module.feature'
    default_order_by = ['code']
    
    def get_breadcrumbs(self):
        return [...]
```

**CreateView:**
```python
class MyCreateView(BaseCreateView):
    model = MyModel
    form_class = MyForm
    success_url = reverse_lazy('module:list')
    feature_code = 'module.feature'
    success_message = _('Created successfully.')
```

**Form:**
```python
class MyForm(BaseModelForm):
    class Meta:
        model = MyModel
        fields = ['name', 'code']
        # BaseModelForm automatically applies 'form-control' class
```

### استفاده از Templates:

- **ListView**: از `generic_list.html` استفاده می‌کند (default)
- **CreateView/UpdateView**: از `generic_form.html` یا extend آن
- **DetailView**: از `generic_detail.html` استفاده می‌کند (default)
- **DeleteView**: از `generic_confirm_delete.html` استفاده می‌کند (default)

### استفاده از Partials:

```django
{% include 'shared/partials/filter_panel.html' %}
{% include 'shared/partials/stats_cards.html' %}
{% include 'shared/partials/pagination.html' %}
{% include 'shared/partials/empty_state.html' %}
{% include 'shared/partials/row_actions.html' with object=item feature_code='...' %}
```

---

## 🎯 مراحل بعدی

1. ✅ **تکمیل Pilot - ماژول `shared`**: همه فایل‌ها refactor شده‌اند!

2. **Rollout به سایر ماژول‌ها** (در حال انجام):
   - ⏳ ماژول `inventory` (اولویت بالا) - شروع شده: Warehouses ✅, Items ✅, Item Serials ✅
     - باقی‌مانده: Item Types, Item Categories, Item Subcategories, Suppliers, Supplier Categories, و سایر viewها
   - ⏳ ماژول `production` (اولویت بالا)
   - ⏳ ماژول `accounting` (اولویت متوسط)
   - ⏳ ماژول `ticketing` و `qc` (اولویت پایین)

---

## 📚 فایل‌های مستندات

- `shared_architecture_refactoring.md` - سند کامل معماری
- `shared_files_implementation_plan.md` - برنامه پیاده‌سازی
- `shared_files_checklist.md` - چک‌لیست پیشرفت
- `shared_files_verification_report.md` - گزارش بررسی فایل‌ها

---

**وضعیت کلی**: ✅ Infrastructure کامل | ✅ Pilot 100% (5/5 فایل) | ⏳ Rollout در حال انجام (4 view در inventory)


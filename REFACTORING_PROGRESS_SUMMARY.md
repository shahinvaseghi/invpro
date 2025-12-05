# خلاصه پیشرفت Refactoring - معماری مشترک

**تاریخ شروع**: 2024-12-05  
**وضعیت فعلی**: Pilot Implementation (ماژول `shared`) - در حال انجام  
**آخرین به‌روزرسانی**: 2024-12-05 (شامل Groups refactoring)

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

### 3. کارهای باقی‌مانده

#### ماژول `shared` (ادامه Pilot):
- ⏳ `shared/views/access_levels.py` - 5 view

#### سایر ماژول‌ها:
- ⏳ ماژول `inventory` - 81+ view
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
- ⏳ **Pilot - سایر**: 0% (access_levels)

**پیشرفت Pilot**: 80% (4/5 فایل)

### کاهش کد:
- **Companies**: از ~227 خط به ~331 خط (اما کد تمیزتر و قابل نگهداری‌تر)
- **Company Units**: از ~223 خط به ~293 خط (اما کد تمیزتر و قابل نگهداری‌تر)
- **Users**: از ~240 خط به ~329 خط (اما کد تمیزتر و قابل نگهداری‌تر)
- **Groups**: از ~190 خط به ~326 خط (اما کد تمیزتر و قابل نگهداری‌تر)

---

## 🔧 مشکلات حل شده

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

**نکته مهم**: اگر active company انتخاب نشده باشد، همه viewها queryset خالی برمی‌گردانند (به جز Superuserها در Users و Groups که global هستند).

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

1. **تکمیل Pilot - ماژول `shared`**:
   - Refactor `access_levels.py`

2. **Rollout به سایر ماژول‌ها**:
   - ماژول `inventory` (اولویت بالا)
   - ماژول `production` (اولویت بالا)
   - ماژول `accounting` (اولویت متوسط)
   - ماژول `ticketing` و `qc` (اولویت پایین)

---

## 📚 فایل‌های مستندات

- `shared_architecture_refactoring.md` - سند کامل معماری
- `shared_files_implementation_plan.md` - برنامه پیاده‌سازی
- `shared_files_checklist.md` - چک‌لیست پیشرفت
- `shared_files_verification_report.md` - گزارش بررسی فایل‌ها

---

**وضعیت کلی**: ✅ Infrastructure کامل | ✅ Pilot 80% (4/5 فایل) | ⏳ Rollout 0%


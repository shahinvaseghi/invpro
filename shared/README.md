# shared app overview

This app hosts common entities, mixins, and admin registration that every other module depends on. Below is a breakdown of each custom file and the objects it defines.

## models.py

Defines the reusable abstractions and core shared tables.

- **Mixins**
  - `TimeStampedModel`: adds `created_at` / `edited_at` fields.
  - `ActivatableModel`: adds `is_enabled`, `enabled_at`, `enabled_by`, `disabled_at`, `disabled_by`.
  - `MetadataModel`: adds a JSON `metadata` field.
  - `SortableModel`: adds `sort_order`.
  - `CompanyScopedModel`: base for multi-company isolation; stores `company`, `company_code` and auto-populates the cached code on save.
- **Entities**
  - `User`: custom auth user (extends `AbstractUser`) with additional contact fields.
  - `Company`: tenant record with contact details, auditing, metadata, and creator/updater links.
  - `CompanyUnit`: hierarchical business units per company (supports parent/child).
  - `AccessLevel`: named roles, supports activation flags and `is_global`.
  - `AccessLevelPermission`: ties an access level to a module/resource with CRUD/approve flags.
  - `UserCompanyAccess`: maps users to companies with the role they hold; enforces one record per user/company pair.
  - `SectionRegistry`: Central registry for all application sections/features. Each section has a unique 6-digit code (XXYYZZ format) and nickname. Used by the Entity Reference System for cross-module action execution.
  - `ActionRegistry`: Registry of actions available for each section. Actions define what can be done in a section (e.g., show, approve, delete). Used by the Entity Reference System for dynamic action execution.

All models inherit the appropriate mixins to guarantee consistent auditing and isolation.

**Important**: See [Entity Reference System Documentation](../docs/ENTITY_REFERENCE_SYSTEM.md) for details on how to add new sections and actions to the registry.

## admin.py

Registers every model with the Django admin and fine-tunes list displays, filters, and search fields to simplify data management during development.

## forms.py

Defines the ModelForms used across the shared module:

- `CompanyForm`: فرم ایجاد/ویرایش شرکت به همراه فیلدهای تماس و وضعیت.
- `CompanyUnitForm`: فرم جدید برای مدیریت واحدهای سازمانی شرکت (واحد اداری، مالی، تاسیسات و ...). فیلد `parent_unit` صرفاً واحدهای همان شرکت را نمایش می‌دهد و از انتخاب نادرست پیشگیری می‌کند.
- `UserCreateForm` / `UserUpdateForm`: مدیریت کامل کاربران شامل انتخاب گروه‌ها، شرکت پیش‌فرض، تعیین/تغییر رمز عبور و دسترسی شرکت (از طریق فرم‌ست). گروه‌ها و وضعیت superuser به‌درستی ذخیره می‌شوند (مشکل قبلی برطرف شده است).
- `GroupForm`: ساخت و ویرایش گروه‌ها به همراه توضیحات، فعال/غیرفعال بودن، تعیین اعضا و نگاشت به `AccessLevel`.
- `AccessLevelForm`: تنظیم کد، نام، وضعیت و ویژگی سراسری بودن نقش.
- `UserCompanyAccessFormSet`: فرم‌ست برای نگاشت کاربر به شرکت و سطح دسترسی مربوطه (یکی primary).

## views.py

- `CompanyListView`, `CompanyCreateView`, ...: مدیریت شرکت‌ها.
- `CompanyUnitListView`, `CompanyUnitCreateView`, `CompanyUnitUpdateView`, `CompanyUnitDeleteView`: رابط کامل CRUD برای واحدهای شرکتی. لیست براساس شرکت فعال فیلتر می‌شود و امکان جستجو و فیلتر وضعیت را فراهم می‌کند.
- **مدیریت کاربران و گروه‌ها**:
  - `UserListView`, `UserCreateView`, `UserUpdateView`, `UserDeleteView`: فهرست، ایجاد و ویرایش کاربران همراه با فرم‌ست دسترسی شرکت‌ها و پیام‌های موفقیت.
  - `GroupListView`, `GroupCreateView`, `GroupUpdateView`, `GroupDeleteView`: مدیریت گروه‌ها، اختصاص کاربران و نگاشت به سطح دسترسی از طریق `GroupProfile`.
- **مدیریت سطوح دسترسی**:
  - `AccessLevelListView`, `AccessLevelCreateView`, `AccessLevelUpdateView`, `AccessLevelDeleteView`: CRUD کامل روی `AccessLevel` به همراه رندر ماتریس اکشن‌ها بر اساس `FEATURE_PERMISSION_MAP` و ذخیره در `AccessLevelPermission`.
  - صفحه ایجاد/ویرایش (`access_level_form.html`) شامل **دکمه‌های Quick Action** برای انتخاب/لغو انتخاب گروهی permissions:
    - برای هر Feature (ردیف): دکمه‌های "همه" و "هیچکدام" برای انتخاب/لغو انتخاب تمام permissions همان Feature
    - برای کل صفحه: دکمه‌های "همه" و "هیچکدام" برای انتخاب/لغو انتخاب تمام permissions تمام Features

## permissions.py

ماژول جدید `shared/permissions.py` کاتالوگ متمرکز مجوزها را نگه می‌دارد:

- `PermissionAction` (Enum): مجموعه اکشن‌های پایه مثل `VIEW_OWN`, `VIEW_ALL`, `CREATE`, `EDIT_OWN`, `EDIT_OTHER`, `DELETE_OWN`, `DELETE_OTHER`, `LOCK_OWN`, `LOCK_OTHER`, `UNLOCK_OWN`, `UNLOCK_OTHER`, `APPROVE`, `REJECT`, `CANCEL`.
- `FeaturePermission`: دیتاکلاس توصیف‌کننده‌ی هر منو / قابلیت و اکشن‌های مجاز آن.
- `FEATURE_PERMISSION_MAP`: نگاشت ماژول‌ها و زیرمنوهای فعلی (رسیدها، حواله‌ها، درخواست‌ها) به لیست اکشن‌های پشتیبانی‌شده. این ساختار بعداً برای ایجاد `AccessLevelPermission` ها، فرم‌های مدیریت دسترسی و کنترل نمایش منوها استفاده خواهد شد.
- `list_feature_permissions()`: هلسپر برای بازگرداندن همه‌ی موارد جهت استفاده در فرم‌ها/فیکسچرها.

## templates/

- `shared/company_units.html`: صفحه فهرست واحدها به همراه فرم جستجو و دکمه ایجاد.
- `shared/company_unit_form.html`: فرم ایجاد/ویرایش واحد با فیلدهای کد، نام، واحد بالادست و توضیحات.
- `shared/company_unit_confirm_delete.html`: صفحه تأیید حذف واحد.
- **صفحات جدید مدیریت کاربران**: `shared/users_list.html`, `shared/user_form.html`, `shared/user_confirm_delete.html`
- **صفحات جدید مدیریت گروه‌ها**: `shared/groups_list.html`, `shared/group_form.html`, `shared/group_confirm_delete.html`
- **صفحات جدید مدیریت سطوح دسترسی**: 
  - `shared/access_levels_list.html`: فهرست سطوح دسترسی
  - `shared/access_level_form.html`: فرم ایجاد/ویرایش سطح دسترسی با **ماتریس permission** و دکمه‌های "همه" و "هیچکدام" برای هر ردیف (Feature) و کل صفحه برای انتخاب/لغو انتخاب گروهی permissions
  - `shared/access_level_confirm_delete.html`: تأیید حذف سطح دسترسی

## migrations/
- `0001_initial.py`: auto-generated from the models and mirrors the database design document (`shared_module_db_design_plan.md`). When models change, run `python manage.py makemigrations shared` to create additional migrations.
- **جدید** `0007_groupprofile.py`: ایجاد مدل `GroupProfile` و نگاشت چند-به-چند به `AccessLevel`.
- **تغییر**: مدل‌های `Person` و `PersonAssignment` از ماژول `shared` به ماژول `production` منتقل شدند (بهتر با جریان کاری تولید همسو هستند).

## apps.py
- `UiConfig`: standard Django app configuration; no custom logic today but serves as the hook for startup code if needed later.

## tests.py

Provides sanity tests for the shared module. Highlights:
- Ensures `__str__` methods return expected values.
- Verifies `UserCompanyAccess` string representation includes company context.
- Tests for `Person` model moved to `production` module tests.

These tests run as part of `python manage.py test shared`.

## context_processors.py

**Purpose**: Provides template context variables available to all templates globally.

### `active_company(request)`

**Location**: `shared/context_processors.py`

**Registered in**: `config/settings.py` → `TEMPLATES['OPTIONS']['context_processors']`

**Context Variables Added**:

1. **`active_company`**: Currently selected company object (or `None`)
   - Retrieved from `request.session['active_company_id']`
   - Falls back to user's default company if no session value
   - Falls back to first accessible company if no default

2. **`user_companies`**: List of all companies user has access to
   - Filtered from `UserCompanyAccess` where `is_enabled=1`
   - Used in company selector dropdown

3. **`user_feature_permissions`**: Dictionary of resolved feature permissions
   - Key: Feature code (e.g., `"inventory__receipts__permanent"`)
   - Value: `FeaturePermissionState` object with `view_scope`, `can_view`, and `actions`
   - Used by `feature_allowed` template filter for permission checks

4. **`notifications`**: List of notification objects for the current user
   - Each notification has: `type`, `key`, `message`, `url`, `count`
   - Types: `approval_pending`, `approved`
   - Automatically marks notifications as read when displayed

5. **`notification_count`**: Total count of unread notifications

**Notification Types**:

1. **Approval Pending**:
   - Purchase requests awaiting user's approval
   - Warehouse requests awaiting user's approval
   - Stocktaking records awaiting user's approval
   - Key format: `approval_pending_{type}_{company_id}`

2. **Approved**:
   - User's purchase requests that were approved (last 7 days)
   - User's warehouse requests that were approved (last 7 days)
   - Key format: `approved_{type}_{company_id}`

**Email Notifications**:

- Automatically sends email notifications for pending approvals
- Uses `shared.utils.email.send_notification_email()`
- Tracks sent emails in session to avoid duplicates
- Only sends once per notification key

**Session Storage**:

- `active_company_id`: Selected company ID
- `read_notifications`: List of notification keys that have been read
- `sent_email_notifications`: Set of notification keys that have triggered emails

**Usage in Templates**:

```django
{# Company selector #}
<select name="company_id">
  {% for company in user_companies %}
    <option value="{{ company.id }}" 
            {% if active_company.id == company.id %}selected{% endif %}>
      {{ company.display_name }}
    </option>
  {% endfor %}
</select>

{# Permission check #}
{% if user_feature_permissions|feature_allowed:"inventory.receipts.permanent:create" %}
  <a href="{% url 'inventory:receipt_permanent_create' %}">Create</a>
{% endif %}

{# Notifications #}
{% if notification_count > 0 %}
  <div class="notifications">
    {% for notification in notifications %}
      <div class="notification">
        <a href="{% url notification.url %}">{{ notification.message }}</a>
      </div>
    {% endfor %}
  </div>
{% endif %}
```

**Related Files**:
- `shared/utils/permissions.py`: Permission resolution logic
- `shared/utils/email.py`: Email notification sending
- `shared/models.py`: `UserCompanyAccess`, `AccessLevel`, `AccessLevelPermission`

---

## templatetags/

### access_tags.py

**Purpose**: Template filters for checking user permissions.

**Filters**:
- `feature_allowed`: Checks if user has permission for a feature/action
  - Usage: `{{ user_feature_permissions|feature_allowed:"feature_code:action" }}`
  - See [Template Tags Documentation](../docs/TEMPLATE_TAGS.md) for details

### json_filters.py

**Purpose**: Template filters for JSON conversion.

**Filters**:
- `to_json`: Converts Python objects to JSON strings
  - Usage: `{{ field_config|to_json }}`
  - See [Template Tags Documentation](../docs/TEMPLATE_TAGS.md) for details

---

## utils/

### modules.py

**Purpose**: Utility functions for checking module availability and optional dependencies.

**Functions**:
- `is_production_installed()`: Returns `True` if production module is installed
- `is_qc_installed()`: Returns `True` if QC module is installed
- `get_work_line_model()`: Returns `WorkLine` model class if production is installed, `None` otherwise
- `get_person_model()`: Returns `Person` model class if production is installed, `None` otherwise

**Usage**:
```python
from shared.utils.modules import is_production_installed, get_work_line_model

if is_production_installed():
    WorkLine = get_work_line_model()
    if WorkLine:
        work_lines = WorkLine.objects.filter(company_id=company_id)
```

### permissions.py

**Purpose**: Utility functions for resolving user feature permissions.

**Functions**:
- `get_user_feature_permissions(user, company_id)`: Returns dictionary of resolved permissions
- `has_feature_permission(permissions, feature_code, action)`: Checks specific permission

**See**: `shared/permissions.py` for permission definitions and `FEATURE_PERMISSION_MAP`

### email.py

**Purpose**: Email utility functions for sending notifications via SMTP.

**Functions**:
- `get_active_smtp_server()`: Returns first enabled SMTP server configuration
- `send_email_notification(subject, message, recipient_email, ...)`: Sends email using active SMTP server
- `send_notification_email(notification_type, notification_message, recipient_user, ...)`: Sends formatted notification email

**SMTP Configuration**:
- Uses `SMTPServer` model from `shared.models`
- Supports SSL, TLS, and authentication
- HTML and plain text email support

**Usage**:
```python
from shared.utils.email import send_notification_email

send_notification_email(
    notification_type='approval_pending',
    notification_message='3 درخواست خرید در انتظار تایید',
    recipient_user=user,
    notification_url='https://example.com/requests/',
    company_name='Company Name'
)
```

---

## Future Work / Notes
- Any new shared entities (e.g., audit logs, global configuration) should extend the existing mixins to preserve consistency.
- Update the design document and regenerate migrations whenever the schema evolves.
- If role-based permission logic moves beyond the current models, document behaviour in this README.
- در صورت گسترش قابلیت‌های CompanyUnit (مانند درخت واحدها، تخصیص کاربران به واحد)، مستندات این فایل و `shared_module_db_design_plan.md` را به‌روزرسانی کنید.
- جریان کاری صدور دسترسی و نگاشت گروه/سطح دسترسی در همین فایل و `shared_module_db_design_plan.md` مستند شده است؛ در صورت افزودن اکشن‌های جدید به `FEATURE_PERMISSION_MAP` یا تغییر رفتار قفل/بازقفل، این مستند را نیز بروزرسانی کنید.


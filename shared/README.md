# shared app overview

This app hosts common entities, mixins, and admin registration that every other module depends on. Below is a breakdown of each custom file and the objects it defines.

## models.py

Defines the reusable abstractions and core shared tables.

- **Mixins**
  - `TimeStampedModel`: adds `created_at` / `edited_at` fields.
  - `ActivatableModel`: adds `is_enabled`, `activated_at`, `deactivated_at`.
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
  - `Person`: personnel directory entry with optional linkage to `User`. هر شخص می‌تواند عضو چند واحد سازمانی از همان شرکت باشد (`ManyToMany` با `CompanyUnit`).
  - `PersonAssignment`: assigns a person to a work center (inventory/production/etc.) with optional primary flag and date range.

All models inherit the appropriate mixins to guarantee consistent auditing and isolation.

## admin.py

Registers every model with the Django admin and fine-tunes list displays, filters, and search fields to simplify data management during development.

## forms.py

Defines the ModelForms used across the shared module:

- `CompanyForm`: فرم ایجاد/ویرایش شرکت به همراه فیلدهای تماس و وضعیت.
- `PersonForm`: فرم مدیریت پرسنل با قابلیت استفاده از کد پرسنلی به عنوان نام کاربری و انتخاب چند واحد سازمانی از شرکت فعال.
- `CompanyUnitForm`: فرم جدید برای مدیریت واحدهای سازمانی شرکت (واحد اداری، مالی، تاسیسات و ...). فیلد `parent_unit` صرفاً واحدهای همان شرکت را نمایش می‌دهد و از انتخاب نادرست پیشگیری می‌کند.
- `UserCreateForm` / `UserUpdateForm`: مدیریت کامل کاربران شامل انتخاب گروه‌ها، شرکت پیش‌فرض، تعیین/تغییر رمز عبور و دسترسی شرکت (از طریق فرم‌ست).
- `GroupForm`: ساخت و ویرایش گروه‌ها به همراه توضیحات، فعال/غیرفعال بودن، تعیین اعضا و نگاشت به `AccessLevel`.
- `AccessLevelForm`: تنظیم کد، نام، وضعیت و ویژگی سراسری بودن نقش.
- `UserCompanyAccessFormSet`: فرم‌ست برای نگاشت کاربر به شرکت و سطح دسترسی مربوطه (یکی primary).

## views.py

- `CompanyListView`, `CompanyCreateView`, ...: مدیریت شرکت‌ها.
- `PersonnelListView`, `PersonCreateView`, ...: فهرست و فرم‌های اختصاصی پرسنل بر اساس شرکت فعال، شامل بارگذاری لیست واحدهای سازمانی مرتبط برای هر شخص.
- `CompanyUnitListView`, `CompanyUnitCreateView`, `CompanyUnitUpdateView`, `CompanyUnitDeleteView`: رابط کامل CRUD برای واحدهای شرکتی. لیست براساس شرکت فعال فیلتر می‌شود و امکان جستجو و فیلتر وضعیت را فراهم می‌کند.
- **مدیریت کاربران و گروه‌ها**:
  - `UserListView`, `UserCreateView`, `UserUpdateView`, `UserDeleteView`: فهرست، ایجاد و ویرایش کاربران همراه با فرم‌ست دسترسی شرکت‌ها و پیام‌های موفقیت.
  - `GroupListView`, `GroupCreateView`, `GroupUpdateView`, `GroupDeleteView`: مدیریت گروه‌ها، اختصاص کاربران و نگاشت به سطح دسترسی از طریق `GroupProfile`.
- **مدیریت سطوح دسترسی**:
  - `AccessLevelListView`, `AccessLevelCreateView`, `AccessLevelUpdateView`, `AccessLevelDeleteView`: CRUD کامل روی `AccessLevel` به همراه رندر ماتریس اکشن‌ها بر اساس `FEATURE_PERMISSION_MAP` و ذخیره در `AccessLevelPermission`.

## permissions.py

ماژول جدید `shared/permissions.py` کاتالوگ متمرکز مجوزها را نگه می‌دارد:

- `PermissionAction` (Enum): مجموعه اکشن‌های پایه مثل `VIEW_OWN`, `VIEW_ALL`, `CREATE`, `EDIT_OWN`, `DELETE_OWN`, `LOCK_OWN`, `LOCK_OTHER`, `UNLOCK_OWN`, `UNLOCK_OTHER`, `APPROVE`, `REJECT`, `CANCEL`.
- `FeaturePermission`: دیتاکلاس توصیف‌کننده‌ی هر منو / قابلیت و اکشن‌های مجاز آن.
- `FEATURE_PERMISSION_MAP`: نگاشت ماژول‌ها و زیرمنوهای فعلی (رسیدها، حواله‌ها، درخواست‌ها) به لیست اکشن‌های پشتیبانی‌شده. این ساختار بعداً برای ایجاد `AccessLevelPermission` ها، فرم‌های مدیریت دسترسی و کنترل نمایش منوها استفاده خواهد شد.
- `list_feature_permissions()`: هلسپر برای بازگرداندن همه‌ی موارد جهت استفاده در فرم‌ها/فیکسچرها.

## templates/

- `shared/company_units.html`: صفحه فهرست واحدها به همراه فرم جستجو و دکمه ایجاد.
- `shared/company_unit_form.html`: فرم ایجاد/ویرایش واحد با فیلدهای کد، نام، واحد بالادست و توضیحات.
- `shared/company_unit_confirm_delete.html`: صفحه تأیید حذف واحد.
- `shared/personnel.html`: جدول پرسنل شامل ستون واحدهای سازمانی هر نفر.
- `shared/person_form.html`: فرم پرسنل با بخش انتخاب واحدهای سازمانی (چند انتخابی).
- **صفحات جدید مدیریت کاربران**: `shared/users_list.html`, `shared/user_form.html`, `shared/user_confirm_delete.html`
- **صفحات جدید مدیریت گروه‌ها**: `shared/groups_list.html`, `shared/group_form.html`, `shared/group_confirm_delete.html`
- **صفحات جدید مدیریت سطوح دسترسی**: `shared/access_levels_list.html`, `shared/access_level_form.html`, `shared/access_level_confirm_delete.html`

## migrations/
- `0001_initial.py`: auto-generated from the models and mirrors the database design document (`shared_module_db_design_plan.md`). When models change, run `python manage.py makemigrations shared` to create additional migrations.
- **جدید** `0006_person_company_units.py`: افزودن فیلد چند-به-چند `company_units` به مدل `Person`.
- **جدید** `0007_groupprofile.py`: ایجاد مدل `GroupProfile` و نگاشت چند-به-چند به `AccessLevel`.

## apps.py
- `UiConfig`: standard Django app configuration; no custom logic today but serves as the hook for startup code if needed later.

## tests.py

Provides sanity tests for the shared module. Highlights:
- Ensures `__str__` methods return expected values.
- Confirms `company_code` caching for `Person`.
- Verifies `UserCompanyAccess` string representation includes company context.

These tests run as part of `python manage.py test shared`.

## Future Work / Notes
- Any new shared entities (e.g., audit logs, global configuration) should extend the existing mixins to preserve consistency.
- Update the design document and regenerate migrations whenever the schema evolves.
- If role-based permission logic moves beyond the current models, document behaviour in this README.
- در صورت گسترش قابلیت‌های CompanyUnit (مانند درخت واحدها، تخصیص کاربران به واحد)، مستندات این فایل و `shared_module_db_design_plan.md` را به‌روزرسانی کنید.
- جریان کاری صدور دسترسی و نگاشت گروه/سطح دسترسی در همین فایل و `shared_module_db_design_plan.md` مستند شده است؛ در صورت افزودن اکشن‌های جدید به `FEATURE_PERMISSION_MAP` یا تغییر رفتار قفل/بازقفل، این مستند را نیز بروزرسانی کنید.


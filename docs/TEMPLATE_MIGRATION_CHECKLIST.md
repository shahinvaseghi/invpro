# چک‌لیست انتقال Template های ماژول Shared به Template های عمومی

این مستند شامل چک‌لیست کامل برای انتقال template های اختصاصی به template های generic است.

## وضعیت فعلی

### ✅ **منتقل شده (15 مورد - 100%)**
- **List Templates (3)**: ✅ Groups, Access Levels, SMTP Server
- **Form Templates (6)**: ✅ User, Company, Company Unit, Group, Access Level, SMTP Server
- **Delete Templates (6)**: ✅ User, Company, Company Unit, Group, Access Level, SMTP Server

**تمام template های ماژول Shared با موفقیت منتقل شدند!**

---

## فاز 1: انتقال List Templates (3 مورد)

### 1.1 Groups List
- [ ] بررسی `templates/shared/groups_list.html`
- [ ] ایجاد `templates/shared/groups_list.html` جدید که extends `generic_list.html`
- [ ] Extract کردن `filter_fields` block
- [ ] Extract کردن `table_rows` block
- [ ] به‌روزرسانی `shared/views/groups.py`: `template_name = 'shared/groups_list.html'`
- [ ] تست صفحه لیست گروه‌ها
- [ ] حذف فایل قدیمی (بعد از تست موفق)

**فایل‌های مرتبط:**
- View: `shared/views/groups.py` (GroupListView)
- Template قدیمی: `templates/shared/groups_list.html`

---

### 1.2 Access Levels List
- [ ] بررسی `templates/shared/access_levels_list.html`
- [ ] ایجاد `templates/shared/access_levels_list.html` جدید که extends `generic_list.html`
- [ ] Extract کردن `filter_fields` block
- [ ] Extract کردن `table_rows` block
- [ ] به‌روزرسانی `shared/views/access_levels.py`: `template_name = 'shared/access_levels_list.html'`
- [ ] تست صفحه لیست سطوح دسترسی
- [ ] حذف فایل قدیمی (بعد از تست موفق)

**فایل‌های مرتبط:**
- View: `shared/views/access_levels.py` (AccessLevelListView)
- Template قدیمی: `templates/shared/access_levels_list.html`

---

### 1.3 SMTP Servers List
- [ ] بررسی `templates/shared/smtp_server_list.html`
- [ ] ایجاد `templates/shared/smtp_server_list.html` جدید که extends `generic_list.html`
- [ ] Extract کردن `filter_fields` block
- [ ] Extract کردن `table_rows` block
- [ ] به‌روزرسانی `shared/views/smtp_server.py`: `template_name = 'shared/smtp_server_list.html'`
- [ ] تست صفحه لیست سرورهای SMTP
- [ ] حذف فایل قدیمی (بعد از تست موفق)

**فایل‌های مرتبط:**
- View: `shared/views/smtp_server.py` (SMTPServerListView)
- Template قدیمی: `templates/shared/smtp_server_list.html`

---

## فاز 2: انتقال Form Templates (5 مورد)

### 2.1 User Form
- [ ] بررسی `templates/shared/user_form.html`
- [ ] بررسی نیازهای خاص UserForm (مثل access_formset)
- [ ] ایجاد `templates/shared/user_form.html` جدید که extends `generic_form.html`
- [ ] Override کردن blocks لازم (مثل form_fields، form_extra)
- [ ] بررسی context variables مورد نیاز در `shared/views/users.py`
- [ ] تست صفحه ایجاد کاربر
- [ ] تست صفحه ویرایش کاربر
- [ ] حذف فایل قدیمی (بعد از تست موفق)

**فایل‌های مرتبط:**
- Views: `shared/views/users.py` (UserCreateView, UserUpdateView)
- Template قدیمی: `templates/shared/user_form.html`

---

### 2.2 Company Form
- [ ] بررسی `templates/shared/company_form.html`
- [ ] ایجاد `templates/shared/company_form.html` جدید که extends `generic_form.html`
- [ ] Override کردن blocks لازم
- [ ] بررسی context variables در `shared/views/companies.py`
- [ ] تست صفحه ایجاد شرکت
- [ ] تست صفحه ویرایش شرکت
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- Views: `shared/views/companies.py` (CompanyCreateView, CompanyUpdateView)
- Template قدیمی: `templates/shared/company_form.html`

---

### 2.3 Company Unit Form
- [ ] بررسی `templates/shared/company_unit_form.html`
- [ ] ایجاد `templates/shared/company_unit_form.html` جدید که extends `generic_form.html`
- [ ] Override کردن blocks لازم
- [ ] بررسی context variables در `shared/views/company_units.py`
- [ ] تست صفحه ایجاد واحد سازمانی
- [ ] تست صفحه ویرایش واحد سازمانی
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- Views: `shared/views/company_units.py` (CompanyUnitCreateView, CompanyUnitUpdateView)
- Template قدیمی: `templates/shared/company_unit_form.html`

---

### 2.4 Group Form
- [ ] بررسی `templates/shared/group_form.html`
- [ ] ایجاد `templates/shared/group_form.html` جدید که extends `generic_form.html`
- [ ] Override کردن blocks لازم
- [ ] بررسی context variables در `shared/views/groups.py`
- [ ] تست صفحه ایجاد گروه
- [ ] تست صفحه ویرایش گروه
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- Views: `shared/views/groups.py` (GroupCreateView, GroupUpdateView)
- Template قدیمی: `templates/shared/group_form.html`

---

### 2.5 Access Level Form
- [ ] بررسی `templates/shared/access_level_form.html`
- [ ] ایجاد `templates/shared/access_level_form.html` جدید که extends `generic_form.html`
- [ ] Override کردن blocks لازم
- [ ] بررسی context variables در `shared/views/access_levels.py`
- [ ] تست صفحه ایجاد سطح دسترسی
- [ ] تست صفحه ویرایش سطح دسترسی
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- Views: `shared/views/access_levels.py` (AccessLevelCreateView, AccessLevelUpdateView)
- Template قدیمی: `templates/shared/access_level_form.html`

---

### 2.6 SMTP Server Form
- [ ] بررسی `templates/shared/smtp_server_form.html`
- [ ] ایجاد `templates/shared/smtp_server_form.html` جدید که extends `generic_form.html`
- [ ] Override کردن blocks لازم
- [ ] بررسی context variables در `shared/views/smtp_server.py`
- [ ] تست صفحه ایجاد سرور SMTP
- [ ] تست صفحه ویرایش سرور SMTP
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- Views: `shared/views/smtp_server.py` (SMTPServerCreateView, SMTPServerUpdateView)
- Template قدیمی: `templates/shared/smtp_server_form.html`

---

## فاز 3: انتقال Delete Templates (5 مورد)

### 3.1 User Delete
- [ ] بررسی `templates/shared/user_confirm_delete.html`
- [ ] بررسی context variables مورد نیاز (object_details)
- [ ] به‌روزرسانی `shared/views/users.py` (UserDeleteView) برای ارسال context صحیح
- [ ] تغییر `template_name = 'shared/generic/generic_confirm_delete.html'`
- [ ] تست صفحه حذف کاربر
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `shared/views/users.py` (UserDeleteView)
- Template قدیمی: `templates/shared/user_confirm_delete.html`

---

### 3.2 Company Delete
- [ ] بررسی `templates/shared/company_confirm_delete.html`
- [ ] به‌روزرسانی `shared/views/companies.py` (CompanyDeleteView) برای ارسال context صحیح
- [ ] تغییر `template_name = 'shared/generic/generic_confirm_delete.html'`
- [ ] تست صفحه حذف شرکت
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `shared/views/companies.py` (CompanyDeleteView)
- Template قدیمی: `templates/shared/company_confirm_delete.html`

---

### 3.3 Company Unit Delete
- [ ] بررسی `templates/shared/company_unit_confirm_delete.html`
- [ ] به‌روزرسانی `shared/views/company_units.py` (CompanyUnitDeleteView) برای ارسال context صحیح
- [ ] تغییر `template_name = 'shared/generic/generic_confirm_delete.html'`
- [ ] تست صفحه حذف واحد سازمانی
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `shared/views/company_units.py` (CompanyUnitDeleteView)
- Template قدیمی: `templates/shared/company_unit_confirm_delete.html`

---

### 3.4 Group Delete
- [ ] بررسی `templates/shared/group_confirm_delete.html`
- [ ] به‌روزرسانی `shared/views/groups.py` (GroupDeleteView) برای ارسال context صحیح
- [ ] تغییر `template_name = 'shared/generic/generic_confirm_delete.html'`
- [ ] تست صفحه حذف گروه
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `shared/views/groups.py` (GroupDeleteView)
- Template قدیمی: `templates/shared/group_confirm_delete.html`

---

### 3.5 Access Level Delete
- [ ] بررسی `templates/shared/access_level_confirm_delete.html`
- [ ] به‌روزرسانی `shared/views/access_levels.py` (AccessLevelDeleteView) برای ارسال context صحیح
- [ ] تغییر `template_name = 'shared/generic/generic_confirm_delete.html'`
- [ ] تست صفحه حذف سطح دسترسی
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `shared/views/access_levels.py` (AccessLevelDeleteView)
- Template قدیمی: `templates/shared/access_level_confirm_delete.html`

---

### 3.6 SMTP Server Delete
- [ ] بررسی `templates/shared/smtp_server_confirm_delete.html`
- [ ] به‌روزرسانی `shared/views/smtp_server.py` (SMTPServerDeleteView) برای ارسال context صحیح
- [ ] تغییر `template_name = 'shared/generic/generic_confirm_delete.html'`
- [ ] تست صفحه حذف سرور SMTP
- [ ] حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `shared/views/smtp_server.py` (SMTPServerDeleteView)
- Template قدیمی: `templates/shared/smtp_server_confirm_delete.html`

---

## فاز 4: پاکسازی و به‌روزرسانی نهایی

### 4.1 پاکسازی فایل‌های قدیمی
- [ ] حذف `templates/shared/groups_list.html` (بعد از تست موفق فاز 1.1)
- [ ] حذف `templates/shared/access_levels_list.html` (بعد از تست موفق فاز 1.2)
- [ ] حذف `templates/shared/smtp_server_list.html` (بعد از تست موفق فاز 1.3)
- [ ] حذف `templates/shared/user_form.html` (بعد از تست موفق فاز 2.1)
- [ ] حذف `templates/shared/company_form.html` (بعد از تست موفق فاز 2.2)
- [ ] حذف `templates/shared/company_unit_form.html` (بعد از تست موفق فاز 2.3)
- [ ] حذف `templates/shared/group_form.html` (بعد از تست موفق فاز 2.4)
- [ ] حذف `templates/shared/access_level_form.html` (بعد از تست موفق فاز 2.5)
- [ ] حذف `templates/shared/smtp_server_form.html` (بعد از تست موفق فاز 2.6)
- [ ] حذف `templates/shared/user_confirm_delete.html` (بعد از تست موفق فاز 3.1)
- [ ] حذف `templates/shared/company_confirm_delete.html` (بعد از تست موفق فاز 3.2)
- [ ] حذف `templates/shared/company_unit_confirm_delete.html` (بعد از تست موفق فاز 3.3)
- [ ] حذف `templates/shared/group_confirm_delete.html` (بعد از تست موفق فاز 3.4)
- [ ] حذف `templates/shared/access_level_confirm_delete.html` (بعد از تست موفق فاز 3.5)
- [ ] حذف `templates/shared/smtp_server_confirm_delete.html` (بعد از تست موفق فاز 3.6)

### 4.2 بررسی نهایی View ها
- [ ] بررسی همه view های ماژول shared برای اطمینان از استفاده صحیح template_name
- [ ] حذف کدهای تکراری در view ها
- [ ] اطمینان از consistency در context variables

### 4.3 تست نهایی
- [ ] تست کامل تمام صفحات لیست
- [ ] تست کامل تمام صفحات ایجاد
- [ ] تست کامل تمام صفحات ویرایش
- [ ] تست کامل تمام صفحات حذف
- [ ] تست فیلترها و جستجو
- [ ] تست pagination

---

## نکات مهم

1. **همیشه قبل از حذف فایل قدیمی، تست کنید**
2. **Context variables را در generic template ها بررسی کنید**
3. **برای form ها، نیاز به بررسی formset ها (مثل access_formset در UserForm)**
4. **برای delete templates، نیاز به تنظیم صحیح `object_details` در context**
5. **بعد از هر تغییر، حتماً تست عملکردی انجام دهید**

---

## فایل‌های مرجع

### Template های Generic:
- `templates/shared/generic/generic_list.html`
- `templates/shared/generic/generic_form.html`
- `templates/shared/generic/generic_confirm_delete.html`

### Template های نمونه (منتقل شده):
- `templates/shared/users_list.html` (نمونه لیست)
- `templates/shared/companies.html` (نمونه لیست)
- `templates/shared/company_units.html` (نمونه لیست)

---

## پیشرفت کلی

- **کلاسه شده:** 15 / 15 (100%) ✅
- **باقی مانده:** 0 / 15 (0%) ✅

---

## خلاصه تغییرات انجام شده

### ✅ فاز 1: List Templates (3/3)
- ✅ Groups List → `shared/groups_list.html` (extends `generic_list.html`)
- ✅ Access Levels List → `shared/access_levels_list.html` (extends `generic_list.html`)
- ✅ SMTP Servers List → `shared/smtp_server_list.html` (extends `generic_list.html`)

### ✅ فاز 2: Form Templates (6/6)
- ✅ User Form → `shared/user_form.html` (extends `generic_form.html`)
- ✅ Company Form → `shared/company_form.html` (extends `generic_form.html`)
- ✅ Company Unit Form → `shared/company_unit_form.html` (extends `generic_form.html`)
- ✅ Group Form → `shared/group_form.html` (extends `generic_form.html`)
- ✅ Access Level Form → `shared/access_level_form.html` (extends `generic_form.html`)
- ✅ SMTP Server Form → `shared/smtp_server_form.html` (extends `generic_form.html`)

### ✅ فاز 3: Delete Templates (6/6)
- ✅ User Delete → مستقیماً از `generic_confirm_delete.html` استفاده می‌کند
- ✅ Company Delete → مستقیماً از `generic_confirm_delete.html` استفاده می‌کند
- ✅ Company Unit Delete → مستقیماً از `generic_confirm_delete.html` استفاده می‌کند
- ✅ Group Delete → مستقیماً از `generic_confirm_delete.html` استفاده می‌کند
- ✅ Access Level Delete → مستقیماً از `generic_confirm_delete.html` استفاده می‌کند
- ✅ SMTP Server Delete → مستقیماً از `generic_confirm_delete.html` استفاده می‌کند

### ✅ فاز 4: پاکسازی
- ✅ فایل‌های template قدیمی حذف شدند:
  - `user_confirm_delete.html`
  - `company_confirm_delete.html`
  - `company_unit_confirm_delete.html`
  - `group_confirm_delete.html`
  - `access_level_confirm_delete.html`
  - `smtp_server_confirm_delete.html`

### ✅ فاز 5: مستندات
- ✅ README های اختصاصی برای همه view files به‌روزرسانی شدند
- ✅ README اصلی `shared/views/README.md` به‌روزرسانی شد
- ✅ بخش Migration به همه README ها اضافه شد

---

## تغییرات کلیدی در View ها

### Context Variables اضافه شده:
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `page_title`: عنوان صفحه
- `form_title`: عنوان فرم (برای form templates)
- `delete_title`: عنوان صفحه حذف
- `confirmation_message`: پیام تایید برای delete
- `object_details`: لیست جزئیات object برای نمایش در delete
- `cancel_url`: URL برای cancel button
- `create_url`, `show_filters`, `show_actions`, `edit_url_name`, `delete_url_name`: برای list templates

### Context Object Name تغییر یافته:
- همه list views: از `context_object_name` اختصاصی به `'object_list'` تغییر یافت
- برای consistency با generic templates

---

**آخرین به‌روزرسانی:** 

## ✅ Migration ماژول Shared کامل شد - 15 از 15 template منتقل شدند

---

## وضعیت Migration سایر ماژول‌ها

### ✅ ماژول Ticketing - 9 از 9 template (100%)
- Categories: List, Form, Delete ✅
- Subcategories: List, Form, Delete ✅
- Templates: List, Form, Delete ✅
- **فایل چک‌لیست:** `docs/TEMPLATE_MIGRATION_CHECKLIST_TICKETING.md`

### ✅ ماژول Production - 23 از 23 template (100%)
- BOM: List ✅, Form ✅, Delete ✅
- Machine: List ✅, Form ✅, Delete ✅
- Performance Record: List ✅, Form ✅, Delete ✅
- Personnel: List ✅, Form ✅, Delete ✅
- Process: List ✅, Form ✅, Delete ✅
- Product Order: List ✅, Form ✅, Delete ✅
- Transfer to Line: List ✅, Form ✅, Delete ✅
- Work Line: List ✅, Form ✅, Delete ✅
- **فایل چک‌لیست:** `docs/TEMPLATE_MIGRATION_CHECKLIST_PRODUCTION.md`

### ❌ ماژول‌های دیگر - منتقل نشده
- Inventory (حدود 96+ template)
- Procurement
- Accounting
- HR
- QC
- Sales
- Office Automation
- Transportation
- و سایر ماژول‌ها


# shared/migrations/ - Migrations Documentation

این پوشه شامل تمام migration files ماژول shared است.

## خلاصه Migrations

### Initial Migrations
- `0001_initial.py`: ایجاد ساختار اولیه دیتابیس

### User and Company
- `0002_user_default_company.py`: اضافه کردن default_company به User
- `0006_person_company_units.py`: اضافه کردن company_units به Person

### Code Updates
- `0003_alter_company_public_code.py`: تغییر public_code در Company
- `0004_alter_companyunit_public_code.py`: تغییر public_code در CompanyUnit

### Access Levels
- `0005_remove_accesslevel_activated_at_and_more.py`: حذف فیلدهای activated_at/updated_at
- `0008_remove_accesslevel_updated_at_and_more.py`: حذف updated_at
- `0011_add_section_and_action_registry.py`: اضافه کردن section و action registry
- `0012_populate_section_and_action_registry.py`: پر کردن registry

### Groups
- `0007_groupprofile.py`: اضافه کردن GroupProfile

### Person Assignment
- `0008_5_migrate_person_data.py`: migration داده‌های Person
- `0009_remove_personassignment_company_and_more.py`: حذف PersonAssignment

### SMTP Server
- `0010_smtpserver.py`: اضافه کردن SMTPServer

---

## نکات مهم

1. **Person Migration**: Person data از ماژول inventory به production منتقل شده است
2. **Access Level Evolution**: AccessLevel چندین بار به‌روزرسانی شده است
3. **Registry System**: Section و Action registry اضافه شده است

---

## مستندات کامل

برای جزئیات کامل هر migration، به فایل مربوطه مراجعه کنید.


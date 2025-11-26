# shared/forms/ - Forms Documentation

این پوشه شامل تمام form classes و formsets ماژول shared است.

## فایل‌ها

### companies.py
- **Forms**: CompanyForm
- **توضیح**: Forms برای شرکت‌ها

### company_units.py
- **Forms**: CompanyUnitForm
- **توضیح**: Forms برای واحدهای سازمانی

### users.py
- **Forms**: UserCreateForm, UserUpdateForm
- **Formsets**: UserCompanyAccessFormSet
- **توضیح**: Forms برای کاربران و دسترسی شرکت

### groups.py
- **Forms**: GroupForm
- **توضیح**: Forms برای گروه‌های کاربری

### access_levels.py
- **Forms**: AccessLevelForm
- **توضیح**: Forms برای سطوح دسترسی

### smtp_server.py
- **Forms**: SMTPServerForm
- **توضیح**: Forms برای تنظیمات سرور SMTP

---

## الگوهای مشترک

تمام forms از الگوهای مشترک زیر پیروی می‌کنند:

1. **Company Scoping**: تمام forms به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Validation**: تمام forms validation مناسب دارند
3. **Formset Management**: User forms از `UserCompanyAccessFormSet` برای مدیریت دسترسی شرکت استفاده می‌کنند

---

## مستندات کامل

برای جزئیات کامل هر form، به `shared/README_FORMS.md` مراجعه کنید.


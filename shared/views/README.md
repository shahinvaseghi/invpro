# shared/views/ - Views Documentation

این پوشه شامل تمام views ماژول shared است.

## فایل‌ها

### base.py
- **README**: [README_BASE.md](README_BASE.md)
- **توضیح**: Mixin‌های قابل استفاده مجدد (UserAccessFormsetMixin, AccessLevelPermissionMixin)

### companies.py
- **Views**: CompanyListView, CompanyCreateView, CompanyUpdateView, CompanyDeleteView
- **توضیح**: CRUD views برای شرکت‌ها

### company_units.py
- **Views**: CompanyUnitListView, CompanyUnitCreateView, CompanyUnitUpdateView, CompanyUnitDeleteView
- **توضیح**: CRUD views برای واحدهای سازمانی

### users.py
- **Views**: UserListView, UserCreateView, UserUpdateView, UserDeleteView
- **توضیح**: CRUD views برای کاربران (با UserAccessFormsetMixin برای مدیریت دسترسی شرکت)

### groups.py
- **Views**: GroupListView, GroupCreateView, GroupUpdateView, GroupDeleteView
- **توضیح**: CRUD views برای گروه‌های کاربری

### access_levels.py
- **Views**: AccessLevelListView, AccessLevelCreateView, AccessLevelUpdateView, AccessLevelDeleteView
- **توضیح**: CRUD views برای سطوح دسترسی (با AccessLevelPermissionMixin برای مدیریت permissions)

### smtp_server.py
- **Views**: SMTPServerListView, SMTPServerCreateView, SMTPServerUpdateView, SMTPServerDeleteView
- **توضیح**: CRUD views برای تنظیمات سرور SMTP

### auth.py
- **README**: [README_AUTH.md](README_AUTH.md)
- **توضیح**: Views مربوط به authentication (login, logout, etc.)

### notifications.py
- **توضیح**: Views مربوط به notifications (mark as read/unread)

---

## الگوهای مشترک

تمام views از الگوهای مشترک زیر پیروی می‌کنند:

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کنند
2. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
3. **Formset Management**: User views از `UserAccessFormsetMixin` برای مدیریت دسترسی شرکت استفاده می‌کنند
4. **Permission Matrix**: AccessLevel views از `AccessLevelPermissionMixin` برای مدیریت ماتریس permission استفاده می‌کنند

---

## مستندات کامل

برای جزئیات کامل هر view، به کد منبع مراجعه کنید.


# shared/views/ - Views Documentation

این پوشه شامل تمام views ماژول shared است.

## فایل‌ها

### base.py
- **README**: [README_BASE.md](README_BASE.md)
- **توضیح**: Mixin‌های قابل استفاده مجدد (UserAccessFormsetMixin, AccessLevelPermissionMixin)

### companies.py
- **Views**: CompanyListView, CompanyCreateView, CompanyUpdateView, CompanyDeleteView
- **README**: [README_COMPANIES.md](README_COMPANIES.md)
- **توضیح**: CRUD views برای شرکت‌ها
- **Templates**: از generic templates استفاده می‌کنند (`generic_list.html`, `generic_form.html`, `generic_confirm_delete.html`)

### company_units.py
- **Views**: CompanyUnitListView, CompanyUnitCreateView, CompanyUnitUpdateView, CompanyUnitDeleteView
- **README**: [README_COMPANY_UNITS.md](README_COMPANY_UNITS.md)
- **توضیح**: CRUD views برای واحدهای سازمانی
- **Templates**: از generic templates استفاده می‌کنند (`generic_list.html`, `generic_form.html`, `generic_confirm_delete.html`)

### users.py
- **Views**: UserListView, UserCreateView, UserUpdateView, UserDeleteView
- **README**: [README_USERS.md](README_USERS.md)
- **توضیح**: CRUD views برای کاربران (با UserAccessFormsetMixin برای مدیریت دسترسی شرکت)
- **Templates**: از generic templates استفاده می‌کنند (`generic_list.html`, `generic_form.html`, `generic_confirm_delete.html`)

### groups.py
- **Views**: GroupListView, GroupCreateView, GroupUpdateView, GroupDeleteView
- **README**: [README_GROUPS.md](README_GROUPS.md)
- **توضیح**: CRUD views برای گروه‌های کاربری
- **Templates**: از generic templates استفاده می‌کنند (`generic_list.html`, `generic_form.html`, `generic_confirm_delete.html`)

### access_levels.py
- **Views**: AccessLevelListView, AccessLevelCreateView, AccessLevelUpdateView, AccessLevelDeleteView
- **README**: [README_ACCESS_LEVELS.md](README_ACCESS_LEVELS.md)
- **توضیح**: CRUD views برای سطوح دسترسی (با AccessLevelPermissionMixin برای مدیریت permissions)
- **Templates**: از generic templates استفاده می‌کنند (`generic_list.html`, `generic_form.html`, `generic_confirm_delete.html`)

### smtp_server.py
- **Views**: SMTPServerListView, SMTPServerCreateView, SMTPServerUpdateView, SMTPServerDeleteView
- **README**: [README_SMTP_SERVER.md](README_SMTP_SERVER.md)
- **توضیح**: CRUD views برای تنظیمات سرور SMTP
- **Templates**: از generic templates استفاده می‌کنند (`generic_list.html`, `generic_form.html`, `generic_confirm_delete.html`)

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
5. **Generic Templates**: تمام views از generic templates استفاده می‌کنند:
   - List views: از `generic_list.html` (از طریق template های اختصاصی که extend می‌کنند)
   - Form views: از `generic_form.html` (از طریق template های اختصاصی که extend می‌کنند)
   - Delete views: مستقیماً از `generic_confirm_delete.html` استفاده می‌کنند

---

## Migration to Generic Templates

تمام template های ماژول shared به template های generic منتقل شده‌اند:

### لیست تغییرات:
- ✅ **List Templates**: همه list templates از `generic_list.html` استفاده می‌کنند
- ✅ **Form Templates**: همه form templates از `generic_form.html` استفاده می‌کنند
- ✅ **Delete Templates**: همه delete views مستقیماً از `generic_confirm_delete.html` استفاده می‌کنند

### مزایا:
- **کاهش تکرار کد**: کد تکراری حذف شد
- **سازگاری UI**: همه صفحات UI یکپارچه دارند
- **نگهداری آسان‌تر**: تغییرات UI فقط در template های generic اعمال می‌شود
- **استانداردسازی**: همه صفحات از context variables یکسان استفاده می‌کنند

### تغییرات کلیدی:
1. `context_object_name` در همه list views به `'object_list'` تغییر یافت
2. Context variables برای generic templates در `get_context_data` اضافه شد
3. Template های اختصاصی delete حذف شدند و از generic استفاده می‌شود
4. Template های form و list از generic extend می‌کنند و فقط blocks لازم را override می‌کنند

---

## مستندات کامل

برای جزئیات کامل هر view، به README اختصاصی هر فایل مراجعه کنید:
- [README_USERS.md](README_USERS.md)
- [README_GROUPS.md](README_GROUPS.md)
- [README_ACCESS_LEVELS.md](README_ACCESS_LEVELS.md)
- [README_COMPANIES.md](README_COMPANIES.md)
- [README_COMPANY_UNITS.md](README_COMPANY_UNITS.md)
- [README_SMTP_SERVER.md](README_SMTP_SERVER.md)


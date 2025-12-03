# accounting/views/ - Other Views Documentation

**هدف**: مستندات سایر view های ماژول accounting

این فایل شامل مستندات view های زیر است:
- `GLAccount` views (`gl_accounts.py`)
- `SubAccount` views (`sub_accounts.py`)
- `TafsiliAccount` views (`tafsili_accounts.py`)
- `TafsiliHierarchy` views (`tafsili_hierarchy.py`)
- `DocumentAttachment` views (`document_attachments.py`)
- `Auth` views (`auth.py`)

---

## فایل‌های README جداگانه

برای جزئیات کامل هر فایل view، به README های زیر مراجعه کنید:

1. ✅ **GL Account Views**: `accounting/views/README_GL_ACCOUNTS.md` - کامل
2. ⏳ **Sub Account Views**: `accounting/views/README_SUB_ACCOUNTS.md` - نیاز به تکمیل
3. ⏳ **Tafsili Account Views**: `accounting/views/README_TAFSILI_ACCOUNTS.md` - نیاز به تکمیل
4. ⏳ **Tafsili Hierarchy Views**: `accounting/views/README_TAFSILI_HIERARCHY.md` - نیاز به تکمیل
5. ⏳ **Document Attachment Views**: `accounting/views/README_DOCUMENT_ATTACHMENTS.md` - نیاز به تکمیل
6. ⏳ **Auth Views**: `accounting/views/README_AUTH.md` - نیاز به تکمیل

---

## خلاصه View ها

### GL Account Views (`gl_accounts.py`)

**4 کلاس view**:
- `GLAccountListView`: فهرست حساب‌های کل (level 1)
- `GLAccountCreateView`: ایجاد حساب کل جدید
- `GLAccountUpdateView`: ویرایش حساب کل (با EditLockProtectedMixin)
- `GLAccountDeleteView`: حذف حساب کل (با بررسی child accounts و system accounts)

**ویژگی‌ها**:
- فیلتر بر اساس search, status, account_type
- Permission-based filtering
- Company scoping

### Sub Account Views (`sub_accounts.py`)

**4 کلاس view**:
- `SubAccountListView`: فهرست حساب‌های معین (level 2)
- `SubAccountCreateView`: ایجاد حساب معین جدید (با M2M GL accounts)
- `SubAccountUpdateView`: ویرایش حساب معین (با EditLockProtectedMixin)
- `SubAccountDeleteView`: حذف حساب معین (با بررسی child accounts و system accounts)

**ویژگی‌ها**:
- فیلتر بر اساس search, status, parent_id (GL account)
- نمایش GL accounts مرتبط در لیست
- M2M relation management

### Tafsili Account Views (`tafsili_accounts.py`)

**4 کلاس view**:
- `TafsiliAccountListView`: فهرست حساب‌های تفصیلی (level 3)
- `TafsiliAccountCreateView`: ایجاد حساب تفصیلی جدید (با M2M sub accounts و floating support)
- `TafsiliAccountUpdateView`: ویرایش حساب تفصیلی (با EditLockProtectedMixin)
- `TafsiliAccountDeleteView`: حذف حساب تفصیلی (با بررسی system accounts)

**ویژگی‌ها**:
- فیلتر بر اساس search, status, parent_id (sub account)
- نمایش sub accounts مرتبط در لیست
- پشتیبانی از تفصیلی شناور (floating tafsili)

### Tafsili Hierarchy Views (`tafsili_hierarchy.py`)

**4 کلاس view**:
- `TafsiliHierarchyListView`: فهرست تفصیلی‌های چند سطحی (با tree structure)
- `TafsiliHierarchyCreateView`: ایجاد تفصیلی چند سطحی جدید
- `TafsiliHierarchyUpdateView`: ویرایش تفصیلی چند سطحی (با EditLockProtectedMixin)
- `TafsiliHierarchyDeleteView`: حذف تفصیلی چند سطحی (با بررسی children)

**ویژگی‌ها**:
- فیلتر بر اساس search, status, level, parent_id
- نمایش مسیر کامل (full path) در لیست
- Tree structure support

### Document Attachment Views (`document_attachments.py`)

**4 کلاس view**:
- `DocumentAttachmentUploadView`: آپلود پیوست‌های اسناد (با multiple file support)
- `DocumentAttachmentListView`: فهرست پیوست‌های اسناد (با فیلترهای پیشرفته)
- `DocumentAttachmentDownloadSingleView`: دانلود یک فایل پیوست
- `DocumentAttachmentDownloadBulkView`: دانلود چندین فایل به صورت ZIP

**ویژگی‌ها**:
- Multiple file upload support
- فیلتر بر اساس document_number, file_type, date range, uploaded_by
- ZIP file generation for bulk download
- Company scoping

### Auth Views (`auth.py`)

**1 function-based view**:
- `set_active_fiscal_year`: تنظیم سال مالی فعال در session (POST only)

**ویژگی‌ها**:
- POST only (decorator: `@require_POST`)
- بررسی تعلق سال مالی به شرکت فعال
- Redirect به صفحه مرجع یا home

---

## ساختار مشترک

همه view های CRUD در این فایل‌ها از ساختار مشترک زیر پیروی می‌کنند:

### ListView ها
- استفاده از `generic_list.html` template
- Permission-based filtering
- Search و filter support
- Pagination (50 items per page)
- Context variables برای table headers و empty states

### CreateView ها
- استفاده از `generic_form.html` template
- اضافه کردن `company_id` به form kwargs
- تنظیم `created_by`
- Success messages
- Breadcrumbs

### UpdateView ها
- استفاده از `generic_form.html` template
- استفاده از `EditLockProtectedMixin`
- اضافه کردن `company_id` به form kwargs
- تنظیم `edited_by`
- Success messages
- Breadcrumbs

### DeleteView ها
- استفاده از `generic_confirm_delete.html` template
- بررسی محدودیت‌ها (system accounts، child accounts، children)
- Success/Error messages
- Breadcrumbs
- Object details برای نمایش

---

## نکات مهم

1. **Permission System**: همه view ها از `FeaturePermissionRequiredMixin` استفاده می‌کنند
2. **Company Scoping**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
3. **Edit Lock**: تمام UpdateView ها از `EditLockProtectedMixin` استفاده می‌کنند
4. **Account Levels**: GL (level 1), Sub (level 2), Tafsili (level 3) به صورت صریح فیلتر می‌شوند
5. **M2M Relations**: SubAccount و TafsiliAccount از M2M fields استفاده می‌کنند که در form.save() مدیریت می‌شوند
6. **Tree Structure**: TafsiliHierarchy از parent/children برای ساختار درختی استفاده می‌کند

---

**Last Updated**: 2025-12-02

**نکته**: برای جزئیات کامل هر view، به README های جداگانه مراجعه کنید.

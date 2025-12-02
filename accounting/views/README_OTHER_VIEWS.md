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

## GL Account Views

### `GLAccountListView`
- فهرست حساب‌های کل (level 1)
- فیلتر بر اساس search, status, account_type

### `GLAccountCreateView`
- ایجاد حساب کل جدید

### `GLAccountUpdateView`
- ویرایش حساب کل

### `GLAccountDeleteView`
- حذف حساب کل

---

## Sub Account Views

### `SubAccountListView`
- فهرست حساب‌های معین (level 2)
- فیلتر بر اساس search, status, parent_id

### `SubAccountCreateView`
- ایجاد حساب معین جدید
- مدیریت ارتباط با حساب‌های کل (M2M)

### `SubAccountUpdateView`
- ویرایش حساب معین
- مدیریت ارتباط با حساب‌های کل (M2M)

### `SubAccountDeleteView`
- حذف حساب معین

---

## Tafsili Account Views

### `TafsiliAccountListView`
- فهرست حساب‌های تفصیلی (level 3)
- فیلتر بر اساس search, status, parent_id

### `TafsiliAccountCreateView`
- ایجاد حساب تفصیلی جدید
- مدیریت ارتباط با حساب‌های معین (M2M)
- پشتیبانی از تفصیلی شناور (floating)

### `TafsiliAccountUpdateView`
- ویرایش حساب تفصیلی
- مدیریت ارتباط با حساب‌های معین (M2M)

### `TafsiliAccountDeleteView`
- حذف حساب تفصیلی

---

## Tafsili Hierarchy Views

### `TafsiliHierarchyListView`
- فهرست تفصیلی‌های چند سطحی

### `TafsiliHierarchyCreateView`
- ایجاد تفصیلی چند سطحی جدید

### `TafsiliHierarchyUpdateView`
- ویرایش تفصیلی چند سطحی

### `TafsiliHierarchyDeleteView`
- حذف تفصیلی چند سطحی

---

## Document Attachment Views

### `DocumentAttachmentUploadView`
- آپلود پیوست‌های اسناد
- پشتیبانی از multiple file upload

### `DocumentAttachmentListView`
- فهرست پیوست‌های اسناد
- فیلتر بر اساس document_number, file_type, date range, uploaded_by

### `DocumentAttachmentDownloadSingleView`
- دانلود یک فایل پیوست

### `DocumentAttachmentDownloadBulkView`
- دانلود چندین فایل به صورت ZIP

---

## Auth Views

### `set_active_fiscal_year(request)`
- Function-based view برای تنظیم سال مالی فعال در session
- POST only
- بررسی تعلق سال مالی به شرکت فعال

---

**نکته**: برای جزئیات کامل هر view، به فایل source مربوطه مراجعه کنید.

**Last Updated**: 2025-12-02


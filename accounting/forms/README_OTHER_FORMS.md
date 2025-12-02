# accounting/forms/ - Other Forms Documentation

**هدف**: مستندات سایر فرم‌های ماژول accounting

این فایل شامل مستندات فرم‌های زیر است:
- `DocumentAttachmentUploadForm` (`document_attachments.py`)
- `GLAccountForm` (`gl_accounts.py`)
- `SubAccountForm` (`sub_accounts.py`)
- `TafsiliAccountForm` (`tafsili_accounts.py`)
- `TafsiliHierarchyForm` (`tafsili_hierarchy.py`)

---

## Document Attachment Forms

### `DocumentAttachmentUploadForm(forms.Form)`

**توضیح**: فرم برای آپلود پیوست‌های اسناد

**Fields**:
- `document_number` (CharField): شماره سند حسابداری
- `files` (FileField): فایل‌های پیوست (multiple support)
- `file_type` (ChoiceField): نوع فایل
- `description` (CharField): توضیحات

---

## GL Account Forms

### `GLAccountForm(forms.ModelForm)`

**Model**: `Account`

**توضیح**: فرم برای ایجاد/ویرایش حساب‌های کل (level 1)

**Fields**: `account_code`, `account_name`, `account_name_en`, `account_type`, `normal_balance`, `opening_balance`, `description`, `is_enabled`

---

## Sub Account Forms

### `SubAccountForm(forms.ModelForm)`

**Model**: `Account`

**توضیح**: فرم برای ایجاد/ویرایش حساب‌های معین (level 2) با ارتباط به حساب‌های کل

**Fields**: `account_code`, `account_name`, `account_name_en`, `normal_balance`, `opening_balance`, `description`, `is_enabled`, `gl_accounts` (M2M)

---

## Tafsili Account Forms

### `TafsiliAccountForm(forms.ModelForm)`

**Model**: `Account`

**توضیح**: فرم برای ایجاد/ویرایش حساب‌های تفصیلی (level 3) با ارتباط به حساب‌های معین

**Fields**: `account_code`, `account_name`, `account_name_en`, `normal_balance`, `opening_balance`, `description`, `is_enabled`, `tafsili_type`, `is_floating`, `sub_accounts` (M2M), `national_id`, `bank_account_number`, `contact_info`

---

## Tafsili Hierarchy Forms

### `TafsiliHierarchyForm(forms.ModelForm)`

**Model**: `TafsiliHierarchy`

**توضیح**: فرم برای ایجاد/ویرایش تفصیلی چند سطحی

**Fields**: `code`, `name`, `name_en`, `parent`, `tafsili_account`, `sort_order`, `description`, `is_enabled`

---

**نکته**: برای جزئیات کامل هر فرم، به فایل source مربوطه مراجعه کنید.

**Last Updated**: 2025-12-02


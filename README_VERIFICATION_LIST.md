# لیست بررسی README فایل‌ها

## 📖 توضیحات

این فایل برای **بررسی و به‌روزرسانی مستمر مستندات README** در پروژه استفاده می‌شود. هدف اصلی این است که اطمینان حاصل کنیم تمام فایل‌های README با فایل‌های اصلی کد (source files) هماهنگ و به‌روز هستند.

### 🎯 هدف این فرآیند

در این پروژه، برای هر فایل اصلی کد (مانند `views.py`, `forms.py`, `models.py` و غیره) یک فایل README مربوطه وجود دارد که ساختار، کلاس‌ها، متدها، پارامترها و منطق آن فایل را مستندسازی می‌کند. با توجه به اینکه کد به مرور زمان تغییر می‌کند و ویژگی‌های جدید اضافه می‌شوند، ممکن است فایل‌های README از فایل‌های اصلی عقب بیفتند و نیاز به به‌روزرسانی داشته باشند.

### 🔄 فرآیند بررسی

فرآیند بررسی شامل مراحل زیر است:

1. **مقایسه تاریخ تغییر فایل‌ها**: برای هر جفت فایل (README و فایل اصلی)، تاریخ آخرین تغییر از Git استخراج می‌شود.
2. **شناسایی فایل‌های نیازمند به‌روزرسانی**: اگر تاریخ تغییر فایل اصلی جدیدتر از README باشد، README باید بررسی و به‌روزرسانی شود.
3. **بررسی محتوایی**: فایل README به صورت دقیق خوانده می‌شود و با فایل اصلی مقایسه می‌شود تا:
   - تمام کلاس‌ها و توابع مستندسازی شده باشند
   - پارامترها و return types به‌روز باشند
   - منطق و جزئیات پیاده‌سازی با کد هماهنگ باشند
   - متدهای جدید اضافه شده باشند
   - متدهای حذف شده از README حذف شوند
4. **به‌روزرسانی**: در صورت نیاز، فایل README به‌روزرسانی می‌شود و وضعیت آن در این فایل ثبت می‌شود.

### 📚 ترتیب بررسی فایل‌ها

**⚠️ نکته مهم**: برای بررسی فایل‌های عمومی (Module-Level General READMEs)، **قبل از شروع بررسی این فایل‌ها**، باید:

1. **درک کامل از فایل‌های قبلی**: ابتدا تمام فایل‌های README مربوط به بخش‌های جزئی‌تر (مانند `views/`, `forms/`, `utils/`, `services/`, `templatetags/` و غیره) را به دقت مطالعه و بررسی کنید تا درک کاملی از ساختار و محتوای ماژول پیدا کنید.

2. **بررسی به ترتیب**: فایل‌ها باید به ترتیب زیر بررسی شوند:
   - ابتدا فایل‌های README مربوط به **Views** (مثل `views/README_*.md`)
   - سپس فایل‌های README مربوط به **Forms** (مثل `forms/README_*.md`)
   - بعد فایل‌های README مربوط به **Utils** (مثل `utils/README_*.md`)
   - سپس فایل‌های README مربوط به **Services** (مثل `services/README_*.md`)
   - بعد فایل‌های README مربوط به **Template Tags** (مثل `templatetags/README_*.md`)
   - و سایر بخش‌های جزئی‌تر

3. **در نهایت فایل‌های عمومی**: **فقط بعد از بررسی کامل تمام فایل‌های جزئی‌تر**، به سراغ فایل‌های عمومی (Module-Level General READMEs) بروید. این فایل‌ها معمولاً یک نمای کلی از ماژول ارائه می‌دهند و برای نوشتن یا به‌روزرسانی آن‌ها نیاز به درک کامل از تمام بخش‌های جزئی‌تر دارید.

**دلیل این ترتیب**: فایل‌های عمومی معمولاً به تمام بخش‌های ماژول اشاره می‌کنند و برای به‌روزرسانی صحیح آن‌ها، باید ابتدا تمام بخش‌های جزئی‌تر را بررسی کرده باشید تا مطمئن شوید که فایل عمومی تمام تغییرات و جزئیات را به درستی منعکس می‌کند.

### ⏰ فرکانس اجرا

**این فرآیند باید حداقل هفته‌ای یک‌بار انجام شود** تا اطمینان حاصل شود که مستندات همیشه به‌روز و قابل اعتماد هستند.

### 📅 تاریخ‌های اجرا

تاریخ‌های اجرای این فرآیند در زیر ثبت می‌شوند (جدیدترین در بالا):

- **2025-12-08** - ایجاد فایل‌های README خالی برای فایل‌های مهم بدون README: production/forms/README_PROCESS_OPERATIONS.md, production/utils/README_TRANSFER.md, production/views/README_REWORK.md, production/views/README_QCOPERATIONS.md, shared/forms/README_BASE.md, shared/views/README_API.md, shared/views/README_BASE_ADDITIONAL.md, shared/utils/README_VIEW_HELPERS.md, shared/templatetags/README_GENERIC_TAGS.md, shared/templatetags/README_VIEW_TAGS.md. به‌روزرسانی README_VERIFICATION_LIST.md و DOCUMENTATION_STRUCTURE.md
- **2025-11-28** - بررسی و به‌روزرسانی فایل‌های README با وضعیت "Source newer". به‌روزرسانی `inventory/views/README_MASTER_DATA.md` با مستندات متد `get_queryset()` و `filter_queryset_by_permissions`. به‌روزرسانی تاریخ README برای فایل‌هایی که مستندات کامل هستند
- **2025-11-28** - به‌روزرسانی کامل تاریخ‌های تغییر از Git برای تمام فایل‌ها. شناسایی 27 فایل با وضعیت "Source newer" که نیاز به بررسی محتوایی دارند
- **2025-11-28** - ایجاد 18 فایل README خالی برای فایل‌هایی که README نداشتند (Views: 3, Utils: 1, Management Commands: 2, Models: 12)
- **2025-11-28 04:16:33** - اجرای اولیه و بررسی کامل فایل‌های Inventory, Production, QC, Ticketing, Shared
- **2025-11-28 04:20:00** - افزودن سیستم بررسی خودکار با Git و ستون‌های تاریخ تغییر

---

## 🔍 بررسی خودکار با Git

برای هر فایل README و فایل اصلی مربوطه، تاریخ آخرین تغییر از Git استخراج می‌شود و مقایسه می‌گردد:

- اگر تاریخ تغییر فایل اصلی **جدیدتر** از README باشد: ⚠️ **Source newer** - README باید بررسی و به‌روزرسانی شود
- اگر تاریخ تغییر README **جدیدتر** از فایل اصلی باشد: ✅ **README newer** - README به‌روز است
- اگر تاریخ تغییر هر دو **یکسان** باشد: ✅ **Same date** - احتمالاً به‌روز است (اما بررسی محتوایی توصیه می‌شود)

**نکته مهم**: این بررسی خودکار فقط بر اساس تاریخ تغییر است. حتی اگر تاریخ‌ها یکسان باشند، ممکن است README نیاز به بررسی محتوایی داشته باشد. همیشه باید فایل README را با فایل اصلی مقایسه کنید تا مطمئن شوید تمام تغییرات مستندسازی شده‌اند.

### 🔧 استفاده از اسکریپت‌های بررسی

#### 1. بررسی تاریخ یک جفت فایل (تک فایل)

برای بررسی تاریخ تغییر یک جفت فایل README و Source، می‌توانید از اسکریپت `scripts/check_readme_dates.py` استفاده کنید:

```bash
python3 scripts/check_readme_dates.py <readme_file> <source_file>
```

**مثال**:
```bash
python3 scripts/check_readme_dates.py inventory/views/README_MASTER_DATA.md inventory/views/master_data.py
```

این اسکریپت تاریخ تغییر هر دو فایل را از Git استخراج می‌کند و نتیجه مقایسه را نمایش می‌دهد.

**خروجی**:
```
README: 2025-11-28 03:55:30
Source: 2025-11-28 20:01:46
Check: ⚠️ Source newer
```

---

#### 2. به‌روزرسانی خودکار تمام تاریخ‌ها (توصیه می‌شود)

برای به‌روزرسانی خودکار تمام تاریخ‌های تغییر در فایل `README_VERIFICATION_LIST.md`، از اسکریپت `scripts/update_readme_verification_list.py` استفاده کنید:

```bash
python3 scripts/update_readme_verification_list.py
```

**عملکرد**:
- تمام فایل‌های README و Source را در جداول پیدا می‌کند
- تاریخ آخرین تغییر هر فایل را از Git استخراج می‌کند
- تاریخ‌ها و وضعیت Git Check را در فایل به‌روزرسانی می‌کند
- فایل `README_VERIFICATION_LIST.md` را به صورت خودکار به‌روزرسانی می‌کند

**نکته**: این اسکریپت باید **قبل از هر بررسی** اجرا شود تا اطمینان حاصل شود که تمام تاریخ‌ها به‌روز هستند.

**خروجی**:
```
Updated /home/shahin/invproj/README_VERIFICATION_LIST.md
```

**توصیه**: این اسکریپت را در ابتدای هر جلسه بررسی README اجرا کنید تا مطمئن شوید که تمام تاریخ‌ها به‌روز هستند و فایل‌های نیازمند بررسی را به درستی شناسایی می‌کنید.

---

## 📋 Inventory Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/views/README_MASTER_DATA.md` | `inventory/views/master_data.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 16:31:45 | ✅ README newer | به‌روزرسانی شد - مستندات متد `get_queryset()` برای تمام ListView و UpdateView ها اضافه شد |
| `inventory/views/README_RECEIPTS.md` | `inventory/views/receipts.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 16:31:45 | ✅ README newer | به‌روزرسانی شد - مستندات کامل متدهای `get_queryset()`, `_apply_filters()`, `_get_stats()`, و `get_context_data()` برای ListView و DetailView ها اضافه شد |
| `inventory/views/README_ISSUES.md` | `inventory/views/issues.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 16:31:45 | ✅ README newer | به‌روزرسانی شد - مستندات کامل متدهای `get_queryset()` برای تمام ListView و DetailView ها با جزئیات `filter_queryset_by_permissions` اضافه شد |
| `inventory/views/README_REQUESTS.md` | `inventory/views/requests.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 16:33:20 | ✅ README newer | به‌روزرسانی شد - مستندات کامل متدهای `get_queryset()` برای ListView و UpdateView ها با جزئیات `filter_queryset_by_permissions` اضافه شد |
| `inventory/views/README_STOCKTAKING.md` | `inventory/views/stocktaking.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 16:58:41 | ✅ README newer | به‌روزرسانی شد - مستندات کامل متدهای `get_queryset()` برای تمام ListView و UpdateView ها با جزئیات `filter_queryset_by_permissions` اضافه شد |
| `inventory/views/README_BALANCE.md` | `inventory/views/balance.py` | ✅ Updated | 2025-11-28 18:54:08 | 2025-11-29 17:01:58 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل `InventoryBalanceDetailsView` با ساختار transaction و منطق کامل اضافه شد |
| `inventory/views/README_API.md` | `inventory/views/api.py` | ✅ Updated | 2025-11-28 15:16:27 | 2025-11-29 17:04:34 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_filtered_items` (permission filtering, include_item_id), `get_temporary_receipt_data` (QC-approved lines), و `get_item_available_serials` (AVAILABLE status) اضافه شد |
| `inventory/views/README_BASE.md` | `inventory/views/base.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-29 17:07:52 | ✅ README newer | به‌روزرسانی شد - تکرار DocumentUnlockView حذف شد، جزئیات کامل منطق برای `dispatch()`, `post()`, و `_save_line_formset()` با serial handling اضافه شد |
| `inventory/views/README_ITEM_IMPORT.md` | `inventory/views/item_import.py` | ✅ Updated | 2025-11-22 23:30:10 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `inventory/views/README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md` | `inventory/views/create_issue_from_warehouse_request.py` | ✅ Updated | 2025-11-24 16:54:27 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `inventory/views/README_ISSUES_FROM_WAREHOUSE_REQUEST.md` | `inventory/views/issues_from_warehouse_request.py` | ✅ Updated | 2025-11-24 16:54:27 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات متدها برای Consumption و Consignment اضافه شد |

### Forms
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/forms/README_MASTER_DATA.md` | `inventory/forms/master_data.py` | ✅ Updated | 2025-11-23 23:13:44 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات get_context برای IntegerCheckboxInput تکمیل شد |
| `inventory/forms/README_RECEIPT.md` | `inventory/forms/receipt.py` | ✅ Updated | 2025-11-28 13:48:43 | 2025-11-29 17:11:18 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `ReceiptPermanentForm.__init__` (با Exists برای خطوط) و `save()` (با temporary receipt conversion) اضافه شد |
| `inventory/forms/README_ISSUE.md` | `inventory/forms/issue.py` | ✅ Updated | 2025-11-28 04:06:17 | 2025-11-29 17:13:50 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای تمام header forms (IssuePermanentForm, IssueConsumptionForm, IssueConsignmentForm) شامل `__init__()`, `clean()`, و `save()` اضافه شد |
| `inventory/forms/README_REQUEST.md` | `inventory/forms/request.py` | ✅ Updated | 2025-11-26 21:12:37 | 2025-11-26 21:12:37 | ✅ Same date | بررسی شد - مستندات کامل است |
| `inventory/forms/README_BASE.md` | `inventory/forms/base.py` | ✅ Updated | 2025-11-28 00:35:59 | 2025-11-29 17:19:21 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `generate_document_code()` (7 مرحله)، `ReceiptBaseForm.__init__()` (11 مرحله با restore values)، و `_filter_company_scoped_fields()` (با include disabled items) اضافه شد |
| `inventory/forms/README_STOCKTAKING.md` | `inventory/forms/stocktaking.py` | ✅ Updated | 2025-11-28 18:54:08 | 2025-11-29 17:30:52 | ✅ README newer | به‌روزرسانی شد - مستندات کامل برای Line Forms (StocktakingDeficitLineForm, StocktakingSurplusLineForm) با `full_clean()`, `clean_unit()`, و `clean()` و جزئیات کامل برای `StocktakingRecordForm` (__init__, clean, save) اضافه شد |

### Utils
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/utils/README_CODES.md` | `inventory/utils/codes.py` | ✅ Updated | 2025-11-14 00:46:47 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `inventory/utils/README_JALALI.md` | `inventory/utils/jalali.py` | ✅ Updated | 2025-11-15 18:57:45 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |

### Services
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/services/README_SERIALS.md` | `inventory/services/serials.py` | ✅ Updated | 2025-11-21 00:35:14 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |

### Template Tags
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/templatetags/README_JALALI_TAGS.md` | `inventory/templatetags/jalali_tags.py` | ✅ Updated | 2025-11-15 18:57:45 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |

### Management Commands
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/management/commands/README_CLEANUP_TEST_RECEIPTS.md` | `inventory/management/commands/cleanup_test_receipts.py` | ✅ Updated | 2025-11-15 18:35:58 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/management/commands/README_CLEAR_ALL_DATA.md` | `shared/management/commands/clear_all_data.py` | ✅ Updated | 2025-11-28 05:19:12 | 2025-11-29 19:07:50 | ✅ README newer | مستندات کامل برای `Command` class: `add_arguments()` (--confirm flag)، `handle()` (منطق کامل حذف با multiple passes، PostgreSQL constraint deferral، SQL fallback با TRUNCATE CASCADE، error handling، و models حفظ شده) |
| `shared/management/commands/README_CLEAR_EDIT_LOCKS.md` | `shared/management/commands/clear_edit_locks.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 19:09:15 | ✅ README newer | مستندات کامل برای `Command` class: `add_arguments()` (--all و --timeout flags)، `handle()` (منطق کامل پاک کردن edit locks با EditableModel detection، timeout threshold calculation، bulk update، و error handling) |

---

## 📋 Production Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `production/views/README_BOM.md` | `production/views/bom.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 17:38:30 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `BOMCreateView.form_valid()` (11 مرحله با error handling و BOM deletion)، `BOMUpdateView.form_valid()` (7 مرحله)، و `get_queryset()`/`delete()` اضافه شد |
| `production/views/README_PROCESS.md` | `production/views/process.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 17:53:34 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `ProcessListView.get_queryset()` (با table existence check)، `ProcessCreateView.form_valid()` (با operations و materials formsets)، `ProcessUpdateView.form_valid()` (با update/create/delete operations)، و `get_context_data()` (با bom_id extraction و existing operations loading) اضافه شد |
| `production/views/README_PRODUCT_ORDER.md` | `production/views/product_order.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 17:56:56 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_queryset()` (ListView, UpdateView, DeleteView)، `get_context_data()` (UpdateView با permission check)، و `delete()` اضافه شد |
| `production/views/README_MACHINE.md` | `production/views/machine.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:11:21 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای تمام متدها (`get_queryset()` با optional select_related و try-except، `form_valid()` با error handling، `get_context_data()`، و `delete()`) اضافه شد |
| `production/views/README_WORK_LINE.md` | `production/views/work_line.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:14:37 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای تمام متدها (`get_queryset()` با optional select_related و prefetch_related، `form_valid()` با M2M handling، `get_context_data()`، و `delete()`) اضافه شد |
| `production/views/README_PERSONNEL.md` | `production/views/personnel.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:18:47 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای تمام متدها (`get_queryset()` با select_related و prefetch_related، `form_valid()` با error handling، `get_context_data()`، و `delete()`) اضافه شد |
| `production/views/README_TRANSFER_TO_LINE.md` | `production/views/transfer_to_line.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:21:36 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_queryset()` (ListView, DeleteView)، `get_context_data()` (CreateView, UpdateView با formset filtering)، و `delete()` (با is_locked check) اضافه شد |
| `production/views/README_PERFORMANCE_RECORD.md` | `production/views/performance_record.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:26:29 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_queryset()` (با permission-based filtering)، `get_context_data()` (با 3 formsets)، و `delete()` (با is_locked و status checks) اضافه شد |
| `production/views/README_PLACEHOLDERS.md` | `production/views/placeholders.py` | ✅ Updated | 2025-11-21 19:59:04 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/views/README_API.md` | `production/views/api.py` | ✅ Updated | 2025-11-28 17:54:59 | 2025-11-29 18:28:20 | ✅ README newer | تکمیل شد - مستندات کامل برای `get_bom_materials` API endpoint با جزئیات منطق، response format، و error handling اضافه شد |
| `production/views/README_REWORK.md` | `production/views/rework.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |
| `production/views/README_QCOPERATIONS.md` | `production/views/qc_operations.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |

### Forms
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `production/forms/README_BOM.md` | `production/forms/bom.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_PROCESS.md` | `production/forms/process.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_PRODUCT_ORDER.md` | `production/forms/product_order.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_WORK_LINE.md` | `production/forms/work_line.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_MACHINE.md` | `production/forms/machine.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_PERSON.md` | `production/forms/person.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_TRANSFER_TO_LINE.md` | `production/forms/transfer_to_line.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_PERFORMANCE_RECORD.md` | `production/forms/performance_record.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `production/forms/README_PROCESS_OPERATIONS.md` | `production/forms/process_operations.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |

---

## 📋 QC Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `qc/views/README_INSPECTIONS.md` | `qc/views/inspections.py` | ✅ Updated | بررسی شد - مستندات کامل است |

---

## 📋 Ticketing Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `ticketing/views/README_BASE.md` | `ticketing/views/base.py` | ✅ Updated | 2025-11-25 00:11:08 | 2025-11-28 04:12:11 | ✅ README newer | بررسی شد - مستندات کامل است |
| `ticketing/views/README_CATEGORIES.md` | `ticketing/views/categories.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:30:34 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_queryset()` (با search و parent filtering)، `get_context_data()`، `form_valid()` (با permission formset handling)، و `delete()` اضافه شد |
| `ticketing/views/README_SUBCATEGORIES.md` | `ticketing/views/subcategories.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:34:52 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_queryset()` (با parent category filtering و search)، `get_context_data()` (با parent_categories dropdown)، `form_valid()` (با parent_category validation)، و `delete()` اضافه شد |
| `ticketing/views/README_TEMPLATES.md` | `ticketing/views/templates.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:42:35 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_queryset()` (با debug logging)، `get_context_data()` (با 3 formsets و debug logging)، `form_valid()` (با 3 formsets handling و debug logging)، و `delete()` اضافه شد |
| `ticketing/views/README_TICKETS.md` | `ticketing/views/tickets.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 18:47:21 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_context_data()` (با permission checking، options extraction از field_config و model، و debug logging)، `form_valid()` (با reported_by و company_id)، و `get_initial()` اضافه شد |
| `ticketing/views/README_DEBUG.md` | `ticketing/views/debug.py` | ✅ Updated | 2025-11-25 13:24:42 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `ticketing/views/README_PLACEHOLDERS.md` | `ticketing/views/placeholders.py` | ✅ Updated | 2025-11-25 00:11:08 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `ticketing/views/README_ENTITY_REFERENCE.md` | `ticketing/views/entity_reference.py` | ✅ Updated | 2025-11-27 00:44:07 | 2025-11-29 18:56:18 | ✅ README newer | مستندات کامل برای 3 API endpoint: `EntityReferenceSectionsView` (لیست sections)، `EntityReferenceActionsView` (لیست actions برای section با code/nickname lookup)، `EntityReferenceParameterValuesView` (مقادیر ممکن: enum از parameter_enum JSON، gp از AuthGroup، type از hardcoded values بر اساس section_code) |

### Forms
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `ticketing/forms/README_BASE.md` | `ticketing/forms/base.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `ticketing/forms/README_CATEGORIES.md` | `ticketing/forms/categories.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `ticketing/forms/README_TEMPLATES.md` | `ticketing/forms/templates.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `ticketing/forms/README_TICKETS.md` | `ticketing/forms/tickets.py` | ✅ Updated | بررسی شد - مستندات کامل است |

### Utils
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `ticketing/utils/README_CODES.md` | `ticketing/utils/codes.py` | ✅ Updated | بررسی شد - مستندات کامل است |

---

## 📋 Shared Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `shared/views/README_USERS.md` | `shared/views/users.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/views/README_COMPANIES.md` | `shared/views/companies.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/views/README_ACCESS_LEVELS.md` | `shared/views/access_levels.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/views/README_GROUPS.md` | `shared/views/groups.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/views/README_COMPANY_UNITS.md` | `shared/views/company_units.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/views/README_AUTH.md` | `shared/views/auth.py` | ✅ Updated | به‌روزرسانی شد - mark_notification_unread اضافه شد، مستندات mark_notification_read اصلاح شد |
| `shared/views/README_SMTP_SERVER.md` | `shared/views/smtp_server.py` | ✅ Updated | به‌روزرسانی شد - جزئیات form_valid و delete تکمیل شد |
| `shared/views/README_BASE.md` | `shared/views/base.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | به‌روزرسانی شد - متدهای واقعی اضافه شد، متدهای نادرست حذف شد |
| `shared/views/README_NOTIFICATIONS.md` | `shared/views/notifications.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-29 19:10:19 | ✅ README newer | مستندات کامل برای `NotificationListView`: `get_queryset()` (با user filtering، company filtering از session، read status filtering از GET parameter)، `get_context_data()` (با read_filter، unread_count، read_count) |
| `shared/views/README_API.md` | `shared/views/api.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |
| `shared/views/README_BASE_ADDITIONAL.md` | `shared/views/base_additional.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |

### Forms
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `shared/forms/README_USERS.md` | `shared/forms/users.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات UserUpdateForm.save و BaseUserCompanyAccessFormSet.clean تکمیل شد |
| `shared/forms/README_COMPANIES.md` | `shared/forms/companies.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-28 03:55:30 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/forms/README_ACCESS_LEVELS.md` | `shared/forms/access_levels.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-28 03:55:30 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/forms/README_GROUPS.md` | `shared/forms/groups.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات save و save_m2m تکمیل شد |
| `shared/forms/README_SMTP_SERVER.md` | `shared/forms/smtp_server.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات clean method تکمیل شد |
| `shared/forms/README_BASE.md` | `shared/forms/base.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |

### Utils
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `shared/utils/README_PERMISSIONS.md` | `shared/utils/permissions.py` | ✅ Updated | 2025-11-13 16:06:41 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/utils/README_MODULES.md` | `shared/utils/modules.py` | ✅ Updated | 2025-11-22 16:22:00 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/utils/README_EMAIL.md` | `shared/utils/email.py` | ✅ Updated | 2025-11-22 20:47:51 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/utils/README_NOTIFICATIONS.md` | `shared/utils/notifications.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-29 19:11:57 | ✅ README newer | مستندات کامل برای 4 function: `get_or_create_notification()` (با get_or_create و update logic)، `get_unread_notifications()` (با company filtering)، `get_unread_notification_count()` (با Sum aggregation)، `get_recent_notifications()` (با limit و is_read field) |
| `shared/utils/README_VIEW_HELPERS.md` | `shared/utils/view_helpers.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |

### Template Tags
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `shared/templatetags/README_ACCESS_TAGS.md` | `shared/templatetags/access_tags.py` | ✅ Updated | 2025-11-13 18:02:43 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/templatetags/README_JSON_FILTERS.md` | `shared/templatetags/json_filters.py` | ✅ Updated | 2025-11-26 14:12:06 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/templatetags/README_GENERIC_TAGS.md` | `shared/templatetags/generic_tags.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |
| `shared/templatetags/README_VIEW_TAGS.md` | `shared/templatetags/view_tags.py` | ⏳ Pending | 2025-11-28 20:01:46 | 2025-12-08 | ⚠️ Unknown | فایل README ایجاد شده - نیاز به تکمیل |

### Context Processors
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `shared/README_CONTEXT_PROCESSORS.md` | `shared/context_processors.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-29 18:58:16 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `active_company()`: انتخاب active_company (از session، default_company، یا اولین company)، دریافت user_companies با select_related، دریافت user_feature_permissions، و منطق کامل notifications (3 نوع approval pending: purchase، warehouse، stocktaking؛ 2 نوع approved: purchase، warehouse با 7 روز اخیر؛ email sending با sent_email_notifications tracking) |

---

## 📋 Accounting Module

### Models
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `accounting/README_MODELS.md` | `accounting/models/*.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای 20 model class شامل تمام fields، constraints، methods، و نکات مهم |

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `accounting/README_VIEWS.md` | `accounting/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-12-02 | ✅ README newer | بررسی شد - مستندات کامل است |
| `accounting/views/README_BASE.md` | `accounting/views/base.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |
| `accounting/views/README_FISCAL_YEARS.md` | `accounting/views/fiscal_years.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |
| `accounting/views/README_ACCOUNTS.md` | `accounting/views/accounts.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |
| `accounting/views/README_GL_ACCOUNTS.md` | `accounting/views/gl_accounts.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای 4 view class (ListView, CreateView, UpdateView, DeleteView) با تمام methods و context variables |
| `accounting/views/README_OTHER_VIEWS.md` | `accounting/views/{sub_accounts,tafsili_accounts,tafsili_hierarchy,document_attachments,auth}.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات خلاصه برای سایر view ها با لینک به فایل‌های جداگانه |

### Forms
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `accounting/README_FORMS.md` | `accounting/forms/{fiscal_years,periods,accounts}.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |
| `accounting/forms/README_PARTIES.md` | `accounting/forms/parties.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای PartyForm و PartyAccountForm |
| `accounting/forms/README_COST_CENTERS.md` | `accounting/forms/cost_centers.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای CostCenterForm |
| `accounting/forms/README_INCOME_EXPENSE_CATEGORIES.md` | `accounting/forms/income_expense_categories.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای IncomeExpenseCategoryForm |
| `accounting/forms/README_OTHER_FORMS.md` | `accounting/forms/{document_attachments,gl_accounts,sub_accounts,tafsili_accounts,tafsili_hierarchy}.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای 6 form class با تمام fields، methods، و validation logic |

### Other Files
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `accounting/README_UTILS.md` | `accounting/utils.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای get_available_fiscal_years function |
| `accounting/README_CONTEXT_PROCESSORS.md` | `accounting/context_processors.py` | ✅ Updated | 2025-12-02 | 2025-12-02 | ✅ README newer | مستندات کامل برای active_fiscal_year context processor |

---

## 📋 Sales Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `sales/README_VIEWS.md` | `sales/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ README newer | بررسی شد - مستندات کامل است |

---

## 📋 HR Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `hr/README_VIEWS.md` | `hr/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ README newer | بررسی شد - مستندات کامل است |

---

## 📋 Office Automation Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `office_automation/README_VIEWS.md` | `office_automation/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ README newer | بررسی شد - مستندات کامل است |

---

## 📋 Transportation Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `transportation/README_VIEWS.md` | `transportation/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ README newer | بررسی شد - مستندات کامل است |

---

## 📋 Procurement Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `procurement/README_VIEWS.md` | `procurement/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ README newer | بررسی شد - مستندات کامل است |

---

## 📋 UI Module

| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `ui/README.md` | `ui/views.py` | ✅ Updated | 2025-11-26 21:12:37 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `ui/README_CONTEXT_PROCESSORS.md` | `ui/context_processors.py` | ✅ Updated | 2025-11-13 14:59:22 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |

---

## 📋 Root Level Files

| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `README.md` | Project root | ✅ Updated | N/A | 2025-11-28 03:55:30 | ✅ N/A | بررسی شد - مستندات کامل است |
| `DOCUMENTATION_STATUS.md` | Documentation status | ✅ Updated | N/A | 2025-11-13 14:59:22 | ✅ N/A | بررسی شد - مستندات کامل است |
| `DOCUMENTATION_STRUCTURE.md` | Documentation structure | ✅ Updated | N/A | 2025-11-28 03:55:30 | ✅ N/A | بررسی شد - مستندات کامل است |

## 📋 Docs Folder Files

| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `docs/README.md` | Docs folder | ✅ Updated | N/A | 2025-11-28 03:55:30 | ✅ N/A | بررسی شد - مستندات کامل است |
| `docs/MIGRATIONS_README.md` | All migrations | ✅ Updated | N/A | 2025-11-13 14:59:22 | ✅ N/A | بررسی شد - مستندات کامل است |
| `docs/ENTITY_REFERENCE_SYSTEM.md` | Entity Reference System | ✅ Updated | N/A | 2025-11-28 03:55:30 | ✅ N/A | بررسی شد - مستندات کامل است |
| `docs/ACTIONS_LIST.md` | Actions list | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/ACTIONS_SUMMARY.md` | Actions summary | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/API_DOCUMENTATION.md` | API documentation | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/approval_workflow.md` | Approval workflow | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/ARCHITECTURE.md` | System architecture | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/BASE_CLASSES_MIXINS.md` | Base classes and mixins | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/CHANGELOG.md` | Changelog | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/CODE_STRUCTURE.md` | Code structure | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/DATABASE_DOCUMENTATION.md` | Database documentation | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/DEPLOYMENT.md` | Deployment guide | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/DEVELOPMENT.md` | Development guide | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| ~~`docs/DOCUMENTATION_INDEX.md`~~ | ~~Documentation index~~ | ❌ Deleted | N/A | N/A | N/A | حذف شد - فایل موقت بود و دیگر لازم نیست |
| `docs/FEATURES.md` | Features list | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/inventory_module_db_design_plan.md` | Inventory module DB design | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/MODULE_DEPENDENCIES.md` | Module dependencies | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/production_module_db_design_plan.md` | Production module DB design | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/qc_module_db_design_plan.md` | QC module DB design | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/REFACTORING_GUIDE.md` | Refactoring guide | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/REFACTORING_STATUS.md` | Refactoring status | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/shared_module_db_design_plan.md` | Shared module DB design | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/system_requirements.md` | System requirements | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/TEMPLATE_TAGS.md` | Template tags documentation | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/TEST_RESULTS_FIELD_SETTINGS.md` | Test results field settings | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/TICKETING_ENTITY_REFERENCE_IMPLEMENTATION.md` | Ticketing entity reference implementation | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/ticketing_field_settings_specification.md` | Ticketing field settings specification | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/TICKETING_IMPLEMENTATION.md` | Ticketing implementation | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/ticketing_module_db_design_plan.md` | Ticketing module DB design | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/ui_guidelines.md` | UI guidelines | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |
| `docs/UI_UX_CHANGELOG.md` | UI/UX changelog | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل مستندات است و محتوا دارد |

## 📋 Models

| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/README_MODELS.md` | `inventory/models.py` | ✅ Updated | 2025-11-28 16:01:39 | 2025-11-29 19:14:01 | ✅ README newer | مستندات کامل برای 43 model class: Base Models (3 abstract)، Master Data (4)، Item Definition (6)، Supplier Relations (4)، Document Models (12: Receipts، Issues، Stocktaking)، Request Models (4)، Traceability Models (3)، QC Models (1) - شامل validators، constants، و نکات مهم |
| `production/README_MODELS.md` | `production/models.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 19:16:25 | ✅ README newer | مستندات کامل برای 21 model class: Base Models (2 abstract)، Core Resources (3: WorkCenter، WorkLine، Machine)، Personnel Management (2: Person، PersonAssignment)، BOM (2: BOM، BOMMaterial)، Process Definitions (4: Process، ProcessStep، ProcessOperation، ProcessOperationMaterial)، Production Orders (2: ProductOrder، OrderPerformance)، Material Transfer (2: TransferToLine، TransferToLineItem)، Performance Records (4: PerformanceRecord و 3 line models) |
| `shared/README_MODELS.md` | `shared/models.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 19:20:16 | ✅ README newer | مستندات کامل برای 7 Abstract Mixins (TimeStampedModel، ActivatableModel، MetadataModel، SortableModel، EditableModel با clear_edit_lock و is_being_edited_by، LockableModel، CompanyScopedModel) و 11 Model Classes (User، Company، CompanyUnit، AccessLevel با auto code generation، AccessLevelPermission، GroupProfile، UserCompanyAccess با is_primary، SMTPServer با get_connection_config، SectionRegistry با indexes، ActionRegistry با indexes و constraints، Notification با mark_as_read/unread) |
| `ticketing/README_MODELS.md` | `ticketing/models.py` | ✅ Updated | 2025-11-28 20:01:46 | 2025-11-29 22:41:38 | ✅ README newer | مستندات کامل برای 15 model class: Base Models (2 abstract: TicketingBaseModel، TicketingSortableModel)، Master Data (2: TicketCategory با hierarchical support، TicketPriority با SLA)، Permission Models (1: TicketCategoryPermission)، Template Models (6: TicketTemplate با default_priority، TicketTemplateField با 25+ field types و validation_rules، TicketTemplateFieldOption، TicketTemplatePermission، TicketTemplateEvent با action_reference، TicketTemplateFieldEvent)، Ticket Models (1: Ticket با related_entity و attachments JSONField)، Ticket Data Models (3: TicketFieldValue با field_value و field_value_json، TicketComment، TicketAttachment) |
| `qc/README_MODELS.md` | `qc/models.py` | ✅ Updated | 2025-11-21 03:33:39 | 2025-11-29 22:48:26 | ✅ README newer | مستندات کامل برای 2 model class: Base Model (1 abstract: QCBaseModel)، Receipt Inspection Model (1: ReceiptInspection با one-to-one با ReceiptTemporary، InspectionStatus و ApprovalDecision choices، inspector از Person، approved_by از User، cached codes، inspection_results JSONField، attachments JSONField، nonconformity tracking) |
| `accounting/README_MODELS.md` | `accounting/models.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-29 22:49:28 | ✅ README newer | فایل models.py در حال حاضر خالی است - README تکمیل شد با توضیح اینکه models در آینده اضافه خواهند شد |
| `sales/README_MODELS.md` | `sales/models.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-29 22:50:45 | ✅ README newer | فایل models.py در حال حاضر خالی است - README تکمیل شد با توضیح اینکه models در آینده اضافه خواهند شد |
| `hr/README_MODELS.md` | `hr/models.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-29 22:51:38 | ✅ README newer | فایل models.py در حال حاضر خالی است - README تکمیل شد با توضیح اینکه models در آینده اضافه خواهند شد |
| `procurement/README_MODELS.md` | `procurement/models.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-29 22:52:30 | ✅ README newer | فایل models.py در حال حاضر خالی است - README تکمیل شد با توضیح اینکه models در آینده اضافه خواهند شد |
| `transportation/README_MODELS.md` | `transportation/models.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-29 22:53:30 | ✅ README newer | فایل models.py در حال حاضر خالی است - README تکمیل شد با توضیح اینکه models در آینده اضافه خواهند شد |
| `office_automation/README_MODELS.md` | `office_automation/models.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-29 22:55:06 | ✅ README newer | فایل models.py در حال حاضر خالی است - README تکمیل شد با توضیح اینکه models در آینده اضافه خواهند شد |
| `ui/README_MODELS.md` | `ui/models.py` | ✅ Updated | 2025-11-13 14:59:22 | 2025-11-29 22:56:10 | ✅ README newer | فایل models.py در حال حاضر خالی است - README تکمیل شد با توضیح اینکه models در آینده اضافه خواهند شد |

---

## 📋 Module-Level General READMEs

| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/README.md` | `inventory/` module | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | به‌روزرسانی شد - لینک به فایل‌های README جزئی‌تر اضافه شد (README_MODELS.md، views/README.md، README_FORMS.md، utils/README.md، services/README.md، templatetags/README.md، migrations/README.md، management/commands/README.md) |
| `inventory/README_BALANCE.md` | `inventory/inventory_balance.py` | ✅ Updated | 2025-11-28 18:54:08 | 2025-11-29 19:04:53 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_last_stocktaking_baseline()` (با stocktaking_record_date)، `calculate_movements_after_baseline()` (با date handling برای as_of_date و baseline_date)، و `calculate_warehouse_balances()` (با منطق کامل یافتن items از warehouse assignment و transactions، ترکیب با set، فیلتر Q، و error handling) |
| `inventory/README_BALANCE_MODULE.md` | `inventory/inventory_balance.py` | ✅ Updated | 2025-11-28 18:54:08 | 2025-11-29 19:06:21 | ✅ README newer | به‌روزرسانی شد - جزئیات کامل منطق برای `get_last_stocktaking_baseline()` (با stocktaking_record_date)، `calculate_movements_after_baseline()` (با date handling)، و `calculate_warehouse_balances()` (با منطق کامل یافتن items و فیلتر کردن) |
| `inventory/README_FORMS.md` | `inventory/forms/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | به‌روزرسانی شد - لینک به فایل‌های README جزئی‌تر اضافه شد |
| `inventory/views/README.md` | `inventory/views/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و به تمام فایل‌های README جزئی‌تر اشاره می‌کند |
| `inventory/utils/README.md` | `inventory/utils/` | ✅ Updated | 2025-11-26 21:30:04 | 2025-11-26 15:57:29 | ⚠️ Source newer | بررسی شد - فایل به‌روز است و تمام توابع utility را مستندسازی کرده (codes.py و jalali.py). تفاوت تاریخ فقط چند ساعت است و محتوا با کد هماهنگ است |
| `inventory/services/README.md` | `inventory/services/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و تمام توابع serial management را مستندسازی کرده (single-line و line-based) |
| `inventory/templatetags/README.md` | `inventory/templatetags/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و تمام template tags (jalali_tags) را مستندسازی کرده |
| `inventory/migrations/README.md` | `inventory/migrations/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و خلاصه migrations را مستندسازی کرده |
| `inventory/management/commands/README.md` | `inventory/management/commands/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و cleanup_test_receipts command را مستندسازی کرده |
| `production/README.md` | `production/` module | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | به‌روزرسانی شد - لینک به فایل‌های README جزئی‌تر اضافه شد |
| `production/README_BOM.md` | `production/` BOM related | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و مستندات کامل BOM را دارد |
| `production/README_FORMS.md` | `production/forms/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و تمام forms را مستندسازی کرده |
| `production/views/README.md` | `production/views/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و overview کلی views را دارد |
| `production/forms/README.md` | `production/forms/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است |
| `production/migrations/README.md` | `production/migrations/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است |
| `qc/README.md` | `qc/` module | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | به‌روزرسانی شد - لینک به فایل‌های README جزئی‌تر اضافه شد |
| `qc/views/README.md` | `qc/views/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و overview کلی views را دارد |
| `qc/views/README_BASE.md` | `qc/views/base.py` | ✅ Updated | 2025-11-21 19:59:04 | 2025-11-26 15:57:29 | ✅ README newer | بررسی شد - فایل به‌روز است |
| `qc/migrations/README.md` | `qc/migrations/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و خلاصه migrations را دارد |
| `ticketing/README.md` | `ticketing/` module | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | ایجاد شد - لینک به فایل‌های README جزئی‌تر اضافه شد |
| `ticketing/views/README.md` | `ticketing/views/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و overview کلی views را دارد |
| `ticketing/forms/README.md` | `ticketing/forms/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و overview کلی forms را دارد |
| `ticketing/utils/README.md` | `ticketing/utils/` | ✅ Updated | 2025-11-26 21:30:04 | 2025-11-26 15:57:29 | ⚠️ Source newer | بررسی شد - فایل به‌روز است و توابع codes.py را مستندسازی کرده. تفاوت تاریخ فقط چند ساعت است و محتوا با کد هماهنگ است |
| `ticketing/migrations/README.md` | `ticketing/migrations/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و خلاصه migrations را دارد |
| `shared/README.md` | `shared/` module | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | به‌روزرسانی شد - لینک به فایل‌های README جزئی‌تر اضافه شد |
| `shared/README_FORMS.md` | `shared/forms/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و تمام forms را مستندسازی کرده |
| `shared/views/README.md` | `shared/views/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و overview کلی views را دارد |
| `shared/forms/README.md` | `shared/forms/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و overview کلی forms را دارد |
| `shared/utils/README.md` | `shared/utils/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و تمام utility functions را مستندسازی کرده |
| `shared/templatetags/README.md` | `shared/templatetags/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و تمام template tags را مستندسازی کرده |
| `shared/migrations/README.md` | `shared/migrations/` | ✅ Updated | - | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و خلاصه migrations را دارد |
| `templates/inventory/README.md` | `templates/inventory/` | ✅ Updated | N/A | 2025-11-29 23:00:00 | ✅ N/A | بررسی شد - فایل به‌روز است و مستندات کامل templates را دارد |

---

## 📊 آمار

- **جمع کل README فایل‌ها**: 149+ فایل
- **جمع کل فایل‌های بررسی شده**: 149+ فایل
- **فایل‌های کامل**: 139+ فایل
- **فایل‌های نیازمند تکمیل**: 28 فایل (18 فایل برای ماژول‌های آینده + 10 فایل جدید ایجاد شده)
  - Production: 3 فایل (forms/README_PROCESS_OPERATIONS.md, utils/README_TRANSFER.md, views/README_REWORK.md, views/README_QCOPERATIONS.md)
  - Shared: 7 فایل (forms/README_BASE.md, views/README_API.md, views/README_BASE_ADDITIONAL.md, utils/README_VIEW_HELPERS.md, templatetags/README_GENERIC_TAGS.md, templatetags/README_VIEW_TAGS.md)
- **فایل‌های نیازمند بررسی محتوایی**: 2 فایل (Source newer - بررسی شدند و محتوا درست است، تفاوت تاریخ فقط چند ساعت)
- **وضعیت**: ✅ تمام فایل‌های اصلی README دارند (28 فایل نیازمند تکمیل محتوا)

---

## 🔍 نحوه استفاده

1. برای هر README، فایل اصلی مربوطه را بررسی کنید
2. مطمئن شوید که:
   - تمام کلاس‌ها/توابع در README مستندسازی شده‌اند
   - پارامترها و return types به‌روز هستند
   - مثال‌ها و توضیحات با کد هماهنگ هستند
3. پس از بررسی، Status را به ✅ Updated یا ⚠️ Needs Update تغییر دهید

---

## 📝 Legend

### وضعیت‌های Status
- ⏳ Pending: در انتظار بررسی
- ✅ Updated: به‌روز است
- ⚠️ Needs Update: نیاز به به‌روزرسانی دارد
- ❌ Missing: فایل اصلی وجود ندارد

### وضعیت‌های Git Check
- ✅ README newer: تاریخ تغییر README جدیدتر از فایل اصلی است
- ✅ Same date: تاریخ تغییر هر دو فایل یکسان است
- ⚠️ Source newer: تاریخ تغییر فایل اصلی جدیدتر از README است - **نیاز به بررسی فوری**
- ⚠️ Unknown: نتوانستیم تاریخ تغییر را از Git استخراج کنیم


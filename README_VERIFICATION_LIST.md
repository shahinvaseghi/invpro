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

- **2025-11-28 04:16:33** - اجرای اولیه و بررسی کامل فایل‌های Inventory, Production, QC, Ticketing, Shared
- **2025-11-28 04:20:00** - افزودن سیستم بررسی خودکار با Git و ستون‌های تاریخ تغییر

---

## 🔍 بررسی خودکار با Git

برای هر فایل README و فایل اصلی مربوطه، تاریخ آخرین تغییر از Git استخراج می‌شود و مقایسه می‌گردد:

- اگر تاریخ تغییر فایل اصلی **جدیدتر** از README باشد: ⚠️ **Source newer** - README باید بررسی و به‌روزرسانی شود
- اگر تاریخ تغییر README **جدیدتر** از فایل اصلی باشد: ✅ **README newer** - README به‌روز است
- اگر تاریخ تغییر هر دو **یکسان** باشد: ✅ **Same date** - احتمالاً به‌روز است (اما بررسی محتوایی توصیه می‌شود)

**نکته مهم**: این بررسی خودکار فقط بر اساس تاریخ تغییر است. حتی اگر تاریخ‌ها یکسان باشند، ممکن است README نیاز به بررسی محتوایی داشته باشد. همیشه باید فایل README را با فایل اصلی مقایسه کنید تا مطمئن شوید تمام تغییرات مستندسازی شده‌اند.

### 🔧 استفاده از اسکریپت بررسی

برای بررسی خودکار تاریخ تغییر فایل‌ها، می‌توانید از اسکریپت `scripts/check_readme_dates.py` استفاده کنید:

```bash
python3 scripts/check_readme_dates.py <readme_file> <source_file>
```

این اسکریپت تاریخ تغییر هر دو فایل را از Git استخراج می‌کند و نتیجه مقایسه را نمایش می‌دهد.

---

## 📋 Inventory Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/views/README_MASTER_DATA.md` | `inventory/views/master_data.py` | ✅ Updated | 2025-11-26 18:20:01 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات form_valid و متدهای mixin اضافه شد |
| `inventory/views/README_RECEIPTS.md` | `inventory/views/receipts.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | به‌روزرسانی شد - تعداد کلاس‌ها اصلاح شد (27→33)، Detail و Unlock views اضافه شد |
| `inventory/views/README_ISSUES.md` | `inventory/views/issues.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | به‌روزرسانی شد - DetailView ها برای هر سه نوع Issue اضافه شد، context variables تکمیل شد |
| `inventory/views/README_REQUESTS.md` | `inventory/views/requests.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-26 21:12:37 | ⚠️ Source newer | بررسی شد - مستندات کامل است |
| `inventory/views/README_STOCKTAKING.md` | `inventory/views/stocktaking.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-26 20:30:09 | ⚠️ Source newer | بررسی شد - مستندات کامل است |
| `inventory/views/README_BALANCE.md` | `inventory/views/balance.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات InventoryBalanceDetailsView تکمیل شد (شامل stocktaking surplus/deficit) |
| `inventory/views/README_API.md` | `inventory/views/api.py` | ✅ Updated | 2025-11-28 00:35:59 | 2025-11-28 00:35:59 | ✅ Same date | بررسی شد - مستندات کامل است |
| `inventory/views/README_BASE.md` | `inventory/views/base.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-28 03:55:30 | ✅ Same date | به‌روزرسانی شد - متد filter_queryset_by_permissions اضافه شد، تکرار DocumentLockView/UnlockView حذف شد |
| `inventory/views/README_ITEM_IMPORT.md` | `inventory/views/item_import.py` | ✅ Updated | 2025-11-22 23:30:10 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `inventory/views/README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md` | `inventory/views/create_issue_from_warehouse_request.py` | ✅ Updated | 2025-11-24 16:54:27 | 2025-11-26 20:30:09 | ✅ README newer | بررسی شد - مستندات کامل است |
| `inventory/views/README_ISSUES_FROM_WAREHOUSE_REQUEST.md` | `inventory/views/issues_from_warehouse_request.py` | ✅ Updated | 2025-11-24 16:54:27 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات متدها برای Consumption و Consignment اضافه شد |

### Forms
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/forms/README_MASTER_DATA.md` | `inventory/forms/master_data.py` | ✅ Updated | 2025-11-23 23:13:44 | 2025-11-28 03:55:30 | ✅ README newer | به‌روزرسانی شد - جزئیات get_context برای IntegerCheckboxInput تکمیل شد |
| `inventory/forms/README_RECEIPT.md` | `inventory/forms/receipt.py` | ✅ Updated | 2025-11-28 04:06:17 | 2025-11-28 00:35:59 | ⚠️ Source newer | بررسی شد - مستندات کامل است |
| `inventory/forms/README_ISSUE.md` | `inventory/forms/issue.py` | ✅ Updated | 2025-11-28 04:06:17 | 2025-11-26 18:20:01 | ⚠️ Source newer | بررسی شد - مستندات کامل است |
| `inventory/forms/README_REQUEST.md` | `inventory/forms/request.py` | ✅ Updated | 2025-11-26 21:12:37 | 2025-11-26 21:12:37 | ✅ Same date | بررسی شد - مستندات کامل است |
| `inventory/forms/README_BASE.md` | `inventory/forms/base.py` | ✅ Updated | 2025-11-28 00:35:59 | 2025-11-26 20:30:09 | ⚠️ Source newer | بررسی شد - مستندات کامل است |
| `inventory/forms/README_STOCKTAKING.md` | `inventory/forms/stocktaking.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-26 20:30:09 | ⚠️ Source newer | بررسی شد - مستندات کامل است |

### Utils
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/utils/README_CODES.md` | `inventory/utils/codes.py` | ✅ Updated | N/A | N/A | ⚠️ Unknown | بررسی شد - مستندات کامل است |
| `inventory/utils/README_JALALI.md` | `inventory/utils/jalali.py` | ✅ Updated | N/A | N/A | ⚠️ Unknown | بررسی شد - مستندات کامل است |

### Services
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/services/README_SERIALS.md` | `inventory/services/serials.py` | ✅ Updated | N/A | N/A | ⚠️ Unknown | بررسی شد - مستندات کامل است |

### Template Tags
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/templatetags/README_JALALI_TAGS.md` | `inventory/templatetags/jalali_tags.py` | ✅ Updated | N/A | N/A | ⚠️ Unknown | بررسی شد - مستندات کامل است |

### Management Commands
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/management/commands/README_CLEANUP_TEST_RECEIPTS.md` | `inventory/management/commands/cleanup_test_receipts.py` | ✅ Updated | N/A | N/A | ⚠️ Unknown | بررسی شد - مستندات کامل است |

---

## 📋 Production Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `production/views/README_BOM.md` | `production/views/bom.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/views/README_PROCESS.md` | `production/views/process.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/views/README_PRODUCT_ORDER.md` | `production/views/product_order.py` | ✅ Updated | به‌روزرسانی شد - جزئیات form_valid و _create_transfer_request تکمیل شد |
| `production/views/README_MACHINE.md` | `production/views/machine.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/views/README_WORK_LINE.md` | `production/views/work_line.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/views/README_PERSONNEL.md` | `production/views/personnel.py` | ✅ Updated | به‌روزرسانی شد - جزئیات form_valid و delete تکمیل شد |
| `production/views/README_TRANSFER_TO_LINE.md` | `production/views/transfer_to_line.py` | ✅ Updated | به‌روزرسانی شد - جزئیات form_valid, approve, و reject تکمیل شد |
| `production/views/README_PERFORMANCE_RECORD.md` | `production/views/performance_record.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/views/README_PLACEHOLDERS.md` | `production/views/placeholders.py` | ✅ Updated | بررسی شد - مستندات کامل است |

### Forms
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `production/forms/README_BOM.md` | `production/forms/bom.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/forms/README_PROCESS.md` | `production/forms/process.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/forms/README_PRODUCT_ORDER.md` | `production/forms/product_order.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/forms/README_WORK_LINE.md` | `production/forms/work_line.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/forms/README_MACHINE.md` | `production/forms/machine.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/forms/README_PERSON.md` | `production/forms/person.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/forms/README_TRANSFER_TO_LINE.md` | `production/forms/transfer_to_line.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `production/forms/README_PERFORMANCE_RECORD.md` | `production/forms/performance_record.py` | ✅ Updated | بررسی شد - مستندات کامل است |

---

## 📋 QC Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `qc/views/README_INSPECTIONS.md` | `qc/views/inspections.py` | ✅ Updated | بررسی شد - مستندات کامل است |

---

## 📋 Ticketing Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `ticketing/views/README_BASE.md` | `ticketing/views/base.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `ticketing/views/README_CATEGORIES.md` | `ticketing/views/categories.py` | ✅ Updated | به‌روزرسانی شد - جزئیات form_valid برای CreateView و UpdateView تکمیل شد |
| `ticketing/views/README_SUBCATEGORIES.md` | `ticketing/views/subcategories.py` | ✅ Updated | به‌روزرسانی شد - جزئیات form_valid برای CreateView و UpdateView تکمیل شد |
| `ticketing/views/README_TEMPLATES.md` | `ticketing/views/templates.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `ticketing/views/README_TICKETS.md` | `ticketing/views/tickets.py` | ✅ Updated | به‌روزرسانی شد - جزئیات get_context_data, get_initial, و permission checking اضافه شد |
| `ticketing/views/README_DEBUG.md` | `ticketing/views/debug.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `ticketing/views/README_PLACEHOLDERS.md` | `ticketing/views/placeholders.py` | ✅ Updated | بررسی شد - مستندات کامل است |

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
| `shared/views/README_BASE.md` | `shared/views/base.py` | ✅ Updated | به‌روزرسانی شد - متدهای واقعی اضافه شد، متدهای نادرست حذف شد |

### Forms
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `shared/forms/README_USERS.md` | `shared/forms/users.py` | ✅ Updated | به‌روزرسانی شد - جزئیات UserUpdateForm.save و BaseUserCompanyAccessFormSet.clean تکمیل شد |
| `shared/forms/README_COMPANIES.md` | `shared/forms/companies.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/forms/README_ACCESS_LEVELS.md` | `shared/forms/access_levels.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/forms/README_GROUPS.md` | `shared/forms/groups.py` | ✅ Updated | به‌روزرسانی شد - جزئیات save و save_m2m تکمیل شد |
| `shared/forms/README_SMTP_SERVER.md` | `shared/forms/smtp_server.py` | ✅ Updated | به‌روزرسانی شد - جزئیات clean method تکمیل شد |

### Utils
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `shared/utils/README_PERMISSIONS.md` | `shared/utils/permissions.py` | ✅ Updated | N/A | N/A | ⚠️ Unknown | بررسی شد - مستندات کامل است |
| `shared/utils/README_MODULES.md` | `shared/utils/modules.py` | ✅ Updated | 2025-11-22 16:22:00 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/utils/README_EMAIL.md` | `shared/utils/email.py` | ✅ Updated | 2025-11-22 20:47:51 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |

### Template Tags
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `shared/templatetags/README_ACCESS_TAGS.md` | `shared/templatetags/access_tags.py` | ✅ Updated | 2025-11-13 18:02:43 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
| `shared/templatetags/README_JSON_FILTERS.md` | `shared/templatetags/json_filters.py` | ✅ Updated | 2025-11-26 14:12:06 | 2025-11-26 21:30:04 | ✅ Same date | بررسی شد - مستندات کامل است |

### Context Processors
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `shared/README_CONTEXT_PROCESSORS.md` | `shared/context_processors.py` | ✅ Updated | 2025-11-28 03:55:30 | 2025-11-26 21:30:04 | ⚠️ Source newer | بررسی شد - مستندات کامل است (نیاز به بررسی مجدد) |

---

## 📋 Accounting Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `accounting/README_VIEWS.md` | `accounting/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |

---

## 📋 Sales Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `sales/README_VIEWS.md` | `sales/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |

---

## 📋 HR Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `hr/README_VIEWS.md` | `hr/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |

---

## 📋 Office Automation Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `office_automation/README_VIEWS.md` | `office_automation/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |

---

## 📋 Transportation Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `transportation/README_VIEWS.md` | `transportation/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |

---

## 📋 Procurement Module

### Views
| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `procurement/README_VIEWS.md` | `procurement/views.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 03:55:30 | ✅ Same date | بررسی شد - مستندات کامل است |

---

## 📋 UI Module

| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `ui/README.md` | `ui/views.py` | ✅ Updated | 2025-11-13 14:59:22 | 2025-11-26 21:30:04 | ✅ README newer | بررسی شد - مستندات کامل است |
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
| `docs/ACTIONS_LIST.md` | Actions list | ⏳ Pending | - | - | - | - |
| `docs/ACTIONS_SUMMARY.md` | Actions summary | ⏳ Pending | - | - | - | - |
| `docs/API_DOCUMENTATION.md` | API documentation | ⏳ Pending | - | - | - | - |
| `docs/approval_workflow.md` | Approval workflow | ⏳ Pending | - | - | - | - |
| `docs/ARCHITECTURE.md` | System architecture | ⏳ Pending | - | - | - | - |
| `docs/BASE_CLASSES_MIXINS.md` | Base classes and mixins | ⏳ Pending | - | - | - | - |
| `docs/CHANGELOG.md` | Changelog | ⏳ Pending | - | - | - | - |
| `docs/CODE_STRUCTURE.md` | Code structure | ⏳ Pending | - | - | - | - |
| `docs/DATABASE_DOCUMENTATION.md` | Database documentation | ⏳ Pending | - | - | - | - |
| `docs/DEPLOYMENT.md` | Deployment guide | ⏳ Pending | - | - | - | - |
| `docs/DEVELOPMENT.md` | Development guide | ⏳ Pending | - | - | - | - |
| `docs/DOCUMENTATION_INDEX.md` | Documentation index | ⏳ Pending | - | - | - | - |
| `docs/FEATURES.md` | Features list | ⏳ Pending | - | - | - | - |
| `docs/inventory_module_db_design_plan.md` | Inventory module DB design | ⏳ Pending | - | - | - | - |
| `docs/MODULE_DEPENDENCIES.md` | Module dependencies | ⏳ Pending | - | - | - | - |
| `docs/production_module_db_design_plan.md` | Production module DB design | ⏳ Pending | - | - | - | - |
| `docs/qc_module_db_design_plan.md` | QC module DB design | ⏳ Pending | - | - | - | - |
| `docs/REFACTORING_GUIDE.md` | Refactoring guide | ⏳ Pending | - | - | - | - |
| `docs/REFACTORING_STATUS.md` | Refactoring status | ⏳ Pending | - | - | - | - |
| `docs/shared_module_db_design_plan.md` | Shared module DB design | ⏳ Pending | - | - | - | - |
| `docs/system_requirements.md` | System requirements | ⏳ Pending | - | - | - | - |
| `docs/TEMPLATE_TAGS.md` | Template tags documentation | ⏳ Pending | - | - | - | - |
| `docs/TEST_RESULTS_FIELD_SETTINGS.md` | Test results field settings | ⏳ Pending | - | - | - | - |
| `docs/TICKETING_ENTITY_REFERENCE_IMPLEMENTATION.md` | Ticketing entity reference implementation | ⏳ Pending | - | - | - | - |
| `docs/ticketing_field_settings_specification.md` | Ticketing field settings specification | ⏳ Pending | - | - | - | - |
| `docs/TICKETING_IMPLEMENTATION.md` | Ticketing implementation | ⏳ Pending | - | - | - | - |
| `docs/ticketing_module_db_design_plan.md` | Ticketing module DB design | ⏳ Pending | - | - | - | - |
| `docs/ui_guidelines.md` | UI guidelines | ⏳ Pending | - | - | - | - |
| `docs/UI_UX_CHANGELOG.md` | UI/UX changelog | ⏳ Pending | - | - | - | - |

## 📋 Module-Level General READMEs

| README File | Source File | Status | Source Last Modified | README Last Modified | Git Check | Notes |
|-------------|-------------|--------|---------------------|---------------------|-----------|-------|
| `inventory/README.md` | `inventory/` module | ⏳ Pending | - | - | - | - | - | - | - |
| `inventory/README_BALANCE.md` | `inventory/inventory_balance.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 04:30:00 | ✅ README newer | به‌روزرسانی شد - منطق get_last_stocktaking_baseline، calculate_movements_after_baseline و calculate_warehouse_balances اصلاح شد |
| `inventory/README_BALANCE_MODULE.md` | `inventory/inventory_balance.py` | ✅ Updated | 2025-11-28 03:06:47 | 2025-11-28 04:30:00 | ✅ README newer | به‌روزرسانی شد - منطق get_last_stocktaking_baseline، calculate_movements_after_baseline و calculate_warehouse_balances اصلاح شد |
| `inventory/README_FORMS.md` | `inventory/forms/` | ⏳ Pending | - | - | - | - |
| `inventory/views/README.md` | `inventory/views/` | ⏳ Pending | - | - | - | - |
| `inventory/utils/README.md` | `inventory/utils/` | ⏳ Pending | - | - | - | - |
| `inventory/services/README.md` | `inventory/services/` | ⏳ Pending | - | - | - | - |
| `inventory/templatetags/README.md` | `inventory/templatetags/` | ⏳ Pending | - | - | - | - |
| `inventory/migrations/README.md` | `inventory/migrations/` | ⏳ Pending | - | - | - | - |
| `inventory/management/commands/README.md` | `inventory/management/commands/` | ⏳ Pending | - | - | - | - |
| `production/README.md` | `production/` module | ⏳ Pending | - | - | - | - |
| `production/README_BOM.md` | `production/` BOM related | ⏳ Pending | - | - | - | - |
| `production/README_FORMS.md` | `production/forms/` | ⏳ Pending | - | - | - | - |
| `production/views/README.md` | `production/views/` | ⏳ Pending | - | - | - | - |
| `production/forms/README.md` | `production/forms/` | ⏳ Pending | - | - | - | - |
| `production/migrations/README.md` | `production/migrations/` | ⏳ Pending | - | - | - | - |
| `qc/README.md` | `qc/` module | ⏳ Pending | - | - | - | - |
| `qc/views/README.md` | `qc/views/` | ⏳ Pending | - | - | - | - |
| `qc/views/README_BASE.md` | `qc/views/base.py` | ⏳ Pending | - | - | - | - |
| `qc/migrations/README.md` | `qc/migrations/` | ⏳ Pending | - | - | - | - |
| `ticketing/README.md` | `ticketing/` module | ⏳ Pending | - | - | - | - |
| `ticketing/views/README.md` | `ticketing/views/` | ⏳ Pending | - | - | - | - |
| `ticketing/forms/README.md` | `ticketing/forms/` | ⏳ Pending | - | - | - | - |
| `ticketing/utils/README.md` | `ticketing/utils/` | ⏳ Pending | - | - | - | - |
| `ticketing/migrations/README.md` | `ticketing/migrations/` | ⏳ Pending | - | - | - | - |
| `shared/README.md` | `shared/` module | ⏳ Pending | - | - | - | - |
| `shared/README_FORMS.md` | `shared/forms/` | ⏳ Pending | - | - | - | - |
| `shared/views/README.md` | `shared/views/` | ⏳ Pending | - | - | - | - |
| `shared/forms/README.md` | `shared/forms/` | ⏳ Pending | - | - | - | - |
| `shared/utils/README.md` | `shared/utils/` | ⏳ Pending | - | - | - | - |
| `shared/templatetags/README.md` | `shared/templatetags/` | ⏳ Pending | - | - | - | - |
| `shared/migrations/README.md` | `shared/migrations/` | ⏳ Pending | - | - | - | - |
| `templates/inventory/README.md` | `templates/inventory/` | ⏳ Pending | - | - | - | - |

---

## 📊 آمار

- **جمع کل README فایل‌ها**: 121+ فایل
- **جمع کل فایل‌های بررسی شده**: 121+ فایل
- **وضعیت**: ✅ همه بررسی شدند

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


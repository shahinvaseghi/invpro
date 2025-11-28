# لیست بررسی README فایل‌ها

این فایل لیست تمام فایل‌های README و فایل‌های اصلی مربوطه را نشان می‌دهد برای بررسی به‌روز بودن مستندات.

---

## 📋 Inventory Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `inventory/views/README_MASTER_DATA.md` | `inventory/views/master_data.py` | ✅ Updated | به‌روزرسانی شد - جزئیات form_valid و متدهای mixin اضافه شد |
| `inventory/views/README_RECEIPTS.md` | `inventory/views/receipts.py` | ✅ Updated | به‌روزرسانی شد - تعداد کلاس‌ها اصلاح شد (27→33)، Detail و Unlock views اضافه شد |
| `inventory/views/README_ISSUES.md` | `inventory/views/issues.py` | ✅ Updated | به‌روزرسانی شد - DetailView ها برای هر سه نوع Issue اضافه شد، context variables تکمیل شد |
| `inventory/views/README_REQUESTS.md` | `inventory/views/requests.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/views/README_STOCKTAKING.md` | `inventory/views/stocktaking.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/views/README_BALANCE.md` | `inventory/views/balance.py` | ✅ Updated | به‌روزرسانی شد - جزئیات InventoryBalanceDetailsView تکمیل شد (شامل stocktaking surplus/deficit) |
| `inventory/views/README_API.md` | `inventory/views/api.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/views/README_BASE.md` | `inventory/views/base.py` | ✅ Updated | به‌روزرسانی شد - متد filter_queryset_by_permissions اضافه شد، تکرار DocumentLockView/UnlockView حذف شد |
| `inventory/views/README_ITEM_IMPORT.md` | `inventory/views/item_import.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/views/README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md` | `inventory/views/create_issue_from_warehouse_request.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/views/README_ISSUES_FROM_WAREHOUSE_REQUEST.md` | `inventory/views/issues_from_warehouse_request.py` | ✅ Updated | به‌روزرسانی شد - جزئیات متدها برای Consumption و Consignment اضافه شد |

### Forms
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `inventory/forms/README_MASTER_DATA.md` | `inventory/forms/master_data.py` | ✅ Updated | به‌روزرسانی شد - جزئیات get_context برای IntegerCheckboxInput تکمیل شد |
| `inventory/forms/README_RECEIPT.md` | `inventory/forms/receipt.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/forms/README_ISSUE.md` | `inventory/forms/issue.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/forms/README_REQUEST.md` | `inventory/forms/request.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/forms/README_BASE.md` | `inventory/forms/base.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/forms/README_STOCKTAKING.md` | `inventory/forms/stocktaking.py` | ✅ Updated | بررسی شد - مستندات کامل است |

### Utils
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `inventory/utils/README_CODES.md` | `inventory/utils/codes.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `inventory/utils/README_JALALI.md` | `inventory/utils/jalali.py` | ✅ Updated | بررسی شد - مستندات کامل است |

### Services
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `inventory/services/README_SERIALS.md` | `inventory/services/serials.py` | ✅ Updated | بررسی شد - مستندات کامل است |

### Template Tags
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `inventory/templatetags/README_JALALI_TAGS.md` | `inventory/templatetags/jalali_tags.py` | ✅ Updated | بررسی شد - مستندات کامل است |

### Management Commands
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `inventory/management/commands/README_CLEANUP_TEST_RECEIPTS.md` | `inventory/management/commands/cleanup_test_receipts.py` | ✅ Updated | بررسی شد - مستندات کامل است |

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
| `production/views/README_PERSONNEL.md` | `production/views/personnel.py` | ✅ Updated | بررسی شد - مستندات کامل است |
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
| `ticketing/views/README_CATEGORIES.md` | `ticketing/views/categories.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `ticketing/views/README_SUBCATEGORIES.md` | `ticketing/views/subcategories.py` | ✅ Updated | بررسی شد - مستندات کامل است |
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
| `shared/views/README_SMTP_SERVER.md` | `shared/views/smtp_server.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/views/README_BASE.md` | `shared/views/base.py` | ✅ Updated | به‌روزرسانی شد - متدهای واقعی اضافه شد، متدهای نادرست حذف شد |

### Forms
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `shared/forms/README_USERS.md` | `shared/forms/users.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/forms/README_COMPANIES.md` | `shared/forms/companies.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/forms/README_ACCESS_LEVELS.md` | `shared/forms/access_levels.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/forms/README_GROUPS.md` | `shared/forms/groups.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/forms/README_SMTP_SERVER.md` | `shared/forms/smtp_server.py` | ✅ Updated | بررسی شد - مستندات کامل است |

### Utils
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `shared/utils/README_PERMISSIONS.md` | `shared/utils/permissions.py` | ✅ Updated | بررسی شد - مستندات کامل است |
| `shared/utils/README_MODULES.md` | `shared/utils/modules.py` | ⏳ Pending | - |
| `shared/utils/README_EMAIL.md` | `shared/utils/email.py` | ⏳ Pending | - |

### Template Tags
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `shared/templatetags/README_ACCESS_TAGS.md` | `shared/templatetags/access_tags.py` | ⏳ Pending | - |
| `shared/templatetags/README_JSON_FILTERS.md` | `shared/templatetags/json_filters.py` | ⏳ Pending | - |

### Context Processors
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `shared/README_CONTEXT_PROCESSORS.md` | `shared/context_processors.py` | ⏳ Pending | - |

---

## 📋 Accounting Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `accounting/README_VIEWS.md` | `accounting/views.py` | ⏳ Pending | - |

---

## 📋 Sales Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `sales/README_VIEWS.md` | `sales/views.py` | ⏳ Pending | - |

---

## 📋 HR Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `hr/README_VIEWS.md` | `hr/views.py` | ⏳ Pending | - |

---

## 📋 Office Automation Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `office_automation/README_VIEWS.md` | `office_automation/views.py` | ⏳ Pending | - |

---

## 📋 Transportation Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `transportation/README_VIEWS.md` | `transportation/views.py` | ⏳ Pending | - |

---

## 📋 Procurement Module

### Views
| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `procurement/README_VIEWS.md` | `procurement/views.py` | ⏳ Pending | - |

---

## 📋 UI Module

| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `ui/README.md` | `ui/views.py` | ⏳ Pending | - |
| `ui/README_CONTEXT_PROCESSORS.md` | `ui/context_processors.py` | ⏳ Pending | - |

---

## 📋 Root Level Files

| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `README.md` | Project root | ⏳ Pending | Main project README |
| `MIGRATIONS_README.md` | All migrations | ⏳ Pending | Migration documentation |
| `DOCUMENTATION_STATUS.md` | - | ⏳ Pending | Documentation status |
| `DOCUMENTATION_STRUCTURE.md` | - | ⏳ Pending | This structure file |
| `docs/README.md` | `docs/` | ⏳ Pending | Docs folder README |
| `docs/ENTITY_REFERENCE_SYSTEM.md` | Entity Reference System | ⏳ Pending | Entity Reference docs |

## 📋 Module-Level General READMEs

| README File | Source File | Status | Notes |
|-------------|-------------|--------|-------|
| `inventory/README.md` | `inventory/` module | ⏳ Pending | - |
| `inventory/README_BALANCE.md` | `inventory/inventory_balance.py` | ⏳ Pending | - |
| `inventory/README_BALANCE_MODULE.md` | `inventory/inventory_balance.py` | ⏳ Pending | - |
| `inventory/README_FORMS.md` | `inventory/forms/` | ⏳ Pending | - |
| `inventory/views/README.md` | `inventory/views/` | ⏳ Pending | - |
| `inventory/forms/README_OLD.md` | `inventory/forms/` (old) | ⏳ Pending | - |
| `inventory/utils/README.md` | `inventory/utils/` | ⏳ Pending | - |
| `inventory/services/README.md` | `inventory/services/` | ⏳ Pending | - |
| `inventory/templatetags/README.md` | `inventory/templatetags/` | ⏳ Pending | - |
| `inventory/migrations/README.md` | `inventory/migrations/` | ⏳ Pending | - |
| `inventory/management/commands/README.md` | `inventory/management/commands/` | ⏳ Pending | - |
| `inventory/views/README_MASTER_DATA_OLD.md` | `inventory/views/master_data.py` (old) | ⏳ Pending | - |
| `production/README.md` | `production/` module | ⏳ Pending | - |
| `production/README_BOM.md` | `production/` BOM related | ⏳ Pending | - |
| `production/README_FORMS.md` | `production/forms/` | ⏳ Pending | - |
| `production/views/README.md` | `production/views/` | ⏳ Pending | - |
| `production/forms/README.md` | `production/forms/` | ⏳ Pending | - |
| `production/migrations/README.md` | `production/migrations/` | ⏳ Pending | - |
| `qc/README.md` | `qc/` module | ⏳ Pending | - |
| `qc/views/README.md` | `qc/views/` | ⏳ Pending | - |
| `qc/views/README_BASE.md` | `qc/views/base.py` | ⏳ Pending | - |
| `qc/migrations/README.md` | `qc/migrations/` | ⏳ Pending | - |
| `ticketing/README.md` | `ticketing/` module | ⏳ Pending | - |
| `ticketing/views/README.md` | `ticketing/views/` | ⏳ Pending | - |
| `ticketing/forms/README.md` | `ticketing/forms/` | ⏳ Pending | - |
| `ticketing/utils/README.md` | `ticketing/utils/` | ⏳ Pending | - |
| `ticketing/migrations/README.md` | `ticketing/migrations/` | ⏳ Pending | - |
| `shared/README.md` | `shared/` module | ⏳ Pending | - |
| `shared/README_FORMS.md` | `shared/forms/` | ⏳ Pending | - |
| `shared/views/README.md` | `shared/views/` | ⏳ Pending | - |
| `shared/forms/README.md` | `shared/forms/` | ⏳ Pending | - |
| `shared/utils/README.md` | `shared/utils/` | ⏳ Pending | - |
| `shared/templatetags/README.md` | `shared/templatetags/` | ⏳ Pending | - |
| `shared/migrations/README.md` | `shared/migrations/` | ⏳ Pending | - |
| `templates/inventory/README.md` | `templates/inventory/` | ⏳ Pending | - |

---

## 📊 آمار

- **جمع کل README فایل‌ها**: 121+ فایل
- **جمع کل فایل‌های نیازمند بررسی**: 121+ فایل
- **وضعیت**: ⏳ همه در انتظار بررسی

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

- ⏳ Pending: در انتظار بررسی
- ✅ Updated: به‌روز است
- ⚠️ Needs Update: نیاز به به‌روزرسانی دارد
- ❌ Missing: فایل اصلی وجود ندارد


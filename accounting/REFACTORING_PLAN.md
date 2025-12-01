# برنامه Refactoring ساختار Accounting Module

## وضعیت فعلی

### انجام شده:
- ✅ `views/` با فایل‌های جداگانه (gl_accounts.py, sub_accounts.py, tafsili_accounts.py, ...)
- ✅ `forms/` با فایل‌های جداگانه
- ✅ مدل‌های اصلی پیاده‌سازی شده
- ✅ DRF نصب و پیکربندی شده

### نیاز به Refactoring:
- ❌ `models.py` (یک فایل بزرگ ~1040 خط)
- ❌ `urls.py` (یک فایل بزرگ ~175 خط)
- ❌ `serializers/` (هنوز وجود ندارد)

---

## ساختار پیشنهادی

### 1. Models Structure

```
accounting/models/
├── __init__.py          # Base classes + imports
├── base.py              # AccountingBaseModel, FiscalYearMixin, etc.
├── fiscal_years.py      # FiscalYear, Period
├── accounts.py          # Account, SubAccountGLAccountRelation, TafsiliSubAccountRelation, TafsiliHierarchy
├── documents.py         # AccountingDocument, AccountingDocumentLine
├── attachments.py       # DocumentAttachment
├── balances.py          # AccountBalance
├── treasury.py          # (آینده: Treasury models)
├── parties.py           # (آینده: Party models)
├── tax.py               # (آینده: Tax models)
└── payroll.py           # (آینده: Payroll models)
```

### 2. URLs Structure

```
accounting/urls/
├── __init__.py          # Main urlpatterns (include all)
├── accounts.py          # GL, Sub, Tafsili accounts URLs
├── documents.py         # Document CRUD URLs
├── treasury.py          # Treasury URLs
├── parties.py           # Party URLs
├── reports.py           # Report URLs
├── tax.py               # Tax URLs
├── payroll.py           # Payroll URLs
├── attachments.py       # Attachment URLs
└── utils.py             # Utilities URLs
```

### 3. Serializers Structure

```
accounting/serializers/
├── __init__.py
├── accounts.py          # Account serializers
├── documents.py         # Document serializers
├── treasury.py          # Treasury serializers
├── parties.py           # Party serializers
├── tax.py               # Tax serializers
└── payroll.py           # Payroll serializers
```

---

## مراحل Refactoring

### مرحله 1: ایجاد ساختار پوشه‌ها
- [x] ایجاد پوشه‌های models/, urls/, serializers/

### مرحله 2: تقسیم Models
- [ ] ایجاد models/base.py (Base classes)
- [ ] ایجاد models/fiscal_years.py
- [ ] ایجاد models/accounts.py
- [ ] ایجاد models/documents.py
- [ ] ایجاد models/attachments.py
- [ ] ایجاد models/balances.py
- [ ] به‌روزرسانی models/__init__.py
- [ ] حذف models.py (یا تبدیل به wrapper)

### مرحله 3: تقسیم URLs
- [ ] ایجاد urls/accounts.py
- [ ] ایجاد urls/documents.py
- [ ] ایجاد urls/treasury.py
- [ ] ایجاد urls/parties.py
- [ ] ایجاد urls/reports.py
- [ ] ایجاد urls/tax.py
- [ ] ایجاد urls/payroll.py
- [ ] ایجاد urls/attachments.py
- [ ] ایجاد urls/utils.py
- [ ] به‌روزرسانی urls/__init__.py
- [ ] حذف urls.py (یا تبدیل به wrapper)

### مرحله 4: ایجاد Serializers
- [ ] ایجاد serializers/__init__.py
- [ ] ایجاد serializers/accounts.py
- [ ] ایجاد serializers/documents.py
- [ ] ایجاد serializers/treasury.py
- [ ] ایجاد serializers/parties.py
- [ ] ایجاد serializers/tax.py
- [ ] ایجاد serializers/payroll.py

### مرحله 5: تست و بررسی
- [ ] بررسی migrationها
- [ ] تست importها
- [ ] تست URLها
- [ ] تست views

---

## نکات مهم

1. **Migration Compatibility**: باید مطمئن شویم که migrationها همچنان کار می‌کنند
2. **Import Paths**: باید تمام importها را به‌روزرسانی کنیم
3. **Admin Registration**: باید admin.py را بررسی کنیم
4. **Tests**: باید تست‌ها را به‌روزرسانی کنیم

---

## تصمیم‌گیری

آیا می‌خواهید که این refactoring را انجام دهم؟

**گزینه 1**: انجام کامل refactoring (خطرناک - ممکن است migrationها را بشکند)
**گزینه 2**: فقط ایجاد ساختار و serializers (ایمن‌تر)
**گزینه 3**: فقط serializers (خیلی ایمن)


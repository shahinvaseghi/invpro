# accounting/forms/ - Forms Package (Complete Documentation)

**هدف**: Forms package برای ماژول accounting

این package شامل **3 فایل**:
- `fiscal_years.py`: Forms برای مدیریت سال‌های مالی
- `periods.py`: Forms برای مدیریت دوره‌های حسابداری
- `accounts.py`: Forms برای مدیریت حساب‌ها (Chart of Accounts)

---

## ساختار Package

```
accounting/forms/
├── __init__.py          # Export همه forms
├── fiscal_years.py      # FiscalYearForm
├── periods.py           # PeriodForm
└── accounts.py          # AccountForm
```

---

## فایل‌های README

برای جزئیات کامل هر فایل، به README های زیر مراجعه کنید:
- `accounting/README_FORMS.md`: مستندات کامل تمام forms

---

## استفاده در پروژه

### Import Forms

```python
# از package
from accounting.forms import FiscalYearForm, PeriodForm, AccountForm

# از فایل اصلی (backward compatibility)
from accounting.forms import FiscalYearForm, PeriodForm, AccountForm
```

---

**Last Updated**: 2025-12-01


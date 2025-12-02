# accounting/forms/ - Forms Package (Complete Documentation)

**هدف**: Forms package برای ماژول accounting

این package شامل **11 فایل** است که به دسته‌های زیر تقسیم می‌شوند:
- `fiscal_years.py`: Forms برای مدیریت سال‌های مالی
- `periods.py`: Forms برای مدیریت دوره‌های حسابداری
- `accounts.py`: Forms برای مدیریت حساب‌ها (Chart of Accounts)
- `parties.py`: Forms برای مدیریت طرف حساب‌ها و حساب‌های طرف حساب
- `cost_centers.py`: Forms برای مدیریت مراکز هزینه
- `income_expense_categories.py`: Forms برای مدیریت دسته‌بندی‌های درآمد و هزینه
- `document_attachments.py`: Forms برای مدیریت پیوست‌های اسناد
- `gl_accounts.py`: Forms برای مدیریت حساب‌های کل
- `sub_accounts.py`: Forms برای مدیریت حساب‌های معین
- `tafsili_accounts.py`: Forms برای مدیریت حساب‌های تفصیلی
- `tafsili_hierarchy.py`: Forms برای مدیریت تفصیلی چند سطحی

---

## ساختار Package

```
accounting/forms/
├── __init__.py                    # Export همه forms
├── fiscal_years.py                # FiscalYearForm
├── periods.py                     # PeriodForm
├── accounts.py                    # AccountForm
├── parties.py                     # PartyForm, PartyAccountForm
├── cost_centers.py                # CostCenterForm
├── income_expense_categories.py   # IncomeExpenseCategoryForm
├── document_attachments.py        # DocumentAttachmentForm
├── gl_accounts.py                 # GLAccountForm
├── sub_accounts.py                # SubAccountForm
├── tafsili_accounts.py            # TafsiliAccountForm
└── tafsili_hierarchy.py           # TafsiliHierarchyForm
```

---

## فایل‌های README

برای جزئیات کامل هر فایل، به README های زیر مراجعه کنید:
- `accounting/README_FORMS.md`: مستندات کامل forms پایه (FiscalYear, Period, Account)
- `accounting/forms/README_PARTIES.md`: مستندات کامل PartyForm و PartyAccountForm
- `accounting/forms/README_COST_CENTERS.md`: مستندات کامل CostCenterForm
- `accounting/forms/README_INCOME_EXPENSE_CATEGORIES.md`: مستندات کامل IncomeExpenseCategoryForm

---

## استفاده در پروژه

### Import Forms

```python
# از package
from accounting.forms import (
    FiscalYearForm, PeriodForm, AccountForm,
    PartyForm, PartyAccountForm,
    CostCenterForm, IncomeExpenseCategoryForm
)

# از فایل اصلی (backward compatibility)
from accounting.forms import (
    FiscalYearForm, PeriodForm, AccountForm,
    PartyForm, PartyAccountForm,
    CostCenterForm, IncomeExpenseCategoryForm
)
```

---

**Last Updated**: 2025-12-02


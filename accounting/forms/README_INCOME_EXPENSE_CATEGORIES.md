# accounting/forms/income_expense_categories.py - Income/Expense Category Forms (Complete Documentation)

**هدف**: Forms برای مدیریت دسته‌بندی‌های درآمد و هزینه

این فایل شامل **1 form class** است:
- `IncomeExpenseCategoryForm`: فرم ایجاد/ویرایش دسته‌بندی درآمد/هزینه

---

## وابستگی‌ها

- `django.forms`: `ModelForm`
- `django.utils.translation`: `gettext_lazy as _`
- `typing`: `Optional`
- `accounting.models`: `IncomeExpenseCategory`
- `shared.models`: `Company`

---

## Forms

### `IncomeExpenseCategoryForm(forms.ModelForm)`

**توضیح**: فرم برای ایجاد/ویرایش دسته‌بندی درآمد/هزینه

**Model**: `IncomeExpenseCategory`

**Fields**:
- `category_type` (CharField): نوع دسته‌بندی
  - Widget: `Select`
  - Label: `'نوع دسته‌بندی'`
  - Required: `True`
  - Choices: `'income'` (درآمد), `'expense'` (هزینه)
  - Help Text: `'نوع دسته‌بندی: درآمد یا هزینه'`

- `category_name` (CharField): نام دسته‌بندی (فارسی)
  - Widget: `TextInput`
  - Label: `'نام دسته‌بندی'`
  - Required: `True`

- `category_name_en` (CharField): نام دسته‌بندی (انگلیسی)
  - Widget: `TextInput`
  - Label: `'نام دسته‌بندی (انگلیسی)'`
  - Required: `False`

- `description` (TextField): توضیحات
  - Widget: `Textarea` (rows=4)
  - Label: `'توضیحات'`
  - Required: `False`

- `is_enabled` (PositiveSmallIntegerField): وضعیت فعال/غیرفعال
  - Widget: `Select`
  - Label: `'وضعیت'`
  - Required: `False`

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: مقداردهی اولیه فرم با company_id

**پارامترهای ورودی**:
- `*args`: Positional arguments
- `company_id` (Optional[int]): شناسه شرکت فعال (از session)
- `**kwargs`: Keyword arguments

**منطق**:
1. فراخوانی `super().__init__()`
2. ذخیره `company_id` در `self.company_id`
3. اگر `company_id` وجود دارد:
   - دریافت شرکت از دیتابیس
   - تنظیم `self.instance.company` برای instance جدید
   - در صورت عدم وجود Company، خطا را نادیده می‌گیرد

---

## استفاده در پروژه

### Import Form

```python
from accounting.forms import IncomeExpenseCategoryForm
```

### استفاده در View ها

```python
# در CreateView
form = IncomeExpenseCategoryForm(company_id=request.session.get('active_company_id'))

# در UpdateView
form = IncomeExpenseCategoryForm(instance=category, company_id=request.session.get('active_company_id'))
```

---

## نکات مهم

1. **Company Scoping**: Company برای instance های جدید به صورت خودکار تنظیم می‌شود
2. **Code Auto-Generation**: کد دسته‌بندی به صورت خودکار در مدل `IncomeExpenseCategory.save()` تولید می‌شود (با فیلتر `category_type`)
3. **Category Type**: نوع دسته‌بندی (درآمد یا هزینه) باید انتخاب شود
4. **Unique Constraints**: نام و کد دسته‌بندی باید در ترکیب با `company` و `category_type` یکتا باشد

---

**Last Updated**: 2025-12-02


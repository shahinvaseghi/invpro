# راهنمای Refactoring - Refactoring Guide

این مستند راهنمای کامل برای refactoring فایل‌های بزرگ پروژه است و برای تیم توسعه جدید طراحی شده است.

**آخرین به‌روزرسانی**: 2025-11-21

---

## 📚 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [اصول Refactoring](#اصول-refactoring)
3. [ساختار Package-Based](#ساختار-package-based)
4. [مراحل Refactoring](#مراحل-refactoring)
5. [Best Practices](#best-practices)
6. [نمونه‌های عملی](#نمونه‌های-عملی)
7. [Troubleshooting](#troubleshooting)

---

## مقدمه

### چرا Refactoring؟

فایل‌های بزرگ (بیش از 1000 خط) مشکلات زیر را ایجاد می‌کنند:
- **خوانایی پایین**: پیدا کردن کد مورد نظر سخت است
- **Maintenance مشکل**: تغییرات در یک بخش ممکن است بخش‌های دیگر را تحت تأثیر قرار دهد
- **Collaboration مشکل**: چند developer نمی‌توانند همزمان روی یک فایل کار کنند
- **Testing مشکل**: تست کردن فایل‌های بزرگ سخت است

### هدف Refactoring

- تقسیم فایل‌های بزرگ به فایل‌های کوچکتر و منطقی
- بهبود خوانایی و maintainability
- افزودن Type Hints برای clarity بیشتر
- حفظ backward compatibility

---

## اصول Refactoring

### 1. Single Responsibility Principle

هر فایل باید یک مسئولیت مشخص داشته باشد:

✅ **خوب**:
```python
# inventory/views/master_data.py
class ItemTypeListView(ListView):
    """List view for item types."""
    pass

class ItemTypeCreateView(CreateView):
    """Create view for item types."""
    pass
```

❌ **بد**:
```python
# inventory/views.py (4000+ خط)
# همه views در یک فایل!
```

### 2. Logical Grouping

فایل‌ها را بر اساس functionality گروه‌بندی کنید:

- **Master Data**: Item, Type, Category, Subcategory, Warehouse, Supplier
- **Documents**: Receipt, Issue, Stocktaking
- **Requests**: Purchase Request, Warehouse Request
- **API**: تمام API endpoints

### 3. Backward Compatibility

همیشه backward compatibility را حفظ کنید:

```python
# inventory/views.py (فایل اصلی)
"""
This file is kept for backward compatibility.
All views have been refactored into inventory.views package.
"""
from inventory.views import (
    ItemTypeListView,
    ItemCreateView,
    # ... all other views
)
```

---

## ساختار Package-Based

### ساختار پیشنهادی

```
module_name/
├── views/              # یا forms/
│   ├── __init__.py     # Export همه classes
│   ├── base.py         # Base classes و mixins
│   ├── module1.py      # Views/Forms برای module1
│   ├── module2.py      # Views/Forms برای module2
│   └── ...
└── views.py            # Backward compatibility
```

### مثال: inventory/views/

```
inventory/views/
├── __init__.py          # Export همه views
├── base.py              # Base classes (InventoryBaseView, mixins)
├── api.py               # API endpoints
├── master_data.py       # Master data CRUD
├── requests.py          # Purchase و Warehouse requests
├── receipts.py          # Receipt documents
├── issues.py            # Issue documents
├── stocktaking.py       # Stocktaking documents
└── balance.py           # Inventory balance
```

---

## مراحل Refactoring

### مرحله 1: تحلیل و برنامه‌ریزی

1. **خواندن فایل اصلی**: کل فایل را بخوانید و درک کنید
2. **شناسایی گروه‌ها**: views/forms را بر اساس functionality گروه‌بندی کنید
3. **تعیین ساختار**: نام فایل‌های جدید را تعیین کنید
4. **بررسی dependencies**: import ها و dependencies را شناسایی کنید

### مرحله 2: ایجاد ساختار Package

```bash
# ایجاد دایرکتوری
mkdir -p module_name/views

# ایجاد __init__.py
touch module_name/views/__init__.py
```

### مرحله 3: انتقال کد

1. **ایجاد فایل‌های جدید**: هر گروه را در فایل جداگانه قرار دهید
2. **اضافه کردن Type Hints**: به تمام functions و methods
3. **اضافه کردن docstrings**: برای تمام classes و functions
4. **اصلاح imports**: از absolute imports استفاده کنید

### مرحله 4: ایجاد __init__.py

```python
"""
Views package for module_name.
"""
__all__ = []

# Import views
from module_name.views.module1 import (
    View1,
    View2,
)

from module_name.views.module2 import (
    View3,
    View4,
)

__all__ = [
    'View1',
    'View2',
    'View3',
    'View4',
]
```

### مرحله 5: Backward Compatibility

```python
# module_name/views.py (فایل اصلی)
"""
Views for module_name.

This file is kept for backward compatibility.
All views have been refactored into module_name.views package.
"""
from module_name.views import (
    View1,
    View2,
    View3,
    View4,
)

__all__ = [
    'View1',
    'View2',
    'View3',
    'View4',
]
```

### مرحله 6: تست

1. **تست Import ها**: مطمئن شوید همه imports کار می‌کنند
2. **تست URL Patterns**: مطمئن شوید همه URLs کار می‌کنند
3. **تست Views**: مطمئن شوید همه views قابل استفاده هستند
4. **تست Backward Compatibility**: مطمئن شوید import paths قدیمی کار می‌کنند
5. **Django System Check**: `python manage.py check`
6. **Linter Check**: `flake8` یا linter دیگر

---

## Best Practices

### 1. Type Hints

✅ **همیشه Type Hints اضافه کنید**:

```python
from typing import Dict, Any, Optional

def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    """Add context data."""
    context = super().get_context_data(**kwargs)
    return context
```

### 2. Docstrings

✅ **همیشه docstrings اضافه کنید**:

```python
class ItemTypeListView(ListView):
    """
    List view for item types.
    
    This view displays all item types in the system with pagination.
    Filters by active company.
    """
    pass
```

### 3. Import Organization

✅ **ترتیب صحیح imports**:

```python
# 1. Standard library
from typing import Dict, Any, Optional

# 2. Django
from django.contrib import messages
from django.views.generic import ListView

# 3. Third-party
# (none in this project)

# 4. Local
from inventory.models import Item
from shared.mixins import FeaturePermissionRequiredMixin
```

### 4. Naming Conventions

✅ **استفاده از نام‌های واضح**:

- **Files**: `snake_case.py` (e.g., `master_data.py`, `receipts.py`)
- **Classes**: `PascalCase` (e.g., `ItemTypeListView`)
- **Functions**: `snake_case` (e.g., `get_context_data`)
- **Variables**: `snake_case` (e.g., `active_company_id`)

---

## نمونه‌های عملی

### نمونه 1: Refactoring Views

#### قبل:
```python
# inventory/views.py (4000+ خط)
class ItemTypeListView(ListView):
    pass

class ItemCreateView(CreateView):
    pass

# ... 100+ view classes
```

#### بعد:
```python
# inventory/views/master_data.py
class ItemTypeListView(ListView):
    pass

class ItemCreateView(CreateView):
    pass

# inventory/views/__init__.py
from inventory.views.master_data import (
    ItemTypeListView,
    ItemCreateView,
)
```

### نمونه 2: Refactoring Forms

#### قبل:
```python
# production/forms.py (700+ خط)
class PersonForm(forms.ModelForm):
    pass

class MachineForm(forms.ModelForm):
    pass

# ... 5+ form classes
```

#### بعد:
```python
# production/forms/person.py
class PersonForm(forms.ModelForm):
    pass

# production/forms/machine.py
class MachineForm(forms.ModelForm):
    pass

# production/forms/__init__.py
from production.forms.person import PersonForm
from production.forms.machine import MachineForm
```

---

## Troubleshooting

### مشکل 1: Import Error

**خطا**: `ModuleNotFoundError: No module named 'module_name.views.submodule'`

**راه حل**:
1. مطمئن شوید `__init__.py` در دایرکتوری وجود دارد
2. مطمئن شوید imports در `__init__.py` درست هستند
3. مطمئن شوید از absolute imports استفاده می‌کنید

### مشکل 2: Circular Import

**خطا**: `ImportError: cannot import name 'X' from partially initialized module`

**راه حل**:
1. imports را به داخل functions منتقل کنید
2. از `TYPE_CHECKING` برای type hints استفاده کنید
3. ساختار imports را بازبینی کنید

### مشکل 3: URL Pattern Error

**خطا**: `NoReverseMatch: Reverse for 'module:view_name' not found`

**راه حل**:
1. مطمئن شوید view در `__init__.py` export شده است
2. مطمئن شوید URL pattern در `urls.py` درست است
3. مطمئن شوید app_name در `urls.py` درست است

---

## چک‌لیست Refactoring

قبل از اعلام completion، این موارد را بررسی کنید:

- [ ] همه فایل‌های جدید ایجاد شده‌اند
- [ ] `__init__.py` همه classes را export می‌کند
- [ ] فایل اصلی برای backward compatibility حفظ شده است
- [ ] Type Hints به تمام functions اضافه شده است
- [ ] Docstrings به تمام classes اضافه شده است
- [ ] همه imports کار می‌کنند
- [ ] همه URL patterns کار می‌کنند
- [ ] Django system check بدون خطا است
- [ ] Linter بدون خطا است
- [ ] Backward compatibility تست شده است

---

## مستندات مرتبط

- `docs/REFACTORING_STATUS.md` - وضعیت refactoring
- `docs/CODE_STRUCTURE.md` - ساختار کد
- `docs/DEVELOPMENT.md` - راهنمای توسعه

---

**توجه**: این مستند به صورت منظم به‌روزرسانی می‌شود. لطفاً قبل از شروع refactoring جدید، این فایل را بررسی کنید.


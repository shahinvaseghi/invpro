# ساختار کد پروژه - Code Structure Guide

این مستند راهنمای کامل ساختار کد پروژه است و برای تیم توسعه جدید طراحی شده است.

**آخرین به‌روزرسانی**: 2025-11-21

---

## 📁 ساختار کلی پروژه

```
invproj/
├── config/                 # تنظیمات Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/              # ماژول انبار
│   ├── models.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── api.py
│   │   ├── master_data.py
│   │   ├── requests.py
│   │   ├── receipts.py
│   │   ├── issues.py
│   │   ├── stocktaking.py
│   │   └── balance.py
│   ├── forms.py
│   ├── urls.py
│   └── ...
├── production/             # ماژول تولید
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── ...
├── qc/                     # ماژول کنترل کیفیت
│   ├── models.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── inspections.py
│   └── ...
├── shared/                 # ماژول مشترک
│   ├── models.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── auth.py
│   │   ├── companies.py
│   │   ├── company_units.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   └── access_levels.py
│   └── ...
└── docs/                   # مستندات
```

---

## 🏗️ معماری Views

### 1. ساختار Package-Based

پس از refactoring، views به صورت package-based سازماندهی شده‌اند:

#### ✅ Refactored Modules

**inventory/views/**
- `base.py`: Base classes و mixins مشترک
- `api.py`: API endpoints برای AJAX requests
- `master_data.py`: CRUD views برای master data (Item, Type, Category, etc.)
- `requests.py`: Purchase و Warehouse request views
- `receipts.py`: Receipt document views (Temporary, Permanent, Consignment)
- `issues.py`: Issue document views (Permanent, Consumption, Consignment)
- `stocktaking.py`: Stocktaking views (Deficit, Surplus, Record)
- `balance.py`: Inventory balance views و API

**shared/views/**
- `__init__.py`: Package exports
- `base.py`: Base mixins (UserAccessFormsetMixin, AccessLevelPermissionMixin)
- `auth.py`: Authentication views (custom_login, set_active_company)
- `companies.py`: Company CRUD views
- `company_units.py`: CompanyUnit CRUD views
- `users.py`: User CRUD views
- `groups.py`: Group CRUD views
- `access_levels.py`: AccessLevel CRUD views

**qc/views/**
- `__init__.py`: Package exports
- `base.py`: Base view (QCBaseView)
- `inspections.py`: Temporary receipt QC inspection views

**production/forms/**
- `__init__.py`: Package exports
- `person.py`: Personnel forms
- `machine.py`: Machine forms
- `bom.py`: BOM forms
- `work_line.py`: WorkLine forms
- `process.py`: Process forms

**production/views/**
- `__init__.py`: Package exports
- `personnel.py`: Personnel CRUD views
- `machine.py`: Machine CRUD views
- `bom.py`: BOM CRUD views
- `work_line.py`: WorkLine CRUD views
- `process.py`: Process CRUD views
- `placeholders.py`: Placeholder views

#### ✅ Refactored Modules

**production/forms/** (6 فایل)
- `__init__.py`: Package exports
- `person.py`: Personnel forms
- `machine.py`: Machine forms
- `bom.py`: BOM forms (BOMForm, BOMMaterialLineForm, BOMMaterialLineFormSet)
- `work_line.py`: WorkLine forms
- `process.py`: Process forms

**production/views/** (7 فایل)
- `__init__.py`: Package exports
- `personnel.py`: Personnel CRUD views
- `machine.py`: Machine CRUD views
- `bom.py`: BOM CRUD views
- `work_line.py`: WorkLine CRUD views
- `process.py`: Process CRUD views
- `placeholders.py`: Placeholder views (TransferToLineRequest, PerformanceRecord)

#### ⏳ Pending Refactoring

**inventory/forms.py** (4,026 خط)
- نیاز به تقسیم به: `base.py`, `master_data.py`, `receipt.py`, `issue.py`, `stocktaking.py`, `request.py`

---

## 📦 ساختار Models

### 1. Base Mixins

تمام models از mixins مشترک استفاده می‌کنند:

```python
# shared/models.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class ActivatableModel(models.Model):
    is_enabled = models.PositiveSmallIntegerField(default=1)
    
class CompanyScopedModel(models.Model):
    company = models.ForeignKey(Company, ...)
    
class LockableModel(models.Model):
    is_locked = models.PositiveSmallIntegerField(default=0)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(User, ...)
```

### 2. Model Organization

- **inventory/models.py**: تمام models مربوط به انبار
- **production/models.py**: تمام models مربوط به تولید
- **qc/models.py**: تمام models مربوط به کنترل کیفیت
- **shared/models.py**: models مشترک (Company, User, etc.)

---

## 📝 ساختار Forms

### 1. Form Organization

**inventory/forms.py** (4026 خط - نیاز به refactoring)
- Master data forms
- Receipt forms
- Issue forms
- Stocktaking forms
- Request forms

**production/forms.py** (719 خط - نیاز به refactoring)
- BOM forms
- Process forms
- WorkLine forms

**shared/forms.py**
- Company forms
- User forms
- Access level forms

### 2. Form Patterns

#### Base Form Classes
```python
class BaseForm(forms.ModelForm):
    """Base form with common functionality."""
    pass
```

#### Formset Patterns
```python
# استفاده از inlineformset_factory برای multi-line forms
ReceiptLineFormSet = inlineformset_factory(
    ReceiptPermanent,
    ReceiptLine,
    form=ReceiptLineForm,
    extra=1,
    can_delete=True
)
```

---

## 🔌 ساختار API Endpoints

### 1. API Organization

تمام API endpoints در `inventory/views/api.py` قرار دارند:

```python
# API endpoints برای AJAX requests
@login_required
def get_item_units(request):
    """Get allowed units for an item."""
    pass

@login_required
def get_filtered_categories(request):
    """Get categories filtered by type."""
    pass
```

### 2. API Patterns

- تمام API endpoints با `@login_required` محافظت می‌شوند
- Response format: JSON
- Error handling: JSON error responses
- Type Hints: کامل برای تمام parameters و return types

---

## 🎨 ساختار Templates

### 1. Template Organization

```
templates/
├── base.html              # Base template
├── login.html            # Login page
├── inventory/            # Inventory templates
│   ├── item_form.html
│   ├── receipt_form.html
│   └── ...
├── production/           # Production templates
│   ├── bom_form.html
│   └── ...
└── shared/               # Shared templates
    ├── company_form.html
    └── ...
```

### 2. Template Patterns

- استفاده از `{% extends %}` برای inheritance
- استفاده از `{% include %}` برای reusable components
- استفاده از `{% block %}` برای customization
- RTL support برای فارسی

---

## 🔐 ساختار Permissions

### 1. Permission System

```python
# shared/permissions.py
FEATURE_PERMISSION_MAP = {
    'inventory.items': FeaturePermission(
        code='inventory.items',
        label='Items',
        actions=[VIEW_OWN, VIEW_ALL, CREATE, EDIT_OWN, ...]
    ),
    ...
}
```

### 2. Permission Mixins

```python
class FeaturePermissionRequiredMixin:
    """Mixin to check feature permissions."""
    feature_code = None
    required_action = None
```

---

## 🧪 ساختار Tests

### 1. Test Organization

```
inventory/tests/
├── __init__.py
├── test_models.py        # Model tests
├── test_views.py         # View tests (در حال توسعه)
└── test_forms.py         # Form tests (در حال توسعه)
```

### 2. Test Patterns

```python
class ItemModelTest(TestCase):
    """Tests for Item model."""
    
    def setUp(self):
        """Set up test data."""
        pass
    
    def test_item_creation(self):
        """Test item creation."""
        pass
```

---

## 📚 Naming Conventions

### 1. File Naming

- **Views**: `snake_case.py` (e.g., `master_data.py`, `receipts.py`)
- **Models**: `models.py` (در هر ماژول)
- **Forms**: `forms.py` (در هر ماژول)
- **URLs**: `urls.py` (در هر ماژول)

### 2. Class Naming

- **Views**: `PascalCase` + `View` suffix (e.g., `ItemListView`, `ReceiptCreateView`)
- **Models**: `PascalCase` (e.g., `Item`, `ReceiptTemporary`)
- **Forms**: `PascalCase` + `Form` suffix (e.g., `ItemForm`, `ReceiptLineForm`)

### 3. Variable Naming

- **Variables**: `snake_case` (e.g., `item_code`, `receipt_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_LENGTH`, `DEFAULT_VALUE`)

---

## 🔄 Import Patterns

### 1. Recommended Imports

```python
# از package exports استفاده کنید
from inventory.views import ItemListView
from shared.views import CompanyListView
from qc.views import TemporaryReceiptQCListView

# یا مستقیماً از submodule
from inventory.views.master_data import ItemListView
from shared.views.companies import CompanyListView
```

### 2. Import Organization

```python
# 1. Standard library imports
from typing import Dict, Any, Optional
from datetime import datetime

# 2. Django imports
from django.contrib import messages
from django.views.generic import ListView

# 3. Third-party imports
# (none in this project)

# 4. Local application imports
from inventory.models import Item
from shared.mixins import FeaturePermissionRequiredMixin
```

---

## 🎯 Best Practices

### 1. Code Organization

✅ **انجام دهید**:
- فایل‌ها را بر اساس functionality تقسیم کنید
- از package-based structure استفاده کنید
- Type Hints به تمام functions اضافه کنید
- Docstrings برای تمام classes و functions

❌ **انجام ندهید**:
- فایل‌های خیلی بزرگ (بیش از 1000 خط)
- Import های circular
- Duplicate code

### 2. Type Hints

✅ **انجام دهید**:
```python
def get_item(self, item_id: int) -> Optional[Item]:
    """Get item by ID."""
    pass
```

❌ **انجام ندهید**:
```python
def get_item(self, item_id):
    pass
```

### 3. Documentation

✅ **انجام دهید**:
```python
class ItemListView(ListView):
    """
    List view for items.
    
    This view displays all items in the system with pagination.
    """
    pass
```

---

## 📖 مستندات مرتبط

- `docs/REFACTORING_STATUS.md` - وضعیت refactoring
- `docs/ARCHITECTURE.md` - معماری کلی
- `docs/DEVELOPMENT.md` - راهنمای توسعه
- `docs/API_DOCUMENTATION.md` - مستندات API

---

**توجه**: این مستند به صورت منظم به‌روزرسانی می‌شود. لطفاً قبل از شروع کار جدید، این فایل را بررسی کنید.


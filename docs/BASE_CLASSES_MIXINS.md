# Base Classes and Mixins Documentation

This document provides comprehensive documentation for all base classes and mixins used across the invproj platform.

## Table of Contents

1. [Overview](#1-overview)
2. [Inventory Module Base Classes](#2-inventory-module-base-classes)
3. [Shared Module Base Classes](#3-shared-module-base-classes)
4. [Ticketing Module Base Classes](#4-ticketing-module-base-classes)
5. [QC Module Base Classes](#5-qc-module-base-classes)
6. [Usage Examples](#6-usage-examples)

---

## 1. Overview

Base classes and mixins provide reusable functionality that can be inherited by views, forms, and models. They follow Django's class-based view patterns and promote code reuse.

**Key Benefits**:
- DRY (Don't Repeat Yourself) principle
- Consistent behavior across modules
- Easy to extend and customize
- Centralized common logic

---

## 2. Inventory Module Base Classes

**Location**: `inventory/views/base.py`

### 2.1 `InventoryBaseView`

**Type**: `LoginRequiredMixin` subclass

**Purpose**: Base view with common context and company filtering for all inventory views.

**Features**:
- Automatic company filtering via `get_queryset()`
- Adds `active_module = 'inventory'` to context
- Helper method for delete permission checks

**Methods**:

#### `get_queryset()`
```python
def get_queryset(self):
    """Filter queryset by active company."""
    queryset = super().get_queryset()
    company_id = self.request.session.get('active_company_id')
    if company_id and hasattr(queryset.model, 'company'):
        queryset = queryset.filter(company_id=company_id)
    return queryset
```

**Usage**:
```python
class ItemListView(InventoryBaseView, ListView):
    model = Item
    # Automatically filters by active company
```

#### `get_context_data(**kwargs)`
```python
def get_context_data(self, **kwargs) -> Dict[str, Any]:
    """Add common context data."""
    context = super().get_context_data(**kwargs)
    context['active_module'] = 'inventory'
    return context
```

#### `add_delete_permissions_to_context(context, feature_code)`
```python
def add_delete_permissions_to_context(self, context: Dict[str, Any], feature_code: str) -> Dict[str, Any]:
    """Helper method to add delete permission checks to context."""
    # Adds 'can_delete_own' and 'can_delete_other' to context
    # Superuser can always delete
```

**Usage**:
```python
class ReceiptListView(InventoryBaseView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_delete_permissions_to_context(
            context, 
            'inventory.receipts.permanent'
        )
        return context
```

---

### 2.2 `DocumentLockProtectedMixin`

**Purpose**: Prevents modifying locked inventory documents.

**Features**:
- Blocks HTTP methods on locked documents
- Optional owner check (only creator can edit)
- Customizable error messages and redirect URLs

**Attributes**:
- `lock_redirect_url_name` (str): URL name to redirect to when document is locked
- `lock_error_message` (str): Error message for locked documents (default: Persian message)
- `owner_field` (str): Field name for document owner (default: `'created_by'`)
- `owner_error_message` (str): Error message for owner mismatch
- `protected_methods` (tuple): HTTP methods to protect (default: `('get', 'post', 'put', 'patch', 'delete')`)

**How It Works**:
1. Intercepts `dispatch()` method
2. Checks if document `is_locked == 1`
3. Checks if user is owner (if `owner_field` is set)
4. Redirects with error message if checks fail

**Usage**:
```python
class ReceiptUpdateView(DocumentLockProtectedMixin, UpdateView):
    model = ReceiptPermanent
    lock_redirect_url_name = 'inventory:receipt_permanent_list'
    
    # Automatically blocks editing if is_locked=1
    # Only creator can edit (if owner_field='created_by')
```

**Customization**:
```python
class CustomUpdateView(DocumentLockProtectedMixin, UpdateView):
    lock_redirect_url_name = 'custom:list'
    lock_error_message = 'Custom lock message'
    owner_field = None  # Disable owner check
    protected_methods = ('post', 'put', 'patch')  # Only protect write methods
```

---

### 2.3 `DocumentLockView`

**Type**: `LoginRequiredMixin, View`

**Purpose**: Generic view to lock inventory documents.

**Features**:
- Sets `is_locked = 1` on document
- Updates `locked_at` and `locked_by` fields
- Hooks for before/after lock actions

**Attributes**:
- `model`: Model class to lock (required)
- `success_url_name`: URL name to redirect to after locking (required)
- `success_message`: Success message (default: Persian message)
- `already_locked_message`: Message if document already locked
- `lock_field`: Field name for lock status (default: `'is_locked'`)

**Methods**:

#### `before_lock(obj, request)`
```python
def before_lock(self, obj, request) -> bool:
    """Hook executed before locking. Return False to cancel lock."""
    return True
```

**Usage**:
```python
class ReceiptLockView(DocumentLockView):
    model = ReceiptPermanent
    success_url_name = 'inventory:receipt_permanent_list'
    
    def before_lock(self, obj, request):
        # Validate that receipt has lines
        if not obj.lines.exists():
            messages.error(request, 'Receipt must have at least one line')
            return False
        return True
```

#### `after_lock(obj, request)`
```python
def after_lock(self, obj, request) -> None:
    """Hook for subclasses to perform extra actions after locking."""
    return None
```

**Usage**:
```python
class ReceiptLockView(DocumentLockView):
    def after_lock(self, obj, request):
        # Generate serials when receipt is locked
        from inventory.services.serials import generate_receipt_line_serials
        for line in obj.lines.all():
            generate_receipt_line_serials(line, user=request.user)
```

**Complete Example**:
```python
class ReceiptPermanentLockView(DocumentLockView):
    model = ReceiptPermanent
    success_url_name = 'inventory:receipt_permanent_list'
    
    def before_lock(self, obj, request):
        # Check if receipt has lines
        if not obj.lines.exists():
            messages.error(request, 'رسید باید حداقل یک ردیف داشته باشد')
            return False
        return True
    
    def after_lock(self, obj, request):
        # Generate serials for all lines
        from inventory.services.serials import generate_receipt_line_serials
        for line in obj.lines.all():
            if line.item and line.item.has_lot_tracking == 1:
                generate_receipt_line_serials(line, user=request.user)
```

---

### 2.4 `LineFormsetMixin`

**Purpose**: Handles line formset creation and saving for multi-line documents.

**Features**:
- Automatic formset building from request data
- Line formset saving with document association
- Serial assignment handling for issue lines

**Attributes**:
- `formset_class`: Formset class to use (must be set by subclass)
- `formset_prefix`: Prefix for formset fields (default: `'lines'`)

**Methods**:

#### `build_line_formset(data, instance, company_id)`
```python
def build_line_formset(self, data=None, instance=None, company_id: Optional[int] = None):
    """Build line formset for the document."""
    # Automatically determines company_id from instance or session
    # Returns formset instance
```

#### `get_line_formset(data)`
```python
def get_line_formset(self, data=None):
    """Get line formset for current request."""
    return self.build_line_formset(data=data)
```

#### `get_context_data(**kwargs)`
```python
def get_context_data(self, **kwargs) -> Dict[str, Any]:
    """Add line formset to context."""
    # Adds 'lines_formset' to context
    # Uses POST data if request method is POST
```

#### `_save_line_formset(formset)`
```python
def _save_line_formset(self, formset) -> None:
    """Save line formset instances."""
    # Saves valid forms
    # Deletes forms marked for deletion
    # Handles serial assignment for issue lines
```

**Usage**:
```python
class ReceiptCreateView(LineFormsetMixin, CreateView):
    model = ReceiptPermanent
    formset_class = ReceiptPermanentLineFormSet
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Save lines after document is created
        self._save_line_formset(self.get_context_data()['lines_formset'])
        return response
```

**Template Usage**:
```django
<form method="post">
  {{ form.as_p }}
  
  {{ lines_formset.management_form }}
  {% for line_form in lines_formset %}
    <div class="line-form">
      {{ line_form.as_p }}
      {% if line_form.DELETE %}
        {{ line_form.DELETE }}
      {% endif %}
    </div>
  {% endfor %}
  
  <button type="submit">Save</button>
</form>
```

---

### 2.5 `ItemUnitFormsetMixin`

**Purpose**: Handles item unit formset creation and saving.

**Features**:
- Automatic unit formset building
- Unit code generation
- Item-warehouse relationship syncing

**Attributes**:
- `formset_prefix`: Prefix for formset fields (default: `'units'`)

**Methods**:

#### `build_unit_formset(data, instance, company_id)`
```python
def build_unit_formset(self, data=None, instance=None, company_id: Optional[int] = None):
    """Build unit formset for item."""
    # Returns ItemUnitFormSet instance
```

#### `_save_unit_formset(formset)`
```python
def _save_unit_formset(self, formset) -> None:
    """Save unit formset instances."""
    # Saves valid units
    # Generates codes for new units
    # Deletes removed units
```

#### `_sync_item_warehouses(item, warehouses, user)`
```python
def _sync_item_warehouses(self, item, warehouses, user) -> None:
    """Sync item-warehouse relationships."""
    # Creates ItemWarehouse records
    # Sets primary warehouse (first in list)
    # Removes warehouses not in list
```

**Usage**:
```python
class ItemCreateView(ItemUnitFormsetMixin, CreateView):
    model = Item
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Save units
        self._save_unit_formset(self.get_context_data()['units_formset'])
        # Sync warehouses
        warehouses = self._get_ordered_warehouses(form)
        self._sync_item_warehouses(self.object, warehouses, self.request.user)
        return response
```

---

## 3. Shared Module Base Classes

**Location**: `shared/views/base.py`

### 3.1 `UserAccessFormsetMixin`

**Purpose**: Handles user company access formset in user create/update views.

**Features**:
- Automatic formset building
- Primary access selection
- Access level assignment

**Usage**:
```python
class UserCreateView(UserAccessFormsetMixin, CreateView):
    model = User
    form_class = UserCreateForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Save company accesses
        self._save_access_formset(self.get_context_data()['access_formset'])
        return response
```

---

### 3.2 `AccessLevelPermissionMixin`

**Purpose**: Handles access level permission matrix in access level create/update views.

**Features**:
- Permission matrix rendering
- Bulk permission selection
- Permission saving

**Usage**:
```python
class AccessLevelCreateView(AccessLevelPermissionMixin, CreateView):
    model = AccessLevel
    form_class = AccessLevelForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Save permissions
        self._save_permissions(self.object, self.request.POST)
        return response
```

---

## 4. Ticketing Module Base Classes

**Location**: `ticketing/views/base.py`

### 4.1 `TicketingBaseView`

**Type**: `LoginRequiredMixin` subclass

**Purpose**: Base view for ticketing module with company filtering.

**Features**:
- Automatic company filtering
- Adds `active_module = 'ticketing'` to context

**Usage**:
```python
class TicketListView(TicketingBaseView, ListView):
    model = Ticket
```

---

### 4.2 `TicketLockProtectedMixin`

**Purpose**: Prevents modifying locked tickets.

**Similar to**: `DocumentLockProtectedMixin` but for tickets

**Usage**:
```python
class TicketUpdateView(TicketLockProtectedMixin, UpdateView):
    model = Ticket
```

---

## 5. QC Module Base Classes

**Location**: `qc/views/base.py`

### 5.1 `QCBaseView`

**Type**: `LoginRequiredMixin` subclass

**Purpose**: Base view for QC module with company filtering.

**Features**:
- Automatic company filtering
- Adds `active_module = 'qc'` to context

**Usage**:
```python
class InspectionListView(QCBaseView, ListView):
    model = ReceiptInspection
```

---

## 6. Usage Examples

### 6.1 Complete View Example

```python
from inventory.views.base import (
    InventoryBaseView,
    DocumentLockProtectedMixin,
    LineFormsetMixin
)
from django.views.generic import CreateView, UpdateView
from inventory.models import ReceiptPermanent
from inventory.forms import ReceiptPermanentForm, ReceiptPermanentLineFormSet

class ReceiptCreateView(LineFormsetMixin, InventoryBaseView, CreateView):
    model = ReceiptPermanent
    form_class = ReceiptPermanentForm
    formset_class = ReceiptPermanentLineFormSet
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Save lines after document is created
        self._save_line_formset(self.get_context_data()['lines_formset'])
        messages.success(self.request, 'رسید با موفقیت ایجاد شد')
        return response

class ReceiptUpdateView(
    LineFormsetMixin,
    DocumentLockProtectedMixin,
    InventoryBaseView,
    UpdateView
):
    model = ReceiptPermanent
    form_class = ReceiptPermanentForm
    formset_class = ReceiptPermanentLineFormSet
    lock_redirect_url_name = 'inventory:receipt_permanent_list'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Save lines
        self._save_line_formset(self.get_context_data()['lines_formset'])
        messages.success(self.request, 'رسید با موفقیت ویرایش شد')
        return response
```

### 6.2 Custom Lock View

```python
from inventory.views.base import DocumentLockView
from inventory.services.serials import generate_receipt_line_serials

class ReceiptPermanentLockView(DocumentLockView):
    model = ReceiptPermanent
    success_url_name = 'inventory:receipt_permanent_list'
    
    def before_lock(self, obj, request):
        # Validate receipt has lines
        if not obj.lines.exists():
            messages.error(request, 'رسید باید حداقل یک ردیف داشته باشد')
            return False
        return True
    
    def after_lock(self, obj, request):
        # Generate serials for all lines
        for line in obj.lines.all():
            if line.item and line.item.has_lot_tracking == 1:
                generate_receipt_line_serials(line, user=request.user)
```

### 6.3 Permission-Aware List View

```python
from inventory.views.base import InventoryBaseView
from django.views.generic import ListView

class ReceiptListView(InventoryBaseView, ListView):
    model = ReceiptPermanent
    template_name = 'inventory/receipt_permanent_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add delete permissions
        context = self.add_delete_permissions_to_context(
            context,
            'inventory.receipts.permanent'
        )
        return context
```

---

## 7. Best Practices

1. **Always inherit base view first**: `InventoryBaseView` should be first in MRO
2. **Use mixins for cross-cutting concerns**: Lock protection, formset handling, etc.
3. **Override hooks, don't replace methods**: Use `before_lock`, `after_lock` instead of overriding `post`
4. **Set required attributes**: `formset_class`, `lock_redirect_url_name`, etc.
5. **Test mixin combinations**: Some mixins may conflict, test thoroughly

---

## 8. Related Files

- `inventory/views/base.py`: Inventory base classes and mixins
- `shared/views/base.py`: Shared base classes and mixins
- `ticketing/views/base.py`: Ticketing base classes
- `qc/views/base.py`: QC base classes
- `inventory/README.md`: Inventory module documentation
- `shared/README.md`: Shared module documentation

---

**Last Updated**: 2025-11-21


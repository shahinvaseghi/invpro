# Shared Module Forms Documentation

## Overview
This document describes the forms used in the shared module for managing companies and personnel.

## Form Classes

### 1. CompanyForm
**Purpose:** Create and edit company records

**Model:** `Company`

**Fields:**
- `public_code` (3 digits) - Unique company code
- `legal_name` - Official registered name
- `display_name` - Short display name (Persian)
- `display_name_en` - Short display name (English)
- `registration_number` - Company registration number
- `tax_id` - Tax identification number
- `phone_number` - Main phone number
- `email` - Company email
- `website` - Company website URL
- `address` - Full address
- `city` - City name
- `state` - State/Province
- `country` - 3-letter country code (e.g., IRN)
- `is_enabled` - Active/Inactive status

**Validation:**
- Code must be exactly 3 digits
- Legal name is required
- Email must be valid format
- Website must be valid URL
- Country code must be 3 characters

**Special Features:**
- Automatically creates `UserCompanyAccess` for creator
- Auto-populates `created_by` and `edited_by`

**Example:**
```python
form = CompanyForm(data={
    'public_code': '001',
    'legal_name': 'شرکت نمونه ایران',
    'display_name': 'نمونه ایران',
    'tax_id': '1234567890',
    'city': 'تهران',
    'country': 'IRN',
    'is_enabled': 1
})
```

---

**Note**: `PersonForm` has been moved to the Production module. See `production/README_FORMS.md` for documentation.

---

## Form Features

### Auto-populated Fields
The following fields are set automatically by views:
- `created_by` - From request.user
- `edited_by` - From request.user
- `created_at` - Auto timestamp
- `updated_at` - Auto timestamp

### CSS Classes
All form fields use consistent styling:
```python
'class': 'form-control'  # Standard input
'class': 'form-check-input'  # Checkbox
```

---

## Usage in Views

### Company Create
```python
class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'shared/company_form.html'
    success_url = reverse_lazy('shared:companies')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Auto-create UserCompanyAccess for creator
        UserCompanyAccess.objects.create(
            user=self.request.user,
            company=self.object,
            access_level_id=1,  # ADMIN
            is_primary=1,
            is_enabled=1
        )
        
        messages.success(self.request, _('Company created successfully.'))
        return response
```

### Person Create
```python
class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = 'shared/person_form.html'
    success_url = reverse_lazy('shared:personnel')
    
    def form_valid(self, form):
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Person created successfully.'))
        return super().form_valid(form)
```

---

## Templates

### Company Form
`templates/shared/company_form.html` - Dedicated template with sections:
1. Basic Information (code, names, status)
2. Registration & Tax (registration number, tax ID)
3. Contact Information (phone, email, website, address)

### Person Form
`templates/shared/person_form.html` - Dedicated template with sections:
1. Basic Information (code, names, IDs, username checkbox)
2. Contact Information (phone, mobile, email, description, notes)

Both templates include:
- Real-time validation
- Error display
- Success/error messages
- Breadcrumb navigation
- Save/Cancel buttons
- Responsive layout

---

## Internationalization

All labels, help text, and error messages support Persian/English:

```python
labels = {
    'public_code': _('Code'),
    'legal_name': _('Legal Name'),
    'display_name': _('Display Name'),
}
```

---

### 3. AccessLevelForm
**Purpose:** Create and edit access level roles with permission matrix

**Model:** `AccessLevel`

**Fields:**
- `code` (max 30 chars) - Unique role code (e.g., "inventory_manager")
- `name` (max 120 chars) - Human-readable role name
- `description` - Detailed description of role responsibilities
- `is_enabled` - Active/Inactive status
- `is_global` - Global role flag (if 1, role can span multiple companies)

**Permission Matrix:**
The form renders a permission matrix table based on `FEATURE_PERMISSION_MAP`:
- Each row represents a feature (e.g., "Companies", "Item Types", "Permanent Receipts")
- View Scope column: Radio buttons (None, Own, All) for view permissions
- Actions column: Checkboxes for each action (Create, Edit Own, Delete Own, Lock Own, Lock Other, Unlock Own, Unlock Other, Approve, Reject, Cancel)
- **Quick Action Buttons**:
  - Per-row buttons: "Select All" and "Deselect All" for each feature row
  - Global buttons: "Select All" and "Deselect All" for entire permission matrix
  - JavaScript-based bulk selection/deselection functionality

**JavaScript Features:**
- `selectAllRow(featureId)`: Selects "All" radio and checks all checkboxes for a feature row
- `deselectAllRow(featureId)`: Selects "None" radio and unchecks all checkboxes for a feature row
- `selectAllGlobal()`: Applies selectAllRow to all features
- `deselectAllGlobal()`: Applies deselectAllRow to all features

**Template:** `templates/shared/access_level_form.html`
- Permission matrix table with feature rows
- Quick action buttons in table header and each row
- JavaScript handlers for bulk operations

**Usage:**
```python
class AccessLevelCreateView(FeaturePermissionRequiredMixin, AccessLevelPermissionMixin, CreateView):
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'shared/access_level_form.html'
    success_url = reverse_lazy('shared:access_levels')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feature_permissions'] = self._prepare_feature_context()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self._save_permissions(form)
        return response
```

**Permission Saving:**
- Permissions stored in `AccessLevelPermission` model
- View scope stored in `metadata.actions.view_scope` (none/own/all)
- Individual actions stored in `metadata.actions` dictionary
- Legacy fields (`can_view`, `can_create`, `can_edit`, `can_delete`, `can_approve`) maintained for backward compatibility

---

---

## Security Considerations

### Company Access Control
When a new company is created:
1. Creator automatically gets ADMIN access
2. `UserCompanyAccess` record is created
3. Company becomes visible in creator's company list
4. Company becomes selectable in header dropdown

---

## Common Patterns

### Required Fields Indicator
Fields marked with `*` are required:
```html
<label for="{{ field.id_for_label }}">
  {{ field.label }}
  {% if field.field.required %}*{% endif %}
</label>
```

### Error Display
```html
{% if field.errors %}
  <span class="error">{{ field.errors.0 }}</span>
{% endif %}
```

### Success Messages
```python
messages.success(self.request, _('Company created successfully.'))
messages.success(self.request, _('Company updated successfully.'))
```

---

## Future Enhancements

1. Implement digital signature for companies
2. Add multi-step wizard for company registration
3. Add role-based field visibility
4. Implement document attachments (contracts, IDs)
5. Add company logo upload
6. Implement company hierarchy (parent/child companies)


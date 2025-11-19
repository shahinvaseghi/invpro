# Production Module Forms Documentation

## Overview
This document describes the forms used in the production module for managing personnel and machines.

## Form Classes

### 1. PersonForm
**Purpose:** Create and edit personnel records

**Model:** `Person`

**Fields:**
- `first_name` - First name (Persian)
- `last_name` - Last name (Persian)
- `first_name_en` - First name (English)
- `last_name_en` - Last name (English)
- `national_id` - National identification number
- `personnel_code` - Employee/Personnel code
- `username` - System username
- `phone_number` - Phone number
- `mobile_number` - Mobile number
- `email` - Email address
- `description` - Brief description
- `notes` - Detailed notes
- `is_enabled` - Active/Inactive status
- `company_units` - Multiple company units assignment (Many-to-Many)

**Auto-Generated Fields:**
- `public_code` (8 digits) - Automatically generated sequential code per company. Not user-editable. Generated on save using `generate_sequential_code()`.

**Special Field: `use_personnel_code_as_username`**
- Checkbox field (not saved to database)
- When checked: username automatically syncs with personnel_code
- When unchecked: user can enter custom username
- JavaScript automatically enables/disables username field

**Validation:**
```python
def clean(self):
    cleaned_data = super().clean()
    use_personnel_code = cleaned_data.get('use_personnel_code_as_username')
    personnel_code = cleaned_data.get('personnel_code')
    username = cleaned_data.get('username')
    
    if use_personnel_code:
        if not personnel_code:
            raise forms.ValidationError(_('Personnel Code is required when using it as username.'))
        cleaned_data['username'] = personnel_code
    else:
        if not username:
            raise forms.ValidationError(_('Username is required when not using personnel code.'))
    
    # Ensure selected units belong to the same company
    if self.company_id:
        units = cleaned_data.get('company_units')
        if units and units.filter(~Q(company_id=self.company_id)).exists():
            raise forms.ValidationError(_('Selected units must belong to the active company.'))
    
    return cleaned_data
```

**Dynamic Behavior:**
```javascript
// When checkbox is checked:
- username field becomes read-only
- username field background turns gray
- username syncs with personnel_code changes

// When checkbox is unchecked:
- username field becomes editable
- user can enter custom username
```

**Usage in Views:**
```python
class PersonCreateView(FeaturePermissionRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

---

### 2. MachineForm
**Purpose:** Create and edit machine/equipment records

**Model:** `Machine`

**Fields:**
- `name` - Machine name (Persian)
- `name_en` - Machine name (English)
- `machine_type` - Machine type classification (CNC, lathe, milling, assembly, packaging, etc.)
- `work_center` - Assigned work center (optional)
- `manufacturer` - Manufacturer name
- `model_number` - Manufacturer model number
- `serial_number` - Machine serial number
- `purchase_date` - Date machine was purchased
- `installation_date` - Date machine was installed
- `capacity_specs` - Technical specifications (JSON field)
- `maintenance_schedule` - Maintenance intervals and requirements (JSON field)
- `last_maintenance_date` - Date of last maintenance
- `next_maintenance_date` - Scheduled next maintenance date
- `status` - Machine status (operational, maintenance, idle, broken, retired)
- `description` - Short description
- `notes` - Operational notes
- `is_enabled` - Active/Inactive status

**Auto-Generated Fields:**
- `public_code` (10 digits) - Automatically generated sequential code per company. Not user-editable. Generated on save using `generate_sequential_code()`.

**Validation:**
- Code is automatically generated and guaranteed to be unique per company
- Name must be unique per company
- Serial number must be unique (if provided)
- Work center must belong to the active company

**Special Features:**
- Work center dropdown filtered by active company
- Status choices: operational, maintenance, idle, broken, retired
- JSON fields for flexible capacity specs and maintenance schedule storage

**Usage in Views:**
```python
class MachineCreateView(FeaturePermissionRequiredMixin, CreateView):
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

---

## Form Features

### Auto-populated Fields
The following fields are set automatically by views or models:
- `company_id` - From active session company
- `public_code` - Auto-generated sequential code (Person: 8 digits, Machine: 10 digits)
- `created_by` - From request.user
- `edited_by` - From request.user
- `created_at` - Auto timestamp
- `updated_at` - Auto timestamp

**Code Generation:**
- Codes are generated using `inventory.utils.codes.generate_sequential_code()`
- Generation happens in model's `save()` method before database insert
- Codes are scoped per company (each company has its own sequence starting from 1)
- Users cannot see or edit the code field in forms

### CSS Classes
All form fields use consistent styling:
```python
'class': 'form-control'  # Standard input
'class': 'form-check-input'  # Checkbox
```

### Company Scoping
- All forms filter related fields (work centers, company units) by the active company
- Forms require `company_id` parameter to properly filter dropdowns
- Validation ensures cross-company assignments are prevented

---

## Internationalization

All form labels and help text are translatable using Django's i18n framework:
- Labels use `_()` for translation
- Help text uses `_()` for translation
- Error messages are translatable

---

## Error Handling

Forms provide comprehensive error handling:
- Field-level validation errors displayed inline
- Form-level validation errors displayed at the top
- JavaScript validation for username sync feature
- Server-side validation for data integrity

---

## Security Considerations

- All forms use CSRF protection
- Access control enforced via `FeaturePermissionRequiredMixin`
- Company scoping prevents cross-company data access
- Input validation prevents SQL injection and XSS attacks


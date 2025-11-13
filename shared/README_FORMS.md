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

### 2. PersonForm
**Purpose:** Create and edit personnel records

**Model:** `Person`

**Fields:**
- `public_code` (8 digits) - Unique person code
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

---

## Form Features

### Auto-populated Fields
The following fields are set automatically by views:
- `company_id` - From active session company (Person only)
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
    'first_name': _('First Name'),
    'use_personnel_code_as_username': _('Use Personnel Code as Username'),
}

help_text = _('If checked, username will be same as personnel code')
```

---

## JavaScript Integration

### Username Sync Feature
Located in `templates/shared/person_form.html`:

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const checkbox = document.getElementById('use_personnel_code');
  const personnelCodeField = document.getElementById('personnel_code_field');
  const usernameField = document.getElementById('username_field');
  
  function syncUsername() {
    if (checkbox && checkbox.checked) {
      usernameField.value = personnelCodeField.value;
      usernameField.readOnly = true;
      usernameField.style.backgroundColor = '#f3f4f6';
    } else {
      usernameField.readOnly = false;
      usernameField.style.backgroundColor = '';
    }
  }
  
  checkbox.addEventListener('change', syncUsername);
  personnelCodeField.addEventListener('input', syncUsername);
});
```

---

## Security Considerations

### Company Access Control
When a new company is created:
1. Creator automatically gets ADMIN access
2. `UserCompanyAccess` record is created
3. Company becomes visible in creator's company list
4. Company becomes selectable in header dropdown

### Person Scope
- Persons are scoped to their company
- Users can only see persons in their active company
- Company ID is validated before creating persons
- QuerySets are filtered by `company_id` in views

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
messages.success(self.request, _('Person updated successfully.'))
```

---

## Future Enhancements

1. Add photo upload for personnel
2. Implement digital signature for companies
3. Add multi-step wizard for company registration
4. Implement employee hierarchy (manager relationships)
5. Add role-based field visibility
6. Implement document attachments (contracts, IDs)


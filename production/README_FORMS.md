# Production Module Forms Documentation

## Overview
This document describes the forms used in the production module for managing personnel, machines, work lines, and BOM (Bill of Materials).

**Note**: Personnel (`Person`) and Work Lines (`WorkLine`) are part of the Production module, not Inventory. They are used for production workflows and can optionally be referenced in inventory consumption issues.

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

### 3. WorkLineForm
**Purpose:** Create and edit work lines with personnel and machines assignment

**Model:** `WorkLine`

**Fields:**
- `warehouse` - Optional warehouse assignment (FK to inventory.Warehouse, only if inventory module is installed)
- `name` - Work line name (Persian)
- `name_en` - Work line name (English)
- `description` - Brief description
- `notes` - Detailed notes
- `sort_order` - Display order
- `is_enabled` - Active/Inactive status
- `personnel` - Multiple personnel assignment (ManyToMany to Person)
- `machines` - Multiple machines assignment (ManyToMany to Machine)

**Auto-Generated Fields:**
- `public_code` (5 digits) - Automatically generated sequential code per company. Not user-editable. Generated on save using `generate_sequential_code()`.

**Special Features:**
- Warehouse field is optional and hidden if inventory module is not installed
- Personnel and machines dropdowns filtered by active company
- ManyToMany relationships saved via `form.save_m2m()` in views
- Warehouse field is hidden if inventory module is not installed

**Validation:**
- Name must be unique per company (and per warehouse if warehouse is assigned)
- Warehouse must belong to the active company (if provided)
- Personnel and machines must belong to the active company

**Usage in Views:**
```python
class WorkLineCreateView(FeaturePermissionRequiredMixin, CreateView):
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'create'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        messages.success(self.request, _('Work line created successfully.'))
        return response
```

**Important Notes:**
- `WorkLine` is part of the Production module, not Inventory
- Warehouse assignment is optional (only if inventory module is installed)
- Work lines can be used in inventory consumption issues as destination
- Personnel and machines are filtered by company and enabled status

---

### 4. BOMForm
**Purpose:** Create and edit BOM (Bill of Materials) headers

**Model:** `BOM`

**Fields:**
- `finished_item` - Finished product that will be produced (FK to Item)
- `version` - BOM version (default: "1.0")
- `effective_date` - Date when BOM becomes effective
- `expiry_date` - Date when BOM expires (optional)
- `is_active` - Active/Inactive status (1=Active, 0=Inactive)
- `description` - Brief description
- `notes` - Detailed notes

**Extra Filter Fields (not saved):**
- `item_type` - Filter finished items by type (cascading)
- `item_category` - Filter finished items by category (cascading)

**Auto-Generated Fields:**
- `bom_code` (16 digits) - Automatically generated sequential code per company. Not user-editable. Generated on save using `generate_sequential_code()`.
- `finished_item_code` - Cached from finished_item.item_code

**Cascading Behavior:**
```python
# Step 1: User selects item_type (optional)
# → item_category dropdown filters to show only categories of that type

# Step 2: User selects item_category (optional)
# → finished_item dropdown filters to show only items in that category

# Step 3: User selects finished_item (required)
# → BOM can be saved
```

**Validation:**
```python
def __init__(self, *args, company_id=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.company_id = company_id
    
    if self.company_id:
        # Filter all dropdowns by company
        self.fields['finished_item'].queryset = Item.objects.filter(
            company_id=self.company_id, is_enabled=1
        )
        self.fields['item_type'].queryset = ItemType.objects.filter(
            company_id=self.company_id, is_enabled=1
        )
        self.fields['item_category'].queryset = ItemCategory.objects.filter(
            company_id=self.company_id, is_enabled=1
        )
    
    # On edit: populate filter fields from existing instance
    if self.instance.pk and self.instance.finished_item:
        self.fields['item_type'].initial = self.instance.finished_item.type
        self.fields['item_category'].initial = self.instance.finished_item.category
```

**Usage in Views:**
```python
class BOMCreateView(FeaturePermissionRequiredMixin, CreateView):
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    success_url = reverse_lazy('production:bom_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = BOMMaterialLineFormSet(
                self.request.POST, 
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        else:
            context['formset'] = BOMMaterialLineFormSet(
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            if form.is_valid() and formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                messages.success(self.request, _('BOM created successfully.'))
                return super().form_valid(form)
            else:
                return self.render_to_response(self.get_context_data(form=form))
```

---

### 5. BOMMaterialLineForm
**Purpose:** Create and edit individual BOM material lines

**Model:** `BOMMaterial`

**Fields:**
- `material_type` - Material type (FK to inventory.ItemType - user-defined types)
- `material_item` - Material/component item (FK to Item)
- `quantity_per_unit` - Quantity needed per 1 unit of finished product
- `unit` - Unit of measurement (CharField - can be primary_unit or conversion unit name)
- `scrap_allowance` - Waste percentage (0-100%)
- `is_optional` - Optional flag (BooleanField in form, stores as 0=Required, 1=Optional in database)
- `description` - Brief description
- `notes` - Detailed notes
- `line_number` - Line ordering (hidden field, auto-managed)

**Extra Filter Fields (not saved to database):**
- `material_category_filter` - Filter materials by category (ModelChoiceField to ItemCategory)
- `material_subcategory_filter` - Filter materials by subcategory (ModelChoiceField to ItemSubcategory)

**Auto-Generated Fields:**
- `material_item_code` - Cached from material_item.item_code
- `company_id` - Inherited from parent BOM

**Cascading Behavior:**
```python
# Step 1: User selects material_type (required) - FK to ItemType
# → material_category_filter dropdown shows only categories containing items of this type

# Step 2: User selects material_category_filter (optional)
# → material_subcategory_filter dropdown shows only subcategories containing items of this type+category

# Step 3: User selects material_subcategory_filter (optional)
# → material_item dropdown filters to show only items matching type+category+subcategory

# Step 4: User selects material_item (required)
# → unit dropdown populated from API with primary_unit + conversion units
# → unit dropdown enabled

# Step 5: User selects unit (required)
# → Line is ready
```

**Important Notes:**
- `material_type` is a ForeignKey to `inventory.ItemType` (not hardcoded choices)
- `unit` is a CharField that stores the unit name (not FK to ItemUnit)
- This allows storing both primary_unit (string) and conversion units (from ItemUnit)
- Filter fields (category/subcategory) only show options that contain items of the selected type

**API Endpoints Used:**
- `/inventory/api/filtered-categories/?type_id=X` - Get categories with items of type X
- `/inventory/api/filtered-subcategories/?type_id=X&category_id=Y` - Get subcategories with items
- `/inventory/api/filtered-items/?type_id=X&category_id=Y&subcategory_id=Z` - Get filtered items
- `/inventory/api/item-units/?item_id=X` - Get primary_unit + conversion units for item X
  - **Enhanced Response** (as of 2025-11-20c):
    ```json
    {
      "units": [
        {"value": "base_kg", "label": "کیلوگرم (واحد اصلی)", "is_base": true, "unit_name": "کیلوگرم"},
        {"value": "gram", "label": "گرم (1 کیلوگرم = 1000 گرم)", "unit_name": "گرم"}
      ],
      "item_type_id": "1",
      "item_type_name": "خام",
      "category_id": "3",
      "subcategory_id": "2"
    }
    ```
  - Returns `category_id` and `subcategory_id` for easier edit mode restoration

**Special Field: `is_optional`**
- Form field type: `BooleanField` with `CheckboxInput` widget
- Database storage: `PositiveSmallIntegerField` (0 = Required, 1 = Optional)
- Conversion handled in `clean_is_optional()` method:
  ```python
  def clean_is_optional(self):
      """Convert Boolean checkbox value to integer (0 or 1) for database storage."""
      value = self.cleaned_data.get('is_optional')
      if value is True:
          return 1  # Optional
      else:
          return 0  # Required
  ```
- When checkbox is checked → stores `1` (optional)
- When checkbox is unchecked → stores `0` (required)

**Validation:**
```python
def clean(self):
    cleaned_data = super().clean()
    material_item = cleaned_data.get('material_item')
    unit = cleaned_data.get('unit')
    
    # Remove filter fields from cleaned_data (they're not saved to DB)
    if 'material_category_filter' in cleaned_data:
        del cleaned_data['material_category_filter']
    if 'material_subcategory_filter' in cleaned_data:
        del cleaned_data['material_subcategory_filter']
    
    # Auto-set material_type from material_item if not provided
    if material_item and not cleaned_data.get('material_type'):
        cleaned_data['material_type'] = material_item.type
    
    # Validate unit is required if material_item is selected
    if material_item and not unit:
        self.add_error('unit', _('Please select a unit for the selected material.'))
    
    # If no material_item, don't require other fields (empty form)
    if not material_item:
        for field in ['material_type', 'quantity_per_unit', 'unit']:
            if field in cleaned_data and not cleaned_data[field]:
                cleaned_data[field] = None
    
    return cleaned_data
```

**Usage in Formset:**
```python
BOMMaterialLineFormSet = inlineformset_factory(
    BOM,                        # Parent model
    BOMMaterial,                # Child model
    form=BOMMaterialLineForm,   # Form class
    extra=1,                    # 1 empty form by default (changed from 3)
    can_delete=True,            # Show DELETE checkbox
    min_num=1,                  # At least 1 line required
    validate_min=True           # Validate minimum
)
```

---

### 6. BOMMaterialLineFormSet
**Purpose:** Manage multiple material lines within a single BOM

**Type:** Django Inline Formset (inlineformset_factory)

**Configuration:**
```python
BOMMaterialLineFormSet = inlineformset_factory(
    BOM,
    BOMMaterial,
    form=BOMMaterialLineForm,
    extra=1,         # Show 1 empty form initially (changed from 3)
    can_delete=True, # Allow deletion of existing lines
    min_num=1,       # Require at least 1 line
    validate_min=True
)
```

**Key Features:**
- **Dynamic Add/Remove**: JavaScript allows adding/removing lines without page reload
- **TOTAL_FORMS Management**: Auto-updates hidden TOTAL_FORMS field when lines are added/removed
- **Line Numbering**: Auto-assigns line_number (1, 2, 3, ...) to maintain order
- **Validation**: Ensures at least 1 material line exists
- **DELETE Handling**: Marks existing lines for deletion using DELETE checkbox

**JavaScript Functions:**

#### 1. Formset Management
```javascript
// Add new line
function addNewLine() {
    // 1. Clone last formset row
    // 2. Update all field names/ids (materials-0-* → materials-N-*)
    // 3. Clear all values
    // 4. Increment line_number
    // 5. Update TOTAL_FORMS count
    // 6. Attach event listeners for cascading filters
    // 7. Append to table
}

// Remove line
function removeLine(button) {
    // 1. Check minimum 1 line requirement
    // 2. Remove row from DOM
    // 3. If new line: decrement TOTAL_FORMS
    // 4. If existing line: check DELETE checkbox
    // 5. Renumber remaining lines
}

// Renumber lines
function renumberLines() {
    // Update line_number fields to maintain sequence (1, 2, 3, ...)
}
```

#### 2. Edit Mode Value Restoration
When editing an existing BOM, the form automatically restores all values (type, category, subcategory, unit) for each material line:

```javascript
// On page load: if item is already selected (edit mode)
if (itemSelect.value) {
    const itemId = itemSelect.value;
    
    // Save current unit value before making API calls
    let savedUnitValue = unitSelect.value || row.dataset.unitValue;
    
    // Load item units API which returns type_id, category_id, subcategory_id, and units
    fetch('/inventory/api/item-units/?item_id=' + itemId)
        .then(response => response.json())
        .then(data => {
            // Step 1: Auto-set material_type
            if (data.item_type_id) {
                typeSelect.value = data.item_type_id;
                
                // Step 2: Load and set category
                if (data.category_id) {
                    filterCategories();
                    setTimeout(() => {
                        categorySelect.value = data.category_id;
                        
                        // Step 3: Load and set subcategory
                        if (data.subcategory_id) {
                            filterSubcategories();
                            setTimeout(() => {
                                subcategorySelect.value = data.subcategory_id;
                            }, 300);
                        }
                    }, 300);
                }
            }
            
            // Step 4: Load and restore unit
            // Populate unit dropdown and restore saved value
        });
}
```

**Restoration Flow:**
1. Material type auto-set from item's `type_id`
2. Category dropdown populated based on type, then value restored from `category_id`
3. Subcategory dropdown populated based on type+category, then value restored from `subcategory_id`
4. Unit dropdown populated with primary_unit + conversion units, then value restored from saved value

**Important Notes:**
- Unit value is saved to `row.dataset.unitValue` before page reload to preserve selection
- All unit selects are enabled before form submission (disabled fields are not submitted)
- Sequential API calls use `setTimeout` to ensure dropdowns are populated before values are set

#### 3. Cascading Filters (Each Line Independent)
```javascript
// Filter Categories based on Material Type
function filterCategories(typeSelect, idx) {
    const typeId = typeSelect.value;
    const categorySelect = document.querySelector(`select[name="materials-${idx}-material_category_filter"]`);
    const subcategorySelect = document.querySelector(`select[name="materials-${idx}-material_subcategory_filter"]`);
    const itemSelect = document.querySelector(`select[name="materials-${idx}-material_item"]`);
    
    if (!typeId) {
        resetDropdown(categorySelect);
        resetDropdown(subcategorySelect);
        resetDropdown(itemSelect);
        return;
    }
    
    fetch(`/inventory/api/filtered-categories/?type_id=${typeId}`)
        .then(response => response.json())
        .then(data => {
            populateSelect(categorySelect, data.categories, 'Category');
            resetDropdown(subcategorySelect);
            resetDropdown(itemSelect);
        });
}

// Filter Subcategories based on Type + Category
function filterSubcategories(categorySelect, idx) {
    const typeId = document.querySelector(`select[name="materials-${idx}-material_type"]`).value;
    const categoryId = categorySelect.value;
    const subcategorySelect = document.querySelector(`select[name="materials-${idx}-material_subcategory_filter"]`);
    const itemSelect = document.querySelector(`select[name="materials-${idx}-material_item"]`);
    
    if (!categoryId) {
        resetDropdown(subcategorySelect);
        resetDropdown(itemSelect);
        return;
    }
    
    fetch(`/inventory/api/filtered-subcategories/?type_id=${typeId}&category_id=${categoryId}`)
        .then(response => response.json())
        .then(data => {
            populateSelect(subcategorySelect, data.subcategories, 'Subcategory');
            resetDropdown(itemSelect);
        });
}

// Filter Items based on Type + Category + Subcategory
function filterItems(subcategorySelect, idx) {
    const typeId = document.querySelector(`select[name="materials-${idx}-material_type"]`).value;
    const categoryId = document.querySelector(`select[name="materials-${idx}-material_category_filter"]`).value;
    const subcategoryId = subcategorySelect.value;
    const itemSelect = document.querySelector(`select[name="materials-${idx}-material_item"]`);
    
    if (!subcategoryId) return;
    
    fetch(`/inventory/api/filtered-items/?type_id=${typeId}&category_id=${categoryId}&subcategory_id=${subcategoryId}`)
        .then(response => response.json())
        .then(data => {
            populateSelect(itemSelect, data.items, 'Select Item');
        });
}

// Load Units based on Selected Item
function loadItemUnits(itemSelect, idx) {
    const itemId = itemSelect.value;
    const unitSelect = document.querySelector(`select[name="materials-${idx}-unit"]`);
    
    if (!itemId) {
        resetDropdown(unitSelect);
        unitSelect.disabled = true;
        return;
    }
    
    fetch(`/inventory/api/item-units/?item_id=${itemId}`)
        .then(response => response.json())
        .then(data => {
            populateSelect(unitSelect, data.units, 'Select Unit');
            unitSelect.disabled = false;
        });
}

// Helper: Populate dropdown
function populateSelect(selectElement, items, placeholder) {
    selectElement.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item.value;
        option.textContent = item.label;
        selectElement.appendChild(option);
    });
}

// Helper: Reset dropdown to default
function resetDropdown(selectElement) {
    selectElement.innerHTML = '<option value="">--------</option>';
}
```

**Cascading Flow:**
1. User selects `material_type` → triggers `filterCategories()`
2. User selects `material_category_filter` → triggers `filterSubcategories()`
3. User selects `material_subcategory_filter` → triggers `filterItems()`
4. User selects `material_item` → triggers `loadItemUnits()`
5. User selects `unit` → line is complete

**Form Validation:**
```javascript
form.addEventListener('submit', function(e) {
    // Count visible, non-deleted lines with material selected
    let validLineCount = 0;
    document.querySelectorAll('.formset-row').forEach(row => {
        if (row.style.display !== 'none') {
            let deleteCheckbox = row.querySelector('input[name$="-DELETE"]');
            let materialSelect = row.querySelector('select[name$="-material_item"]');
            
            if ((!deleteCheckbox || !deleteCheckbox.checked) && 
                materialSelect && materialSelect.value) {
                validLineCount++;
            }
        }
    });
    
    if (validLineCount < 1) {
        e.preventDefault();
        alert('حداقل یک ردیف ماده اولیه الزامی است');
    }
});
```

**Template Usage:**
```django
<form method="post">
  {% csrf_token %}
  
  <!-- BOM Header Form -->
  {{ form.as_p }}
  
  <!-- Material Lines Formset -->
  {{ formset.management_form }}
  
  <table>
    <tbody id="formset-container">
      {% for line_form in formset %}
        <tr class="formset-row">
          {{ line_form.as_table_row }}
          <td><button type="button" onclick="removeLine(this)">×</button></td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
  
  <button type="button" onclick="addNewLine()">➕ افزودن ردیف ماده</button>
  <button type="submit">ذخیره</button>
</form>
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


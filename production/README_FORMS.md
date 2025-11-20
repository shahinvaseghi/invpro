# Production Module Forms Documentation

## Overview
This document describes the forms used in the production module for managing personnel, machines, and BOM (Bill of Materials).

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

### 3. BOMForm
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

### 4. BOMMaterialLineForm
**Purpose:** Create and edit individual BOM material lines

**Model:** `BOMMaterial`

**Fields:**
- `material_type` - Material type (FK to inventory.ItemType - user-defined types)
- `material_item` - Material/component item (FK to Item)
- `quantity_per_unit` - Quantity needed per 1 unit of finished product
- `unit` - Unit of measurement (CharField - can be primary_unit or conversion unit name)
- `scrap_allowance` - Waste percentage (0-100%)
- `is_optional` - Optional flag (0=Required, 1=Optional)
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

**Validation:**
```python
def clean(self):
    cleaned_data = super().clean()
    material_item = cleaned_data.get('material_item')
    unit = cleaned_data.get('unit')
    
    # Validate unit exists for material item (either primary_unit or in ItemUnit)
    if material_item and unit:
        if not ItemUnit.objects.filter(
            item=material_item,
            to_unit=unit,
            company_id=self.company_id
        ).exists():
            self.add_error('unit', _("The selected unit must belong to the selected material item."))
    
    return cleaned_data
```

**Usage in Formset:**
```python
BOMMaterialLineFormSet = inlineformset_factory(
    BOM,                        # Parent model
    BOMMaterial,                # Child model
    form=BOMMaterialLineForm,   # Form class
    extra=3,                    # 3 empty forms by default
    can_delete=True,            # Show DELETE checkbox
    min_num=1,                  # At least 1 line required
    validate_min=True           # Validate minimum
)
```

---

### 5. BOMMaterialLineFormSet
**Purpose:** Manage multiple material lines within a single BOM

**Type:** Django Inline Formset (inlineformset_factory)

**Configuration:**
```python
BOMMaterialLineFormSet = inlineformset_factory(
    BOM,
    BOMMaterial,
    form=BOMMaterialLineForm,
    extra=3,         # Show 3 empty forms initially
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

#### 2. Cascading Filters (Each Line Independent)
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


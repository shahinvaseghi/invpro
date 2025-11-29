# Inventory Module Templates Documentation

## Overview

This directory contains all HTML templates for the inventory module. Templates follow Django's template inheritance pattern and use the i18n system for multilingual support (Persian/English).

## Template Hierarchy

```
templates/inventory/
├── base.html                     # Module base template (extends global base)
├── inventory_balance.html        # Balance calculation & display
├── items.html                    # Item catalog list
├── item_types.html              # Item types management
├── item_categories.html         # Item categories (extends item_types)
├── warehouses.html              # Warehouse management
├── work_lines.html              # Work lines management
├── suppliers.html               # Supplier list
├── supplier_categories.html     # Supplier categories
├── warehouse_requests.html      # Warehouse request management
├── purchase_requests.html       # Purchase request management
├── receipt_temporary.html       # Temporary receipts
├── receipt_permanent.html       # Permanent receipts (extends temporary)
├── receipt_consignment.html     # Consignment receipts (extends temporary)
├── issue_permanent.html         # Permanent issues
├── issue_consumption.html       # Consumption issues (extends permanent)
├── issue_consignment.html       # Consignment issues (extends permanent)
├── stocktaking_deficit.html     # Deficit records
├── stocktaking_surplus.html     # Surplus records (extends deficit)
└── stocktaking_records.html     # Stocktaking confirmation records
```

---

## Base Template (`base.html`)

**Purpose**: Provides common structure for all inventory module pages

**Extends**: `base.html` (global)

**Block Structure**:
```django
{% block title %}           # Page title
{% block breadcrumb_extra %} # Additional breadcrumb items
{% block page_title %}       # H1 heading
{% block page_actions %}     # Action buttons (Create, Print, Export)
{% block inventory_content %}# Main content area
{% block inventory_scripts %}# Page-specific JavaScript
```

**Context Variables**:
- `active_module`: Set to 'inventory' for navigation highlighting
- `active_company`: Currently selected company (from context processor)
- `request.user`: Current user object

**Example Usage**:
```django
{% extends "inventory/base.html" %}
{% load i18n %}

{% block page_title %}{% trans "My Page" %}{% endblock %}

{% block inventory_content %}
  <p>Page content here</p>
{% endblock %}
```

---

## Data Display Templates

### 1. List Views (items.html, suppliers.html, etc.)

**Common Structure**:
1. **Filter Panel**: Form with search and filter options
2. **Data Table**: Paginated table with sortable columns
3. **Pagination**: Previous/Next navigation
4. **Empty State**: Displayed when no data exists

**Components**:

#### Filter Panel
```django
<div class="filter-panel">
  <h3>{% trans "Filter" %}</h3>
  <form method="get" action="" class="filter-form">
    <div class="form-group">
      <label for="field">{% trans "Label" %}</label>
      <input type="text" name="field" class="form-control">
    </div>
    <button type="submit" class="btn btn-primary">
      {% trans "Filter" %}
    </button>
  </form>
</div>
```

#### Data Table
```django
<div class="data-table-container">
  <table class="data-table">
    <thead>
      <tr>
        <th>{% trans "Column" %}</th>
      </tr>
    </thead>
    <tbody>
      {% for object in objects %}
      <tr>
        <td>{{ object.field }}</td>
      </tr>
      {% empty %}
      <tr>
        <td colspan="N">
          <div class="empty-state">
            <h3>{% trans "No Data" %}</h3>
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

#### Pagination
```django
{% if is_paginated %}
<div class="pagination">
  {% if page_obj.has_previous %}
    <a href="?page={{ page_obj.previous_page_number }}">
      {% trans "Previous" %}
    </a>
  {% endif %}
  <span class="current">
    {% trans "Page" %} {{ page_obj.number }}
  </span>
  {% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}">
      {% trans "Next" %}
    </a>
  {% endif %}
</div>
{% endif %}
```

#### Temporary Receipts (`receipt_temporary.html`)

- **Stats Grid**: Uses `stats.total`, `stats.awaiting_qc`, `stats.qc_passed`, `stats.converted` (provided by `ReceiptTemporaryListView`).
- **Filters**:
  - `status_filter`: Values `draft`, `awaiting_qc`, `qc_passed`, `qc_failed`.
  - `converted_filter`: `"0"` یا `"1"` برای وضعیت تبدیل.
  - `search_query`: متن جستجو برای کد سند یا نام کالا.
- **QC Badges**: چهار وضعیت نمایش داده می‌شود:
  - `Draft` (badge-draft)
  - `Awaiting QC` (badge-pending)
  - `QC Approved` (badge-active)
  - `Closed/Rejected` (badge-inactive)

---

### 2. Special Templates

#### inventory_balance.html

**Purpose**: Display calculated inventory balances with filters

**Unique Features**:
- **Stats Cards**: Show total items, total balance, calculation date
- **Advanced Filters**: Warehouse, item type, category, as-of date
- **Balance Calculation**: Color-coded balance display (red=negative, green=positive)
- **Export**: JavaScript function to export table to CSV/Excel

**Key Elements**:
```django
<!-- Stats Summary -->
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-label">{% trans "Total Items" %}</div>
    <div class="stat-value">{{ total_items }}</div>
  </div>
</div>

<!-- Balance Table -->
<table class="data-table">
  <tr>
    <td style="font-weight: 600;">
      {% if balance.current_balance < 0 %}
        <span style="color: #ef4444;">{{ balance.current_balance }}</span>
      {% else %}
        <span style="color: #10b981;">{{ balance.current_balance }}</span>
      {% endif %}
    </td>
  </tr>
</table>
```

**JavaScript**:
- `exportToExcel()`: Converts table to CSV and triggers download

---

#### warehouse_requests.html / purchase_requests.html

**Purpose**: Manage internal and external material requests

**Unique Features**:
- **Priority Badges**: Visual priority indicators (low, normal, high, urgent)
- **Status Workflow**: Draft → Submitted → Approved → Issued/Rejected/Cancelled
- **Stats Cards**: Count by status

**Status Display Logic**:
```django
{% if request.request_status == 'draft' %}
  <span class="badge badge-draft">{% trans "Draft" %}</span>
{% elif request.request_status == 'submitted' %}
  <span class="badge badge-pending">{% trans "Submitted" %}</span>
{% elif request.request_status == 'approved' %}
  <span class="badge badge-approved">{% trans "Approved" %}</span>
{% endif %}
```

---

## CSS Classes

### Layout Classes
- `.inventory-module`: Main container
- `.module-header`: Page header with breadcrumbs and title
- `.module-content`: Main content area
- `.page-title`: H1 page heading
- `.breadcrumb`: Navigation trail

### Component Classes
- `.filter-panel`: Filter form container
- `.filter-form`: Grid layout for form fields
- `.form-group`: Single form field wrapper
- `.form-control`: Input/select styling

### Data Display
- `.data-table-container`: Table wrapper with border
- `.data-table`: Main table styling
- `.data-table thead`: Table header
- `.data-table tbody tr:hover`: Row hover effect

### Status & Actions
- `.badge`: Base badge style
- `.badge-draft`: Gray (draft status)
- `.badge-pending`: Yellow (pending approval)
- `.badge-approved`: Green (approved)
- `.badge-rejected`: Red (rejected)
- `.badge-active`: Green (active/enabled)
- `.badge-inactive`: Gray (inactive/disabled)

### Buttons
- `.btn`: Base button style
- `.btn-primary`: Blue primary action button
- `.btn-secondary`: Gray secondary button
- `.btn-success`: Green success button

### Stats & Cards
- `.stats-grid`: Grid layout for stat cards
- `.stat-card`: Individual stat card
- `.stat-label`: Label text
- `.stat-value`: Large number display

### Empty States
- `.empty-state`: Container for empty state
- `.empty-state-icon`: Large icon (emoji)
- `.empty-state h3`: Title
- `.empty-state p`: Description text

---

## Internationalization (i18n)

### Setup
Every template must load i18n at the top:
```django
{% load i18n %}
```

### Translating Strings
Use `{% trans %}` tag for static strings:
```django
<h1>{% trans "Item Catalog" %}</h1>
<button>{% trans "Create" %}</button>
```

### Variable Translation
For dynamic content, translate in views:
```python
from django.utils.translation import gettext as _

context['message'] = _("Welcome to %(name)s") % {'name': company.name}
```

### RTL Support
Template automatically adjusts for RTL via `dir` attribute:
```html
<html dir="{% if LANGUAGE_CODE == 'fa' %}rtl{% else %}ltr{% endif %}">
```

CSS handles RTL-specific styles:
```css
[dir="rtl"] .element {
  /* RTL-specific styles */
}
```

---

## Template Inheritance Patterns

### Pattern 1: Direct Extension
```django
{% extends "inventory/base.html" %}
```
Used by most templates.

### Pattern 2: Sibling Extension
```django
{% extends "inventory/receipt_temporary.html" %}
```
Used when templates share 95% of structure (e.g., receipt types).

**Benefits**:
- DRY (Don't Repeat Yourself)
- Consistent styling
- Easy maintenance

**When to Use Sibling Extension**:
- Templates differ only in title and actions
- Same data structure
- Same table columns
- Only minor text differences

---

## Context Variables

### Common to All Templates
- `request`: Django request object
  - `request.user`: Current user
  - `request.GET`: URL parameters
  - `request.POST`: Form data
- `active_company`: Selected company object
- `user_companies`: List of accessible companies
- `active_module`: Module identifier ('inventory')

### List View Templates
- `object_list` or custom name (e.g., `items`, `suppliers`)
- `is_paginated`: Boolean for pagination
- `page_obj`: Paginator object with:
  - `number`: Current page number
  - `paginator.num_pages`: Total pages
  - `has_previous`: Boolean
  - `has_next`: Boolean
  - `previous_page_number`: Int
  - `next_page_number`: Int

### Balance Template Specific
- `warehouses`: Queryset of available warehouses
- `item_types`: Queryset of item types
- `item_categories`: Queryset of categories
- `balances`: List of balance calculations
- `total_items`: Count of items with balances
- `total_balance_value`: Sum of all balances
- `selected_warehouse_id`: Currently selected warehouse
- `as_of_date`: Date for balance calculation

---

## JavaScript Integration

### Inline Scripts
Place in `{% block inventory_scripts %}`:
```django
{% block inventory_scripts %}
<script>
  document.addEventListener('DOMContentLoaded', function() {
    // Your code here
  });
</script>
{% endblock %}
```

### Common Functions

#### Table Export
```javascript
function exportToExcel() {
  const table = document.getElementById('tableId');
  // Convert table to CSV
  // Trigger download
}
```

#### Form Auto-Submit
```javascript
// Used for filters
<select onchange="this.form.submit()">
```

---

## Accessibility

### Best Practices
1. **Labels**: All form inputs have `<label>` tags
2. **Alt Text**: Images include `alt` attributes
3. **Semantic HTML**: Use `<table>`, `<form>`, `<button>` appropriately
4. **Keyboard Navigation**: All interactive elements focusable
5. **Color Contrast**: Text meets WCAG AA standards

### ARIA Attributes (Future Enhancement)
```html
<button aria-label="{% trans 'Create new item' %}">+</button>
<div role="alert">{% trans "Error message" %}</div>
```

---

## Performance Optimization

### Lazy Loading
Use `{% if %}` to conditionally load content:
```django
{% if warehouse_id %}
  {# Only calculate when warehouse selected #}
  {{ balances }}
{% endif %}
```

### Pagination
Always paginate large datasets:
```python
# In views.py
paginate_by = 50  # Show 50 items per page
```

### Query Optimization
Use `select_related()` and `prefetch_related()` in views to reduce N+1 queries.

---

## Customization Guide

### Adding a New Template

1. **Create File**: `templates/inventory/my_feature.html`

2. **Extend Base**:
```django
{% extends "inventory/base.html" %}
{% load i18n %}
```

3. **Set Title**:
```django
{% block page_title %}{% trans "My Feature" %}{% endblock %}
```

4. **Add Breadcrumb**:
```django
{% block breadcrumb_extra %}
<span class="separator">/</span>
<span>{% trans "My Feature" %}</span>
{% endblock %}
```

5. **Add Actions**:
```django
{% block page_actions %}
<a href="#" class="btn btn-primary">
  + {% trans "Create" %}
</a>
{% endblock %}
```

6. **Add Content**:
```django
{% block inventory_content %}
  <!-- Your content here -->
{% endblock %}
```

7. **Create View**: Add to `inventory/views.py`
8. **Add URL**: Add to `inventory/urls.py`
9. **Update Sidebar**: Add link to `templates/ui/components/sidebar.html`
10. **Add Translations**: Update `locale/fa/LC_MESSAGES/django.po`

---

## Troubleshooting

### Common Issues

**Problem**: Template not found
```
TemplateDoesNotExist at /inventory/items/
```
**Solution**: Check file name matches exactly, including `.html` extension

**Problem**: Translation not working
```
Text appears in English even in Persian mode
```
**Solution**: 
1. Ensure `{% load i18n %}` at top
2. Check `{% trans "Text" %}` syntax
3. Verify translation in `.po` file
4. Compile translations: `python manage.py compilemessages`

**Problem**: Styles not applied
```
Elements have no styling
```
**Solution**:
1. Check CSS class names match `base.css`
2. Ensure `{% load static %}` if using images/JS
3. Run `python manage.py collectstatic` in production

**Problem**: Context variable undefined
```
'items' is undefined
```
**Solution**:
1. Check view passes variable in `get_context_data()`
2. Check variable name matches `context_object_name` in view
3. Use `{% if items %}` to handle missing data

---

## Testing Templates

### Manual Testing Checklist
- [ ] Persian and English translations display correctly
- [ ] RTL layout works properly in Persian mode
- [ ] Empty state displays when no data
- [ ] Pagination works correctly
- [ ] Filter form submits and filters data
- [ ] Action buttons are visible and clickable
- [ ] Table rows are hoverable
- [ ] Status badges display correct colors
- [ ] Print layout is readable
- [ ] Mobile responsive (if applicable)

### Automated Testing (Future)
```python
from django.test import TestCase

class TemplateRenderTest(TestCase):
    def test_items_page_renders(self):
        response = self.client.get('/inventory/items/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/items.html')
```

---

## Related Files

- `inventory/views.py`: View classes that render these templates
- `inventory/urls.py`: URL routing to views
- `static/css/base.css`: Stylesheet for all templates
- `locale/fa/LC_MESSAGES/django.po`: Persian translations
- `templates/base.html`: Global base template
- `templates/ui/components/sidebar.html`: Navigation menu

---

## Maintainer Notes

- Always extend from `inventory/base.html` for consistency
- Use existing CSS classes before creating new ones
- Add new translatable strings to `.po` file immediately
- Test both Persian and English modes
- Follow naming convention: singular for detail, plural for list
- Document any new template patterns in this README
- Keep templates DRY using inheritance and includes

---

## Future Enhancements

1. **AJAX Loading**: Load table data without page refresh
2. **Advanced Filters**: Collapsible filter panel with more options
3. **Bulk Actions**: Select multiple rows and perform batch operations
4. **Inline Editing**: Edit table cells directly without modal
5. **Custom Columns**: Let users choose which columns to display
6. **Saved Filters**: Save and recall filter combinations
7. **Print Templates**: Dedicated print-friendly layouts
8. **Mobile App**: Responsive templates for mobile warehouse tasks


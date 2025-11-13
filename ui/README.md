# ui app overview

The UI app provides the template-based user interface shell, navigation, company/language switching, and dashboard for the platform. This README documents all custom files and their responsibilities.

---

## views.py

### DashboardView
- **Type**: `TemplateView` with `LoginRequiredMixin`
- **Template**: `templates/ui/dashboard.html`
- **Purpose**: Entry point showing platform overview with module cards
- **Auth**: Redirects unauthenticated users to admin login
- **URL**: `/` (root path)

---

## urls.py

Defines URL patterns for the UI module:

| Path | View | Name | Description |
|------|------|------|-------------|
| `""` | `DashboardView` | `ui:dashboard` | Landing page / dashboard |

---

## context_processors.py

### active_module(request)
- **Purpose**: Exposes `active_module` value to all templates
- **Current Implementation**: Derived from query string `module` parameter
- **Usage**: Highlights current module in navigation
- **Future**: Will be set automatically based on URL path

**Context Variables Added**:
- `active_module`: String identifying current module ('inventory', 'production', 'qc', etc.)

---

## templates

### base.html (Global Layout)

**Location**: `templates/base.html`

**Purpose**: Master template providing consistent layout for entire platform

**Structure**:
```html
<html dir="rtl/ltr">  <!-- Auto-set based on language -->
  <header class="app-header">
    <div class="logo">invproj</div>
    <nav class="top-nav">
      <!-- Company Selector -->
      <form class="company-switcher">
        <select name="company_id">...</select>
      </form>
      
      <!-- Language Switcher -->
      <form class="language-switcher">
        <select name="language">
          <option value="en">English</option>
          <option value="fa">Persian</option>
        </select>
      </form>
      
      <!-- User Info -->
      <span class="company-context">👤 Username</span>
    </nav>
  </header>
  
  <aside class="app-sidebar">
    {% include "ui/components/sidebar.html" %}
  </aside>
  
  <main class="app-content">
    {% block content %}{% endblock %}
  </main>
</html>
```

**Blocks**:
- `{% block title %}`: Page title (appears in browser tab)
- `{% block top_nav %}`: Header navigation override
- `{% block sidebar %}`: Sidebar override
- `{% block content %}`: Main page content
- `{% block extra_scripts %}`: Page-specific JavaScript

**Features**:
- **Company Switching**: Dropdown to select active company
  - POST to `/shared/set-company/`
  - Stores `company_id` in session
  - Reloads page with selected company
  
- **Language Switching**: Dropdown to select UI language
  - POST to `/i18n/setlang/`
  - Supports English and Persian
  - Automatic RTL layout for Persian
  
- **Responsive Design**: CSS Grid layout adapts to screen size
- **Icon Support**: User icon (👤) displayed next to username

---

### templates/ui/components/sidebar.html

**Purpose**: Navigation menu with hierarchical structure

**Structure**:
```
Shared
├── Dashboard
├── Companies
├── Personnel
├── Users
├── Groups
└── Access Levels

Inventory
├── Master Data
│   ├── Item Types
│   ├── Item Categories
│   ├── Item Catalog
│   ├── Warehouses
│   └── Work Lines
├── Suppliers
│   ├── Supplier Categories
│   └── Supplier List
├── Inventory Balance
├── Purchase Requests
├── Warehouse Requests
├── Receipts
│   ├── Temporary Receipts
│   ├── Permanent Receipts
│   └── Consignment Receipts
├── Issues
│   ├── Permanent Issues
│   ├── Consumption Issues
│   └── Consignment Issues
└── Stocktaking
    ├── Deficit Records
    ├── Surplus Records
    └── Stocktaking Records

Production
├── BOM
├── Processes
└── Orders

Quality Control
└── Inspections
```

**Features**:
- **Collapsible Submenus**: Click to expand/collapse
- **Active Highlighting**: Current page highlighted
- **i18n Support**: All labels translatable
- **RTL Compatible**: Menu structure flips for Persian
- **Request Workflows**: صفحات Purchase/Warehouse Requests شامل دکمه‌های ایجاد، ویرایش و تایید هستند و وضعیت قفل‌بودن را با نشانگر مشخص نمایش می‌دهند.

**JavaScript**:
```javascript
// Toggle submenu
document.querySelectorAll('.nav-expandable').forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    const submenuId = this.getAttribute('data-submenu');
    const submenu = document.getElementById(submenuId);
    submenu.classList.toggle('open');
    this.classList.toggle('expanded');
  });
});
```

**CSS Classes**:
- `.nav-section-title`: Section header (e.g., "Inventory")
- `.nav-link`: Main menu item
- `.nav-expandable`: Menu item with submenu
- `.nav-submenu`: Hidden submenu container
- `.nav-link-sub`: Submenu item

---

### templates/ui/dashboard.html

**Purpose**: Landing page showing platform overview

**Extends**: `base.html`

**Content**:
```django
<section class="page-section">
  <div class="section-header">
    <h1>Platform Overview</h1>
    <p>Quick snapshot of inventory, production, and QC activities.</p>
  </div>

  <div class="dashboard-grid">
    <!-- Inventory Card -->
    <div class="card">
      <h2>Inventory</h2>
      <ul>
        <li><strong>Master Data</strong>: manage item catalog, suppliers, warehouses.</li>
        <li><strong>Transactions</strong>: capture receipts, issues, and stocktaking adjustments.</li>
        <li><strong>Traceability</strong>: track lot numbers for critical items.</li>
      </ul>
    </div>

    <!-- Production Card -->
    <div class="card">
      <h2>Production</h2>
      <ul>
        <li><strong>BOM & Processes</strong>: define materials, steps, and work centers.</li>
        <li><strong>Orders</strong>: plan, release, and monitor production jobs.</li>
        <li><strong>Performance</strong>: record production output, scrap, cycle times.</li>
      </ul>
    </div>

    <!-- Quality Control Card -->
    <div class="card">
      <h2>Quality Control</h2>
      <ul>
        <li><strong>Inspections</strong>: review temporary receipts pending approval.</li>
        <li><strong>Decisions</strong>: approve, reject, or log deviations with notes.</li>
        <li><strong>Attachments</strong>: keep inspection evidence accessible.</li>
      </ul>
    </div>
  </div>
</section>
```

**Features**:
- **Module Overview**: Summary cards for each module
- **Quick Actions**: Prominent links to common tasks
- **i18n**: All text translatable

---

## static assets

### static/css/base.css

**Purpose**: Global stylesheet for platform UI

**Sections**:

1. **Root Variables & Typography**
   ```css
   :root {
     font-family: "Inter", "Segoe UI", sans-serif;
   }
   [dir="rtl"] {
     font-family: "Vazir", "Tahoma", sans-serif;
   }
   ```

2. **Layout Grid**
   ```css
   .app-shell {
     display: grid;
     grid-template-columns: 280px 1fr;
     grid-template-rows: 64px 1fr;
   }
   ```

3. **Header Styling**
   ```css
   .app-header {
     background-color: #111827;
     color: #fff;
   }
   ```

4. **Company & Language Selectors**
   ```css
   .company-select, .language-select {
     background-color: rgba(255, 255, 255, 0.1);
     border-radius: 6px;
     padding: 6px 12px;
   }
   ```

5. **Sidebar Navigation**
   ```css
   .sidebar-nav { /* Styling */ }
   .nav-link { /* Styling */ }
   .nav-submenu { /* Collapsible submenu */ }
   ```

6. **Content Area**
   ```css
   .page-section {
     background-color: #fff;
     border-radius: 12px;
     padding: 32px;
     box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
   }
   ```

7. **Dashboard Cards**
   ```css
   .dashboard-grid {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
     gap: 24px;
   }
   .card { /* Card styling */ }
   ```

8. **Inventory Module Styles**
   - Filter panels
   - Data tables
   - Status badges
   - Buttons
   - Pagination
   - Empty states
   - Stats cards

**Total Lines**: ~500 lines of CSS

**RTL Support**: Uses `[dir="rtl"]` selectors for Persian layout

---

## apps.py

### UiConfig
- **Type**: `AppConfig` subclass
- **Purpose**: Django app configuration
- **Current**: Default configuration only
- **Future**: Use `ready()` hook for:
  - Template tag registration
  - Signal connections
  - UI-specific initialization

---

## Multi-Company Integration

### How It Works

1. **Context Processor**: `shared.context_processors.active_company`
   - Adds `active_company` to all templates
   - Adds `user_companies` list to all templates

2. **Company Selector in Header**:
   ```django
   <form action="/shared/set-company/" method="post">
     <select name="company_id" onchange="this.form.submit()">
       {% for company in user_companies %}
         <option value="{{ company.id }}" 
                 {% if active_company.id == company.id %}selected{% endif %}>
           {{ company.display_name }} ({{ company.public_code }})
         </option>
       {% endfor %}
     </select>
   </form>
   ```

3. **Session Storage**:
   - Selected company stored in `request.session['active_company_id']`
   - Persists across page loads
   - Cleared on logout

4. **View Integration**:
   - All views automatically filter by active company
   - See `inventory.views.InventoryBaseView.get_queryset()`

---

## Internationalization (i18n)

### Supported Languages
- **English** (en): Default
- **Persian** (fa): Full RTL support

### Translation Files
- `locale/fa/LC_MESSAGES/django.po`: Persian translations (268 strings)
- Compiled to `django.mo` for runtime use

### Usage in Templates
```django
{% load i18n %}
{% trans "Dashboard" %}  <!-- Translated to داشبورد in Persian -->
```

### Language Switching Flow
1. User selects language from dropdown
2. Form POSTs to `/i18n/setlang/`
3. Django sets `django_language` cookie
4. Page reloads with new language
5. `<html>` tag `dir` attribute updates (rtl/ltr)

---

## Navigation System

### URL Structure
```
/                                   # Dashboard
/inventory/
├── /item-types/                   # Master data
├── /items/                        # Item catalog
├── /balance/                      # Inventory balance
├── /purchase-requests/            # Purchase requests
├── /warehouse-requests/           # Warehouse requests
├── /receipts/temporary/           # Receipts
├── /issues/permanent/             # Issues
└── /stocktaking/deficit/          # Stocktaking

/production/
└── (future URLs)

/qc/
└── (future URLs)

/shared/
└── /set-company/                  # Company switching endpoint
```

### URL Naming Convention
- **Namespace**: Each module has namespace (`ui:`, `inventory:`, etc.)
- **Names**: Lowercase with underscores (`item_types`, `warehouse_requests`)
- **Patterns**: Plural for lists, singular for details

---

## Security & Access Control

### Current Implementation
- **Authentication**: `LoginRequiredMixin` on all views
- **Redirect**: Unauthenticated users → `/admin/login/`
- **Company Filtering**: Automatic in views via `get_queryset()`

### Future Enhancements
- **Permission Checks**: Use `AccessLevel` and `AccessLevelPermission`
- **Decorator**: `@permission_required('module', 'resource', 'action')`
- **Template Tags**: `{% if has_perm 'inventory' 'item' 'create' %}`

---

## Testing

### Manual Testing Checklist
- [ ] Dashboard loads for authenticated user
- [ ] Company selector shows all accessible companies
- [ ] Company switching works and persists
- [ ] Language switching works (English/Persian)
- [ ] RTL layout correct in Persian mode
- [ ] Sidebar navigation expands/collapses
- [ ] All sidebar links point to correct URLs
- [ ] Logout redirects properly

### Automated Tests (Future)
```python
class DashboardTest(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/admin/login/?next=/')
    
    def test_dashboard_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ui/dashboard.html')
```

---

## Future Work / Notes

### Planned Features
1. **Real-time Notifications**: WebSocket for alerts
2. **User Preferences**: Save sidebar state, default company
3. **Customizable Dashboard**: Drag-and-drop widgets
4. **Dark Mode**: Theme toggle
5. **Mobile Navigation**: Hamburger menu for small screens
6. **Search**: Global search across all modules
7. **Recent Items**: Quick access to recently viewed records

### Integration Tests
- Add Selenium/Playwright tests for critical user flows
- Test company switching with multiple users
- Verify permission-based navigation hiding

### SPA Considerations
- If migrating to React/Vue:
  - Keep Django templates for server-rendered fallback
  - Use Django REST Framework for API
  - Document build process and asset pipeline

---

## Troubleshooting

### Company Selector Not Showing
**Cause**: User has no company access
**Solution**: Create `UserCompanyAccess` record in admin

### Language Not Switching
**Cause**: Translation files not compiled
**Solution**: Run `python manage.py compilemessages`

### Sidebar Links Broken
**Cause**: URLs not defined in module
**Solution**: Check `inventory/urls.py` for missing patterns

### RTL Layout Broken
**Cause**: CSS not loaded or `dir` attribute missing
**Solution**: Verify `{% load static %}` and check `<html dir="...">`

---

## Related Files

### Core Files
- `templates/base.html`: Global layout
- `templates/ui/dashboard.html`: Landing page
- `templates/ui/components/sidebar.html`: Navigation
- `static/css/base.css`: Styles
- `ui/views.py`: Dashboard view
- `ui/urls.py`: URL routing
- `ui/context_processors.py`: Template context

### Multi-Company System
- `shared/context_processors.py`: Company context
- `shared/views.py`: Company switching
- `shared/urls.py`: Company switching URL
- `shared/models.py`: `UserCompanyAccess`

### Internationalization
- `locale/fa/LC_MESSAGES/django.po`: Translations
- `config/settings.py`: i18n configuration
- `config/urls.py`: Language switching URL

---

## Maintainer Notes

- Update sidebar when adding new modules/pages
- Add translations immediately when adding new UI text
- Test both English and Persian modes
- Verify company filtering in all new views
- Keep CSS organized by component
- Document any new template patterns
- Run `collectstatic` before deployment
- Monitor CSS file size (currently ~500 lines)

---

## Performance Optimization

### Current
- Static assets served via Django (dev)
- No minification
- No bundling

### Production Recommendations
- Use CDN for static files
- Minify CSS (`django-compressor`)
- Enable gzip compression
- Cache static assets (1 year)
- Use HTTP/2 for parallel loading

---

Happy building! 🎯


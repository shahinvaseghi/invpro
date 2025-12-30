---
description: "Mandatory adherence to DEVELOPMENT_GUIDE.md standards. No inline CSS/JS. Use shared files. Must check all files with standards_checker before commit."
alwaysApply: true
---

# Development Standards Compliance

**⚠️ CRITICAL**: All code must strictly follow the rules and standards defined in `DEVELOPMENT_GUIDE.md`.

## Mandatory Requirements

When writing any code in this project, you **MUST** follow all standards from `@DEVELOPMENT_GUIDE.md`:

### 🔴 Backend Standards

1. **Base Classes**: Always use Base Classes from `shared/views/base.py`
   - ❌ Never write ListView, CreateView, UpdateView, DeleteView, DetailView from scratch
   - ✅ Use `BaseListView`, `BaseCreateView`, `BaseUpdateView`, `BaseDeleteView`, `BaseDetailView`
   - ✅ Use `BaseFormsetCreateView`, `BaseFormsetUpdateView` for formsets
   - ✅ Use `BaseDocumentListView`, `BaseDocumentCreateView`, `BaseDocumentUpdateView` for documents

2. **Filter Functions**: Use shared filter functions from `shared/filters.py`
   - ✅ Use `apply_search()`, `apply_status_filter()`, `apply_company_filter()`, etc.
   - ❌ Never write custom filter/search logic in views

3. **Mixins**: Use shared mixins from `shared/mixins.py`
   - ✅ Use `PermissionFilterMixin`, `CompanyScopedViewMixin`, `AutoSetFieldsMixin`, etc.

4. **Forms**: Use `BaseModelForm` from `shared/forms/base.py`

### 🔴 Frontend Standards

1. **Generic Templates**: Always use Generic Templates
   - ✅ Use `generic_list.html` for List Views
   - ✅ Use `generic_form.html` for Create/Update Views
   - ✅ Use `generic_detail.html` for Detail Views
   - ✅ Use `generic_confirm_delete.html` for Delete Views
   - ❌ Never create new templates for standard CRUD operations

2. **Template Partials**: Use shared partials from `templates/shared/partials/`
   - ✅ Use `row_actions.html` for row action buttons
   - ✅ Use `pagination.html` for pagination
   - ✅ Use `filter_panel.html` for filter panels

3. **JavaScript**: Use shared JavaScript files from `static/js/`
   - ✅ Use `formset.js` for formset management
   - ✅ Use `cascading-dropdowns.js` for cascading dropdowns
   - ✅ Use `table-export.js` for table export
   - ❌ Never write inline JavaScript for common functionality

4. **CSS**: Use `shared.css` from `static/css/`
   - ❌ Never use inline styles or `<style>` tags
   - ✅ Use CSS classes from `shared.css`

### 🔴 Code Reusability & Shared Files

**CRITICAL RULE**: For any repetitive functionality, you **MUST** create shared/public files instead of duplicating code.

1. **No Inline Code**: Never write inline CSS, JavaScript, or HTML for common functionality
   - ❌ **FORBIDDEN**: `<style>...</style>` tags in templates
   - ❌ **FORBIDDEN**: `<script>...</script>` inline JavaScript in templates
   - ❌ **FORBIDDEN**: `style="..."` inline CSS attributes
   - ✅ **REQUIRED**: Create shared files in appropriate directories

2. **JavaScript Reusability**:
   - ✅ If functionality is used in 2+ places → Create shared JS file in `static/js/`
   - ✅ Reuse existing shared JS files (`formset.js`, `cascading-dropdowns.js`, etc.)
   - ✅ Create new shared file if needed: `static/js/your-feature.js`
   - ❌ Never duplicate JavaScript code across multiple templates

3. **CSS Reusability**:
   - ✅ If styles are used in 2+ places → Add to `static/css/shared.css`
   - ✅ Create CSS classes, not inline styles
   - ✅ Use existing CSS classes from `shared.css`
   - ❌ Never duplicate CSS rules in multiple templates

4. **Template Reusability**:
   - ✅ If template code is repeated → Create partial in `templates/shared/partials/`
   - ✅ Use `{% include %}` to reuse partials
   - ✅ Extend generic templates instead of copying code
   - ❌ Never duplicate template code

5. **Backend Reusability**:
   - ✅ If logic is used in 2+ views → Create shared function/class
   - ✅ Use existing Base Classes, Mixins, and Helper Functions
   - ✅ Create new shared utilities in `shared/utils/` if needed
   - ❌ Never duplicate business logic across views

6. **When to Create Shared Files**:
   - ✅ Functionality appears in 2+ places → **MUST** be shared
   - ✅ Common patterns (formsets, dropdowns, tables) → **MUST** use shared files
   - ✅ Repeated validation logic → **MUST** be in shared utilities
   - ✅ Repeated template patterns → **MUST** use partials or generic templates

7. **Shared File Locations**:
   ```
   static/js/              # Shared JavaScript files
   static/css/shared.css   # Shared CSS styles
   templates/shared/partials/  # Shared template partials
   templates/shared/generic/  # Generic templates
   shared/views/base.py    # Base view classes
   shared/filters.py       # Shared filter functions
   shared/mixins.py        # Shared mixins
   shared/utils/           # Shared utility functions
   shared/forms/base.py    # Base form classes
   ```

**Examples:**

```html
<!-- ❌ FORBIDDEN: Inline JavaScript -->
<script>
function addRow() {
    // 50 lines of code...
}
</script>

<!-- ✅ REQUIRED: Use shared file -->
{% load static %}
<script src="{% static 'js/formset.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    initFormset('formset', '#template-row');
});
</script>
```

```html
<!-- ❌ FORBIDDEN: Inline CSS -->
<div style="padding: 20px; margin: 10px; background: #fff;">
    Content
</div>

<!-- ✅ REQUIRED: Use shared CSS -->
<div class="container-fluid content-section">
    Content
</div>
```

```python
# ❌ FORBIDDEN: Duplicated logic in multiple views
class View1(ListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        # ... 30 more lines

class View2(ListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        # ... same 30 lines duplicated

# ✅ REQUIRED: Use shared function
from shared.filters import apply_search

class View1(BaseListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = apply_search(queryset, self.request.GET.get('search', ''), ['name'])
        return queryset

class View2(BaseListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = apply_search(queryset, self.request.GET.get('search', ''), ['name'])
        return queryset
```

### 🔴 Code Quality Standards

1. **Variable Naming**: Names must be logical, correct, and understandable
   - ✅ `userAccountBalance`, `isAuthenticated`, `maxRetryAttempts`
   - ❌ `x`, `temp`, `data`, `flag`, `val`

2. **Best Practices**: Follow language-specific best practices
   - ✅ Use `select_related()` for ForeignKey/OneToOne
   - ✅ Use `prefetch_related()` for ManyToMany/Reverse FK
   - ✅ Avoid N+1 queries
   - ✅ Use proper error handling

3. **Testing**: Write tests for new features
   - ✅ Unit tests for models, forms, utilities
   - ✅ Integration tests for views
   - ✅ Minimum 80% test coverage

4. **Security**: Follow security standards
   - ✅ Use ORM (no raw SQL with user input)
   - ✅ CSRF protection in all forms
   - ✅ Input validation and sanitization
   - ✅ Permission checking

5. **Documentation**: Document complex logic
   - ✅ Docstrings for functions/classes
   - ✅ Comments for complex business logic
   - ✅ Update README when needed

### 🔴 API Standards

1. **Response Format**: Use standard response format
   ```python
   {
       "status": "success",
       "data": {...},
       "message": "..."
   }
   ```

2. **HTTP Methods**: Use RESTful conventions
   - GET for retrieval
   - POST for creation
   - PUT/PATCH for updates
   - DELETE for deletion

3. **Error Handling**: Use standard error format
   ```python
   {
       "status": "error",
       "error": {
           "code": "ERROR_CODE",
           "message": "...",
           "details": {...}
       }
   }
   ```

### 🔴 Git Workflow

1. **Commit Messages**: Follow conventional commit format
   - ✅ `feat(module): description`
   - ✅ `fix(module): description`
   - ✅ `refactor(module): description`
   - ❌ Vague messages like "update" or "fix bug"

2. **Branching**: Follow branch naming conventions
   - ✅ `feature/feature-name`
   - ✅ `bugfix/bug-name`
   - ✅ `hotfix/issue-name`

### 🔴 Mandatory Standards Checker Validation

**CRITICAL RULE**: Every new or modified file **MUST** be checked with the standards checker before committing.

1. **After Creating/Modifying Any File**:
   - ✅ **REQUIRED**: Run standards checker on the file
   - ✅ **REQUIRED**: Fix all issues found before committing
   - ❌ **FORBIDDEN**: Committing files without checking

2. **How to Check Files**:

   **Method 1: Interactive Checker (Recommended)** ⭐
   ```bash
   cd standards_checker
   ./check_manual.sh
   # Select: "1. Manual Check" → Choose your file
   ```

   **Method 2: Direct Python Check**
   ```bash
   cd standards_checker
   python3 check_standards.py --file path/to/your/file.py
   ```

   **Method 3: Check Module**
   ```bash
   cd standards_checker
   python3 check_standards.py --module inventory
   ```

   **Method 4: Quick Check Script**
   ```bash
   cd standards_checker
   ./tools/check.sh
   # Checks staged files in git
   ```

3. **What Gets Checked**:
   - ✅ Base Classes usage (BaseListView, BaseCreateView, etc.)
   - ✅ Inline CSS/JavaScript detection
   - ✅ Code duplication
   - ✅ Variable naming standards
   - ✅ Security issues (SQL injection, hardcoded secrets)
   - ✅ Template standards
   - ✅ Documentation (docstrings)
   - ✅ Best practices compliance

4. **Fix Issues Before Commit**:
   - ✅ All **CRITICAL** issues must be fixed
   - ✅ All **ERROR** issues must be fixed
   - ⚠️ **WARNING** issues should be fixed (preferred) or documented
   - ℹ️ **INFO** issues can be addressed later

5. **Workflow**:
   ```
   1. Create/Modify file
   2. Run standards checker → cd standards_checker && ./check_manual.sh
   3. Review issues found
   4. Fix all CRITICAL and ERROR issues
   5. Re-check to verify fixes
   6. Commit only when all critical issues are resolved
   ```

6. **Standards Checker Location**:
   - Main checker: `standards_checker/check_standards.py`
   - Interactive checker: `standards_checker/interactive_checker_v2.py`
   - Quick launcher: `standards_checker/check_manual.sh`
   - Git integration: `standards_checker/tools/check.sh`

**Example**:
```bash
# After creating a new view file
cd standards_checker
./check_manual.sh
# Select: "1. Manual Check"
# Navigate to: inventory/views/new_view.py
# Review issues
# Fix all CRITICAL and ERROR issues
# Re-check
# Now safe to commit
```

**Remember**: Files with unresolved CRITICAL or ERROR issues will be rejected in code review.

## Pre-Commit Checklist

Before committing code, verify:

- [ ] **✅ MANDATORY: Ran standards checker on all new/modified files**
  - [ ] Used `./check_manual.sh` or `check_standards.py`
  - [ ] Fixed all CRITICAL issues
  - [ ] Fixed all ERROR issues
  - [ ] Reviewed and addressed WARNING issues
- [ ] Used Base Classes instead of writing from scratch
- [ ] Used Generic Templates instead of custom templates
- [ ] **NO inline CSS** - All styles in `shared.css` or separate CSS files
- [ ] **NO inline JavaScript** - All JS in `static/js/` shared files
- [ ] **NO code duplication** - Repeated functionality uses shared files
- [ ] Created shared files for functionality used in 2+ places
- [ ] Used existing shared files instead of writing new code
- [ ] Variable names are logical and understandable
- [ ] Followed Django best practices
- [ ] Added proper error handling
- [ ] Added tests for new features
- [ ] Security standards are followed
- [ ] Documentation is updated

## Reference

For complete details, refer to: `@DEVELOPMENT_GUIDE.md`

**Remember**: Code that doesn't follow these standards will be rejected in code review.


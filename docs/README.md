# Documentation Directory

This directory contains all project documentation files organized by topic and purpose.

## 📚 Main Documentation

### Core Documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[UI_UX_CHANGELOG.md](UI_UX_CHANGELOG.md)** - **Detailed UI/UX design improvements and changelog**
- **[FEATURES.md](FEATURES.md)** - Complete feature list and capabilities
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guidelines, workflows, and best practices

### Technical Documentation
- **[DATABASE_DOCUMENTATION.md](DATABASE_DOCUMENTATION.md)** - Database schema, tables, and relationships
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API endpoints documentation for all modules
- **[MODULE_DEPENDENCIES.md](MODULE_DEPENDENCIES.md)** - Module dependencies and optional features handling
- **[system_requirements.md](system_requirements.md)** - System requirements and deployment guide
- **[ui_guidelines.md](ui_guidelines.md)** - UI/UX guidelines and component documentation
- **[TEMPLATE_TAGS.md](TEMPLATE_TAGS.md)** - Template tags and filters documentation (Jalali dates, permissions, JSON)
- **[BASE_CLASSES_MIXINS.md](BASE_CLASSES_MIXINS.md)** - Base classes and mixins documentation for views and forms

### Workflow Documentation
- **[approval_workflow.md](approval_workflow.md)** - Approval workflow reference for purchase requests, warehouse requests, and stocktaking records

## 🗄️ Module Design Plans

Detailed database design specifications for each module:

- **[shared_module_db_design_plan.md](shared_module_db_design_plan.md)** - Shared module database design
- **[inventory_module_db_design_plan.md](inventory_module_db_design_plan.md)** - Inventory module database design
- **[production_module_db_design_plan.md](production_module_db_design_plan.md)** - Production module database design
- **[qc_module_db_design_plan.md](qc_module_db_design_plan.md)** - Quality Control module database design

## 📝 Other Files

- **[PR_DESCRIPTION.md](PR_DESCRIPTION.md)** - Pull request template and guidelines

## 📖 How to Navigate

1. **New to the project?** Start with the main [README.md](../README.md) in the project root
2. **Setting up development?** Check [DEVELOPMENT.md](DEVELOPMENT.md)
3. **Need to understand features?** See [FEATURES.md](FEATURES.md)
4. **Deploying to production?** Read [system_requirements.md](system_requirements.md)
5. **Working on UI?** Review [ui_guidelines.md](ui_guidelines.md)
6. **Database changes?** Consult [DATABASE_DOCUMENTATION.md](DATABASE_DOCUMENTATION.md) and the relevant module design plan

## 🔄 Recent Updates

All documentation has been updated to reflect:
- Removal of `Person` model from inventory module - all requests now use Django `User` model
- Enhanced sidebar navigation with modern styling
- Complete Persian (Farsi) translations
- User management form fixes (groups and superuser status)
- Entity Reference System implementation with Section Registry and Action Registry tables
- **Important**: New section/feature workflow requires Access Level permission configuration

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## ⚠️ Important: New Section Development Workflow

**CRITICAL**: When creating any new section or feature in the application, the following steps are **mandatory**:

1. **Register in Entity Reference System**:
   - Add section to `SectionRegistry` table
   - Add all actions to `ActionRegistry` table
   - See [Entity Reference System Documentation](ENTITY_REFERENCE_SYSTEM.md) for details

2. **Define Feature Permissions**:
   - Add feature code to `FEATURE_PERMISSION_MAP` in `shared/permissions.py`
   - Define all supported actions (view, create, edit, delete, approve, etc.)

3. **⚠️ Configure Access Level Permissions (MANDATORY)**:
   - Go to `/shared/access-levels/` in the application
   - Create or edit Access Levels that should have access to the new section
   - Enable appropriate permissions for the new section
   - **Without this step, users will NOT be able to access the new section, even if it appears in the sidebar**

4. **Assign Access Levels**:
   - Assign the configured Access Levels to appropriate users or groups

For detailed step-by-step instructions, see:
- [Development Guide](DEVELOPMENT.md#creating-new-features)
- [Entity Reference System Documentation](ENTITY_REFERENCE_SYSTEM.md#adding-new-sections-and-actions)

## 📂 Module-Specific Documentation

For detailed documentation about each module, check the README files in their respective directories:
- `shared/README.md` - Shared module overview (includes context processors, utils, templatetags)
- `shared/README_FORMS.md` - Shared module forms
- `inventory/README.md` - Inventory module overview (includes base classes, mixins, API endpoints, management commands)
- `inventory/README_FORMS.md` - Inventory module forms
- `inventory/README_BALANCE.md` - Inventory balance calculation
- `production/README.md` - Production module overview
- `production/README_BOM.md` - BOM (Bill of Materials) system documentation
- `production/README_FORMS.md` - Production module forms
- `qc/README.md` - Quality Control module overview
- `ui/README.md` - UI module overview
- `templates/inventory/README.md` - Inventory module templates documentation

---

**Note**: All documentation is maintained in English with Persian (Farsi) support where applicable.


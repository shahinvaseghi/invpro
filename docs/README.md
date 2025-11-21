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
- **[system_requirements.md](system_requirements.md)** - System requirements and deployment guide
- **[ui_guidelines.md](ui_guidelines.md)** - UI/UX guidelines and component documentation

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

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 📂 Module-Specific Documentation

For detailed documentation about each module, check the README files in their respective directories:
- `shared/README.md` - Shared module overview
- `shared/README_FORMS.md` - Shared module forms
- `inventory/README.md` - Inventory module overview
- `inventory/README_FORMS.md` - Inventory module forms
- `inventory/README_BALANCE.md` - Inventory balance calculation
- `production/README.md` - Production module overview
- `qc/README.md` - Quality Control module overview
- `ui/README.md` - UI module overview

---

**Note**: All documentation is maintained in English with Persian (Farsi) support where applicable.


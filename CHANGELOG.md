# Changelog

All notable changes to the invproj platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Multi-company architecture with session-based company switching
- Company selector dropdown in header (alongside language switcher)
- Default company support for users
- Context processor for active company injection into templates
- Custom CRUD forms for inventory master data:
  - ItemTypeForm (انواع کالا)
  - ItemCategoryForm (دسته‌بندی)
  - ItemSubcategoryForm (زیردسته‌بندی/کاتالوگ)
  - WarehouseForm (انبار)
- Custom CRUD forms for shared entities:
  - CompanyForm with automatic UserCompanyAccess creation
  - PersonForm with username sync checkbox feature و انتخاب چند واحد سازمانی
- Generic reusable templates for forms and delete confirmations
- Comprehensive form documentation (README_FORMS.md for inventory and shared)
- Persian/English internationalization (i18n) with full RTL support
- Language switcher in header
- Compiled translation files (django.po/django.mo for Persian)
- Inventory balance calculation logic (inventory_balance.py)
- WarehouseRequest model for internal material requests
- Delete functionality with confirmation pages for all entities
- Auto-population of created_by and edited_by fields
- Breadcrumb navigation across all modules
- Consistent status badges (Active/Inactive)
- Empty state messages with actionable buttons
- Edit and Delete buttons in all list views
- امکان تخصیص پرسنل به چند واحد سازمانی و نمایش واحدها در فهرست پرسنل
- Centralised permission catalog (`shared/permissions.py`) with granular actions (view own/all, create, edit/delete own, lock/unlock, approve/reject/cancel)
- Placeholder navigation pages for Users, Groups, Access Levels (under Shared menu) ahead of full CRUD implementation
- Full user/group/access level management UI under Shared module:
  - User CRUD with group assignment and company-access formset
  - Group CRUD backed by `GroupProfile` (description, enabled flag, access level linkage, member selection)
  - Access level CRUD with feature/action matrix driven by `FEATURE_PERMISSION_MAP`
- Dedicated stocktaking document pages (deficit, surplus, record) with auto code generation, item-aware unit/warehouse filtering, locking controls, and shared stocktaking form template
- Dedicated purchase request workspace with locking, approver routing, and automatic exposure in permanent/consignment receipts after approval
- Dedicated warehouse request workspace with item-aware unit/warehouse filtering, approver routing, and automatic exposure in permanent/consignment receipts after approval
- **Multi-line document support** for Issue and Receipt documents:
  - Converted `IssuePermanent`, `IssueConsumption`, `IssueConsignment`, `ReceiptPermanent`, `ReceiptConsignment` to header-only documents
  - Created line item models: `IssuePermanentLine`, `IssueConsumptionLine`, `IssueConsignmentLine`, `ReceiptPermanentLine`, `ReceiptConsignmentLine`
  - Each line can have its own item, quantity, warehouse, unit, and pricing information
  - Users can add/remove multiple lines dynamically in document forms
- **Line-based serial assignment**:
  - Serial numbers are now managed at the line item level, not document level
  - Each line with a lot-tracked item has a dedicated serial assignment page
  - Serial generation for receipt lines with format `{DOC_CODE}-L{LINE_ID}-{SEQUENCE:04d}`
  - Serial reservation and finalization for issue lines
  - Validation ensures serial count matches line quantity before document lock
  - New views: `IssueLineSerialAssignmentBaseView`, `ReceiptLineSerialAssignmentBaseView` and their concrete implementations
  - New services: `generate_receipt_line_serials()`, `sync_issue_line_serials()`, `finalize_issue_line_serials()`
- Line formsets for managing multiple line items in document forms
- `LineFormsetMixin` for reusable line formset handling in views
- Updated document lock views to validate and finalize serials for all lines
- **Strict warehouse restrictions (allowed warehouses)**:
  - Items can only be received/issued in warehouses explicitly configured in `ItemWarehouse` relationship
  - Validation enforced in forms (server-side and client-side)
  - JavaScript dynamically updates warehouse dropdown when item changes
  - API endpoint: `/inventory/api/item-allowed-warehouses/?item_id=X`
  - Error messages if warehouse not allowed or no warehouses configured
- **Jalali date display**:
  - All dates displayed in Jalali (Persian) format in UI while stored in Gregorian format in database
  - Custom `JalaliDateField` and `JalaliDateInput` widget
  - Template tags `jalali_tags` for displaying dates in templates
  - Automatic conversion on input/output
  - Applied to all document forms (receipts, issues, purchase requests, warehouse requests)
- **Access Level permission matrix UI enhancements**:
  - Added "Select All" and "Deselect All" buttons for each feature row
  - Added global "Select All" and "Deselect All" buttons for the entire permission matrix
  - Quick action buttons allow bulk selection/deselection of permissions per feature
  - JavaScript-based functionality for efficient permission management
- **Enhanced permission actions**:
  - Added `DELETE_OTHER` permission action to all document types (receipts, issues, requests, stocktaking)
  - Added `APPROVE` permission to stocktaking records (previously missing)
  - Added `EDIT_OTHER` permission action to PermissionAction enum
  - All document resources now support deletion of other users' documents when `DELETE_OTHER` permission is granted
  - Stocktaking records now support approval workflow with `APPROVE` permission
- **Document deletion functionality**:
  - Added delete functionality for all document types (receipts, issues, stocktaking records)
  - Created `DocumentDeleteViewBase` class for unified delete view implementation with permission checking
  - Implemented delete views for:
    - Receipt types: Temporary, Permanent, Consignment
    - Issue types: Permanent, Consumption, Consignment
    - Stocktaking types: Deficit, Surplus, Records
  - Delete buttons conditionally displayed in list views based on user permissions (`DELETE_OWN` and `DELETE_OTHER`)
  - Permission-based access control: users can delete their own documents with `DELETE_OWN` permission, or any document with `DELETE_OTHER` permission
  - Superuser bypass: superusers can delete any document without explicit permission assignment
  - Document lock protection: locked documents cannot be deleted (enforced by `DocumentLockProtectedMixin`)
  - Confirmation templates created for all document types with detailed information display
  - Helper method `add_delete_permissions_to_context()` added to `InventoryBaseView` for consistent permission checking across list views
- **Inventory balance details page**:
  - New view `InventoryBalanceDetailsView` to display detailed transaction history for items
  - Shows all receipts and issues from baseline date to selected date
  - Displays running balance calculation for each transaction
  - Accessible via "Details" button next to each item in inventory balance report
- **Document form validation improvements**:
  - Auto-population of `document_date` and `document_code` fields in Issue and Receipt forms
  - Added `clean_document_date()` and `clean_document_code()` methods to ensure fields are always populated
  - Prevents form submission failures due to missing auto-generated fields

### Changed
- Removed `activated_at` and `deactivated_at` fields from ActivatableModel
- Made `created_by` and `edited_by` auto-populated (not user-selectable)
- Updated Company.public_code from 8 to 3 digits
- Updated CompanyUnit.public_code from 6 to 5 digits
- Updated WorkCenter.public_code to 5 digits
- Updated Item code structure:
  - item_code: 7 digits (User 2 + Sequence 5)
  - full_item_code: 16 digits (Type 3 + Category 3 + SubCategory 3 + ItemCode 7)
- Standardized all forms to use consistent CSS classes
- Moved "Work Lines" from Inventory module to Production module in sidebar
- **Refactored Issue and Receipt models to header-only architecture**:
  - Removed `item`, `warehouse`, `quantity`, `unit` fields from document models
  - These fields are now managed by line item models
  - Document models now only contain header-level information
- **Updated serial assignment workflow**:
  - Serials are now linked to line items via `ManyToManyField`
  - Serial assignment pages work with specific line items, not entire documents
  - `ItemSerial.current_document_type` and `current_document_id` now reference line models
- **IssueConsignmentLine model**:
  - Made `consignment_receipt` and `consignment_receipt_code` fields optional (`null=True, blank=True`)
  - Consignment issues can now be created independently without requiring a consignment receipt
- **StocktakingRecord model**:
  - Changed `confirmed_by` and `approver` foreign keys from `Person` to `User` model
  - Updated `confirmed_by_code` to use `username` instead of `public_code`
  - Enables proper user-based approval workflow
- **Group form**:
  - Removed `members` field from Group form (membership now managed via User form)
  - Changed `access_levels` widget from `SelectMultiple` to `CheckboxSelectMultiple` for better UX
  - Users can now select multiple access levels simultaneously
- **User form**:
  - Changed `groups` widget from `SelectMultiple` to `CheckboxSelectMultiple` for better UX
  - Users can now be assigned to multiple groups simultaneously
- **StocktakingRecord form**:
  - Added `approval_status` field as `ChoiceField` with three options: pending, approved, rejected
  - Reordered fields: `approver` now appears before `approval_status`
  - `approved_at` field automatically set/cleared based on `approval_status`
  - Only the designated `approver` can change `approval_status` (enforced client-side and server-side)
- **Document list views**:
  - Added `ordering = ['-id']` to `IssueConsumptionListView`, `IssueConsignmentListView`, `IssuePermanentListView`, and `StocktakingRecordListView`
  - Lists now display newest documents first
- **Inventory balance calculation**:
  - Modified `calculate_movements_after_baseline()` to query line item models instead of header models
  - Now includes `IssueConsignmentLine` in issues calculation
  - Removed `is_locked=1` filter, now only checks `document__is_enabled=1`
  - Improved baseline detection: uses `StocktakingSurplus`/`StocktakingDeficit` first, then falls back to approved and locked `StocktakingRecord`
  - `calculate_warehouse_balances()` now includes items with actual transactions, not just explicit warehouse assignments
- **Inventory balance UI**:
  - Hidden "As of Date" input field (automatically set to today's date)
  - Baseline date now displayed in Jalali format using `|jalali_date` filter

### Fixed
- Language switcher error resolved
- Company selector not appearing (fixed URL patterns)
- Translations missing for many UI elements
- Form field names corrected (ItemSubcategory uses 'category' not 'item_category')
- Warehouse form field corrected (no 'location' field in model)
- Template block names corrected (inventory_content instead of module_content)
- Duplicate translation entries removed from django.po
- URL namespacing issues resolved for company switching
- **IssueConsumption form submission**:
  - Fixed form not submitting due to missing `document_date` validation
  - Added automatic population of `document_date` and `document_code` fields
  - Form now successfully saves consumption issues
- **IssueConsignment form submission**:
  - Fixed form not submitting due to missing `document_date` validation
  - Added automatic population of `document_date` and `document_code` fields
  - Form now successfully saves consignment issues
- **IssueConsignment consignment_receipt requirement**:
  - Fixed `IntegrityError` when creating consignment issues without a receipt
  - Made `consignment_receipt` field optional in model and form
  - Applied database migration to make columns nullable
- **Inventory balance not displaying items**:
  - Fixed calculation querying header models instead of line item models
  - Fixed missing `IssueConsignmentLine` in issues calculation
  - Fixed baseline detection to properly use `StocktakingRecord` when surplus/deficit documents don't exist
  - Fixed warehouse balance calculation to include items with actual transactions
  - Inventory balance now correctly displays all items with transactions
- **StocktakingRecord form FieldError**:
  - Fixed `Cannot resolve keyword 'usercompanyaccess' into field` error
  - Corrected queryset filter from `usercompanyaccess__company_id` to `company_accesses__company_id`
  - Form now correctly filters users by company access
- **Group form multiple access level selection**:
  - Fixed inability to select multiple access levels simultaneously
  - Changed widget to `CheckboxSelectMultiple` for better user experience
- **Inventory balance date input**:
  - Fixed Gregorian calendar display in date input field
  - Changed to hidden field with automatic date population (today's date)
  - Baseline date now displays in Jalali format

### Security
- Company data isolation enforced via session-based filtering
- Users can only access companies they have explicit permission for
- Personnel records scoped to active company
- QuerySet filtering by company_id in all views

---

## [0.1.0] - Initial Release

### Added
- Django 4.2 project structure
- PostgreSQL database support
- Multi-company (multi-tenant) architecture
- Shared module with:
  - Custom User model
  - Company model
  - Person model
  - AccessLevel and UserCompanyAccess models
- Inventory module with:
  - ItemType, ItemCategory, ItemSubcategory models
  - Item model with dynamic code generation
  - Warehouse model
  - Supplier and SupplierCategory models
  - Receipt models (Temporary, Permanent, Consignment)
  - Issue models (Permanent, Consumption, Consignment)
  - Stocktaking models (Record, Deficit, Surplus)
  - PurchaseRequest model
- Production module with:
  - WorkCenter model
  - WorkLine model
  - BOM (Bill of Materials) support
- QC module foundation
- UI module with:
  - Dashboard template
  - Navigation sidebar
  - Base templates
- Common model mixins:
  - TimeStampedModel (created_at, updated_at)
  - ActivatableModel (is_enabled)
  - SortableModel (sort_order)
  - MetadataModel (metadata JSON field)
  - CompanyScopedModel (company foreign key)
- Admin interface for all models
- Environment configuration via django-environ
- Database migration system
- Static files setup

### Documentation
- Main README.md with architecture overview
- inventory_module_db_design_plan.md
- ui_guidelines.md
- Module-specific README files
- Code comments and docstrings

---

## Future Versions

### Planned for v0.2.0
- API layer with Django REST Framework
- Barcode/QR code scanning support
- File attachments for documents
- Email/SMS notifications
- Excel/CSV import/export
- Advanced filtering and search
- Audit log viewer
- Role-based permissions enforcement

### Planned for v0.3.0
- Advanced reporting and analytics
- Dashboard widgets
- Real-time production monitoring
- Mobile-optimized UI
- Bulk operations
- Template customization

### Planned for v0.4.0
- Integration with external ERPs
- Automated backup system
- Advanced workflow engine
- Custom report builder
- Multi-warehouse transfer support
- Batch/lot tracking enhancements


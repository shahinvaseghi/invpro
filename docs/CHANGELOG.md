# Changelog

All notable changes to the invproj platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **Secondary Batch Number for Items**: Added optional `secondary_batch_number` field to `Item` model allowing users to define a custom secondary batch number in addition to the auto-generated batch number. This field is displayed in the item definition form and can be used for external batch tracking.
- **Secondary Serial Number for Item Serials**: Added optional `secondary_serial_code` field to `ItemSerial` model allowing users to define a custom secondary serial number in addition to the auto-generated serial code. This field can be managed on the serial assignment page during receipt creation and updated via API endpoint `/inventory/api/update-serial-secondary-code/`.
- **Inventory Balance Validation in Issue Forms**: Added validation to prevent issuing more items than available inventory. The system now checks current balance before allowing issue creation/editing, and displays an error message if insufficient inventory is available.

### Changed
- **Issue Forms Destination Type**: 
  - **Permanent Issues**: Changed `destination_type` field from `WorkLine` to `CompanyUnit` (optional). Only organizational units can be selected as destination.
  - **Consignment Issues**: Changed `destination_type` field from `WorkLine` to `CompanyUnit` (optional). Only organizational units can be selected as destination.
  - **Consumption Issues**: Remains unchanged - supports both `CompanyUnit` and `WorkLine` selection via `destination_type_choice` field.
- **JavaScript Form Validation**: Updated validation logic to only check `destination_type_choice` for Consumption Issues. For Permanent/Consignment Issues, `destination_type` is optional and validation is skipped if the field doesn't exist.

### Changed
- **Removed Debug Logging**: Cleaned up all temporary debug logging code from:
  - `inventory/views.py` - Removed all logger.debug/info/warning/error calls (including ItemCreateView and IssueConsumptionView)
  - `inventory/forms.py` - Removed all logger.debug calls
  - `production/views.py` - Removed all logger.debug/info/warning/error calls and unused import logging
  - `production/forms.py` - Removed all logger.debug calls and unused import logging
  - `templates/inventory/item_form.html` - Removed console.log calls (kept essential error handling)
  - `templates/inventory/receipt_form.html` - Removed all console.log/warn calls (66 instances, kept console.error for error handling)
  - `templates/production/bom_form.html` - Removed localStorage logging, debug logs section, and console.log/warn calls (kept console.error for error handling)
- **Logging Configuration**: Simplified LOGGING configuration in `config/settings.py` - removed DEBUG level loggers for inventory and production modules
- **Code Cleanup**: Removed all temporary debugging code added during development and bug fixing to improve code maintainability

### Fixed
- **Item Form Subcategory Filtering**: Fixed issue where subcategories were not properly filtered by category
  - Updated `get_filtered_subcategories` API to return all subcategories for a category (not just those with items)
  - Added JavaScript cascading dropdown logic to filter subcategories when category changes
  - Subcategories now properly clear and reload when category selection changes

---

## [2025-11-20c] - BOM Form Validation & Edit Mode Fixes

### Fixed
- **`is_optional` Validation Error**:
  - Changed `is_optional` field from `IntegerField` to `BooleanField` in form
  - Added `clean_is_optional()` method to convert checkbox Boolean value (True/False) to integer (1/0) for database storage
  - Fixed validation error "Enter a whole number" when checkbox was unchecked
  - Checkbox now properly saves as 0 (required) when unchecked or 1 (optional) when checked

- **Unit Field Clearing on Form Submit**:
  - Fixed issue where unit dropdown values were not being submitted when field was disabled
  - Added JavaScript code to enable all unit selects before form submission
  - Disabled fields are not included in form submission, causing unit values to be lost
  - Unit values now properly restore after validation errors or page reload

- **`extra_form_count()` AttributeError in Create View**:
  - Fixed `AttributeError: 'BOMMaterialFormFormSet' object has no attribute 'extra_form_count'`
  - Added check for method existence using `hasattr()`
  - Fallback to calculated value: `total_form_count() - initial_form_count()`
  - Added try/except block for better error handling

- **Values Not Restoring in Edit Mode**:
  - Fixed issue where category, subcategory, and unit values were not restored when editing existing BOM
  - Enhanced `get_item_units` API to return `category_id` and `subcategory_id` in addition to `item_type_id`
  - Added JavaScript logic to restore all values (type, category, subcategory, unit) on page load in edit mode
  - Material lines now properly display previously selected values when editing BOM

### Changed
- **Enhanced `get_item_units` API Response**:
  - Now returns `category_id` and `subcategory_id` along with existing `item_type_id`, `item_type_name`, and `units`
  - Response structure:
    ```json
    {
      "units": [...],
      "item_type_id": "1",
      "item_type_name": "خام",
      "category_id": "3",
      "subcategory_id": "2"
    }
    ```
  - Allows single API call to restore all related values in edit mode

- **BOMMaterialLineForm.is_optional Field**:
  - Changed from `IntegerField` to `BooleanField` with `CheckboxInput` widget
  - Added `clean_is_optional()` method for Boolean → Integer conversion
  - Removed `is_optional` from `Meta.widgets` as it's now defined explicitly

- **JavaScript Form Submission Handler**:
  - Added code to enable all disabled unit selects before form submission
  - Ensures all unit values are included in POST data
  - Logs unit values prominently for debugging

- **JavaScript Page Load Handler**:
  - Added comprehensive value restoration logic for edit mode
  - Restores material_type, category, subcategory, and unit from item selection
  - Uses cascading API calls to populate dropdowns in correct order
  - Handles timing issues with setTimeout for sequential dropdown population

### Technical Details
- **Form Field Type Change**: `is_optional` uses `BooleanField` in form but stores as `PositiveSmallIntegerField(0/1)` in database
- **API Enhancement**: `get_item_units` endpoint now includes category/subcategory for easier edit mode restoration
- **Validation Timing**: `clean_is_optional()` runs after Django's default checkbox handling, converting to integer format

---

## [2025-11-20b] - BOM Enhanced Cascading Filters & Unit Management

### Added
- **New Inventory API Endpoints for BOM Cascading Filters**:
  - `get_filtered_categories()`: Returns categories that contain at least one item of specified type
  - `get_filtered_subcategories()`: Returns subcategories filtered by type and/or category
  - `get_filtered_items()`: Returns items filtered by type, category, and subcategory
  - All APIs respect company scope and only return enabled (is_enabled=1) items
  
- **Enhanced BOM Material Line Form**:
  - `material_category_filter`: New filter field (ModelChoiceField) for Category selection
  - `material_subcategory_filter`: New filter field (ModelChoiceField) for Subcategory selection
  - Cascading flow: Type → Category → Subcategory → Item → Unit
  - Each filter only shows options that contain items matching previous selections
  
- **Primary Unit Support in BOM**:
  - `get_item_units()` API now includes item's `primary_unit` as first option
  - Primary unit labeled as "واحد اصلی" (Base Unit) in dropdown
  - Format: `{unit_name} (واحد اصلی)` for primary unit
  - Conversion units follow with conversion ratio in label
  
- **Master Data Menu in Top Navigation**:
  - Added "Master Data" submenu under Inventory in top navbar
  - Links to Item Types, Item Categories, Item Subcategories
  - Permission-based visibility for each submenu item
  
- **JavaScript Cascading Functions for Material Lines**:
  - `filterCategories(typeSelect, idx)`: Populates category dropdown based on type
  - `filterSubcategories(categorySelect, idx)`: Populates subcategory dropdown based on type+category
  - `filterItems(subcategorySelect, idx)`: Populates item dropdown based on type+category+subcategory
  - `loadItemUnits(itemSelect, idx)`: Populates unit dropdown with primary_unit + conversion units
  - Each material line operates independently with its own index
  
### Changed
- **BOMMaterial.material_type Field**:
  - Changed from `CharField` with hardcoded choices to `ForeignKey` to `inventory.ItemType`
  - Now uses user-defined item types instead of system-defined list
  - Provides flexibility for different material classification schemes per company
  - Updated form to use `ModelChoiceField` populated from `ItemType.objects.filter(company=...)`
  
- **BOMMaterial.unit Field**:
  - Changed from `ForeignKey` to `inventory.ItemUnit` back to `CharField(max_length=30)`
  - Reason: Item's `primary_unit` is stored as string field, not as ItemUnit object
  - Now stores unit name (string) which can be either primary_unit or conversion unit name
  - Form uses `ChoiceField` populated dynamically from `get_item_units` API
  - Unit dropdown disabled until item is selected
  
- **BOM Form UX Improvements**:
  - Material type dropdown now populated from database (ItemType)
  - Category/Subcategory filters intelligently show only relevant options
  - Reduced dropdown clutter by filtering out empty categories/subcategories
  - Unit selection now includes base unit prominently as first option
  
- **API Response Format**:
  - `get_item_units` now returns array with structure:
    ```json
    {
      "units": [
        {"value": "base_kg", "label": "کیلوگرم (واحد اصلی)", "is_base": true, "unit_name": "کیلوگرم"},
        {"value": "gram", "label": "گرم (1 کیلوگرم = 1000 گرم)"}
      ]
    }
    ```
  - Base unit prefixed with "base_" to distinguish from conversion units
  
### Fixed
- **Unit Dropdown Not Showing Base Unit**:
  - Fixed `get_item_units` API to read from `item.primary_unit` instead of non-existent `item.base_unit`
  - Fixed `BOMMaterialLineForm.__init__` to use `item.primary_unit`
  - Now correctly displays both primary unit and conversion units
  
- **Categories/Subcategories Showing Empty Options**:
  - Fixed API queries to use `.filter(items__type_id=...).distinct()` 
  - Only returns categories/subcategories that actually contain items of selected type
  - Eliminates confusion from seeing empty options in cascading dropdowns
  
- **UI/CSS Box Overlap in BOM Form**:
  - Adjusted CSS grid layout in `bom_form.html`
  - Changed to `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`
  - Added `gap: 1.5rem` for proper spacing
  - Fixed responsive behavior on smaller screens

### Documentation
- **Updated production/README_BOM.md**:
  - Documented new `material_type` as ForeignKey to ItemType
  - Added API Endpoints section with all 4 new APIs
  - Updated JavaScript section with cascading filter functions
  - Clarified `unit` field as CharField storing unit names
  - Added details about primary_unit vs conversion units
  
- **Updated production/README_FORMS.md**:
  - Enhanced BOMMaterialLineForm documentation
  - Documented `material_category_filter` and `material_subcategory_filter` fields
  - Added complete cascading behavior flow (5 steps)
  - Documented all JavaScript cascading functions with code examples
  - Added API endpoint references
  - Clarified that filter fields are not saved to database
  
- **Updated locale/fa/LC_MESSAGES/django.po**:
  - Added translations: "Master Data", "Category", "Subcategory"
  - Added loading messages: "Loading categories...", "Loading items..."
  - Added error messages for cascading filter failures
  - Compiled with `compilemessages`

### Database Migrations
- **0009_bom_material_type_to_fk.py**: Changed `BOMMaterial.material_type` to ForeignKey(ItemType)
- **0010_bom_unit_to_fk.py**: Changed `BOMMaterial.unit` to ForeignKey(ItemUnit) - later reverted
- **0011_bom_unit_back_to_char.py**: Reverted `BOMMaterial.unit` back to CharField to support primary_unit

### Technical Notes
- **Why CharField for unit?**: 
  - Item's primary_unit is a CharField, not a foreign key
  - ItemUnit model only covers conversion units (e.g., kg→gram)
  - To support both primary and conversion units, we store the unit name as string
  - Form validation ensures the unit name matches either primary_unit or exists in ItemUnit
  
- **Cascading Filter Independence**:
  - Each material line in the formset has its own set of cascading filters
  - JavaScript uses row index (idx) to target correct dropdowns
  - No interference between different material lines
  - Allows different material types in same BOM
  
- **Performance Consideration**:
  - Filtered APIs use `.distinct()` to avoid duplicate entries
  - Queries optimized to check `items__type_id` directly without loading all items
  - Company scope filter applied at database level
  - Only enabled items (is_enabled=1) are considered

---

## [2025-11-20] - BOM Module Implementation

### Added
- **BOM (Bill of Materials) Complete Implementation**:
  - Header-Line Architecture: `BOM` model (header) and `BOMMaterial` model (lines)
  - Version control for BOMs with unique constraint on (company, finished_item, version)
  - Auto-generated 16-digit `bom_code` per company using sequential code generation
  - Material type classification: Raw, Semi-Finished, Component, Packaging
  - Scrap allowance percentage (0-100%) for waste calculation
  - Optional/Required material flags
  - Effective/Expiry date tracking for BOM validity
  - Active/Inactive status management
  - Complete CRUD views: List, Create, Update, Delete
  - Permissions: `production.bom` with view_all, create, edit_own, delete_own actions

- **BOM Forms**:
  - `BOMForm`: Header form with cascading filters (Type → Category → Item) for finished product selection
  - `BOMMaterialLineForm`: Material line form with cascading filters for material and unit selection
  - `BOMMaterialLineFormSet`: Django inline formset with dynamic add/remove functionality
  - Minimum 1 material line validation
  - Company-scoped dropdowns to ensure data isolation
  - Unit validation to ensure selected unit belongs to selected material

- **BOM Templates**:
  - `bom_list.html`: List view with expand/collapse material details, filter by finished item
  - `bom_form.html`: Multi-section form with:
    - Finished product selection section with cascading dropdowns
    - Dynamic material lines table with JavaScript add/remove functionality
    - Material type badges with color coding (Raw=Blue, Semi-Finished=Yellow, Component=Green, Packaging=Red)
    - Line numbering and TOTAL_FORMS management
    - Form validation with Persian error messages
  - `bom_confirm_delete.html`: Delete confirmation with material count display

- **JavaScript Features**:
  - Dynamic formset line addition with automatic field name/id updating
  - Line removal with minimum 1 line validation
  - Auto-increment line numbers
  - TOTAL_FORMS counter management
  - Cascading dropdown filtering for both finished item and materials
  - Client-side form validation before submission

- **Database Migrations**:
  - `0006_bom_restructure.py`: Custom migration to restructure BOM from single-model to header-line architecture
  - Drops old `BOMMaterial` table and creates new `BOM` and `BOMMaterial` tables
  - `0007_*.py`: Auto-generated migration for ProductionBaseModel fields

- **Production Module Enhancements**:
  - Transfer to Line Requests placeholder (`/production/transfer-requests/`)
  - Performance Records placeholder (`/production/performance-records/`)
  - Updated sidebar menu with BOM link and permission checks
  - Sidebar sections now collapsed by default (user can expand as needed)

- **Documentation**:
  - `production/README_BOM.md`: Complete 500+ line documentation covering:
    - BOM architecture and database schema
    - Model field descriptions and methods
    - Form structure and validation
    - View implementation details
    - Template and JavaScript functionality
    - Permission system
    - Usage instructions with examples
    - Practical BOM examples (office chair, L-shaped desk)
    - Material calculation examples
    - Migration history
  - Updated `production/README.md` with BOM section and automatic code generation details
  - Updated `production/README_FORMS.md` with BOMForm, BOMMaterialLineForm, and BOMMaterialLineFormSet documentation
  - Updated main `README.md` with comprehensive BOM feature description

- **Persian Translations**:
  - All BOM-related terms translated to Persian
  - Form labels, field names, error messages
  - Material type choices
  - Success/error messages
  - Compiled translations with `compilemessages`

### Changed
- **BOM Model Architecture**: Completely redesigned from single-model to header-line structure
  - Old: `BOMMaterial` standalone model with `finished_item` FK
  - New: `BOM` header model + `BOMMaterial` line model with `bom` FK
  - Enables multiple BOM versions per finished item
  - Better data organization and version control
  - CASCADE delete for material lines when parent BOM is deleted

- **Sidebar Navigation**:
  - All sections now collapsed by default on page load
  - User state saved in localStorage but defaults to collapsed if no state exists
  - Provides cleaner initial view and user control over menu visibility

- **Permission System**:
  - Added `production.bom` to `FEATURE_PERMISSION_MAP` with full CRUD actions

- **Admin Interface**:
  - Added `BOMAdmin` with list display, filters, and search
  - Added `BOMMaterialInline` for inline material editing
  - Updated `BOMMaterialAdmin` to reflect new model structure

### Fixed
- Resolved migration conflicts when introducing BOM header-line architecture
- Fixed duplicate msgid entries in `locale/fa/LC_MESSAGES/django.po`
- Corrected cascading dropdown filtering in BOM forms
- Fixed TOTAL_FORMS management in dynamic formset
- Resolved unit validation to ensure unit belongs to selected material item

### Technical Details
- **Database Constraints**:
  - UniqueConstraint on (company, finished_item, version) for BOM
  - UniqueConstraint on (bom, material_item, line_number) for BOMMaterial
  - Foreign key protections (PROTECT for items, CASCADE for materials)

- **Code Generation**:
  - `BOM.bom_code`: 16-digit sequential per company
  - `BOM.finished_item_code`: Cached from finished_item
  - `BOMMaterial.material_item_code`: Cached from material_item

- **Transaction Safety**:
  - All BOM create/update operations wrapped in `transaction.atomic()`
  - Ensures data consistency between header and lines

- **Form Architecture**:
  - Inline formset with extra=3, can_delete=True, min_num=1
  - Company-scoped queryset filtering in form __init__
  - Cascading filter fields not saved to database

---

## [Previous Updates]

### Added
- Default language set to Persian (Farsi) - application now opens in Persian by default
- Complete Persian translations for all UI elements and messages
- Enhanced dashboard design with minimal, modern styling
- Improved top menu button layout with proper text wrapping for long labels
- **Custom login page** (`/login/`) with professional UI/UX design:
  - Gradient animated backgrounds with floating shapes
  - Glass morphism card design with backdrop blur effects
  - Modern input fields with emoji icons and smooth transitions
  - Language switcher integrated into login page
  - Auto-focus on username field
  - Responsive design for mobile devices
  - Pulse animation for logo
  - Shimmer effect on login button
  - Animated error messages with shake effect
- Version query strings for CSS files to prevent browser caching issues

### Changed
- Default language changed from English to Persian (`LANGUAGE_CODE = 'fa'`)
- Top menu buttons now have flexible width (85-100px) to accommodate text properly
- Dashboard cards redesigned with gradient backgrounds, hover animations, and improved spacing
- Menu button font size reduced to 0.65rem for better text fitting
- Menu icons reduced in size to provide more space for labels
- **Login system**: Replaced Django admin login with custom login page at `/login/`
- **Button styling** enhanced across all pages:
  - Gradient backgrounds instead of solid colors
  - Box shadows and hover transform effects (translateY)
  - Padding increased from 10px×20px to 12px×24px
  - Added ::before pseudo-element for shimmer effect
  - Minimum width of 120px for form action buttons
- **Form inputs** redesigned with professional styling:
  - Border thickness increased from 1px to 2px
  - Padding increased from 8px×12px to 12px×16px
  - Enhanced hover states with border color and shadow changes
  - Focus states with blue glow and subtle translateY animation
  - Custom dropdown arrow for select elements
  - Textarea minimum height increased from 80px to 100px
- **Table styling** improvements:
  - Striped rows (alternating background colors)
  - Hover effects with background change and shadow
  - Header with gradient background
  - Padding increased from 12px×16px to 16px×20px
  - Action buttons padding increased from 8px×14px to 10px×18px
- **Form sections** enhanced with:
  - Gradient backgrounds (white to subtle blue tint)
  - Padding increased from 32px to 36px
  - Hover effects with border and shadow changes
  - Decorative colored bar before section titles
- **Status badges** redesigned:
  - Gradient backgrounds for all states
  - Colored borders matching status
  - Hover transform effects
  - Padding increased from 4px×10px to 6px×14px
  - Text uppercase with letter-spacing
- **Alert messages** enhanced:
  - Gradient backgrounds
  - Emoji icons (✓, ✗, ⚠, ℹ) before text
  - Slide-down animation on appear
  - Border thickness increased to 2px
  - Padding increased from 12px×16px to 16px×20px
- **Spacing improvements** throughout the application:
  - Table action buttons gap: 8px → 12px
  - Form action buttons gap: 16px → 20px
  - Form fields gap: 24px → 28px
  - Form section spacing: 40px → 32px between sections
  - Filter form gap: 20px → 24px
  - Label margins increased for better readability

### Fixed
- Top menu button text overflow issue - English labels no longer overflow from buttons
- Missing Persian translations for common UI elements (View, Lock, Locked, Yes/No, Error, etc.)
- Duplicate translation entries in django.po file causing compilation errors
- Dashboard visual design - made more minimal and modern with better card styling
- User edit form: Groups and superuser checkbox now save correctly - fixed issue where group selections and superuser status were not persisted when editing users
- Purchase Request and Warehouse Request forms now correctly redirect to list view after successful save
- **Button spacing issues**: Increased gaps between action buttons to prevent visual crowding
- **Form field spacing**: Improved spacing between fields and labels for better readability
- **Visual crowding**: Added proper breathing room throughout the application
- **CSS caching issues**: Added version query strings to force browser cache refresh

### Changed
- **BREAKING**: Person model removed from inventory module - all request/approval fields now use Django User model directly
  - `PurchaseRequest.requested_by` changed from Person to User
  - `WarehouseRequest.requester` changed from Person to User
  - Removed `requested_by_code`, `requester_code`, `approved_by`, `approved_by_code`, `rejected_by`, `cancelled_by` fields
  - Person model now only used in Production module for workforce management
- Enhanced sidebar navigation with modern styling:
  - Gradient backgrounds and hover effects
  - Icon indicators (📁, 📄, 📝) for better visual hierarchy
  - Improved spacing and animations
  - Clearer section headers with visual indicators

### Added
- Machine management in Production module (`production_machine` table)
  - Machine code, name, type classification
  - Work center assignment
  - Manufacturer and model information
  - Serial number tracking
  - Capacity specifications (JSON field)
  - Maintenance schedule and tracking
  - Machine status (operational, maintenance, idle, broken, retired)
  - Purchase and installation date tracking
- Personnel management moved from Shared module to Production module
  - Better alignment with production workflows and resource management
  - Personnel records now in `production_person` table
  - Personnel assignments in `production_person_assignment` table
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
- Custom CRUD forms for production entities:
  - PersonForm with username sync checkbox feature و انتخاب چند واحد سازمانی (moved from Shared module)
  - MachineForm for machine management
- Automatic code generation for production entities:
  - Person: 8-digit sequential code auto-generated per company (not user-editable)
  - Machine: 10-digit sequential code auto-generated per company (not user-editable)
  - Codes generated using `generate_sequential_code()` utility function
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
- Automatic code generation for Person and Machine models:
  - `public_code` fields are now `editable=False` in models
  - Codes are automatically generated on save using `generate_sequential_code()`
  - Code fields removed from PersonForm and MachineForm (users cannot enter codes)
  - Code fields removed from form templates (machine_form.html, person_form.html)
- Personnel management moved from Shared module (`shared_person`) to Production module (`production_person`)
  - All personnel-related models, views, forms, and templates moved to production app
  - Database tables renamed from `shared_person*` to `production_person*`
  - URLs changed from `/shared/personnel/` to `/production/personnel/`
  - Better alignment with production resource management workflows
- Process approval workflow now references `production_person` instead of `shared_person`
- ProcessStep model extended with optional `machine_id` field for machine assignment
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

## [Unreleased]

### Added
- **WorkLine Model Migration to Production Module**: `WorkLine` has been moved from `inventory` module to `production` module as it is primarily a production concept. The model now supports:
  - Optional warehouse assignment (only if inventory module is installed)
  - ManyToMany relationships with `Person` (personnel) and `Machine`
  - Automatic 5-digit `public_code` generation
- **WorkLine Management Views**: Complete CRUD views for work lines in production module:
  - `WorkLineListView`: List all work lines with personnel and machines display
  - `WorkLineCreateView`: Create new work lines with personnel and machines assignment
  - `WorkLineUpdateView`: Update existing work lines
  - `WorkLineDeleteView`: Delete work lines with confirmation
- **WorkLine Forms**: `WorkLineForm` in production module with support for:
  - Optional warehouse selection (hidden if inventory module not installed)
  - Personnel multi-select (filtered by company)
  - Machines multi-select (filtered by company)
- **WorkLine Templates**: New templates in `templates/production/`:
  - `work_lines.html`: List view with personnel and machines display
  - `work_line_form.html`: Create/edit form
  - `work_line_confirm_delete.html`: Delete confirmation
- **WorkLine Permissions**: New permission `production.work_lines` with actions (view_own, view_all, create, edit_own, delete_own)
- **WorkLine URLs**: New URL patterns in `production/urls.py`:
  - `/production/work-lines/` - List view
  - `/production/work-lines/create/` - Create view
  - `/production/work-lines/<id>/edit/` - Edit view
  - `/production/work-lines/<id>/delete/` - Delete view

### Changed
- **WorkLine Location**: `WorkLine` model moved from `inventory.models` to `production.models`
- **WorkLine Admin**: `WorkLineAdmin` moved from `inventory.admin` to `production.admin`
- **WorkLine Forms**: `WorkLineForm` moved from `inventory.forms` to `production.forms`
- **WorkLine Views**: All work line views moved from `inventory.views` to `production.views`
- **WorkLine URLs**: All work line URLs moved from `inventory.urls` to `production.urls`
- **WorkLine Permission**: Permission code changed from `inventory.master.work_lines` to `production.work_lines`
- **Sidebar Navigation**: Work Lines link moved from Inventory section to Production section in sidebar
- **IssueConsumptionLine**: Updated to reference `production.WorkLine` instead of `inventory.WorkLine` (optional dependency)
- **Inventory Forms**: `IssueConsumptionLineForm` updated to handle optional `WorkLine` import from production module

### Migration Notes
- **Database Migrations**: Four migrations created to move `WorkLine` from inventory to production:
  - `inventory.0026_add_personnel_machines_to_workline`: Added ManyToMany fields (reverted in later migration)
  - `inventory.0027_move_workline_to_production`: Removed fields from inventory WorkLine
  - `production.0013_move_workline_to_production`: Created WorkLine in production module
  - `inventory.0028_move_workline_to_production`: Updated IssueConsumptionLine foreign key and deleted inventory WorkLine
- **Backward Compatibility**: `inventory` module can work without `production` module installed. `WorkLine` references in `IssueConsumptionLine` are optional and handled gracefully.

### Notes
- **Personnel (`Person`)**: Personnel management is part of the Production module, not Inventory. The `Person` model is used for workforce management in production workflows and can optionally be assigned to work lines.
- **WorkLine**: Work lines are part of the Production module, not Inventory. They can optionally be associated with warehouses (if inventory module is installed) and are primarily used in production workflows, though they can also be referenced in inventory consumption issues.

### Planned for v0.4.0
- Integration with external ERPs
- Automated backup system
- Advanced workflow engine
- Custom report builder
- Multi-warehouse transfer support
- Batch/lot tracking enhancements


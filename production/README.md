# production app overview

The production module captures manufacturing definitions, work centers, orders, material movements, personnel, and machines. This document describes each custom file and the classes within it.

## models.py

Defines all production entities. Structure:

- **Mixins**
  - `ProductionBaseModel`: shared multi-company/timestamp/activation base.
  - `ProductionSortableModel`: adds `sort_order`.

- **Core Resources**
  - `WorkCenter`: identifies work centers/lines, with per-company unique `public_code` and name. Automatically generates 5-digit `public_code` on save.
  - `WorkLine`: production work lines that can be assigned personnel and machines. Each work line can optionally be associated with a warehouse (if inventory module is installed). Automatically generates 5-digit `public_code` on save. Used primarily in production but can also be referenced in inventory consumption issues.
  - `Machine`: production machines and equipment with specifications, maintenance tracking, and work center assignments. Automatically generates 10-digit `public_code` on save using `generate_sequential_code()`.

- **Personnel Management**
  - `Person`: personnel directory entry with optional linkage to `User`. هر شخص می‌تواند عضو چند واحد سازمانی از همان شرکت باشد (`ManyToMany` با `CompanyUnit`). Automatically generates 8-digit `public_code` on save using `generate_sequential_code()`.
  - `PersonAssignment`: assigns a person to a work center (inventory/production/etc.) with optional primary flag and date range.

- **Bill of Materials**
  - `BOM`: Bill of Materials header defining a finished item's material requirements with version control and approval workflow. Automatically generates unique 16-digit `bom_code` on save. Each finished item can have multiple versions with unique constraint on (company, finished_item, version).
  - `BOMMaterial`: BOM line items connecting materials to the BOM header. Stores material item, type (FK to ItemType - user-defined), quantity per unit, unit (CharField - stores unit name), scrap allowance percentage, optional flag (0=Required, 1=Optional), and line number for ordering. Automatically caches material item code. CASCADE delete when parent BOM is deleted.

- **Process Definitions**
  - `Process`: describes a production process for a finished item; stores optional BOM reference, optional revision, work lines assignment (ManyToMany), and primary flag. Populates cached finished item code from BOM if provided. References `User` (not `Person`) for approval workflow via `approved_by` field. **Note**: `effective_from` and `effective_to` fields have been removed. `revision` is now optional. `approval_status` is managed via approval workflow in list view, not in form.
  - `ProcessStep`: details each step within a process (work center, optional machine assignment, sequence, labor/machine minutes, setup time). Caches work center code and machine code when machine is assigned.

- **Production Orders**
  - `ProductOrder`: plans execution for a finished item with BOM selection, planned quantity, approver assignment, priority, due date, customer reference, and status. Automatically generates unique 8-digit `order_code` per company. References `BOM` (ForeignKey, required) and `User` (for approver, optional). Caches finished item code from BOM and process code if process is assigned. Made `process` field nullable to allow orders without process assignment.
  - `OrderPerformance`: records daily/periodic production results including produced/received/scrapped quantities, cycle times, labor/machine usage, and optional shift context. Enforces one record per order per date and caches order/finished item codes.

- **Material Transfer**
  - `TransferToLine`: documents material transfers to production lines for a specific order with workflow status.
  - `TransferToLineItem`: line items for transfers, capturing required versus transferred quantities, source warehouse, destination work center, and scrap allowance. Caches item and warehouse codes.

- **Performance Records**
  - `PerformanceRecord`: records production performance for a specific order with workflow status, materials, personnel, and machines used.
  - `PerformanceRecordMaterial`: line items for materials used in performance records, capturing item, quantity, unit, and warehouse.
  - `PerformanceRecordPerson`: line items for personnel used in performance records, capturing person, hours worked, and role.
  - `PerformanceRecordMachine`: line items for machines used in performance records, capturing machine, hours used, and maintenance notes.

All models inherit audit fields and apply `save()` overrides to populate cached codes where necessary. Personnel models (`Person`, `PersonAssignment`) were moved from the `shared` module to better align with production workflows and resource management.

**Automatic Code Generation:**
- `Person.public_code`: Auto-generated 8-digit sequential code per company (not user-editable)
- `Machine.public_code`: Auto-generated 10-digit sequential code per company (not user-editable)
- `WorkCenter.public_code`: Auto-generated 5-digit sequential code per company
- `WorkLine.public_code`: Auto-generated 5-digit sequential code per company (not user-editable)
- `BOM.bom_code`: Auto-generated 16-digit sequential code per company (not user-editable)
- `ProductOrder.order_code`: Auto-generated 8-digit sequential code per company with prefix "PO" (not user-editable)
- Codes are generated using `inventory.utils.codes.generate_sequential_code()` function
- Users cannot manually enter codes; they are automatically assigned on save
- All codes are company-scoped (each company has independent sequences starting from 1)

## forms.py

Defines ModelForms for production entities:

- `PersonForm`: Create and edit personnel records with username sync checkbox feature and multi-select for company units. Does not include `public_code` field (auto-generated).
- `MachineForm`: Create and edit machine records with work center assignment, specifications, and maintenance tracking. Does not include `public_code` field (auto-generated).
- `WorkLineForm`: Create and edit work lines with optional warehouse assignment (if inventory module is installed), personnel and machines ManyToMany fields. Does not include `public_code` field (auto-generated).
- `BOMForm`: Create and edit BOM headers with cascading filters for finished item selection (Type → Category → Subcategory → Item). Includes version, description, notes, active flag, and status fields.
- `BOMMaterialLineForm`: Form for individual BOM material lines with cascading filters for material selection. Includes material type (FK to ItemType), category/subcategory filters (UI-only), material item, quantity, unit (CharField), scrap allowance, optional flag (BooleanField in form, stores as 0/1), and description. Auto-sets material_type from material_item if not provided.
- `BOMMaterialLineFormSet`: Django inline formset factory for managing multiple material lines within a BOM. Supports dynamic add/remove of lines with minimum 1 line validation. Shows 1 empty form initially (extra=1).
- `ProcessForm`: Create and edit production processes. Includes optional BOM selection, optional revision, work lines multi-select (ManyToMany), description, is_primary flag (optional), approved_by (ForeignKey to User, filtered to show only users with APPROVE permission for production.processes), notes, is_enabled, and sort_order. **Note**: `effective_from` and `effective_to` fields have been removed. `approval_status` is not in form (managed via approval workflow in list view). **Important**: `approved_by` uses `User` model, not `Person` model.
- `ProductOrderForm`: Create and edit production orders. Includes BOM selection (required, filtered by company and enabled status), quantity_planned (required, must be positive), approved_by (ForeignKey to User, optional, filtered to show only users with APPROVE permission for production.product_orders), due_date (JalaliDateField, optional), priority (ChoiceField), customer_reference (optional), notes (optional), and is_enabled. Auto-sets finished_item from selected BOM. Uses `JalaliDateInput` widget for due_date field with Persian date picker.

## views.py

Provides CRUD views for production resources:

- **Personnel Management**:
  - `PersonnelListView`: List all personnel for the active company
  - `PersonCreateView`: Create new personnel records
  - `PersonUpdateView`: Update existing personnel records
  - `PersonDeleteView`: Delete personnel records (with confirmation)

- **Machine Management**:
  - `MachineListView`: List all machines for the active company with filtering by work center and status
  - `MachineCreateView`: Create new machine records
  - `MachineUpdateView`: Update existing machine records
  - `MachineDeleteView`: Delete machine records (with confirmation)

- **Work Line Management**:
  - `WorkLineListView`: List all work lines for the active company with personnel and machines display
  - `WorkLineCreateView`: Create new work line records with personnel and machines assignment
  - `WorkLineUpdateView`: Update existing work line records
  - `WorkLineDeleteView`: Delete work line records (with confirmation)

- **BOM Management**:
  - `BOMListView`: List all BOMs with expand/collapse material details, filtering by finished item
  - `BOMCreateView`: Create new BOM with header form and inline material formset. Handles formset validation, auto-sets company/created_by, saves BOM header first then material lines. Includes comprehensive logging for debugging.
  - `BOMUpdateView`: Update BOM header and materials with formset validation. Handles edit mode value restoration, auto-sets edited_by, saves with proper line numbering. Includes comprehensive logging for debugging.
  - `BOMDeleteView`: Delete BOM and cascade delete all material lines

- **Process Management**:
  - `ProcessListView`: List all processes for the active company with BOM, work lines, and status display. Filters by active company, uses select_related for BOM/finished_item/approved_by and prefetch_related for work_lines.
  - `ProcessCreateView`: Create new process records. Auto-sets company_id and created_by. Sets finished_item from BOM if provided. Saves ManyToMany work_lines relationship via form.save_m2m().
  - `ProcessUpdateView`: Update existing process records. Auto-sets edited_by. Sets finished_item from BOM if changed. Saves ManyToMany work_lines relationship via form.save_m2m().
  - `ProcessDeleteView`: Delete process records (with confirmation). Filters by active company.

- **Transfer Requests** (Placeholder):
  - `TransferToLineRequestListView`: List transfer requests to production lines

- **Performance Records** (Placeholder):
  - `PerformanceRecordListView`: List production performance records

All views use `FeaturePermissionRequiredMixin` for access control and filter by active company from session.

## urls.py

URL patterns for production module:

- `/production/personnel/` - Personnel list
- `/production/personnel/create/` - Create personnel
- `/production/personnel/<id>/edit/` - Edit personnel
- `/production/personnel/<id>/delete/` - Delete personnel
- `/production/machines/` - Machines list
- `/production/machines/create/` - Create machine
- `/production/machines/<id>/edit/` - Edit machine
- `/production/machines/<id>/delete/` - Delete machine
- `/production/work-lines/` - Work lines list
- `/production/work-lines/create/` - Create work line
- `/production/work-lines/<id>/edit/` - Edit work line
- `/production/work-lines/<id>/delete/` - Delete work line
- `/production/bom/` - BOM list with material details
- `/production/bom/create/` - Create new BOM with materials
- `/production/bom/<id>/edit/` - Edit BOM and materials
- `/production/bom/<id>/delete/` - Delete BOM (cascade)
- `/production/processes/` - Processes list
- `/production/processes/create/` - Create process
- `/production/processes/<id>/edit/` - Edit process
- `/production/processes/<id>/delete/` - Delete process
- `/production/product-orders/` - Product orders list
- `/production/product-orders/create/` - Create product order
- `/production/product-orders/<id>/edit/` - Edit product order
- `/production/product-orders/<id>/delete/` - Delete product order
- `/production/transfer-requests/` - Transfer to line requests (placeholder)
- `/production/performance-records/` - Performance records (placeholder)

## templates/

Production module templates:

- `production/personnel.html`: Personnel list view with search and filter capabilities
- `production/person_form.html`: Personnel create/edit form with company unit multi-select and username sync feature
- `production/person_confirm_delete.html`: Personnel deletion confirmation page
- `production/machines.html`: Machines list view with filtering by work center and status
- `production/machine_form.html`: Machine create/edit form with work center assignment and specifications
- `production/machine_confirm_delete.html`: Machine deletion confirmation page
- `production/work_lines.html`: Work lines list view with personnel and machines display
- `production/work_line_form.html`: Work line create/edit form with optional warehouse, personnel and machines assignment
- `production/work_line_confirm_delete.html`: Work line deletion confirmation page
- `production/bom_list.html`: BOM list with expand/collapse material details, filter by finished item, material type badges
- `production/bom_form.html`: Multi-section form with cascading dropdowns for finished item selection and dynamic formset for materials with JavaScript add/remove functionality
- `production/bom_confirm_delete.html`: BOM deletion confirmation with material count display
- `production/processes.html`: Processes list view with BOM, work lines, and status display. Shows empty state if no processes exist.
- `production/process_form.html`: Process create/edit form with optional BOM selection, optional revision, work lines multi-select, description, is_primary, approved_by (filtered by approve permission), notes, is_enabled, and sort_order fields.
- `production/process_confirm_delete.html`: Process deletion confirmation page
- `production/product_orders.html`: Product orders list view with BOM, quantity, status, and actions (edit/delete)
- `production/product_order_form.html`: Product order create/edit form with BOM selection, quantity, approver, due date (with Persian date picker), priority, customer reference, and notes
- `production/product_order_confirm_delete.html`: Product order deletion confirmation page

## admin.py

Registers each model with admin list displays, filters, and search fields tailored to production workflows (e.g., filtering orders by status, steps by process, machines by type and status).

## migrations/
- `0001_initial.py`: Initial schema derived from `production_module_db_design_plan.md`
- `0002_*.py` to `0005_*.py`: Various model updates and field additions
- `0006_bom_restructure.py`: Custom migration to restructure BOM from single-model to header-line architecture. Drops old `BOMMaterial` table and creates new `BOM` (header) and `BOMMaterial` (lines) tables
- `0007_*.py`: Auto-generated migration to add missing `ProductionBaseModel` fields to BOM models
- Future changes should include updates to the design plan and new migrations

## apps.py
- Default configuration (`ProductionConfig`); use this location for signal registration or ready hooks if later required.

## tests.py

Validation coverage includes:
- `BOMMaterial` caching of finished and material item codes.
- `Process` and `ProcessStep` ensuring derived codes are populated.
- `ProductOrder`, `OrderPerformance`, and `TransferToLineItem` verifying cached codes/relations.
- `Person` and `PersonAssignment` model validation (moved from shared module).
- `Machine` model validation and work center code caching.

Run with `python manage.py test production`.

## URLs

Production module URLs are registered in `production/urls.py` and included in the main URL configuration at `/production/`:

- Personnel management: `/production/personnel/`
- Machine management: `/production/machines/`

## Permissions

Production module uses the centralized permission system defined in `shared/permissions.py`:

- `production.personnel`: Personnel management with actions (view_own, view_all, create, edit_own, delete_own) - **Personnel is part of Production module, not Inventory**
- `production.machines`: Machine management with actions (view_own, view_all, create, edit_own, delete_own)
- `production.work_lines`: Work line management with actions (view_own, view_all, create, edit_own, delete_own) - **WorkLine is part of Production module, not Inventory**
- `production.bom`: BOM (Bill of Materials) management with actions (view_own, view_all, create, edit_own, delete_own)
- `production.product_orders`: Product orders management with actions (view_own, view_all, create, edit_own, delete_own, approve)
- `production.transfer_requests`: Transfer to line requests (placeholder)
- `production.performance_records`: Production performance records (placeholder)

## BOM (Bill of Materials) - Detailed Overview

**For complete BOM documentation, see:** `production/README_BOM.md`

### Key Features:
- **Header-Line Structure**: BOM (header) contains finished item info, BOMMaterial (lines) contain material requirements
- **Version Control**: Multiple BOM versions per finished item with unique constraint on (company, finished_item, version)
- **Multi-line Form**: Dynamic formset with JavaScript add/remove lines, minimum 1 line validation
- **Cascading Filters**: Type → Category → Item filtering for both finished product and materials
- **Material Types**: Raw, Semi-Finished, Component, Packaging with color-coded badges
- **Scrap Allowance**: Percentage-based waste calculation (0-100%)
- **Optional Materials**: Flag materials as optional or required
- **Expand/Collapse**: List view with expandable material details
- **Transaction Safety**: All create/update operations wrapped in `transaction.atomic()`

### Database Schema:
```
BOM (1) ──────< BOMMaterial (N)
  │                 │
  └── finished_item │
      (FK → Item)   └── material_item
                        (FK → Item)
```

### Form Architecture:
- **BOMForm**: Header form with cascading finished item selection
- **BOMMaterialLineForm**: Individual material line with cascading material selection
- **BOMMaterialLineFormSet**: Inline formset (extra=3, can_delete=True, min_num=1)

### JavaScript Features:
- Dynamic add/remove formset lines
- Auto-update TOTAL_FORMS count
- Cascading dropdown filtering
- Line number auto-increment
- Minimum 1 line validation

## Future Work / Notes
- When integrating with scheduling/MES systems, document new service layers here.
- If production order lifecycle expands (e.g., statuses, approvals), ensure the README and design document reflect the changes.
- Keep admin forms/pages synchronized with new fields so planners have the correct metadata.
- Consider adding machine maintenance history tracking as a separate model.
- ProcessStep machine assignment can be extended to support multiple machines per step if needed.
- Complete implementation of Transfer to Line Requests and Performance Records (currently placeholders).
- BOM future features: cost calculation, BOM tree view, bulk import/export, version comparison, approval workflow.


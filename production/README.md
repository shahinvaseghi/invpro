# production app overview

The production module captures manufacturing definitions, work centers, orders, material movements, personnel, and machines. This document describes each custom file and the classes within it.

## models.py

Defines all production entities. Structure:

- **Mixins**
  - `ProductionBaseModel`: shared multi-company/timestamp/activation base.
  - `ProductionSortableModel`: adds `sort_order`.

- **Core Resources**
  - `WorkCenter`: identifies work centers/lines, with per-company unique `public_code` and name. Automatically generates 5-digit `public_code` on save.
  - `Machine`: production machines and equipment with specifications, maintenance tracking, and work center assignments. Automatically generates 10-digit `public_code` on save using `generate_sequential_code()`.

- **Personnel Management**
  - `Person`: personnel directory entry with optional linkage to `User`. هر شخص می‌تواند عضو چند واحد سازمانی از همان شرکت باشد (`ManyToMany` با `CompanyUnit`). Automatically generates 8-digit `public_code` on save using `generate_sequential_code()`.
  - `PersonAssignment`: assigns a person to a work center (inventory/production/etc.) with optional primary flag and date range.

- **Bill of Materials**
  - `BOM`: Bill of Materials header defining a finished item's material requirements with version control, effective/expiry dates, and approval workflow. Automatically generates unique 16-digit `bom_code` on save. Each finished item can have multiple versions with unique constraint on (company, finished_item, version).
  - `BOMMaterial`: BOM line items connecting materials to the BOM header. Stores material item, type (raw/semi-finished/component/packaging), quantity per unit, unit, scrap allowance percentage, and line number for ordering. Automatically caches material item code. CASCADE delete when parent BOM is deleted.

- **Process Definitions**
  - `Process`: describes a production process for a finished item; stores BOM reference, revision, approval state, and primary flag. Populates cached finished item code. References `Person` for approval workflow.
  - `ProcessStep`: details each step within a process (work center, optional machine assignment, sequence, labor/machine minutes, setup time). Caches work center code and machine code when machine is assigned.

- **Production Orders**
  - `ProductOrder`: plans execution for a finished item with BOM/process reference, planned quantity, priority, and status. Caches finished item and process codes.
  - `OrderPerformance`: records daily/periodic production results including produced/received/scrapped quantities, cycle times, labor/machine usage, and optional shift context. Enforces one record per order per date and caches order/finished item codes.

- **Material Transfer**
  - `TransferToLine`: documents material transfers to production lines for a specific order with workflow status.
  - `TransferToLineItem`: line items for transfers, capturing required versus transferred quantities, source warehouse, destination work center, and scrap allowance. Caches item and warehouse codes.

All models inherit audit fields and apply `save()` overrides to populate cached codes where necessary. Personnel models (`Person`, `PersonAssignment`) were moved from the `shared` module to better align with production workflows and resource management.

**Automatic Code Generation:**
- `Person.public_code`: Auto-generated 8-digit sequential code per company (not user-editable)
- `Machine.public_code`: Auto-generated 10-digit sequential code per company (not user-editable)
- `WorkCenter.public_code`: Auto-generated 5-digit sequential code per company
- `BOM.bom_code`: Auto-generated 16-digit sequential code per company (not user-editable)
- Codes are generated using `inventory.utils.codes.generate_sequential_code()` function
- Users cannot manually enter codes; they are automatically assigned on save
- All codes are company-scoped (each company has independent sequences starting from 1)

## forms.py

Defines ModelForms for production entities:

- `PersonForm`: Create and edit personnel records with username sync checkbox feature and multi-select for company units. Does not include `public_code` field (auto-generated).
- `MachineForm`: Create and edit machine records with work center assignment, specifications, and maintenance tracking. Does not include `public_code` field (auto-generated).
- `BOMForm`: Create and edit BOM headers with cascading filters for finished item selection (Type → Category → Item). Includes version, effective/expiry dates, and status fields.
- `BOMMaterialLineForm`: Form for individual BOM material lines with cascading filters for material selection. Includes material type, quantity, unit, scrap allowance, and optional flag.
- `BOMMaterialLineFormSet`: Django inline formset factory for managing multiple material lines within a BOM. Supports dynamic add/remove of lines with minimum 1 line validation.

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

- **BOM Management**:
  - `BOMListView`: List all BOMs with expand/collapse material details, filtering by finished item
  - `BOMCreateView`: Create new BOM with header form and inline material formset using transaction.atomic()
  - `BOMUpdateView`: Update BOM header and materials with formset validation
  - `BOMDeleteView`: Delete BOM and cascade delete all material lines

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
- `/production/bom/` - BOM list with material details
- `/production/bom/create/` - Create new BOM with materials
- `/production/bom/<id>/edit/` - Edit BOM and materials
- `/production/bom/<id>/delete/` - Delete BOM (cascade)
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
- `production/bom_list.html`: BOM list with expand/collapse material details, filter by finished item, material type badges
- `production/bom_form.html`: Multi-section form with cascading dropdowns for finished item selection and dynamic formset for materials with JavaScript add/remove functionality
- `production/bom_confirm_delete.html`: BOM deletion confirmation with material count display

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

- `production.personnel`: Personnel management with actions (view_own, view_all, create, edit_own, delete_own)
- `production.machines`: Machine management with actions (view_own, view_all, create, edit_own, delete_own)
- `production.bom`: BOM (Bill of Materials) management with actions (view_own, view_all, create, edit_own, delete_own)
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


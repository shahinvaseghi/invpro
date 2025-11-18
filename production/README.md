# production app overview

The production module captures manufacturing definitions, work centers, orders, material movements, personnel, and machines. This document describes each custom file and the classes within it.

## models.py

Defines all production entities. Structure:

- **Mixins**
  - `ProductionBaseModel`: shared multi-company/timestamp/activation base.
  - `ProductionSortableModel`: adds `sort_order`.

- **Core Resources**
  - `WorkCenter`: identifies work centers/lines, with per-company unique `public_code` and name.
  - `Machine`: production machines and equipment with specifications, maintenance tracking, and work center assignments.

- **Personnel Management**
  - `Person`: personnel directory entry with optional linkage to `User`. هر شخص می‌تواند عضو چند واحد سازمانی از همان شرکت باشد (`ManyToMany` با `CompanyUnit`).
  - `PersonAssignment`: assigns a person to a work center (inventory/production/etc.) with optional primary flag and date range.

- **Bill of Materials**
  - `BOMMaterial`: connects a finished item to required material items, storing quantity, unit, optional scrap allowance, and sequence order. Automatically caches item codes.

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

## forms.py

Defines ModelForms for production entities:

- `PersonForm`: Create and edit personnel records with username sync checkbox feature and multi-select for company units.
- `MachineForm`: Create and edit machine records with work center assignment, specifications, and maintenance tracking.

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

## templates/

Production module templates:

- `production/personnel.html`: Personnel list view with search and filter capabilities
- `production/person_form.html`: Personnel create/edit form with company unit multi-select and username sync feature
- `production/person_confirm_delete.html`: Personnel deletion confirmation page
- `production/machines.html`: Machines list view with filtering by work center and status
- `production/machine_form.html`: Machine create/edit form with work center assignment and specifications
- `production/machine_confirm_delete.html`: Machine deletion confirmation page

## admin.py

Registers each model with admin list displays, filters, and search fields tailored to production workflows (e.g., filtering orders by status, steps by process, machines by type and status).

## migrations/
- `0001_initial.py`: schema derived from `production_module_db_design_plan.md`. Future changes should include updates to the design plan and new migrations.

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

## Future Work / Notes
- When integrating with scheduling/ MES systems, document new service layers here.
- If production order lifecycle expands (e.g., statuses, approvals), ensure the README and design document reflect the changes.
- Keep admin forms/pages synchronized with new fields so planners have the correct metadata.
- Consider adding machine maintenance history tracking as a separate model.
- ProcessStep machine assignment can be extended to support multiple machines per step if needed.


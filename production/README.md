# production app overview

The production module captures manufacturing definitions, work centers, orders, and material movements. This document describes each custom file and the classes within it.

## models.py

Defines all production entities. Structure:

- **Mixins**
  - `ProductionBaseModel`: shared multi-company/timestamp/activation base.
  - `ProductionSortableModel`: adds `sort_order`.

- **Core Resources**
  - `WorkCenter`: identifies work centers/lines, with per-company unique `public_code` and name.

- **Bill of Materials**
  - `BOMMaterial`: connects a finished item to required material items, storing quantity, unit, optional scrap allowance, and sequence order. Automatically caches item codes.

- **Process Definitions**
  - `Process`: describes a production process for a finished item; stores BOM reference, revision, approval state, and primary flag. Populates cached finished item code.
  - `ProcessStep`: details each step within a process (work center, sequence, labor/machine minutes, setup time). Caches work center code.

- **Production Orders**
  - `ProductOrder`: plans execution for a finished item with BOM/process reference, planned quantity, priority, and status. Caches finished item and process codes.
  - `OrderPerformance`: records daily/periodic production results including produced/received/scrapped quantities, cycle times, labor/machine usage, and optional shift context. Enforces one record per order per date and caches order/finished item codes.

- **Material Transfer**
  - `TransferToLine`: documents material transfers to production lines for a specific order with workflow status.
  - `TransferToLineItem`: line items for transfers, capturing required versus transferred quantities, source warehouse, destination work center, and scrap allowance. Caches item and warehouse codes.

All models inherit audit fields and apply `save()` overrides to populate cached codes where necessary.

## admin.py

Registers each model with admin list displays, filters, and search fields tailored to production workflows (e.g., filtering orders by status, steps by process).

## migrations/
- `0001_initial.py`: schema derived from `production_module_db_design_plan.md`. Future changes should include updates to the design plan and new migrations.

## apps.py
- Default configuration (`ProductionConfig`); use this location for signal registration or ready hooks if later required.

## tests.py

Validation coverage includes:
- `BOMMaterial` caching of finished and material item codes.
- `Process` and `ProcessStep` ensuring derived codes are populated.
- `ProductOrder`, `OrderPerformance`, and `TransferToLineItem` verifying cached codes/relations.

Run with `python manage.py test production`.

## Future Work / Notes
- When integrating with scheduling/ MES systems, document new service layers here.
- If production order lifecycle expands (e.g., statuses, approvals), ensure the README and design document reflect the changes.
- Keep admin forms/pages synchronized with new fields so planners have the correct metadata.


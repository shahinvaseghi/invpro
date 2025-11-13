# qc app overview

The quality control module manages inspections tied to temporary inventory receipts. This README explains the custom files and classes within the app.

## models.py

Defines:

- `QCBaseModel`: inherits from shared multi-company/timestamp/activation/metadata mixins to ensure uniform auditing.
- `ReceiptInspection`: one-to-one inspection record linked to `inventory.ReceiptTemporary`. Key fields:
  - `inspection_code`, `inspection_date`, `inspection_status`
  - `inspector`, `inspector_code` (cached from `Person.public_code`)
  - `inspection_results` JSON payload and `attachments`
  - Decision workflow fields (`approval_decision`, `approved_by`, `approved_at`, `approval_notes`)
  - Optional `nonconformity_flag` and `nonconformity_report_id`
  
`save()` auto-populates `temporary_receipt_code` and `inspector_code` to avoid repeated joins when rendering dashboards.

## admin.py

Registers `ReceiptInspection` and configures filters (status, decision, nonconformity) plus search fields (inspection code, temporary receipt, inspector names).

## migrations/
- `0001_initial.py`: creates the `qc_receipt_inspection` table aligning with `qc_module_db_design_plan.md`. Generate new migrations if inspection data model changes.

## apps.py
- Contains the default `QcConfig`. Hook into `ready()` if QC-specific signals or initialization are added later.

## tests.py

Provides coverage for:
- Auto-filling cached codes (`temporary_receipt_code`, `inspector_code`)
- Approval linkage to another `Person`

Executed via `python manage.py test qc`.

## Future Work / Notes
- When CAPA or deviation workflows are implemented, extend this README with new models/services.
- Keep the QC design document synchronized with schema updates to avoid drift.
- Integrate with notification systems (email/slack) as part of future enhancements.


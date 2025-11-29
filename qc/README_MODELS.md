# qc/models.py - Quality Control Models (Complete Documentation)

**هدف**: تمام model classes برای ماژول Quality Control

این فایل شامل 2 model class است:
- Base Model (Abstract)
- Receipt Inspection Model

---

## وابستگی‌ها

- `shared.models`: `ActivatableModel`, `CompanyScopedModel`, `MetadataModel`, `TimeStampedModel`
- `production.models`: `Person`
- `django.db.models`
- `django.core.validators`: `RegexValidator`
- `django.utils.timezone`
- `django.conf.settings`

---

## Constants

### `NUMERIC_CODE_VALIDATOR`
- `RegexValidator(regex=r"^\d+$")`: فقط کاراکترهای عددی مجاز
- برای استفاده در QC models

---

## Base Model (Abstract)

### `QCBaseModel`
**Inheritance**: `CompanyScopedModel`, `TimeStampedModel`, `ActivatableModel`, `MetadataModel`

**توضیح**: Base model برای تمام QC models

**Fields** (از mixins):
- `company` (ForeignKey): Company scope
- `company_code` (CharField): کد company (cache)
- `created_at`, `edited_at` (DateTime): Timestamps
- `created_by`, `edited_by` (ForeignKey): Metadata
- `is_enabled` (IntegerField): Activation flag
- `metadata` (JSONField): Metadata

**نکات مهم**:
- Abstract model
- برای uniform auditing در QC models

---

## Receipt Inspection Model

### `ReceiptInspection`
**Inheritance**: `QCBaseModel`

**توضیح**: Inspection record برای temporary receipts (one-to-one با `inventory.ReceiptTemporary`)

**Fields**:
- `temporary_receipt` (OneToOneField → inventory.ReceiptTemporary, on_delete=CASCADE, related_name="qc_inspection"): Temporary receipt مرتبط
- `temporary_receipt_code` (CharField, max_length=20): کد temporary receipt (cache)
- `inspection_code` (CharField, max_length=30, unique=True): کد inspection
- `inspection_date` (DateTimeField, default=timezone.now): تاریخ inspection
- `inspection_status` (CharField, max_length=20, choices=InspectionStatus.choices, default=InspectionStatus.IN_PROGRESS): وضعیت inspection
- `inspector` (ForeignKey → Person, on_delete=PROTECT, related_name="receipt_inspections"): Inspector
- `inspector_code` (CharField, max_length=8, validators=[NUMERIC_CODE_VALIDATOR]): کد inspector (cache)
- `inspection_summary` (TextField, blank=True): خلاصه inspection
- `inspection_results` (JSONField, default=dict, blank=True): نتایج inspection (JSON payload)
- `nonconformity_flag` (PositiveSmallIntegerField, default=0): Flag برای nonconformity
- `nonconformity_report_id` (BigIntegerField, null=True, blank=True): شناسه nonconformity report
- `approval_decision` (CharField, max_length=30, choices=ApprovalDecision.choices, default=ApprovalDecision.PENDING): تصمیم approval
- `approved_at` (DateTimeField, null=True, blank=True): زمان approval
- `approved_by` (ForeignKey → User, on_delete=SET_NULL, null=True, blank=True, related_name="receipt_inspections_approved"): کاربر approver (User، نه Person)
- `approval_notes` (TextField, blank=True): یادداشت‌های approval
- `attachments` (JSONField, default=list, blank=True): فایل‌های ضمیمه (array)
- و fields از QCBaseModel

**InspectionStatus Choices**:
- `IN_PROGRESS` ("in_progress"): در حال انجام
- `PASSED` ("passed"): قبول شده
- `FAILED` ("failed"): رد شده
- `REWORK` ("rework"): نیاز به بازکاری
- `CANCELLED` ("cancelled"): لغو شده

**ApprovalDecision Choices**:
- `PENDING` ("pending"): در انتظار
- `APPROVED` ("approved"): تایید شده
- `APPROVED_WITH_DEVIATION` ("approved_with_deviation"): تایید شده با انحراف
- `REJECTED` ("rejected"): رد شده

**Constraints**:
- Unique: `(company, temporary_receipt)` (یک temporary receipt فقط یک inspection می‌تواند داشته باشد)

**Ordering**: `("-inspection_date", "inspection_code")` (جدیدترین اول)

**Methods**:
- `save()`: Auto-populate `temporary_receipt_code` از `temporary_receipt.document_code` و `inspector_code` از `inspector.public_code` اگر set نشده باشند

**نکات مهم**:
- One-to-one relationship با `inventory.ReceiptTemporary`
- `inspector`: از `production.Person` (نه User)
- `approved_by`: از `User` (نه Person) - برای approval workflow
- `temporary_receipt_code` و `inspector_code`: cached برای جلوگیری از repeated joins در dashboards
- `inspection_results`: JSON payload برای نتایج inspection
- `attachments`: JSON array برای file attachments
- `nonconformity_flag` و `nonconformity_report_id`: برای nonconformity tracking

---

## نکات مهم

1. **Code Caching**: `temporary_receipt_code` و `inspector_code` به صورت خودکار cache می‌شوند
2. **Company Scoping**: تمام models از `CompanyScopedModel` استفاده می‌کنند
3. **Activation**: تمام models از `ActivatableModel` استفاده می‌کنند (`is_enabled`)
4. **Timestamps**: تمام models از `TimeStampedModel` استفاده می‌کنند
5. **One-to-One Relationship**: هر `ReceiptTemporary` فقط یک `ReceiptInspection` می‌تواند داشته باشد
6. **Approval Workflow**: `approved_by` از `User` است (نه `Person`) برای approval workflow
7. **Nonconformity Tracking**: `nonconformity_flag` و `nonconformity_report_id` برای nonconformity tracking

---

## Related Files

- `qc/README.md`: Overview کلی ماژول
- `qc/views/`: Views برای این models
- `qc/admin.py`: Admin registration
- `qc/tests.py`: Tests برای auto-filling cached codes و approval linkage

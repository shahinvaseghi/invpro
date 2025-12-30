from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from shared.models import (
    ActivatableModel,
    CompanyScopedModel,
    MetadataModel,
    TimeStampedModel,
)
from production.models import Person


NUMERIC_CODE_VALIDATOR = RegexValidator(
    regex=r"^\d+$",
    message=_("Only numeric characters are allowed."),
)


class QCBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    class Meta:
        abstract = True


class ReceiptInspection(QCBaseModel):
    class InspectionStatus(models.TextChoices):
        IN_PROGRESS = "in_progress", _("In Progress")
        PASSED = "passed", _("Passed")
        FAILED = "failed", _("Failed")
        REWORK = "rework", _("Rework")
        CANCELLED = "cancelled", _("Cancelled")

    class ApprovalDecision(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        APPROVED_WITH_DEVIATION = "approved_with_deviation", _("Approved with Deviation")
        REJECTED = "rejected", _("Rejected")

    temporary_receipt = models.OneToOneField(
        "inventory.ReceiptTemporary",
        on_delete=models.CASCADE,
        related_name="qc_inspection",
    )
    temporary_receipt_code = models.CharField(max_length=20)
    inspection_code = models.CharField(max_length=30, unique=True)
    inspection_date = models.DateTimeField(default=timezone.now)
    inspection_status = models.CharField(
        max_length=20,
        choices=InspectionStatus.choices,
        default=InspectionStatus.IN_PROGRESS,
    )
    inspector = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="receipt_inspections",
    )
    inspector_code = models.CharField(max_length=8, validators=[NUMERIC_CODE_VALIDATOR])
    inspection_summary = models.TextField(blank=True)
    inspection_results = models.JSONField(default=dict, blank=True)
    nonconformity_flag = models.PositiveSmallIntegerField(default=0)
    nonconformity_report_id = models.BigIntegerField(null=True, blank=True)
    approval_decision = models.CharField(
        max_length=30,
        choices=ApprovalDecision.choices,
        default=ApprovalDecision.PENDING,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="receipt_inspections_approved",
        null=True,
        blank=True,
        help_text=_("User who approved this inspection"),
    )
    approval_notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = _("Receipt Inspection")
        verbose_name_plural = _("Receipt Inspections")
        ordering = ("-inspection_date", "inspection_code")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "temporary_receipt"),
                name="qc_inspection_unique_temp_receipt",
            ),
        ]

    def __str__(self) -> str:
        return self.inspection_code

    def save(self, *args, **kwargs):
        if not self.temporary_receipt_code:
            self.temporary_receipt_code = self.temporary_receipt.document_code
        if not self.inspector_code:
            self.inspector_code = self.inspector.public_code
        super().save(*args, **kwargs)


class ItemBatch(QCBaseModel):
    """Batch number tracking for items received through temporary receipts."""
    
    class Status(models.TextChoices):
        AVAILABLE = "available", _("Available")
        RESERVED = "reserved", _("Reserved")
        CONSUMED = "consumed", _("Consumed")
        SCRAPPED = "scrapped", _("Scrapped")
    
    item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="qc_batches",
    )
    item_code = models.CharField(
        max_length=16,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("Cached item code"),
    )
    batch_number = models.CharField(
        max_length=30,
        help_text=_("Batch number for this receipt line"),
    )
    receipt_temporary = models.ForeignKey(
        "inventory.ReceiptTemporary",
        on_delete=models.CASCADE,
        related_name="batches",
    )
    receipt_temporary_code = models.CharField(
        max_length=20,
        help_text=_("Cached temporary receipt document code"),
    )
    receipt_temporary_line = models.ForeignKey(
        "inventory.ReceiptTemporaryLine",
        on_delete=models.CASCADE,
        related_name="batches",
    )
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[],
        help_text=_("Quantity for this batch"),
    )
    unit = models.CharField(
        max_length=30,
        help_text=_("Unit of measure"),
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        related_name="qc_batches",
        null=True,
        blank=True,
    )
    warehouse_code = models.CharField(
        max_length=6,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
        help_text=_("Cached warehouse code"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        help_text=_("Current status of the batch"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes for this batch"),
    )
    
    class Meta:
        verbose_name = _("Item Batch")
        verbose_name_plural = _("Item Batches")
        ordering = ("company", "item", "batch_number", "-created_at")
        indexes = [
            models.Index(fields=("company", "item"), name="qc_batch_item_idx"),
            models.Index(fields=("company", "receipt_temporary"), name="qc_batch_receipt_idx"),
            models.Index(fields=("company", "receipt_temporary_line"), name="qc_batch_line_idx"),
            models.Index(fields=("company", "batch_number"), name="qc_batch_number_idx"),
            models.Index(fields=("company", "status"), name="qc_batch_status_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("company", "batch_number"),
                name="qc_batch_unique_number",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.batch_number} - {self.item.name}"
    
    def save(self, *args, **kwargs):
        """Auto-populate cached fields."""
        if self.item and not self.item_code:
            self.item_code = self.item.item_code or self.item.full_item_code or ""
        
        if self.receipt_temporary and not self.receipt_temporary_code:
            self.receipt_temporary_code = self.receipt_temporary.document_code
        
        if self.receipt_temporary_line and not self.quantity:
            self.quantity = self.receipt_temporary_line.qc_approved_quantity or self.receipt_temporary_line.quantity
        
        if self.receipt_temporary_line and not self.unit:
            self.unit = self.receipt_temporary_line.unit
        
        if self.receipt_temporary_line and not self.warehouse:
            self.warehouse = self.receipt_temporary_line.warehouse
        
        if self.warehouse and not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        
        super().save(*args, **kwargs)

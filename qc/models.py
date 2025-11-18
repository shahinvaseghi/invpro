from django.utils.translation import gettext_lazy as _

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
        Person,
        on_delete=models.SET_NULL,
        related_name="receipt_inspections_approved",
        null=True,
        blank=True,
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

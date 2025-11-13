from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shared.models import (
    ActivatableModel,
    CompanyScopedModel,
    MetadataModel,
    Person,
    SortableModel,
    TimeStampedModel,
)


NUMERIC_CODE_VALIDATOR = RegexValidator(
    regex=r"^\d+$",
    message=_("Only numeric characters are allowed."),
)

POSITIVE_DECIMAL = MinValueValidator(Decimal("0"))


class ProductionBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    class Meta:
        abstract = True


class ProductionSortableModel(ProductionBaseModel, SortableModel):
    class Meta:
        abstract = True


class WorkCenter(ProductionSortableModel):
    public_code = models.CharField(
        max_length=5,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=180)
    name_en = models.CharField(max_length=180, blank=True)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Work Center")
        verbose_name_plural = _("Work Centers")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="production_work_center_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="production_work_center_name_unique",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return f"{self.public_code} · {self.name}"


class BOMMaterial(ProductionBaseModel):
    finished_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="bom_materials",
    )
    finished_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    material_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="material_in_boms",
    )
    material_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    material_type = models.CharField(max_length=30, default="raw")
    quantity_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    unit = models.CharField(max_length=30)
    scrap_allowance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[POSITIVE_DECIMAL],
    )
    sequence_order = models.PositiveSmallIntegerField(default=0)
    is_optional = models.PositiveSmallIntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("BOM Material")
        verbose_name_plural = _("BOM Materials")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "finished_item", "material_item", "sequence_order"),
                name="production_bom_material_unique_order",
            ),
        ]
        ordering = ("company", "finished_item", "sequence_order")

    def __str__(self) -> str:
        return f"{self.finished_item_code} ← {self.material_item_code}"

    def save(self, *args, **kwargs):
        if not self.finished_item_code:
            self.finished_item_code = self.finished_item.item_code
        if not self.material_item_code:
            self.material_item_code = self.material_item.item_code
        super().save(*args, **kwargs)


class Process(ProductionSortableModel):
    process_code = models.CharField(max_length=30)
    finished_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="production_processes",
    )
    finished_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    bom_code = models.CharField(max_length=30)
    revision = models.CharField(max_length=10)
    description = models.CharField(max_length=255, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    is_primary = models.PositiveSmallIntegerField(default=0)
    approval_status = models.CharField(max_length=20, default="draft")
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        related_name="processes_approved",
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Production Process")
        verbose_name_plural = _("Production Processes")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "finished_item", "revision"),
                name="production_process_revision_unique",
            ),
        ]
        ordering = ("company", "finished_item", "sort_order", "revision")

    def __str__(self) -> str:
        return f"{self.process_code} · {self.revision}"

    def save(self, *args, **kwargs):
        if not self.finished_item_code:
            self.finished_item_code = self.finished_item.item_code
        super().save(*args, **kwargs)


class ProcessStep(ProductionSortableModel):
    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    work_center = models.ForeignKey(
        WorkCenter,
        on_delete=models.PROTECT,
        related_name="process_steps",
    )
    work_center_code = models.CharField(max_length=20)
    sequence_order = models.PositiveSmallIntegerField()
    personnel_requirements = models.JSONField(default=list, blank=True)
    labor_minutes_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    machine_minutes_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    setup_minutes = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Process Step")
        verbose_name_plural = _("Process Steps")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "process", "sequence_order"),
                name="production_process_step_sequence_unique",
            ),
        ]
        ordering = ("company", "process", "sequence_order")

    def __str__(self) -> str:
        return f"{self.process} · #{self.sequence_order}"

    def save(self, *args, **kwargs):
        if not self.work_center_code:
            self.work_center_code = self.work_center.public_code
        super().save(*args, **kwargs)


class ProductOrder(ProductionBaseModel):
    class Status(models.TextChoices):
        PLANNED = "planned", _("Planned")
        RELEASED = "released", _("Released")
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        NORMAL = "normal", _("Normal")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    order_code = models.CharField(max_length=30, unique=True)
    order_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    finished_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="production_orders",
    )
    finished_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    bom_code = models.CharField(max_length=30)
    process = models.ForeignKey(
        Process,
        on_delete=models.PROTECT,
        related_name="product_orders",
    )
    process_code = models.CharField(max_length=30)
    quantity_planned = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    unit = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    customer_reference = models.CharField(max_length=60, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Production Order")
        verbose_name_plural = _("Production Orders")
        ordering = ("-order_date", "order_code")

    def __str__(self) -> str:
        return self.order_code

    def save(self, *args, **kwargs):
        if not self.finished_item_code:
            self.finished_item_code = self.finished_item.item_code
        if not self.process_code:
            self.process_code = self.process.process_code
        super().save(*args, **kwargs)


class OrderPerformance(ProductionBaseModel):
    order = models.ForeignKey(
        ProductOrder,
        on_delete=models.CASCADE,
        related_name="performances",
    )
    order_code = models.CharField(max_length=30)
    finished_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="order_performances",
    )
    finished_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    report_date = models.DateField(default=timezone.now)
    quantity_produced = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    quantity_received = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    quantity_scrapped = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    unit_cycle_minutes = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    total_run_minutes = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    labor_usage = models.JSONField(default=list, blank=True)
    material_scrap = models.JSONField(default=list, blank=True)
    machine_usage_minutes = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    shift_id = models.BigIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Order Performance")
        verbose_name_plural = _("Order Performances")
        ordering = ("-report_date", "order")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "order", "report_date"),
                name="production_order_performance_unique_day",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order_code} · {self.report_date}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self.order.order_code
        if not self.finished_item_code:
            self.finished_item_code = self.finished_item.item_code
        super().save(*args, **kwargs)


class TransferToLine(ProductionBaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ISSUED = "issued", _("Issued")
        DELIVERED = "delivered", _("Delivered")
        CANCELLED = "cancelled", _("Cancelled")

    transfer_code = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey(
        ProductOrder,
        on_delete=models.PROTECT,
        related_name="transfers",
    )
    order_code = models.CharField(max_length=30)
    transfer_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Transfer To Line")
        verbose_name_plural = _("Transfers To Line")
        ordering = ("-transfer_date", "transfer_code")

    def __str__(self) -> str:
        return self.transfer_code

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self.order.order_code
        super().save(*args, **kwargs)


class TransferToLineItem(ProductionBaseModel):
    transfer = models.ForeignKey(
        TransferToLine,
        on_delete=models.CASCADE,
        related_name="items",
    )
    material_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="transfer_line_items",
    )
    material_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    quantity_required = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    quantity_transferred = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    unit = models.CharField(max_length=30)
    source_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        related_name="transfer_source_items",
    )
    source_warehouse_code = models.CharField(max_length=5, validators=[NUMERIC_CODE_VALIDATOR])
    destination_work_center = models.ForeignKey(
        WorkCenter,
        on_delete=models.PROTECT,
        related_name="transfer_items",
    )
    destination_location_code = models.CharField(max_length=30, blank=True)
    material_scrap_allowance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[POSITIVE_DECIMAL],
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Transfer To Line Item")
        verbose_name_plural = _("Transfer To Line Items")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "transfer", "material_item"),
                name="production_transfer_item_unique_material",
            ),
        ]
        ordering = ("company", "transfer", "material_item")

    def __str__(self) -> str:
        return f"{self.transfer} · {self.material_item_code}"

    def save(self, *args, **kwargs):
        if not self.material_item_code:
            self.material_item_code = self.material_item.item_code
        if not self.source_warehouse_code:
            self.source_warehouse_code = self.source_warehouse.public_code
        super().save(*args, **kwargs)

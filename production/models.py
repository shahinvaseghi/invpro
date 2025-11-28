from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shared.models import (
    ActivatableModel,
    CompanyScopedModel,
    CompanyUnit,
    ENABLED_FLAG_CHOICES,
    LockableModel,
    MetadataModel,
    NUMERIC_CODE_VALIDATOR,
    SortableModel,
    TimeStampedModel,
)

from inventory.utils.codes import generate_sequential_code


# Import Warehouse for WorkLine (optional dependency)
try:
    from inventory.models import Warehouse
except ImportError:
    Warehouse = None



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


class Person(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    SortableModel,
    MetadataModel,
):
    public_code = models.CharField(
        max_length=8,
        validators=[NUMERIC_CODE_VALIDATOR],
        editable=False,
    )
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    first_name_en = models.CharField(max_length=120, blank=True)
    last_name_en = models.CharField(max_length=120, blank=True)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    personnel_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="person_profile",
        null=True,
        blank=True,
    )
    company_units = models.ManyToManyField(
        CompanyUnit,
        blank=True,
        related_name="people",
    )

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        ordering = ("company", "sort_order", "public_code")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="production_person_company_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "username"),
                name="production_person_company_username_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "first_name", "last_name"),
                name="production_person_company_name_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=8,
            )
        super().save(*args, **kwargs)


class PersonAssignment(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    work_center_id = models.BigIntegerField()
    work_center_type = models.CharField(max_length=30)
    is_primary = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
    )
    assignment_start = models.DateField(null=True, blank=True)
    assignment_end = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Person Assignment")
        verbose_name_plural = _("Person Assignments")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "person", "work_center_id", "work_center_type"),
                name="production_person_assignment_unique_scope",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.person} → {self.work_center_type}:{self.work_center_id}"


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


class WorkLine(ProductionSortableModel):
    """
    Work Line - خط کاری
    Used in production module and optionally in inventory module (for consumption issues).
    Can be associated with a warehouse (if inventory module is installed).
    """
    public_code = models.CharField(
        max_length=5,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        related_name="work_lines",
        null=True,
        blank=True,
        help_text=_("Warehouse (optional, only if inventory module is installed)"),
    )
    name = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    personnel = models.ManyToManyField(
        'Person',
        related_name='work_lines',
        blank=True,
        help_text=_("Personnel assigned to this work line"),
    )
    machines = models.ManyToManyField(
        'Machine',
        related_name='work_lines',
        blank=True,
        help_text=_("Machines assigned to this work line"),
    )

    class Meta:
        verbose_name = _("Work Line")
        verbose_name_plural = _("Work Lines")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "warehouse", "public_code"),
                name="production_work_line_public_code_unique",
                condition=models.Q(warehouse__isnull=False),
            ),
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="production_work_line_public_code_unique_no_warehouse",
                condition=models.Q(warehouse__isnull=True),
            ),
            models.UniqueConstraint(
                fields=("company", "warehouse", "name"),
                name="production_work_line_name_unique",
                condition=models.Q(warehouse__isnull=False),
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="production_work_line_name_unique_no_warehouse",
                condition=models.Q(warehouse__isnull=True),
            ),
        ]
        ordering = ("company", "warehouse", "sort_order", "public_code")

    def __str__(self) -> str:
        if self.warehouse:
            return f"{self.warehouse} · {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=5,
            )
        super().save(*args, **kwargs)


class Machine(ProductionSortableModel):
    public_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        editable=False,
    )
    name = models.CharField(max_length=180)
    name_en = models.CharField(max_length=180, blank=True)
    machine_type = models.CharField(max_length=30)
    work_center = models.ForeignKey(
        WorkCenter,
        on_delete=models.SET_NULL,
        related_name="machines",
        null=True,
        blank=True,
    )
    work_center_code = models.CharField(max_length=5, blank=True)
    manufacturer = models.CharField(max_length=120, blank=True)
    model_number = models.CharField(max_length=60, blank=True)
    serial_number = models.CharField(max_length=60, unique=True, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    capacity_specs = models.JSONField(default=dict, blank=True)
    maintenance_schedule = models.JSONField(default=dict, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("operational", _("Operational")),
            ("maintenance", _("Maintenance")),
            ("idle", _("Idle")),
            ("broken", _("Broken")),
            ("retired", _("Retired")),
        ],
        default="operational",
    )
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Machine")
        verbose_name_plural = _("Machines")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="production_machine_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="production_machine_name_unique",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return f"{self.public_code} · {self.name}"

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=10,
            )
        if self.work_center and not self.work_center_code:
            self.work_center_code = self.work_center.public_code
        super().save(*args, **kwargs)


class BOM(ProductionBaseModel):
    """
    Bill of Materials Header - سند فهرست مواد اولیه
    Similar to ReceiptDocument/IssueDocument structure
    """
    bom_code = models.CharField(
        max_length=16,
        validators=[NUMERIC_CODE_VALIDATOR],
        unique=True,
    )
    finished_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="boms",
    )
    finished_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    version = models.CharField(max_length=10, default="1.0")
    is_active = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=1,
    )
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("BOM")
        verbose_name_plural = _("BOMs")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "finished_item", "version"),
                name="production_bom_unique_version",
            ),
        ]
        ordering = ("company", "finished_item", "-version")

    def __str__(self) -> str:
        return f"{self.bom_code} · {self.finished_item}"

    def save(self, *args, **kwargs):
        if not self.bom_code and self.company_id:
            self.bom_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                field='bom_code',
                width=16,
            )
        if not self.finished_item_code and self.finished_item_id:
            self.finished_item_code = self.finished_item.item_code
        super().save(*args, **kwargs)


class BOMMaterial(ProductionBaseModel):
    """
    BOM Material Line - خط فهرست مواد اولیه
    Similar to ReceiptLine/IssueLine structure
    """
    
    bom = models.ForeignKey(
        BOM,
        on_delete=models.CASCADE,
        related_name="materials",
    )
    material_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="material_in_boms",
    )
    material_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    material_type = models.ForeignKey(
        "inventory.ItemType",
        on_delete=models.PROTECT,
        related_name="bom_materials",
        verbose_name=_("Material Type"),
        help_text=_("Type/category of the material"),
    )
    quantity_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    unit = models.CharField(
        max_length=50,
        verbose_name=_("Unit"),
        help_text=_("Unit of measurement for this material"),
    )
    scrap_allowance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[POSITIVE_DECIMAL],
    )
    line_number = models.PositiveSmallIntegerField(default=1)
    is_optional = models.PositiveSmallIntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("BOM Material")
        verbose_name_plural = _("BOM Materials")
        constraints = [
            models.UniqueConstraint(
                fields=("bom", "material_item"),
                name="production_bom_material_unique",
            ),
            models.UniqueConstraint(
                fields=("bom", "line_number"),
                name="production_bom_material_line_unique",
            ),
        ]
        ordering = ("bom", "line_number")

    def __str__(self) -> str:
        return f"{self.bom.bom_code} · Line {self.line_number}"

    def save(self, *args, **kwargs):
        if not self.material_item_code and self.material_item_id:
            self.material_item_code = self.material_item.item_code
        # Auto-assign company from BOM
        if not self.company_id and self.bom_id:
            self.company_id = self.bom.company_id
        super().save(*args, **kwargs)


class Process(ProductionSortableModel):
    process_code = models.CharField(
        max_length=16,
        validators=[NUMERIC_CODE_VALIDATOR],
        editable=False,
    )
    finished_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="production_processes",
    )
    finished_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    bom = models.ForeignKey(
        "BOM",
        on_delete=models.PROTECT,
        related_name="processes",
        null=True,
        blank=True,
        help_text=_("Bill of Materials for this process"),
    )
    bom_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR], blank=True)
    work_lines = models.ManyToManyField(
        "WorkLine",
        related_name="processes",
        blank=True,
        help_text=_("Work lines assigned to this process"),
    )
    revision = models.CharField(max_length=10, blank=True)
    description = models.CharField(max_length=255, blank=True)
    is_primary = models.PositiveSmallIntegerField(default=0)
    approval_status = models.CharField(max_length=20, default="draft")
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="processes_approved",
        null=True,
        blank=True,
        help_text=_("User who approved this process"),
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Production Process")
        verbose_name_plural = _("Production Processes")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "finished_item", "revision"),
                name="production_process_revision_unique",
                condition=~models.Q(revision=''),
            ),
        ]
        ordering = ("company", "finished_item", "sort_order", "revision")

    def __str__(self) -> str:
        return f"{self.process_code} · {self.revision}"

    def save(self, *args, **kwargs):
        if not self.process_code and self.company_id:
            self.process_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=16,
                field='process_code',
            )
        if not self.finished_item_code and self.finished_item:
            self.finished_item_code = self.finished_item.item_code
        if self.bom and not self.bom_code:
            self.bom_code = self.bom.bom_code
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
    machine = models.ForeignKey(
        Machine,
        on_delete=models.SET_NULL,
        related_name="process_steps",
        null=True,
        blank=True,
    )
    machine_code = models.CharField(max_length=10, blank=True)
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
        if self.machine and not self.machine_code:
            self.machine_code = self.machine.public_code
        super().save(*args, **kwargs)


class ProcessOperation(ProductionBaseModel):
    """
    Production Operation - عملیات تولید
    Each process can have multiple operations that define the production steps.
    """
    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        related_name="operations",
        help_text=_("Production process this operation belongs to"),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Name of the operation"),
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Description of the operation"),
    )
    sequence_order = models.PositiveSmallIntegerField(
        default=1,
        help_text=_("Execution order (can be same for parallel operations)"),
    )
    labor_minutes_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        help_text=_("Labor minutes required per unit"),
    )
    machine_minutes_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("Machine minutes required per unit"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes for this operation"),
    )

    class Meta:
        verbose_name = _("Process Operation")
        verbose_name_plural = _("Process Operations")
        ordering = ("company", "process", "sequence_order", "id")
        indexes = [
            models.Index(fields=["process", "sequence_order"]),
        ]

    def __str__(self) -> str:
        name = self.name or f"Operation {self.sequence_order}"
        return f"{self.process.process_code} · {name} · Seq: {self.sequence_order}"

    def save(self, *args, **kwargs):
        # Auto-assign company from process
        if not self.company_id and self.process_id:
            self.company_id = self.process.company_id
        super().save(*args, **kwargs)


class ProcessOperationMaterial(ProductionBaseModel):
    """
    Materials used in a production operation - مواد استفاده شده در عملیات
    Links BOMMaterial to ProcessOperation with quantity used in that operation.
    """
    operation = models.ForeignKey(
        ProcessOperation,
        on_delete=models.CASCADE,
        related_name="operation_materials",
        help_text=_("Production operation"),
    )
    bom_material = models.ForeignKey(
        "BOMMaterial",
        on_delete=models.PROTECT,
        related_name="operation_usages",
        help_text=_("BOM material being used"),
    )
    material_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="operation_materials",
        help_text=_("Material item (cached from BOM material)"),
    )
    material_item_code = models.CharField(
        max_length=16,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("Material item code (cached)"),
    )
    quantity_used = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        help_text=_("Quantity used in this operation"),
    )
    unit = models.CharField(
        max_length=50,
        help_text=_("Unit of measurement (cached from BOM material)"),
    )

    class Meta:
        verbose_name = _("Process Operation Material")
        verbose_name_plural = _("Process Operation Materials")
        constraints = [
            models.UniqueConstraint(
                fields=("operation", "bom_material"),
                name="production_operation_material_unique",
            ),
        ]
        ordering = ("operation", "id")

    def __str__(self) -> str:
        return f"{self.operation} · {self.material_item_code} · {self.quantity_used} {self.unit}"

    def save(self, *args, **kwargs):
        # Auto-assign company from operation
        if not self.company_id and self.operation_id:
            self.company_id = self.operation.company_id
        
        # Cache values from BOM material if not set
        if self.bom_material_id:
            if not self.material_item_id:
                self.material_item = self.bom_material.material_item
            if not self.material_item_code:
                self.material_item_code = self.bom_material.material_item_code
            if not self.unit:
                self.unit = self.bom_material.unit
        
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
    bom = models.ForeignKey(
        "BOM",
        on_delete=models.PROTECT,
        related_name="product_orders",
        verbose_name=_("BOM"),
        help_text=_("Bill of Materials for this order"),
        null=True,
        blank=True,
    )
    bom_code = models.CharField(max_length=30)
    process = models.ForeignKey(
        Process,
        on_delete=models.PROTECT,
        related_name="product_orders",
        null=True,
        blank=True,
    )
    process_code = models.CharField(max_length=30, blank=True)
    quantity_planned = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    unit = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_product_orders",
        null=True,
        blank=True,
        verbose_name=_("Approver"),
        help_text=_("User who can approve this order"),
    )
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
        if self.bom and not self.bom_code:
            self.bom_code = self.bom.bom_code
        if self.process and not self.process_code:
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


class TransferToLine(ProductionBaseModel, LockableModel):
    class Status(models.TextChoices):
        PENDING_APPROVAL = "pending_approval", _("Pending Approval")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    transfer_code = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey(
        ProductOrder,
        on_delete=models.PROTECT,
        related_name="transfers",
    )
    order_code = models.CharField(max_length=30)
    transfer_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_APPROVAL)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_transfers",
        null=True,
        blank=True,
        verbose_name=_("Approver"),
        help_text=_("User who can approve this transfer request"),
    )
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
        null=True,
        blank=True,
    )
    destination_location_code = models.CharField(max_length=30, blank=True)
    material_scrap_allowance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[POSITIVE_DECIMAL],
    )
    is_extra = models.PositiveSmallIntegerField(
        default=0,
        choices=ENABLED_FLAG_CHOICES,
        verbose_name=_("Extra Request"),
        help_text=_("Whether this item is an extra request (not from BOM)"),
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


class PerformanceRecord(ProductionBaseModel, LockableModel):
    """
    Performance Record - سند عملکرد
    Records production performance for a product order including material waste,
    actual production quantity, labor time, and machine usage.
    """
    class Status(models.TextChoices):
        PENDING_APPROVAL = "pending_approval", _("Pending Approval")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    performance_code = models.CharField(max_length=30, unique=True)
    order = models.ForeignKey(
        ProductOrder,
        on_delete=models.PROTECT,
        related_name="performance_records",
        verbose_name=_("Product Order"),
        help_text=_("The product order this performance record is for"),
    )
    order_code = models.CharField(max_length=30)
    transfer = models.ForeignKey(
        TransferToLine,
        on_delete=models.PROTECT,
        related_name="performance_records",
        null=True,
        blank=True,
        verbose_name=_("Transfer to Line"),
        help_text=_("The transfer document used for this order (optional)"),
    )
    transfer_code = models.CharField(max_length=30, blank=True)
    performance_date = models.DateField(default=timezone.now)
    quantity_planned = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        verbose_name=_("Planned Quantity"),
        help_text=_("The planned quantity from the order"),
    )
    quantity_actual = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        verbose_name=_("Actual Quantity Produced"),
        help_text=_("The actual quantity produced (may be less than planned due to waste)"),
    )
    finished_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="performance_records",
    )
    finished_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_APPROVAL)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_performance_records",
        null=True,
        blank=True,
        verbose_name=_("Approver"),
        help_text=_("User who can approve this performance record"),
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Performance Record")
        verbose_name_plural = _("Performance Records")
        ordering = ("-performance_date", "performance_code")

    def __str__(self) -> str:
        return self.performance_code

    def save(self, *args, **kwargs):
        # performance_code will be generated in view (like transfer_code)
        # We don't generate it here to allow view to add prefix
        if not self.order_code:
            self.order_code = self.order.order_code
        if not self.quantity_planned:
            self.quantity_planned = self.order.quantity_planned
        if not self.finished_item_code:
            self.finished_item_code = self.order.finished_item.item_code
        if not self.finished_item_id:
            self.finished_item = self.order.finished_item
        if not self.unit:
            self.unit = self.order.unit
        if self.transfer and not self.transfer_code:
            self.transfer_code = self.transfer.transfer_code
        super().save(*args, **kwargs)


class PerformanceRecordMaterial(ProductionBaseModel):
    """
    Performance Record Material - ردیف مواد سند عملکرد
    Tracks material waste for each material item used in production.
    """
    performance = models.ForeignKey(
        PerformanceRecord,
        on_delete=models.CASCADE,
        related_name="materials",
    )
    material_item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="performance_record_materials",
    )
    material_item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    quantity_required = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        verbose_name=_("Required Quantity"),
        help_text=_("Quantity required from transfer document"),
    )
    quantity_waste = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
        verbose_name=_("Waste Quantity"),
        help_text=_("Quantity wasted during production"),
    )
    unit = models.CharField(max_length=30)
    is_extra = models.PositiveSmallIntegerField(
        default=0,
        choices=ENABLED_FLAG_CHOICES,
        verbose_name=_("Extra Material"),
        help_text=_("Whether this is an extra material (not from BOM)"),
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Performance Record Material")
        verbose_name_plural = _("Performance Record Materials")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "performance", "material_item"),
                name="production_performance_material_unique",
            ),
        ]
        ordering = ("company", "performance", "material_item")

    def __str__(self) -> str:
        return f"{self.performance} · {self.material_item_code}"

    def save(self, *args, **kwargs):
        if not self.material_item_code:
            self.material_item_code = self.material_item.item_code
        super().save(*args, **kwargs)


class PerformanceRecordPerson(ProductionBaseModel):
    """
    Performance Record Person - ردیف پرسنل سند عملکرد
    Tracks labor time for each person working on the order.
    """
    performance = models.ForeignKey(
        PerformanceRecord,
        on_delete=models.CASCADE,
        related_name="persons",
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="performance_records",
    )
    person_code = models.CharField(max_length=8, validators=[NUMERIC_CODE_VALIDATOR])
    work_minutes = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        verbose_name=_("Work Minutes"),
        help_text=_("Number of minutes this person worked on this order"),
    )
    work_line = models.ForeignKey(
        WorkLine,
        on_delete=models.SET_NULL,
        related_name="performance_record_persons",
        null=True,
        blank=True,
        verbose_name=_("Work Line"),
        help_text=_("Work line where this person worked"),
    )
    work_line_code = models.CharField(max_length=5, validators=[NUMERIC_CODE_VALIDATOR], blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Performance Record Person")
        verbose_name_plural = _("Performance Record Persons")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "performance", "person"),
                name="production_performance_person_unique",
            ),
        ]
        ordering = ("company", "performance", "person")

    def __str__(self) -> str:
        return f"{self.performance} · {self.person_code}"

    def save(self, *args, **kwargs):
        if not self.person_code:
            self.person_code = self.person.public_code
        if self.work_line and not self.work_line_code:
            self.work_line_code = self.work_line.public_code
        super().save(*args, **kwargs)


class PerformanceRecordMachine(ProductionBaseModel):
    """
    Performance Record Machine - ردیف ماشین سند عملکرد
    Tracks machine usage time for each machine used in production.
    """
    performance = models.ForeignKey(
        PerformanceRecord,
        on_delete=models.CASCADE,
        related_name="machines",
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT,
        related_name="performance_records",
    )
    machine_code = models.CharField(max_length=10, validators=[NUMERIC_CODE_VALIDATOR])
    work_minutes = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        verbose_name=_("Work Minutes"),
        help_text=_("Number of minutes this machine was used"),
    )
    work_line = models.ForeignKey(
        WorkLine,
        on_delete=models.SET_NULL,
        related_name="performance_record_machines",
        null=True,
        blank=True,
        verbose_name=_("Work Line"),
        help_text=_("Work line where this machine was used"),
    )
    work_line_code = models.CharField(max_length=5, validators=[NUMERIC_CODE_VALIDATOR], blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Performance Record Machine")
        verbose_name_plural = _("Performance Record Machines")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "performance", "machine"),
                name="production_performance_machine_unique",
            ),
        ]
        ordering = ("company", "performance", "machine")

    def __str__(self) -> str:
        return f"{self.performance} · {self.machine_code}"

    def save(self, *args, **kwargs):
        if not self.machine_code:
            self.machine_code = self.machine.public_code
        if self.work_line and not self.work_line_code:
            self.work_line_code = self.work_line.public_code
        super().save(*args, **kwargs)

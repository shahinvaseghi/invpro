from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shared.models import (
    ActivatableModel,
    CompanyUnit,
    CompanyScopedModel,
    LockableModel,
    MetadataModel,
    SortableModel,
    TimeStampedModel,
    User,
)
from .utils.codes import generate_sequential_code


NUMERIC_CODE_VALIDATOR = RegexValidator(
    regex=r"^\d+$",
    message=_("Only numeric characters are allowed."),
)

POSITIVE_DECIMAL = MinValueValidator(Decimal("0"))

CURRENCY_CHOICES = (
    ("IRT", _("Toman")),
    ("IRR", _("Rial")),
    ("USD", _("US Dollar")),
)


class InventoryBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    class Meta:
        abstract = True


class InventorySortableModel(InventoryBaseModel, SortableModel):
    class Meta:
        abstract = True


class InventoryDocumentBase(InventoryBaseModel, LockableModel):
    public_code_validator = NUMERIC_CODE_VALIDATOR

    document_code = models.CharField(max_length=30, unique=True)
    document_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True


class ItemType(InventorySortableModel):
    public_code = models.CharField(
        max_length=3,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Type")
        verbose_name_plural = _("Item Types")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="inventory_item_type_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="inventory_item_type_name_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name_en"),
                name="inventory_item_type_name_en_unique",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=3,
            )
        super().save(*args, **kwargs)


class ItemCategory(InventorySortableModel):
    public_code = models.CharField(
        max_length=3,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Category")
        verbose_name_plural = _("Item Categories")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="inventory_item_category_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="inventory_item_category_name_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name_en"),
                name="inventory_item_category_name_en_unique",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=3,
            )
        super().save(*args, **kwargs)


class ItemSubcategory(InventorySortableModel):
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )
    public_code = models.CharField(
        max_length=3,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Subcategory")
        verbose_name_plural = _("Item Subcategories")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "category", "public_code"),
                name="inventory_item_subcategory_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "category", "name"),
                name="inventory_item_subcategory_name_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "category", "name_en"),
                name="inventory_item_subcategory_name_en_unique",
            ),
        ]
        ordering = ("company", "category", "sort_order", "public_code")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id and self.category_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=3,
                extra_filters={"category": self.category},
            )
        super().save(*args, **kwargs)


class Warehouse(InventorySortableModel):
    public_code = models.CharField(
        max_length=5,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    location_label = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="inventory_warehouse_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="inventory_warehouse_name_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name_en"),
                name="inventory_warehouse_name_en_unique",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=5,
            )
        super().save(*args, **kwargs)


# WorkLine moved to production module
# Import it here for backward compatibility in IssueConsumptionLine
try:
    from production.models import WorkLine
except ImportError:
    # If production module is not installed, WorkLine won't be available
    WorkLine = None


class Item(InventorySortableModel):
    type = models.ForeignKey(
        ItemType,
        on_delete=models.PROTECT,
        related_name="items",
    )
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.PROTECT,
        related_name="items",
    )
    subcategory = models.ForeignKey(
        ItemSubcategory,
        on_delete=models.PROTECT,
        related_name="items",
    )
    type_code = models.CharField(max_length=3, validators=[NUMERIC_CODE_VALIDATOR], editable=False)
    category_code = models.CharField(max_length=3, validators=[NUMERIC_CODE_VALIDATOR], editable=False)
    subcategory_code = models.CharField(max_length=3, validators=[NUMERIC_CODE_VALIDATOR], editable=False)
    user_segment = models.CharField(max_length=2, validators=[NUMERIC_CODE_VALIDATOR])
    sequence_segment = models.CharField(max_length=5, validators=[NUMERIC_CODE_VALIDATOR], editable=False)
    item_code = models.CharField(max_length=7, validators=[NUMERIC_CODE_VALIDATOR], blank=True, help_text="7-digit code: User(2) + Sequence(5)")
    full_item_code = models.CharField(max_length=16, unique=True, validators=[NUMERIC_CODE_VALIDATOR], blank=True, help_text="16-digit complete code: Type(3) + Category(3) + SubCategory(3) + ItemCode(7)")
    batch_number = models.CharField(max_length=20)
    secondary_batch_number = models.CharField(max_length=50, blank=True, help_text=_("User-defined secondary batch number"))
    name = models.CharField(max_length=180, unique=True)
    name_en = models.CharField(max_length=180, unique=True)
    is_sellable = models.PositiveSmallIntegerField(default=0)
    has_lot_tracking = models.PositiveSmallIntegerField(default=0)
    requires_temporary_receipt = models.PositiveSmallIntegerField(default=0)
    tax_id = models.CharField(max_length=30, blank=True)
    tax_title = models.CharField(max_length=120, blank=True)
    min_stock = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    default_unit = models.CharField(max_length=30)
    default_unit_id = models.BigIntegerField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    primary_unit = models.CharField(max_length=30)
    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        ordering = ("company", "sort_order", "item_code")

    def __str__(self) -> str:
        return f"{self.item_code} · {self.name}"

    def save(self, *args, **kwargs):
        # Copy codes from type, category, subcategory if not set
        if self.type and not self.type_code:
            self.type_code = self.type.public_code
        if self.category and not self.category_code:
            self.category_code = self.category.public_code
        if self.subcategory and not self.subcategory_code:
            self.subcategory_code = self.subcategory.public_code
        
        # Generate sequence_segment if not set
        if not self.sequence_segment:
            self.sequence_segment = self._generate_sequence_segment()
        
        # Generate item_code if not set
        if not self.item_code:
            # Item code: User(2) + Sequence(5) = 7 digits
            self.item_code = f"{self.user_segment}{self.sequence_segment}"
        
        # Generate full_item_code if not set
        if not self.full_item_code:
            # Full item code: Type(3) + Category(3) + SubCategory(3) + ItemCode(7) = 16 digits
            self.full_item_code = f"{self.type_code}{self.category_code}{self.subcategory_code}{self.item_code}"
        
        # Generate batch_number if not set
        if not self.batch_number:
            self.batch_number = self._generate_batch_number()
        
        super().save(*args, **kwargs)

    def _generate_sequence_segment(self) -> str:
        queryset = Item.objects.filter(
            company=self.company,
            type=self.type,
            category=self.category,
            subcategory=self.subcategory,
            user_segment=self.user_segment,
        ).exclude(pk=self.pk)
        last_value = queryset.order_by("-sequence_segment").values_list("sequence_segment", flat=True).first()
        if last_value:
            return str(int(last_value) + 1).zfill(5)
        return "00001"

    def _generate_batch_number(self) -> str:
        now = timezone.now()
        prefix = now.strftime("%m%y")
        queryset = Item.objects.filter(
            company=self.company,
            batch_number__startswith=prefix,
        ).exclude(pk=self.pk)
        last = queryset.order_by("-batch_number").values_list("batch_number", flat=True).first()
        if last:
            sequence = int(last.split("-")[-1]) + 1
        else:
            sequence = 1
        return f"{prefix}-{str(sequence).zfill(6)}"


class ItemSpec(InventorySortableModel):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="specifications",
    )
    item_code = models.CharField(max_length=30)
    supplier_name = models.CharField(max_length=180, blank=True)
    spec_data = models.JSONField(default=dict, blank=True)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Specification")
        verbose_name_plural = _("Item Specifications")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "item", "sort_order"),
                name="inventory_item_spec_sort_order_unique",
            ),
        ]
        ordering = ("company", "item", "sort_order")

    def __str__(self) -> str:
        return f"{self.item} · {self.description or _('Specification')}"

    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = self.item.item_code
        super().save(*args, **kwargs)


class ItemUnit(InventorySortableModel):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="units",
    )
    item_code = models.CharField(max_length=30)
    public_code = models.CharField(
        max_length=6,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    from_unit = models.CharField(max_length=30)
    from_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("1.0"),
        validators=[POSITIVE_DECIMAL],
    )
    to_unit = models.CharField(max_length=30)
    to_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    is_primary = models.PositiveSmallIntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Unit Conversion")
        verbose_name_plural = _("Item Unit Conversions")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "item", "from_unit", "to_unit"),
                name="inventory_item_unit_unique_conversion",
            ),
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="inventory_item_unit_public_code_unique",
            ),
        ]
        ordering = ("company", "item", "sort_order")

    def __str__(self) -> str:
        return f"{self.item} · {self.from_unit}->{self.to_unit}"

    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = self.item.item_code
        super().save(*args, **kwargs)


class ItemWarehouse(InventoryBaseModel):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="warehouses",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="items",
    )
    is_primary = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Warehouse")
        verbose_name_plural = _("Item Warehouses")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "item", "warehouse"),
                name="inventory_item_warehouse_unique_pair",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.item} @ {self.warehouse}"


class ItemSubstitute(InventorySortableModel):
    source_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="substitutions",
    )
    source_item_code = models.CharField(max_length=30)
    source_unit = models.CharField(max_length=30)
    source_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("1.0"),
        validators=[POSITIVE_DECIMAL],
    )
    target_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="substituted_in",
    )
    target_item_code = models.CharField(max_length=30)
    target_unit = models.CharField(max_length=30)
    target_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    is_bidirectional = models.PositiveSmallIntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Substitute")
        verbose_name_plural = _("Item Substitutes")
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "company",
                    "source_item",
                    "target_item",
                    "source_unit",
                    "target_unit",
                ),
                name="inventory_item_substitute_unique_pair",
            ),
        ]
        ordering = ("company", "source_item", "sort_order")

    def __str__(self) -> str:
        return f"{self.source_item} → {self.target_item}"

    def save(self, *args, **kwargs):
        if not self.source_item_code:
            self.source_item_code = self.source_item.item_code
        if not self.target_item_code:
            self.target_item_code = self.target_item.item_code
        super().save(*args, **kwargs)


class Supplier(InventorySortableModel):
    public_code = models.CharField(
        max_length=6,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=180)
    name_en = models.CharField(max_length=180, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=3, blank=True)
    tax_id = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="inventory_supplier_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="inventory_supplier_name_unique",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=6,
            )
        super().save(*args, **kwargs)


class SupplierCategory(InventoryBaseModel):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.CASCADE,
        related_name="suppliers",
    )
    is_primary = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Supplier Category")
        verbose_name_plural = _("Supplier Categories")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "supplier", "category"),
                name="inventory_supplier_category_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.supplier.name} - {self.category.name}"


class SupplierSubcategory(InventoryBaseModel):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )
    subcategory = models.ForeignKey(
        ItemSubcategory,
        on_delete=models.CASCADE,
        related_name="suppliers",
    )
    is_primary = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Supplier Subcategory")
        verbose_name_plural = _("Supplier Subcategories")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "supplier", "subcategory"),
                name="inventory_supplier_subcategory_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.supplier.name} - {self.subcategory.name}"


class SupplierItem(InventoryBaseModel):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="suppliers",
    )
    is_primary = models.PositiveSmallIntegerField(default=0)
    min_order_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    lead_time_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    price_metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Supplier Item")
        verbose_name_plural = _("Supplier Items")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "supplier", "item"),
                name="inventory_supplier_item_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.item} by {self.supplier}"


class PurchaseRequest(InventoryBaseModel, LockableModel):
    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        NORMAL = "normal", _("Normal")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        APPROVED = "approved", _("Approved")
        ORDERED = "ordered", _("Ordered")
        FULFILLED = "fulfilled", _("Fulfilled")
        CANCELLED = "cancelled", _("Cancelled")

    request_code = models.CharField(max_length=20, unique=True)
    request_date = models.DateField(default=timezone.now)
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="purchase_requests",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="purchase_requests",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(max_length=30)
    quantity_requested = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    quantity_fulfilled = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    needed_by_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    reason_code = models.CharField(max_length=30, blank=True)
    reference_document_type = models.CharField(max_length=30, blank=True)
    reference_document_id = models.BigIntegerField(null=True, blank=True)
    reference_document_code = models.CharField(max_length=30, blank=True)
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="purchase_requests_approved",
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    request_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Purchase Request")
        verbose_name_plural = _("Purchase Requests")
        ordering = ("-request_date", "request_code")

    def __str__(self) -> str:
        return f"{self.request_code} · {self.item}"

    def _generate_request_code(self) -> str:
        """
        Generates a unique code following the pattern PRQ-YYYYMM-XXXXXX scoped per company.
        """
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"PRQ-{month_year}"
        last_request = (
            PurchaseRequest.objects.filter(
                company_id=self.company_id,
                request_code__startswith=prefix,
            )
            .order_by("-request_code")
            .first()
        )
        if last_request and last_request.request_code:
            try:
                sequence = int(last_request.request_code.split("-")[-1])
            except (ValueError, IndexError):
                sequence = 0
        else:
            sequence = 0
        return f"{prefix}-{sequence + 1:06d}"

    def save(self, *args, **kwargs):
        if not self.request_code:
            self.request_code = self._generate_request_code()
        if not self.item_code:
            self.item_code = self.item.item_code
        super().save(*args, **kwargs)


class ReceiptTemporary(InventoryBaseModel, LockableModel):
    class Status(models.IntegerChoices):
        DRAFT = 0, _("Draft")
        AWAITING_INSPECTION = 1, _("Awaiting inspection")
        CLOSED = 2, _("Closed/Cancelled")

    document_code = models.CharField(max_length=20, unique=True)
    document_date = models.DateField(default=timezone.now)
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="temporary_receipts",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="temporary_receipts",
    )
    warehouse_code = models.CharField(max_length=5, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(max_length=30)
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    expected_receipt_date = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="temporary_receipts",
        null=True,
        blank=True,
    )
    supplier_code = models.CharField(max_length=6, validators=[NUMERIC_CODE_VALIDATOR], blank=True)
    source_document_type = models.CharField(max_length=60, blank=True)
    source_document_code = models.CharField(max_length=30, blank=True)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.DRAFT)
    inspection_result = models.JSONField(default=dict, blank=True)
    document_metadata = models.JSONField(default=dict, blank=True)
    qc_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="temporary_receipts_qc_approved",
        null=True,
        blank=True,
    )
    qc_approved_at = models.DateTimeField(null=True, blank=True)
    qc_approval_notes = models.TextField(blank=True)
    is_converted = models.PositiveSmallIntegerField(default=0)
    converted_receipt = models.OneToOneField(
        "ReceiptPermanent",
        on_delete=models.SET_NULL,
        related_name="temporary_conversion",
        null=True,
        blank=True,
    )
    converted_receipt_code = models.CharField(max_length=20, blank=True)
    entered_unit = models.CharField(max_length=30, blank=True)
    entered_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[POSITIVE_DECIMAL],
    )

    class Meta:
        verbose_name = _("Temporary Receipt")
        verbose_name_plural = _("Temporary Receipts")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = self.item.item_code
        if not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        if self.supplier and not self.supplier_code:
            self.supplier_code = self.supplier.public_code
        super().save(*args, **kwargs)


class ReceiptPermanent(InventoryDocumentBase):
    """Header-only model for permanent receipt documents with multi-line support."""
    document_code = models.CharField(max_length=20, unique=True)
    document_date = models.DateField(default=timezone.now)
    # Header-level fields only - item/warehouse/quantity moved to ReceiptPermanentLine
    requires_temporary_receipt = models.PositiveSmallIntegerField(default=0)
    temporary_receipt = models.ForeignKey(
        ReceiptTemporary,
        on_delete=models.SET_NULL,
        related_name="permanent_receipts",
        null=True,
        blank=True,
    )
    temporary_receipt_code = models.CharField(max_length=20, blank=True)
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.SET_NULL,
        related_name="permanent_receipts",
        null=True,
        blank=True,
    )
    purchase_request_code = models.CharField(max_length=20, blank=True)
    warehouse_request = models.ForeignKey(
        "WarehouseRequest",
        on_delete=models.SET_NULL,
        related_name="permanent_receipts",
        null=True,
        blank=True,
    )
    warehouse_request_code = models.CharField(max_length=20, blank=True)
    document_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Permanent Receipt")
        verbose_name_plural = _("Permanent Receipts")
        ordering = ("-id", "-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if self.temporary_receipt and not self.temporary_receipt_code:
            self.temporary_receipt_code = self.temporary_receipt.document_code
        if self.purchase_request and not self.purchase_request_code:
            self.purchase_request_code = self.purchase_request.request_code
        if self.warehouse_request and not self.warehouse_request_code:
            self.warehouse_request_code = self.warehouse_request.request_code
        super().save(*args, **kwargs)


class ReceiptConsignment(InventoryDocumentBase):
    """Header-only model for consignment receipt documents with multi-line support."""
    document_code = models.CharField(max_length=20, unique=True)
    document_date = models.DateField(default=timezone.now)
    # Header-level fields only - item/warehouse/quantity moved to ReceiptConsignmentLine
    consignment_contract_code = models.CharField(max_length=30, blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    valuation_method = models.CharField(max_length=30, blank=True)
    requires_temporary_receipt = models.PositiveSmallIntegerField(default=0)
    temporary_receipt = models.ForeignKey(
        ReceiptTemporary,
        on_delete=models.SET_NULL,
        related_name="consignment_receipts",
        null=True,
        blank=True,
    )
    temporary_receipt_code = models.CharField(max_length=20, blank=True)
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.SET_NULL,
        related_name="consignment_receipts",
        null=True,
        blank=True,
    )
    purchase_request_code = models.CharField(max_length=20, blank=True)
    warehouse_request = models.ForeignKey(
        "WarehouseRequest",
        on_delete=models.SET_NULL,
        related_name="consignment_receipts",
        null=True,
        blank=True,
    )
    warehouse_request_code = models.CharField(max_length=20, blank=True)
    ownership_status = models.CharField(max_length=30, default="consigned")
    conversion_receipt = models.ForeignKey(
        "ReceiptPermanent",
        on_delete=models.SET_NULL,
        related_name="consignment_conversions",
        null=True,
        blank=True,
    )
    conversion_receipt_code = models.CharField(max_length=20, blank=True)
    conversion_date = models.DateField(null=True, blank=True)
    return_document_id = models.BigIntegerField(null=True, blank=True)
    document_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Consignment Receipt")
        verbose_name_plural = _("Consignment Receipts")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if self.temporary_receipt and not self.temporary_receipt_code:
            self.temporary_receipt_code = self.temporary_receipt.document_code
        if self.purchase_request and not self.purchase_request_code:
            self.purchase_request_code = self.purchase_request.request_code
        if self.warehouse_request and not self.warehouse_request_code:
            self.warehouse_request_code = self.warehouse_request.request_code
        if self.conversion_receipt and not self.conversion_receipt_code:
            self.conversion_receipt_code = self.conversion_receipt.document_code
        super().save(*args, **kwargs)


class ItemLot(InventoryBaseModel):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="lots",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    lot_code = models.CharField(max_length=30, unique=True)
    batch_number = models.CharField(max_length=20)
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("1.0"),
        validators=[POSITIVE_DECIMAL],
    )
    unit = models.CharField(max_length=30)
    status = models.CharField(max_length=20, default="available")
    receipt_document = models.ForeignKey(
        ReceiptPermanent,
        on_delete=models.CASCADE,
        related_name="lots",
    )
    receipt_document_code = models.CharField(max_length=20)
    issue_document_type = models.CharField(max_length=30, blank=True)
    issue_document_id = models.BigIntegerField(null=True, blank=True)
    issue_document_code = models.CharField(max_length=20, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Item Lot")
        verbose_name_plural = _("Item Lots")
        ordering = ("company", "item", "lot_code")

    def __str__(self) -> str:
        return self.lot_code

    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = self.item.item_code
        if not self.batch_number:
            self.batch_number = self.item.batch_number
        if not self.lot_code:
            self.lot_code = self._generate_lot_code()
        if not self.receipt_document_code:
            self.receipt_document_code = self.receipt_document.document_code
        super().save(*args, **kwargs)

    def _generate_lot_code(self) -> str:
        now = timezone.now()
        prefix = now.strftime("LOT-%m%y")
        queryset = ItemLot.objects.filter(
            company=self.company,
            lot_code__startswith=prefix,
        ).exclude(pk=self.pk)
        last = queryset.order_by("-lot_code").values_list("lot_code", flat=True).first()
        if last:
            sequence = int(last.split("-")[-1]) + 1
        else:
            sequence = 1
        return f"{prefix}-{str(sequence).zfill(6)}"


class ItemSerial(InventoryBaseModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", _("Available")
        RESERVED = "reserved", _("Reserved")
        ISSUED = "issued", _("Issued")
        CONSUMED = "consumed", _("Consumed")
        RETURNED = "returned", _("Returned")
        DAMAGED = "damaged", _("Damaged")

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="serials",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    lot = models.ForeignKey(
        ItemLot,
        on_delete=models.SET_NULL,
        related_name="serials",
        null=True,
        blank=True,
    )
    lot_code = models.CharField(max_length=30, blank=True)
    serial_code = models.CharField(max_length=50, unique=True)
    secondary_serial_code = models.CharField(max_length=50, blank=True, help_text=_("User-defined secondary serial number"))
    receipt_document = models.ForeignKey(
        "ReceiptPermanent",
        on_delete=models.PROTECT,
        related_name="serials",
    )
    receipt_document_code = models.CharField(max_length=20)
    receipt_line_reference = models.CharField(max_length=30, blank=True)
    current_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    current_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        related_name="serials",
        null=True,
        blank=True,
    )
    current_warehouse_code = models.CharField(max_length=5, blank=True)
    current_company_unit = models.ForeignKey(
        CompanyUnit,
        on_delete=models.SET_NULL,
        related_name="serials",
        null=True,
        blank=True,
    )
    current_company_unit_code = models.CharField(max_length=8, blank=True)
    current_document_type = models.CharField(max_length=30, blank=True)
    current_document_id = models.BigIntegerField(null=True, blank=True)
    current_document_code = models.CharField(max_length=30, blank=True)
    last_moved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Item Serial")
        verbose_name_plural = _("Item Serials")
        ordering = ("company", "item_code", "serial_code")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "serial_code"),
                name="inventory_item_serial_code_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=("company", "item", "current_status"),
                name="inv_item_serial_status_idx",
            ),
            models.Index(
                fields=("company", "receipt_document"),
                name="inv_item_serial_receipt_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.serial_code

    def save(self, *args, **kwargs):
        if self.item and not self.item_code:
            self.item_code = self.item.item_code
        if self.lot and not self.lot_code:
            self.lot_code = self.lot.lot_code
        if self.receipt_document and not self.receipt_document_code:
            self.receipt_document_code = self.receipt_document.document_code
        if self.current_warehouse and not self.current_warehouse_code:
            self.current_warehouse_code = self.current_warehouse.public_code
        if self.current_company_unit and not self.current_company_unit_code:
            self.current_company_unit_code = self.current_company_unit.public_code
        super().save(*args, **kwargs)


class ItemSerialHistory(InventoryBaseModel):
    class EventType(models.TextChoices):
        CREATED = "created", _("Created")
        RESERVED = "reserved", _("Reserved")
        RELEASED = "released", _("Reservation Released")
        ISSUED = "issued", _("Issued")
        CONSUMED = "consumed", _("Consumed")
        RETURNED = "returned", _("Returned")
        ADJUSTED = "adjusted", _("Adjusted")

    serial = models.ForeignKey(
        ItemSerial,
        on_delete=models.CASCADE,
        related_name="history",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="serial_history",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    event_at = models.DateTimeField(default=timezone.now)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    reference_document_type = models.CharField(max_length=30, blank=True)
    reference_document_code = models.CharField(max_length=30, blank=True)
    reference_document_id = models.BigIntegerField(null=True, blank=True)
    from_warehouse_code = models.CharField(max_length=5, blank=True)
    to_warehouse_code = models.CharField(max_length=5, blank=True)
    from_company_unit_code = models.CharField(max_length=8, blank=True)
    to_company_unit_code = models.CharField(max_length=8, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Item Serial History")
        verbose_name_plural = _("Item Serial History")
        ordering = ("-event_at", "-id")
        indexes = [
            models.Index(
                fields=("company", "serial", "event_at"),
                name="inv_item_serial_hist_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.serial.serial_code} · {self.event_type}"

    def save(self, *args, **kwargs):
        if self.item and not self.item_code:
            self.item_code = self.item.item_code
        if not self.event_at:
            self.event_at = timezone.now()
        super().save(*args, **kwargs)


# ============================================================================
# Issue and Receipt Line Models (Multi-line support)
# ============================================================================

class IssueLineBase(InventoryBaseModel, SortableModel):
    """Base model for issue line items."""
    
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="%(class)s_lines",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="%(class)s_lines",
    )
    warehouse_code = models.CharField(max_length=5, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(max_length=30)
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    entered_unit = models.CharField(max_length=30, blank=True)
    entered_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[POSITIVE_DECIMAL],
    )
    line_notes = models.TextField(blank=True)
    
    class Meta:
        abstract = True
        ordering = ("sort_order", "id")
    
    def save(self, *args, **kwargs):
        if self.item and not self.item_code:
            self.item_code = self.item.item_code
        if self.warehouse and not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        super().save(*args, **kwargs)


class IssuePermanentLine(IssueLineBase):
    """Line item for permanent issue documents."""
    
    document = models.ForeignKey(
        "IssuePermanent",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    destination_type = models.CharField(max_length=30, blank=True, default='')
    destination_id = models.BigIntegerField(null=True, blank=True)
    destination_code = models.CharField(max_length=30, blank=True)
    reason_code = models.CharField(max_length=30, blank=True)
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True)
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    serials = models.ManyToManyField(
        "inventory.ItemSerial",
        related_name="issue_permanent_lines",
        blank=True,
    )
    
    class Meta:
        verbose_name = _("Permanent Issue Line")
        verbose_name_plural = _("Permanent Issue Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="inv_issue_perm_line_doc_idx"),
            models.Index(fields=("company", "item"), name="inv_issue_perm_line_item_idx"),
        ]
    
    def __str__(self) -> str:
        return f"{self.document.document_code} - {self.item.name}"


class IssueConsumptionLine(IssueLineBase):
    """Line item for consumption issue documents."""
    
    document = models.ForeignKey(
        "IssueConsumption",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    consumption_type = models.CharField(max_length=30)
    reference_document_type = models.CharField(max_length=30, blank=True)
    reference_document_id = models.BigIntegerField(null=True, blank=True)
    reference_document_code = models.CharField(max_length=30, blank=True)
    production_transfer_id = models.BigIntegerField(null=True, blank=True)
    production_transfer_code = models.CharField(max_length=30, blank=True)
    unit_cost = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    total_cost = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    cost_center_code = models.CharField(max_length=30, blank=True)
    work_line = models.ForeignKey(
        "production.WorkLine",
        on_delete=models.SET_NULL,
        related_name="consumption_issue_lines",
        null=True,
        blank=True,
        help_text=_("Work line (optional, only if production module is installed)"),
    )
    work_line_code = models.CharField(
        max_length=5,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
    )
    serials = models.ManyToManyField(
        "inventory.ItemSerial",
        related_name="issue_consumption_lines",
        blank=True,
    )
    
    class Meta:
        verbose_name = _("Consumption Issue Line")
        verbose_name_plural = _("Consumption Issue Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="inv_issue_cons_line_doc_idx"),
            models.Index(fields=("company", "item"), name="inv_issue_cons_line_item_idx"),
        ]
    
    def __str__(self) -> str:
        return f"{self.document.document_code} - {self.item.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.work_line and not self.work_line_code:
            self.work_line_code = self.work_line.public_code
            super().save(*args, **kwargs)


class IssueConsignmentLine(IssueLineBase):
    """Line item for consignment issue documents."""
    
    document = models.ForeignKey(
        "IssueConsignment",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    consignment_receipt = models.ForeignKey(
        ReceiptConsignment,
        on_delete=models.PROTECT,
        related_name="issue_lines",
        null=True,
        blank=True,
    )
    consignment_receipt_code = models.CharField(max_length=20, blank=True)
    destination_type = models.CharField(max_length=30)
    destination_id = models.BigIntegerField(null=True, blank=True)
    destination_code = models.CharField(max_length=30, blank=True)
    reason_code = models.CharField(max_length=30, blank=True)
    serials = models.ManyToManyField(
        "inventory.ItemSerial",
        related_name="issue_consignment_lines",
        blank=True,
    )
    
    class Meta:
        verbose_name = _("Consignment Issue Line")
        verbose_name_plural = _("Consignment Issue Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="inv_issue_consg_line_doc_idx"),
            models.Index(fields=("company", "item"), name="inv_issue_consg_line_item_idx"),
        ]
    
    def __str__(self) -> str:
        return f"{self.document.document_code} - {self.item.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.consignment_receipt and not self.consignment_receipt_code:
            self.consignment_receipt_code = self.consignment_receipt.document_code
            super().save(*args, **kwargs)


class ReceiptLineBase(InventoryBaseModel, SortableModel):
    """Base model for receipt line items."""
    
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="%(class)s_lines",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="%(class)s_lines",
    )
    warehouse_code = models.CharField(max_length=5, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(max_length=30)
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    entered_unit = models.CharField(max_length=30, blank=True)
    entered_quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[POSITIVE_DECIMAL],
    )
    entered_unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[POSITIVE_DECIMAL],
    )
    entered_price_unit = models.CharField(
        max_length=30,
        blank=True,
        help_text=_("Unit for entered_unit_price (e.g., BOX, CARTON). If empty, same as entered_unit."),
    )
    line_notes = models.TextField(blank=True)
    
    class Meta:
        abstract = True
        ordering = ("sort_order", "id")
    
    def save(self, *args, **kwargs):
        if self.item and not self.item_code:
            self.item_code = self.item.item_code
        if self.warehouse and not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        super().save(*args, **kwargs)


class ReceiptPermanentLine(ReceiptLineBase):
    """Line item for permanent receipt documents."""
    
    document = models.ForeignKey(
        "ReceiptPermanent",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="permanent_receipt_lines",
        null=True,
        blank=True,
    )
    supplier_code = models.CharField(max_length=6, validators=[NUMERIC_CODE_VALIDATOR], blank=True)
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True)
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    serials = models.ManyToManyField(
        "inventory.ItemSerial",
        related_name="receipt_permanent_lines",
        blank=True,
    )
    
    class Meta:
        verbose_name = _("Permanent Receipt Line")
        verbose_name_plural = _("Permanent Receipt Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="inv_receipt_perm_line_doc_idx"),
            models.Index(fields=("company", "item"), name="inv_receipt_perm_line_item_idx"),
        ]
    
    def __str__(self) -> str:
        return f"{self.document.document_code} - {self.item.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.supplier and not self.supplier_code:
            self.supplier_code = self.supplier.public_code
            super().save(*args, **kwargs)


class ReceiptConsignmentLine(ReceiptLineBase):
    """Line item for consignment receipt documents."""
    
    document = models.ForeignKey(
        "ReceiptConsignment",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="consignment_receipt_lines",
    )
    supplier_code = models.CharField(max_length=6, validators=[NUMERIC_CODE_VALIDATOR])
    unit_price_estimate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True)
    serials = models.ManyToManyField(
        "inventory.ItemSerial",
        related_name="receipt_consignment_lines",
        blank=True,
    )
    
    class Meta:
        verbose_name = _("Consignment Receipt Line")
        verbose_name_plural = _("Consignment Receipt Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="inv_rec_consg_line_doc_idx"),
            models.Index(fields=("company", "item"), name="inv_rec_consg_line_item_idx"),
        ]
    
    def __str__(self) -> str:
        return f"{self.document.document_code} - {self.item.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.supplier and not self.supplier_code:
            self.supplier_code = self.supplier.public_code
            super().save(*args, **kwargs)


# ============================================================================
# Issue and Receipt Document Models (Header-only, multi-line support)
# ============================================================================

class IssuePermanent(InventoryDocumentBase):
    """Header-only model for permanent issue documents with multi-line support."""
    document_code = models.CharField(max_length=20, unique=True)
    document_date = models.DateField(default=timezone.now)
    # Header-level fields only - item/warehouse/quantity moved to IssuePermanentLine
    department_unit = models.ForeignKey(
        "shared.CompanyUnit",
        on_delete=models.SET_NULL,
        related_name="permanent_issues",
        null=True,
        blank=True,
    )
    department_unit_code = models.CharField(
        max_length=8,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
    )
    warehouse_request = models.ForeignKey(
        "WarehouseRequest",
        on_delete=models.SET_NULL,
        related_name="permanent_issues",
        null=True,
        blank=True,
    )
    warehouse_request_code = models.CharField(max_length=20, blank=True)
    issue_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Permanent Issue")
        verbose_name_plural = _("Permanent Issues")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if self.department_unit and not self.department_unit_code:
            self.department_unit_code = self.department_unit.public_code
        if self.warehouse_request and not self.warehouse_request_code:
            self.warehouse_request_code = self.warehouse_request.request_code
        super().save(*args, **kwargs)


class IssueConsumption(InventoryDocumentBase):
    """Header-only model for consumption issue documents with multi-line support."""
    document_code = models.CharField(max_length=20, unique=True)
    document_date = models.DateField(default=timezone.now)
    # Header-level fields only - item/warehouse/quantity moved to IssueConsumptionLine
    department_unit = models.ForeignKey(
        "shared.CompanyUnit",
        on_delete=models.SET_NULL,
        related_name="consumption_issues",
        null=True,
        blank=True,
    )
    department_unit_code = models.CharField(
        max_length=8,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
    )
    issue_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Consumption Issue")
        verbose_name_plural = _("Consumption Issues")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if self.department_unit and not self.department_unit_code:
            self.department_unit_code = self.department_unit.public_code
        super().save(*args, **kwargs)


class IssueConsignment(InventoryDocumentBase):
    """Header-only model for consignment issue documents with multi-line support."""
    document_code = models.CharField(max_length=20, unique=True)
    document_date = models.DateField(default=timezone.now)
    # Header-level fields only - item/warehouse/quantity moved to IssueConsignmentLine
    department_unit = models.ForeignKey(
        "shared.CompanyUnit",
        on_delete=models.SET_NULL,
        related_name="consignment_issues",
        null=True,
        blank=True,
    )
    department_unit_code = models.CharField(
        max_length=8,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
    )
    issue_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Consignment Issue")
        verbose_name_plural = _("Consignment Issues")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if self.department_unit and not self.department_unit_code:
            self.department_unit_code = self.department_unit.public_code
        super().save(*args, **kwargs)


class StocktakingDeficit(InventoryDocumentBase):
    document_code = models.CharField(_("Document Code"), max_length=20, unique=True)
    document_date = models.DateField(_("Document Date"), default=timezone.now)
    stocktaking_session_id = models.BigIntegerField(
        _("Stocktaking Session ID"),
        null=True,
        blank=True,
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="stocktaking_deficits",
    )
    item_code = models.CharField(_("Item Code"), max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stocktaking_deficits",
    )
    warehouse_code = models.CharField(_("Warehouse Code"), max_length=5, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(_("Unit"), max_length=30)
    quantity_expected = models.DecimalField(
        _("Quantity Expected"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    quantity_counted = models.DecimalField(
        _("Quantity Counted"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    quantity_adjusted = models.DecimalField(
        _("Quantity Adjusted"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    valuation_method = models.CharField(_("Valuation Method"), max_length=30, blank=True)
    unit_cost = models.DecimalField(
        _("Unit Cost"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    total_cost = models.DecimalField(
        _("Total Cost"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    reason_code = models.CharField(_("Reason Code"), max_length=30, blank=True)
    investigation_reference = models.CharField(_("Investigation Reference"), max_length=30, blank=True)
    adjustment_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Stocktaking Deficit")
        verbose_name_plural = _("Stocktaking Deficits")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = self.item.item_code
        if not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        super().save(*args, **kwargs)


class StocktakingSurplus(InventoryDocumentBase):
    document_code = models.CharField(_("Document Code"), max_length=20, unique=True)
    document_date = models.DateField(_("Document Date"), default=timezone.now)
    stocktaking_session_id = models.BigIntegerField(
        _("Stocktaking Session ID"),
        null=True,
        blank=True,
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="stocktaking_surpluses",
    )
    item_code = models.CharField(_("Item Code"), max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stocktaking_surpluses",
    )
    warehouse_code = models.CharField(_("Warehouse Code"), max_length=5, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(_("Unit"), max_length=30)
    quantity_expected = models.DecimalField(
        _("Quantity Expected"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    quantity_counted = models.DecimalField(
        _("Quantity Counted"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    quantity_adjusted = models.DecimalField(
        _("Quantity Adjusted"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    valuation_method = models.CharField(_("Valuation Method"), max_length=30, blank=True)
    unit_cost = models.DecimalField(
        _("Unit Cost"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    total_cost = models.DecimalField(
        _("Total Cost"),
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    reason_code = models.CharField(_("Reason Code"), max_length=30, blank=True)
    investigation_reference = models.CharField(_("Investigation Reference"), max_length=30, blank=True)
    adjustment_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Stocktaking Surplus")
        verbose_name_plural = _("Stocktaking Surpluses")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if not self.item_code:
            self.item_code = self.item.item_code
        if not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        super().save(*args, **kwargs)


class StocktakingRecord(InventoryDocumentBase):
    document_code = models.CharField(_("Document Code"), max_length=20, unique=True)
    document_date = models.DateField(_("Document Date"), default=timezone.now)
    stocktaking_session_id = models.BigIntegerField(_("Stocktaking Session ID"))
    inventory_snapshot_time = models.DateTimeField(_("Inventory Snapshot Time"))
    confirmed_by = models.ForeignKey(
        'shared.User',
        on_delete=models.PROTECT,
        related_name="stocktaking_records_confirmed",
    )
    confirmed_by_code = models.CharField(_("Confirmed By Code"), max_length=8, validators=[NUMERIC_CODE_VALIDATOR])
    confirmation_notes = models.TextField(_("Confirmation Notes"), blank=True)
    variance_document_ids = models.JSONField(_("Variance Document IDs"), default=list, blank=True)
    variance_document_codes = models.JSONField(_("Variance Document Codes"), default=list, blank=True)
    final_inventory_value = models.DecimalField(
        _("Final Value"),
        max_digits=20,
        decimal_places=4,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    approval_status = models.CharField(_("Approval Status"), max_length=20, default="pending")
    approved_at = models.DateTimeField(_("Approved At"), null=True, blank=True)
    approver = models.ForeignKey(
        'shared.User',
        on_delete=models.SET_NULL,
        related_name="stocktaking_records_approved",
        null=True,
        blank=True,
    )
    approver_notes = models.TextField(_("Approver Notes"), blank=True)
    record_metadata = models.JSONField(_("Record Metadata"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Stocktaking Record")
        verbose_name_plural = _("Stocktaking Records")
        ordering = ("-document_date", "document_code")

    def __str__(self) -> str:
        return self.document_code

    def save(self, *args, **kwargs):
        if not self.confirmed_by_code and self.confirmed_by:
            self.confirmed_by_code = self.confirmed_by.username
        super().save(*args, **kwargs)


class WarehouseRequest(InventoryBaseModel, LockableModel):
    """
    Warehouse request for issuing materials to departments, production, or other internal use.
    Pattern: WRQ-YYYYMM-XXXXXX
    """
    request_code = models.CharField(max_length=20, unique=True)
    request_date = models.DateField(default=timezone.now)
    
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name="warehouse_requests",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    
    quantity_requested = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )
    unit = models.CharField(max_length=20)
    
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="warehouse_requests",
    )
    warehouse_code = models.CharField(max_length=8, validators=[NUMERIC_CODE_VALIDATOR])
    
    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="warehouse_requests",
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="warehouse_requests_to_approve",
        null=True,
        blank=True,
    )
    
    department_unit = models.ForeignKey(
        "shared.CompanyUnit",
        on_delete=models.SET_NULL,
        related_name="warehouse_requests",
        null=True,
        blank=True,
    )
    department_unit_code = models.CharField(
        max_length=8,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
    )
    
    priority = models.CharField(
        max_length=20,
        default="normal",
        choices=[
            ("low", "Low"),
            ("normal", "Normal"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ],
    )
    needed_by_date = models.DateField(null=True, blank=True)
    purpose = models.TextField(blank=True)
    
    request_status = models.CharField(
        max_length=20,
        default="draft",
        choices=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("issued", "Issued"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
    )
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    issued_at = models.DateTimeField(null=True, blank=True)
    issue_document_id = models.BigIntegerField(null=True, blank=True)
    issue_document_code = models.CharField(max_length=20, blank=True)
    quantity_issued = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
    )
    
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)
    request_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Warehouse Request")
        verbose_name_plural = _("Warehouse Requests")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "request_code"),
                name="inventory_warehouse_request_code_unique",
            ),
        ]
        ordering = ("-request_date", "-id")

    def __str__(self) -> str:
        return f"{self.request_code} · {self.item.name}"

    def save(self, *args, **kwargs):
        # Auto-generate request code if not set
        if not self.request_code:
            now = timezone.now()
            month_year = now.strftime("%Y%m")
            # Find the max sequence for this month
            last_request = (
                WarehouseRequest.objects.filter(
                    company=self.company,
                    request_code__startswith=f"WRQ-{month_year}",
                )
                .order_by("-request_code")
                .first()
            )
            if last_request and last_request.request_code:
                last_seq = int(last_request.request_code.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            self.request_code = f"WRQ-{month_year}-{new_seq:06d}"
        
        # Cache related codes
        if self.item and not self.item_code:
            self.item_code = self.item.item_code
        if self.warehouse and not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        if self.department_unit and not self.department_unit_code:
            self.department_unit_code = self.department_unit.public_code
        super().save(*args, **kwargs)

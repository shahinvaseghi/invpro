"""
Models for procurement module.
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shared.models import (
    ActivatableModel,
    CompanyScopedModel,
    LockableModel,
    MetadataModel,
    SortableModel,
    TimeStampedModel,
    User,
)
from accounting.models import get_fiscal_year_from_date


NUMERIC_CODE_VALIDATOR = RegexValidator(
    regex=r"^\d+$",
    message=_("Only numeric characters are allowed."),
)

POSITIVE_DECIMAL = MinValueValidator(Decimal("0"))


class ProcurementBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    """Base model for procurement module."""
    class Meta:
        abstract = True


class ProcurementSortableModel(ProcurementBaseModel, SortableModel):
    """Base model for sortable procurement models."""
    class Meta:
        abstract = True


class FiscalYearMixin(models.Model):
    """
    Mixin to auto-populate fiscal_year_id from document_date or order_date.
    Use this mixin for models that have document_date/order_date and need fiscal_year_id.
    """
    fiscal_year = models.ForeignKey(
        'accounting.FiscalYear',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_set',
        null=True,
        blank=True,
        help_text=_("Fiscal year for this document (auto-populated from document_date)"),
        db_index=True,
    )
    
    class Meta:
        abstract = True
    
    def get_document_date_field_name(self):
        """
        Override this method if document_date field has a different name.
        Default: 'document_date', fallback to 'order_date', 'invoice_date'
        """
        if hasattr(self, 'document_date'):
            return 'document_date'
        elif hasattr(self, 'order_date'):
            return 'order_date'
        elif hasattr(self, 'invoice_date'):
            return 'invoice_date'
        return 'document_date'
    
    def save(self, *args, **kwargs):
        """Auto-populate fiscal_year_id from document_date/order_date."""
        if not self.fiscal_year_id:
            date_field_name = self.get_document_date_field_name()
            document_date = getattr(self, date_field_name, None)
            
            if document_date and self.company_id:
                fiscal_year = get_fiscal_year_from_date(
                    company_id=self.company_id,
                    document_date=document_date
                )
                if fiscal_year:
                    self.fiscal_year = fiscal_year
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate that document_date is within fiscal_year range."""
        from django.core.exceptions import ValidationError
        
        date_field_name = self.get_document_date_field_name()
        document_date = getattr(self, date_field_name, None)
        
        if document_date and self.fiscal_year:
            if document_date < self.fiscal_year.start_date:
                raise ValidationError(
                    _("Document date (%(date)s) is before fiscal year start date (%(start)s).") % {
                        'date': document_date,
                        'start': self.fiscal_year.start_date,
                    }
                )
            if document_date > self.fiscal_year.end_date:
                raise ValidationError(
                    _("Document date (%(date)s) is after fiscal year end date (%(end)s).") % {
                        'date': document_date,
                        'end': self.fiscal_year.end_date,
                    }
                )
        
        super().clean()


class ProcurementDocumentBase(ProcurementBaseModel, LockableModel, FiscalYearMixin):
    """Base model for procurement documents."""
    public_code_validator = NUMERIC_CODE_VALIDATOR

    document_code = models.CharField(max_length=30, unique=True)
    document_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True


class PurchaseOrder(ProcurementBaseModel, LockableModel, FiscalYearMixin):
    """
    Purchase Order - سفارش خرید
    Pattern: PO-YYYYMM-XXXXXX
    """
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        APPROVED = "approved", _("Approved")
        SENT = "sent", _("Sent to Supplier")
        PARTIALLY_RECEIVED = "partially_received", _("Partially Received")
        RECEIVED = "received", _("Fully Received")
        CANCELLED = "cancelled", _("Cancelled")

    order_code = models.CharField(max_length=20, unique=True)
    order_date = models.DateField(default=timezone.now)
    supplier = models.ForeignKey(
        'inventory.Supplier',
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )
    supplier_code = models.CharField(max_length=6, validators=[NUMERIC_CODE_VALIDATOR])
    purchase_request = models.ForeignKey(
        'inventory.PurchaseRequest',
        on_delete=models.SET_NULL,
        related_name="purchase_orders",
        null=True,
        blank=True,
        help_text=_("Related purchase request (optional)"),
    )
    purchase_request_code = models.CharField(max_length=20, blank=True)
    order_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    expected_delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.TextField(blank=True)
    payment_terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    document_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")
        ordering = ("-order_date", "-order_code")
        indexes = [
            models.Index(fields=("company", "order_date"), name="proc_po_date_idx"),
            models.Index(fields=("company", "supplier"), name="proc_po_supplier_idx"),
            models.Index(fields=("company", "purchase_request"), name="proc_po_request_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.order_code} - {self.supplier.name if self.supplier else 'N/A'}"

    def _generate_order_code(self) -> str:
        """
        Generates a unique code following the pattern PO-YYYYMM-XXXXXX scoped per company.
        """
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"PO-{month_year}"
        last_order = (
            PurchaseOrder.objects.filter(
                company_id=self.company_id,
                order_code__startswith=prefix,
            )
            .order_by("-order_code")
            .first()
        )
        if last_order and last_order.order_code:
            try:
                sequence = int(last_order.order_code.split("-")[-1])
            except (ValueError, IndexError):
                sequence = 0
        else:
            sequence = 0
        return f"{prefix}-{sequence + 1:06d}"

    def save(self, *args, **kwargs):
        """Auto-generate order_code if not provided."""
        if not self.order_code or not self.order_code.strip():
            self.order_code = self._generate_order_code()
        
        # Ensure supplier_code is set from supplier if not already set
        if self.supplier and not self.supplier_code:
            self.supplier_code = self.supplier.public_code
        
        # Ensure purchase_request_code is set from purchase_request if not already set
        if self.purchase_request and not self.purchase_request_code:
            self.purchase_request_code = self.purchase_request.request_code
        
        super().save(*args, **kwargs)

    @property
    def total_quantity(self):
        """Calculate total quantity across all lines."""
        return sum(line.quantity for line in self.lines.filter(is_enabled=1))

    @property
    def total_amount(self):
        """Calculate total amount across all lines."""
        return sum(line.total_amount for line in self.lines.filter(is_enabled=1))

    @property
    def is_fully_received(self):
        """Check if all lines are fully received."""
        lines = self.lines.filter(is_enabled=1)
        if not lines.exists():
            return False
        return all(line.quantity_received >= line.quantity for line in lines)


class PurchaseOrderLine(ProcurementBaseModel, SortableModel):
    """
    Line item for purchase order documents.
    """
    document = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name="purchase_order_lines",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(max_length=30)
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
    )
    quantity_received = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0"),
        validators=[POSITIVE_DECIMAL],
    )
    line_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Purchase Order Line")
        verbose_name_plural = _("Purchase Order Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="proc_po_line_doc_idx"),
            models.Index(fields=("company", "item"), name="proc_po_line_item_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.document.order_code} - {self.item.name}"

    def save(self, *args, **kwargs):
        """Auto-calculate total_amount and ensure item_code is set."""
        if self.item and not self.item_code:
            self.item_code = self.item.item_code or self.item.full_item_code or ''
        
        # Calculate total_amount
        if self.quantity and self.unit_price:
            self.total_amount = self.quantity * self.unit_price
        else:
            self.total_amount = Decimal("0")
        
        super().save(*args, **kwargs)

    @property
    def quantity_remaining(self):
        """Calculate remaining quantity to be received."""
        return max(Decimal("0"), self.quantity - self.quantity_received)

    @property
    def is_fully_received(self):
        """Check if this line is fully received."""
        return self.quantity_received >= self.quantity


class PurchaseInvoice(ProcurementBaseModel, LockableModel, FiscalYearMixin):
    """
    Purchase Invoice - فاکتور خرید کالا
    Pattern: PINV-YYYYMM-XXXXXX
    """
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        APPROVED = "approved", _("Approved")
        POSTED = "posted", _("Posted to Accounting")
        PAID = "paid", _("Paid")
        CANCELLED = "cancelled", _("Cancelled")

    invoice_code = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField(default=timezone.now)
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Supplier's invoice number"),
    )
    supplier = models.ForeignKey(
        'inventory.Supplier',
        on_delete=models.PROTECT,
        related_name="purchase_invoices",
    )
    supplier_code = models.CharField(max_length=6, validators=[NUMERIC_CODE_VALIDATOR])
    party = models.ForeignKey(
        'accounting.Party',
        on_delete=models.SET_NULL,
        related_name="purchase_invoices",
        null=True,
        blank=True,
        help_text=_("Accounting party (linked to supplier)"),
    )
    party_code = models.CharField(max_length=10, blank=True)
    receipt_permanent = models.ForeignKey(
        'inventory.ReceiptPermanent',
        on_delete=models.SET_NULL,
        related_name="purchase_invoices",
        null=True,
        blank=True,
        help_text=_("Related permanent receipt (optional)"),
    )
    receipt_permanent_code = models.CharField(max_length=20, blank=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        related_name="purchase_invoices",
        null=True,
        blank=True,
        help_text=_("Related purchase order (optional)"),
    )
    purchase_order_code = models.CharField(max_length=20, blank=True)
    invoice_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("Subtotal before VAT"),
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("9"),
        help_text=_("VAT rate percentage"),
    )
    vat_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("VAT amount"),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("Total amount (subtotal + VAT)"),
    )
    accounting_document = models.ForeignKey(
        'accounting.AccountingDocument',
        on_delete=models.SET_NULL,
        related_name="purchase_invoices",
        null=True,
        blank=True,
        help_text=_("Related accounting document (auto-created when posted)"),
    )
    accounting_document_number = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    document_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Purchase Invoice")
        verbose_name_plural = _("Purchase Invoices")
        ordering = ("-invoice_date", "-invoice_code")
        indexes = [
            models.Index(fields=("company", "invoice_date"), name="proc_pinv_date_idx"),
            models.Index(fields=("company", "supplier"), name="proc_pinv_supplier_idx"),
            models.Index(fields=("company", "receipt_permanent"), name="proc_pinv_receipt_idx"),
            models.Index(fields=("company", "purchase_order"), name="proc_pinv_order_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.invoice_code} - {self.supplier.name if self.supplier else 'N/A'}"

    def _generate_invoice_code(self) -> str:
        """
        Generates a unique code following the pattern PINV-YYYYMM-XXXXXX scoped per company.
        """
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"PINV-{month_year}"
        last_invoice = (
            PurchaseInvoice.objects.filter(
                company_id=self.company_id,
                invoice_code__startswith=prefix,
            )
            .order_by("-invoice_code")
            .first()
        )
        if last_invoice and last_invoice.invoice_code:
            try:
                sequence = int(last_invoice.invoice_code.split("-")[-1])
            except (ValueError, IndexError):
                sequence = 0
        else:
            sequence = 0
        return f"{prefix}-{sequence + 1:06d}"

    def save(self, *args, **kwargs):
        """Auto-generate invoice_code and calculate totals."""
        if not self.invoice_code or not self.invoice_code.strip():
            self.invoice_code = self._generate_invoice_code()
        
        # Ensure supplier_code is set from supplier if not already set
        if self.supplier and not self.supplier_code:
            self.supplier_code = self.supplier.public_code
        
        # Ensure receipt_permanent_code is set from receipt_permanent if not already set
        if self.receipt_permanent and not self.receipt_permanent_code:
            self.receipt_permanent_code = self.receipt_permanent.document_code
        
        # Ensure purchase_order_code is set from purchase_order if not already set
        if self.purchase_order and not self.purchase_order_code:
            self.purchase_order_code = self.purchase_order.order_code
        
        # Ensure party_code is set from party if not already set
        if self.party and not self.party_code:
            self.party_code = self.party.party_code
        
        # Ensure accounting_document_number is set from accounting_document if not already set
        if self.accounting_document and not self.accounting_document_number:
            self.accounting_document_number = self.accounting_document.document_number
        
        # Calculate totals from lines
        lines = self.lines.filter(is_enabled=1)
        self.subtotal = sum(line.line_total for line in lines)
        self.vat_amount = self.subtotal * (self.vat_rate / Decimal("100"))
        self.total_amount = self.subtotal + self.vat_amount
        
        super().save(*args, **kwargs)

    @property
    def total_quantity(self):
        """Calculate total quantity across all lines."""
        return sum(line.quantity for line in self.lines.filter(is_enabled=1))


class PurchaseInvoiceLine(ProcurementBaseModel, SortableModel):
    """
    Line item for purchase invoice documents.
    """
    document = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name="purchase_invoice_lines",
    )
    item_code = models.CharField(max_length=16, validators=[NUMERIC_CODE_VALIDATOR])
    unit = models.CharField(max_length=30)
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
    )
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("Line total (quantity * unit_price)"),
    )
    cost_allocation = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Cost allocation breakdown (freight, insurance, etc.)"),
    )
    line_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Purchase Invoice Line")
        verbose_name_plural = _("Purchase Invoice Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="proc_pinv_line_doc_idx"),
            models.Index(fields=("company", "item"), name="proc_pinv_line_item_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.document.invoice_code} - {self.item.name}"

    def save(self, *args, **kwargs):
        """Auto-calculate line_total and ensure item_code is set."""
        if self.item and not self.item_code:
            self.item_code = self.item.item_code or self.item.full_item_code or ''
        
        # Calculate line_total
        if self.quantity and self.unit_price:
            self.line_total = self.quantity * self.unit_price
        else:
            self.line_total = Decimal("0")
        
        super().save(*args, **kwargs)
        
        # Update parent invoice totals
        if self.document_id:
            self.document.save()


class ServiceRequest(ProcurementBaseModel, LockableModel, FiscalYearMixin):
    """
    Service Request - درخواست خدمت
    Pattern: SREQ-YYYYMM-XXXXXX
    """
    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        NORMAL = "normal", _("Normal")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        APPROVED = "approved", _("Approved")
        ORDERED = "ordered", _("Ordered / Contracted")
        FULFILLED = "fulfilled", _("Fulfilled")
        CANCELLED = "cancelled", _("Cancelled")

    request_code = models.CharField(max_length=20, unique=True)
    request_date = models.DateField(default=timezone.now)
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="service_requests",
    )
    service_description = models.TextField(
        help_text=_("Description of requested service"),
    )
    supplier = models.ForeignKey(
        'inventory.Supplier',
        on_delete=models.SET_NULL,
        related_name="service_requests",
        null=True,
        blank=True,
        help_text=_("Service provider / supplier"),
    )
    supplier_code = models.CharField(max_length=6, validators=[NUMERIC_CODE_VALIDATOR], blank=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    needed_by_date = models.DateField(null=True, blank=True)
    estimated_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        null=True,
        blank=True,
        help_text=_("Estimated service cost"),
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="service_requests_approved",
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    request_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Service Request")
        verbose_name_plural = _("Service Requests")
        ordering = ("-request_date", "request_code")
        indexes = [
            models.Index(fields=("company", "request_date"), name="proc_sreq_date_idx"),
            models.Index(fields=("company", "supplier"), name="proc_sreq_supplier_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.request_code}"

    def get_document_date_field_name(self):
        """Override to use request_date instead of document_date."""
        return 'request_date'

    def _generate_request_code(self) -> str:
        """
        Generates a unique code following the pattern SREQ-YYYYMM-XXXXXX scoped per company.
        """
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"SREQ-{month_year}"
        last_request = (
            ServiceRequest.objects.filter(
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
        """Auto-generate request_code if not provided."""
        if not self.request_code or not self.request_code.strip():
            self.request_code = self._generate_request_code()
        
        # Ensure supplier_code is set from supplier if not already set
        if self.supplier and not self.supplier_code:
            self.supplier_code = self.supplier.public_code
        
        super().save(*args, **kwargs)


class ServiceInvoice(ProcurementBaseModel, LockableModel, FiscalYearMixin):
    """
    Service Invoice - فاکتور خرید خدمت
    Pattern: SINV-YYYYMM-XXXXXX
    """
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        APPROVED = "approved", _("Approved")
        POSTED = "posted", _("Posted to Accounting")
        PAID = "paid", _("Paid")
        CANCELLED = "cancelled", _("Cancelled")

    invoice_code = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField(default=timezone.now)
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Supplier's invoice number"),
    )
    supplier = models.ForeignKey(
        'inventory.Supplier',
        on_delete=models.PROTECT,
        related_name="service_invoices",
    )
    supplier_code = models.CharField(max_length=6, validators=[NUMERIC_CODE_VALIDATOR])
    party = models.ForeignKey(
        'accounting.Party',
        on_delete=models.SET_NULL,
        related_name="service_invoices",
        null=True,
        blank=True,
        help_text=_("Accounting party (linked to supplier)"),
    )
    party_code = models.CharField(max_length=10, blank=True)
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.SET_NULL,
        related_name="service_invoices",
        null=True,
        blank=True,
        help_text=_("Related service request (optional)"),
    )
    service_request_code = models.CharField(max_length=20, blank=True)
    service_description = models.TextField(
        help_text=_("Description of service provided"),
    )
    expense_category = models.ForeignKey(
        'accounting.IncomeExpenseCategory',
        on_delete=models.SET_NULL,
        related_name="service_invoices",
        null=True,
        blank=True,
        help_text=_("Expense category for this service"),
    )
    expense_category_code = models.CharField(max_length=30, blank=True)
    invoice_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("Subtotal before VAT"),
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("9"),
        help_text=_("VAT rate percentage"),
    )
    vat_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("VAT amount"),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        default=Decimal("0"),
        help_text=_("Total amount (subtotal + VAT)"),
    )
    accounting_document = models.ForeignKey(
        'accounting.AccountingDocument',
        on_delete=models.SET_NULL,
        related_name="service_invoices",
        null=True,
        blank=True,
        help_text=_("Related accounting document (auto-created when posted)"),
    )
    accounting_document_number = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    document_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Service Invoice")
        verbose_name_plural = _("Service Invoices")
        ordering = ("-invoice_date", "-invoice_code")
        indexes = [
            models.Index(fields=("company", "invoice_date"), name="proc_sinv_date_idx"),
            models.Index(fields=("company", "supplier"), name="proc_sinv_supplier_idx"),
            models.Index(fields=("company", "service_request"), name="proc_sinv_request_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.invoice_code} - {self.supplier.name if self.supplier else 'N/A'}"

    def _generate_invoice_code(self) -> str:
        """
        Generates a unique code following the pattern SINV-YYYYMM-XXXXXX scoped per company.
        """
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"SINV-{month_year}"
        last_invoice = (
            ServiceInvoice.objects.filter(
                company_id=self.company_id,
                invoice_code__startswith=prefix,
            )
            .order_by("-invoice_code")
            .first()
        )
        if last_invoice and last_invoice.invoice_code:
            try:
                sequence = int(last_invoice.invoice_code.split("-")[-1])
            except (ValueError, IndexError):
                sequence = 0
        else:
            sequence = 0
        return f"{prefix}-{sequence + 1:06d}"

    def save(self, *args, **kwargs):
        """Auto-generate invoice_code and calculate totals."""
        if not self.invoice_code or not self.invoice_code.strip():
            self.invoice_code = self._generate_invoice_code()
        
        # Ensure supplier_code is set from supplier if not already set
        if self.supplier and not self.supplier_code:
            self.supplier_code = self.supplier.public_code
        
        # Ensure service_request_code is set from service_request if not already set
        if self.service_request and not self.service_request_code:
            self.service_request_code = self.service_request.request_code
        
        # Ensure party_code is set from party if not already set
        if self.party and not self.party_code:
            self.party_code = self.party.party_code
        
        # Ensure expense_category_code is set from expense_category if not already set
        if self.expense_category and not self.expense_category_code:
            self.expense_category_code = self.expense_category.category_code
        
        # Ensure accounting_document_number is set from accounting_document if not already set
        if self.accounting_document and not self.accounting_document_number:
            self.accounting_document_number = self.accounting_document.document_number
        
        # Calculate totals
        self.vat_amount = self.subtotal * (self.vat_rate / Decimal("100"))
        self.total_amount = self.subtotal + self.vat_amount
        
        super().save(*args, **kwargs)

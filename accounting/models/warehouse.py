"""
Warehouse Accounting models.
"""
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingDocumentBase, AccountingSortableModel, POSITIVE_DECIMAL


class WarehouseExpenseDocument(AccountingDocumentBase):
    """Warehouse expense document linked to inventory receipts."""
    
    RECEIPT_TYPE_CHOICES = [
        ('PERMANENT', _('Permanent Receipt')),
        ('TEMPORARY', _('Temporary Receipt')),
        ('CONSIGNMENT', _('Consignment Receipt')),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', _('Draft')),
        ('POSTED', _('Posted')),
        ('LOCKED', _('Locked')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    document_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text=_("Auto-generated document code"),
    )
    receipt_type = models.CharField(
        max_length=20,
        choices=RECEIPT_TYPE_CHOICES,
        help_text=_("Type of receipt this expense document is linked to"),
    )
    receipt_id = models.BigIntegerField(
        help_text=_("ID of the receipt document"),
    )
    receipt_code = models.CharField(
        max_length=30,
        help_text=_("Code of the receipt document"),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Total expense amount"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text=_("Document status"),
    )
    accounting_document = models.ForeignKey(
        'AccountingDocument',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warehouse_expense_documents',
        help_text=_("Linked accounting document"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Document description"),
    )
    
    class Meta:
        verbose_name = _("Warehouse Expense Document")
        verbose_name_plural = _("Warehouse Expense Documents")
        ordering = ("-document_date", "-id")
        indexes = [
            models.Index(fields=("company", "receipt_type", "receipt_id"), name="warehouse_exp_receipt_idx"),
            models.Index(fields=("company", "status"), name="warehouse_exp_status_idx"),
        ]
    
    def __str__(self):
        return f"{self.document_code} - {self.receipt_code}"
    
    def save(self, *args, **kwargs):
        if not self.document_code:
            self.document_code = self._generate_document_code()
        super().save(*args, **kwargs)
    
    def _generate_document_code(self):
        """Generate document code: WHE-YYYYMM-XXXXXX"""
        from django.utils import timezone
        from inventory.utils.codes import generate_sequential_code
        
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"WHE-{month_year}"
        
        last_doc = WarehouseExpenseDocument.objects.filter(
            company=self.company,
            document_code__startswith=prefix,
        ).order_by("-document_code").first()
        
        if last_doc and last_doc.document_code:
            try:
                sequence = int(last_doc.document_code.split("-")[-1])
            except (ValueError, IndexError):
                sequence = 0
        else:
            sequence = 0
        
        return f"{prefix}-{sequence + 1:06d}"


class WarehouseExpenseDocumentLine(AccountingSortableModel):
    """Line item for warehouse expense document."""
    
    document = models.ForeignKey(
        WarehouseExpenseDocument,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name="warehouse_expense_lines",
    )
    item_code = models.CharField(
        max_length=16,
        help_text=_("Item code from receipt line"),
    )
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.PROTECT,
        related_name="warehouse_expense_lines",
        null=True,
        blank=True,
    )
    warehouse_code = models.CharField(
        max_length=5,
        blank=True,
        help_text=_("Warehouse code from receipt line"),
    )
    # Unit and quantity from receipt
    unit = models.CharField(
        max_length=30,
        help_text=_("Unit used in receipt (entered_unit if exists, otherwise unit)"),
    )
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        help_text=_("Quantity in the unit used in receipt"),
    )
    # Price fields
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        help_text=_("Price per unit (in the unit used in receipt)"),
    )
    # Base unit (item's default_unit)
    base_unit = models.CharField(
        max_length=30,
        help_text=_("Item's default unit"),
    )
    base_unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        help_text=_("Price per base unit (converted from unit_price)"),
    )
    total_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        help_text=_("Total price for this line (quantity * unit_price)"),
    )
    line_notes = models.TextField(
        blank=True,
        help_text=_("Line notes"),
    )
    
    class Meta:
        verbose_name = _("Warehouse Expense Document Line")
        verbose_name_plural = _("Warehouse Expense Document Lines")
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=("company", "document"), name="warehouse_exp_line_doc_idx"),
            models.Index(fields=("company", "item"), name="warehouse_exp_line_item_idx"),
        ]
    
    def __str__(self):
        return f"{self.document.document_code} - {self.item.name if self.item else self.item_code}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total_price and set codes."""
        if self.item and not self.item_code:
            self.item_code = self.item.item_code
        if self.warehouse and not self.warehouse_code:
            self.warehouse_code = self.warehouse.public_code
        
        # Calculate total price
        if self.quantity and self.unit_price:
            self.total_price = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)


class WarehouseIncomeDocument(AccountingDocumentBase):
    """Warehouse income document linked to inventory issues."""
    
    ISSUE_TYPE_CHOICES = [
        ('PERMANENT', _('Permanent Issue')),
        ('CONSUMPTION', _('Consumption Issue')),
        ('CONSIGNMENT', _('Consignment Issue')),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', _('Draft')),
        ('POSTED', _('Posted')),
        ('LOCKED', _('Locked')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    document_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text=_("Auto-generated document code"),
    )
    issue_type = models.CharField(
        max_length=20,
        choices=ISSUE_TYPE_CHOICES,
        help_text=_("Type of issue this income document is linked to"),
    )
    issue_id = models.BigIntegerField(
        help_text=_("ID of the issue document"),
    )
    issue_code = models.CharField(
        max_length=30,
        help_text=_("Code of the issue document"),
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Total income amount"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text=_("Document status"),
    )
    accounting_document = models.ForeignKey(
        'AccountingDocument',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warehouse_income_documents',
        help_text=_("Linked accounting document"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Document description"),
    )
    
    class Meta:
        verbose_name = _("Warehouse Income Document")
        verbose_name_plural = _("Warehouse Income Documents")
        ordering = ("-document_date", "-id")
        indexes = [
            models.Index(fields=("company", "issue_type", "issue_id"), name="warehouse_inc_issue_idx"),
            models.Index(fields=("company", "status"), name="warehouse_inc_status_idx"),
        ]
    
    def __str__(self):
        return f"{self.document_code} - {self.issue_code}"
    
    def save(self, *args, **kwargs):
        if not self.document_code:
            self.document_code = self._generate_document_code()
        super().save(*args, **kwargs)
    
    def _generate_document_code(self):
        """Generate document code: WHI-YYYYMM-XXXXXX"""
        from django.utils import timezone
        
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"WHI-{month_year}"
        
        last_doc = WarehouseIncomeDocument.objects.filter(
            company=self.company,
            document_code__startswith=prefix,
        ).order_by("-document_code").first()
        
        if last_doc and last_doc.document_code:
            try:
                sequence = int(last_doc.document_code.split("-")[-1])
            except (ValueError, IndexError):
                sequence = 0
        else:
            sequence = 0
        
        return f"{prefix}-{sequence + 1:06d}"


"""
Payment Request models for accounting module.
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base import AccountingBaseModel, LockableModel, FiscalYearMixin, POSITIVE_DECIMAL


class PaymentRequest(AccountingBaseModel, LockableModel, FiscalYearMixin):
    """
    Payment Request - درخواست پرداخت
    Pattern: PAYREQ-YYYYMM-XXXXXX
    
    This model handles payment requests for various purposes:
    - Purchase invoices (PurchaseInvoice)
    - Service invoices (ServiceInvoice)
    - Direct expenses (salaries, rent, bills)
    - Prepayments (on-account payments)
    """
    class PaymentType(models.TextChoices):
        PURCHASE_INVOICE = "purchase_invoice", _("Purchase Invoice")
        SERVICE_INVOICE = "service_invoice", _("Service Invoice")
        DIRECT_EXPENSE = "direct_expense", _("Direct Expense")
        PREPAYMENT = "prepayment", _("Prepayment")
        OTHER = "other", _("Other")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        APPROVED = "approved", _("Approved")
        PAID = "paid", _("Paid")
        CANCELLED = "cancelled", _("Cancelled")

    request_code = models.CharField(max_length=30, unique=True)
    request_date = models.DateField(default=timezone.now)
    payment_type = models.CharField(
        max_length=30,
        choices=PaymentType.choices,
        help_text=_("Type of payment request"),
    )
    request_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[POSITIVE_DECIMAL],
        help_text=_("Requested payment amount"),
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Due date for payment"),
    )
    party = models.ForeignKey(
        'Party',
        on_delete=models.PROTECT,
        related_name="payment_requests",
        null=True,
        blank=True,
        help_text=_("Party to pay (supplier, vendor, etc.)"),
    )
    party_code = models.CharField(max_length=10, blank=True)
    
    # Reference to purchase invoice (for purchase invoice payments)
    purchase_invoice = models.ForeignKey(
        'procurement.PurchaseInvoice',
        on_delete=models.SET_NULL,
        related_name="payment_requests",
        null=True,
        blank=True,
        help_text=_("Related purchase invoice (if payment_type = purchase_invoice)"),
    )
    purchase_invoice_code = models.CharField(max_length=20, blank=True)
    
    # Reference to service invoice (for service invoice payments)
    service_invoice = models.ForeignKey(
        'procurement.ServiceInvoice',
        on_delete=models.SET_NULL,
        related_name="payment_requests",
        null=True,
        blank=True,
        help_text=_("Related service invoice (if payment_type = service_invoice)"),
    )
    service_invoice_code = models.CharField(max_length=20, blank=True)
    
    # For direct expenses (salaries, rent, bills, etc.)
    expense_category = models.ForeignKey(
        'IncomeExpenseCategory',
        on_delete=models.SET_NULL,
        related_name="payment_requests",
        null=True,
        blank=True,
        help_text=_("Expense category (for direct expense payments)"),
    )
    expense_category_code = models.CharField(max_length=30, blank=True)
    expense_description = models.TextField(
        blank=True,
        help_text=_("Description of expense (for direct expense payments)"),
    )
    
    # For prepayments
    prepayment_account = models.ForeignKey(
        'Account',
        on_delete=models.SET_NULL,
        related_name="prepayment_payment_requests",
        null=True,
        blank=True,
        limit_choices_to={'account_level': 3},
        help_text=_("Prepayment account (for prepayment payments)"),
    )
    prepayment_account_code = models.CharField(max_length=30, blank=True)
    
    # Treasury transaction link (created when payment is processed)
    # Note: TreasuryTransaction model may not exist yet, using BigIntegerField as placeholder
    treasury_transaction_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Related treasury transaction ID (created when paid)"),
    )
    treasury_transaction_number = models.CharField(max_length=30, blank=True)
    
    # Accounting document link (created when payment is processed)
    accounting_document = models.ForeignKey(
        'AccountingDocument',
        on_delete=models.SET_NULL,
        related_name="payment_requests",
        null=True,
        blank=True,
        help_text=_("Related accounting document (created when paid)"),
    )
    accounting_document_number = models.CharField(max_length=30, blank=True)
    
    notes = models.TextField(blank=True)
    document_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Payment Request")
        verbose_name_plural = _("Payment Requests")
        ordering = ("-request_date", "-request_code")
        indexes = [
            models.Index(fields=("company", "request_date"), name="acc_payreq_date_idx"),
            models.Index(fields=("company", "party"), name="acc_payreq_party_idx"),
            models.Index(fields=("company", "purchase_invoice"), name="acc_payreq_pinv_idx"),
            models.Index(fields=("company", "service_invoice"), name="acc_payreq_sinv_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.request_code} - {self.get_payment_type_display()}"

    def get_document_date_field_name(self):
        """Override to use request_date instead of document_date."""
        return 'request_date'

    def _generate_request_code(self) -> str:
        """
        Generates a unique code following the pattern PAYREQ-YYYYMM-XXXXXX scoped per company.
        """
        now = timezone.now()
        month_year = now.strftime("%Y%m")
        prefix = f"PAYREQ-{month_year}"
        last_request = (
            PaymentRequest.objects.filter(
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
        """Auto-generate request_code and cache reference codes."""
        if not self.request_code or not self.request_code.strip():
            self.request_code = self._generate_request_code()
        
        # Cache party_code
        if self.party and not self.party_code:
            self.party_code = self.party.party_code
        
        # Cache purchase_invoice_code
        if self.purchase_invoice and not self.purchase_invoice_code:
            self.purchase_invoice_code = self.purchase_invoice.invoice_code
        
        # Cache service_invoice_code
        if self.service_invoice and not self.service_invoice_code:
            self.service_invoice_code = self.service_invoice.invoice_code
        
        # Cache expense_category_code
        if self.expense_category and not self.expense_category_code:
            self.expense_category_code = self.expense_category.category_code
        
        # Cache prepayment_account_code
        if self.prepayment_account and not self.prepayment_account_code:
            self.prepayment_account_code = self.prepayment_account.account_code
        
        # Cache treasury_transaction_number
        # Note: TreasuryTransaction may not exist yet, so this is a placeholder
        # TODO: Implement when TreasuryTransaction model is created
        
        # Cache accounting_document_number
        if self.accounting_document and not self.accounting_document_number:
            self.accounting_document_number = self.accounting_document.document_number
        
        super().save(*args, **kwargs)


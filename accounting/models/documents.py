"""
Accounting Document models.
"""
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingDocumentBase, AccountingBaseModel, POSITIVE_DECIMAL
from .accounts import Account
from .fiscal_years import FiscalYear, Period


class AccountingDocument(AccountingDocumentBase):
    """Accounting document - core transactional record following double-entry bookkeeping."""
    DOCUMENT_TYPE_CHOICES = [
        ('MANUAL', _('Manual Entry')),
        ('AUTOMATIC', _('Automatic Entry')),
        ('OPENING', _('Opening Entry')),
        ('CLOSING', _('Closing Entry')),
        ('ADJUSTMENT', _('Adjustment')),
    ]

    STATUS_CHOICES = [
        ('DRAFT', _('Draft')),
        ('POSTED', _('Posted')),
        ('LOCKED', _('Locked')),
        ('REVERSED', _('Reversed')),
        ('CANCELLED', _('Cancelled')),
    ]

    document_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text=_("Auto-generated document number"),
    )
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text=_("Document classification"),
    )
    # fiscal_year is inherited from AccountingDocumentBase (FiscalYearMixin)
    # Override to make it required (not nullable)
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.PROTECT,
        related_name="documents",
        null=False,  # Required for AccountingDocument
        help_text=_("Fiscal year for document (auto-populated from document_date)"),
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.SET_NULL,
        related_name="documents",
        null=True,
        blank=True,
        help_text=_("Optional period reference"),
    )
    description = models.TextField(
        help_text=_("Document description/explanation"),
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("External reference (invoice number, receipt number, etc.)"),
    )
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Type of reference (e.g., 'INVENTORY_RECEIPT', 'SALES_INVOICE')"),
    )
    reference_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Foreign key to referenced document"),
    )
    total_debit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Sum of all debit lines"),
    )
    total_credit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Sum of all credit lines (must equal total_debit)"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text=_("Document workflow status"),
    )
    posted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When document was posted"),
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="accounting_documents_posted",
        null=True,
        blank=True,
        help_text=_("User who posted the document"),
    )
    locked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When document was locked"),
    )
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="accounting_documents_locked",
        null=True,
        blank=True,
        help_text=_("User who locked the document"),
    )
    reversed_document = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='reversal_documents',
        null=True,
        blank=True,
        help_text=_("Reference to reversal document if reversed"),
    )
    attachment_count = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Number of attached files"),
    )

    class Meta:
        verbose_name = _("Accounting Document")
        verbose_name_plural = _("Accounting Documents")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "document_number"),
                name="accounting_document_number_unique",
            ),
            models.CheckConstraint(
                check=models.Q(total_debit=models.F('total_credit')),
                name="accounting_document_balanced",
            ),
        ]
        ordering = ("company", "-document_date", "-document_number")

    def __str__(self) -> str:
        return f"{self.document_number} - {self.document_date}"
    
    @property
    def is_locked(self) -> bool:
        """Check if document is locked."""
        return self.status == 'LOCKED' or self.locked_at is not None
    
    def lock(self, user):
        """Lock the document to prevent editing/deletion."""
        from django.utils import timezone
        if not self.is_locked:
            self.status = 'LOCKED'
            self.locked_at = timezone.now()
            self.locked_by = user
            self.save(update_fields=['status', 'locked_at', 'locked_by'])
    
    def unlock(self, user=None):
        """Unlock the document to allow editing/deletion."""
        if self.is_locked:
            self.status = 'POSTED' if self.posted_at else 'DRAFT'
            self.locked_at = None
            self.locked_by = None
            self.save(update_fields=['status', 'locked_at', 'locked_by'])

    def clean(self):
        """Validate document totals."""
        if self.total_debit != self.total_credit:
            raise ValidationError(_("Total debits must equal total credits."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AccountingDocumentLine(AccountingBaseModel):
    """Line items for accounting documents."""
    document = models.ForeignKey(
        AccountingDocument,
        on_delete=models.CASCADE,
        related_name="lines",
        help_text=_("Parent document"),
    )
    line_number = models.PositiveSmallIntegerField(
        help_text=_("Sequential line number within document"),
    )
    sub_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="document_lines_as_sub",
        limit_choices_to={'account_level': 2},
        null=True,
        blank=True,
        help_text=_("Sub Account (معین)"),
    )
    tafsili_level_1 = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="document_lines_as_tafsili_1",
        limit_choices_to={'account_level': 3},
        null=True,
        blank=True,
        help_text=_("Tafsili Level 1 (تفصیلی سطح ۱)"),
    )
    tafsili_level_2 = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="document_lines_as_tafsili_2",
        limit_choices_to={'account_level': 3},
        null=True,
        blank=True,
        help_text=_("Tafsili Level 2 (تفصیلی سطح ۲)"),
    )
    tafsili_level_3 = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="document_lines_as_tafsili_3",
        limit_choices_to={'account_level': 3},
        null=True,
        blank=True,
        help_text=_("Tafsili Level 3 (تفصیلی سطح ۳)"),
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Line item description"),
    )
    debit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Debit amount"),
    )
    credit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Credit amount"),
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Sort order for display"),
    )

    @property
    def gl_account(self):
        """Auto-populate GL account from selected sub_account."""
        if self.sub_account:
            return self.sub_account.gl_account_relations.first().gl_account if self.sub_account.gl_account_relations.exists() else None
        return None

    class Meta:
        verbose_name = _("Accounting Document Line")
        verbose_name_plural = _("Accounting Document Lines")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "document", "line_number"),
                name="accounting_document_line_unique",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(debit__gt=0, credit=0) |
                    models.Q(debit=0, credit__gt=0)
                ),
                name="accounting_document_line_debit_or_credit",
            ),
        ]
        ordering = ("company", "document", "sort_order", "line_number")

    def __str__(self) -> str:
        return f"{self.document.document_number} - Line {self.line_number}"

    def clean(self):
        """Validate line amounts and account selections."""
        # Handle None values (from blank fields)
        debit = self.debit if self.debit is not None else Decimal('0.00')
        credit = self.credit if self.credit is not None else Decimal('0.00')

        if debit > 0 and credit > 0:
            raise ValidationError(_("Line must be either debit or credit, not both."))
        if debit == 0 and credit == 0:
            raise ValidationError(_("Line must have either debit or credit amount."))

        # Validate account selections
        has_any_account = (
            self.sub_account or
            self.tafsili_level_1 or
            self.tafsili_level_2 or
            self.tafsili_level_3
        )
        if not has_any_account:
            raise ValidationError(_('لطفاً حداقل یک حساب (معین یا تفصیلی) را انتخاب کنید.'))

        # Note: Tafsili levels are independent - no hierarchical validation required
        # Each level is filtered independently based on sub_account configuration in chart of accounts

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


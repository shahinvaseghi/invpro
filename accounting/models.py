"""
Models for accounting module.
"""
from decimal import Decimal
from typing import Optional

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
    NUMERIC_CODE_VALIDATOR,
    ENABLED_FLAG_CHOICES,
)

from inventory.utils.codes import generate_sequential_code


POSITIVE_DECIMAL = MinValueValidator(Decimal("0"))


class AccountingBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    """Base model for all accounting models."""
    class Meta:
        abstract = True


class FiscalYearMixin(models.Model):
    """
    Mixin to auto-populate fiscal_year_id from document_date.
    Use this mixin for models that have document_date and need fiscal_year_id.
    """
    fiscal_year = models.ForeignKey(
        'FiscalYear',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_set',
        null=True,
        blank=True,
        help_text=_("Fiscal year for this document (auto-populated from document_date)"),
    )
    
    class Meta:
        abstract = True
    
    def get_document_date_field_name(self):
        """
        Override this method if document_date field has a different name.
        Default: 'document_date'
        """
        return 'document_date'
    
    def save(self, *args, **kwargs):
        """Auto-populate fiscal_year_id from document_date."""
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


class AccountingSortableModel(AccountingBaseModel, SortableModel):
    """Base model for sortable accounting entities."""
    class Meta:
        abstract = True


class AccountingDocumentBase(AccountingBaseModel, LockableModel, FiscalYearMixin):
    """Base model for accounting documents."""
    document_code = models.CharField(max_length=30, blank=True, editable=False)
    document_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True


# Fiscal Year Management
class FiscalYear(AccountingBaseModel):
    """Fiscal year definition for accounting periods."""
    fiscal_year_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("Fiscal year code (e.g., '1403')"),
    )
    fiscal_year_name = models.CharField(
        max_length=100,
        help_text=_("Fiscal year name"),
    )
    start_date = models.DateField(
        help_text=_("Fiscal year start date"),
    )
    end_date = models.DateField(
        help_text=_("Fiscal year end date"),
    )
    is_current = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("Current fiscal year flag"),
    )
    is_closed = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("Closed fiscal year flag"),
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="accounting_fiscal_years_closed",
        null=True,
        blank=True,
    )
    opening_document_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Reference to opening entry document (will be FK to AccountingDocument)"),
    )
    closing_document_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Reference to closing entry document (will be FK to AccountingDocument)"),
    )

    class Meta:
        verbose_name = _("Fiscal Year")
        verbose_name_plural = _("Fiscal Years")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "fiscal_year_code"),
                name="accounting_fiscal_year_code_unique",
            ),
        ]
        ordering = ("company", "-fiscal_year_code")

    def __str__(self) -> str:
        return f"{self.fiscal_year_code} - {self.fiscal_year_name}"

    def clean(self):
        """Validate fiscal year dates."""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_("End date must be after start date."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Period(AccountingBaseModel):
    """Accounting period within a fiscal year (typically monthly)."""
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.CASCADE,
        related_name="periods",
    )
    period_code = models.CharField(
        max_length=10,
        help_text=_("Period code (e.g., '1403-01')"),
    )
    period_name = models.CharField(
        max_length=100,
        help_text=_("Period name"),
    )
    start_date = models.DateField(
        help_text=_("Period start date"),
    )
    end_date = models.DateField(
        help_text=_("Period end date"),
    )
    is_closed = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("Closed period flag"),
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="accounting_periods_closed",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Period")
        verbose_name_plural = _("Periods")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "fiscal_year", "period_code"),
                name="accounting_period_code_unique",
            ),
        ]
        ordering = ("company", "fiscal_year", "period_code")

    def __str__(self) -> str:
        return f"{self.period_code} - {self.period_name}"

    def clean(self):
        """Validate period dates."""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_("End date must be after start date."))
        if self.fiscal_year:
            if self.start_date < self.fiscal_year.start_date:
                raise ValidationError(_("Period start date must be within fiscal year."))
            if self.end_date > self.fiscal_year.end_date:
                raise ValidationError(_("Period end date must be within fiscal year."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# Chart of Accounts
class Account(AccountingSortableModel):
    """Chart of Accounts - General, Subsidiary, and Detail accounts."""
    ACCOUNT_TYPE_CHOICES = [
        ('ASSET', _('Asset')),
        ('LIABILITY', _('Liability')),
        ('EQUITY', _('Equity')),
        ('REVENUE', _('Revenue')),
        ('EXPENSE', _('Expense')),
    ]

    ACCOUNT_LEVEL_CHOICES = [
        (1, _('General Ledger (کل)')),
        (2, _('Subsidiary Ledger (معین)')),
        (3, _('Detail Ledger (تفصیلی)')),
    ]

    NORMAL_BALANCE_CHOICES = [
        ('DEBIT', _('Debit')),
        ('CREDIT', _('Credit')),
    ]

    account_code = models.CharField(
        max_length=20,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("Hierarchical account code (e.g., '1.01.001')"),
    )
    account_name = models.CharField(
        max_length=200,
        help_text=_("Persian/local account name"),
    )
    account_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("English account name"),
    )
    account_type = models.CharField(
        max_length=30,
        choices=ACCOUNT_TYPE_CHOICES,
        help_text=_("Account classification"),
    )
    account_level = models.PositiveSmallIntegerField(
        choices=ACCOUNT_LEVEL_CHOICES,
        help_text=_("Account level: 1=General, 2=Subsidiary, 3=Detail"),
    )
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='child_accounts',
        null=True,
        blank=True,
        help_text=_("Parent account for hierarchical structure"),
    )
    normal_balance = models.CharField(
        max_length=10,
        choices=NORMAL_BALANCE_CHOICES,
        help_text=_("Expected balance side"),
    )
    is_system_account = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("System-generated accounts cannot be deleted"),
    )
    opening_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Opening balance for current fiscal year"),
    )
    current_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("Current period balance (calculated)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Account description and usage notes"),
    )

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "account_code"),
                name="accounting_account_code_unique",
            ),
        ]
        ordering = ("company", "account_code")

    def __str__(self) -> str:
        return f"{self.account_code} - {self.account_name}"

    def clean(self):
        """Validate account structure."""
        from django.core.exceptions import ValidationError
        
        # Validate parent account
        if self.parent_account:
            if self.parent_account.company_id != self.company_id:
                raise ValidationError(_("Parent account must belong to the same company."))
            if self.parent_account.account_level >= self.account_level:
                raise ValidationError(_("Parent account level must be less than child account level."))
        
        # Validate normal balance based on account type
        if self.account_type in ['ASSET', 'EXPENSE']:
            if self.normal_balance != 'DEBIT':
                raise ValidationError(_("Assets and Expenses must have DEBIT normal balance."))
        elif self.account_type in ['LIABILITY', 'EQUITY', 'REVENUE']:
            if self.normal_balance != 'CREDIT':
                raise ValidationError(_("Liabilities, Equity, and Revenue must have CREDIT normal balance."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AccountBalance(AccountingBaseModel):
    """Period-based account balance tracking."""
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="balances",
    )
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.CASCADE,
        related_name="account_balances",
    )
    period_start = models.DateField(
        help_text=_("Start date of balance period"),
    )
    period_end = models.DateField(
        help_text=_("End date of balance period"),
    )
    debit_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
    )
    credit_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
    )
    opening_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    closing_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Account Balance")
        verbose_name_plural = _("Account Balances")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "account", "fiscal_year", "period_start", "period_end"),
                name="accounting_account_balance_unique",
            ),
        ]
        ordering = ("company", "fiscal_year", "period_start")

    def __str__(self) -> str:
        return f"{self.account.account_code} - {self.period_start} to {self.period_end}"


# Accounting Documents
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

    def clean(self):
        """Validate document totals."""
        from django.core.exceptions import ValidationError
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
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="document_lines",
        help_text=_("Account being debited or credited"),
    )
    debit_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Debit amount (must be 0 if credit_amount > 0)"),
    )
    credit_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("Credit amount (must be 0 if debit_amount > 0)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Line item description"),
    )
    party_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Optional party reference (will be FK to accounting_party)"),
    )
    cost_center_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Optional cost center allocation (will be FK to accounting_cost_center)"),
    )
    project_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Optional project reference"),
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("VAT rate percentage if applicable"),
    )
    vat_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("VAT amount if applicable"),
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Additional reference for line item"),
    )

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
                    models.Q(debit_amount__gt=0, credit_amount=0) |
                    models.Q(debit_amount=0, credit_amount__gt=0)
                ),
                name="accounting_document_line_debit_or_credit",
            ),
        ]
        ordering = ("company", "document", "line_number")

    def __str__(self) -> str:
        return f"{self.document.document_number} - Line {self.line_number}"

    def clean(self):
        """Validate line amounts."""
        from django.core.exceptions import ValidationError
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError(_("Line must be either debit or credit, not both."))
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValidationError(_("Line must have either debit or credit amount."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

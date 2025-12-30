"""
Fiscal Year and Period models.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingBaseModel
from shared.models import ENABLED_FLAG_CHOICES, NUMERIC_CODE_VALIDATOR


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
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_("End date must be after start date."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Period(AccountingBaseModel):
    """Period within a fiscal year."""
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
                raise ValidationError(_("Start date must be before end date."))
            if self.fiscal_year:
                if self.start_date < self.fiscal_year.start_date:
                    raise ValidationError(_("Period start date must be within fiscal year."))
                if self.end_date > self.fiscal_year.end_date:
                    raise ValidationError(_("Period end date must be within fiscal year."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


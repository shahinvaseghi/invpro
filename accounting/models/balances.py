"""
Account Balance model for period-based balance tracking.
"""
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingBaseModel, POSITIVE_DECIMAL
from .accounts import Account
from .fiscal_years import FiscalYear


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


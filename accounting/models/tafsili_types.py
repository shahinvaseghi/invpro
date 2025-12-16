"""
Tafsili Type (نوع تفصیلی) model for accounting module.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingSortableModel
from shared.models import NUMERIC_CODE_VALIDATOR


class TafsiliType(AccountingSortableModel):
    """
    Tafsili Type (نوع تفصیلی) - Types of detailed accounts.
    Examples: Customer, Supplier, Employee, Project, Cost Center, Bank Account, Check, Other
    """
    public_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("کد عمومی نوع تفصیلی"),
    )
    name = models.CharField(
        max_length=100,
        help_text=_("نام نوع تفصیلی (فارسی)"),
    )
    name_en = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("نام نوع تفصیلی (انگلیسی)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("توضیحات"),
    )

    class Meta:
        verbose_name = _("نوع تفصیلی")
        verbose_name_plural = _("انواع تفصیلی")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="accounting_tafsili_type_company_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="accounting_tafsili_type_company_name_unique",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return f"{self.public_code} - {self.name}"


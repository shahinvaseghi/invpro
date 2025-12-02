"""
Cost Center models for accounting module.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingBaseModel, AccountingSortableModel
from shared.models import NUMERIC_CODE_VALIDATOR
from inventory.utils.codes import generate_sequential_code


class CostCenter(AccountingSortableModel):
    """Cost center model for tracking costs by organizational unit and work line."""
    
    cost_center_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("Cost center code (auto-generated if not provided)"),
        blank=True,
        editable=False,
    )
    cost_center_name = models.CharField(
        max_length=200,
        help_text=_("Cost center name (Persian)"),
    )
    cost_center_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Cost center name (English)"),
    )
    company_unit = models.ForeignKey(
        'shared.CompanyUnit',
        on_delete=models.PROTECT,
        related_name='cost_centers',
        help_text=_("Organizational unit this cost center belongs to"),
    )
    company_unit_code = models.CharField(
        max_length=5,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
        editable=False,
        help_text=_("Cached company unit code"),
    )
    work_line = models.ForeignKey(
        'production.WorkLine',
        on_delete=models.SET_NULL,
        related_name='cost_centers',
        null=True,
        blank=True,
        help_text=_("Production work line this cost center is associated with (optional - only if production module is installed)"),
    )
    work_line_code = models.CharField(
        max_length=5,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
        editable=False,
        help_text=_("Cached work line code"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description and notes about this cost center"),
    )

    class Meta:
        verbose_name = _("مرکز هزینه")
        verbose_name_plural = _("مراکز هزینه")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "cost_center_code"),
                name="accounting_cost_center_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "cost_center_name"),
                name="accounting_cost_center_name_unique",
            ),
        ]
        ordering = ("company", "sort_order", "cost_center_code")

    def __str__(self) -> str:
        return f"{self.cost_center_code} - {self.cost_center_name}"

    def save(self, *args, **kwargs):
        """Auto-generate cost center code if not provided."""
        if not self.cost_center_code and self.company_id:
            self.cost_center_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=10,
            )
        
        # Cache company unit code
        if self.company_unit and not self.company_unit_code:
            self.company_unit_code = self.company_unit.public_code
        
        # Cache work line code (if provided)
        if self.work_line and not self.work_line_code:
            self.work_line_code = self.work_line.public_code
        
        super().save(*args, **kwargs)


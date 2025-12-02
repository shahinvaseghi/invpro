"""
Income and Expense Category models for accounting module.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingSortableModel
from shared.models import NUMERIC_CODE_VALIDATOR
from inventory.utils.codes import generate_sequential_code


class IncomeExpenseCategory(AccountingSortableModel):
    """Category model for classifying income and expense transactions."""
    
    category_type = models.CharField(
        max_length=20,
        choices=[
            ('income', _('درآمد')),
            ('expense', _('هزینه')),
        ],
        help_text=_("Type of category: income or expense"),
    )
    category_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("Category code (auto-generated if not provided)"),
        blank=True,
        editable=False,
    )
    category_name = models.CharField(
        max_length=200,
        help_text=_("Category name (Persian)"),
    )
    category_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Category name (English)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description and notes about this category"),
    )
    
    class Meta:
        verbose_name = _("دسته‌بندی درآمد/هزینه")
        verbose_name_plural = _("دسته‌بندی‌های درآمد/هزینه")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "category_type", "category_code"),
                name="accounting_income_expense_category_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "category_type", "category_name"),
                name="accounting_income_expense_category_name_unique",
            ),
        ]
        ordering = ("company", "category_type", "sort_order", "category_code")

    def __str__(self) -> str:
        type_label = _("درآمد") if self.category_type == 'income' else _("هزینه")
        return f"{type_label} - {self.category_code} - {self.category_name}"

    def save(self, *args, **kwargs):
        """Auto-generate category code if not provided."""
        if not self.category_code and self.company_id and self.category_type:
            self.category_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                width=10,
                extra_filters={"category_type": self.category_type},
            )
        super().save(*args, **kwargs)


"""
Treasury Account models for accounting module.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .base import AccountingSortableModel
from shared.models import NUMERIC_CODE_VALIDATOR

User = get_user_model()


class TreasuryAccount(AccountingSortableModel):
    """Cash and bank account model for treasury management."""
    
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('cash', _('نقدی')),
            ('bank', _('بانکی')),
        ],
        help_text=_("Type of treasury account"),
    )
    tafsili_account = models.ForeignKey(
        'Account',
        on_delete=models.PROTECT,
        related_name='treasury_accounts',
        limit_choices_to={'account_level': 3},
        null=True,
        blank=True,
        help_text=_("حساب تفصیلی (فقط تفصیلی‌های قابل استفاده در فروش)"),
    )
    account_name = models.CharField(
        max_length=200,
        help_text=_("نام حساب نقدی/بانکی"),
    )
    account_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("نام حساب (انگلیسی)"),
    )
    bank_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("نام بانک (برای حساب‌های بانکی)"),
    )
    account_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("شماره حساب"),
    )
    branch_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("نام شعبه"),
    )
    branch_code = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("کد شعبه"),
    )
    iban = models.CharField(
        max_length=34,
        blank=True,
        help_text=_("شماره شبا (IBAN)"),
    )
    currency = models.CharField(
        max_length=3,
        default='IRR',
        help_text=_("واحد پول"),
    )
    initial_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0.00,
        help_text=_("موجودی اولیه"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("توضیحات و یادداشت‌ها"),
    )
    
    class Meta:
        verbose_name = _("حساب نقدی/بانکی")
        verbose_name_plural = _("حساب‌های نقدی و بانکی")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "tafsili_account"),
                name="accounting_treasury_account_tafsili_unique",
            ),
        ]
        ordering = ("company", "account_type", "sort_order", "account_name")

    def __str__(self) -> str:
        type_label = _("نقدی") if self.account_type == 'cash' else _("بانکی")
        return f"{type_label} - {self.account_name}"

    def clean(self):
        """Validate treasury account."""
        from django.core.exceptions import ValidationError

        # Validate tafsili_account is selected
        if not self.tafsili_account:
            raise ValidationError(_("حساب تفصیلی الزامی است."))

        # Validate tafsili_account belongs to company
        if self.company_id and self.tafsili_account.company_id != self.company_id:
            raise ValidationError(_("حساب تفصیلی انتخاب شده باید متعلق به شرکت فعال باشد."))

        # Validate tafsili_account is level 3
        if self.tafsili_account.account_level != 3:
            raise ValidationError(_("حساب تفصیلی باید سطح 3 باشد."))

        # Validate tafsili_account is usable in sales (has customer party)
        from .parties import PartyAccount
        if not PartyAccount.objects.filter(
            company_id=self.company_id,
            account=self.tafsili_account,
            party__party_type='customer'
        ).exists():
            raise ValidationError(_("حساب تفصیلی انتخاب شده باید قابل استفاده در فروش باشد (به مشتری متصل باشد)."))

    def save(self, *args, **kwargs):
        """Auto-set company."""
        # Set company from tafsili_account
        if not self.company_id and self.tafsili_account:
            self.company = self.tafsili_account.company

        self.clean()
        super().save(*args, **kwargs)


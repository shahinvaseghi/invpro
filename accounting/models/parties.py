"""
Party models for accounting module.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .base import AccountingSortableModel
from shared.models import NUMERIC_CODE_VALIDATOR
from inventory.utils.codes import generate_sequential_code

User = get_user_model()


class Party(AccountingSortableModel):
    """Party model for tracking customers, suppliers, and other business partners."""
    
    party_type = models.CharField(
        max_length=20,
        choices=[
            ('customer', _('مشتری')),
            ('supplier', _('تأمین‌کننده')),
            ('employee', _('کارمند')),
            ('other', _('سایر')),
        ],
        help_text=_("Type of party"),
    )
    party_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("Party code (auto-generated if not provided)"),
        blank=True,
        editable=False,
    )
    first_name = models.CharField(
        max_length=100,
        help_text=_("First name (Persian)"),
        verbose_name=_("نام"),
        default='',
    )
    last_name = models.CharField(
        max_length=100,
        help_text=_("Last name (Persian)"),
        verbose_name=_("نام خانوادگی"),
        default='',
    )
    party_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Party name (English)"),
    )
    national_id = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("National ID / Company Registration Number"),
    )
    tax_id = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Tax ID"),
    )
    address = models.TextField(
        blank=True,
        help_text=_("Address"),
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Phone number"),
    )
    email = models.EmailField(
        blank=True,
        help_text=_("Email address"),
    )
    contact_person = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Contact person name"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes"),
    )
    customer_tafsili_level = models.PositiveSmallIntegerField(
        choices=[
            (1, _('سطح ۱')),
            (2, _('سطح ۲')),
            (3, _('سطح ۳')),
        ],
        null=True,
        blank=True,
        help_text=_(""),
        verbose_name=_("نوع مشتری"),
    )

    class Meta:
        verbose_name = _("طرف حساب")
        verbose_name_plural = _("طرف حساب‌ها")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "party_code"),
                name="accounting_party_code_unique",
            ),
        ]
        ordering = ("company", "party_type", "sort_order", "party_code")

    @property
    def party_name(self) -> str:
        """Return full name combining first and last name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def customer_type_description(self) -> str:
        """Return customer type description based on customer_tafsili_level."""
        if self.party_type != 'customer' or not self.customer_tafsili_level:
            return ''

        try:
            from sales.models import SalesSettings
            settings = SalesSettings.get_or_create_for_company(self.company_id)
            desc_field = f'customer_tafsili_level_{self.customer_tafsili_level}_description'
            description = getattr(settings, desc_field, '')

            if description:
                return f'مشتری {self.customer_tafsili_level} - {description}'
            else:
                return f'مشتری {self.customer_tafsili_level}'
        except Exception:
            return f'مشتری {self.customer_tafsili_level}'

    def __str__(self) -> str:
        return f"{self.party_code} - {self.party_name}"

    def save(self, *args, **kwargs):
        """Auto-generate party code if not provided."""
        if not self.party_code and self.company_id and self.party_type:
            self.party_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                field='party_code',
                width=10,
                extra_filters={"party_type": self.party_type},
            )
        super().save(*args, **kwargs)


class PartyAccount(AccountingSortableModel):
    """Account model for parties linking to Tafsili accounts."""
    
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name='accounts',
        help_text=_("Party this account belongs to"),
    )
    account = models.ForeignKey(
        'Account',
        on_delete=models.PROTECT,
        related_name='party_accounts',
        limit_choices_to={'account_level': 3},
        help_text=_("Tafsili account for this party"),
    )
    account_code = models.CharField(
        max_length=30,
        blank=True,
        editable=False,
        help_text=_("Cached account code"),
    )
    account_name = models.CharField(
        max_length=200,
        blank=True,
        editable=False,
        help_text=_("Cached account name"),
    )
    is_primary = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Primary account for this party (1=Yes, 0=No)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about this account"),
    )
    
    class Meta:
        verbose_name = _("حساب طرف حساب")
        verbose_name_plural = _("حساب‌های طرف حساب")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "party", "account"),
                name="accounting_party_account_unique",
            ),
        ]
        ordering = ("company", "party", "-is_primary", "account_code")

    def __str__(self) -> str:
        return f"{self.party.party_name} - {self.account.account_code}"

    def save(self, *args, **kwargs):
        """Cache account code and name."""
        if self.account:
            if not self.account_code:
                self.account_code = self.account.account_code
            if not self.account_name:
                self.account_name = self.account.account_name
        super().save(*args, **kwargs)


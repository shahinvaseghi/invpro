"""
Models for sales module.
"""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from shared.models import (
    ActivatableModel,
    CompanyScopedModel,
    MetadataModel,
    SortableModel,
    TimeStampedModel,
)

POSITIVE_DECIMAL = MinValueValidator(Decimal("0"))


class SalesBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    """Base model for all sales models."""

    class Meta:
        abstract = True


class SalesSortableModel(SalesBaseModel, SortableModel):
    """Base model for sortable sales models."""

    class Meta:
        abstract = True


class ItemPriceCard(SalesSortableModel):
    """
    Model for storing item prices in sales module.
    Represents a price card for items that can be sold.
    """

    item = models.ForeignKey(
        "inventory.Item",
        on_delete=models.PROTECT,
        related_name="price_cards",
        verbose_name=_("Item"),
    )
    item_code = models.CharField(
        max_length=16,
        editable=False,
        verbose_name=_("Item Code"),
        help_text=_("Cached item code"),
    )
    price = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[POSITIVE_DECIMAL],
        verbose_name=_("Price"),
        help_text=_("Item price"),
    )
    currency = models.CharField(
        max_length=10,
        default="IRT",
        choices=(
            ("IRT", _("Toman")),
            ("IRR", _("Rial")),
            ("USD", _("US Dollar")),
        ),
        verbose_name=_("Currency"),
    )
    effective_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Effective Date"),
        help_text=_("Date when this price becomes effective"),
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Expiry Date"),
        help_text=_("Date when this price expires"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
    )

    class Meta:
        verbose_name = _("Item Price Card")
        verbose_name_plural = _("Item Price Cards")
        ordering = ("company", "sort_order", "item_code")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "item"),
                name="sales_item_price_card_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.item.name} - {self.price} {self.currency}"

    def save(self, *args, **kwargs):
        """Auto-populate item_code from item."""
        if self.item and not self.item_code:
            self.item_code = self.item.item_code
        super().save(*args, **kwargs)


class SalesSettings(SalesBaseModel):
    """
    Model for storing sales module settings.
    Stores tafsili type configuration for customers.
    """
    customer_tafsili_level_1 = models.ForeignKey(
        'accounting.TafsiliType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_settings_customer_level_1',
        verbose_name=_('نوع تفصیلی مشتری ۱'),
        help_text=_('نوع تفصیلی سطح ۱ برای مشتریان'),
    )
    customer_tafsili_level_2 = models.ForeignKey(
        'accounting.TafsiliType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_settings_customer_level_2',
        verbose_name=_('نوع تفصیلی مشتری ۲'),
        help_text=_('نوع تفصیلی سطح ۲ برای مشتریان'),
    )
    customer_tafsili_level_3 = models.ForeignKey(
        'accounting.TafsiliType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_settings_customer_level_3',
        verbose_name=_('نوع تفصیلی مشتری ۳'),
        help_text=_('نوع تفصیلی سطح ۳ برای مشتریان'),
    )
    customer_tafsili_level_1_description = models.TextField(
        blank=True,
        verbose_name=_('توضیحات سطح ۱'),
        help_text=_('توضیحات اضافی برای نوع تفصیلی سطح ۱ مشتریان'),
    )
    customer_tafsili_level_2_description = models.TextField(
        blank=True,
        verbose_name=_('توضیحات سطح ۲'),
        help_text=_('توضیحات اضافی برای نوع تفصیلی سطح ۲ مشتریان'),
    )
    customer_tafsili_level_3_description = models.TextField(
        blank=True,
        verbose_name=_('توضیحات سطح ۳'),
        help_text=_('توضیحات اضافی برای نوع تفصیلی سطح ۳ مشتریان'),
    )
    customer_tafsili_level_1_account_level = models.PositiveSmallIntegerField(
        choices=[
            (1, _('سطح ۱')),
            (2, _('سطح ۲')),
            (3, _('سطح ۳')),
        ],
        null=True,
        blank=True,
        verbose_name=_('سطح حساب ۱'),
        help_text=_('سطح حساب تفصیلی برای نوع تفصیلی سطح ۱'),
    )
    customer_tafsili_level_2_account_level = models.PositiveSmallIntegerField(
        choices=[
            (1, _('سطح ۱')),
            (2, _('سطح ۲')),
            (3, _('سطح ۳')),
        ],
        null=True,
        blank=True,
        verbose_name=_('سطح حساب ۲'),
        help_text=_('سطح حساب تفصیلی برای نوع تفصیلی سطح ۲'),
    )
    customer_tafsili_level_3_account_level = models.PositiveSmallIntegerField(
        choices=[
            (1, _('سطح ۱')),
            (2, _('سطح ۲')),
            (3, _('سطح ۳')),
        ],
        null=True,
        blank=True,
        verbose_name=_('سطح حساب ۳'),
        help_text=_('سطح حساب تفصیلی برای نوع تفصیلی سطح ۳'),
    )

    class Meta:
        verbose_name = _("Sales Settings")
        verbose_name_plural = _("Sales Settings")
        constraints = [
            models.UniqueConstraint(
                fields=("company",),
                name="sales_settings_company_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"Sales Settings - {self.company.display_name}"

    @classmethod
    def get_or_create_for_company(cls, company_id):
        """Get or create settings for a company."""
        settings, created = cls.objects.get_or_create(company_id=company_id)
        return settings

    @classmethod
    def get_customer_type_choices(cls, company_id):
        """Get customer type choices based on configured settings."""
        settings = cls.get_or_create_for_company(company_id)
        choices = []

        for level in range(1, 4):
            tafsili_field = f'customer_tafsili_level_{level}'
            tafsili_type = getattr(settings, tafsili_field, None)

            if tafsili_type:
                # Get description from settings
                desc_field = f'customer_tafsili_level_{level}_description'
                description = getattr(settings, desc_field, '')

                # Create choice with level number and tafsili type info
                choice_text = f'مشتری {level}'
                if description:
                    choice_text += f' - {description}'

                choices.append((level, choice_text))

        return choices


class IncomeReceiptLocation(SalesSortableModel):
    """
    Model for storing income receipt locations in sales module.
    Represents where and how income is received (cash, POS, bank transfer, etc.).
    """
    
    treasury_account = models.ForeignKey(
        "accounting.TreasuryAccount",
        on_delete=models.PROTECT,
        related_name="income_receipt_locations",
        verbose_name=_("Treasury Account"),
        help_text=_("حساب نقدی یا بانکی برای دریافت درآمد"),
    )
    receipt_method = models.CharField(
        max_length=50,
        choices=[
            ('pos', _('پوز')),
            ('cash', _('نقد')),
            ('account', _('حساب')),
            ('check', _('چک')),
            ('paya', _('پایا')),
            ('satna', _('ساتنا')),
            ('pay', _('پل')),
            ('multiple', _('چند مورد با هم')),
        ],
        verbose_name=_("Receipt Method"),
        help_text=_("روش دریافت درآمد"),
    )
    location_name = models.CharField(
        max_length=200,
        verbose_name=_("Location Name"),
        help_text=_("نام محل دریافت درآمد"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("توضیحات و یادداشت‌ها"),
    )

    class Meta:
        verbose_name = _("Income Receipt Location")
        verbose_name_plural = _("Income Receipt Locations")
        ordering = ("company", "sort_order", "location_name")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "treasury_account", "receipt_method", "location_name"),
                name="sales_income_receipt_location_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.location_name} - {self.get_receipt_method_display()}"


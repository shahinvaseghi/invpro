"""
Account models (GL, Sub, Tafsili) and relations.
"""
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingBaseModel, AccountingSortableModel, POSITIVE_DECIMAL
from shared.models import NUMERIC_CODE_VALIDATOR, ENABLED_FLAG_CHOICES


class Account(AccountingSortableModel):
    """Chart of Accounts - General, Subsidiary, and Detail accounts."""
    ACCOUNT_TYPE_CHOICES = [
        ('ASSET', _('دارایی')),
        ('LIABILITY', _('بدهی')),
        ('EQUITY', _('حقوق صاحبان سهام')),
        ('REVENUE', _('درآمد')),
        ('EXPENSE', _('هزینه')),
    ]

    ACCOUNT_LEVEL_CHOICES = [
        (1, _('کل')),
        (2, _('معین')),
        (3, _('تفصیلی')),
    ]

    NORMAL_BALANCE_CHOICES = [
        ('DEBIT', _('بدهکار')),
        ('CREDIT', _('بستانکار')),
    ]

    account_code = models.CharField(
        max_length=20,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("کد سلسله مراتبی حساب (مثال: '1.01.001')"),
    )
    account_name = models.CharField(
        max_length=200,
        help_text=_("نام حساب (فارسی)"),
    )
    account_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("نام حساب (انگلیسی)"),
    )
    account_type = models.CharField(
        max_length=30,
        choices=ACCOUNT_TYPE_CHOICES,
        help_text=_("نوع حساب"),
    )
    account_level = models.PositiveSmallIntegerField(
        choices=ACCOUNT_LEVEL_CHOICES,
        help_text=_("سطح حساب: 1=کل، 2=معین، 3=تفصیلی"),
    )
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='child_accounts',
        null=True,
        blank=True,
        help_text=_("حساب والد برای ساختار سلسله مراتبی"),
    )
    normal_balance = models.CharField(
        max_length=10,
        choices=NORMAL_BALANCE_CHOICES,
        help_text=_("طرف تراز مورد انتظار"),
    )
    is_system_account = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("حساب‌های تولید شده توسط سیستم قابل حذف نیستند"),
    )
    opening_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[POSITIVE_DECIMAL],
        help_text=_("مانده ابتدای سال مالی جاری"),
    )
    current_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("مانده جاری (محاسبه شده)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("توضیحات حساب و یادداشت‌های استفاده"),
    )

    class Meta:
        verbose_name = _("حساب")
        verbose_name_plural = _("حساب‌ها")
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


class SubAccountGLAccountRelation(AccountingBaseModel):
    """
    Many-to-many relationship between Sub Accounts (معین) and GL Accounts (کل).
    Allows a sub account to belong to multiple GL accounts.
    """
    sub_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='gl_account_relations',
        limit_choices_to={'account_level': 2},
        help_text=_("حساب معین"),
    )
    gl_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='sub_account_relations_as_gl',
        limit_choices_to={'account_level': 1},
        help_text=_("حساب کل"),
    )
    is_primary = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("حساب کل اصلی (برای نمایش پیش‌فرض)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("یادداشت‌های اضافی"),
    )

    class Meta:
        verbose_name = _("رابطه معین-کل")
        verbose_name_plural = _("روابط معین-کل")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "sub_account", "gl_account"),
                name="accounting_sub_gl_relation_unique",
            ),
        ]
        ordering = ("company", "sub_account", "-is_primary", "gl_account")

    def __str__(self) -> str:
        return f"{self.sub_account.account_code} → {self.gl_account.account_code}"

    def clean(self):
        """Validate relation."""
        if self.sub_account.account_level != 2:
            raise ValidationError(_("Sub account must be level 2 (معین)."))
        if self.gl_account.account_level != 1:
            raise ValidationError(_("GL account must be level 1 (کل)."))
        if self.sub_account.company_id != self.gl_account.company_id:
            raise ValidationError(_("Both accounts must belong to the same company."))
        if self.sub_account.account_type != self.gl_account.account_type:
            raise ValidationError(_("Sub account and GL account must have the same account type."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class TafsiliSubAccountRelation(AccountingBaseModel):
    """
    Many-to-many relationship between Tafsili Accounts (تفصیلی) and Sub Accounts (معین).
    Allows a tafsili account to belong to multiple sub accounts (floating tafsili).
    """
    tafsili_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='tafsili_sub_relations',
        limit_choices_to={'account_level': 3},
        help_text=_("حساب تفصیلی"),
    )
    sub_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='tafsili_account_relations',
        limit_choices_to={'account_level': 2},
        help_text=_("حساب معین"),
    )
    is_primary = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("حساب معین اصلی (برای نمایش پیش‌فرض)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("یادداشت‌های اضافی"),
    )

    class Meta:
        verbose_name = _("رابطه تفصیلی-معین")
        verbose_name_plural = _("روابط تفصیلی-معین")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "tafsili_account", "sub_account"),
                name="accounting_tafsili_sub_relation_unique",
            ),
        ]
        ordering = ("company", "tafsili_account", "-is_primary", "sub_account")

    def __str__(self) -> str:
        return f"{self.tafsili_account.account_code} → {self.sub_account.account_code}"

    def clean(self):
        """Validate relation."""
        if self.tafsili_account.account_level != 3:
            raise ValidationError(_("Tafsili account must be level 3 (تفصیلی)."))
        if self.sub_account.account_level != 2:
            raise ValidationError(_("Sub account must be level 2 (معین)."))
        if self.tafsili_account.company_id != self.sub_account.company_id:
            raise ValidationError(_("Both accounts must belong to the same company."))
        if self.tafsili_account.account_type != self.sub_account.account_type:
            raise ValidationError(_("Tafsili account and Sub account must have the same account type."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


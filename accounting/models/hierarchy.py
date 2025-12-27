"""
Tafsili Level model for tafsili level categorization.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingBaseModel
from .accounts import Account
from shared.models import NUMERIC_CODE_VALIDATOR, ENABLED_FLAG_CHOICES


class TafsiliHierarchy(AccountingBaseModel):
    """
    Tafsili Level (سطح تفضیلی) - allows grouping of tafsili accounts by associating them with sub accounts.
    """
    code = models.CharField(
        max_length=50,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("کد سطح تفضیلی (یکتا در شرکت)"),
    )
    name = models.CharField(
        max_length=200,
        help_text=_("نام سطح تفضیلی"),
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("نام سطح تفضیلی (انگلیسی)"),
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("ترتیب نمایش"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("توضیحات"),
    )

    class Meta:
        verbose_name = _("سطح تفضیلی")
        verbose_name_plural = _("سطوح تفضیلی")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "code"),
                name="accounting_tafsili_hierarchy_code_unique",
            ),
        ]
        ordering = ("company", "sort_order", "code")

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def clean(self):
        """Validate tafsili level."""
        # Validate unique code within company
        if self.company_id and self.code:
            existing = TafsiliHierarchy.objects.filter(
                company_id=self.company_id,
                code=self.code
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(_("کد سطح تفضیلی باید یکتا باشد."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class TafsiliLevelSubAccountRelation(AccountingBaseModel):
    """
    Many-to-many relationship between Tafsili Levels (سطح تفضیلی) and Sub Accounts (معین).
    Allows a tafsili level to be associated with multiple sub accounts.
    """
    tafsili_level = models.ForeignKey(
        TafsiliHierarchy,
        on_delete=models.CASCADE,
        related_name='sub_account_relations',
        help_text=_("سطح تفضیلی"),
    )
    sub_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='tafsili_level_relations',
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
        verbose_name = _("رابطه سطح تفضیلی-معین")
        verbose_name_plural = _("روابط سطح تفضیلی-معین")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "tafsili_level", "sub_account"),
                name="accounting_tafsili_level_sub_relation_unique",
            ),
        ]
        ordering = ("company", "tafsili_level", "-is_primary", "sub_account")

    def __str__(self) -> str:
        return f"{self.tafsili_level.code} → {self.sub_account.account_code}"

    def clean(self):
        """Validate relation."""
        if self.sub_account.account_level != 2:
            raise ValidationError(_("حساب باید سطح 2 (معین) باشد."))
        if self.tafsili_level.company_id != self.sub_account.company_id:
            raise ValidationError(_("سطح تفضیلی و حساب معین باید متعلق به همان شرکت باشند."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


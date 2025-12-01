"""
Tafsili Hierarchy model for multi-level tafsili categorization.
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
    Hierarchical structure for multi-level tafsili categorization.
    Allows creating tree structures for better organization and classification of tafsili accounts.
    """
    code = models.CharField(
        max_length=50,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("کد تفصیلی چند سطحی (یکتا در شرکت)"),
    )
    name = models.CharField(
        max_length=200,
        help_text=_("نام تفصیلی چند سطحی"),
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("نام تفصیلی چند سطحی (انگلیسی)"),
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        help_text=_("تفصیلی چند سطحی والد (برای ساختار درختی)"),
    )
    tafsili_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        related_name='hierarchies',
        null=True,
        blank=True,
        limit_choices_to={'account_level': 3},
        help_text=_("تفصیلی اصلی مرتبط (اختیاری - برای ریشه‌های درخت)"),
    )
    level = models.PositiveSmallIntegerField(
        default=1,
        editable=False,
        help_text=_("سطح در درخت (1=ریشه، 2=زیرگروه اول، ...)"),
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
        verbose_name = _("تفصیلی چند سطحی")
        verbose_name_plural = _("تفصیلی‌های چند سطحی")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "code"),
                name="accounting_tafsili_hierarchy_code_unique",
            ),
        ]
        ordering = ("company", "level", "sort_order", "code")

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def clean(self):
        """Validate hierarchy structure."""
        if self.parent:
            if self.parent.company_id != self.company_id:
                raise ValidationError(_("تفصیلی چند سطحی والد باید متعلق به همان شرکت باشد."))
            
            # Prevent circular references
            current = self.parent
            depth = 0
            while current and depth < 100:  # Safety limit
                if current.id == self.id:
                    raise ValidationError(_("نمی‌توان یک تفصیلی چند سطحی را والد خودش قرار داد."))
                current = current.parent
                depth += 1
        
        # Validate tafsili_account if provided
        if self.tafsili_account:
            if self.tafsili_account.company_id != self.company_id:
                raise ValidationError(_("تفصیلی اصلی باید متعلق به همان شرکت باشد."))
            if self.tafsili_account.account_level != 3:
                raise ValidationError(_("تفصیلی اصلی باید سطح 3 (تفصیلی) باشد."))

    def save(self, *args, **kwargs):
        # Calculate level based on parent
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        
        self.clean()
        super().save(*args, **kwargs)
        
        # Update children levels if level changed
        if self.pk:
            for child in self.children.all():
                child.save()  # This will recalculate child's level

    def get_full_path(self):
        """Get full path from root to this node."""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)

    def get_full_code_path(self):
        """Get full code path from root to this node."""
        path = [self.code]
        current = self.parent
        while current:
            path.insert(0, current.code)
            current = current.parent
        return ' > '.join(path)


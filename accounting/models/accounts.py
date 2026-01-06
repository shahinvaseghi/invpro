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


class AccountGroup(AccountingSortableModel):
    """گروه حساب‌ها - سطح بالاتر از حساب کل که حساب‌های کل را دسته‌بندی می‌کند."""
    
    group_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        help_text=_("کد گروه حساب (مثال: '1' برای دارایی‌های جاری)"),
    )
    group_name = models.CharField(
        max_length=200,
        help_text=_("نام گروه حساب (فارسی)"),
    )
    group_name_en = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("نام گروه حساب (انگلیسی)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("توضیحات گروه حساب"),
    )
    
    class Meta:
        verbose_name = _("گروه حساب")
        verbose_name_plural = _("گروه‌های حساب")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "group_code"),
                name="accounting_account_group_code_unique",
            ),
        ]
        ordering = ("company", "group_code")
    
    def __str__(self) -> str:
        return f"{self.group_code} - {self.group_name}"


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
        help_text=_("کد حساب (مثال: '11' برای حساب کل، '1101' برای معین)"),
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
        null=True,
        blank=True,
        help_text=_("نوع حساب (در سند حسابداری تعریف می‌شود)"),
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
        null=True,
        blank=True,
        help_text=_("طرف تراز مورد انتظار (در سند حسابداری تعریف می‌شود)"),
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
    tafsili_type = models.ForeignKey(
        'TafsiliType',
        on_delete=models.PROTECT,
        related_name='tafsili_accounts',
        null=True,
        blank=True,
        help_text=_("نوع تفصیلی (فقط برای حساب‌های تفصیلی)"),
    )
    tafsili_level = models.PositiveSmallIntegerField(
        choices=[(1, _('سطح 1')), (2, _('سطح 2')), (3, _('سطح 3'))],
        null=True,
        blank=True,
        help_text=_("سطح تفصیلی (1 تا 3) - فقط برای حساب‌های تفصیلی"),
    )
    is_tafsili_enabled = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("تفصیل پذیر (فقط برای حساب‌های معین)"),
    )
    account_group = models.ForeignKey(
        'AccountGroup',
        on_delete=models.PROTECT,
        related_name='accounts',
        null=True,
        blank=True,
        limit_choices_to={'is_enabled': 1},
        help_text=_("گروه حساب (فقط برای حساب‌های کل)"),
    )

    class Meta:
        verbose_name = _("حساب")
        verbose_name_plural = _("حساب‌ها")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "account_code", "account_level"),
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
        
        # Validate account_group: only GL accounts (level 1) can have account_group
        if self.account_group:
            if self.account_level != 1:
                raise ValidationError(_("گروه حساب فقط برای حساب‌های کل قابل تعریف است."))
            if self.account_group.company_id != self.company_id:
                raise ValidationError(_("گروه حساب باید متعلق به همان شرکت باشد."))
        
        # Validate tafsili_level: only tafsili accounts (level 3) can have tafsili_level
        if self.tafsili_level is not None:
            if self.account_level != 3:
                raise ValidationError(_("سطح تفصیلی فقط برای حساب‌های تفصیلی قابل تعریف است."))
        
        # Validate tafsili_type: only tafsili accounts (level 3) can have tafsili_type
        if self.tafsili_type:
            if self.account_level != 3:
                raise ValidationError(_("نوع تفصیلی فقط برای حساب‌های تفصیلی قابل تعریف است."))
            if self.tafsili_type.company_id != self.company_id:
                raise ValidationError(_("نوع تفصیلی باید متعلق به همان شرکت باشد."))
        
        # Validate is_tafsili_enabled: only sub accounts (level 2) should have this flag
        # (not enforced, but documented)

    def save(self, *args, **kwargs):
        self.clean()
        # User must enter account_code manually for all account levels
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

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class SubAccountTafsiliTypeRelation(AccountingBaseModel):
    """
    Many-to-many relationship between Sub Accounts (معین) and Tafsili Types (نوع تفصیلی) for each level (1-3).
    Specifies which tafsili types can be used for each level (1, 2, 3) in a sub account.
    """
    sub_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='tafsili_type_relations',
        limit_choices_to={'account_level': 2},
        help_text=_("حساب معین"),
    )
    tafsili_type = models.ForeignKey(
        'TafsiliType',
        on_delete=models.CASCADE,
        related_name='sub_account_relations',
        help_text=_("نوع تفصیلی"),
    )
    level = models.PositiveSmallIntegerField(
        choices=[(1, _('سطح 1')), (2, _('سطح 2')), (3, _('سطح 3'))],
        help_text=_("سطح تفصیلی (1 تا 3)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("یادداشت‌های اضافی"),
    )

    class Meta:
        verbose_name = _("رابطه معین-نوع تفصیلی")
        verbose_name_plural = _("روابط معین-نوع تفصیلی")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "sub_account", "tafsili_type", "level"),
                name="accounting_sub_tafsili_type_level_unique",
            ),
        ]
        ordering = ("company", "sub_account", "level", "tafsili_type")

    def __str__(self) -> str:
        return f"{self.sub_account.account_code} - سطح {self.level} - {self.tafsili_type.name}"

    def clean(self):
        """Validate relation."""
        if self.sub_account.account_level != 2:
            raise ValidationError(_("حساب باید سطح 2 (معین) باشد."))
        if self.sub_account.company_id != self.tafsili_type.company_id:
            raise ValidationError(_("حساب معین و نوع تفصیلی باید متعلق به همان شرکت باشند."))
        if self.level not in [1, 2, 3]:
            raise ValidationError(_("سطح باید بین 1 تا 3 باشد."))

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
        related_name='sub_account_relations_as_tafsili',
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

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class SubAccountTafsiliLevel1Relation(AccountingBaseModel):
    """
    رابطه مستقیم بین معین و تفصیلی سطح ۱.
    هر معین مشخص می‌کنه که به کدوم تفصیلی‌های سطح ۱ وصل هست.
    """
    sub_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='tafsili_level1_relations',
        limit_choices_to={'account_level': 2},
        help_text=_("حساب معین")
    )
    tafsili_level1_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='sub_account_level1_relations',
        limit_choices_to={'account_level': 3, 'tafsili_level': 1},
        help_text=_("حساب تفصیلی سطح ۱")
    )
    is_primary = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        help_text=_("حساب تفصیلی سطح ۱ اصلی (برای نمایش پیش‌فرض)")
    )
    notes = models.TextField(
        blank=True,
        help_text=_("یادداشت‌های اضافی")
    )

    class Meta:
        verbose_name = _("رابطه معین-تفصیلی سطح ۱")
        verbose_name_plural = _("روابط معین-تفصیلی سطح ۱")
        ordering = ("company", "sub_account", "-is_primary", "tafsili_level1_account")

    def __str__(self) -> str:
        return f"{self.sub_account.account_code} → {self.tafsili_level1_account.account_code}"

    def clean(self):
        """Validate relation."""
        # Skip validation if objects are not loaded yet (during form validation)
        try:
            if self.sub_account and self.sub_account.account_level != 2:
                raise ValidationError(_("Sub account must be level 2 (معین)."))

            if self.tafsili_level1_account:
                if self.tafsili_level1_account.account_level != 3:
                    raise ValidationError(_("Tafsili account must be level 3 (تفصیلی)."))
                if self.tafsili_level1_account.tafsili_level != 1:
                    raise ValidationError(_("Tafsili account must be level 1."))

            # Validate company consistency
            if self.sub_account and self.tafsili_level1_account:
                if self.sub_account.company_id != self.tafsili_level1_account.company_id:
                    raise ValidationError(_("Both accounts must belong to the same company."))
        except:
            # If related objects are not loaded, skip validation
            # Validation will be done in the form
            pass


class TafsiliAccountHierarchy(AccountingBaseModel):
    """
    روابط سلسله مراتبی بین حساب‌های تفصیلی.
    امکان ایجاد ساختار درختی برای سازماندهی بهتر حساب‌های تفصیلی.
    """
    parent_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='hierarchy_children',
        limit_choices_to={'account_level': 3},
        help_text="حساب تفصیلی والد (parent)"
    )
    child_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='hierarchy_parents',
        limit_choices_to={'account_level': 3},
        help_text="حساب تفصیلی فرزند (child)"
    )
    level_depth = models.PositiveSmallIntegerField(
        default=1,
        help_text="عمق رابطه در درخت (۱=مستقیم، ۲=نوه، ...)"
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text="ترتیب نمایش در لیست"
    )
    notes = models.TextField(
        blank=True,
        help_text="یادداشت‌های اضافی"
    )

    class Meta:
        verbose_name = "رابطه سلسله مراتبی تفصیلی"
        verbose_name_plural = "روابط سلسله مراتبی تفصیلی"
        constraints = [
            models.UniqueConstraint(
                fields=("company", "parent_account", "child_account"),
                name="accounting_tafsili_hierarchy_unique",
            ),
        ]
        ordering = ("company", "sort_order", "parent_account", "child_account")

    def __str__(self) -> str:
        return f"{self.parent_account.account_code} → {self.child_account.account_code}"

    def clean(self):
        """Validate hierarchy relation."""
        if self.parent_account.account_level != 3:
            raise ValidationError(_("Parent account must be level 3 (تفصیلی)."))
        if self.child_account.account_level != 3:
            raise ValidationError(_("Child account must be level 3 (تفصیلی)."))
        if self.parent_account.company_id != self.child_account.company_id:
            raise ValidationError(_("Both accounts must belong to the same company."))
        if self.parent_account == self.child_account:
            raise ValidationError(_("Parent and child accounts cannot be the same."))

        # Validate tafsili level hierarchy - parent should have lower tafsili_level than child
        if (hasattr(self.parent_account, 'tafsili_level') and hasattr(self.child_account, 'tafsili_level')):
            if (self.parent_account.tafsili_level is not None and self.child_account.tafsili_level is not None):
                if self.parent_account.tafsili_level >= self.child_account.tafsili_level:
                    raise ValidationError(
                        _("حساب والد باید سطح تفصیلی پایین‌تری نسبت به حساب فرزند داشته باشد. "
                          "مثلاً سطح ۱ می‌تواند والد سطح ۲ باشد، سطح ۲ می‌تواند والد سطح ۳ باشد.")
                    )

        # Check for circular reference
        if self._has_circular_reference(self.parent_account, self.child_account):
            raise ValidationError(_("This relation would create a circular reference."))

        # Calculate level_depth automatically
        self.level_depth = self._calculate_level_depth()

    def _has_circular_reference(self, parent, child, visited=None):
        """Check if adding this relation would create a circular reference."""
        if visited is None:
            visited = set()

        if parent in visited:
            return True

        visited.add(parent)

        # Check all children of the child account
        for relation in TafsiliAccountHierarchy.objects.filter(
            company=self.company,
            parent_account=child
        ).exclude(id=self.id if self.pk else None):
            if self._has_circular_reference(parent, relation.child_account, visited.copy()):
                return True

        return False

    def _calculate_level_depth(self):
        """Calculate the depth level of this relation in the hierarchy tree."""
        # Find the maximum depth path from parent to this child
        max_depth = 1

        # Check if parent has any parents (indirect ancestors)
        for ancestor_relation in TafsiliAccountHierarchy.objects.filter(
            company=self.company,
            child_account=self.parent_account
        ):
            # This relation adds one level to the ancestor's depth
            max_depth = max(max_depth, ancestor_relation.level_depth + 1)

        return max_depth

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


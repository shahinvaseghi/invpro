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
    tafsili_level = models.ForeignKey(
        'TafsiliHierarchy',
        on_delete=models.PROTECT,
        related_name='treasury_accounts',
        null=True,
        blank=True,
        help_text=_("سطح تفصیلی (یا سطح تفصیلی یا معین باید انتخاب شود)"),
    )
    tafsili_account = models.ForeignKey(
        'Account',
        on_delete=models.PROTECT,
        related_name='treasury_accounts',
        limit_choices_to={'account_level': 3},
        null=True,
        blank=True,
        editable=False,
        help_text=_("حساب تفصیلی (خودکار ساخته می‌شود)"),
    )
    sub_account = models.ForeignKey(
        'Account',
        on_delete=models.PROTECT,
        related_name='treasury_accounts_as_sub',
        limit_choices_to={'account_level': 2},
        null=True,
        blank=True,
        help_text=_("معین حساب (یا سطح تفصیلی یا معین باید انتخاب شود)"),
    )
    gl_account = models.ForeignKey(
        'Account',
        on_delete=models.PROTECT,
        related_name='treasury_accounts_as_gl',
        limit_choices_to={'account_level': 1},
        null=True,
        blank=True,
        help_text=_("حساب کل (خودکار از معین)"),
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
                condition=models.Q(tafsili_account__isnull=False),
            ),
        ]
        ordering = ("company", "account_type", "sort_order", "account_name")

    def __str__(self) -> str:
        type_label = _("نقدی") if self.account_type == 'cash' else _("بانکی")
        return f"{type_label} - {self.account_name}"

    def clean(self):
        """Validate account hierarchy."""
        from django.core.exceptions import ValidationError
        
        # Validate that either tafsili_level or sub_account is selected, but not both
        if not self.tafsili_level and not self.sub_account:
            raise ValidationError(_("باید یا سطح تفصیلی انتخاب شود یا حساب معین (حداقل یکی از آن‌ها الزامی است)."))
        
        if self.tafsili_level and self.sub_account:
            raise ValidationError(_("نمی‌توان هم سطح تفصیلی و هم حساب معین را انتخاب کرد. فقط یکی از آن‌ها باید انتخاب شود."))
        
        if self.tafsili_level:
            # Validate tafsili_level belongs to company
            if self.company_id and self.tafsili_level.company_id != self.company_id:
                raise ValidationError(_("سطح تفصیلی انتخاب شده باید متعلق به شرکت فعال باشد."))
        
        if self.sub_account:
            # Validate sub_account is level 2
            if self.sub_account.account_level != 2:
                raise ValidationError(_("حساب معین باید سطح 2 باشد."))
            
            # If gl_account is set, validate it's related to sub_account
            if self.gl_account:
                from .accounts import SubAccountGLAccountRelation
                if not SubAccountGLAccountRelation.objects.filter(
                    company_id=self.company_id,
                    sub_account=self.sub_account,
                    gl_account=self.gl_account,
                ).exists():
                    raise ValidationError(_("حساب کل انتخاب شده برای این معین مجاز نیست."))

    def save(self, *args, **kwargs):
        """Auto-set company and create tafsili account if needed."""
        # Set company
        if not self.company_id:
            if self.tafsili_level:
                self.company = self.tafsili_level.company
            elif self.sub_account:
                self.company = self.sub_account.company
        
        self.clean()
        
        # Save first to get pk
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        # Create tafsili account automatically if it doesn't exist
        if not self.tafsili_account:
            from .accounts import Account, TafsiliSubAccountRelation
            from .hierarchy import TafsiliLevelSubAccountRelation
            from inventory.utils.codes import generate_sequential_code
            
            # Generate account code
            account_code = generate_sequential_code(
                Account,
                company_id=self.company_id,
                field='account_code',
                width=10,
                extra_filters={'account_level': 3},
            )
            
            # Create tafsili account
            tafsili_account = Account.objects.create(
                company=self.company,
                account_code=account_code,
                account_name=self.account_name,
                account_name_en=self.account_name_en or '',
                account_level=3,
                is_system_account=1,  # Mark as system account
                created_by=getattr(self, 'created_by', None),
            )
            
            self.tafsili_account = tafsili_account
            
            # Create relations based on selection
            if self.tafsili_level:
                # Get sub accounts from tafsili_level
                relations = TafsiliLevelSubAccountRelation.objects.filter(
                    company_id=self.company_id,
                    tafsili_level=self.tafsili_level,
                    is_enabled=1
                ).select_related('sub_account')
                
                for relation in relations:
                    TafsiliSubAccountRelation.objects.get_or_create(
                        company_id=self.company_id,
                        tafsili_account=tafsili_account,
                        sub_account=relation.sub_account,
                        defaults={'is_primary': relation.is_primary}
                    )
            elif self.sub_account:
                # Create relation with selected sub_account
                TafsiliSubAccountRelation.objects.get_or_create(
                    company_id=self.company_id,
                    tafsili_account=tafsili_account,
                    sub_account=self.sub_account,
                    defaults={'is_primary': 1}
                )
            
            # Save again to update tafsili_account
            super().save(*args, **kwargs)


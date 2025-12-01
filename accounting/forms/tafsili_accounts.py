"""
Forms for Tafsili Account (حساب تفصیلی) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Account, TafsiliSubAccountRelation


TAFSILI_TYPE_CHOICES = [
    ('CUSTOMER', _('مشتری')),
    ('SUPPLIER', _('فروشنده')),
    ('EMPLOYEE', _('پرسنل')),
    ('PROJECT', _('پروژه')),
    ('COST_CENTER', _('مرکز هزینه')),
    ('BANK_ACCOUNT', _('حساب بانکی')),
    ('CHECK', _('چک')),
    ('OTHER', _('سایر')),
]


class TafsiliAccountForm(forms.ModelForm):
    """Form for creating/editing Tafsili accounts (حساب تفصیلی)."""
    
    tafsili_type = forms.ChoiceField(
        choices=TAFSILI_TYPE_CHOICES,
        label=_('نوع تفصیلی'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )
    is_floating = forms.BooleanField(
        label=_('تفصیلی شناور'),
        help_text=_('اگر فعال باشد، می‌تواند به چند معین ارتباط داده شود'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    national_id = forms.CharField(
        max_length=20,
        label=_('کد ملی / شناسه ملی / کد اقتصادی'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    bank_account_number = forms.CharField(
        max_length=50,
        label=_('شماره حساب بانکی'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    contact_info = forms.CharField(
        max_length=500,
        label=_('اطلاعات تماس (آدرس/تلفن/ایمیل)'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )
    
    sub_accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        label=_('حساب‌های معین مرتبط'),
        help_text=_('می‌توانید یک یا چند حساب معین را انتخاب کنید'),
        required=False,
    )
    
    class Meta:
        model = Account
        fields = [
            'account_code',
            'account_name',
            'account_name_en',
            'normal_balance',
            'opening_balance',
            'description',
            'is_enabled',
        ]
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'normal_balance': forms.Select(attrs={'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_code': _('کد تفصیلی'),
            'account_name': _('نام تفصیلی'),
            'account_name_en': _('نام تفصیلی (انگلیسی)'),
            'normal_balance': _('طرف تراز'),
            'opening_balance': _('مانده ابتدای دوره'),
            'description': _('شرح'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, exclude_account_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Set account_level to 3 (تفصیلی) for Tafsili accounts
        if not self.instance.pk:
            self.instance.account_level = 3
        
        # Remove account_level and account_type from form
        if 'account_level' in self.fields:
            del self.fields['account_level']
        if 'account_type' in self.fields:
            del self.fields['account_type']
        if 'parent_account' in self.fields:
            del self.fields['parent_account']
        
        # Filter sub accounts for multiple choice
        if company_id:
            sub_queryset = Account.objects.filter(
                company_id=company_id,
                account_level=2,
                is_enabled=1
            ).order_by('account_code')
            self.fields['sub_accounts'].queryset = sub_queryset
            
            # Load existing relations for edit
            if self.instance.pk:
                from accounting.models import TafsiliSubAccountRelation
                existing_sub_accounts = TafsiliSubAccountRelation.objects.filter(
                    tafsili_account=self.instance,
                    company_id=company_id
                ).values_list('sub_account_id', flat=True)
                self.initial['sub_accounts'] = list(existing_sub_accounts)
                
                # Load is_floating from existing relations
                if existing_sub_accounts.count() > 1:
                    self.initial['is_floating'] = True
        
        # Load additional fields from description if editing
        if self.instance.pk and self.instance.description:
            # Try to parse additional info from description (simple approach)
            # In production, you might want to use a JSON field or separate model
            pass
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        sub_accounts = cleaned_data.get('sub_accounts', [])
        account_code = cleaned_data.get('account_code')
        is_floating = cleaned_data.get('is_floating', False)
        
        # Validate sub accounts
        if not is_floating and not sub_accounts:
            raise forms.ValidationError({
                'sub_accounts': _('برای تفصیلی غیرشناور، حداقل یک حساب معین باید انتخاب شود.')
            })
        
        # Check all sub accounts belong to same company
        if self.company_id and sub_accounts:
            for sub_account in sub_accounts:
                if sub_account.company_id != self.company_id:
                    raise forms.ValidationError({
                        'sub_accounts': _('همه حساب‌های معین باید متعلق به همان شرکت باشند.')
                    })
                if sub_account.account_level != 2:
                    raise forms.ValidationError({
                        'sub_accounts': _('همه انتخاب‌ها باید حساب معین (سطح 2) باشند.')
                    })
            
            # Inherit account_type and normal_balance from first sub account
            if sub_accounts:
                first_sub = sub_accounts[0]
                if not self.instance.pk or not self.instance.account_type:
                    self.instance.account_type = first_sub.account_type
                if not self.instance.pk or not self.instance.normal_balance:
                    self.instance.normal_balance = first_sub.normal_balance
                
                # Check all sub accounts have same type
                for sub_account in sub_accounts[1:]:
                    if sub_account.account_type != first_sub.account_type:
                        raise forms.ValidationError({
                            'sub_accounts': _('همه حساب‌های معین باید از یک نوع باشند.')
                        })
        
        # Validate unique code globally (for tafsili accounts)
        if account_code and self.company_id:
            existing = Account.objects.filter(
                company_id=self.company_id,
                account_code=account_code,
                account_level=3
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError({
                    'account_code': _('کد تفصیلی باید یکتا باشد در کل سیستم.')
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save account and create relations."""
        instance = super().save(commit=commit)
        
        if commit and self.company_id:
            # Delete existing relations
            TafsiliSubAccountRelation.objects.filter(
                tafsili_account=instance,
                company_id=self.company_id
            ).delete()
            
            # Create new relations
            sub_accounts = self.cleaned_data.get('sub_accounts', [])
            for idx, sub_account in enumerate(sub_accounts):
                TafsiliSubAccountRelation.objects.create(
                    tafsili_account=instance,
                    sub_account=sub_account,
                    company=instance.company,
                    is_primary=1 if idx == 0 else 0,  # First one is primary
                    created_by=self.instance.created_by if hasattr(self.instance, 'created_by') else None,
                )
        
        return instance


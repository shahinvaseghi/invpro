"""
Forms for Treasury Account management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import TreasuryAccount, Account
from shared.models import Company


class TreasuryAccountForm(forms.ModelForm):
    """Form for creating/editing treasury accounts."""
    
    class Meta:
        model = TreasuryAccount
        fields = [
            'account_type',
            'tafsili_account',
            'sub_account',
            'gl_account',
            'account_name',
            'account_name_en',
            'bank_name',
            'account_number',
            'branch_name',
            'branch_code',
            'iban',
            'currency',
            'initial_balance',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'account_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_account_type'}),
            'tafsili_account': forms.Select(attrs={'class': 'form-control', 'id': 'id_tafsili_account'}),
            'sub_account': forms.Select(attrs={'class': 'form-control', 'id': 'id_sub_account'}),
            'gl_account': forms.Select(attrs={'class': 'form-control', 'id': 'id_gl_account', 'readonly': True}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_code': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'initial_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_type': _('نوع حساب'),
            'tafsili_account': _('حساب تفصیلی'),
            'sub_account': _('حساب معین'),
            'gl_account': _('حساب کل'),
            'account_name': _('نام حساب'),
            'account_name_en': _('نام حساب (انگلیسی)'),
            'bank_name': _('نام بانک'),
            'account_number': _('شماره حساب'),
            'branch_name': _('نام شعبه'),
            'branch_code': _('کد شعبه'),
            'iban': _('شماره شبا'),
            'currency': _('واحد پول'),
            'initial_balance': _('موجودی اولیه'),
            'notes': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
        help_texts = {
            'tafsili_account': _('ابتدا حساب تفصیلی را انتخاب کنید'),
            'sub_account': _('معین‌های مجاز برای تفصیلی انتخاب شده نمایش داده می‌شود'),
            'gl_account': _('حساب کل به صورت خودکار از معین انتخاب می‌شود'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if company_id:
            # Set company for new instances
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
            
            # Filter tafsili accounts (level 3)
            if 'tafsili_account' in self.fields:
                self.fields['tafsili_account'].queryset = Account.objects.filter(
                    company_id=company_id,
                    account_level=3,
                    is_enabled=1
                ).order_by('account_code')
                self.fields['tafsili_account'].empty_label = _("--- انتخاب کنید ---")
                self.fields['tafsili_account'].label_from_instance = lambda obj: f"{obj.account_code} · {obj.account_name}"
            
            # Initially disable sub_account and gl_account
            if 'sub_account' in self.fields:
                self.fields['sub_account'].queryset = Account.objects.none()
                self.fields['sub_account'].required = False
                self.fields['sub_account'].empty_label = _("--- ابتدا تفصیلی را انتخاب کنید ---")
            
            if 'gl_account' in self.fields:
                self.fields['gl_account'].queryset = Account.objects.none()
                self.fields['gl_account'].required = False
                self.fields['gl_account'].empty_label = _("--- ابتدا معین را انتخاب کنید ---")
    
    def clean(self):
        """Validate account hierarchy."""
        cleaned_data = super().clean()
        tafsili_account = cleaned_data.get('tafsili_account')
        sub_account = cleaned_data.get('sub_account')
        gl_account = cleaned_data.get('gl_account')
        
        if tafsili_account and self.company_id:
            # Validate tafsili belongs to company
            if tafsili_account.company_id != self.company_id:
                raise forms.ValidationError(_('حساب تفصیلی انتخاب شده باید متعلق به شرکت فعال باشد.'))
            
            # If sub_account is selected, validate it's related to tafsili
            if sub_account:
                from ..models import TafsiliSubAccountRelation
                if not TafsiliSubAccountRelation.objects.filter(
                    company_id=self.company_id,
                    tafsili_account=tafsili_account,
                    sub_account=sub_account,
                ).exists():
                    raise forms.ValidationError(_('معین انتخاب شده برای این تفصیلی مجاز نیست.'))
                
                # If gl_account is selected, validate it's related to sub_account
                if gl_account:
                    from ..models import SubAccountGLAccountRelation
                    if not SubAccountGLAccountRelation.objects.filter(
                        company_id=self.company_id,
                        sub_account=sub_account,
                        gl_account=gl_account,
                    ).exists():
                        raise forms.ValidationError(_('حساب کل انتخاب شده برای این معین مجاز نیست.'))
        
        return cleaned_data


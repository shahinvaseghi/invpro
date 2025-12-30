"""
Forms for Treasury Account management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import TreasuryAccount, Account
from ..models.hierarchy import TafsiliHierarchy
from shared.models import Company


class TreasuryAccountForm(forms.ModelForm):
    """Form for creating/editing treasury accounts."""
    
    class Meta:
        model = TreasuryAccount
        fields = [
            'account_type',
            'tafsili_level',
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
            'tafsili_level': forms.Select(attrs={'class': 'form-control', 'id': 'id_tafsili_level'}),
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
            'tafsili_level': _('سطح تفصیلی'),
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
            'tafsili_level': _('یا سطح تفصیلی را انتخاب کنید یا حساب معین (هر دو با هم امکان‌پذیر نیست)'),
            'sub_account': _('یا حساب معین را انتخاب کنید یا سطح تفصیلی (هر دو با هم امکان‌پذیر نیست)'),
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
            
            # Filter tafsili levels
            if 'tafsili_level' in self.fields:
                self.fields['tafsili_level'].queryset = TafsiliHierarchy.objects.filter(
                    company_id=company_id,
                    is_enabled=1
                ).order_by('code')
                self.fields['tafsili_level'].empty_label = _("--- انتخاب کنید ---")
                self.fields['tafsili_level'].label_from_instance = lambda obj: f"{obj.code} · {obj.name}"
                self.fields['tafsili_level'].required = False
            
            # Filter sub accounts (level 2) - independent selection
            if 'sub_account' in self.fields:
                self.fields['sub_account'].queryset = Account.objects.filter(
                    company_id=company_id,
                    account_level=2,
                    is_enabled=1
                ).order_by('account_code')
                self.fields['sub_account'].required = False
                self.fields['sub_account'].empty_label = _("--- انتخاب کنید ---")
                self.fields['sub_account'].label_from_instance = lambda obj: f"{obj.account_code} · {obj.account_name}"
            
            if 'gl_account' in self.fields:
                self.fields['gl_account'].queryset = Account.objects.none()
                self.fields['gl_account'].required = False
                self.fields['gl_account'].empty_label = _("--- ابتدا معین را انتخاب کنید ---")
    
    def clean(self):
        """Validate account hierarchy."""
        cleaned_data = super().clean()
        tafsili_level = cleaned_data.get('tafsili_level')
        sub_account = cleaned_data.get('sub_account')
        gl_account = cleaned_data.get('gl_account')
        
        # Validate that either tafsili_level or sub_account is selected, but not both
        if not tafsili_level and not sub_account:
            raise forms.ValidationError(_('باید یا سطح تفصیلی انتخاب شود یا حساب معین (حداقل یکی از آن‌ها الزامی است).'))
        
        if tafsili_level and sub_account:
            raise forms.ValidationError(_('نمی‌توان هم سطح تفصیلی و هم حساب معین را انتخاب کرد. فقط یکی از آن‌ها باید انتخاب شود.'))
        
        if self.company_id:
            # Validate tafsili_level belongs to company
            if tafsili_level:
                if tafsili_level.company_id != self.company_id:
                    raise forms.ValidationError(_('سطح تفصیلی انتخاب شده باید متعلق به شرکت فعال باشد.'))
            
            # Validate sub_account belongs to company
            if sub_account:
                if sub_account.company_id != self.company_id:
                    raise forms.ValidationError(_('حساب معین انتخاب شده باید متعلق به شرکت فعال باشد.'))
                
                # If gl_account is selected, validate it's related to sub_account
                if gl_account:
                    from ..models.accounts import SubAccountGLAccountRelation
                    if not SubAccountGLAccountRelation.objects.filter(
                        company_id=self.company_id,
                        sub_account=sub_account,
                        gl_account=gl_account,
                    ).exists():
                        raise forms.ValidationError(_('حساب کل انتخاب شده برای این معین مجاز نیست.'))
        
        return cleaned_data


"""
Forms for Account (Chart of Accounts) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Account


class AccountForm(forms.ModelForm):
    """Form for creating/editing accounts."""
    
    class Meta:
        model = Account
        fields = [
            'account_code',
            'account_name',
            'account_name_en',
            'account_type',
            'account_level',
            'parent_account',
            'normal_balance',
            'opening_balance',
            'description',
            'is_enabled',
        ]
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'account_level': forms.Select(attrs={'class': 'form-control'}),
            'parent_account': forms.Select(attrs={'class': 'form-control'}),
            'normal_balance': forms.Select(attrs={'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_code': _('کد حساب'),
            'account_name': _('نام حساب'),
            'account_name_en': _('نام حساب (انگلیسی)'),
            'account_type': _('نوع حساب'),
            'account_level': _('سطح حساب'),
            'parent_account': _('حساب والد'),
            'normal_balance': _('طرف تراز'),
            'opening_balance': _('مانده ابتدای دوره'),
            'description': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, exclude_account_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Filter parent accounts by company
        if company_id:
            queryset = Account.objects.filter(
                company_id=company_id,
                is_enabled=1
            )
            # Exclude current account from parent choices (to prevent circular references)
            if exclude_account_id:
                queryset = queryset.exclude(pk=exclude_account_id)
            self.fields['parent_account'].queryset = queryset.order_by('account_code')
        
        # Make parent_account optional
        self.fields['parent_account'].required = False
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        normal_balance = cleaned_data.get('normal_balance')
        parent_account = cleaned_data.get('parent_account')
        account_level = cleaned_data.get('account_level')
        
        # Validate normal balance based on account type
        if account_type and normal_balance:
            if account_type in ['ASSET', 'EXPENSE']:
                if normal_balance != 'DEBIT':
                    raise forms.ValidationError(_('دارایی‌ها و هزینه‌ها باید طرف تراز بدهکار داشته باشند.'))
            elif account_type in ['LIABILITY', 'EQUITY', 'REVENUE']:
                if normal_balance != 'CREDIT':
                    raise forms.ValidationError(_('بدهی‌ها، حقوق صاحبان سهام و درآمد باید طرف تراز بستانکار داشته باشند.'))
        
        # Validate parent account
        if parent_account:
            if self.company_id and parent_account.company_id != self.company_id:
                raise forms.ValidationError(_('حساب والد باید متعلق به همان شرکت باشد.'))
            if account_level and parent_account.account_level >= account_level:
                raise forms.ValidationError(_('سطح حساب والد باید کمتر از سطح حساب فرزند باشد.'))
        
        return cleaned_data


"""
Forms for GL Account (حساب کل) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Account


class GLAccountForm(forms.ModelForm):
    """Form for creating/editing GL accounts (حساب کل)."""
    
    class Meta:
        model = Account
        fields = [
            'account_code',
            'account_name',
            'account_name_en',
            'opening_balance',
            'description',
            'is_enabled',
        ]
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20', 'placeholder': 'مثال: 1 یا 10'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: دارایی'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_code': _('کد کل'),
            'account_name': _('نام کل'),
            'account_name_en': _('نام کل (انگلیسی)'),
            'opening_balance': _('مانده ابتدای دوره'),
            'description': _('شرح'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Set account_level to 1 (کل) for GL accounts
        if not self.instance.pk:
            self.instance.account_level = 1
        
        # Remove account_level and parent_account from form (they're fixed for GL accounts)
        if 'account_level' in self.fields:
            del self.fields['account_level']
        if 'parent_account' in self.fields:
            del self.fields['parent_account']
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        account_code = cleaned_data.get('account_code')
        
        # Validate unique code within company
        if account_code and self.company_id:
            existing = Account.objects.filter(
                company_id=self.company_id,
                account_code=account_code,
                account_level=1
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError({
                    'account_code': _('کد کل باید یکتا باشد.')
                })
        
        return cleaned_data


"""
Forms for Sub Account (حساب معین) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Account, SubAccountGLAccountRelation


class SubAccountForm(forms.ModelForm):
    """Form for creating/editing Sub accounts (حساب معین)."""
    
    gl_accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        label=_('حساب‌های کل مرتبط'),
        help_text=_('می‌توانید یک یا چند حساب کل را انتخاب کنید'),
        required=True,
    )
    
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
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20', 'readonly': True, 'placeholder': 'کد به صورت خودکار تولید می‌شود'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_code': _('کد معین'),
            'account_name': _('نام معین'),
            'account_name_en': _('نام معین (انگلیسی)'),
            'opening_balance': _('مانده ابتدای دوره'),
            'description': _('شرح'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, exclude_account_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Set account_level to 2 (معین) for Sub accounts
        if not self.instance.pk:
            self.instance.account_level = 2
            # Auto-generate account_code for new sub accounts
            if not self.instance.account_code and company_id:
                from inventory.utils.codes import generate_sequential_code
                self.instance.account_code = generate_sequential_code(
                    Account,
                    company_id=company_id,
                    field='account_code',
                    width=10,
                    extra_filters={'account_level': 2},
                )
                # Set initial value for display
                self.initial['account_code'] = self.instance.account_code
        
        # Remove account_level and account_type from form
        if 'account_level' in self.fields:
            del self.fields['account_level']
        if 'account_type' in self.fields:
            del self.fields['account_type']
        if 'parent_account' in self.fields:
            del self.fields['parent_account']
        
        # Make account_code readonly for sub accounts
        if 'account_code' in self.fields:
            self.fields['account_code'].required = False
            self.fields['account_code'].widget.attrs['readonly'] = True
        
        # Filter GL accounts for multiple choice
        if company_id:
            gl_queryset = Account.objects.filter(
                company_id=company_id,
                account_level=1,
                is_enabled=1
            ).order_by('account_code')
            self.fields['gl_accounts'].queryset = gl_queryset
            
            # Load existing relations for edit
            if self.instance.pk:
                from accounting.models import SubAccountGLAccountRelation
                existing_gl_accounts = SubAccountGLAccountRelation.objects.filter(
                    sub_account=self.instance,
                    company_id=company_id
                ).values_list('gl_account_id', flat=True)
                self.initial['gl_accounts'] = list(existing_gl_accounts)
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        gl_accounts = cleaned_data.get('gl_accounts', [])
        
        # Auto-generate account_code if not set (for new instances)
        # Check both cleaned_data and instance.account_code
        account_code = cleaned_data.get('account_code') or getattr(self.instance, 'account_code', None)
        if not self.instance.pk and not account_code and self.company_id:
            from inventory.utils.codes import generate_sequential_code
            account_code = generate_sequential_code(
                Account,
                company_id=self.company_id,
                field='account_code',
                width=10,
                extra_filters={'account_level': 2},
            )
            cleaned_data['account_code'] = account_code
            self.instance.account_code = account_code
        
        # Validate GL accounts
        if not gl_accounts:
            raise forms.ValidationError({
                'gl_accounts': _('حداقل یک حساب کل باید انتخاب شود.')
            })
        
        # Check all GL accounts belong to same company
        if self.company_id:
            for gl_account in gl_accounts:
                if gl_account.company_id != self.company_id:
                    raise forms.ValidationError({
                        'gl_accounts': _('همه حساب‌های کل باید متعلق به همان شرکت باشند.')
                    })
                if gl_account.account_level != 1:
                    raise forms.ValidationError({
                        'gl_accounts': _('همه انتخاب‌ها باید حساب کل (سطح 1) باشند.')
                    })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save account and create relations."""
        instance = super().save(commit=commit)
        
        if commit and self.company_id:
            # Delete existing relations
            SubAccountGLAccountRelation.objects.filter(
                sub_account=instance,
                company_id=self.company_id
            ).delete()
            
            # Create new relations
            gl_accounts = self.cleaned_data.get('gl_accounts', [])
            for idx, gl_account in enumerate(gl_accounts):
                SubAccountGLAccountRelation.objects.create(
                    sub_account=instance,
                    gl_account=gl_account,
                    company=instance.company,
                    is_primary=1 if idx == 0 else 0,  # First one is primary
                    created_by=self.instance.created_by if hasattr(self.instance, 'created_by') else None,
                )
        
        return instance


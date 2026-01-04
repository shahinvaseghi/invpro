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
            'tafsili_account': _('فقط تفصیلی‌هایی که قابل استفاده در فروش هستند نمایش داده می‌شوند'),
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

            # Filter tafsili accounts that are usable in sales (connected to customers)
            if 'tafsili_account' in self.fields:
                from ..models.parties import PartyAccount
                # Get tafsili accounts that are connected to customers
                customer_tafsili_ids = PartyAccount.objects.filter(
                    company_id=company_id,
                    party__party_type='customer',
                    account__account_level=3
                ).values_list('account_id', flat=True).distinct()

                self.fields['tafsili_account'].queryset = Account.objects.filter(
                    company_id=company_id,
                    account_level=3,
                    is_enabled=1,
                    id__in=customer_tafsili_ids
                ).order_by('account_code')
                self.fields['tafsili_account'].empty_label = _("--- انتخاب کنید ---")
                self.fields['tafsili_account'].label_from_instance = lambda obj: f"{obj.account_code} · {obj.account_name}"
                self.fields['tafsili_account'].required = True
    
    def clean(self):
        """Validate treasury account."""
        cleaned_data = super().clean()
        tafsili_account = cleaned_data.get('tafsili_account')

        if self.company_id:
            # Validate tafsili_account belongs to company
            if tafsili_account:
                if tafsili_account.company_id != self.company_id:
                    raise forms.ValidationError(_('حساب تفصیلی انتخاب شده باید متعلق به شرکت فعال باشد.'))

                # Validate tafsili_account is usable in sales
                from ..models.parties import PartyAccount
                if not PartyAccount.objects.filter(
                    company_id=self.company_id,
                    account=tafsili_account,
                    party__party_type='customer'
                ).exists():
                    raise forms.ValidationError(_('حساب تفصیلی انتخاب شده باید قابل استفاده در فروش باشد.'))

        return cleaned_data


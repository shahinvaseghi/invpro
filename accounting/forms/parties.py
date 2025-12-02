"""
Forms for Party management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Party, PartyAccount


class PartyForm(forms.ModelForm):
    """Form for creating/editing parties."""
    
    class Meta:
        model = Party
        fields = [
            'party_type',
            'party_name',
            'party_name_en',
            'national_id',
            'tax_id',
            'address',
            'phone',
            'email',
            'contact_person',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'party_type': forms.Select(attrs={'class': 'form-control'}),
            'party_name': forms.TextInput(attrs={'class': 'form-control'}),
            'party_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'party_type': _('نوع طرف حساب'),
            'party_name': _('نام طرف حساب'),
            'party_name_en': _('نام طرف حساب (انگلیسی)'),
            'national_id': _('کد ملی / شماره ثبت'),
            'tax_id': _('شناسه مالیاتی'),
            'address': _('آدرس'),
            'phone': _('تلفن'),
            'email': _('ایمیل'),
            'contact_person': _('شخص رابط'),
            'notes': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if company_id:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass


class PartyAccountForm(forms.ModelForm):
    """Form for creating/editing party accounts."""
    
    class Meta:
        model = PartyAccount
        fields = [
            'party',
            'account',
            'is_primary',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'party': forms.Select(attrs={'class': 'form-control'}),
            'account': forms.Select(attrs={'class': 'form-control'}),
            'is_primary': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'party': _('طرف حساب'),
            'account': _('حساب تفصیلی'),
            'is_primary': _('حساب اصلی'),
            'notes': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
        help_texts = {
            'account': _('حساب تفصیلی مرتبط با این طرف حساب'),
            'is_primary': _('اگر این حساب اصلی طرف حساب است، انتخاب کنید'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        if company_id:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
            
            # Filter parties
            if 'party' in self.fields:
                self.fields['party'].queryset = Party.objects.filter(
                    company_id=company_id,
                    is_enabled=1
                ).order_by('party_name')
                self.fields['party'].empty_label = _("--- انتخاب کنید ---")
                self.fields['party'].label_from_instance = lambda obj: f"{obj.party_code} · {obj.party_name}"
            
            # Filter accounts (only level 3 - Tafsili)
            if 'account' in self.fields:
                from ..models import Account
                self.fields['account'].queryset = Account.objects.filter(
                    company_id=company_id,
                    account_level=3,
                    is_enabled=1
                ).order_by('account_code')
                self.fields['account'].empty_label = _("--- انتخاب کنید ---")
                self.fields['account'].label_from_instance = lambda obj: f"{obj.account_code} · {obj.account_name}"


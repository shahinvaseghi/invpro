"""
Forms for Tafsili Account (حساب تفصیلی) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Account, TafsiliType


class TafsiliAccountForm(forms.ModelForm):
    """Form for creating/editing Tafsili accounts (حساب تفصیلی)."""
    
    tafsili_type = forms.ModelChoiceField(
        queryset=TafsiliType.objects.none(),
        label=_('نوع تفصیلی'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        empty_label=_('-- انتخاب کنید --'),
    )
    is_customer = forms.BooleanField(
        label=_('مشتریان'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    is_supplier = forms.BooleanField(
        label=_('تأمین کنندگان'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    is_contractor = forms.BooleanField(
        label=_('پیمانکاران'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    is_connected_to_sales = forms.BooleanField(
        label=_('متصل به فروش'),
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
    
    class Meta:
        model = Account
        fields = [
            'account_code',
            'account_name',
            'account_name_en',
            'tafsili_type',
            'tafsili_level',
            'opening_balance',
            'description',
            'is_enabled',
        ]
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20', 'placeholder': 'مثال: 1101 یا 1102'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'tafsili_level': forms.Select(attrs={'class': 'form-control'}, choices=[(1, _('سطح 1')), (2, _('سطح 2')), (3, _('سطح 3'))]),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_code': _('کد تفصیلی'),
            'account_name': _('نام تفصیلی'),
            'account_name_en': _('نام تفصیلی (انگلیسی)'),
            'tafsili_level': _('سطح تفصیلی'),
            'opening_balance': _('مانده ابتدای دوره'),
            'description': _('شرح'),
            'is_enabled': _('وضعیت'),
        }
        help_texts = {
            'tafsili_level': _('سطح تفصیلی (1 تا 3)'),
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
        
        # User must enter account_code manually
        if 'account_code' in self.fields:
            self.fields['account_code'].required = True
        
        # Filter tafsili types by company
        if company_id:
            tafsili_type_queryset = TafsiliType.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).order_by('sort_order', 'public_code')
            self.fields['tafsili_type'].queryset = tafsili_type_queryset
            
            # Set initial value if editing
            if self.instance.pk and self.instance.tafsili_type:
                self.initial['tafsili_type'] = self.instance.tafsili_type
            
            # Set initial value for tafsili_level if editing
            if self.instance.pk and self.instance.tafsili_level:
                self.initial['tafsili_level'] = self.instance.tafsili_level
        
        # Load metadata fields
        if self.instance.pk and self.instance.metadata:
            self.initial['is_customer'] = self.instance.metadata.get('is_customer', False)
            self.initial['is_supplier'] = self.instance.metadata.get('is_supplier', False)
            self.initial['is_contractor'] = self.instance.metadata.get('is_contractor', False)
            self.initial['is_connected_to_sales'] = self.instance.metadata.get('is_connected_to_sales', False)
            if self.instance.metadata.get('national_id'):
                self.initial['national_id'] = self.instance.metadata.get('national_id')
            if self.instance.metadata.get('bank_account_number'):
                self.initial['bank_account_number'] = self.instance.metadata.get('bank_account_number')
            if self.instance.metadata.get('contact_info'):
                self.initial['contact_info'] = self.instance.metadata.get('contact_info')
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        tafsili_type = cleaned_data.get('tafsili_type')
        tafsili_level = cleaned_data.get('tafsili_level')
        account_code = cleaned_data.get('account_code')
        
        # Validate account_code is provided
        if not account_code:
            raise forms.ValidationError({
                'account_code': _('کد تفصیلی الزامی است.')
            })
        
        # Validate account_code is unique within company and account_level
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
                    'account_code': _('کد تفصیلی باید یکتا باشد.')
                })
        
        # Validate tafsili_type is provided
        if not tafsili_type:
            raise forms.ValidationError({
                'tafsili_type': _('نوع تفصیلی الزامی است.')
            })
        
        # Validate tafsili_level is provided and between 1-3
        if not tafsili_level:
            raise forms.ValidationError({
                'tafsili_level': _('سطح تفصیلی الزامی است.')
            })
        if tafsili_level not in [1, 2, 3]:
            raise forms.ValidationError({
                'tafsili_level': _('سطح تفصیلی باید بین 1 تا 3 باشد.')
            })
        
        # Check tafsili_type belongs to same company
        if self.company_id and tafsili_type:
            if tafsili_type.company_id != self.company_id:
                raise forms.ValidationError({
                    'tafsili_type': _('نوع تفصیلی باید متعلق به همان شرکت باشد.')
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save account."""
        # Set tafsili_type before saving
        tafsili_type = self.cleaned_data.get('tafsili_type')
        if tafsili_type:
            self.instance.tafsili_type = tafsili_type
        
        instance = super().save(commit=commit)
        
        # Save metadata fields
        if commit:
            if not instance.metadata:
                instance.metadata = {}
            
            instance.metadata['is_customer'] = self.cleaned_data.get('is_customer', False)
            instance.metadata['is_supplier'] = self.cleaned_data.get('is_supplier', False)
            instance.metadata['is_contractor'] = self.cleaned_data.get('is_contractor', False)
            instance.metadata['is_connected_to_sales'] = self.cleaned_data.get('is_connected_to_sales', False)
            if self.cleaned_data.get('national_id'):
                instance.metadata['national_id'] = self.cleaned_data.get('national_id')
            if self.cleaned_data.get('bank_account_number'):
                instance.metadata['bank_account_number'] = self.cleaned_data.get('bank_account_number')
            if self.cleaned_data.get('contact_info'):
                instance.metadata['contact_info'] = self.cleaned_data.get('contact_info')
            instance.save(update_fields=['metadata'])
        
        return instance

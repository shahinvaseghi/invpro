"""
Forms for Accounting Document management.
"""
from decimal import Decimal
from typing import Optional
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from ..models.documents import AccountingDocument, AccountingDocumentLine
from ..models.accounts import Account
from ..models.hierarchy import TafsiliHierarchy
from shared.forms.base import BaseModelForm


class AccountingDocumentForm(BaseModelForm):
    """Form for creating/editing Accounting Documents."""
    
    class Meta:
        model = AccountingDocument
        fields = [
            'document_date',
            'document_type',
            'fiscal_year',
            'period',
            'description',
            'reference_number',
            'reference_type',
            'status',
        ]
        widgets = {
            'document_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'fiscal_year': forms.Select(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_type': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'document_date': _('تاریخ سند'),
            'document_type': _('نوع سند'),
            'fiscal_year': _('سال مالی'),
            'period': _('دوره'),
            'description': _('شرح سند'),
            'reference_number': _('شماره مرجع'),
            'reference_type': _('نوع مرجع'),
            'status': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Auto-fill fields and make them readonly
        if company_id:
            from ..models.fiscal_years import FiscalYear
            from django.utils import timezone
            
            # Set document_date to today
            if not self.instance.pk:
                self.fields['document_date'].initial = timezone.now().date()
            
            # Auto-select fiscal year based on date
            if not self.instance.pk:
                document_date = self.fields['document_date'].initial or timezone.now().date()
                fiscal_year = FiscalYear.objects.filter(
                    company_id=company_id,
                    is_enabled=1,
                    start_date__lte=document_date,
                    end_date__gte=document_date
                ).first()
                if fiscal_year:
                    self.fields['fiscal_year'].initial = fiscal_year.pk
                    self.fields['fiscal_year'].queryset = FiscalYear.objects.filter(pk=fiscal_year.pk)
                else:
                    # Get active fiscal year
                    fiscal_year = FiscalYear.objects.filter(
                        company_id=company_id,
                        is_enabled=1
                    ).order_by('-start_date').first()
                    if fiscal_year:
                        self.fields['fiscal_year'].initial = fiscal_year.pk
                        self.fields['fiscal_year'].queryset = FiscalYear.objects.filter(pk=fiscal_year.pk)
            
            # Set defaults
            if not self.instance.pk:
                self.fields['status'].initial = 'DRAFT'
                self.fields['document_type'].initial = 'MANUAL'
            
            # Make fields hidden (values will be auto-filled in view)
            # Don't disable fields as disabled fields don't submit values
            # Instead, we'll set values in view's form_valid method
            for field_name in ['document_date', 'document_type', 'fiscal_year', 'period', 'status']:
                if field_name in self.fields:
                    self.fields[field_name].required = False
        
        if company_id and not self.instance.pk:
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass


class AccountingDocumentLineForm(forms.ModelForm):
    """Form for Accounting Document Line items - simplified version."""
    
    class Meta:
        model = AccountingDocumentLine
        fields = [
            'description',
            'gl_account',
            'sub_account',
            'tafsili_account',
            'debit',
            'credit',
            'sort_order',
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control line-description', 'placeholder': _('عنوان')}),
            'gl_account': forms.Select(attrs={'class': 'form-control line-gl-account', 'style': 'width: 100%;'}),
            'sub_account': forms.Select(attrs={'class': 'form-control line-sub-account', 'style': 'width: 100%;'}),
            'tafsili_account': forms.Select(attrs={'class': 'form-control line-tafsili-account', 'style': 'width: 100%;'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control line-debit', 'step': '0.01', 'placeholder': '0.00'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control line-credit', 'step': '0.01', 'placeholder': '0.00'}),
            'sort_order': forms.HiddenInput(),
        }
        labels = {
            'description': _('عنوان'),
            'gl_account': _('سند کل'),
            'sub_account': _('معین'),
            'tafsili_account': _('تفصیلی'),
            'debit': _('بدهکار'),
            'credit': _('بستانکار'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Make account fields optional
        self.fields['gl_account'].required = False
        self.fields['sub_account'].required = False
        self.fields['tafsili_account'].required = False
        
        # Set querysets for account fields based on company_id
        if company_id:
            # GL Accounts (level 1)
            gl_queryset = Account.objects.filter(
                company_id=company_id,
                account_level=1,
                is_enabled=1
            ).order_by('account_code')
            self.fields['gl_account'].queryset = gl_queryset
            
            # Sub Accounts (level 2) - initially empty, will be filtered by JS based on selected GL
            self.fields['sub_account'].queryset = Account.objects.filter(
                company_id=company_id,
                account_level=2,
                is_enabled=1
            ).order_by('account_code')
            
            # Tafsili Accounts (level 3) - initially empty, will be filtered by JS based on selected Sub
            self.fields['tafsili_account'].queryset = Account.objects.filter(
                company_id=company_id,
                account_level=3,
                is_enabled=1
            ).order_by('account_code')
        else:
            self.fields['gl_account'].queryset = Account.objects.none()
            self.fields['sub_account'].queryset = Account.objects.none()
            self.fields['tafsili_account'].queryset = Account.objects.none()
        
        # Set initial sort_order
        if not self.instance.pk:
            self.fields['sort_order'].initial = 0
    
    def clean(self):
        cleaned_data = super().clean()
        debit = cleaned_data.get('debit', Decimal('0.00'))
        credit = cleaned_data.get('credit', Decimal('0.00'))
        gl_account = cleaned_data.get('gl_account')
        sub_account = cleaned_data.get('sub_account')
        tafsili_account = cleaned_data.get('tafsili_account')
        
        # Validate that at least one account is set
        if not gl_account and not sub_account and not tafsili_account:
            raise forms.ValidationError(_('لطفاً حداقل یک حساب (سند کل، معین یا تفصیلی) را انتخاب کنید.'))
        
        # Validate account hierarchy
        if tafsili_account and not sub_account:
            raise forms.ValidationError(_('برای انتخاب حساب تفصیلی، ابتدا باید حساب معین را انتخاب کنید.'))
        
        if sub_account and not gl_account:
            raise forms.ValidationError(_('برای انتخاب حساب معین، ابتدا باید حساب کل را انتخاب کنید.'))
        
        # Validate debit/credit
        if debit > Decimal('0.00') and credit > Decimal('0.00'):
            raise forms.ValidationError(_('هر ردیف باید یا بدهکار باشد یا بستانکار، نه هر دو.'))
        
        if debit == Decimal('0.00') and credit == Decimal('0.00'):
            raise forms.ValidationError(_('هر ردیف باید حداقل یک مبلغ بدهکار یا بستانکار داشته باشد.'))
        
        return cleaned_data


# Create inline formset
AccountingDocumentLineFormSet = inlineformset_factory(
    AccountingDocument,
    AccountingDocumentLine,
    form=AccountingDocumentLineForm,
    extra=2,  # Default 2 empty rows
    can_delete=True,
    min_num=1,
    validate_min=True,
)


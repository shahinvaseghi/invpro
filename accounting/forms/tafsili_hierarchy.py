"""
Forms for Tafsili Level (سطح تفصیلی) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import TafsiliHierarchy, Account, TafsiliLevelSubAccountRelation


class TafsiliHierarchyForm(forms.ModelForm):
    """Form for creating/editing Tafsili Level (سطح تفصیلی)."""
    
    sub_accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        label=_('حساب‌های معین مرتبط'),
        help_text=_('می‌توانید یک یا چند حساب معین را انتخاب کنید'),
        required=True,
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
    
    class Meta:
        model = TafsiliHierarchy
        fields = [
            'code',
            'name',
            'name_en',
            'sort_order',
            'description',
            'is_enabled',
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'code': _('کد سطح تفصیلی'),
            'name': _('نام سطح تفصیلی'),
            'name_en': _('نام سطح تفصیلی (انگلیسی)'),
            'sort_order': _('ترتیب نمایش'),
            'description': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, exclude_hierarchy_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Filter sub accounts by company
        if company_id:
            sub_account_queryset = Account.objects.filter(
                company_id=company_id,
                account_level=2,
                is_enabled=1
            ).order_by('account_code')
            self.fields['sub_accounts'].queryset = sub_account_queryset
            
            # Load existing relations for edit
            if self.instance.pk:
                existing_sub_accounts = TafsiliLevelSubAccountRelation.objects.filter(
                    tafsili_level=self.instance,
                    company_id=company_id
                ).values_list('sub_account_id', flat=True)
                self.initial['sub_accounts'] = list(existing_sub_accounts)
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        sub_accounts = cleaned_data.get('sub_accounts', [])
        
        # Validate unique code within company
        if code and self.company_id:
            existing = TafsiliHierarchy.objects.filter(
                company_id=self.company_id,
                code=code
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError({
                    'code': _('کد سطح تفصیلی باید یکتا باشد.')
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
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save tafsili level and create relations."""
        instance = super().save(commit=commit)
        
        if commit and self.company_id:
            # Delete existing relations
            TafsiliLevelSubAccountRelation.objects.filter(
                tafsili_level=instance,
                company_id=self.company_id
            ).delete()
            
            # Create new relations
            sub_accounts = self.cleaned_data.get('sub_accounts', [])
            for idx, sub_account in enumerate(sub_accounts):
                TafsiliLevelSubAccountRelation.objects.create(
                    tafsili_level=instance,
                    sub_account=sub_account,
                    company=instance.company,
                    is_primary=1 if idx == 0 else 0,  # First one is primary
                    created_by=self.instance.created_by if hasattr(self.instance, 'created_by') else None,
                )
        
        return instance


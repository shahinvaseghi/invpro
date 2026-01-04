"""
Forms for Sub Account (حساب معین) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Account, SubAccountGLAccountRelation, SubAccountTafsiliTypeRelation, TafsiliType


class SubAccountForm(forms.ModelForm):
    """Form for creating/editing Sub accounts (حساب معین)."""
    
    gl_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('حساب کل'),
        help_text=_('حساب کل مرتبط با این حساب معین'),
        required=True,
        empty_label=_('-- انتخاب کنید --'),
    )
    
    tafsili_types_level_1 = forms.ModelMultipleChoiceField(
        queryset=TafsiliType.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        label=_('انواع تفصیلی قابل استفاده در سطح 1'),
        help_text=_('انواع تفصیلی که می‌توانند در سطح 1 برای این معین استفاده شوند'),
        required=False,
    )
    tafsili_types_level_2 = forms.ModelMultipleChoiceField(
        queryset=TafsiliType.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        label=_('انواع تفصیلی قابل استفاده در سطح 2'),
        help_text=_('انواع تفصیلی که می‌توانند در سطح 2 برای این معین استفاده شوند'),
        required=False,
    )
    tafsili_types_level_3 = forms.ModelMultipleChoiceField(
        queryset=TafsiliType.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        label=_('انواع تفصیلی قابل استفاده در سطح 3'),
        help_text=_('انواع تفصیلی که می‌توانند در سطح 3 برای این معین استفاده شوند'),
        required=False,
    )
    
    class Meta:
        model = Account
        fields = [
            'account_code',
            'account_name',
            'account_name_en',
            'opening_balance',
            'description',
            'is_tafsili_enabled',
            'is_enabled',
        ]
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20', 'placeholder': 'مثال: 11 یا 12'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_tafsili_enabled': forms.Select(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_code': _('کد معین'),
            'account_name': _('نام معین'),
            'account_name_en': _('نام معین (انگلیسی)'),
            'opening_balance': _('مانده ابتدای دوره'),
            'description': _('شرح'),
            'is_tafsili_enabled': _('تفصیل پذیر'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, exclude_account_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Set account_level to 2 (معین) for Sub accounts
        if not self.instance.pk:
            self.instance.account_level = 2
        
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
        
        # Filter GL accounts for single choice
        if company_id:
            gl_queryset = Account.objects.filter(
                company_id=company_id,
                account_level=1,
                is_enabled=1
            ).order_by('account_code')
            self.fields['gl_account'].queryset = gl_queryset
            
            # Load existing relation for edit (get primary or first one)
            if self.instance.pk:
                existing_relation = SubAccountGLAccountRelation.objects.filter(
                    sub_account=self.instance,
                    company_id=company_id
                ).order_by('-is_primary', 'gl_account__account_code').first()
                if existing_relation:
                    self.initial['gl_account'] = existing_relation.gl_account_id
                
                # Load existing tafsili type relations for each level
                for level in [1, 2, 3]:
                    existing_types = SubAccountTafsiliTypeRelation.objects.filter(
                        sub_account=self.instance,
                        company_id=company_id,
                        level=level
                    ).values_list('tafsili_type_id', flat=True)
                    self.initial[f'tafsili_types_level_{level}'] = list(existing_types)
        
        # Filter tafsili types by company
        if company_id:
            tafsili_type_queryset = TafsiliType.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).order_by('sort_order', 'public_code')
            self.fields['tafsili_types_level_1'].queryset = tafsili_type_queryset
            self.fields['tafsili_types_level_2'].queryset = tafsili_type_queryset
            self.fields['tafsili_types_level_3'].queryset = tafsili_type_queryset
                
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        gl_account = cleaned_data.get('gl_account')
        account_code = cleaned_data.get('account_code')
        
        # Validate account_code is provided
        if not account_code:
            raise forms.ValidationError({
                'account_code': _('کد معین الزامی است.')
            })
        
        # Validate account_code is unique within company and account_level
        if account_code and self.company_id:
            existing = Account.objects.filter(
                company_id=self.company_id,
                account_code=account_code,
                account_level=2
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError({
                    'account_code': _('کد معین باید یکتا باشد.')
                })
        
        # Validate GL account is provided
        if not gl_account:
            raise forms.ValidationError({
                'gl_account': _('حساب کل الزامی است.')
            })
        
        # Check GL account belongs to same company and is level 1
        if self.company_id and gl_account:
            if gl_account.company_id != self.company_id:
                raise forms.ValidationError({
                    'gl_account': _('حساب کل باید متعلق به همان شرکت باشد.')
                })
            if gl_account.account_level != 1:
                raise forms.ValidationError({
                    'gl_account': _('انتخاب باید حساب کل (سطح 1) باشد.')
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save account and create relations."""
        instance = super().save(commit=commit)
        
        if commit and self.company_id:
            # Delete existing GL account relations
            SubAccountGLAccountRelation.objects.filter(
                sub_account=instance,
                company_id=self.company_id
            ).delete()
            
            # Create single GL account relation
            gl_account = self.cleaned_data.get('gl_account')
            if gl_account:
                SubAccountGLAccountRelation.objects.create(
                    sub_account=instance,
                    gl_account=gl_account,
                    company=instance.company,
                    is_primary=1,  # Only one relation, so it's primary
                    created_by=self.instance.created_by if hasattr(self.instance, 'created_by') else None,
                )
            
            # Delete existing tafsili type relations
            SubAccountTafsiliTypeRelation.objects.filter(
                sub_account=instance,
                company_id=self.company_id
            ).delete()
            
            # Create new tafsili type relations for each level
            for level in [1, 2, 3]:
                tafsili_types = self.cleaned_data.get(f'tafsili_types_level_{level}', [])
                for tafsili_type in tafsili_types:
                    SubAccountTafsiliTypeRelation.objects.create(
                        sub_account=instance,
                        tafsili_type=tafsili_type,
                        level=level,
                        company=instance.company,
                        created_by=self.instance.created_by if hasattr(self.instance, 'created_by') else None,
                    )
            
        return instance


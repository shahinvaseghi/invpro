"""
Forms for Tafsili Account (حساب تفصیلی) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Account, TafsiliSubAccountRelation, TafsiliType, TafsiliHierarchy, TafsiliLevelSubAccountRelation


class TafsiliAccountForm(forms.ModelForm):
    """Form for creating/editing Tafsili accounts (حساب تفصیلی)."""
    
    tafsili_type = forms.ModelChoiceField(
        queryset=TafsiliType.objects.none(),
        label=_('نوع تفصیلی'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        empty_label=_('-- انتخاب کنید --'),
    )
    is_floating = forms.BooleanField(
        label=_('تفصیلی شناور'),
        help_text=_('اگر فعال باشد، می‌تواند به چند معین ارتباط داده شود'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
    
    tafsili_level = forms.ModelChoiceField(
        queryset=TafsiliHierarchy.objects.none(),
        label=_('سطح تفصیلی'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_tafsili_level'}),
        required=False,
        empty_label=_('-- انتخاب کنید --'),
        help_text=_('اگر سطح تفصیلی انتخاب شود، حساب‌های معین مرتبط به صورت خودکار انتخاب می‌شوند'),
    )
    
    sub_accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5', 'id': 'id_sub_accounts'}),
        label=_('حساب‌های معین مرتبط'),
        help_text=_('می‌توانید یک یا چند حساب معین را انتخاب کنید (در صورت انتخاب سطح تفصیلی، این فیلد غیرفعال می‌شود)'),
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
            'is_enabled',
        ]
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20', 'placeholder': 'مثال: 1101 یا 1102'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_code': _('کد تفصیلی'),
            'account_name': _('نام تفصیلی'),
            'account_name_en': _('نام تفصیلی (انگلیسی)'),
            'opening_balance': _('مانده ابتدای دوره'),
            'description': _('شرح'),
            'is_enabled': _('وضعیت'),
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
        
        # Filter tafsili levels by company
        if company_id:
            tafsili_level_queryset = TafsiliHierarchy.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).order_by('sort_order', 'code')
            self.fields['tafsili_level'].queryset = tafsili_level_queryset
            
            # Load existing tafsili level for edit - check if all sub_accounts belong to same level
            if self.instance.pk:
                existing_sub_accounts = TafsiliSubAccountRelation.objects.filter(
                    tafsili_account=self.instance,
                    company_id=company_id
                ).select_related('sub_account')
                
                if existing_sub_accounts.exists():
                    # Check if all sub accounts belong to the same tafsili level
                    sub_account_ids = [rel.sub_account_id for rel in existing_sub_accounts]
                    level_relations = TafsiliLevelSubAccountRelation.objects.filter(
                        sub_account_id__in=sub_account_ids,
                        company_id=company_id
                    ).select_related('tafsili_level')
                    
                    if level_relations.exists():
                        # Get unique tafsili levels
                        tafsili_levels = set(rel.tafsili_level_id for rel in level_relations)
                        # If all sub accounts belong to the same level
                        if len(tafsili_levels) == 1:
                            tafsili_level_id = tafsili_levels.pop()
                            self.initial['tafsili_level'] = tafsili_level_id
                            # Disable sub_accounts field if tafsili_level is set
                            self.fields['sub_accounts'].widget.attrs['disabled'] = True
        
        # Filter sub accounts for multiple choice
        if company_id:
            sub_queryset = Account.objects.filter(
                company_id=company_id,
                account_level=2,
                is_enabled=1
            ).order_by('account_code')
            self.fields['sub_accounts'].queryset = sub_queryset
            
            # Load existing relations for edit (only if tafsili_level is not set)
            if self.instance.pk and not self.initial.get('tafsili_level'):
                existing_sub_accounts = TafsiliSubAccountRelation.objects.filter(
                    tafsili_account=self.instance,
                    company_id=company_id
                ).values_list('sub_account_id', flat=True)
                self.initial['sub_accounts'] = list(existing_sub_accounts)
                
                # Load is_floating from existing relations
                if existing_sub_accounts.count() > 1:
                    self.initial['is_floating'] = True
        
        # Load additional fields from description if editing
        if self.instance.pk and self.instance.description:
            # Try to parse additional info from description (simple approach)
            # In production, you might want to use a JSON field or separate model
            pass
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        tafsili_level = cleaned_data.get('tafsili_level')
        sub_accounts = cleaned_data.get('sub_accounts', [])
        is_floating = cleaned_data.get('is_floating', False)
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
        
        # If tafsili_level is selected, ignore sub_accounts (they will be loaded from level)
        if tafsili_level:
            # Clear sub_accounts since they will come from tafsili_level
            cleaned_data['sub_accounts'] = []
        else:
            # Validate sub accounts only if tafsili_level is not selected
            if not sub_accounts:
                raise forms.ValidationError({
                    'sub_accounts': _('حداقل یک حساب معین باید انتخاب شود (یا سطح تفصیلی را انتخاب کنید).')
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
        """Save account and create relations."""
        # Set tafsili_type before saving
        tafsili_type = self.cleaned_data.get('tafsili_type')
        if tafsili_type:
            self.instance.tafsili_type = tafsili_type
        
        instance = super().save(commit=commit)
        
        if commit and self.company_id:
            # Delete existing relations
            TafsiliSubAccountRelation.objects.filter(
                tafsili_account=instance,
                company_id=self.company_id
            ).delete()
            
            # Get sub accounts - either from tafsili_level or from direct selection
            tafsili_level = self.cleaned_data.get('tafsili_level')
            if tafsili_level:
                # Get sub accounts from tafsili level
                level_relations = TafsiliLevelSubAccountRelation.objects.filter(
                    tafsili_level=tafsili_level,
                    company_id=self.company_id
                ).select_related('sub_account').order_by('-is_primary', 'sub_account__account_code')
                sub_accounts = [rel.sub_account for rel in level_relations]
            else:
                # Use directly selected sub accounts
                sub_accounts = self.cleaned_data.get('sub_accounts', [])
            
            # Create new relations
            for idx, sub_account in enumerate(sub_accounts):
                TafsiliSubAccountRelation.objects.create(
                    tafsili_account=instance,
                    sub_account=sub_account,
                    company=instance.company,
                    is_primary=1 if idx == 0 else 0,  # First one is primary
                    created_by=self.instance.created_by if hasattr(self.instance, 'created_by') else None,
                )
        
        return instance


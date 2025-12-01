"""
Forms for Tafsili Hierarchy (تفصیلی چند سطحی) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import TafsiliHierarchy, Account


class TafsiliHierarchyForm(forms.ModelForm):
    """Form for creating/editing Tafsili Hierarchy (تفصیلی چند سطحی)."""
    
    class Meta:
        model = TafsiliHierarchy
        fields = [
            'code',
            'name',
            'name_en',
            'parent',
            'tafsili_account',
            'sort_order',
            'description',
            'is_enabled',
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'tafsili_account': forms.Select(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'code': _('کد تفصیلی چند سطحی'),
            'name': _('نام تفصیلی چند سطحی'),
            'name_en': _('نام تفصیلی چند سطحی (انگلیسی)'),
            'parent': _('تفصیلی چند سطحی والد'),
            'tafsili_account': _('تفصیلی اصلی مرتبط'),
            'sort_order': _('ترتیب نمایش'),
            'description': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, exclude_hierarchy_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Filter parent hierarchies by company
        if company_id:
            parent_queryset = TafsiliHierarchy.objects.filter(
                company_id=company_id,
                is_enabled=1
            )
            # Exclude current instance from parent choices
            if exclude_hierarchy_id:
                parent_queryset = parent_queryset.exclude(pk=exclude_hierarchy_id)
            self.fields['parent'].queryset = parent_queryset.order_by('level', 'sort_order', 'code')
        
        # Filter tafsili accounts by company
        if company_id:
            tafsili_queryset = Account.objects.filter(
                company_id=company_id,
                account_level=3,
                is_enabled=1
            ).order_by('account_code')
            self.fields['tafsili_account'].queryset = tafsili_queryset
        
        # Make parent and tafsili_account optional
        self.fields['parent'].required = False
        self.fields['tafsili_account'].required = False
        
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
        parent = cleaned_data.get('parent')
        
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
                    'code': _('کد تفصیلی چند سطحی باید یکتا باشد.')
                })
        
        return cleaned_data


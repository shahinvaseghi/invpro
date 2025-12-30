"""
Forms for Tafsili Type (نوع تفصیلی) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import TafsiliType
from inventory.utils.codes import generate_sequential_code


class TafsiliTypeForm(forms.ModelForm):
    """Form for creating/editing Tafsili Types (نوع تفصیلی)."""
    
    class Meta:
        model = TafsiliType
        fields = [
            'public_code',
            'name',
            'name_en',
            'description',
            'sort_order',
            'is_enabled',
        ]
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'public_code': _('کد'),
            'name': _('نام (فارسی)'),
            'name_en': _('نام (انگلیسی)'),
            'description': _('توضیحات'),
            'sort_order': _('ترتیب نمایش'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Auto-generate public_code if not provided
        if not self.instance.pk and not self.initial.get('public_code'):
            if company_id:
                try:
                    last_type = TafsiliType.objects.filter(
                        company_id=company_id
                    ).order_by('-public_code').first()
                    if last_type and last_type.public_code.isdigit():
                        next_code = str(int(last_type.public_code) + 1).zfill(10)
                    else:
                        next_code = '1'.zfill(10)
                    self.initial['public_code'] = next_code
                except Exception:
                    self.initial['public_code'] = '1'.zfill(10)
        
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        public_code = cleaned_data.get('public_code')
        
        # Validate public_code uniqueness within company
        if public_code and self.company_id:
            queryset = TafsiliType.objects.filter(
                company_id=self.company_id,
                public_code=public_code
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError({
                    'public_code': _('کد باید در این شرکت یکتا باشد.')
                })
        
        return cleaned_data


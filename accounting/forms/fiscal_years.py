"""
Forms for Fiscal Year management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import FiscalYear


class FiscalYearForm(forms.ModelForm):
    """Form for creating/editing fiscal years."""
    
    class Meta:
        model = FiscalYear
        fields = [
            'fiscal_year_code',
            'fiscal_year_name',
            'start_date',
            'end_date',
            'is_current',
            'is_enabled',
        ]
        widgets = {
            'fiscal_year_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'fiscal_year_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.Select(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'fiscal_year_code': _('Fiscal Year Code'),
            'fiscal_year_name': _('Fiscal Year Name'),
            'start_date': _('Start Date'),
            'end_date': _('End Date'),
            'is_current': _('Current Year'),
            'is_enabled': _('Status'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        if company_id and not self.instance.pk:
            # Set company for new instances
            from shared.models import Company
            try:
                self.instance.company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(_('End date must be after start date.'))
        
        return cleaned_data


"""
Forms for Period management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Period, FiscalYear


class PeriodForm(forms.ModelForm):
    """Form for creating/editing accounting periods."""
    
    class Meta:
        model = Period
        fields = [
            'fiscal_year',
            'period_code',
            'period_name',
            'start_date',
            'end_date',
            'is_enabled',
        ]
        widgets = {
            'fiscal_year': forms.Select(attrs={'class': 'form-control'}),
            'period_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'period_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'fiscal_year': _('Fiscal Year'),
            'period_code': _('Period Code'),
            'period_name': _('Period Name'),
            'start_date': _('Start Date'),
            'end_date': _('End Date'),
            'is_enabled': _('Status'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Filter fiscal years by company
        if company_id:
            self.fields['fiscal_year'].queryset = FiscalYear.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).order_by('-fiscal_year_code')
        
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
        fiscal_year = cleaned_data.get('fiscal_year')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(_('End date must be after start date.'))
        
        if fiscal_year and start_date and end_date:
            if start_date < fiscal_year.start_date:
                raise forms.ValidationError(_('Period start date must be within fiscal year.'))
            if end_date > fiscal_year.end_date:
                raise forms.ValidationError(_('Period end date must be within fiscal year.'))
        
        return cleaned_data


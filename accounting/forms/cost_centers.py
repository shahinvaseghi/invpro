"""
Forms for Cost Center management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import CostCenter
from shared.models import CompanyUnit
from shared.utils.modules import get_work_line_model


class CostCenterForm(forms.ModelForm):
    """Form for creating/editing cost centers."""
    
    class Meta:
        model = CostCenter
        fields = [
            'cost_center_name',
            'cost_center_name_en',
            'company_unit',
            'work_line',
            'description',
            'is_enabled',
        ]
        widgets = {
            'cost_center_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cost_center_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'company_unit': forms.Select(attrs={'class': 'form-control'}),
            'work_line': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'cost_center_name': _('نام مرکز هزینه'),
            'cost_center_name_en': _('نام مرکز هزینه (انگلیسی)'),
            'company_unit': _('واحد کاری'),
            'work_line': _('خط کاری'),
            'description': _('توضیحات'),
            'is_enabled': _('وضعیت'),
        }
        help_texts = {
            'work_line': _('خط کاری تولید (اختیاری - فقط در صورت نصب ماژول تولید)'),
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
            
            # Filter company units
            if 'company_unit' in self.fields:
                self.fields['company_unit'].queryset = CompanyUnit.objects.filter(
                    company_id=company_id,
                    is_enabled=1
                ).order_by('name')
                self.fields['company_unit'].empty_label = _("--- انتخاب کنید ---")
                self.fields['company_unit'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
            
            # Filter work lines if production module is installed
            WorkLine = get_work_line_model()
            if 'work_line' in self.fields:
                if WorkLine:
                    self.fields['work_line'].queryset = WorkLine.objects.filter(
                        company_id=company_id,
                        is_enabled=1
                    ).order_by('name')
                    self.fields['work_line'].empty_label = _("--- انتخاب کنید (اختیاری) ---")
                    self.fields['work_line'].label_from_instance = lambda obj: f"{obj.public_code} · {obj.name}"
                else:
                    # Hide work_line field if production module is not installed
                    self.fields['work_line'].widget = forms.HiddenInput()
                    self.fields['work_line'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        company_unit = cleaned_data.get('company_unit')
        
        if company_unit and self.company_id:
            # Validate company unit belongs to the company
            if company_unit.company_id != self.company_id:
                raise forms.ValidationError(_('واحد کاری انتخاب شده باید متعلق به شرکت فعال باشد.'))
        
        work_line = cleaned_data.get('work_line')
        if work_line and self.company_id:
            # Validate work line belongs to the company
            if work_line.company_id != self.company_id:
                raise forms.ValidationError(_('خط کاری انتخاب شده باید متعلق به شرکت فعال باشد.'))
        
        return cleaned_data


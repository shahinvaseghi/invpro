"""
Personnel forms for production module.
"""
from typing import Optional
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shared.models import CompanyUnit
from production.models import Person


class PersonForm(forms.ModelForm):
    """Form for creating/editing personnel."""
    
    use_personnel_code_as_username = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Use Personnel Code as Username'),
        help_text=_('If checked, username will be same as personnel code'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'use_personnel_code'})
    )
    
    class Meta:
        model = Person
        fields = [
            'first_name',
            'last_name',
            'first_name_en',
            'last_name_en',
            'national_id',
            'personnel_code',
            'username',
            'phone_number',
            'mobile_number',
            'email',
            'description',
            'notes',
            'is_enabled',
            'company_units',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'personnel_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'personnel_code_field'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'username_field'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
            'company_units': forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),
        }
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'first_name_en': _('First Name (English)'),
            'last_name_en': _('Last Name (English)'),
            'national_id': _('National ID'),
            'personnel_code': _('Personnel Code'),
            'username': _('Username'),
            'phone_number': _('Phone'),
            'mobile_number': _('Mobile'),
            'email': _('Email'),
            'description': _('Description'),
            'notes': _('Notes'),
            'is_enabled': _('Status'),
            'company_units': _('Company Units'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        if self.company_id:
            self.fields['company_units'].queryset = CompanyUnit.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['company_units'].help_text = _('Select one or more organizational units.')
        else:
            self.fields['company_units'].queryset = CompanyUnit.objects.none()
            self.fields['company_units'].help_text = _('Please select a company first.')

        self.fields['company_units'].required = False

        # If editing and username equals personnel_code, check the box
        if self.instance.pk and self.instance.username == self.instance.personnel_code:
            self.fields['use_personnel_code_as_username'].initial = True
    
    def clean(self) -> dict:
        """Validate form data."""
        cleaned_data = super().clean()
        use_personnel_code = cleaned_data.get('use_personnel_code_as_username')
        personnel_code = cleaned_data.get('personnel_code')
        username = cleaned_data.get('username')
        
        # If checkbox is checked, use personnel_code as username
        if use_personnel_code:
            if not personnel_code:
                raise forms.ValidationError(_('Personnel Code is required when using it as username.'))
            cleaned_data['username'] = personnel_code
        else:
            if not username:
                raise forms.ValidationError(_('Username is required when not using personnel code.'))
        
        # Ensure selected units belong to the same company
        if self.company_id:
            units = cleaned_data.get('company_units')
            if units and units.filter(~Q(company_id=self.company_id)).exists():
                raise forms.ValidationError(_('Selected units must belong to the active company.'))
        
        return cleaned_data


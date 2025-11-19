"""
Forms for production module.
"""
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shared.models import CompanyUnit
from .models import Machine, Person


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
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

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
    
    def clean(self):
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


class MachineForm(forms.ModelForm):
    """Form for creating/editing machines."""
    
    class Meta:
        model = Machine
        fields = [
            'name',
            'name_en',
            'machine_type',
            'work_center',
            'manufacturer',
            'model_number',
            'serial_number',
            'purchase_date',
            'installation_date',
            'capacity_specs',
            'maintenance_schedule',
            'last_maintenance_date',
            'next_maintenance_date',
            'status',
            'description',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'machine_type': forms.TextInput(attrs={'class': 'form-control'}),
            'work_center': forms.Select(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'capacity_specs': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'maintenance_schedule': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'last_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name'),
            'name_en': _('Name (English)'),
            'machine_type': _('Machine Type'),
            'work_center': _('Work Center'),
            'manufacturer': _('Manufacturer'),
            'model_number': _('Model Number'),
            'serial_number': _('Serial Number'),
            'purchase_date': _('Purchase Date'),
            'installation_date': _('Installation Date'),
            'capacity_specs': _('Capacity Specifications'),
            'maintenance_schedule': _('Maintenance Schedule'),
            'last_maintenance_date': _('Last Maintenance Date'),
            'next_maintenance_date': _('Next Maintenance Date'),
            'status': _('Status'),
            'description': _('Description'),
            'notes': _('Notes'),
            'is_enabled': _('Status'),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        if self.company_id:
            from .models import WorkCenter
            self.fields['work_center'].queryset = WorkCenter.objects.filter(company_id=self.company_id, is_enabled=1)
        else:
            from .models import WorkCenter
            self.fields['work_center'].queryset = WorkCenter.objects.none()


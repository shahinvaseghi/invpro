"""
Machine forms for production module.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _

from production.models import Machine


class MachineForm(forms.ModelForm):
    """Form for creating/editing machines."""
    
    work_lines = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label=_('Work Lines'),
        help_text=_('Select work lines for this machine'),
    )
    
    class Meta:
        model = Machine
        fields = [
            'name',
            'name_en',
            'machine_type',
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
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id: Optional[int] = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        if self.company_id:
            from production.models import WorkLine
            # Set work_lines queryset
            self.fields['work_lines'].queryset = WorkLine.objects.filter(company_id=self.company_id, is_enabled=1)
        else:
            from production.models import WorkLine
            self.fields['work_lines'].queryset = WorkLine.objects.none()
        
        # If editing, set initial work_lines
        if self.instance and self.instance.pk:
            self.fields['work_lines'].initial = self.instance.work_lines.all()
    
    def save(self, commit=True):
        """Save machine and update work lines."""
        instance = super().save(commit=commit)
        
        if commit:
            # Get selected work lines from form
            work_lines = self.cleaned_data.get('work_lines')
            
            # Update work_lines relationship
            # Remove this machine from all work lines first
            from production.models import WorkLine
            WorkLine.objects.filter(machines=instance).update()
            for wl in WorkLine.objects.filter(machines=instance):
                wl.machines.remove(instance)
            
            # Add this machine to selected work lines
            if work_lines:
                for work_line in work_lines:
                    work_line.machines.add(instance)
        
        return instance


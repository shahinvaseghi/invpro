"""
Company and CompanyUnit forms for shared module.
"""
from typing import Optional

from django import forms
from django.utils.translation import gettext_lazy as _

from shared.models import Company, CompanyUnit
from shared.forms.base import BaseModelForm


class CompanyForm(BaseModelForm):
    """Form for creating/editing companies."""
    
    def __init__(self, *args, **kwargs):
        """Initialize form and remove company_id if not needed."""
        # Company model doesn't need company_id (it IS the company)
        kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Company
        fields = [
            'public_code',
            'legal_name',
            'display_name',
            'display_name_en',
            'registration_number',
            'tax_id',
            'phone_number',
            'email',
            'website',
            'address',
            'city',
            'state',
            'country',
            'is_enabled',
        ]
        widgets = {
            # BaseModelForm automatically applies 'form-control' class, but we can add extra attributes
            'public_code': forms.TextInput(attrs={'maxlength': '3'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'country': forms.TextInput(attrs={'maxlength': '3'}),
        }
        labels = {
            'public_code': _('Code'),
            'legal_name': _('Legal Name'),
            'display_name': _('Display Name'),
            'display_name_en': _('Display Name (English)'),
            'registration_number': _('Registration Number'),
            'tax_id': _('Tax ID'),
            'phone_number': _('Phone'),
            'email': _('Email'),
            'website': _('Website'),
            'address': _('Address'),
            'city': _('City'),
            'state': _('State/Province'),
            'country': _('Country'),
            'is_enabled': _('Status'),
        }


class CompanyUnitForm(BaseModelForm):
    """Form for creating/editing company units (organizational units)."""

    parent_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Parent Unit'),
        # BaseModelForm automatically applies 'form-control' class
    )

    class Meta:
        model = CompanyUnit
        fields = [
            'public_code',
            'name',
            'name_en',
            'parent_unit',
            'description',
            'notes',
            'is_enabled',
        ]
        widgets = {
            # BaseModelForm automatically applies 'form-control' class, but we can add extra attributes
            'public_code': forms.TextInput(attrs={'maxlength': '5'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'public_code': _('Code'),
            'name': _('Unit Name'),
            'name_en': _('Unit Name (English)'),
            'parent_unit': _('Parent Unit'),
            'description': _('Description'),
            'notes': _('Notes'),
            'is_enabled': _('Status'),
        }

    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        queryset = CompanyUnit.objects.none()
        if self.company_id:
            queryset = CompanyUnit.objects.filter(company_id=self.company_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

        self.fields['parent_unit'].queryset = queryset
        self.fields['is_enabled'].choices = (
            (1, _('Active')),
            (0, _('Inactive')),
        )

    def clean_parent_unit(self) -> Optional[CompanyUnit]:
        """Validate parent unit belongs to same company."""
        parent = self.cleaned_data.get('parent_unit')
        if parent and self.company_id and parent.company_id != self.company_id:
            raise forms.ValidationError(_('Parent unit must belong to the same company.'))
        return parent


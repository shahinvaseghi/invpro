"""
Company and CompanyUnit forms for shared module.
"""
from typing import Optional

from django import forms
from django.utils.translation import gettext_lazy as _

from shared.models import Company, CompanyUnit


class CompanyForm(forms.ModelForm):
    """Form for creating/editing companies."""
    
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
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'legal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
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


class CompanyUnitForm(forms.ModelForm):
    """Form for creating/editing company units (organizational units)."""

    parent_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Parent Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
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
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '5'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'public_code': 'کد',
            'name': 'نام واحد',
            'name_en': 'نام واحد (انگلیسی)',
            'parent_unit': 'واحد بالادست',
            'description': 'توضیح',
            'notes': 'یادداشت‌ها',
            'is_enabled': 'وضعیت',
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
            (1, 'فعال'),
            (0, 'غیرفعال'),
        )

    def clean_parent_unit(self) -> Optional[CompanyUnit]:
        """Validate parent unit belongs to same company."""
        parent = self.cleaned_data.get('parent_unit')
        if parent and self.company_id and parent.company_id != self.company_id:
            raise forms.ValidationError(_('Parent unit must belong to the same company.'))
        return parent


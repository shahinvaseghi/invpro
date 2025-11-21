"""
WorkLine forms for production module.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _

from production.models import WorkLine, Person, Machine

# Import Warehouse for WorkLine (optional dependency - only if inventory module is installed)
try:
    from inventory.models import Warehouse
except ImportError:
    Warehouse = None


class WorkLineForm(forms.ModelForm):
    """Form for creating/editing work lines."""
    
    personnel = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label=_('پرسنل'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        help_text=_('یک یا چند پرسنل را برای این خط کاری انتخاب کنید'),
    )
    machines = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label=_('ماشین‌ها'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        help_text=_('یک یا چند ماشین را برای این خط کاری انتخاب کنید'),
    )
    
    class Meta:
        model = WorkLine
        fields = ['warehouse', 'name', 'name_en', 'description', 'notes', 'sort_order', 'is_enabled', 'personnel', 'machines']
        widgets = {
            'warehouse': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'warehouse': _('انبار (اختیاری)'),
            'name': _('نام (فارسی)'),
            'name_en': _('نام (انگلیسی)'),
            'description': _('توضیحات'),
            'notes': _('یادداشت‌ها'),
            'sort_order': _('ترتیب نمایش'),
            'is_enabled': _('وضعیت'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        
        if company_id:
            # Filter warehouses by company (only if inventory module is installed)
            if Warehouse:
                self.fields['warehouse'].queryset = Warehouse.objects.filter(
                    company_id=company_id,
                    is_enabled=1,
                ).order_by('name')
            else:
                self.fields['warehouse'].widget = forms.HiddenInput()
                self.fields['warehouse'].required = False
            
            # Filter personnel by company
            self.fields['personnel'].queryset = Person.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('first_name', 'last_name')
            
            # Filter machines by company
            self.fields['machines'].queryset = Machine.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
        else:
            if Warehouse:
                self.fields['warehouse'].queryset = Warehouse.objects.none()
            else:
                self.fields['warehouse'].widget = forms.HiddenInput()
            self.fields['personnel'].queryset = Person.objects.none()
            self.fields['machines'].queryset = Machine.objects.none()
        
        if self.instance.pk:
            self.fields['personnel'].initial = self.instance.personnel.all()
            self.fields['machines'].initial = self.instance.machines.all()
    
    def save(self, commit: bool = True):
        """Save work line instance."""
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    def save_m2m(self) -> None:
        """Save many-to-many relationships."""
        super().save_m2m()
        if self.instance.pk:
            self.instance.personnel.set(self.cleaned_data['personnel'])
            self.instance.machines.set(self.cleaned_data['machines'])


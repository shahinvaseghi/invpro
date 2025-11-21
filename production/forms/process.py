"""
Process forms for production module.
"""
from typing import Optional, Any
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest

from production.models import Process, BOM, WorkLine


class ProcessForm(forms.ModelForm):
    """Form for creating/editing production processes."""
    
    work_lines = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label=_('خطوط کاری'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        help_text=_('یک یا چند خط کاری را برای این فرایند انتخاب کنید'),
    )
    
    class Meta:
        model = Process
        fields = [
            'bom',  # Optional
            'work_lines',
            'revision',  # Optional
            'description',
            'is_primary',
            'approved_by',
            'notes',
            'is_enabled',
            'sort_order',
        ]
        widgets = {
            'bom': forms.Select(attrs={'class': 'form-control'}),
            'revision': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.Select(attrs={'class': 'form-control'}),
            'approved_by': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'bom': _('فهرست مواد اولیه (BOM)'),
            'revision': _('نسخه'),
            'description': _('توضیحات'),
            'is_primary': _('فرایند اصلی'),
            'approved_by': _('تایید کننده'),
            'notes': _('یادداشت‌ها'),
            'is_enabled': _('وضعیت'),
            'sort_order': _('ترتیب نمایش'),
        }
    
    def __init__(self, *args: tuple, company_id: Optional[int] = None, request: Optional[HttpRequest] = None, **kwargs: dict):
        """Initialize form with company filtering."""
        super().__init__(*args, **kwargs)
        
        if company_id:
            # Filter BOMs by company
            self.fields['bom'].queryset = BOM.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).select_related('finished_item').order_by('finished_item__name', 'version')
            self.fields['bom'].required = False  # Optional
            self.fields['revision'].required = False  # Optional
            self.fields['is_primary'].required = False  # Optional
            
            # Filter work lines by company
            self.fields['work_lines'].queryset = WorkLine.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
            
            # Filter approved_by (User) - only users with approve permission for production.processes
            from shared.models import UserCompanyAccess, AccessLevelPermission
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Find access levels that have approve permission for production.processes
            approve_access_levels = list(AccessLevelPermission.objects.filter(
                module_code='production',
                resource_code='production.processes',
                can_approve=1,
            ).values_list('access_level_id', flat=True))
            
            # Find users with those access levels for this company
            approver_user_ids = list(UserCompanyAccess.objects.filter(
                company_id=company_id,
                access_level_id__in=approve_access_levels,
                is_enabled=1,
            ).values_list('user_id', flat=True))
            
            # Filter User queryset to show only users with approve permission
            if approver_user_ids:
                self.fields['approved_by'].queryset = User.objects.filter(
                    id__in=approver_user_ids,
                    is_active=True,
                ).order_by('first_name', 'last_name', 'username')
            else:
                # No approvers found, show empty queryset
                self.fields['approved_by'].queryset = User.objects.none()
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            self.fields['bom'].queryset = BOM.objects.none()
            self.fields['work_lines'].queryset = WorkLine.objects.none()
            self.fields['approved_by'].queryset = User.objects.none()
        
        # Set initial values for edit mode
        if self.instance.pk:
            self.fields['work_lines'].initial = self.instance.work_lines.all()
    
    def save(self, commit: bool = True) -> Process:
        """Save process instance."""
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    def save_m2m(self) -> None:
        """Save many-to-many relationships."""
        super().save_m2m()
        if self.instance.pk:
            self.instance.work_lines.set(self.cleaned_data['work_lines'])


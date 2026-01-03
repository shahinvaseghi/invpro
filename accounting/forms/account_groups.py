"""
Forms for AccountGroup (گروه حساب‌ها) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import AccountGroup


class AccountGroupForm(forms.ModelForm):
    """Form for creating/editing account groups (گروه حساب‌ها)."""
    
    class Meta:
        model = AccountGroup
        fields = [
            'group_code',
            'group_name',
            'group_name_en',
            'description',
            'is_enabled',
        ]
        widgets = {
            'group_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10', 'placeholder': 'مثال: 1'}),
            'group_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: دارایی‌های جاری'}),
            'group_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'group_code': _('کد گروه'),
            'group_name': _('نام گروه'),
            'group_name_en': _('نام گروه (انگلیسی)'),
            'description': _('توضیحات'),
            'is_enabled': _('وضعیت'),
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
        group_code = cleaned_data.get('group_code')
        
        # Validate group_code is provided
        if not group_code:
            raise forms.ValidationError({
                'group_code': _('کد گروه الزامی است.')
            })
        
        # Validate unique code within company
        if group_code and self.company_id:
            existing = AccountGroup.objects.filter(
                company_id=self.company_id,
                group_code=group_code
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError({
                    'group_code': _('کد گروه باید یکتا باشد.')
                })
        
        return cleaned_data


"""
AccessLevel forms for shared module.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from shared.models import AccessLevel, ENABLED_FLAG_CHOICES
from shared.forms.base import BaseModelForm


class AccessLevelForm(BaseModelForm):
    """Form for creating/editing access levels."""
    
    class Meta:
        model = AccessLevel
        fields = ['name', 'description', 'is_enabled', 'is_global']  # Removed 'code' - auto-generated
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': _('Name'),
            'description': _('Description'),
            'is_enabled': _('Status'),
            'is_global': _('Global Role'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with choices and read-only code field."""
        # AccessLevels are not company-scoped, remove company_id if passed
        kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        self.fields['is_enabled'].choices = ENABLED_FLAG_CHOICES
        self.fields['is_global'].choices = ENABLED_FLAG_CHOICES
        
        # Show code as read-only if editing existing instance
        if self.instance and self.instance.pk:
            self.fields['code'] = forms.CharField(
                label=_('Code'),
                required=False,
                widget=forms.TextInput(attrs={'readonly': True}),
                initial=self.instance.code,
                help_text=_('Auto-generated from name. Cannot be changed.')
            )


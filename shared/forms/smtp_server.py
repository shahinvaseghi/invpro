"""
Forms for SMTP Server management.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from shared.models import SMTPServer


class SMTPServerForm(forms.ModelForm):
    """Form for creating and editing SMTP Server configurations."""
    
    class Meta:
        model = SMTPServer
        fields = [
            'name',
            'host',
            'port',
            'use_tls',
            'use_ssl',
            'username',
            'password',
            'from_email',
            'from_name',
            'timeout',
            'description',
            'is_enabled',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'host': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 65535}),
            'use_tls': forms.Select(attrs={'class': 'form-control'}, choices=[(0, _('Disabled')), (1, _('Enabled'))]),
            'use_ssl': forms.Select(attrs={'class': 'form-control'}, choices=[(0, _('Disabled')), (1, _('Enabled'))]),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
            'from_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'from_name': forms.TextInput(attrs={'class': 'form-control'}),
            'timeout': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 300}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}, choices=[(0, _('Disabled')), (1, _('Enabled'))]),
        }
        labels = {
            'name': _('Server Name'),
            'host': _('SMTP Host'),
            'port': _('SMTP Port'),
            'use_tls': _('Use TLS'),
            'use_ssl': _('Use SSL'),
            'username': _('Username'),
            'password': _('Password'),
            'from_email': _('From Email'),
            'from_name': _('From Name'),
            'timeout': _('Connection Timeout (seconds)'),
            'description': _('Description'),
            'is_enabled': _('Enabled'),
        }
        help_texts = {
            'name': _('A descriptive name for this SMTP server configuration'),
            'host': _('SMTP server hostname or IP address (e.g., smtp.gmail.com)'),
            'port': _('SMTP server port (usually 587 for TLS, 465 for SSL, 25 for plain)'),
            'use_tls': _('Enable TLS encryption for SMTP connection'),
            'use_ssl': _('Enable SSL encryption for SMTP connection (usually for port 465)'),
            'username': _('SMTP authentication username (usually email address)'),
            'password': _('SMTP authentication password or app-specific password'),
            'from_email': _('Default sender email address'),
            'from_name': _('Default sender name (optional)'),
            'timeout': _('Connection timeout in seconds'),
            'description': _('Additional notes about this SMTP configuration'),
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form and make password optional for updates."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # For updates, password is optional
            self.fields['password'].required = False
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        use_tls = cleaned_data.get('use_tls')
        use_ssl = cleaned_data.get('use_ssl')
        
        if use_tls == 1 and use_ssl == 1:
            raise forms.ValidationError(_('Cannot use both TLS and SSL. Choose one.'))
        
        # Password is required for new instances
        if not self.instance.pk and not cleaned_data.get('password'):
            self.add_error('password', _('Password is required for new SMTP server configurations.'))
        
        return cleaned_data


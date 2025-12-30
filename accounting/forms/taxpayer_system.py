"""
Forms for Taxpayer System (سامانه مودیان) configuration.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from ..models import FiscalMemoryConfig


class FiscalMemoryConfigForm(forms.ModelForm):
    """Form for creating/editing Fiscal Memory Configuration."""
    
    # File upload fields for keys and certificates
    private_key_file = forms.FileField(
        label=_('فایل کلید خصوصی'),
        help_text=_('فایل کلید خصوصی (PEM format) برای امضای دیجیتال'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pem,.key'
        }),
    )
    
    public_key_file = forms.FileField(
        label=_('فایل کلید عمومی'),
        help_text=_('فایل کلید عمومی (PEM format) برای تبادل با سامانه'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pem,.key,.crt'
        }),
    )
    
    certificate_file = forms.FileField(
        label=_('فایل گواهینامه (Certificate)'),
        help_text=_('فایل گواهینامه دیجیتال (PEM/CER format)'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pem,.cer,.crt,.cert'
        }),
    )
    
    certificate_text = forms.CharField(
        label=_('متن گواهینامه (Certificate Text)'),
        help_text=_('متن گواهینامه دیجیتال (PEM format)'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': '-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----',
            'style': 'font-family: monospace; font-size: 12px;'
        }),
    )
    
    class Meta:
        model = FiscalMemoryConfig
        fields = [
            'fiscal_id',
            'name',
            'server_url',
            'is_enabled',
            'api_timeout',
            'max_retry_count',
            'private_key',
            'private_key_password',
            'public_key',
            'signature_type',
            'encryption_type',
            'notes',
        ]
        widgets = {
            'fiscal_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 1234567890123456'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام حافظه مالیاتی'
            }),
            'server_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://tp.tax.gov.ir'
            }),
            'is_enabled': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[(0, _('غیرفعال')), (1, _('فعال'))]),
            'api_timeout': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 10,
                'max': 300,
                'step': 1
            }),
            'max_retry_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10,
                'step': 1
            }),
            'private_key': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----',
                'style': 'font-family: monospace; font-size: 12px;'
            }),
            'private_key_password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'رمز عبور کلید خصوصی (اختیاری)'
            }),
            'public_key': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----',
                'style': 'font-family: monospace; font-size: 12px;'
            }),
            'signature_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'encryption_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'یادداشت‌ها و توضیحات اضافی...'
            }),
        }
        labels = {
            'fiscal_id': _('شناسه یکتای حافظه مالیاتی'),
            'name': _('نام/توضیحات'),
            'server_url': _('آدرس سرور سامانه مودیان'),
            'is_enabled': _('وضعیت'),
            'api_timeout': _('مدت زمان انتظار برای پاسخ API (ثانیه)'),
            'max_retry_count': _('حداکثر تعداد تلاش مجدد'),
            'private_key': _('کلید خصوصی (متن)'),
            'private_key_password': _('رمز عبور کلید خصوصی'),
            'public_key': _('کلید عمومی (متن)'),
            'signature_type': _('نوع امضا'),
            'encryption_type': _('نوع رمزگذاری'),
            'notes': _('یادداشت‌ها'),
        }
        help_texts = {
            'fiscal_id': _('شناسه یکتای حافظه مالیاتی که از سازمان امور مالیاتی دریافت می‌کنید'),
            'name': _('نام یا توضیحات برای شناسایی این پیکربندی'),
            'server_url': _('آدرس API سرور سامانه مودیان (پیش‌فرض: https://tp.tax.gov.ir)'),
            'is_enabled': _('وضعیت فعال/غیرفعال بودن این پیکربندی'),
            'api_timeout': _('مدت زمان انتظار برای دریافت پاسخ از API (10 تا 300 ثانیه)'),
            'max_retry_count': _('حداکثر تعداد تلاش‌های مجدد در صورت خطا (0 تا 10)'),
            'private_key': _('متن کلید خصوصی برای امضای دیجیتال (یا از فایل آپلود کنید)'),
            'private_key_password': _('رمز عبور کلید خصوصی در صورت رمزگذاری شده بودن'),
            'public_key': _('متن کلید عمومی برای تبادل با سامانه (یا از فایل آپلود کنید)'),
            'signature_type': _('نوع الگوریتم امضای دیجیتال'),
            'encryption_type': _('نوع الگوریتم رمزگذاری'),
            'notes': _('یادداشت‌ها و توضیحات اضافی در مورد این پیکربندی'),
        }
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        # Certificate field (not in model, stored in metadata)
        if self.instance and self.instance.pk:
            self.fields['certificate_file'].help_text += _(' (اگر فایل جدید آپلود کنید، فایل قبلی جایگزین می‌شود)')
    
    def clean_fiscal_id(self):
        """Validate fiscal_id format."""
        fiscal_id = self.cleaned_data.get('fiscal_id')
        if fiscal_id:
            # Remove any whitespace
            fiscal_id = fiscal_id.strip()
            # Basic validation - should be alphanumeric (adjust according to actual requirements)
            if not fiscal_id:
                raise ValidationError(_('شناسه حافظه مالیاتی نمی‌تواند خالی باشد'))
        return fiscal_id
    
    def clean_api_timeout(self):
        """Validate API timeout."""
        timeout = self.cleaned_data.get('api_timeout')
        if timeout and (timeout < 10 or timeout > 300):
            raise ValidationError(_('مدت زمان انتظار باید بین 10 تا 300 ثانیه باشد'))
        return timeout
    
    def clean_max_retry_count(self):
        """Validate max retry count."""
        retry_count = self.cleaned_data.get('max_retry_count')
        if retry_count and (retry_count < 0 or retry_count > 10):
            raise ValidationError(_('تعداد تلاش مجدد باید بین 0 تا 10 باشد'))
        return retry_count
    
    def clean(self):
        """Handle file uploads and validate."""
        cleaned_data = super().clean()
        
        # Handle private key file upload
        private_key_file = cleaned_data.get('private_key_file')
        if private_key_file:
            try:
                # Read file content
                private_key_content = private_key_file.read().decode('utf-8')
                # Basic validation - check if it looks like a PEM key
                if 'BEGIN' in private_key_content and 'KEY' in private_key_content:
                    cleaned_data['private_key'] = private_key_content.strip()
                else:
                    raise ValidationError({
                        'private_key_file': _('فایل کلید خصوصی معتبر نیست. فرمت باید PEM باشد.')
                    })
            except UnicodeDecodeError:
                raise ValidationError({
                    'private_key_file': _('فایل کلید خصوصی باید متن قابل خواندن (UTF-8) باشد.')
                })
        
        # Handle public key file upload
        public_key_file = cleaned_data.get('public_key_file')
        if public_key_file:
            try:
                public_key_content = public_key_file.read().decode('utf-8')
                if 'BEGIN' in public_key_content and 'KEY' in public_key_content:
                    cleaned_data['public_key'] = public_key_content.strip()
                else:
                    raise ValidationError({
                        'public_key_file': _('فایل کلید عمومی معتبر نیست. فرمت باید PEM باشد.')
                    })
            except UnicodeDecodeError:
                raise ValidationError({
                    'public_key_file': _('فایل کلید عمومی باید متن قابل خواندن (UTF-8) باشد.')
                })
        
        # Handle certificate file upload or text (store in metadata)
        certificate_file = cleaned_data.get('certificate_file')
        certificate_text = cleaned_data.get('certificate_text', '').strip()
        
        certificate_content = None
        if certificate_file:
            try:
                certificate_content = certificate_file.read().decode('utf-8')
                if 'BEGIN CERTIFICATE' in certificate_content or 'BEGIN' in certificate_content:
                    certificate_content = certificate_content.strip()
                else:
                    raise ValidationError({
                        'certificate_file': _('فایل گواهینامه معتبر نیست. فرمت باید PEM/CER باشد.')
                    })
            except UnicodeDecodeError:
                raise ValidationError({
                    'certificate_file': _('فایل گواهینامه باید متن قابل خواندن (UTF-8) باشد.')
                })
        elif certificate_text:
            if 'BEGIN CERTIFICATE' in certificate_text or 'BEGIN' in certificate_text:
                certificate_content = certificate_text
            else:
                raise ValidationError({
                    'certificate_text': _('متن گواهینامه معتبر نیست. فرمت باید PEM باشد.')
                })
        
        # Store certificate in metadata
        if certificate_content:
            if not self.instance.metadata:
                self.instance.metadata = {}
            self.instance.metadata['certificate'] = certificate_content
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the form instance."""
        instance = super().save(commit=False)
        if self.company_id:
            instance.company_id = self.company_id
        
        if commit:
            instance.save()
        
        return instance


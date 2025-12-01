"""
Forms for Document Attachment (پیوست اسناد) management.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import DocumentAttachment, AccountingDocument


class DocumentAttachmentUploadForm(forms.Form):
    """Form for uploading document attachments."""
    
    document_number = forms.CharField(
        max_length=50,
        label=_('شماره سند'),
        help_text=_('شماره سند حسابداری که می‌خواهید فایل را به آن مرتبط کنید'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: DOC-1403-001'}),
    )
    files = forms.FileField(
        label=_('فایل‌ها'),
        help_text=_('می‌توانید یک یا چند فایل را انتخاب کنید (تصاویر فاکتور، رسید و...)'),
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'multiple': True, 'accept': 'image/*,.pdf,.doc,.docx'}),
    )
    
    file_type = forms.ChoiceField(
        choices=[('', _('انتخاب کنید'))] + DocumentAttachment.FILE_TYPE_CHOICES,
        label=_('نوع فایل'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    description = forms.CharField(
        label=_('توضیحات'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
    
    def __init__(self, *args, company_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
    
    def clean(self):
        cleaned_data = super().clean()
        document_number = cleaned_data.get('document_number')
        
        # Validate document number if provided
        if document_number and self.company_id:
            # Check if document exists
            try:
                document = AccountingDocument.objects.get(
                    company_id=self.company_id,
                    document_number=document_number
                )
                # Store document for later use
                self._document = document
            except AccountingDocument.DoesNotExist:
                raise forms.ValidationError({
                    'document_number': _('سندی با این شماره یافت نشد.')
                })
            except AccountingDocument.MultipleObjectsReturned:
                raise forms.ValidationError({
                    'document_number': _('چند سند با این شماره یافت شد. لطفاً شماره دقیق‌تر وارد کنید.')
                })
        else:
            self._document = None
        
        return cleaned_data


class DocumentAttachmentFilterForm(forms.Form):
    """Form for filtering document attachments."""
    
    document_number = forms.CharField(
        max_length=50,
        required=False,
        label=_('شماره سند'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'جستجو بر اساس شماره سند'}),
    )
    file_type = forms.ChoiceField(
        choices=[('', _('همه'))] + DocumentAttachment.FILE_TYPE_CHOICES,
        required=False,
        label=_('نوع فایل'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    date_from = forms.DateField(
        required=False,
        label=_('از تاریخ'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False,
        label=_('تا تاریخ'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    uploaded_by = forms.IntegerField(
        required=False,
        label=_('کاربر آپلودکننده'),
        widget=forms.HiddenInput(),
    )


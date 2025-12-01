"""
Document Attachment model.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import AccountingBaseModel


class DocumentAttachment(AccountingBaseModel):
    """
    Attachment files for accounting documents (e.g., invoice images, receipts).
    Allows uploading and linking files to accounting documents.
    """
    FILE_TYPE_CHOICES = [
        ('INVOICE', _('فاکتور')),
        ('RECEIPT', _('رسید')),
        ('CONTRACT', _('قرارداد')),
        ('CHECK', _('چک')),
        ('OTHER', _('سایر')),
    ]
    
    document = models.ForeignKey(
        'AccountingDocument',  # Use string literal for forward reference
        on_delete=models.CASCADE,
        related_name='attachments',
        null=True,
        blank=True,
        help_text=_("سند حسابداری مرتبط (اختیاری)"),
    )
    document_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("شماره سند (برای جستجو و فیلتر)"),
    )
    file = models.FileField(
        upload_to='accounting/documents/%Y/%m/',
        help_text=_("فایل پیوست"),
    )
    file_type = models.CharField(
        max_length=30,
        choices=FILE_TYPE_CHOICES,
        default='OTHER',
        help_text=_("نوع فایل"),
    )
    file_name = models.CharField(
        max_length=255,
        help_text=_("نام اصلی فایل"),
    )
    file_size = models.PositiveIntegerField(
        help_text=_("حجم فایل به بایت"),
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("نوع MIME فایل"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("توضیحات فایل"),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="accounting_attachments_uploaded",
        null=True,
        blank=True,
        help_text=_("کاربری که فایل را آپلود کرده"),
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("تاریخ و زمان آپلود"),
    )

    class Meta:
        verbose_name = _("پیوست سند")
        verbose_name_plural = _("پیوست‌های اسناد")
        ordering = ("company", "-uploaded_at", "document_number")
        indexes = [
            models.Index(fields=("company", "document"), name="acc_attach_doc_idx"),
            models.Index(fields=("company", "document_number"), name="acc_attach_docnum_idx"),
            models.Index(fields=("company", "file_type"), name="acc_attach_type_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.file_name} - {self.document_number or 'بدون سند'}"

    def save(self, *args, **kwargs):
        """Auto-populate file metadata."""
        if self.file and not self.file_name:
            self.file_name = self.file.name.split('/')[-1]
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (AttributeError, OSError):
                pass
        if not self.uploaded_by and hasattr(self, '_uploaded_by'):
            self.uploaded_by = self._uploaded_by
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Get human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


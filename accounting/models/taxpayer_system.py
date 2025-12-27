"""
Taxpayer System (سامانه مودیان) models for accounting module.
"""
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

from .base import AccountingBaseModel, POSITIVE_DECIMAL
from .documents import AccountingDocument

User = get_user_model()


class FiscalMemoryConfig(AccountingBaseModel):
    """
    پیکربندی پایانه فروشگاهی - حافظه مالیاتی
    Configuration for POS Terminal - Fiscal Memory for Taxpayer System
    """
    
    fiscal_id = models.CharField(
        max_length=50,
        help_text=_("شناسه یکتای حافظه مالیاتی (Fiscal ID)"),
    )
    name = models.CharField(
        max_length=200,
        help_text=_("نام/توضیحات حافظه مالیاتی"),
    )
    server_url = models.URLField(
        default='https://tp.tax.gov.ir',
        help_text=_("آدرس سرور سامانه مودیان"),
    )
    is_enabled = models.SmallIntegerField(
        default=1,
        choices=[(0, _('غیرفعال')), (1, _('فعال'))],
        help_text=_("وضعیت فعال/غیرفعال"),
    )
    
    # API Configuration
    api_timeout = models.IntegerField(
        default=30,
        help_text=_("مدت زمان انتظار برای پاسخ API (ثانیه)"),
    )
    max_retry_count = models.IntegerField(
        default=3,
        help_text=_("حداکثر تعداد تلاش مجدد در صورت خطا"),
    )
    
    # Encryption & Security
    private_key = models.TextField(
        blank=True,
        help_text=_("کلید خصوصی برای امضای دیجیتال"),
    )
    private_key_password = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("رمز عبور کلید خصوصی (در صورت نیاز)"),
    )
    public_key = models.TextField(
        blank=True,
        help_text=_("کلید عمومی برای تبادل با سامانه"),
    )
    signature_type = models.CharField(
        max_length=50,
        default='PKCS#7',
        choices=[
            ('PKCS#7', _('PKCS#7')),
            ('RSA', _('RSA')),
            ('ECDSA', _('ECDSA')),
        ],
        help_text=_("نوع امضای دیجیتال"),
    )
    encryption_type = models.CharField(
        max_length=50,
        default='AES-256',
        choices=[
            ('AES-256', _('AES-256')),
            ('AES-128', _('AES-128')),
            ('RSA-2048', _('RSA-2048')),
        ],
        help_text=_("نوع رمزگذاری"),
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        help_text=_("یادداشت‌ها و توضیحات اضافی"),
    )
    
    class Meta:
        verbose_name = _("پیکربندی حافظه مالیاتی")
        verbose_name_plural = _("پیکربندی‌های حافظه مالیاتی")
        ordering = ('company', 'fiscal_id')
        constraints = [
            models.UniqueConstraint(
                fields=('company', 'fiscal_id'),
                name='accounting_fiscalmemory_company_fiscalid_unique'
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.fiscal_id} - {self.name}"


class TaxInvoiceSubmission(AccountingBaseModel):
    """
    ارسال صورتحساب به سامانه مودیان
    Tax Invoice Submission to Taxpayer System
    """
    
    STATUS_CHOICES = [
        ('PENDING', _('در انتظار ارسال')),
        ('SENT', _('ارسال شده')),
        ('ACCEPTED', _('تأیید شده')),
        ('REJECTED', _('رد شده')),
        ('FAILED', _('خطا در ارسال')),
        ('RETRYING', _('در حال تلاش مجدد')),
    ]
    
    # Document Reference
    document = models.ForeignKey(
        AccountingDocument,
        on_delete=models.PROTECT,
        related_name='tax_submissions',
        help_text=_("سند حسابداری مرتبط"),
    )
    
    # Fiscal Memory
    fiscal_memory = models.ForeignKey(
        FiscalMemoryConfig,
        on_delete=models.PROTECT,
        related_name='invoice_submissions',
        help_text=_("حافظه مالیاتی استفاده شده"),
    )
    
    # Submission Info
    submission_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text=_("وضعیت ارسال"),
    )
    submission_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("تاریخ و زمان ارسال"),
    )
    
    # Taxpayer System Response
    response_uid = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("شناسه یکتای پاسخ از سامانه (UID)"),
    )
    response_code = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("کد پاسخ از سامانه"),
    )
    response_message = models.TextField(
        blank=True,
        help_text=_("پیام پاسخ از سامانه"),
    )
    response_timestamp = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("Timestamp پاسخ از سامانه"),
    )
    
    # Invoice Data (JSON)
    invoice_data = models.JSONField(
        default=dict,
        help_text=_("داده‌های صورتحساب (JSON format)"),
    )
    
    # Retry Information
    retry_count = models.IntegerField(
        default=0,
        help_text=_("تعداد تلاش‌های انجام شده"),
    )
    last_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("زمان آخرین تلاش مجدد"),
    )
    
    # Error Information
    error_code = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("کد خطا (در صورت وجود)"),
    )
    error_message = models.TextField(
        blank=True,
        help_text=_("پیام خطا"),
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        help_text=_("یادداشت‌ها و توضیحات"),
    )
    
    class Meta:
        verbose_name = _("ارسال صورتحساب به سامانه مودیان")
        verbose_name_plural = _("ارسال‌های صورتحساب به سامانه مودیان")
        ordering = ('-submission_date', '-created_at')
        indexes = [
            models.Index(fields=['document', 'submission_status']),
            models.Index(fields=['fiscal_memory', 'submission_status']),
            models.Index(fields=['response_uid']),
        ]
    
    def __str__(self) -> str:
        return f"{self.document.document_number} - {self.get_submission_status_display()}"


class TaxInvoiceSubmissionLog(AccountingBaseModel):
    """
    لاگ ارسال صورتحساب به سامانه مودیان
    Log for Tax Invoice Submission
    """
    
    LOG_TYPE_CHOICES = [
        ('SUBMIT', _('ارسال')),
        ('RESPONSE', _('پاسخ')),
        ('RETRY', _('تلاش مجدد')),
        ('ERROR', _('خطا')),
        ('VALIDATION', _('اعتبارسنجی')),
    ]
    
    submission = models.ForeignKey(
        TaxInvoiceSubmission,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text=_("ارسال مرتبط"),
    )
    
    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPE_CHOICES,
        help_text=_("نوع لاگ"),
    )
    
    log_message = models.TextField(
        help_text=_("پیام لاگ"),
    )
    
    request_data = models.JSONField(
        null=True,
        blank=True,
        help_text=_("داده‌های درخواست (JSON)"),
    )
    
    response_data = models.JSONField(
        null=True,
        blank=True,
        help_text=_("داده‌های پاسخ (JSON)"),
    )
    
    http_status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("کد وضعیت HTTP"),
    )
    
    execution_time = models.FloatField(
        null=True,
        blank=True,
        help_text=_("زمان اجرا (ثانیه)"),
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_submission_logs',
        help_text=_("کاربر ایجادکننده"),
    )
    
    class Meta:
        verbose_name = _("لاگ ارسال صورتحساب")
        verbose_name_plural = _("لاگ‌های ارسال صورتحساب")
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['submission', 'log_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.submission} - {self.get_log_type_display()} - {self.created_at}"


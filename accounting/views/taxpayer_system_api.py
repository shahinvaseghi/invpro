"""
API Views for Taxpayer System (سامانه مودیان)
AJAX endpoints for submitting invoices, checking status, etc.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.utils.decorators import method_decorator

from ..models import (
    FiscalMemoryConfig,
    TaxInvoiceSubmission,
    TaxInvoiceSubmissionLog,
    AccountingDocument
)
from ..services import MoadianService, InvoiceConverter
from shared.mixins import FeaturePermissionRequiredMixin

logger = logging.getLogger('accounting.views.taxpayer_system_api')


@method_decorator(login_required, name='dispatch')
class TaxpayerSystemBaseAPIView(FeaturePermissionRequiredMixin, View):
    """Base API view for taxpayer system operations."""
    feature_code = 'accounting.tax.validation'
    required_action = 'view'
    
    def get_company_id(self):
        """Get company ID from session."""
        return self.request.session.get('active_company_id')
    
    def json_response(self, data, status=200):
        """Return JSON response."""
        return JsonResponse(data, status=status)
    
    def error_response(self, message, status=400):
        """Return error JSON response."""
        return self.json_response({'success': False, 'error': str(message)}, status=status)


class TestConnectionAPIView(TaxpayerSystemBaseAPIView):
    """Test connection to taxpayer system."""
    
    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Test connection to fiscal memory."""
        fiscal_memory_id = request.POST.get('fiscal_memory_id')
        company_id = self.get_company_id()
        
        if not fiscal_memory_id or not company_id:
            return self.error_response(_('Missing required parameters'), 400)
        
        try:
            fiscal_memory = FiscalMemoryConfig.objects.get(
                pk=fiscal_memory_id,
                company_id=company_id,
                is_enabled=1
            )
            
            # Initialize service
            service = MoadianService(fiscal_memory)
            
            # Try to get server information (this will test connection)
            server_info = service.get_server_information()
            
            # Log success
            logger.info(f"Connection test successful for fiscal memory {fiscal_memory_id}")
            
            return self.json_response({
                'success': True,
                'message': _('اتصال موفق بود'),
                'server_info': server_info
            })
            
        except FiscalMemoryConfig.DoesNotExist:
            return self.error_response(_('پیکربندی حافظه مالیاتی یافت نشد'), 404)
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return self.error_response(_('خطا در تست اتصال: {error}').format(error=str(e)), 500)


class ValidateDocumentAPIView(TaxpayerSystemBaseAPIView):
    """Validate document before submission."""
    
    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Validate document for submission."""
        document_id = request.POST.get('document_id')
        fiscal_memory_id = request.POST.get('fiscal_memory_id')
        company_id = self.get_company_id()
        
        if not document_id or not fiscal_memory_id or not company_id:
            return self.error_response(_('Missing required parameters'), 400)
        
        try:
            document = AccountingDocument.objects.get(
                pk=document_id,
                company_id=company_id
            )
            
            fiscal_memory = FiscalMemoryConfig.objects.get(
                pk=fiscal_memory_id,
                company_id=company_id,
                is_enabled=1
            )
            
            # Convert document to invoice format
            converter = InvoiceConverter(document, fiscal_memory)
            invoice_data = converter.convert()
            
            # Validate invoice data
            service = MoadianService(fiscal_memory)
            is_valid, errors = service.validate_invoice_data(invoice_data)
            
            if is_valid:
                return self.json_response({
                    'success': True,
                    'message': _('سند معتبر است و آماده ارسال می‌باشد'),
                    'invoice_data': invoice_data
                })
            else:
                return self.json_response({
                    'success': False,
                    'message': _('سند معتبر نیست'),
                    'errors': errors,
                    'invoice_data': invoice_data
                }, 400)
                
        except AccountingDocument.DoesNotExist:
            return self.error_response(_('سند یافت نشد'), 404)
        except FiscalMemoryConfig.DoesNotExist:
            return self.error_response(_('پیکربندی حافظه مالیاتی یافت نشد'), 404)
        except Exception as e:
            logger.error(f"Document validation failed: {e}")
            return self.error_response(_('خطا در اعتبارسنجی: {error}').format(error=str(e)), 500)


class SubmitInvoiceAPIView(TaxpayerSystemBaseAPIView):
    """Submit invoice to taxpayer system."""
    
    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Submit invoice to taxpayer system."""
        document_id = request.POST.get('document_id')
        fiscal_memory_id = request.POST.get('fiscal_memory_id')
        company_id = self.get_company_id()
        
        if not document_id or not fiscal_memory_id or not company_id:
            return self.error_response(_('Missing required parameters'), 400)
        
        try:
            document = AccountingDocument.objects.get(
                pk=document_id,
                company_id=company_id
            )
            
            fiscal_memory = FiscalMemoryConfig.objects.get(
                pk=fiscal_memory_id,
                company_id=company_id,
                is_enabled=1
            )
            
            # Convert document to invoice format
            converter = InvoiceConverter(document, fiscal_memory)
            invoice_data = converter.convert()
            
            # Validate invoice data
            service = MoadianService(fiscal_memory)
            is_valid, errors = service.validate_invoice_data(invoice_data)
            
            if not is_valid:
                return self.json_response({
                    'success': False,
                    'message': _('سند معتبر نیست'),
                    'errors': errors
                }, 400)
            
            # Create submission record
            submission = TaxInvoiceSubmission.objects.create(
                document=document,
                fiscal_memory=fiscal_memory,
                company_id=company_id,
                submission_status='PENDING',
                invoice_data=invoice_data,
                created_by=request.user
            )
            
            # Log submission start
            TaxInvoiceSubmissionLog.objects.create(
                submission=submission,
                log_type='SUBMIT',
                log_message=_('شروع ارسال صورتحساب'),
                request_data=invoice_data,
                created_by=request.user
            )
            
            # Submit invoice
            try:
                response = service.submit_invoice(invoice_data)
                
                # Update submission record
                submission.submission_status = 'SENT'
                submission.submission_date = service._get_timestamp() / 1000  # Convert to datetime
                submission.response_uid = response.get('uid', '')
                submission.response_code = response.get('code', '')
                submission.response_message = response.get('message', '')
                submission.save()
                
                # Log success
                TaxInvoiceSubmissionLog.objects.create(
                    submission=submission,
                    log_type='RESPONSE',
                    log_message=_('ارسال موفق بود'),
                    response_data=response,
                    created_by=request.user
                )
                
                return self.json_response({
                    'success': True,
                    'message': _('صورتحساب با موفقیت ارسال شد'),
                    'submission_id': submission.id,
                    'response': response
                })
                
            except Exception as e:
                # Update submission record with error
                submission.submission_status = 'FAILED'
                submission.error_message = str(e)
                submission.retry_count += 1
                submission.save()
                
                # Log error
                TaxInvoiceSubmissionLog.objects.create(
                    submission=submission,
                    log_type='ERROR',
                    log_message=_('خطا در ارسال: {error}').format(error=str(e)),
                    created_by=request.user
                )
                
                logger.error(f"Invoice submission failed: {e}")
                return self.error_response(_('خطا در ارسال: {error}').format(error=str(e)), 500)
                
        except AccountingDocument.DoesNotExist:
            return self.error_response(_('سند یافت نشد'), 404)
        except FiscalMemoryConfig.DoesNotExist:
            return self.error_response(_('پیکربندی حافظه مالیاتی یافت نشد'), 404)
        except Exception as e:
            logger.error(f"Invoice submission error: {e}")
            return self.error_response(_('خطا: {error}').format(error=str(e)), 500)


class CheckStatusAPIView(TaxpayerSystemBaseAPIView):
    """Check invoice submission status."""
    
    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Check invoice submission status."""
        submission_id = request.POST.get('submission_id')
        company_id = self.get_company_id()
        
        if not submission_id or not company_id:
            return self.error_response(_('Missing required parameters'), 400)
        
        try:
            submission = TaxInvoiceSubmission.objects.get(
                pk=submission_id,
                company_id=company_id
            )
            
            if not submission.response_uid:
                return self.error_response(_('شناسه پاسخ یافت نشد'), 400)
            
            # Initialize service
            service = MoadianService(submission.fiscal_memory)
            
            # Check status
            status_response = service.get_invoice_status(submission.response_uid)
            
            # Update submission record
            submission.response_code = status_response.get('code', '')
            submission.response_message = status_response.get('message', '')
            
            # Update status based on response
            status = status_response.get('status', '').upper()
            if status == 'ACCEPTED':
                submission.submission_status = 'ACCEPTED'
            elif status == 'REJECTED':
                submission.submission_status = 'REJECTED'
            
            submission.save()
            
            # Log status check
            TaxInvoiceSubmissionLog.objects.create(
                submission=submission,
                log_type='RESPONSE',
                log_message=_('بررسی وضعیت انجام شد'),
                response_data=status_response,
                created_by=request.user
            )
            
            return self.json_response({
                'success': True,
                'message': _('وضعیت با موفقیت دریافت شد'),
                'status': submission.get_submission_status_display(),
                'response': status_response
            })
            
        except TaxInvoiceSubmission.DoesNotExist:
            return self.error_response(_('ارسال یافت نشد'), 404)
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return self.error_response(_('خطا در بررسی وضعیت: {error}').format(error=str(e)), 500)


class ViewLogsAPIView(TaxpayerSystemBaseAPIView):
    """View logs for a submission."""
    
    @method_decorator(require_http_methods(["GET"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Get logs for a submission."""
        submission_id = request.GET.get('submission_id')
        company_id = self.get_company_id()
        
        if not submission_id or not company_id:
            return self.error_response(_('Missing required parameters'), 400)
        
        try:
            submission = TaxInvoiceSubmission.objects.get(
                pk=submission_id,
                company_id=company_id
            )
            
            logs = TaxInvoiceSubmissionLog.objects.filter(
                submission=submission
            ).order_by('-created_at')[:100]
            
            logs_data = []
            for log in logs:
                logs_data.append({
                    'id': log.id,
                    'log_type': log.get_log_type_display(),
                    'log_message': log.log_message,
                    'request_data': log.request_data,
                    'response_data': log.response_data,
                    'http_status_code': log.http_status_code,
                    'execution_time': log.execution_time,
                    'created_at': log.created_at.isoformat() if log.created_at else None,
                    'created_by': log.created_by.get_full_name() if log.created_by else None,
                })
            
            return self.json_response({
                'success': True,
                'logs': logs_data,
                'count': len(logs_data)
            })
            
        except TaxInvoiceSubmission.DoesNotExist:
            return self.error_response(_('ارسال یافت نشد'), 404)
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return self.error_response(_('خطا: {error}').format(error=str(e)), 500)


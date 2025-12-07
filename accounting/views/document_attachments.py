"""
Document Attachment (پیوست اسناد) views for accounting module.
"""
from typing import Any, Dict
import os
import zipfile
from io import BytesIO
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, FormView
from django.core.files.uploadedfile import UploadedFile

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import BaseListView
from accounting.models import DocumentAttachment, AccountingDocument
from accounting.forms import DocumentAttachmentUploadForm, DocumentAttachmentFilterForm
from accounting.views.base import AccountingBaseView


class DocumentAttachmentUploadView(FeaturePermissionRequiredMixin, AccountingBaseView, FormView):
    """View for uploading document attachments."""
    form_class = DocumentAttachmentUploadForm
    template_name = 'accounting/attachments/upload.html'
    success_url = reverse_lazy('accounting:attachment_upload')
    feature_code = 'accounting.attachments.upload'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: DocumentAttachmentUploadForm) -> HttpResponseRedirect:
        """Handle multiple file uploads."""
        files = self.request.FILES.getlist('files')
        document = getattr(form, '_document', None)
        document_number = form.cleaned_data.get('document_number', '')
        file_type = form.cleaned_data.get('file_type', 'OTHER')
        description = form.cleaned_data.get('description', '')
        company_id = self.request.session.get('active_company_id')
        
        if not files:
            messages.error(self.request, _('لطفاً حداقل یک فایل انتخاب کنید.'))
            return self.form_invalid(form)
        
        if not company_id:
            messages.error(self.request, _('شرکت فعال انتخاب نشده است.'))
            return self.form_invalid(form)
        
        from shared.models import Company
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            messages.error(self.request, _('شرکت یافت نشد.'))
            return self.form_invalid(form)
        
        uploaded_count = 0
        for file in files:
            if isinstance(file, UploadedFile):
                attachment = DocumentAttachment(
                    company=company,
                    document=document,
                    document_number=document_number,
                    file=file,
                    file_type=file_type,
                    file_name=file.name,
                    file_size=file.size,
                    mime_type=file.content_type or '',
                    description=description,
                    uploaded_by=self.request.user,
                )
                attachment.save()
                uploaded_count += 1
        
        if uploaded_count > 0:
            messages.success(
                self.request,
                _('%(count)d فایل با موفقیت آپلود شد.') % {'count': uploaded_count}
            )
        else:
            messages.error(self.request, _('هیچ فایلی آپلود نشد.'))
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('بارگذاری اسناد')
        context['form_title'] = _('بارگذاری اسناد')
        context['enctype'] = 'multipart/form-data'  # Required for file uploads
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('بارگذاری اسناد')},
        ]
        context['cancel_url'] = reverse('accounting:attachment_list')
        return context


class DocumentAttachmentListView(BaseListView):
    """
    List view for document attachments with filtering and download capabilities.
    """
    model = DocumentAttachment
    template_name = 'accounting/attachments/list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.attachments.list'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['-uploaded_at', 'document_number']
    
    def get_base_queryset(self):
        """Get base queryset filtered by company."""
        queryset = super().get_base_queryset()
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_queryset(self):
        """Filter attachments by active company and search/filter criteria."""
        queryset = super().get_queryset()
        
        document_number = self.request.GET.get('document_number', '').strip()
        file_type = self.request.GET.get('file_type', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        uploaded_by = self.request.GET.get('uploaded_by', '')
        
        if document_number:
            queryset = queryset.filter(
                Q(document_number__icontains=document_number) |
                Q(document__document_number__icontains=document_number)
            )
        
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        if date_from:
            try:
                from django.utils.dateparse import parse_date
                date_from_obj = parse_date(date_from)
                if date_from_obj:
                    queryset = queryset.filter(uploaded_at__gte=date_from_obj)
            except (ValueError, TypeError):
                pass
        
        if date_to:
            try:
                from django.utils.dateparse import parse_date
                from datetime import timedelta
                date_to_obj = parse_date(date_to)
                if date_to_obj:
                    # Include the entire day
                    date_to_obj = date_to_obj + timedelta(days=1)
                    queryset = queryset.filter(uploaded_at__lt=date_to_obj)
            except (ValueError, TypeError):
                pass
        
        if uploaded_by:
            try:
                queryset = queryset.filter(uploaded_by_id=int(uploaded_by))
            except ValueError:
                pass
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('فراخوانی اسناد')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('فراخوانی اسناد'), 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['filter_form'] = DocumentAttachmentFilterForm(self.request.GET)
        
        # Add download URLs
        context['download_single_url'] = reverse('accounting:attachment_download_single')
        context['download_bulk_url'] = reverse('accounting:attachment_download_bulk')
        context['print_enabled'] = True
        
        return context


class DocumentAttachmentDownloadSingleView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """Download a single attachment file."""
    feature_code = 'accounting.attachments.download'
    required_action = 'view_own'
    
    def get(self, request, *args, **kwargs):
        """Download single file."""
        attachment_id = request.GET.get('id')
        if not attachment_id:
            raise Http404(_('فایل یافت نشد.'))
        
        try:
            attachment = DocumentAttachment.objects.get(
                pk=attachment_id,
                company_id=request.session.get('active_company_id')
            )
        except DocumentAttachment.DoesNotExist:
            raise Http404(_('فایل یافت نشد.'))
        
        if not attachment.file:
            raise Http404(_('فایل موجود نیست.'))
        
        response = HttpResponse(attachment.file.read(), content_type=attachment.mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
        return response


class DocumentAttachmentDownloadBulkView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """Download multiple attachments as a ZIP file."""
    feature_code = 'accounting.attachments.download'
    required_action = 'view_own'
    
    def get(self, request, *args, **kwargs):
        """Download multiple files as ZIP."""
        attachment_ids = request.GET.getlist('ids')
        if not attachment_ids:
            messages.error(request, _('لطفاً حداقل یک فایل را انتخاب کنید.'))
            return HttpResponseRedirect(reverse('accounting:attachment_list'))
        
        company_id = request.session.get('active_company_id')
        attachments = DocumentAttachment.objects.filter(
            pk__in=attachment_ids,
            company_id=company_id
        )
        
        if not attachments.exists():
            messages.error(request, _('هیچ فایلی یافت نشد.'))
            return HttpResponseRedirect(reverse('accounting:attachment_list'))
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for attachment in attachments:
                if attachment.file:
                    try:
                        file_content = attachment.file.read()
                        # Use document_number and file_name for path
                        file_path = f"{attachment.document_number or 'بدون_سند'}/{attachment.file_name}"
                        zip_file.writestr(file_path, file_content)
                    except (OSError, IOError):
                        continue
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="accounting_attachments.zip"'
        return response


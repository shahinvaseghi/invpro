"""
Views for Service Request.
"""
from typing import Dict, Any, List, Optional
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .base import ProcurementBaseView
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
)
from procurement.models import ServiceRequest
from procurement import forms


class ServiceRequestListView(ProcurementBaseView, BaseListView):
    """List view for service requests."""
    model = ServiceRequest
    template_name = 'procurement/service_request_list.html'
    feature_code = 'procurement.services.request'
    search_fields = ['request_code']
    filter_fields = ['status', 'priority']
    default_order_by = ['-request_date', '-request_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['requested_by', 'supplier', 'approver']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Service Requests')
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('procurement:service_request_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Service Request')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'procurement:service_request_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'procurement:service_request_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'procurement:service_request_delete'


class ServiceRequestCreateView(ProcurementBaseView, BaseCreateView):
    """Create view for service requests."""
    model = ServiceRequest
    form_class = forms.ServiceRequestForm
    template_name = 'procurement/service_request_form.html'
    success_url = reverse_lazy('procurement:service_requests')
    feature_code = 'procurement.services.request'
    success_message = _('درخواست خدمت با موفقیت ایجاد شد.')
    form_title = _('ایجاد درخواست خدمت')
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs
    
    def form_valid(self, form):
        """Set company and requested_by before saving."""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        
        form.instance.company_id = company_id
        form.instance.requested_by = self.request.user
        
        return super().form_valid(form)


class ServiceRequestDetailView(ProcurementBaseView, BaseDetailView):
    """Detail view for service requests."""
    model = ServiceRequest
    template_name = 'procurement/service_request_detail.html'
    context_object_name = 'service_request'
    feature_code = 'procurement.services.request'
    
    def get_select_related(self):
        """Select related objects."""
        return ['requested_by', 'supplier', 'approver']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Service Request')
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('procurement:service_requests')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('procurement:service_request_edit', kwargs={'pk': self.object.pk})


class ServiceRequestUpdateView(ProcurementBaseView, BaseUpdateView):
    """Update view for service requests."""
    model = ServiceRequest
    form_class = forms.ServiceRequestForm
    template_name = 'procurement/service_request_form.html'
    success_url = reverse_lazy('procurement:service_requests')
    feature_code = 'procurement.services.request'
    success_message = _('درخواست خدمت با موفقیت بروزرسانی شد.')
    form_title = _('ویرایش درخواست خدمت')
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs


class ServiceRequestDeleteView(ProcurementBaseView, BaseDeleteView):
    """Delete view for service requests."""
    model = ServiceRequest
    template_name = 'procurement/service_request_confirm_delete.html'
    success_url = reverse_lazy('procurement:service_requests')
    feature_code = 'procurement.services.request'
    success_message = _('درخواست خدمت با موفقیت حذف شد.')


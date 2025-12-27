"""
Views for Service Invoice.
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
from procurement.models import ServiceInvoice
from procurement import forms


class ServiceInvoiceListView(ProcurementBaseView, BaseListView):
    """List view for service invoices."""
    model = ServiceInvoice
    template_name = 'procurement/service_invoice_list.html'
    feature_code = 'procurement.invoices.service'
    search_fields = ['invoice_code']
    filter_fields = ['invoice_status']
    default_order_by = ['-invoice_date', '-invoice_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['supplier', 'party', 'service_request']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Service Invoices')
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('procurement:service_invoice_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Service Invoice')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'procurement:service_invoice_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'procurement:service_invoice_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'procurement:service_invoice_delete'


class ServiceInvoiceCreateView(ProcurementBaseView, BaseCreateView):
    """Create view for service invoices."""
    model = ServiceInvoice
    form_class = forms.ServiceInvoiceForm
    template_name = 'procurement/service_invoice_form.html'
    success_url = reverse_lazy('procurement:service_invoices')
    feature_code = 'procurement.invoices.service'
    success_message = _('فاکتور خرید خدمت با موفقیت ایجاد شد.')
    form_title = _('ایجاد فاکتور خرید خدمت')
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs


class ServiceInvoiceDetailView(ProcurementBaseView, BaseDetailView):
    """Detail view for service invoices."""
    model = ServiceInvoice
    template_name = 'procurement/service_invoice_detail.html'
    context_object_name = 'service_invoice'
    feature_code = 'procurement.invoices.service'
    
    def get_select_related(self):
        """Select related objects."""
        return ['supplier', 'party', 'service_request']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Service Invoice')
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('procurement:service_invoices')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('procurement:service_invoice_edit', kwargs={'pk': self.object.pk})


class ServiceInvoiceUpdateView(ProcurementBaseView, BaseUpdateView):
    """Update view for service invoices."""
    model = ServiceInvoice
    form_class = forms.ServiceInvoiceForm
    template_name = 'procurement/service_invoice_form.html'
    success_url = reverse_lazy('procurement:service_invoices')
    feature_code = 'procurement.invoices.service'
    success_message = _('فاکتور خرید خدمت با موفقیت بروزرسانی شد.')
    form_title = _('ویرایش فاکتور خرید خدمت')
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs


class ServiceInvoiceDeleteView(ProcurementBaseView, BaseDeleteView):
    """Delete view for service invoices."""
    model = ServiceInvoice
    template_name = 'procurement/service_invoice_confirm_delete.html'
    success_url = reverse_lazy('procurement:service_invoices')
    feature_code = 'procurement.invoices.service'
    success_message = _('فاکتور خرید خدمت با موفقیت حذف شد.')


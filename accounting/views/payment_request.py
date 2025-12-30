"""
Views for Payment Request.
"""
from typing import Dict, Any, List, Optional
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
)
from accounting.models.payment_requests import PaymentRequest
from accounting import forms


class PaymentRequestListView(BaseListView):
    """List view for payment requests."""
    model = PaymentRequest
    template_name = 'accounting/payment_request_list.html'
    feature_code = 'accounting.payment_requests.list'
    active_module = 'accounting'
    search_fields = ['request_code']
    filter_fields = ['request_status', 'payment_type']
    default_order_by = ['-request_date', '-request_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['party', 'purchase_invoice', 'service_invoice']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Payment Requests')
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('accounting:payment_request_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Payment Request')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:payment_request_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:payment_request_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'accounting:payment_request_delete'


class PaymentRequestCreateView(BaseCreateView):
    """Create view for payment requests."""
    model = PaymentRequest
    form_class = forms.PaymentRequestForm
    template_name = 'accounting/payment_request_form.html'
    success_url = reverse_lazy('accounting:payment_requests')
    feature_code = 'accounting.payment_requests.list'
    active_module = 'accounting'
    success_message = _('درخواست پرداخت با موفقیت ایجاد شد.')
    form_title = _('ایجاد درخواست پرداخت')
    
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


class PaymentRequestDetailView(BaseDetailView):
    """Detail view for payment requests."""
    model = PaymentRequest
    template_name = 'accounting/payment_request_detail.html'
    context_object_name = 'payment_request'
    feature_code = 'accounting.payment_requests.list'
    active_module = 'accounting'
    
    def get_select_related(self):
        """Select related objects."""
        return ['party', 'purchase_invoice', 'service_invoice']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Payment Request')
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:payment_requests')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:payment_request_edit', kwargs={'pk': self.object.pk})


class PaymentRequestUpdateView(BaseUpdateView):
    """Update view for payment requests."""
    model = PaymentRequest
    form_class = forms.PaymentRequestForm
    template_name = 'accounting/payment_request_form.html'
    success_url = reverse_lazy('accounting:payment_requests')
    feature_code = 'accounting.payment_requests.list'
    active_module = 'accounting'
    success_message = _('درخواست پرداخت با موفقیت بروزرسانی شد.')
    form_title = _('ویرایش درخواست پرداخت')
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs


class PaymentRequestDeleteView(BaseDeleteView):
    """Delete view for payment requests."""
    model = PaymentRequest
    template_name = 'accounting/payment_request_confirm_delete.html'
    success_url = reverse_lazy('accounting:payment_requests')
    feature_code = 'accounting.payment_requests.list'
    active_module = 'accounting'
    success_message = _('درخواست پرداخت با موفقیت حذف شد.')


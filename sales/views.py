"""
Views for sales module.
"""
from django.views.generic import TemplateView
from shared.mixins import FeaturePermissionRequiredMixin


class SalesDashboardView(FeaturePermissionRequiredMixin, TemplateView):
    """Dashboard view for sales module."""
    template_name = 'sales/dashboard.html'
    feature_code = 'sales.dashboard'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['page_title'] = 'فروش'
        return context


class SalesInvoiceCreateView(FeaturePermissionRequiredMixin, TemplateView):
    """Create view for sales invoice."""
    template_name = 'sales/invoice_create.html'
    feature_code = 'sales.invoice'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['page_title'] = 'صدور فاکتور فروش'
        return context

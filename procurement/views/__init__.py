"""
Views package for procurement module.
"""
from django.views.generic import TemplateView
from shared.mixins import FeaturePermissionRequiredMixin

from .purchase_order import (
    PurchaseOrderListView,
    PurchaseOrderCreateView,
    PurchaseOrderDetailView,
    PurchaseOrderUpdateView,
    PurchaseOrderDeleteView,
)
from .purchase_invoice import (
    PurchaseInvoiceListView,
    PurchaseInvoiceCreateView,
    PurchaseInvoiceDetailView,
    PurchaseInvoiceUpdateView,
    PurchaseInvoiceDeleteView,
)
from .service_request import (
    ServiceRequestListView,
    ServiceRequestCreateView,
    ServiceRequestDetailView,
    ServiceRequestUpdateView,
    ServiceRequestDeleteView,
)
from .service_invoice import (
    ServiceInvoiceListView,
    ServiceInvoiceCreateView,
    ServiceInvoiceDetailView,
    ServiceInvoiceUpdateView,
    ServiceInvoiceDeleteView,
)


# Dashboard and other views
class ProcurementDashboardView(FeaturePermissionRequiredMixin, TemplateView):
    """Dashboard view for procurement module."""
    template_name = 'procurement/dashboard.html'
    feature_code = 'procurement.dashboard'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'procurement'
        context['page_title'] = 'تدارکات'
        return context


class PurchaseListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for purchases."""
    template_name = 'procurement/purchase_list.html'
    feature_code = 'procurement.purchases'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'procurement'
        context['page_title'] = 'خریدها'
        return context


class BuyerListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for buyers."""
    template_name = 'procurement/buyer_list.html'
    feature_code = 'procurement.buyers'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'procurement'
        context['page_title'] = 'خریداران'
        return context


class BuyerCreateView(FeaturePermissionRequiredMixin, TemplateView):
    """Create view for buyers."""
    template_name = 'procurement/buyer_form.html'
    feature_code = 'procurement.buyers'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'procurement'
        context['page_title'] = 'تعریف خریدار'
        return context


class BuyerAssignmentView(FeaturePermissionRequiredMixin, TemplateView):
    """Assignment view for buyers."""
    template_name = 'procurement/buyer_assignment.html'
    feature_code = 'procurement.buyers'
    required_action = 'edit_own'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'procurement'
        context['page_title'] = 'تخصیص خریداران'
        return context


__all__ = [
    'ProcurementDashboardView',
    'PurchaseListView',
    'BuyerListView',
    'BuyerCreateView',
    'BuyerAssignmentView',
    'PurchaseOrderListView',
    'PurchaseOrderCreateView',
    'PurchaseOrderDetailView',
    'PurchaseOrderUpdateView',
    'PurchaseOrderDeleteView',
    'PurchaseInvoiceListView',
    'PurchaseInvoiceCreateView',
    'PurchaseInvoiceDetailView',
    'PurchaseInvoiceUpdateView',
    'PurchaseInvoiceDeleteView',
    'ServiceRequestListView',
    'ServiceRequestCreateView',
    'ServiceRequestDetailView',
    'ServiceRequestUpdateView',
    'ServiceRequestDeleteView',
    'ServiceInvoiceListView',
    'ServiceInvoiceCreateView',
    'ServiceInvoiceDetailView',
    'ServiceInvoiceUpdateView',
    'ServiceInvoiceDeleteView',
]


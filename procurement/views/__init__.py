"""
Views package for procurement module.
"""
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

__all__ = [
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


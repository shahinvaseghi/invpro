"""
URL configuration for procurement module.
"""
from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    path('', views.ProcurementDashboardView.as_view(), name='dashboard'),
    # Purchase
    path('purchases/', views.PurchaseListView.as_view(), name='purchases'),
    # Purchase Orders
    path('purchase-orders/', views.PurchaseOrderListView.as_view(), name='purchase_orders'),
    path('purchase-orders/create/', views.PurchaseOrderCreateView.as_view(), name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='purchase_order_edit'),
    path('purchase-orders/<int:pk>/delete/', views.PurchaseOrderDeleteView.as_view(), name='purchase_order_delete'),
    # Purchase Invoices
    path('purchase-invoices/', views.PurchaseInvoiceListView.as_view(), name='purchase_invoices'),
    path('purchase-invoices/create/', views.PurchaseInvoiceCreateView.as_view(), name='purchase_invoice_create'),
    path('purchase-invoices/<int:pk>/', views.PurchaseInvoiceDetailView.as_view(), name='purchase_invoice_detail'),
    path('purchase-invoices/<int:pk>/edit/', views.PurchaseInvoiceUpdateView.as_view(), name='purchase_invoice_edit'),
    path('purchase-invoices/<int:pk>/delete/', views.PurchaseInvoiceDeleteView.as_view(), name='purchase_invoice_delete'),
    # Service Requests
    path('service-requests/', views.ServiceRequestListView.as_view(), name='service_requests'),
    path('service-requests/create/', views.ServiceRequestCreateView.as_view(), name='service_request_create'),
    path('service-requests/<int:pk>/', views.ServiceRequestDetailView.as_view(), name='service_request_detail'),
    path('service-requests/<int:pk>/edit/', views.ServiceRequestUpdateView.as_view(), name='service_request_edit'),
    path('service-requests/<int:pk>/delete/', views.ServiceRequestDeleteView.as_view(), name='service_request_delete'),
    # Service Invoices
    path('service-invoices/', views.ServiceInvoiceListView.as_view(), name='service_invoices'),
    path('service-invoices/create/', views.ServiceInvoiceCreateView.as_view(), name='service_invoice_create'),
    path('service-invoices/<int:pk>/', views.ServiceInvoiceDetailView.as_view(), name='service_invoice_detail'),
    path('service-invoices/<int:pk>/edit/', views.ServiceInvoiceUpdateView.as_view(), name='service_invoice_edit'),
    path('service-invoices/<int:pk>/delete/', views.ServiceInvoiceDeleteView.as_view(), name='service_invoice_delete'),
    # Buyers
    path('buyers/', views.BuyerListView.as_view(), name='buyers'),
    path('buyers/create/', views.BuyerCreateView.as_view(), name='buyer_create'),
    path('buyers/assignment/', views.BuyerAssignmentView.as_view(), name='buyer_assignment'),
]


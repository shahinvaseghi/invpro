"""
URL configuration for sales module.
"""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SalesDashboardView.as_view(), name='dashboard'),
    path('invoice/create/', views.SalesInvoiceCreateView.as_view(), name='invoice_create'),
]

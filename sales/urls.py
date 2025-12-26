"""
URL configuration for sales module.
"""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SalesDashboardView.as_view(), name='dashboard'),
    path('invoice/create/', views.SalesInvoiceCreateView.as_view(), name='invoice_create'),
    path('price-card/', views.ItemPriceCardListView.as_view(), name='price_card_list'),
    path('price-card/create/', views.ItemPriceCardCreateView.as_view(), name='price_card_create'),
]

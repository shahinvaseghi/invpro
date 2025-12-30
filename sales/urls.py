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
    path('price-card/<int:pk>/', views.ItemPriceCardDetailView.as_view(), name='price_card_detail'),
    path('price-card/<int:pk>/edit/', views.ItemPriceCardUpdateView.as_view(), name='price_card_edit'),
    path('price-card/<int:pk>/delete/', views.ItemPriceCardDeleteView.as_view(), name='price_card_delete'),
    path('customers/', views.CustomersListView.as_view(), name='customers'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('income-receipt-location/', views.IncomeReceiptLocationListView.as_view(), name='income_receipt_location_list'),
    path('income-receipt-location/create/', views.IncomeReceiptLocationCreateView.as_view(), name='income_receipt_location_create'),
    path('settings/', views.SalesSettingsView.as_view(), name='settings'),
]

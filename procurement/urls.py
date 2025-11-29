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
    # Buyers
    path('buyers/', views.BuyerListView.as_view(), name='buyers'),
    path('buyers/create/', views.BuyerCreateView.as_view(), name='buyer_create'),
    path('buyers/assignment/', views.BuyerAssignmentView.as_view(), name='buyer_assignment'),
]


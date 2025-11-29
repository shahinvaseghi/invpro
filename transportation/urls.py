"""
URL configuration for transportation module.
"""
from django.urls import path
from . import views

app_name = 'transportation'

urlpatterns = [
    path('', views.TransportationDashboardView.as_view(), name='dashboard'),
]


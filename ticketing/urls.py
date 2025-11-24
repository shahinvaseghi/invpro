"""
URL configuration for ticketing app.
"""
from django.urls import path

from . import views

app_name = 'ticketing'

urlpatterns = [
    # Tickets
    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/respond/', views.TicketRespondView.as_view(), name='ticket_respond'),
    
    # Management
    path('management/templates/create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('management/categories/', views.CategoriesView.as_view(), name='categories'),
    path('management/subcategories/', views.SubcategoriesView.as_view(), name='subcategories'),
    
    # Automation
    path('automation/auto-response/', views.AutoResponseView.as_view(), name='auto_response'),
]


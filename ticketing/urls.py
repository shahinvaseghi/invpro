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
    
    # Management - Categories
    path('management/categories/', views.TicketCategoryListView.as_view(), name='categories'),
    path('management/categories/create/', views.TicketCategoryCreateView.as_view(), name='category_create'),
    path('management/categories/<int:pk>/edit/', views.TicketCategoryUpdateView.as_view(), name='category_edit'),
    path('management/categories/<int:pk>/delete/', views.TicketCategoryDeleteView.as_view(), name='category_delete'),
    
    # Management - Templates
    path('management/templates/', views.TicketTemplateListView.as_view(), name='templates'),
    path('management/templates/create/', views.TicketTemplateCreateView.as_view(), name='template_create'),
    path('management/templates/<int:pk>/edit/', views.TicketTemplateUpdateView.as_view(), name='template_edit'),
    path('management/templates/<int:pk>/delete/', views.TicketTemplateDeleteView.as_view(), name='template_delete'),
    
    # Management - Subcategories
    path('management/subcategories/', views.TicketSubcategoryListView.as_view(), name='subcategories'),
    path('management/subcategories/create/', views.TicketSubcategoryCreateView.as_view(), name='subcategory_create'),
    path('management/subcategories/<int:pk>/edit/', views.TicketSubcategoryUpdateView.as_view(), name='subcategory_edit'),
    path('management/subcategories/<int:pk>/delete/', views.TicketSubcategoryDeleteView.as_view(), name='subcategory_delete'),
    
    # Automation
    path('automation/auto-response/', views.AutoResponseView.as_view(), name='auto_response'),
    
    # Debug
    path('debug-log/', views.debug_log_view, name='debug_log'),
]


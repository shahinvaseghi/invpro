"""
URL configuration for office automation module.
"""
from django.urls import path
from . import views

app_name = 'office_automation'

urlpatterns = [
    path('', views.OfficeAutomationDashboardView.as_view(), name='dashboard'),
    
    # Inbox (کارتابل)
    path('inbox/incoming/', views.InboxIncomingLettersView.as_view(), name='inbox_incoming'),
    path('inbox/write/', views.InboxWriteLetterView.as_view(), name='inbox_write'),
    path('inbox/fill-form/', views.InboxFillFormView.as_view(), name='inbox_fill_form'),
    
    # Processes (فرایندها)
    path('processes/engine/', views.ProcessEngineView.as_view(), name='processes_engine'),
    path('processes/form-connection/', views.ProcessFormConnectionView.as_view(), name='processes_form_connection'),
    
    # Forms (فرم‌ها)
    path('forms/builder/', views.FormBuilderView.as_view(), name='forms_builder'),
]

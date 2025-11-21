"""
URL configuration for production module.
"""
from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('personnel/', views.PersonnelListView.as_view(), name='personnel'),
    path('personnel/create/', views.PersonCreateView.as_view(), name='person_create'),
    path('personnel/<int:pk>/edit/', views.PersonUpdateView.as_view(), name='person_edit'),
    path('personnel/<int:pk>/delete/', views.PersonDeleteView.as_view(), name='person_delete'),
    
    path('machines/', views.MachineListView.as_view(), name='machines'),
    path('machines/create/', views.MachineCreateView.as_view(), name='machine_create'),
    path('machines/<int:pk>/edit/', views.MachineUpdateView.as_view(), name='machine_edit'),
    path('machines/<int:pk>/delete/', views.MachineDeleteView.as_view(), name='machine_delete'),
    
    # Work Lines (خطوط کاری)
    path('work-lines/', views.WorkLineListView.as_view(), name='work_lines'),
    path('work-lines/create/', views.WorkLineCreateView.as_view(), name='work_line_create'),
    path('work-lines/<int:pk>/edit/', views.WorkLineUpdateView.as_view(), name='work_line_edit'),
    path('work-lines/<int:pk>/delete/', views.WorkLineDeleteView.as_view(), name='work_line_delete'),
    
    # BOM (Bill of Materials - فهرست مواد اولیه)
    path('bom/', views.BOMListView.as_view(), name='bom_list'),
    path('bom/create/', views.BOMCreateView.as_view(), name='bom_create'),
    path('bom/<int:pk>/edit/', views.BOMUpdateView.as_view(), name='bom_edit'),
    path('bom/<int:pk>/delete/', views.BOMDeleteView.as_view(), name='bom_delete'),
    
    # Processes (فرایندهای تولید)
    path('processes/', views.ProcessListView.as_view(), name='processes'),
    path('processes/create/', views.ProcessCreateView.as_view(), name='process_create'),
    path('processes/<int:pk>/edit/', views.ProcessUpdateView.as_view(), name='process_edit'),
    path('processes/<int:pk>/delete/', views.ProcessDeleteView.as_view(), name='process_delete'),
    
    # Transfer to Line Requests (درخواست انتقال به پای کار)
    path('transfer-requests/', views.TransferToLineRequestListView.as_view(), name='transfer_requests'),
    
    # Performance Records (سند عملکرد)
    path('performance-records/', views.PerformanceRecordListView.as_view(), name='performance_records'),
]


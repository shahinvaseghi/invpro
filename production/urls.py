"""
URL configuration for production module.
"""
from django.urls import path
from . import views
from .views import api

app_name = 'production'

urlpatterns = [
    path('personnel/', views.PersonnelListView.as_view(), name='personnel'),
    path('personnel/create/', views.PersonCreateView.as_view(), name='person_create'),
    path('personnel/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('personnel/<int:pk>/edit/', views.PersonUpdateView.as_view(), name='person_edit'),
    path('personnel/<int:pk>/delete/', views.PersonDeleteView.as_view(), name='person_delete'),
    
    path('machines/', views.MachineListView.as_view(), name='machines'),
    path('machines/create/', views.MachineCreateView.as_view(), name='machine_create'),
    path('machines/<int:pk>/', views.MachineDetailView.as_view(), name='machine_detail'),
    path('machines/<int:pk>/edit/', views.MachineUpdateView.as_view(), name='machine_edit'),
    path('machines/<int:pk>/delete/', views.MachineDeleteView.as_view(), name='machine_delete'),
    
    # Work Lines (خطوط کاری)
    path('work-lines/', views.WorkLineListView.as_view(), name='work_lines'),
    path('work-lines/create/', views.WorkLineCreateView.as_view(), name='work_line_create'),
    path('work-lines/<int:pk>/', views.WorkLineDetailView.as_view(), name='work_line_detail'),
    path('work-lines/<int:pk>/edit/', views.WorkLineUpdateView.as_view(), name='work_line_edit'),
    path('work-lines/<int:pk>/delete/', views.WorkLineDeleteView.as_view(), name='work_line_delete'),
    
    # BOM (Bill of Materials - فهرست مواد اولیه)
    path('bom/', views.BOMListView.as_view(), name='bom_list'),
    path('bom/create/', views.BOMCreateView.as_view(), name='bom_create'),
    path('bom/<int:pk>/', views.BOMDetailView.as_view(), name='bom_detail'),
    path('bom/<int:pk>/edit/', views.BOMUpdateView.as_view(), name='bom_edit'),
    path('bom/<int:pk>/delete/', views.BOMDeleteView.as_view(), name='bom_delete'),
    
    # Processes (فرایندهای تولید)
    path('processes/', views.ProcessListView.as_view(), name='processes'),
    path('processes/create/', views.ProcessCreateView.as_view(), name='process_create'),
    path('processes/<int:pk>/', views.ProcessDetailView.as_view(), name='process_detail'),
    path('processes/<int:pk>/edit/', views.ProcessUpdateView.as_view(), name='process_edit'),
    path('processes/<int:pk>/delete/', views.ProcessDeleteView.as_view(), name='process_delete'),
    
    # Product Orders (سفارشات تولید)
    path('product-orders/', views.ProductOrderListView.as_view(), name='product_orders'),
    path('product-orders/create/', views.ProductOrderCreateView.as_view(), name='product_order_create'),
    path('product-orders/<int:pk>/', views.ProductOrderDetailView.as_view(), name='product_order_detail'),
    path('product-orders/<int:pk>/edit/', views.ProductOrderUpdateView.as_view(), name='product_order_edit'),
    path('product-orders/<int:pk>/delete/', views.ProductOrderDeleteView.as_view(), name='product_order_delete'),
    
    # Transfer to Line Requests (درخواست انتقال به پای کار)
    path('transfer-requests/', views.TransferToLineListView.as_view(), name='transfer_requests'),
    path('transfer-requests/create/', views.TransferToLineCreateView.as_view(), name='transfer_request_create'),
    path('transfer-requests/<int:pk>/', views.TransferToLineDetailView.as_view(), name='transfer_request_detail'),
    path('transfer-requests/<int:pk>/edit/', views.TransferToLineUpdateView.as_view(), name='transfer_request_edit'),
    path('transfer-requests/<int:pk>/delete/', views.TransferToLineDeleteView.as_view(), name='transfer_request_delete'),
    path('transfer-requests/<int:pk>/approve/', views.TransferToLineApproveView.as_view(), name='transfer_request_approve'),
    path('transfer-requests/<int:pk>/reject/', views.TransferToLineRejectView.as_view(), name='transfer_request_reject'),
    path('transfer-requests/<int:pk>/qc-approve/', views.TransferToLineQCApproveView.as_view(), name='transfer_request_qc_approve'),
    path('transfer-requests/<int:pk>/qc-reject/', views.TransferToLineQCRejectView.as_view(), name='transfer_request_qc_reject'),
    path('transfer-requests/<int:pk>/create-warehouse-transfer/', views.TransferToLineCreateWarehouseTransferView.as_view(), name='transfer_request_create_warehouse_transfer'),
    path('transfer-requests/<int:pk>/unlock/', views.TransferToLineUnlockView.as_view(), name='transfer_request_unlock'),
    
    # Performance Records (سند عملکرد)
    path('performance-records/', views.PerformanceRecordListView.as_view(), name='performance_records'),
    path('performance-records/create/', views.PerformanceRecordCreateView.as_view(), name='performance_record_create'),
    path('performance-records/get-operations/', views.PerformanceRecordGetOperationsView.as_view(), name='performance_record_get_operations'),
    path('performance-records/<int:pk>/', views.PerformanceRecordDetailView.as_view(), name='performance_record_detail'),
    path('performance-records/<int:pk>/edit/', views.PerformanceRecordUpdateView.as_view(), name='performance_record_edit'),
    path('performance-records/<int:pk>/delete/', views.PerformanceRecordDeleteView.as_view(), name='performance_record_delete'),
    path('performance-records/<int:pk>/approve/', views.PerformanceRecordApproveView.as_view(), name='performance_record_approve'),
    path('performance-records/<int:pk>/reject/', views.PerformanceRecordRejectView.as_view(), name='performance_record_reject'),
    path('performance-records/<int:pk>/create-receipt/', views.PerformanceRecordCreateReceiptView.as_view(), name='performance_record_create_receipt'),
    
    # Tracking and Identification (شناسایی و ردیابی)
    path('tracking-identification/', views.TrackingIdentificationView.as_view(), name='tracking_identification'),
    
    # API endpoints
    path('api/bom/<int:bom_id>/materials/', api.get_bom_materials, name='api_bom_materials'),
    path('api/order/<int:order_id>/operations/', api.get_order_operations, name='api_order_operations'),
    path('api/process/<int:process_id>/operations/', api.get_process_operations, name='api_process_operations'),
    path('api/process/<int:process_id>/details/', api.get_process_details, name='api_process_details'),
    path('api/process/<int:process_id>/bom-materials/', api.get_process_bom_materials, name='api_process_bom_materials'),
]


"""
URL configuration for the inventory module.
"""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Master Data - Item Types
    path('item-types/', views.ItemTypeListView.as_view(), name='item_types'),
    path('item-types/create/', views.ItemTypeCreateView.as_view(), name='itemtype_create'),
    path('item-types/<int:pk>/edit/', views.ItemTypeUpdateView.as_view(), name='itemtype_edit'),
    path('item-types/<int:pk>/delete/', views.ItemTypeDeleteView.as_view(), name='itemtype_delete'),
    
    # Master Data - Item Categories
    path('item-categories/', views.ItemCategoryListView.as_view(), name='item_categories'),
    path('item-categories/create/', views.ItemCategoryCreateView.as_view(), name='itemcategory_create'),
    path('item-categories/<int:pk>/edit/', views.ItemCategoryUpdateView.as_view(), name='itemcategory_edit'),
    path('item-categories/<int:pk>/delete/', views.ItemCategoryDeleteView.as_view(), name='itemcategory_delete'),
    
    # Master Data - Item Subcategories
    path('item-subcategories/', views.ItemSubcategoryListView.as_view(), name='item_subcategories'),
    path('item-subcategories/create/', views.ItemSubcategoryCreateView.as_view(), name='itemsubcategory_create'),
    path('item-subcategories/<int:pk>/edit/', views.ItemSubcategoryUpdateView.as_view(), name='itemsubcategory_edit'),
    path('item-subcategories/<int:pk>/delete/', views.ItemSubcategoryDeleteView.as_view(), name='itemsubcategory_delete'),
    
    # Master Data - Items
    path('items/', views.ItemListView.as_view(), name='items'),
    path('items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    
    # Master Data - Warehouses
    path('warehouses/', views.WarehouseListView.as_view(), name='warehouses'),
    path('warehouses/create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouses/<int:pk>/edit/', views.WarehouseUpdateView.as_view(), name='warehouse_edit'),
    path('warehouses/<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),
    
    # Master Data - Work Lines
    path('work-lines/', views.WorkLineListView.as_view(), name='work_lines'),
    
    # Suppliers
    path('supplier-categories/', views.SupplierCategoryListView.as_view(), name='supplier_categories'),
    path('supplier-categories/create/', views.SupplierCategoryCreateView.as_view(), name='suppliercategory_create'),
    path('supplier-categories/<int:pk>/edit/', views.SupplierCategoryUpdateView.as_view(), name='suppliercategory_edit'),
    path('supplier-categories/<int:pk>/delete/', views.SupplierCategoryDeleteView.as_view(), name='suppliercategory_delete'),
    
    path('suppliers/', views.SupplierListView.as_view(), name='suppliers'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Purchase Requests
    path('purchase-requests/', views.PurchaseRequestListView.as_view(), name='purchase_requests'),
    path('purchase-requests/create/', views.PurchaseRequestCreateView.as_view(), name='purchase_request_create'),
    path('purchase-requests/<int:pk>/edit/', views.PurchaseRequestUpdateView.as_view(), name='purchase_request_edit'),
    path('purchase-requests/<int:pk>/approve/', views.PurchaseRequestApproveView.as_view(), name='purchase_request_approve'),
    
    # Receipts
    path('receipts/temporary/', views.ReceiptTemporaryListView.as_view(), name='receipt_temporary'),
    path('receipts/temporary/create/', views.ReceiptTemporaryCreateView.as_view(), name='receipt_temporary_create'),
    path('receipts/temporary/<int:pk>/edit/', views.ReceiptTemporaryUpdateView.as_view(), name='receipt_temporary_edit'),
    path('receipts/temporary/<int:pk>/lock/', views.ReceiptTemporaryLockView.as_view(), name='receipt_temporary_lock'),
    path('receipts/permanent/', views.ReceiptPermanentListView.as_view(), name='receipt_permanent'),
    path('receipts/permanent/create/', views.ReceiptPermanentCreateView.as_view(), name='receipt_permanent_create'),
    path('receipts/permanent/<int:pk>/edit/', views.ReceiptPermanentUpdateView.as_view(), name='receipt_permanent_edit'),
    path('receipts/permanent/<int:pk>/lock/', views.ReceiptPermanentLockView.as_view(), name='receipt_permanent_lock'),
    path('receipts/consignment/', views.ReceiptConsignmentListView.as_view(), name='receipt_consignment'),
    path('receipts/consignment/create/', views.ReceiptConsignmentCreateView.as_view(), name='receipt_consignment_create'),
    path('receipts/consignment/<int:pk>/edit/', views.ReceiptConsignmentUpdateView.as_view(), name='receipt_consignment_edit'),
    path('receipts/consignment/<int:pk>/lock/', views.ReceiptConsignmentLockView.as_view(), name='receipt_consignment_lock'),
    
    # Issues
    path('issues/permanent/', views.IssuePermanentListView.as_view(), name='issue_permanent'),
    path('issues/permanent/create/', views.IssuePermanentCreateView.as_view(), name='issue_permanent_create'),
    path('issues/permanent/<int:pk>/edit/', views.IssuePermanentUpdateView.as_view(), name='issue_permanent_edit'),
    path('issues/permanent/<int:pk>/lock/', views.IssuePermanentLockView.as_view(), name='issue_permanent_lock'),
    path('issues/consumption/', views.IssueConsumptionListView.as_view(), name='issue_consumption'),
    path('issues/consumption/create/', views.IssueConsumptionCreateView.as_view(), name='issue_consumption_create'),
    path('issues/consumption/<int:pk>/edit/', views.IssueConsumptionUpdateView.as_view(), name='issue_consumption_edit'),
    path('issues/consumption/<int:pk>/lock/', views.IssueConsumptionLockView.as_view(), name='issue_consumption_lock'),
    path('issues/consignment/', views.IssueConsignmentListView.as_view(), name='issue_consignment'),
    path('issues/consignment/create/', views.IssueConsignmentCreateView.as_view(), name='issue_consignment_create'),
    path('issues/consignment/<int:pk>/edit/', views.IssueConsignmentUpdateView.as_view(), name='issue_consignment_edit'),
    path('issues/consignment/<int:pk>/lock/', views.IssueConsignmentLockView.as_view(), name='issue_consignment_lock'),
    
    # Stocktaking
    path('stocktaking/deficit/', views.StocktakingDeficitListView.as_view(), name='stocktaking_deficit'),
    path('stocktaking/deficit/create/', views.StocktakingDeficitCreateView.as_view(), name='stocktaking_deficit_create'),
    path('stocktaking/deficit/<int:pk>/edit/', views.StocktakingDeficitUpdateView.as_view(), name='stocktaking_deficit_edit'),
    path('stocktaking/deficit/<int:pk>/lock/', views.StocktakingDeficitLockView.as_view(), name='stocktaking_deficit_lock'),
    path('stocktaking/surplus/', views.StocktakingSurplusListView.as_view(), name='stocktaking_surplus'),
    path('stocktaking/surplus/create/', views.StocktakingSurplusCreateView.as_view(), name='stocktaking_surplus_create'),
    path('stocktaking/surplus/<int:pk>/edit/', views.StocktakingSurplusUpdateView.as_view(), name='stocktaking_surplus_edit'),
    path('stocktaking/surplus/<int:pk>/lock/', views.StocktakingSurplusLockView.as_view(), name='stocktaking_surplus_lock'),
    path('stocktaking/records/', views.StocktakingRecordListView.as_view(), name='stocktaking_records'),
    path('stocktaking/records/create/', views.StocktakingRecordCreateView.as_view(), name='stocktaking_record_create'),
    path('stocktaking/records/<int:pk>/edit/', views.StocktakingRecordUpdateView.as_view(), name='stocktaking_record_edit'),
    path('stocktaking/records/<int:pk>/lock/', views.StocktakingRecordLockView.as_view(), name='stocktaking_record_lock'),
    
    # Warehouse Requests
    path('warehouse-requests/', views.WarehouseRequestListView.as_view(), name='warehouse_requests'),
    path('warehouse-requests/create/', views.WarehouseRequestCreateView.as_view(), name='warehouse_request_create'),
    path('warehouse-requests/<int:pk>/edit/', views.WarehouseRequestUpdateView.as_view(), name='warehouse_request_edit'),
    path('warehouse-requests/<int:pk>/approve/', views.WarehouseRequestApproveView.as_view(), name='warehouse_request_approve'),
    
    # Inventory Balance
    path('balance/', views.InventoryBalanceView.as_view(), name='inventory_balance'),
    path('api/balance/', views.InventoryBalanceAPIView.as_view(), name='inventory_balance_api'),
]


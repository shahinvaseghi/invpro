"""
URL configuration for the inventory module.
"""
from django.urls import path
from . import views
# Import API endpoints from refactored module (with Type Hints)
from .views import api as views_api

app_name = 'inventory'

urlpatterns = [
    # Master Data - Item Types
    path('item-types/', views.ItemTypeListView.as_view(), name='item_types'),
    path('item-types/create/', views.ItemTypeCreateView.as_view(), name='itemtype_create'),
    path('item-types/<int:pk>/', views.ItemTypeDetailView.as_view(), name='itemtype_detail'),
    path('item-types/<int:pk>/edit/', views.ItemTypeUpdateView.as_view(), name='itemtype_edit'),
    path('item-types/<int:pk>/delete/', views.ItemTypeDeleteView.as_view(), name='itemtype_delete'),
    
    # Master Data - Item Categories
    path('item-categories/', views.ItemCategoryListView.as_view(), name='item_categories'),
    path('item-categories/create/', views.ItemCategoryCreateView.as_view(), name='itemcategory_create'),
    path('item-categories/<int:pk>/', views.ItemCategoryDetailView.as_view(), name='itemcategory_detail'),
    path('item-categories/<int:pk>/edit/', views.ItemCategoryUpdateView.as_view(), name='itemcategory_edit'),
    path('item-categories/<int:pk>/delete/', views.ItemCategoryDeleteView.as_view(), name='itemcategory_delete'),
    
    # Master Data - Item Subcategories
    path('item-subcategories/', views.ItemSubcategoryListView.as_view(), name='item_subcategories'),
    path('item-subcategories/create/', views.ItemSubcategoryCreateView.as_view(), name='itemsubcategory_create'),
    path('item-subcategories/<int:pk>/', views.ItemSubcategoryDetailView.as_view(), name='itemsubcategory_detail'),
    path('item-subcategories/<int:pk>/edit/', views.ItemSubcategoryUpdateView.as_view(), name='itemsubcategory_edit'),
    path('item-subcategories/<int:pk>/delete/', views.ItemSubcategoryDeleteView.as_view(), name='itemsubcategory_delete'),
    
    # Master Data - Items
    path('items/', views.ItemListView.as_view(), name='items'),
    path('items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    path('item-serials/', views.ItemSerialListView.as_view(), name='item_serials'),
    # Item Excel Import/Export
    path('items/excel-template/', views.ItemExcelTemplateDownloadView.as_view(), name='item_excel_template'),
    path('items/excel-import/', views.ItemExcelImportView.as_view(), name='item_excel_import'),
    
    # API endpoints (from refactored views.api module with Type Hints)
    path('api/item-allowed-units/', views_api.get_item_allowed_units, name='item_allowed_units'),
    path('api/filtered-categories/', views_api.get_filtered_categories, name='filtered_categories'),
    path('api/filtered-subcategories/', views_api.get_filtered_subcategories, name='filtered_subcategories'),
    path('api/filtered-items/', views_api.get_filtered_items, name='filtered_items'),
    path('api/item-units/', views_api.get_item_units, name='item_units'),
    path('api/item-allowed-warehouses/', views_api.get_item_allowed_warehouses, name='item_allowed_warehouses'),
    path('api/item-available-serials/', views_api.get_item_available_serials, name='item_available_serials'),
    path('api/serial/<int:serial_id>/update-secondary/', views_api.update_serial_secondary_code, name='update_serial_secondary_code'),
    path('api/temporary-receipt-data/', views_api.get_temporary_receipt_data, name='temporary_receipt_data'),
    path('api/warehouse-work-lines/', views_api.get_warehouse_work_lines, name='warehouse_work_lines'),
    
    # Master Data - Warehouses
    path('warehouses/', views.WarehouseListView.as_view(), name='warehouses'),
    path('warehouses/create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouses/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse_detail'),
    path('warehouses/<int:pk>/edit/', views.WarehouseUpdateView.as_view(), name='warehouse_edit'),
    path('warehouses/<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),
    
    # Work Lines moved to production module
    # URLs are now in production/urls.py
    
    # Suppliers
    path('supplier-categories/', views.SupplierCategoryListView.as_view(), name='supplier_categories'),
    path('supplier-categories/create/', views.SupplierCategoryCreateView.as_view(), name='suppliercategory_create'),
    path('supplier-categories/<int:pk>/', views.SupplierCategoryDetailView.as_view(), name='suppliercategory_detail'),
    path('supplier-categories/<int:pk>/edit/', views.SupplierCategoryUpdateView.as_view(), name='suppliercategory_edit'),
    path('supplier-categories/<int:pk>/delete/', views.SupplierCategoryDeleteView.as_view(), name='suppliercategory_delete'),
    
    path('suppliers/', views.SupplierListView.as_view(), name='suppliers'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Purchase Requests
    path('purchase-requests/', views.PurchaseRequestListView.as_view(), name='purchase_requests'),
    path('purchase-requests/create/', views.PurchaseRequestCreateView.as_view(), name='purchase_request_create'),
    path('purchase-requests/create-from-transfer-request/<int:transfer_id>/', views.PurchaseRequestCreateFromTransferRequestView.as_view(), name='purchase_request_create_from_transfer_request'),
    path('purchase-requests/<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='purchase_request_detail'),
    path('purchase-requests/<int:pk>/edit/', views.PurchaseRequestUpdateView.as_view(), name='purchase_request_edit'),
    path('purchase-requests/<int:pk>/approve/', views.PurchaseRequestApproveView.as_view(), name='purchase_request_approve'),
    path('purchase-requests/<int:pk>/create-temporary-receipt/', views.CreateTemporaryReceiptFromPurchaseRequestView.as_view(), name='purchase_request_create_temporary_receipt'),
    path('purchase-requests/<int:pk>/create-permanent-receipt/', views.CreatePermanentReceiptFromPurchaseRequestView.as_view(), name='purchase_request_create_permanent_receipt'),
    path('purchase-requests/<int:pk>/create-consignment-receipt/', views.CreateConsignmentReceiptFromPurchaseRequestView.as_view(), name='purchase_request_create_consignment_receipt'),
    
    # Receipts
    path('receipts/temporary/', views.ReceiptTemporaryListView.as_view(), name='receipt_temporary'),
    path('receipts/temporary/create/', views.ReceiptTemporaryCreateView.as_view(), name='receipt_temporary_create'),
    path('receipts/temporary/create-from-request/<int:pk>/', views.ReceiptTemporaryCreateFromPurchaseRequestView.as_view(), name='receipt_temporary_create_from_request'),
    path('receipts/temporary/<int:pk>/', views.ReceiptTemporaryDetailView.as_view(), name='receipt_temporary_detail'),
    path('receipts/temporary/<int:pk>/edit/', views.ReceiptTemporaryUpdateView.as_view(), name='receipt_temporary_edit'),
    path('receipts/temporary/<int:pk>/delete/', views.ReceiptTemporaryDeleteView.as_view(), name='receipt_temporary_delete'),
    path('receipts/temporary/<int:pk>/lock/', views.ReceiptTemporaryLockView.as_view(), name='receipt_temporary_lock'),
    path('receipts/temporary/<int:pk>/unlock/', views.ReceiptTemporaryUnlockView.as_view(), name='receipt_temporary_unlock'),
    path('receipts/temporary/<int:pk>/send-to-qc/', views.ReceiptTemporarySendToQCView.as_view(), name='receipt_temporary_send_to_qc'),
    path('receipts/permanent/', views.ReceiptPermanentListView.as_view(), name='receipt_permanent'),
    path('receipts/permanent/create/', views.ReceiptPermanentCreateView.as_view(), name='receipt_permanent_create'),
    path('receipts/permanent/create-from-request/<int:pk>/', views.ReceiptPermanentCreateFromPurchaseRequestView.as_view(), name='receipt_permanent_create_from_request'),
    path('receipts/permanent/<int:pk>/', views.ReceiptPermanentDetailView.as_view(), name='receipt_permanent_detail'),
    path('receipts/permanent/<int:pk>/edit/', views.ReceiptPermanentUpdateView.as_view(), name='receipt_permanent_edit'),
    path('receipts/permanent/<int:pk>/delete/', views.ReceiptPermanentDeleteView.as_view(), name='receipt_permanent_delete'),
    path('receipts/permanent/<int:pk>/lock/', views.ReceiptPermanentLockView.as_view(), name='receipt_permanent_lock'),
    path('receipts/permanent/<int:pk>/unlock/', views.ReceiptPermanentUnlockView.as_view(), name='receipt_permanent_unlock'),
    path('receipts/permanent/<int:pk>/lines/<int:line_id>/serials/', views.ReceiptPermanentLineSerialAssignmentView.as_view(), name='receipt_permanent_line_serials'),
    path('receipts/consignment/', views.ReceiptConsignmentListView.as_view(), name='receipt_consignment'),
    path('receipts/consignment/create/', views.ReceiptConsignmentCreateView.as_view(), name='receipt_consignment_create'),
    path('receipts/consignment/create-from-request/<int:pk>/', views.ReceiptConsignmentCreateFromPurchaseRequestView.as_view(), name='receipt_consignment_create_from_request'),
    path('receipts/consignment/<int:pk>/', views.ReceiptConsignmentDetailView.as_view(), name='receipt_consignment_detail'),
    path('receipts/consignment/<int:pk>/edit/', views.ReceiptConsignmentUpdateView.as_view(), name='receipt_consignment_edit'),
    path('receipts/consignment/<int:pk>/delete/', views.ReceiptConsignmentDeleteView.as_view(), name='receipt_consignment_delete'),
    path('receipts/consignment/<int:pk>/lock/', views.ReceiptConsignmentLockView.as_view(), name='receipt_consignment_lock'),
    path('receipts/consignment/<int:pk>/unlock/', views.ReceiptConsignmentUnlockView.as_view(), name='receipt_consignment_unlock'),
    path('receipts/consignment/<int:pk>/lines/<int:line_id>/serials/', views.ReceiptConsignmentLineSerialAssignmentView.as_view(), name='receipt_consignment_line_serials'),
    
    # Issues
    path('issues/permanent/', views.IssuePermanentListView.as_view(), name='issue_permanent'),
    path('issues/permanent/create/', views.IssuePermanentCreateView.as_view(), name='issue_permanent_create'),
    path('issues/permanent/<int:pk>/', views.IssuePermanentDetailView.as_view(), name='issue_permanent_detail'),
    path('issues/permanent/<int:pk>/edit/', views.IssuePermanentUpdateView.as_view(), name='issue_permanent_edit'),
    path('issues/permanent/<int:pk>/delete/', views.IssuePermanentDeleteView.as_view(), name='issue_permanent_delete'),
    path('issues/permanent/<int:pk>/lock/', views.IssuePermanentLockView.as_view(), name='issue_permanent_lock'),
    path('issues/permanent/<int:pk>/lines/<int:line_id>/serials/', views.IssuePermanentLineSerialAssignmentView.as_view(), name='issue_permanent_line_serials'),
    path('issues/consumption/', views.IssueConsumptionListView.as_view(), name='issue_consumption'),
    path('issues/consumption/create/', views.IssueConsumptionCreateView.as_view(), name='issue_consumption_create'),
    path('issues/consumption/<int:pk>/', views.IssueConsumptionDetailView.as_view(), name='issue_consumption_detail'),
    path('issues/consumption/<int:pk>/edit/', views.IssueConsumptionUpdateView.as_view(), name='issue_consumption_edit'),
    path('issues/consumption/<int:pk>/delete/', views.IssueConsumptionDeleteView.as_view(), name='issue_consumption_delete'),
    path('issues/consumption/<int:pk>/lock/', views.IssueConsumptionLockView.as_view(), name='issue_consumption_lock'),
    path('issues/consumption/<int:pk>/lines/<int:line_id>/serials/', views.IssueConsumptionLineSerialAssignmentView.as_view(), name='issue_consumption_line_serials'),
    path('issues/consignment/', views.IssueConsignmentListView.as_view(), name='issue_consignment'),
    path('issues/consignment/create/', views.IssueConsignmentCreateView.as_view(), name='issue_consignment_create'),
    path('issues/consignment/<int:pk>/', views.IssueConsignmentDetailView.as_view(), name='issue_consignment_detail'),
    path('issues/consignment/<int:pk>/edit/', views.IssueConsignmentUpdateView.as_view(), name='issue_consignment_edit'),
    path('issues/consignment/<int:pk>/delete/', views.IssueConsignmentDeleteView.as_view(), name='issue_consignment_delete'),
    path('issues/consignment/<int:pk>/lock/', views.IssueConsignmentLockView.as_view(), name='issue_consignment_lock'),
    path('issues/consignment/<int:pk>/lines/<int:line_id>/serials/', views.IssueConsignmentLineSerialAssignmentView.as_view(), name='issue_consignment_line_serials'),
    path('issues/warehouse-transfer/', views.IssueWarehouseTransferListView.as_view(), name='issue_warehouse_transfer'),
    path('issues/warehouse-transfer/create/', views.IssueWarehouseTransferCreateView.as_view(), name='issue_warehouse_transfer_create'),
    path('issues/warehouse-transfer/<int:pk>/', views.IssueWarehouseTransferDetailView.as_view(), name='issue_warehouse_transfer_detail'),
    path('issues/warehouse-transfer/<int:pk>/edit/', views.IssueWarehouseTransferUpdateView.as_view(), name='issue_warehouse_transfer_edit'),
    path('issues/warehouse-transfer/<int:pk>/lock/', views.IssueWarehouseTransferLockView.as_view(), name='issue_warehouse_transfer_lock'),
    path('issues/warehouse-transfer/<int:pk>/unlock/', views.IssueWarehouseTransferUnlockView.as_view(), name='issue_warehouse_transfer_unlock'),
    
    # Stocktaking
    path('stocktaking/deficit/', views.StocktakingDeficitListView.as_view(), name='stocktaking_deficit'),
    path('stocktaking/deficit/create/', views.StocktakingDeficitCreateView.as_view(), name='stocktaking_deficit_create'),
    path('stocktaking/deficit/<int:pk>/', views.StocktakingDeficitDetailView.as_view(), name='stocktaking_deficit_detail'),
    path('stocktaking/deficit/<int:pk>/edit/', views.StocktakingDeficitUpdateView.as_view(), name='stocktaking_deficit_edit'),
    path('stocktaking/deficit/<int:pk>/delete/', views.StocktakingDeficitDeleteView.as_view(), name='stocktaking_deficit_delete'),
    path('stocktaking/deficit/<int:pk>/lock/', views.StocktakingDeficitLockView.as_view(), name='stocktaking_deficit_lock'),
    path('stocktaking/surplus/', views.StocktakingSurplusListView.as_view(), name='stocktaking_surplus'),
    path('stocktaking/surplus/create/', views.StocktakingSurplusCreateView.as_view(), name='stocktaking_surplus_create'),
    path('stocktaking/surplus/<int:pk>/', views.StocktakingSurplusDetailView.as_view(), name='stocktaking_surplus_detail'),
    path('stocktaking/surplus/<int:pk>/edit/', views.StocktakingSurplusUpdateView.as_view(), name='stocktaking_surplus_edit'),
    path('stocktaking/surplus/<int:pk>/delete/', views.StocktakingSurplusDeleteView.as_view(), name='stocktaking_surplus_delete'),
    path('stocktaking/surplus/<int:pk>/lock/', views.StocktakingSurplusLockView.as_view(), name='stocktaking_surplus_lock'),
    path('stocktaking/records/', views.StocktakingRecordListView.as_view(), name='stocktaking_records'),
    path('stocktaking/records/create/', views.StocktakingRecordCreateView.as_view(), name='stocktaking_record_create'),
    path('stocktaking/records/<int:pk>/', views.StocktakingRecordDetailView.as_view(), name='stocktaking_record_detail'),
    path('stocktaking/records/<int:pk>/edit/', views.StocktakingRecordUpdateView.as_view(), name='stocktaking_record_edit'),
    path('stocktaking/records/<int:pk>/delete/', views.StocktakingRecordDeleteView.as_view(), name='stocktaking_record_delete'),
    path('stocktaking/records/<int:pk>/lock/', views.StocktakingRecordLockView.as_view(), name='stocktaking_record_lock'),
    
    # Warehouse Requests
    path('warehouse-requests/', views.WarehouseRequestListView.as_view(), name='warehouse_requests'),
    path('warehouse-requests/create/', views.WarehouseRequestCreateView.as_view(), name='warehouse_request_create'),
    path('warehouse-requests/<int:pk>/', views.WarehouseRequestDetailView.as_view(), name='warehouse_request_detail'),
    path('warehouse-requests/<int:pk>/edit/', views.WarehouseRequestUpdateView.as_view(), name='warehouse_request_edit'),
    path('warehouse-requests/<int:pk>/approve/', views.WarehouseRequestApproveView.as_view(), name='warehouse_request_approve'),
    # Intermediate selection views (quantity selection)
    path('warehouse-requests/<int:pk>/create-permanent-issue/', views.CreatePermanentIssueFromWarehouseRequestView.as_view(), name='warehouse_request_create_permanent_issue'),
    path('warehouse-requests/<int:pk>/create-consumption-issue/', views.CreateConsumptionIssueFromWarehouseRequestView.as_view(), name='warehouse_request_create_consumption_issue'),
    path('warehouse-requests/<int:pk>/create-consignment-issue/', views.CreateConsignmentIssueFromWarehouseRequestView.as_view(), name='warehouse_request_create_consignment_issue'),
    # Actual creation views (redirected from selection views)
    path('warehouse-requests/<int:pk>/create-permanent-issue/continue/', views.IssuePermanentCreateFromWarehouseRequestView.as_view(), name='issue_permanent_create_from_warehouse_request'),
    path('warehouse-requests/<int:pk>/create-consumption-issue/continue/', views.IssueConsumptionCreateFromWarehouseRequestView.as_view(), name='issue_consumption_create_from_warehouse_request'),
    path('warehouse-requests/<int:pk>/create-consignment-issue/continue/', views.IssueConsignmentCreateFromWarehouseRequestView.as_view(), name='issue_consignment_create_from_warehouse_request'),
    
    # Inventory Balance
    path('balance/', views.InventoryBalanceView.as_view(), name='inventory_balance'),
    path('balance/details/<int:item_id>/<int:warehouse_id>/', views.InventoryBalanceDetailsView.as_view(), name='balance_details'),
    path('api/balance/', views.InventoryBalanceAPIView.as_view(), name='inventory_balance_api'),
]

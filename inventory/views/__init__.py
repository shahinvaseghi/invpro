"""
Views package for inventory module.

NOTE: Refactoring is in progress. Currently, most views are still in inventory/views.py.
This package structure is being prepared for the refactoring.

Currently available:
- base.py: Base views and mixins (with Type Hints)
- api.py: API endpoints (with Type Hints)
- master_data.py: Master data CRUD views (with Type Hints)

To use views, import from inventory.views directly (not from inventory.views.views).
The main views.py file is still the primary source for most views.

IMPORTANT: Since inventory/views is now a package (has __init__.py), Python will
import this package instead of inventory/views.py. To maintain backward compatibility,
we import all remaining views from the parent views.py file using importlib.
"""
import sys
import importlib.util
from pathlib import Path

# Import API endpoints (already refactored with Type Hints)
from .api import (
    get_item_allowed_units,
    get_item_units,
    get_filtered_categories,
    get_filtered_subcategories,
    get_filtered_items,
    get_item_allowed_warehouses,
    get_item_available_serials,
    update_serial_secondary_code,
    get_temporary_receipt_data,
    get_warehouse_work_lines,
)

# Import base classes (already refactored with Type Hints)
from .base import (
    InventoryBaseView,
    DocumentLockProtectedMixin,
    DocumentLockView,
    DocumentUnlockView,
    LineFormsetMixin,
    ItemUnitFormsetMixin,
)

# Import request views (already refactored with Type Hints)
from .requests import (
    # Purchase Requests
    PurchaseRequestFormMixin,
    PurchaseRequestListView,
    PurchaseRequestCreateView,
    PurchaseRequestUpdateView,
    PurchaseRequestApproveView,
    CreateTemporaryReceiptFromPurchaseRequestView,
    CreatePermanentReceiptFromPurchaseRequestView,
    CreateConsignmentReceiptFromPurchaseRequestView,
    # Warehouse Requests
    WarehouseRequestFormMixin,
    WarehouseRequestListView,
    WarehouseRequestCreateView,
    WarehouseRequestUpdateView,
    WarehouseRequestApproveView,
)

# Import receipt views (already refactored with Type Hints)
from .receipts import (
    # Base
    DocumentDeleteViewBase,
    ReceiptFormMixin,
    # Temporary Receipts
    ReceiptTemporaryListView,
    ReceiptTemporaryCreateView,
    ReceiptTemporaryCreateFromPurchaseRequestView,
    ReceiptTemporaryDetailView,
    ReceiptTemporaryUpdateView,
    ReceiptTemporaryDeleteView,
    ReceiptTemporaryLockView,
    ReceiptTemporaryUnlockView,
    ReceiptTemporarySendToQCView,
    # Permanent Receipts
    ReceiptPermanentListView,
    ReceiptPermanentCreateView,
    ReceiptPermanentCreateFromPurchaseRequestView,
    ReceiptPermanentUpdateView,
    ReceiptPermanentDeleteView,
    ReceiptPermanentLockView,
    ReceiptPermanentUnlockView,
    ReceiptPermanentSerialAssignmentView,
    ReceiptPermanentLineSerialAssignmentView,
    # Consignment Receipts
    ReceiptConsignmentListView,
    ReceiptConsignmentCreateView,
    ReceiptConsignmentCreateFromPurchaseRequestView,
    ReceiptConsignmentUpdateView,
    ReceiptConsignmentDeleteView,
    ReceiptConsignmentLockView,
    ReceiptConsignmentUnlockView,
    ReceiptConsignmentSerialAssignmentView,
    ReceiptConsignmentLineSerialAssignmentView,
)

# Import issue views (already refactored with Type Hints)
from .issues import (
    # Permanent Issues
    IssuePermanentListView,
    IssuePermanentCreateView,
    IssuePermanentUpdateView,
    IssuePermanentDeleteView,
    IssuePermanentLockView,
    IssuePermanentLineSerialAssignmentView,
    # Consumption Issues
    IssueConsumptionListView,
    IssueConsumptionCreateView,
    IssueConsumptionUpdateView,
    IssueConsumptionDeleteView,
    IssueConsumptionLockView,
    IssueConsumptionLineSerialAssignmentView,
    # Consignment Issues
    IssueConsignmentListView,
    IssueConsignmentCreateView,
    IssueConsignmentUpdateView,
    IssueConsignmentDeleteView,
    IssueConsignmentLockView,
    IssueConsignmentLineSerialAssignmentView,
)

# Import issue views from warehouse request (intermediate selection views)
from .create_issue_from_warehouse_request import (
    CreatePermanentIssueFromWarehouseRequestView,
    CreateConsumptionIssueFromWarehouseRequestView,
    CreateConsignmentIssueFromWarehouseRequestView,
)
# Import issue views from warehouse request (actual creation views)
from .issues_from_warehouse_request import (
    IssuePermanentCreateFromWarehouseRequestView,
    IssueConsumptionCreateFromWarehouseRequestView,
    IssueConsignmentCreateFromWarehouseRequestView,
)

# Import stocktaking views (already refactored with Type Hints)
from .stocktaking import (
    StocktakingFormMixin,
    # Deficit
    StocktakingDeficitListView,
    StocktakingDeficitCreateView,
    StocktakingDeficitUpdateView,
    StocktakingDeficitDeleteView,
    StocktakingDeficitLockView,
    # Surplus
    StocktakingSurplusListView,
    StocktakingSurplusCreateView,
    StocktakingSurplusUpdateView,
    StocktakingSurplusDeleteView,
    StocktakingSurplusLockView,
    # Record
    StocktakingRecordListView,
    StocktakingRecordCreateView,
    StocktakingRecordUpdateView,
    StocktakingRecordDeleteView,
    StocktakingRecordLockView,
)

# Import balance views (already refactored with Type Hints)
from .balance import (
    InventoryBalanceView,
    InventoryBalanceDetailsView,
    InventoryBalanceAPIView,
)

# Import master data views (already refactored with Type Hints)
from .master_data import (
    # Item Types
    ItemTypeListView,
    ItemTypeCreateView,
    ItemTypeUpdateView,
    ItemTypeDeleteView,
    # Item Categories
    ItemCategoryListView,
    ItemCategoryCreateView,
    ItemCategoryUpdateView,
    ItemCategoryDeleteView,
    # Item Subcategories
    ItemSubcategoryListView,
    ItemSubcategoryCreateView,
    ItemSubcategoryUpdateView,
    ItemSubcategoryDeleteView,
    # Items
    ItemListView,
    ItemSerialListView,
    ItemCreateView,
    ItemUpdateView,
    ItemDeleteView,
)

# Import item import/export views
from .item_import import (
    ItemExcelTemplateDownloadView,
    ItemExcelImportView,
)

# Import remaining master data views
from .master_data import (
    # Warehouses
    WarehouseListView,
    WarehouseCreateView,
    WarehouseUpdateView,
    WarehouseDeleteView,
    # Supplier Categories
    SupplierCategoryListView,
    SupplierCategoryCreateView,
    SupplierCategoryUpdateView,
    SupplierCategoryDeleteView,
    # Suppliers
    SupplierListView,
    SupplierCreateView,
    SupplierUpdateView,
    SupplierDeleteView,
)

__all__ = [
    # Base (refactored)
    'InventoryBaseView',
    'DocumentLockProtectedMixin',
    'DocumentLockView',
    'DocumentUnlockView',
    'LineFormsetMixin',
    'ItemUnitFormsetMixin',
    # Requests (refactored)
    'PurchaseRequestFormMixin',
    'PurchaseRequestListView',
    'PurchaseRequestCreateView',
    'PurchaseRequestUpdateView',
    'PurchaseRequestApproveView',
    'CreateTemporaryReceiptFromPurchaseRequestView',
    'CreatePermanentReceiptFromPurchaseRequestView',
    'CreateConsignmentReceiptFromPurchaseRequestView',
    'WarehouseRequestFormMixin',
    'WarehouseRequestListView',
    'WarehouseRequestCreateView',
    'WarehouseRequestUpdateView',
    'WarehouseRequestApproveView',
    # Receipts (refactored)
    'DocumentDeleteViewBase',
    'ReceiptFormMixin',
    'ReceiptTemporaryListView',
    'ReceiptTemporaryCreateView',
    'ReceiptTemporaryCreateFromPurchaseRequestView',
    'ReceiptTemporaryDetailView',
    'ReceiptTemporaryUpdateView',
    'ReceiptTemporaryDeleteView',
    'ReceiptTemporaryLockView',
    'ReceiptTemporaryUnlockView',
    'ReceiptTemporarySendToQCView',
    'ReceiptPermanentListView',
    'ReceiptPermanentCreateView',
    'ReceiptPermanentCreateFromPurchaseRequestView',
    'ReceiptPermanentUpdateView',
    'ReceiptPermanentDeleteView',
    'ReceiptPermanentLockView',
    'ReceiptPermanentUnlockView',
    'ReceiptPermanentSerialAssignmentView',
    'ReceiptPermanentLineSerialAssignmentView',
    'ReceiptConsignmentListView',
    'ReceiptConsignmentCreateView',
    'ReceiptConsignmentCreateFromPurchaseRequestView',
    'ReceiptConsignmentUpdateView',
    'ReceiptConsignmentDeleteView',
    'ReceiptConsignmentLockView',
    'ReceiptConsignmentUnlockView',
    'ReceiptConsignmentSerialAssignmentView',
    'ReceiptConsignmentLineSerialAssignmentView',
    # Issues (refactored)
    'IssuePermanentListView',
    'IssuePermanentCreateView',
    'IssuePermanentUpdateView',
    'IssuePermanentDeleteView',
    'IssuePermanentLockView',
    'IssuePermanentLineSerialAssignmentView',
    'IssueConsumptionListView',
    'IssueConsumptionCreateView',
    'IssueConsumptionUpdateView',
    'IssueConsumptionDeleteView',
    'IssueConsumptionLockView',
    'IssueConsumptionLineSerialAssignmentView',
    'IssueConsignmentListView',
    'IssueConsignmentCreateView',
    'IssueConsignmentUpdateView',
    'IssueConsignmentDeleteView',
    'IssueConsignmentLockView',
    'IssueConsignmentLineSerialAssignmentView',
    # Issues from Warehouse Request (intermediate selection)
    'CreatePermanentIssueFromWarehouseRequestView',
    'CreateConsumptionIssueFromWarehouseRequestView',
    'CreateConsignmentIssueFromWarehouseRequestView',
    # Issues from Warehouse Request (creation)
    'IssuePermanentCreateFromWarehouseRequestView',
    'IssueConsumptionCreateFromWarehouseRequestView',
    'IssueConsignmentCreateFromWarehouseRequestView',
    # Stocktaking (refactored)
    'StocktakingFormMixin',
    'StocktakingDeficitListView',
    'StocktakingDeficitCreateView',
    'StocktakingDeficitUpdateView',
    'StocktakingDeficitDeleteView',
    'StocktakingDeficitLockView',
    'StocktakingSurplusListView',
    'StocktakingSurplusCreateView',
    'StocktakingSurplusUpdateView',
    'StocktakingSurplusDeleteView',
    'StocktakingSurplusLockView',
    'StocktakingRecordListView',
    'StocktakingRecordCreateView',
    'StocktakingRecordUpdateView',
    'StocktakingRecordDeleteView',
    'StocktakingRecordLockView',
    # Balance (refactored)
    'InventoryBalanceView',
    'InventoryBalanceDetailsView',
    'InventoryBalanceAPIView',
    # API (refactored)
    'get_item_allowed_units',
    'get_item_units',
    'get_filtered_categories',
    'get_filtered_subcategories',
    'get_filtered_items',
    'get_item_allowed_warehouses',
    'get_item_available_serials',
    'update_serial_secondary_code',
    'get_temporary_receipt_data',
    'get_warehouse_work_lines',
    # Master Data (refactored)
    'ItemTypeListView',
    'ItemTypeCreateView',
    'ItemTypeUpdateView',
    'ItemTypeDeleteView',
    'ItemCategoryListView',
    'ItemCategoryCreateView',
    'ItemCategoryUpdateView',
    'ItemCategoryDeleteView',
    'ItemSubcategoryListView',
    'ItemSubcategoryCreateView',
    'ItemSubcategoryUpdateView',
    'ItemSubcategoryDeleteView',
    'ItemListView',
    'ItemSerialListView',
    'ItemCreateView',
    'ItemUpdateView',
    'ItemDeleteView',
    'ItemExcelTemplateDownloadView',
    'ItemExcelImportView',
    'WarehouseListView',
    'WarehouseCreateView',
    'WarehouseUpdateView',
    'WarehouseDeleteView',
    'SupplierCategoryListView',
    'SupplierCategoryCreateView',
    'SupplierCategoryUpdateView',
    'SupplierCategoryDeleteView',
    'SupplierListView',
    'SupplierCreateView',
    'SupplierUpdateView',
    'SupplierDeleteView',
]

# Import remaining views from inventory/views.py (parent directory)
# This is necessary because Python prioritizes packages over modules with the same name
_inventory_dir = Path(__file__).parent.parent
_views_py_path = _inventory_dir / 'views.py'

if _views_py_path.exists():
    spec = importlib.util.spec_from_file_location("inventory.views_module", _views_py_path)
    views_module = importlib.util.module_from_spec(spec)
    sys.modules['inventory.views_module'] = views_module
    spec.loader.exec_module(views_module)
    
    # Import all views from views.py (except those already imported from refactored modules)
    _exclude = {
        'InventoryBaseView', 'DocumentLockProtectedMixin', 'DocumentLockView',
        'LineFormsetMixin', 'ItemUnitFormsetMixin',
        'ItemTypeListView', 'ItemTypeCreateView', 'ItemTypeUpdateView', 'ItemTypeDeleteView',
        'ItemCategoryListView', 'ItemCategoryCreateView', 'ItemCategoryUpdateView', 'ItemCategoryDeleteView',
        'ItemSubcategoryListView', 'ItemSubcategoryCreateView', 'ItemSubcategoryUpdateView', 'ItemSubcategoryDeleteView',
        'ItemListView', 'ItemSerialListView', 'ItemCreateView', 'ItemUpdateView', 'ItemDeleteView',
        'WarehouseListView', 'WarehouseCreateView', 'WarehouseUpdateView', 'WarehouseDeleteView',
        'SupplierCategoryListView', 'SupplierCategoryCreateView', 'SupplierCategoryUpdateView', 'SupplierCategoryDeleteView',
        'SupplierListView', 'SupplierCreateView', 'SupplierUpdateView', 'SupplierDeleteView',
        'PurchaseRequestFormMixin', 'PurchaseRequestListView', 'PurchaseRequestCreateView',
        'PurchaseRequestUpdateView', 'PurchaseRequestApproveView',
        'WarehouseRequestFormMixin', 'WarehouseRequestListView', 'WarehouseRequestCreateView',
        'WarehouseRequestUpdateView', 'WarehouseRequestApproveView',
        'DocumentDeleteViewBase', 'ReceiptFormMixin',
        'ReceiptTemporaryListView', 'ReceiptTemporaryCreateView', 'ReceiptTemporaryDetailView', 'ReceiptTemporaryUpdateView',
        'ReceiptTemporaryDeleteView', 'ReceiptTemporaryLockView', 'ReceiptTemporaryUnlockView', 'ReceiptTemporarySendToQCView',
        'ReceiptPermanentListView', 'ReceiptPermanentCreateView', 'ReceiptPermanentUpdateView',
        'ReceiptPermanentDeleteView', 'ReceiptPermanentLockView', 'ReceiptPermanentUnlockView',
        'ReceiptPermanentSerialAssignmentView', 'ReceiptPermanentLineSerialAssignmentView',
        'ReceiptConsignmentListView', 'ReceiptConsignmentCreateView', 'ReceiptConsignmentUpdateView',
        'ReceiptConsignmentDeleteView', 'ReceiptConsignmentLockView', 'ReceiptConsignmentUnlockView',
        'ReceiptConsignmentSerialAssignmentView', 'ReceiptConsignmentLineSerialAssignmentView',
        'IssuePermanentListView', 'IssuePermanentCreateView', 'IssuePermanentUpdateView',
        'IssuePermanentDeleteView', 'IssuePermanentLockView', 'IssuePermanentLineSerialAssignmentView',
        'IssueConsumptionListView', 'IssueConsumptionCreateView', 'IssueConsumptionUpdateView',
        'IssueConsumptionDeleteView', 'IssueConsumptionLockView', 'IssueConsumptionLineSerialAssignmentView',
        'IssueConsignmentListView', 'IssueConsignmentCreateView', 'IssueConsignmentUpdateView',
        'IssueConsignmentDeleteView', 'IssueConsignmentLockView', 'IssueConsignmentLineSerialAssignmentView',
        'StocktakingFormMixin',
        'StocktakingDeficitListView', 'StocktakingDeficitCreateView', 'StocktakingDeficitUpdateView',
        'StocktakingDeficitDeleteView', 'StocktakingDeficitLockView',
        'StocktakingSurplusListView', 'StocktakingSurplusCreateView', 'StocktakingSurplusUpdateView',
        'StocktakingSurplusDeleteView', 'StocktakingSurplusLockView',
        'StocktakingRecordListView', 'StocktakingRecordCreateView', 'StocktakingRecordUpdateView',
        'StocktakingRecordDeleteView', 'StocktakingRecordLockView',
        'InventoryBalanceView', 'InventoryBalanceDetailsView', 'InventoryBalanceAPIView',
    }
    
    # Import all public classes from views_module
    _imported_views = []
    for name in dir(views_module):
        if not name.startswith('_') and name not in _exclude:
            obj = getattr(views_module, name)
            if isinstance(obj, type) and hasattr(obj, '__module__'):
                setattr(sys.modules[__name__], name, obj)
                _imported_views.append(name)
    
    # Add imported views to __all__
    __all__.extend(_imported_views)

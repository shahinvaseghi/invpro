"""
Forms package for inventory module.

This package contains all forms for the inventory module, organized by functionality:
- base.py: Base forms and helper functions
- master_data.py: Master data forms (Item, Type, Category, etc.)
- request.py: Request forms (Purchase, Warehouse)
- receipt.py: Receipt forms (Temporary, Permanent, Consignment)
- issue.py: Issue forms (Permanent, Consumption, Consignment)
- stocktaking.py: Stocktaking forms (Deficit, Surplus, Record)

NOTE: During refactoring, some forms are still in inventory/forms.py (legacy file).
This __init__.py imports from both the package and the legacy file for backward compatibility.
"""
__all__ = []

# Import base forms and helpers from package
from inventory.forms.base import (
    UNIT_CHOICES,
    get_purchase_request_approvers,
    generate_document_code,
    get_feature_approvers,
    ReceiptBaseForm,
    IssueBaseForm,
    StocktakingBaseForm,
)

__all__.extend([
    'UNIT_CHOICES',
    'get_purchase_request_approvers',
    'generate_document_code',
    'get_feature_approvers',
    'ReceiptBaseForm',
    'IssueBaseForm',
    'StocktakingBaseForm',
])

# Import master data forms
from inventory.forms.master_data import (
    ItemTypeForm,
    ItemCategoryForm,
    ItemSubcategoryForm,
    WarehouseForm,
    SupplierForm,
    SupplierCategoryForm,
    ItemForm,
    ItemUnitForm,
    ItemUnitFormSet,
)

__all__.extend([
    'ItemTypeForm',
    'ItemCategoryForm',
    'ItemSubcategoryForm',
    'WarehouseForm',
    'SupplierForm',
    'SupplierCategoryForm',
    'ItemForm',
    'ItemUnitForm',
    'ItemUnitFormSet',
])

# Import request forms
from inventory.forms.request import (
    PurchaseRequestForm,
    PurchaseRequestLineForm,
    PurchaseRequestLineFormSet,
    WarehouseRequestForm,
    WarehouseRequestLineForm,
    WarehouseRequestLineFormSet,
)

__all__.extend([
    'PurchaseRequestForm',
    'PurchaseRequestLineForm',
    'PurchaseRequestLineFormSet',
    'WarehouseRequestForm',
    'WarehouseRequestLineForm',
    'WarehouseRequestLineFormSet',
])

# Import receipt forms
from inventory.forms.receipt import (
    ReceiptTemporaryForm,
    ReceiptTemporaryLineForm,
    ReceiptTemporaryLineFormSet,
    ReceiptPermanentForm,
    ReceiptConsignmentForm,
    ReceiptLineBaseForm,
    ReceiptPermanentLineForm,
    ReceiptConsignmentLineForm,
    ReceiptPermanentLineFormSet,
    ReceiptConsignmentLineFormSet,
)

__all__.extend([
    'ReceiptTemporaryForm',
    'ReceiptTemporaryLineForm',
    'ReceiptTemporaryLineFormSet',
    'ReceiptPermanentForm',
    'ReceiptConsignmentForm',
    'ReceiptLineBaseForm',
    'ReceiptPermanentLineForm',
    'ReceiptConsignmentLineForm',
    'ReceiptPermanentLineFormSet',
    'ReceiptConsignmentLineFormSet',
])

# Import issue forms
from inventory.forms.issue import (
    IssuePermanentForm,
    IssueConsumptionForm,
    IssueConsignmentForm,
    IssueLineSerialAssignmentForm,
    IssueLineBaseForm,
    IssuePermanentLineForm,
    IssueConsumptionLineForm,
    IssueConsignmentLineForm,
    IssuePermanentLineFormSet,
    IssueConsumptionLineFormSet,
    IssueConsignmentLineFormSet,
)

__all__.extend([
    'IssuePermanentForm',
    'IssueConsumptionForm',
    'IssueConsignmentForm',
    'IssueLineSerialAssignmentForm',
    'IssueLineBaseForm',
    'IssuePermanentLineForm',
    'IssueConsumptionLineForm',
    'IssueConsignmentLineForm',
    'IssuePermanentLineFormSet',
    'IssueConsumptionLineFormSet',
    'IssueConsignmentLineFormSet',
])

# Import stocktaking forms
from inventory.forms.stocktaking import (
    StocktakingDeficitForm,
    StocktakingSurplusForm,
    StocktakingRecordForm,
)

__all__.extend([
    'StocktakingDeficitForm',
    'StocktakingSurplusForm',
    'StocktakingRecordForm',
])

# All forms have been moved to package files
# No legacy imports needed

"""
Centralised permission definitions for the application.

These structures will be consumed by the upcoming access level / role engine.
Until persistence is implemented, this module documents the expected actions
per feature and can be reused in fixtures, forms or serializers later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Dict, List

from django.utils.translation import gettext_lazy as _


@unique
class PermissionAction(Enum):
    """
    Supported primitive actions that can be attached to an access level.
    """

    VIEW_OWN = "view_own"
    VIEW_ALL = "view_all"
    CREATE = "create"
    EDIT_OWN = "edit_own"
    EDIT_OTHER = "edit_other"
    DELETE_OWN = "delete_own"
    DELETE_OTHER = "delete_other"
    LOCK_OWN = "lock_own"
    LOCK_OTHER = "lock_other"
    UNLOCK_OWN = "unlock_own"
    UNLOCK_OTHER = "unlock_other"
    APPROVE = "approve"
    REJECT = "reject"
    CANCEL = "cancel"
    CREATE_TRANSFER_FROM_ORDER = "create_transfer_from_order"
    CREATE_RECEIPT = "create_receipt"
    CREATE_RECEIPT_FROM_PURCHASE_REQUEST = "create_receipt_from_purchase_request"
    CREATE_ISSUE_FROM_WAREHOUSE_REQUEST = "create_issue_from_warehouse_request"


@dataclass(frozen=True)
class FeaturePermission:
    """
    Describes a navigational feature together with the actions it supports.
    """

    code: str
    label: str
    actions: List[PermissionAction] = field(default_factory=list)


FEATURE_PERMISSION_MAP: Dict[str, FeaturePermission] = {
    # Shared – Company & User Management
    "shared.companies": FeaturePermission(
        code="shared.companies",
        label=_("Companies"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "shared.company_units": FeaturePermission(
        code="shared.company_units",
        label=_("Company Units"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "shared.smtp_servers": FeaturePermission(
        code="shared.smtp_servers",
        label=_("SMTP Servers"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "production.personnel": FeaturePermission(
        code="production.personnel",
        label=_("Personnel"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "production.machines": FeaturePermission(
        code="production.machines",
        label=_("Machines"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "production.bom": FeaturePermission(
        code="production.bom",
        label=_("BOM (Bill of Materials)"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "production.processes": FeaturePermission(
        code="production.processes",
        label=_("Processes"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
        ],
    ),
    "production.product_orders": FeaturePermission(
        code="production.product_orders",
        label=_("Product Orders"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.CREATE_TRANSFER_FROM_ORDER,
        ],
    ),
    "production.transfer_requests": FeaturePermission(
        code="production.transfer_requests",
        label=_("Transfer to Line Requests"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "production.transfer_requests.qc_approval": FeaturePermission(
        code="production.transfer_requests.qc_approval",
        label=_("QC Approval for Transfer to Line Requests"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "production.performance_records": FeaturePermission(
        code="production.performance_records",
        label=_("Performance Records"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.EDIT_OTHER,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CREATE_RECEIPT,
        ],
    ),
    "production.tracking_identification": FeaturePermission(
        code="production.tracking_identification",
        label=_("Tracking and Identification"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    "shared.users": FeaturePermission(
        code="shared.users",
        label=_("Users"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "shared.groups": FeaturePermission(
        code="shared.groups",
        label=_("Groups"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "shared.access_levels": FeaturePermission(
        code="shared.access_levels",
        label=_("Access Levels"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
        ],
    ),
    # Inventory – Master Data
    "inventory.master.item_types": FeaturePermission(
        code="inventory.master.item_types",
        label=_("Item Types"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "inventory.master.item_categories": FeaturePermission(
        code="inventory.master.item_categories",
        label=_("Item Categories"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "inventory.master.item_subcategories": FeaturePermission(
        code="inventory.master.item_subcategories",
        label=_("Item Subcategories"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "inventory.master.items": FeaturePermission(
        code="inventory.master.items",
        label=_("Items"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "inventory.master.item_serials": FeaturePermission(
        code="inventory.master.item_serials",
        label=_("Item Serials"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    "inventory.master.warehouses": FeaturePermission(
        code="inventory.master.warehouses",
        label=_("Warehouses"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "production.work_lines": FeaturePermission(
        code="production.work_lines",
        label=_("Work Lines"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Inventory – Suppliers
    "inventory.suppliers.categories": FeaturePermission(
        code="inventory.suppliers.categories",
        label=_("Supplier Categories"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "inventory.suppliers.list": FeaturePermission(
        code="inventory.suppliers.list",
        label=_("Suppliers"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Inventory – Receipts
    "inventory.receipts.temporary": FeaturePermission(
        code="inventory.receipts.temporary",
        label=_("Temporary Receipts"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_RECEIPT_FROM_PURCHASE_REQUEST,
        ],
    ),
    "inventory.receipts.permanent": FeaturePermission(
        code="inventory.receipts.permanent",
        label=_("Permanent Receipts"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_RECEIPT_FROM_PURCHASE_REQUEST,
        ],
    ),
    "inventory.receipts.consignment": FeaturePermission(
        code="inventory.receipts.consignment",
        label=_("Consignment Receipts"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_RECEIPT_FROM_PURCHASE_REQUEST,
        ],
    ),
    # Inventory – Issues
    "inventory.issues.permanent": FeaturePermission(
        code="inventory.issues.permanent",
        label=_("Permanent Issues"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_ISSUE_FROM_WAREHOUSE_REQUEST,
        ],
    ),
    "inventory.issues.consumption": FeaturePermission(
        code="inventory.issues.consumption",
        label=_("Consumption Issues"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_ISSUE_FROM_WAREHOUSE_REQUEST,
        ],
    ),
    "inventory.issues.consignment": FeaturePermission(
        code="inventory.issues.consignment",
        label=_("Consignment Issues"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_ISSUE_FROM_WAREHOUSE_REQUEST,
        ],
    ),
    # Inventory – Requests
    "inventory.requests.purchase": FeaturePermission(
        code="inventory.requests.purchase",
        label=_("Purchase Requests"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_RECEIPT_FROM_PURCHASE_REQUEST,
        ],
    ),
    "inventory.requests.warehouse": FeaturePermission(
        code="inventory.requests.warehouse",
        label=_("Warehouse Requests"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
            PermissionAction.CREATE_ISSUE_FROM_WAREHOUSE_REQUEST,
        ],
    ),
    # Inventory – Stocktaking & Balance
    "inventory.stocktaking.deficit": FeaturePermission(
        code="inventory.stocktaking.deficit",
        label=_("Stocktaking Deficit"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
        ],
    ),
    "inventory.stocktaking.surplus": FeaturePermission(
        code="inventory.stocktaking.surplus",
        label=_("Stocktaking Surplus"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
        ],
    ),
    "inventory.stocktaking.records": FeaturePermission(
        code="inventory.stocktaking.records",
        label=_("Stocktaking Records"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.DELETE_OTHER,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
        ],
    ),
    "inventory.balance": FeaturePermission(
        code="inventory.balance",
        label=_("Inventory Balance"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    # QC – Inspections
    "qc.inspections": FeaturePermission(
        code="qc.inspections",
        label=_("QC Inspections"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
        ],
    ),
    # Accounting – Dashboard
    "accounting.dashboard": FeaturePermission(
        code="accounting.dashboard",
        label=_("Accounting Dashboard"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    # Accounting – Fiscal Years
    "accounting.fiscal_years": FeaturePermission(
        code="accounting.fiscal_years",
        label=_("Fiscal Years"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Accounting – Chart of Accounts
    "accounting.accounts": FeaturePermission(
        code="accounting.accounts",
        label=_("Chart of Accounts"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.accounts.gl": FeaturePermission(
        code="accounting.accounts.gl",
        label=_("GL Accounts (حساب کل)"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.accounts.sub": FeaturePermission(
        code="accounting.accounts.sub",
        label=_("Sub Accounts (حساب معین)"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.accounts.tafsili": FeaturePermission(
        code="accounting.accounts.tafsili",
        label=_("Tafsili Accounts (حساب تفصیلی)"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.accounts.tafsili_hierarchy": FeaturePermission(
        code="accounting.accounts.tafsili_hierarchy",
        label=_("Tafsili Hierarchy (تفصیلی چند سطحی)"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.attachments.upload": FeaturePermission(
        code="accounting.attachments.upload",
        label=_("Document Attachments Upload"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
        ],
    ),
    "accounting.attachments.list": FeaturePermission(
        code="accounting.attachments.list",
        label=_("Document Attachments List"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    "accounting.attachments.download": FeaturePermission(
        code="accounting.attachments.download",
        label=_("Document Attachments Download"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    # Accounting – General
    "accounting.general.ledger": FeaturePermission(
        code="accounting.general.ledger",
        label=_("General Ledger"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.general.subsidiary": FeaturePermission(
        code="accounting.general.subsidiary",
        label=_("Subsidiary Ledgers"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.general.detail": FeaturePermission(
        code="accounting.general.detail",
        label=_("Detail Ledgers"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Accounting – Documents
    "accounting.documents.entry": FeaturePermission(
        code="accounting.documents.entry",
        label=_("Entry Document"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
        ],
    ),
    "accounting.documents.exit": FeaturePermission(
        code="accounting.documents.exit",
        label=_("Exit Document"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
        ],
    ),
    # Accounting – Treasury
    "accounting.treasury.expense": FeaturePermission(
        code="accounting.treasury.expense",
        label=_("Expense Document"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "accounting.treasury.income": FeaturePermission(
        code="accounting.treasury.income",
        label=_("Income Document"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    # Accounting – Payroll
    "accounting.payroll.payment": FeaturePermission(
        code="accounting.payroll.payment",
        label=_("Payroll Payment"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.payroll.insurance_tax": FeaturePermission(
        code="accounting.payroll.insurance_tax",
        label=_("Insurance and Tax Settings"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "accounting.payroll.document": FeaturePermission(
        code="accounting.payroll.document",
        label=_("Payroll Document Upload"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "accounting.payroll.bank_transfer": FeaturePermission(
        code="accounting.payroll.bank_transfer",
        label=_("Bank Transfer Output"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Sales
    "sales.dashboard": FeaturePermission(
        code="sales.dashboard",
        label=_("Sales Dashboard"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    "sales.invoice": FeaturePermission(
        code="sales.invoice",
        label=_("Sales Invoice"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    # HR – Dashboard
    "hr.dashboard": FeaturePermission(
        code="hr.dashboard",
        label=_("HR Dashboard"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    # HR – Personnel
    "hr.personnel": FeaturePermission(
        code="hr.personnel",
        label=_("Personnel"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "hr.personnel.decree": FeaturePermission(
        code="hr.personnel.decree",
        label=_("Personnel Decree Assignment"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.EDIT_OWN,
            PermissionAction.EDIT_OTHER,
        ],
    ),
    "hr.personnel.form": FeaturePermission(
        code="hr.personnel.form",
        label=_("Personnel Forms"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "hr.personnel.form_groups": FeaturePermission(
        code="hr.personnel.form_groups",
        label=_("Personnel Form Groups"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "hr.personnel.form_subgroups": FeaturePermission(
        code="hr.personnel.form_subgroups",
        label=_("Personnel Form Sub-Groups"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # HR - Payroll Decrees
    "hr.payroll.decrees": FeaturePermission(
        code="hr.payroll.decrees",
        label=_("Payroll Decrees"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "hr.payroll.decree_groups": FeaturePermission(
        code="hr.payroll.decree_groups",
        label=_("Decree Groups"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "hr.payroll.decree_subgroups": FeaturePermission(
        code="hr.payroll.decree_subgroups",
        label=_("Decree Sub-Groups"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # HR – Requests
    "hr.requests.leave": FeaturePermission(
        code="hr.requests.leave",
        label=_("Leave Requests"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "hr.requests.sick_leave": FeaturePermission(
        code="hr.requests.sick_leave",
        label=_("Sick Leave Requests"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "hr.requests.loan": FeaturePermission(
        code="hr.requests.loan",
        label=_("Loan Requests"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    # HR – Loans
    "hr.loans.management": FeaturePermission(
        code="hr.loans.management",
        label=_("Loan Management"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "hr.loans.scheduling": FeaturePermission(
        code="hr.loans.scheduling",
        label=_("Loan Scheduling"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "hr.loans.savings_fund": FeaturePermission(
        code="hr.loans.savings_fund",
        label=_("Savings Fund"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Office Automation – Dashboard
    "office_automation.dashboard": FeaturePermission(
        code="office_automation.dashboard",
        label=_("Office Automation Dashboard"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    # Office Automation – Inbox
    "office_automation.inbox.incoming": FeaturePermission(
        code="office_automation.inbox.incoming",
        label=_("Incoming Letters"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.EDIT_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    "office_automation.inbox.write": FeaturePermission(
        code="office_automation.inbox.write",
        label=_("Write Letter"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
        ],
    ),
    "office_automation.inbox.fill_form": FeaturePermission(
        code="office_automation.inbox.fill_form",
        label=_("Fill Form"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
        ],
    ),
    # Office Automation – Processes
    "office_automation.processes.engine": FeaturePermission(
        code="office_automation.processes.engine",
        label=_("Process Engine"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "office_automation.processes.form_connection": FeaturePermission(
        code="office_automation.processes.form_connection",
        label=_("Process-Form Connection"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Office Automation – Forms
    "office_automation.forms.builder": FeaturePermission(
        code="office_automation.forms.builder",
        label=_("Form Builder"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Transportation
    "transportation.dashboard": FeaturePermission(
        code="transportation.dashboard",
        label=_("Transportation Dashboard"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    # Procurement – Dashboard
    "procurement.dashboard": FeaturePermission(
        code="procurement.dashboard",
        label=_("Procurement Dashboard"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
        ],
    ),
    # Procurement – Purchases
    "procurement.purchases": FeaturePermission(
        code="procurement.purchases",
        label=_("Purchases"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
        ],
    ),
    # Procurement – Buyers
    "procurement.buyers": FeaturePermission(
        code="procurement.buyers",
        label=_("Buyers"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    # Ticketing – Management
    "ticketing.management.categories": FeaturePermission(
        code="ticketing.management.categories",
        label=_("Ticket Categories"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "ticketing.management.subcategories": FeaturePermission(
        code="ticketing.management.subcategories",
        label=_("Ticket Subcategories"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
    "ticketing.management.templates": FeaturePermission(
        code="ticketing.management.templates",
        label=_("Ticket Templates"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
        ],
    ),
}


def list_feature_permissions() -> List[FeaturePermission]:
    """
    Convenience helper for iterating over defined permissions (e.g. in forms).
    """

    return list(FEATURE_PERMISSION_MAP.values())


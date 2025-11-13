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
    DELETE_OWN = "delete_own"
    LOCK_OWN = "lock_own"
    LOCK_OTHER = "lock_other"
    UNLOCK_OWN = "unlock_own"
    UNLOCK_OTHER = "unlock_other"
    APPROVE = "approve"
    REJECT = "reject"
    CANCEL = "cancel"


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
    "shared.personnel": FeaturePermission(
        code="shared.personnel",
        label=_("Personnel"),
        actions=[
            PermissionAction.VIEW_OWN,
            PermissionAction.VIEW_ALL,
            PermissionAction.CREATE,
            PermissionAction.EDIT_OWN,
            PermissionAction.DELETE_OWN,
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
    "inventory.master.work_lines": FeaturePermission(
        code="inventory.master.work_lines",
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
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.CANCEL,
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
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
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
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
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
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
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
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.CANCEL,
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
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
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
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
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
            PermissionAction.APPROVE,
            PermissionAction.REJECT,
            PermissionAction.CANCEL,
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
            PermissionAction.LOCK_OWN,
            PermissionAction.LOCK_OTHER,
            PermissionAction.UNLOCK_OWN,
            PermissionAction.UNLOCK_OTHER,
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
}


def list_feature_permissions() -> List[FeaturePermission]:
    """
    Convenience helper for iterating over defined permissions (e.g. in forms).
    """

    return list(FEATURE_PERMISSION_MAP.values())


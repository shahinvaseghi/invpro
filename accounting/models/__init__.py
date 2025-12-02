"""
Models for accounting module.
All models are imported here for backward compatibility with existing code.
"""
# Base classes
from .base import (
    AccountingBaseModel,
    FiscalYearMixin,
    AccountingSortableModel,
    AccountingDocumentBase,
    POSITIVE_DECIMAL,
    get_fiscal_year_from_date,
)

# Fiscal Years
from .fiscal_years import FiscalYear, Period

# Accounts
from .accounts import (
    Account,
    SubAccountGLAccountRelation,
    TafsiliSubAccountRelation,
)

# Hierarchy
from .hierarchy import TafsiliHierarchy

# Documents
from .documents import (
    AccountingDocument,
    AccountingDocumentLine,
)

# Attachments
from .attachments import DocumentAttachment

# Balances
from .balances import AccountBalance

# Cost Centers
from .cost_centers import CostCenter

# Income/Expense Categories
from .income_expense_categories import IncomeExpenseCategory

# Parties
from .parties import Party, PartyAccount

# Export all models for backward compatibility
__all__ = [
    # Base
    'AccountingBaseModel',
    'FiscalYearMixin',
    'AccountingSortableModel',
    'AccountingDocumentBase',
    'POSITIVE_DECIMAL',
    'get_fiscal_year_from_date',
    # Fiscal Years
    'FiscalYear',
    'Period',
    # Accounts
    'Account',
    'SubAccountGLAccountRelation',
    'TafsiliSubAccountRelation',
    # Hierarchy
    'TafsiliHierarchy',
    # Documents
    'AccountingDocument',
    'AccountingDocumentLine',
    # Attachments
    'DocumentAttachment',
    # Balances
    'AccountBalance',
    # Cost Centers
    'CostCenter',
    # Income/Expense Categories
    'IncomeExpenseCategory',
    # Parties
    'Party',
    'PartyAccount',
]


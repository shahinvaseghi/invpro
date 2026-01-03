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
    AccountGroup,
    Account,
    SubAccountGLAccountRelation,
    TafsiliSubAccountRelation,
)

# Tafsili Types
from .tafsili_types import TafsiliType

# Hierarchy
from .hierarchy import TafsiliHierarchy, TafsiliLevelSubAccountRelation

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

# Treasury Accounts
from .treasury_accounts import TreasuryAccount

# Payment Requests
from .payment_requests import PaymentRequest

# Warehouse Accounting
from .warehouse import (
    WarehouseExpenseDocument,
    WarehouseExpenseDocumentLine,
    WarehouseIncomeDocument,
)

# Taxpayer System
from .taxpayer_system import (
    FiscalMemoryConfig,
    TaxInvoiceSubmission,
    TaxInvoiceSubmissionLog,
)

# Automation
from .automation import (
    AutomationProcess,
    AutomationCondition,
    AutomationVariable,
    AutomationDocumentStep,
    AutomationDocumentLine,
    AutomationExecutionLog,
    AutomationDocumentApproval,
)

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
    'AccountGroup',
    'Account',
    'SubAccountGLAccountRelation',
    'TafsiliSubAccountRelation',
    # Tafsili Types
    'TafsiliType',
    # Hierarchy
    'TafsiliHierarchy',
    'TafsiliLevelSubAccountRelation',
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
    # Treasury Accounts
    'TreasuryAccount',
    # Payment Requests
    'PaymentRequest',
    # Warehouse Accounting
    'WarehouseExpenseDocument',
    'WarehouseExpenseDocumentLine',
    'WarehouseIncomeDocument',
    # Taxpayer System
    'FiscalMemoryConfig',
    'TaxInvoiceSubmission',
    'TaxInvoiceSubmissionLog',
    # Automation
    'AutomationProcess',
    'AutomationCondition',
    'AutomationVariable',
    'AutomationDocumentStep',
    'AutomationDocumentLine',
    'AutomationExecutionLog',
    'AutomationDocumentApproval',
]


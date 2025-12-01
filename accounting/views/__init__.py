"""
Views package for accounting module.
"""
from .base import AccountingBaseView
from .fiscal_years import (
    FiscalYearListView,
    FiscalYearCreateView,
    FiscalYearUpdateView,
    FiscalYearDeleteView,
)
from .accounts import (
    AccountListView,
    AccountCreateView,
    AccountUpdateView,
    AccountDeleteView,
)
from .gl_accounts import (
    GLAccountListView,
    GLAccountCreateView,
    GLAccountUpdateView,
    GLAccountDeleteView,
)
from .sub_accounts import (
    SubAccountListView,
    SubAccountCreateView,
    SubAccountUpdateView,
    SubAccountDeleteView,
)
from .tafsili_accounts import (
    TafsiliAccountListView,
    TafsiliAccountCreateView,
    TafsiliAccountUpdateView,
    TafsiliAccountDeleteView,
)
from .tafsili_hierarchy import (
    TafsiliHierarchyListView,
    TafsiliHierarchyCreateView,
    TafsiliHierarchyUpdateView,
    TafsiliHierarchyDeleteView,
)

# Import placeholder views from parent views.py for backward compatibility
# Using TYPE_CHECKING to avoid circular import
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..views import (
        AccountingDashboardView,
        GeneralLedgerListView,
        SubsidiaryLedgerListView,
        DetailLedgerListView,
        AccountingDocumentEntryView,
        AccountingDocumentExitView,
        TreasuryExpenseView,
        TreasuryIncomeView,
        PayrollDocumentView,
    )
else:
    # Lazy import to avoid circular import
    import sys
    from pathlib import Path
    
    _accounting_dir = Path(__file__).parent.parent
    _views_py_path = _accounting_dir / 'views.py'
    
    if _views_py_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("accounting.views_module", _views_py_path)
        views_module = importlib.util.module_from_spec(spec)
        sys.modules['accounting.views_module'] = views_module
        spec.loader.exec_module(views_module)
        
        # Import placeholder views
        AccountingDashboardView = views_module.AccountingDashboardView
        GeneralLedgerListView = views_module.GeneralLedgerListView
        SubsidiaryLedgerListView = views_module.SubsidiaryLedgerListView
        DetailLedgerListView = views_module.DetailLedgerListView
        AccountingDocumentEntryView = views_module.AccountingDocumentEntryView
        AccountingDocumentExitView = views_module.AccountingDocumentExitView
        TreasuryExpenseView = views_module.TreasuryExpenseView
        TreasuryIncomeView = views_module.TreasuryIncomeView
        PayrollDocumentView = views_module.PayrollDocumentView

__all__ = [
    # Base
    'AccountingBaseView',
    # Fiscal Years
    'FiscalYearListView',
    'FiscalYearCreateView',
    'FiscalYearUpdateView',
    'FiscalYearDeleteView',
    # Accounts
    'AccountListView',
    'AccountCreateView',
    'AccountUpdateView',
    'AccountDeleteView',
    # GL Accounts (حساب کل)
    'GLAccountListView',
    'GLAccountCreateView',
    'GLAccountUpdateView',
    'GLAccountDeleteView',
    # Sub Accounts (حساب معین)
    'SubAccountListView',
    'SubAccountCreateView',
    'SubAccountUpdateView',
    'SubAccountDeleteView',
    # Tafsili Accounts (حساب تفصیلی)
    'TafsiliAccountListView',
    'TafsiliAccountCreateView',
    'TafsiliAccountUpdateView',
    'TafsiliAccountDeleteView',
    # Tafsili Hierarchy (تفصیلی چند سطحی)
    'TafsiliHierarchyListView',
    'TafsiliHierarchyCreateView',
    'TafsiliHierarchyUpdateView',
    'TafsiliHierarchyDeleteView',
    # Placeholder views
    'AccountingDashboardView',
    'GeneralLedgerListView',
    'SubsidiaryLedgerListView',
    'DetailLedgerListView',
    'AccountingDocumentEntryView',
    'AccountingDocumentExitView',
    'TreasuryExpenseView',
    'TreasuryIncomeView',
    'PayrollDocumentView',
]


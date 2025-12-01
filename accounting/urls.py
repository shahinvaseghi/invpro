"""
URL configuration for accounting module.
"""
from django.urls import path
import importlib.util
from pathlib import Path
from .views.auth import set_active_fiscal_year

# Import from views.py file (not views package)
_accounting_dir = Path(__file__).parent
_views_py_path = _accounting_dir / 'views.py'
spec = importlib.util.spec_from_file_location("accounting.views_module", _views_py_path)
views_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(views_module)

from .views import (
    FiscalYearListView,
    FiscalYearCreateView,
    FiscalYearUpdateView,
    FiscalYearDeleteView,
    AccountListView,
    AccountCreateView,
    AccountUpdateView,
    AccountDeleteView,
)

app_name = 'accounting'

urlpatterns = [
    path('', views_module.AccountingDashboardView.as_view(), name='dashboard'),
    
    # Fiscal year selection
    path('set-fiscal-year/', set_active_fiscal_year, name='set_fiscal_year'),
    
    # Fiscal Years
    path('fiscal-years/', FiscalYearListView.as_view(), name='fiscal_years'),
    path('fiscal-years/create/', FiscalYearCreateView.as_view(), name='fiscal_year_create'),
    path('fiscal-years/<int:pk>/edit/', FiscalYearUpdateView.as_view(), name='fiscal_year_edit'),
    path('fiscal-years/<int:pk>/delete/', FiscalYearDeleteView.as_view(), name='fiscal_year_delete'),
    
    # Chart of Accounts
    path('accounts/', AccountListView.as_view(), name='accounts'),
    path('accounts/create/', AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/edit/', AccountUpdateView.as_view(), name='account_edit'),
    path('accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
    
    # General Section (عمومی)
    path('general/ledger/', views_module.GeneralLedgerListView.as_view(), name='general_ledger'),
    path('general/subsidiary/', views_module.SubsidiaryLedgerListView.as_view(), name='general_subsidiary'),
    path('general/detail/', views_module.DetailLedgerListView.as_view(), name='general_detail'),
    
    # Accounting Documents (اسناد حسابداری)
    path('documents/entry/', views_module.AccountingDocumentEntryView.as_view(), name='document_entry'),
    path('documents/exit/', views_module.AccountingDocumentExitView.as_view(), name='document_exit'),
    
    # Treasury (خزانه)
    path('treasury/expense/', views_module.TreasuryExpenseView.as_view(), name='treasury_expense'),
    path('treasury/income/', views_module.TreasuryIncomeView.as_view(), name='treasury_income'),
    path('treasury/accounts/', views_module.TreasuryAccountsView.as_view(), name='treasury_accounts'),
    path('treasury/transactions/', views_module.TreasuryTransactionsView.as_view(), name='treasury_transactions'),
    path('treasury/checks/', views_module.TreasuryChecksView.as_view(), name='treasury_checks'),
    path('treasury/reconciliation/', views_module.TreasuryReconciliationView.as_view(), name='treasury_reconciliation'),
    
    # Income & Expense (درآمد و هزینه)
    path('income-expense/income/', views_module.IncomeExpenseIncomeView.as_view(), name='income_expense_income'),
    path('income-expense/expense/', views_module.IncomeExpenseExpenseView.as_view(), name='income_expense_expense'),
    path('income-expense/categories/', views_module.IncomeExpenseCategoriesView.as_view(), name='income_expense_categories'),
    path('income-expense/cost-centers/', views_module.CostCentersView.as_view(), name='cost_centers'),
    
    # Party Accounts (طرف حساب‌ها)
    path('parties/', views_module.PartiesView.as_view(), name='parties'),
    path('parties/accounts/', views_module.PartyAccountsView.as_view(), name='party_accounts'),
    path('parties/transactions/', views_module.PartyTransactionsView.as_view(), name='party_transactions'),
    
    # Tax Compliance (مالیات)
    path('tax/vat/', views_module.TaxVATView.as_view(), name='tax_vat'),
    path('tax/ttms/', views_module.TaxTTMSView.as_view(), name='tax_ttms'),
    path('tax/seasonal/', views_module.TaxSeasonalView.as_view(), name='tax_seasonal'),
    
    # Financial Reports (گزارش‌های مالی)
    path('reports/balance-sheet/', views_module.ReportBalanceSheetView.as_view(), name='report_balance_sheet'),
    path('reports/income-statement/', views_module.ReportIncomeStatementView.as_view(), name='report_income_statement'),
    path('reports/account-movements/', views_module.ReportAccountMovementsView.as_view(), name='report_account_movements'),
    path('reports/trial-balance/', views_module.ReportTrialBalanceView.as_view(), name='report_trial_balance'),
    path('reports/party-statement/', views_module.ReportPartyStatementView.as_view(), name='report_party_statement'),
    path('reports/vat/', views_module.ReportVATView.as_view(), name='report_vat'),
    
    # Settings (تنظیمات)
    path('settings/', views_module.SettingsView.as_view(), name='settings'),
    
    # Payroll (حقوق و دستمزد)
    path('payroll/payment/', views_module.PayrollPaymentView.as_view(), name='payroll_payment'),
    path('payroll/insurance-tax/', views_module.PayrollInsuranceTaxSettingsView.as_view(), name='payroll_insurance_tax'),
    path('payroll/document/', views_module.PayrollDocumentView.as_view(), name='payroll_document'),
    path('payroll/bank-transfer/', views_module.PayrollBankTransferView.as_view(), name='payroll_bank_transfer'),
]

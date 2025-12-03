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
    FiscalYearDetailView,
    FiscalYearUpdateView,
    FiscalYearDeleteView,
    AccountListView,
    AccountCreateView,
    AccountDetailView,
    AccountUpdateView,
    AccountDeleteView,
    GLAccountListView,
    GLAccountCreateView,
    GLAccountDetailView,
    GLAccountUpdateView,
    GLAccountDeleteView,
    SubAccountListView,
    SubAccountCreateView,
    SubAccountDetailView,
    SubAccountUpdateView,
    SubAccountDeleteView,
    TafsiliAccountListView,
    TafsiliAccountCreateView,
    TafsiliAccountDetailView,
    TafsiliAccountUpdateView,
    TafsiliAccountDeleteView,
    TafsiliHierarchyListView,
    TafsiliHierarchyCreateView,
    TafsiliHierarchyDetailView,
    TafsiliHierarchyUpdateView,
    TafsiliHierarchyDeleteView,
)
from .views.document_attachments import (
    DocumentAttachmentUploadView,
    DocumentAttachmentListView,
    DocumentAttachmentDownloadSingleView,
    DocumentAttachmentDownloadBulkView,
)

app_name = 'accounting'

urlpatterns = [
    path('', views_module.AccountingDashboardView.as_view(), name='dashboard'),
    
    # Fiscal year selection
    path('set-fiscal-year/', set_active_fiscal_year, name='set_fiscal_year'),
    
    # Fiscal Years
    path('fiscal-years/', FiscalYearListView.as_view(), name='fiscal_years'),
    path('fiscal-years/create/', FiscalYearCreateView.as_view(), name='fiscal_year_create'),
    path('fiscal-years/<int:pk>/', FiscalYearDetailView.as_view(), name='fiscal_year_detail'),
    path('fiscal-years/<int:pk>/edit/', FiscalYearUpdateView.as_view(), name='fiscal_year_edit'),
    path('fiscal-years/<int:pk>/delete/', FiscalYearDeleteView.as_view(), name='fiscal_year_delete'),
    
    # Chart of Accounts
    path('accounts/', AccountListView.as_view(), name='accounts'),
    path('accounts/create/', AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/', AccountDetailView.as_view(), name='account_detail'),
    path('accounts/<int:pk>/edit/', AccountUpdateView.as_view(), name='account_edit'),
    path('accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
    
    # General Section (عمومی)
    path('general/ledger/', views_module.GeneralLedgerListView.as_view(), name='general_ledger'),
    path('general/subsidiary/', views_module.SubsidiaryLedgerListView.as_view(), name='general_subsidiary'),
    path('general/detail/', views_module.DetailLedgerListView.as_view(), name='general_detail'),
    
    # GL Accounts (حساب کل)
    path('gl-accounts/', GLAccountListView.as_view(), name='gl_accounts'),
    path('gl-accounts/create/', GLAccountCreateView.as_view(), name='gl_account_create'),
    path('gl-accounts/<int:pk>/', GLAccountDetailView.as_view(), name='gl_account_detail'),
    path('gl-accounts/<int:pk>/edit/', GLAccountUpdateView.as_view(), name='gl_account_edit'),
    path('gl-accounts/<int:pk>/delete/', GLAccountDeleteView.as_view(), name='gl_account_delete'),
    
    # Sub Accounts (حساب معین)
    path('sub-accounts/', SubAccountListView.as_view(), name='sub_accounts'),
    path('sub-accounts/create/', SubAccountCreateView.as_view(), name='sub_account_create'),
    path('sub-accounts/<int:pk>/', SubAccountDetailView.as_view(), name='sub_account_detail'),
    path('sub-accounts/<int:pk>/edit/', SubAccountUpdateView.as_view(), name='sub_account_edit'),
    path('sub-accounts/<int:pk>/delete/', SubAccountDeleteView.as_view(), name='sub_account_delete'),
    
    # Tafsili Accounts (حساب تفصیلی)
    path('tafsili-accounts/', TafsiliAccountListView.as_view(), name='tafsili_accounts'),
    path('tafsili-accounts/create/', TafsiliAccountCreateView.as_view(), name='tafsili_account_create'),
    path('tafsili-accounts/<int:pk>/', TafsiliAccountDetailView.as_view(), name='tafsili_account_detail'),
    path('tafsili-accounts/<int:pk>/edit/', TafsiliAccountUpdateView.as_view(), name='tafsili_account_edit'),
    path('tafsili-accounts/<int:pk>/delete/', TafsiliAccountDeleteView.as_view(), name='tafsili_account_delete'),
    
    # Tafsili Hierarchy (تفصیلی چند سطحی)
    path('tafsili-hierarchy/', TafsiliHierarchyListView.as_view(), name='tafsili_hierarchy_list'),
    path('tafsili-hierarchy/create/', TafsiliHierarchyCreateView.as_view(), name='tafsili_hierarchy_create'),
    path('tafsili-hierarchy/<int:pk>/', TafsiliHierarchyDetailView.as_view(), name='tafsili_hierarchy_detail'),
    path('tafsili-hierarchy/<int:pk>/edit/', TafsiliHierarchyUpdateView.as_view(), name='tafsili_hierarchy_edit'),
    path('tafsili-hierarchy/<int:pk>/delete/', TafsiliHierarchyDeleteView.as_view(), name='tafsili_hierarchy_delete'),
    
    # Accounting Documents (اسناد حسابداری)
    path('documents/create/', views_module.AccountingDocumentCreateView.as_view(), name='document_create'),
    path('documents/list/', views_module.AccountingDocumentListView.as_view(), name='document_list'),
    path('documents/status/', views_module.AccountingDocumentStatusView.as_view(), name='document_status'),
    path('tafsili-movements/', views_module.TafsiliMovementsView.as_view(), name='tafsili_movements'),
    
    # Treasury (خزانه)
    path('treasury/income/', views_module.TreasuryIncomeView.as_view(), name='treasury_income'),
    path('treasury/expense/', views_module.TreasuryExpenseView.as_view(), name='treasury_expense'),
    path('treasury/receive/', views_module.TreasuryReceiveView.as_view(), name='treasury_receive'),
    path('treasury/pay/', views_module.TreasuryPayView.as_view(), name='treasury_pay'),
    path('treasury/transactions/', views_module.TreasuryTransactionsView.as_view(), name='treasury_transactions'),
    path('treasury/transfer/', views_module.TreasuryTransferView.as_view(), name='treasury_transfer'),
    path('treasury/accounts/', views_module.TreasuryAccountsView.as_view(), name='treasury_accounts'),
    path('treasury/accounts/create/', views_module.TreasuryAccountCreateView.as_view(), name='treasury_account_create'),
    path('treasury/accounts/api/sub-accounts/', views_module.TreasuryAccountSubAccountsAPIView.as_view(), name='treasury_account_api_sub_accounts'),
    path('treasury/accounts/api/gl-accounts/', views_module.TreasuryAccountGLAccountsAPIView.as_view(), name='treasury_account_api_gl_accounts'),
    path('treasury/checks/', views_module.TreasuryChecksView.as_view(), name='treasury_checks'),
    path('treasury/reconciliation/', views_module.TreasuryReconciliationView.as_view(), name='treasury_reconciliation'),
    path('treasury/cash-report/', views_module.TreasuryCashReportView.as_view(), name='treasury_cash_report'),
    
    # Income & Expense (درآمد و هزینه)
    path('income-expense/income/', views_module.IncomeExpenseIncomeView.as_view(), name='income_expense_income'),
    path('income-expense/expense/', views_module.IncomeExpenseExpenseView.as_view(), name='income_expense_expense'),
    path('income-expense/cost-allocation/', views_module.CostAllocationView.as_view(), name='cost_allocation'),
    path('income-expense/income-report/', views_module.IncomeReportView.as_view(), name='income_report'),
    path('income-expense/expense-report/', views_module.ExpenseReportView.as_view(), name='expense_report'),
    path('income-expense/cost-center-report/', views_module.CostCenterReportView.as_view(), name='cost_center_report'),
    path('income-expense/categories/', views_module.IncomeExpenseCategoriesView.as_view(), name='income_expense_categories'),
    path('income-expense/categories/create/', views_module.IncomeExpenseCategoryCreateView.as_view(), name='income_expense_category_create'),
    path('income-expense/cost-centers/', views_module.CostCentersView.as_view(), name='cost_centers'),
    path('income-expense/cost-centers/create/', views_module.CostCenterCreateView.as_view(), name='cost_center_create'),
    
    # Party Accounts (طرف حساب‌ها)
    path('parties/', views_module.PartiesView.as_view(), name='parties'),
    path('parties/create/', views_module.PartyCreateView.as_view(), name='party_create'),
    path('parties/accounts/', views_module.PartyAccountsView.as_view(), name='party_accounts'),
    path('parties/accounts/create/', views_module.PartyAccountCreateView.as_view(), name='party_account_create'),
    path('parties/movements/', views_module.PartyMovementsView.as_view(), name='party_movements'),
    path('parties/balance-report/', views_module.PartyBalanceReportView.as_view(), name='party_balance_report'),
    
    # Tax Compliance (مالیات)
    path('tax/vat/', views_module.TaxVATView.as_view(), name='tax_vat'),
    path('tax/validation/', views_module.TaxValidationView.as_view(), name='tax_validation'),
    path('tax/discrepancy-report/', views_module.TaxDiscrepancyReportView.as_view(), name='tax_discrepancy_report'),
    path('tax/seasonal/', views_module.TaxSeasonalView.as_view(), name='tax_seasonal'),
    
    # Financial Reports (گزارش‌های مالی)
    path('reports/trial-balance/', views_module.ReportTrialBalanceView.as_view(), name='report_trial_balance'),
    path('reports/balance-sheet/', views_module.ReportBalanceSheetView.as_view(), name='report_balance_sheet'),
    path('reports/income-statement/', views_module.ReportIncomeStatementView.as_view(), name='report_income_statement'),
    path('reports/cash-flow/', views_module.ReportCashFlowView.as_view(), name='report_cash_flow'),
    path('reports/account-movements/', views_module.ReportAccountMovementsView.as_view(), name='report_account_movements'),
    path('reports/tafsili-cost-center/', views_module.ReportTafsiliCostCenterView.as_view(), name='report_tafsili_cost_center'),
    path('reports/checks/', views_module.ReportChecksView.as_view(), name='report_checks'),
    path('reports/treasury/', views_module.ReportTreasuryView.as_view(), name='report_treasury'),
    path('reports/party-statement/', views_module.ReportPartyStatementView.as_view(), name='report_party_statement'),
    path('reports/vat/', views_module.ReportVATView.as_view(), name='report_vat'),
    path('reports/monthly/', views_module.ReportMonthlyView.as_view(), name='report_monthly'),
    
    # Settings (تنظیمات)
    path('settings/', views_module.SettingsView.as_view(), name='settings'),
    path('settings/treasury/', views_module.SettingsTreasuryView.as_view(), name='settings_treasury'),
    path('settings/tax/', views_module.SettingsTaxView.as_view(), name='settings_tax'),
    
    # Document Attachments (بارگذاری اسناد)
    path('attachments/upload/', DocumentAttachmentUploadView.as_view(), name='attachment_upload'),
    path('attachments/list/', DocumentAttachmentListView.as_view(), name='attachment_list'),
    path('attachments/attach/', views_module.AttachmentAttachView.as_view(), name='attachment_attach'),
    path('attachments/download-single/', DocumentAttachmentDownloadSingleView.as_view(), name='attachment_download_single'),
    path('attachments/download-bulk/', DocumentAttachmentDownloadBulkView.as_view(), name='attachment_download_bulk'),
    
    # Utilities (ابزارها و عملیات تکمیلی)
    path('utils/close-temp-accounts/', views_module.CloseTempAccountsView.as_view(), name='close_temp_accounts'),
    path('utils/opening-entry/', views_module.OpeningEntryView.as_view(), name='opening_entry'),
    path('utils/closing-entry/', views_module.ClosingEntryView.as_view(), name='closing_entry'),
    path('utils/integration/', views_module.IntegrationView.as_view(), name='integration'),
    path('utils/backup-restore/', views_module.BackupRestoreView.as_view(), name='backup_restore'),
    
    # Payroll (حقوق و دستمزد)
    path('payroll/payment/', views_module.PayrollPaymentView.as_view(), name='payroll_payment'),
    path('payroll/insurance-tax/', views_module.PayrollInsuranceTaxSettingsView.as_view(), name='payroll_insurance_tax'),
    path('payroll/document/', views_module.PayrollDocumentView.as_view(), name='payroll_document'),
    path('payroll/bank-transfer/', views_module.PayrollBankTransferView.as_view(), name='payroll_bank_transfer'),
]

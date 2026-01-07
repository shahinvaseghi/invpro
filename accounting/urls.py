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
    AccountTreeView,
    AccountGroupListView,
    AccountGroupCreateView,
    AccountGroupDetailView,
    AccountGroupUpdateView,
    AccountGroupDeleteView,
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
    TafsiliTypeListView,
    TafsiliTypeCreateView,
    TafsiliTypeDetailView,
    TafsiliTypeUpdateView,
    TafsiliTypeDeleteView,
)
from .views.document_attachments import (
    DocumentAttachmentUploadView,
    DocumentAttachmentListView,
    DocumentAttachmentDownloadSingleView,
    DocumentAttachmentDownloadBulkView,
)
from .views.api import (
    filter_sub_accounts_by_tafsili,
    filter_gl_accounts_by_sub,
    filter_sub_accounts_by_gl,
    filter_tafsili_accounts_by_sub,
    toggle_document_lock,
    import_account_tree,
    get_account_tree,
    get_allowed_tafsili_accounts,
    get_gl_account_info,
)
from .views.taxpayer_system_api import (
    TestConnectionAPIView,
    ValidateDocumentAPIView,
    SubmitInvoiceAPIView,
    CheckStatusAPIView,
    ViewLogsAPIView,
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
    path('accounts/tree/', AccountTreeView.as_view(), name='accounts_tree'),
    path('accounts/create/', AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/', AccountDetailView.as_view(), name='account_detail'),
    path('accounts/<int:pk>/edit/', AccountUpdateView.as_view(), name='account_edit'),
    path('accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
    
    # Account Groups (گروه حساب‌ها)
    path('account-groups/', AccountGroupListView.as_view(), name='account_groups'),
    path('account-groups/create/', AccountGroupCreateView.as_view(), name='account_group_create'),
    path('account-groups/<int:pk>/', AccountGroupDetailView.as_view(), name='account_group_detail'),
    path('account-groups/<int:pk>/edit/', AccountGroupUpdateView.as_view(), name='account_group_edit'),
    path('account-groups/<int:pk>/delete/', AccountGroupDeleteView.as_view(), name='account_group_delete'),
    
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
    
    # Tafsili Types (نوع تفصیلی)
    path('tafsili-types/', TafsiliTypeListView.as_view(), name='tafsili_types'),
    path('tafsili-types/create/', TafsiliTypeCreateView.as_view(), name='tafsili_type_create'),
    path('tafsili-types/<int:pk>/', TafsiliTypeDetailView.as_view(), name='tafsili_type_detail'),
    path('tafsili-types/<int:pk>/edit/', TafsiliTypeUpdateView.as_view(), name='tafsili_type_edit'),
    path('tafsili-types/<int:pk>/delete/', TafsiliTypeDeleteView.as_view(), name='tafsili_type_delete'),

    # SubAccount Tafsili Level1 Connection (اتصال تفصیلی به معین)
    path('subaccount-tafsili-level1-connection/', views_module.SubAccountTafsiliLevel1ConnectionView.as_view(), name='subaccount_tafsili_level1_connection'),
    path('subaccount-tafsili-level1-connection/create/', views_module.SubAccountTafsiliLevel1CreateView.as_view(), name='subaccount_tafsili_level1_create'),
    path('subaccount-tafsili-level1-connection/<int:pk>/edit/', views_module.SubAccountTafsiliLevel1UpdateView.as_view(), name='subaccount_tafsili_level1_edit'),
    path('subaccount-tafsili-level1-connection/<int:pk>/delete/', views_module.SubAccountTafsiliLevel1DeleteView.as_view(), name='subaccount_tafsili_level1_delete'),

    # Hierarchical Tafsili Connection (اتصال سلسله مراتبی تفصیلی)
    path('hierarchical-tafsili-connection/', views_module.HierarchicalTafsiliConnectionView.as_view(), name='hierarchical_tafsili_connection'),
    path('hierarchical-tafsili-connection/create/', views_module.TafsiliHierarchyCreateView.as_view(), name='tafsili_hierarchy_create'),
    path('hierarchical-tafsili-connection/<int:pk>/edit/', views_module.TafsiliHierarchyUpdateView.as_view(), name='tafsili_hierarchy_edit'),
    path('hierarchical-tafsili-connection/<int:pk>/delete/', views_module.TafsiliHierarchyDeleteView.as_view(), name='tafsili_hierarchy_delete'),
    
    # Accounting Documents (اسناد حسابداری)
    path('documents/create/', views_module.AccountingDocumentCreateView.as_view(), name='document_create'),
    path('documents/list/', views_module.AccountingDocumentListView.as_view(), name='document_list'),
    path('documents/<int:pk>/', views_module.AccountingDocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/edit/', views_module.AccountingDocumentUpdateView.as_view(), name='document_edit'),
    path('documents/<int:pk>/delete/', views_module.AccountingDocumentDeleteView.as_view(), name='document_delete'),
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
    path('treasury/checks/', views_module.TreasuryChecksView.as_view(), name='treasury_checks'),
    path('treasury/reconciliation/', views_module.TreasuryReconciliationView.as_view(), name='treasury_reconciliation'),
    path('treasury/cash-report/', views_module.TreasuryCashReportView.as_view(), name='treasury_cash_report'),
    path('treasury/payment-requests/', views_module.PaymentRequestListView.as_view(), name='payment_requests'),
    path('treasury/payment-requests/create/', views_module.PaymentRequestCreateView.as_view(), name='payment_request_create'),
    path('treasury/payment-requests/<int:pk>/', views_module.PaymentRequestDetailView.as_view(), name='payment_request_detail'),
    path('treasury/payment-requests/<int:pk>/edit/', views_module.PaymentRequestUpdateView.as_view(), name='payment_request_edit'),
    path('treasury/payment-requests/<int:pk>/delete/', views_module.PaymentRequestDeleteView.as_view(), name='payment_request_delete'),
    
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
    path('parties/<int:pk>/', views_module.PartyDetailView.as_view(), name='party_detail'),
    path('parties/<int:pk>/edit/', views_module.PartyUpdateView.as_view(), name='party_edit'),
    path('parties/<int:pk>/delete/', views_module.PartyDeleteView.as_view(), name='party_delete'),
    path('parties/accounts/', views_module.PartyAccountsView.as_view(), name='party_accounts'),
    path('parties/accounts/create/', views_module.PartyAccountCreateView.as_view(), name='party_account_create'),
    path('parties/movements/', views_module.PartyMovementsView.as_view(), name='party_movements'),
    path('parties/balance-report/', views_module.PartyBalanceReportView.as_view(), name='party_balance_report'),
    
    # Tax Compliance (مالیات)
    path('tax/vat/', views_module.TaxVATView.as_view(), name='tax_vat'),
    path('tax/moadian-settings/', views_module.TaxMoadianSettingsView.as_view(), name='tax_moadian_settings'),
    path('tax/validation/', views_module.TaxValidationView.as_view(), name='tax_validation'),
    path('tax/discrepancy-report/', views_module.TaxDiscrepancyReportView.as_view(), name='tax_discrepancy_report'),
    path('tax/seasonal/', views_module.TaxSeasonalView.as_view(), name='tax_seasonal'),
    
    # Taxpayer System API endpoints
    path('tax/api/test-connection/', TestConnectionAPIView.as_view(), name='tax_api_test_connection'),
    path('tax/api/validate-document/', ValidateDocumentAPIView.as_view(), name='tax_api_validate_document'),
    path('tax/api/submit-invoice/', SubmitInvoiceAPIView.as_view(), name='tax_api_submit_invoice'),
    path('tax/api/check-status/', CheckStatusAPIView.as_view(), name='tax_api_check_status'),
    path('tax/api/view-logs/', ViewLogsAPIView.as_view(), name='tax_api_view_logs'),
    
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
    path('reports/account-browser/', views_module.AccountBrowserView.as_view(), name='report_account_browser'),

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
    
    # API endpoints for filtering accounts (bidirectional cascade)
    path('api/filter-sub-accounts-by-tafsili/', filter_sub_accounts_by_tafsili, name='api_filter_sub_by_tafsili'),
    path('api/filter-gl-accounts-by-sub/', filter_gl_accounts_by_sub, name='api_filter_gl_by_sub'),
    path('api/filter-sub-accounts-by-gl/', filter_sub_accounts_by_gl, name='api_filter_sub_by_gl'),
    path('api/filter-tafsili-accounts-by-sub/', filter_tafsili_accounts_by_sub, name='api_filter_tafsili_by_sub'),
    path('api/get-allowed-tafsili-accounts/', get_allowed_tafsili_accounts, name='api_get_allowed_tafsili_accounts'),
    path('api/get-gl-account-info/', get_gl_account_info, name='api_get_gl_account_info'),
    path('api/toggle-document-lock/', toggle_document_lock, name='api_toggle_document_lock'),
    path('api/import-account-tree/', import_account_tree, name='import_account_tree'),
    path('api/account-tree/', get_account_tree, name='api_account_tree'),
    
    # Warehouse Accounting (حسابداری انبار)
    path('warehouse/expense/', views_module.WarehouseExpenseView.as_view(), name='warehouse_expense'),
    path('warehouse/expense/create/', views_module.WarehouseExpenseCreateView.as_view(), name='warehouse_expense_create'),
    path('warehouse/expense/<int:pk>/', views_module.WarehouseExpenseDetailView.as_view(), name='warehouse_expense_detail'),
    path('warehouse/expense/create-from-receipt/<str:receipt_type>/<int:receipt_id>/', views_module.WarehouseExpenseCreateFromReceiptView.as_view(), name='warehouse_expense_create_from_receipt'),
    path('warehouse/expense/api/receipts/', views_module.WarehouseExpenseReceiptsAPIView.as_view(), name='warehouse_expense_api_receipts'),
    path('warehouse/expense/api/receipt-lines/', views_module.WarehouseExpenseReceiptLinesAPIView.as_view(), name='warehouse_expense_api_receipt_lines'),
    path('warehouse/income/', views_module.WarehouseIncomeView.as_view(), name='warehouse_income'),
    path('warehouse/opening-closing/', views_module.WarehouseOpeningClosingView.as_view(), name='warehouse_opening_closing'),
    path('warehouse/settings/', views_module.WarehouseSettingsView.as_view(), name='warehouse_settings'),
    
    # Automation (خودکارسازی)
    path('automation/processes/', views_module.AutomationProcessListView.as_view(), name='automation_processes'),
    path('automation/processes/create/', views_module.AutomationProcessCreateView.as_view(), name='automation_process_create'),
    path('automation/processes/<int:pk>/', views_module.AutomationProcessDetailView.as_view(), name='automation_process_detail'),
    path('automation/processes/<int:pk>/edit/', views_module.AutomationProcessUpdateView.as_view(), name='automation_process_edit'),
    path('automation/processes/<int:pk>/delete/', views_module.AutomationProcessDeleteView.as_view(), name='automation_process_delete'),
    path('automation/logs/', views_module.AutomationExecutionLogListView.as_view(), name='automation_execution_logs'),
    path('automation/logs/<int:pk>/', views_module.AutomationExecutionLogDetailView.as_view(), name='automation_execution_log_detail'),
    # Conditions
    path('automation/processes/<int:process_id>/conditions/create/', views_module.AutomationConditionCreateView.as_view(), name='automation_condition_create'),
    path('automation/conditions/<int:pk>/edit/', views_module.AutomationConditionUpdateView.as_view(), name='automation_condition_edit'),
    path('automation/conditions/<int:pk>/delete/', views_module.AutomationConditionDeleteView.as_view(), name='automation_condition_delete'),
    # Variables
    path('automation/processes/<int:process_id>/variables/create/', views_module.AutomationVariableCreateView.as_view(), name='automation_variable_create'),
    path('automation/variables/<int:pk>/edit/', views_module.AutomationVariableUpdateView.as_view(), name='automation_variable_edit'),
    path('automation/variables/<int:pk>/delete/', views_module.AutomationVariableDeleteView.as_view(), name='automation_variable_delete'),
    # Document Steps
    path('automation/processes/<int:process_id>/steps/create/', views_module.AutomationDocumentStepCreateView.as_view(), name='automation_document_step_create'),
    path('automation/processes/<int:process_id>/steps/<int:pk>/', views_module.AutomationDocumentStepDetailView.as_view(), name='automation_document_step_detail'),
    path('automation/steps/<int:pk>/edit/', views_module.AutomationDocumentStepUpdateView.as_view(), name='automation_document_step_edit'),
    path('automation/steps/<int:pk>/delete/', views_module.AutomationDocumentStepDeleteView.as_view(), name='automation_document_step_delete'),
    # Document Lines
    path('automation/steps/<int:step_id>/lines/create/', views_module.AutomationDocumentLineCreateView.as_view(), name='automation_document_line_create'),
    path('automation/lines/<int:pk>/edit/', views_module.AutomationDocumentLineUpdateView.as_view(), name='automation_document_line_edit'),
    path('automation/lines/<int:pk>/delete/', views_module.AutomationDocumentLineDeleteView.as_view(), name='automation_document_line_delete'),
    # API endpoints
    path('api/tafsili-hierarchy-tree/', views_module.TafsiliHierarchyTreeAPIView.as_view(), name='tafsili_hierarchy_tree_api'),
    path('api/filtered-tafsili-accounts/', views_module.FilteredTafsiliAccountsAPIView.as_view(), name='filtered_tafsili_accounts_api'),
    path('automation/api/document-info/<str:document_id>/', views_module.get_document_info, name='automation_api_document_info'),
    path('automation/api/filterable-fields/<str:document_id>/', views_module.get_filterable_fields, name='automation_api_filterable_fields'),
    path('automation/api/extractable-fields/<str:document_id>/', views_module.get_extractable_fields, name='automation_api_extractable_fields'),
    path('automation/api/autocomplete/<str:model_name>/', views_module.get_autocomplete_options, name='automation_api_autocomplete'),
]

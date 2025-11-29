"""
URL configuration for accounting module.
"""
from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.AccountingDashboardView.as_view(), name='dashboard'),
    
    # General Section (عمومی)
    path('general/ledger/', views.GeneralLedgerListView.as_view(), name='general_ledger'),
    path('general/subsidiary/', views.SubsidiaryLedgerListView.as_view(), name='general_subsidiary'),
    path('general/detail/', views.DetailLedgerListView.as_view(), name='general_detail'),
    
    # Accounting Documents (اسناد حسابداری)
    path('documents/entry/', views.AccountingDocumentEntryView.as_view(), name='document_entry'),
    path('documents/exit/', views.AccountingDocumentExitView.as_view(), name='document_exit'),
    
    # Treasury (خزانه)
    path('treasury/expense/', views.TreasuryExpenseView.as_view(), name='treasury_expense'),
    path('treasury/income/', views.TreasuryIncomeView.as_view(), name='treasury_income'),
    
    # Payroll (حقوق و دستمزد)
    path('payroll/document/', views.PayrollDocumentView.as_view(), name='payroll_document'),
    path('payroll/decrees/', views.PayrollDecreeListView.as_view(), name='payroll_decrees'),
    path('payroll/decree-groups/', views.PayrollDecreeGroupListView.as_view(), name='payroll_decree_groups'),
    path('payroll/decree-subgroups/', views.PayrollDecreeSubGroupListView.as_view(), name='payroll_decree_subgroups'),
]

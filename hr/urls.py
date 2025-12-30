"""
URL configuration for HR module.
"""
from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    path('', views.HrDashboardView.as_view(), name='dashboard'),
    
    # Personnel (پرسنل)
    path('personnel/create/', views.PersonnelCreateView.as_view(), name='personnel_create'),
    path('personnel/decree-assignment/', views.PersonnelDecreeAssignmentView.as_view(), name='personnel_decree_assignment'),
    path('personnel/form/create/', views.PersonnelFormCreateView.as_view(), name='personnel_form_create'),
    path('personnel/form-groups/', views.PersonnelFormGroupListView.as_view(), name='personnel_form_groups'),
    path('personnel/form-subgroups/', views.PersonnelFormSubGroupListView.as_view(), name='personnel_form_subgroups'),
    
    # Requests (درخواست‌ها)
    path('requests/leave/', views.LeaveRequestView.as_view(), name='requests_leave'),
    path('requests/sick-leave/', views.SickLeaveRequestView.as_view(), name='requests_sick_leave'),
    path('requests/loan/', views.LoanRequestView.as_view(), name='requests_loan'),
    
    # Loans (وام)
    path('loans/management/', views.LoanManagementView.as_view(), name='loans_management'),
    path('loans/scheduling/', views.LoanSchedulingView.as_view(), name='loans_scheduling'),
    path('loans/savings-fund/', views.SavingsFundView.as_view(), name='loans_savings_fund'),
    
    # Payroll Decrees (حکم‌های حقوق و دستمزد)
    path('payroll/decrees/', views.PayrollDecreeListView.as_view(), name='payroll_decrees'),
    path('payroll/decree-groups/', views.PayrollDecreeGroupListView.as_view(), name='payroll_decree_groups'),
    path('payroll/decree-subgroups/', views.PayrollDecreeSubGroupListView.as_view(), name='payroll_decree_subgroups'),
]

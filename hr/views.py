"""
Views for HR module.
"""
from django.views.generic import TemplateView
from shared.mixins import FeaturePermissionRequiredMixin


class HrDashboardView(FeaturePermissionRequiredMixin, TemplateView):
    """Dashboard view for HR module."""
    template_name = 'hr/dashboard.html'
    feature_code = 'hr.dashboard'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'منابع انسانی'
        return context


# Personnel Section (پرسنل)
class PersonnelCreateView(FeaturePermissionRequiredMixin, TemplateView):
    """Create view for personnel."""
    template_name = 'hr/personnel/create.html'
    feature_code = 'hr.personnel'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'ایجاد پرسنل'
        return context


class PersonnelDecreeAssignmentView(FeaturePermissionRequiredMixin, TemplateView):
    """View for assigning decrees to personnel."""
    template_name = 'hr/personnel/decree_assignment.html'
    feature_code = 'hr.personnel.decree'
    required_action = 'edit_own'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'تخصیص حکم'
        return context


class PersonnelFormCreateView(FeaturePermissionRequiredMixin, TemplateView):
    """Create view for personnel forms."""
    template_name = 'hr/personnel/form_create.html'
    feature_code = 'hr.personnel.form'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'ایجاد فرم پرسنل'
        return context


class PersonnelFormGroupListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for personnel form groups."""
    template_name = 'hr/personnel/form_group_list.html'
    feature_code = 'hr.personnel.form_groups'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'گروه‌بندی فرم پرسنل'
        return context


class PersonnelFormSubGroupListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for personnel form sub-groups."""
    template_name = 'hr/personnel/form_subgroup_list.html'
    feature_code = 'hr.personnel.form_subgroups'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'زیر گروه‌بندی فرم پرسنل'
        return context


# Requests Section (درخواست‌ها)
class LeaveRequestView(FeaturePermissionRequiredMixin, TemplateView):
    """View for leave requests."""
    template_name = 'hr/requests/leave.html'
    feature_code = 'hr.requests.leave'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'درخواست مرخصی'
        return context


class SickLeaveRequestView(FeaturePermissionRequiredMixin, TemplateView):
    """View for sick leave requests."""
    template_name = 'hr/requests/sick_leave.html'
    feature_code = 'hr.requests.sick_leave'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'درخواست استعلاجی'
        return context


class LoanRequestView(FeaturePermissionRequiredMixin, TemplateView):
    """View for loan requests."""
    template_name = 'hr/requests/loan.html'
    feature_code = 'hr.requests.loan'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'درخواست وام'
        return context


# Loan Section (وام)
class LoanManagementView(FeaturePermissionRequiredMixin, TemplateView):
    """View for loan management."""
    template_name = 'hr/loans/management.html'
    feature_code = 'hr.loans.management'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'مدیریت وام'
        return context


class LoanSchedulingView(FeaturePermissionRequiredMixin, TemplateView):
    """View for loan scheduling."""
    template_name = 'hr/loans/scheduling.html'
    feature_code = 'hr.loans.scheduling'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'نوبت‌بندی'
        return context


class SavingsFundView(FeaturePermissionRequiredMixin, TemplateView):
    """View for savings fund."""
    template_name = 'hr/loans/savings_fund.html'
    feature_code = 'hr.loans.savings_fund'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'hr'
        context['page_title'] = 'صندوق اندوخته'
        return context

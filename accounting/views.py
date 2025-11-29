"""
Views for accounting module.
"""
from django.views.generic import TemplateView
from shared.mixins import FeaturePermissionRequiredMixin


class AccountingDashboardView(FeaturePermissionRequiredMixin, TemplateView):
    """Dashboard view for accounting module."""
    template_name = 'accounting/dashboard.html'
    feature_code = 'accounting.dashboard'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'حسابداری'
        return context


# General Section (عمومی)
class GeneralLedgerListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for general ledger documents."""
    template_name = 'accounting/general/ledger_list.html'
    feature_code = 'accounting.general.ledger'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'اسناد کل'
        return context


class SubsidiaryLedgerListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for subsidiary ledgers."""
    template_name = 'accounting/general/subsidiary_list.html'
    feature_code = 'accounting.general.subsidiary'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'معین‌ها'
        return context


class DetailLedgerListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for detail ledgers."""
    template_name = 'accounting/general/detail_list.html'
    feature_code = 'accounting.general.detail'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تفصیلی‌ها'
        return context


# Accounting Documents (اسناد حسابداری)
class AccountingDocumentEntryView(FeaturePermissionRequiredMixin, TemplateView):
    """Entry view for accounting documents."""
    template_name = 'accounting/documents/entry.html'
    feature_code = 'accounting.documents.entry'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'سند ورودی'
        return context


class AccountingDocumentExitView(FeaturePermissionRequiredMixin, TemplateView):
    """Exit view for accounting documents."""
    template_name = 'accounting/documents/exit.html'
    feature_code = 'accounting.documents.exit'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'سند خروجی'
        return context


# Treasury (خزانه)
class TreasuryExpenseView(FeaturePermissionRequiredMixin, TemplateView):
    """Expense document view for treasury."""
    template_name = 'accounting/treasury/expense.html'
    feature_code = 'accounting.treasury.expense'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'سند هزینه'
        return context


class TreasuryIncomeView(FeaturePermissionRequiredMixin, TemplateView):
    """Income document view for treasury."""
    template_name = 'accounting/treasury/income.html'
    feature_code = 'accounting.treasury.income'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'سند درآمد'
        return context


# Payroll (حقوق و دستمزد)
class PayrollDocumentView(FeaturePermissionRequiredMixin, TemplateView):
    """Payroll document view."""
    template_name = 'accounting/payroll/document.html'
    feature_code = 'accounting.payroll.document'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'سند حقوق دستمزد'
        return context


class PayrollDecreeListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for payroll decrees."""
    template_name = 'accounting/payroll/decree_list.html'
    feature_code = 'accounting.payroll.decrees'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'حکم‌ها'
        return context


class PayrollDecreeGroupListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for payroll decree groups."""
    template_name = 'accounting/payroll/decree_group_list.html'
    feature_code = 'accounting.payroll.decree_groups'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'گروه‌بندی حکم‌ها'
        return context


class PayrollDecreeSubGroupListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for payroll decree sub-groups."""
    template_name = 'accounting/payroll/decree_subgroup_list.html'
    feature_code = 'accounting.payroll.decree_subgroups'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'زیر گروه‌بندی حکم‌ها'
        return context

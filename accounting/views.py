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
class PayrollPaymentView(FeaturePermissionRequiredMixin, TemplateView):
    """Payroll payment processing view."""
    template_name = 'accounting/payroll/payment.html'
    feature_code = 'accounting.payroll.payment'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'پرداخت حقوق و دستمزد'
        return context


class PayrollInsuranceTaxSettingsView(FeaturePermissionRequiredMixin, TemplateView):
    """Insurance and tax settings view."""
    template_name = 'accounting/payroll/insurance_tax_settings.html'
    feature_code = 'accounting.payroll.insurance_tax'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تنظیمات بیمه و مالیات'
        return context


class PayrollDocumentView(FeaturePermissionRequiredMixin, TemplateView):
    """Payroll document upload view."""
    template_name = 'accounting/payroll/document.html'
    feature_code = 'accounting.payroll.document'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'بارگذاری اسناد حقوق و دستمزد'
        return context


class PayrollBankTransferView(FeaturePermissionRequiredMixin, TemplateView):
    """Bank transfer file generation view."""
    template_name = 'accounting/payroll/bank_transfer.html'
    feature_code = 'accounting.payroll.bank_transfer'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'خروجی حقوق و دستمزد برای بانک'
        return context


# Treasury - Additional Views
class TreasuryAccountsView(FeaturePermissionRequiredMixin, TemplateView):
    """Cash and bank accounts management view."""
    template_name = 'accounting/treasury/accounts.html'
    feature_code = 'accounting.treasury.accounts'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'حساب‌های نقدی و بانکی'
        return context


class TreasuryTransactionsView(FeaturePermissionRequiredMixin, TemplateView):
    """Treasury transactions view."""
    template_name = 'accounting/treasury/transactions.html'
    feature_code = 'accounting.treasury.transactions'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تراکنش‌های خزانه'
        return context


class TreasuryChecksView(FeaturePermissionRequiredMixin, TemplateView):
    """Check management view."""
    template_name = 'accounting/treasury/checks.html'
    feature_code = 'accounting.treasury.checks'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'مدیریت چک‌ها'
        return context


class TreasuryReconciliationView(FeaturePermissionRequiredMixin, TemplateView):
    """Bank reconciliation view."""
    template_name = 'accounting/treasury/reconciliation.html'
    feature_code = 'accounting.treasury.reconciliation'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تطبیق بانکی'
        return context


# Income & Expense
class IncomeExpenseIncomeView(FeaturePermissionRequiredMixin, TemplateView):
    """Income records view."""
    template_name = 'accounting/income_expense/income.html'
    feature_code = 'accounting.income_expense.income'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'ثبت درآمد'
        return context


class IncomeExpenseExpenseView(FeaturePermissionRequiredMixin, TemplateView):
    """Expense records view."""
    template_name = 'accounting/income_expense/expense.html'
    feature_code = 'accounting.income_expense.expense'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'ثبت هزینه'
        return context


class IncomeExpenseCategoriesView(FeaturePermissionRequiredMixin, TemplateView):
    """Income and expense categories view."""
    template_name = 'accounting/income_expense/categories.html'
    feature_code = 'accounting.income_expense.categories'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'دسته‌بندی درآمد و هزینه'
        return context


class CostCentersView(FeaturePermissionRequiredMixin, TemplateView):
    """Cost centers view."""
    template_name = 'accounting/income_expense/cost_centers.html'
    feature_code = 'accounting.income_expense.cost_centers'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'مرکز هزینه'
        return context


# Party Accounts
class PartiesView(FeaturePermissionRequiredMixin, TemplateView):
    """Parties management view."""
    template_name = 'accounting/parties/list.html'
    feature_code = 'accounting.parties.list'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'طرف حساب‌ها'
        return context


class PartyAccountsView(FeaturePermissionRequiredMixin, TemplateView):
    """Party accounts view."""
    template_name = 'accounting/parties/accounts.html'
    feature_code = 'accounting.parties.accounts'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'حساب‌های طرف حساب'
        return context


class PartyTransactionsView(FeaturePermissionRequiredMixin, TemplateView):
    """Party transactions view."""
    template_name = 'accounting/parties/transactions.html'
    feature_code = 'accounting.parties.transactions'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تراکنش‌های طرف حساب'
        return context


# Tax Compliance
class TaxVATView(FeaturePermissionRequiredMixin, TemplateView):
    """VAT management view."""
    template_name = 'accounting/tax/vat.html'
    feature_code = 'accounting.tax.vat'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'مدیریت VAT'
        return context


class TaxTTMSView(FeaturePermissionRequiredMixin, TemplateView):
    """TTMS integration view."""
    template_name = 'accounting/tax/ttms.html'
    feature_code = 'accounting.tax.ttms'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'TTMS Integration'
        return context


class TaxSeasonalView(FeaturePermissionRequiredMixin, TemplateView):
    """Seasonal transaction report view."""
    template_name = 'accounting/tax/seasonal.html'
    feature_code = 'accounting.tax.seasonal'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'گزارش فصلی'
        return context


# Financial Reports
class ReportBalanceSheetView(FeaturePermissionRequiredMixin, TemplateView):
    """Balance sheet report view."""
    template_name = 'accounting/reports/balance_sheet.html'
    feature_code = 'accounting.reports.balance_sheet'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'ترازنامه'
        return context


class ReportIncomeStatementView(FeaturePermissionRequiredMixin, TemplateView):
    """Income statement report view."""
    template_name = 'accounting/reports/income_statement.html'
    feature_code = 'accounting.reports.income_statement'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'صورت سود و زیان'
        return context


class ReportAccountMovementsView(FeaturePermissionRequiredMixin, TemplateView):
    """Account movements report view."""
    template_name = 'accounting/reports/account_movements.html'
    feature_code = 'accounting.reports.account_movements'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'گردش حساب'
        return context


class ReportTrialBalanceView(FeaturePermissionRequiredMixin, TemplateView):
    """Trial balance report view."""
    template_name = 'accounting/reports/trial_balance.html'
    feature_code = 'accounting.reports.trial_balance'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تراز آزمایشی'
        return context


class ReportPartyStatementView(FeaturePermissionRequiredMixin, TemplateView):
    """Party account statement report view."""
    template_name = 'accounting/reports/party_statement.html'
    feature_code = 'accounting.reports.party_statement'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'گزارش تفصیلی طرف حساب'
        return context


class ReportVATView(FeaturePermissionRequiredMixin, TemplateView):
    """VAT report view."""
    template_name = 'accounting/reports/vat.html'
    feature_code = 'accounting.reports.vat'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'گزارش VAT'
        return context


# Settings
class SettingsView(FeaturePermissionRequiredMixin, TemplateView):
    """Accounting settings view."""
    template_name = 'accounting/settings.html'
    feature_code = 'accounting.settings'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تنظیمات حسابداری'
        return context


# Document Attachments (بارگذاری اسناد) - imported from views package

# Placeholder views for new menu items
class AccountingDocumentCreateView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/documents/create.html'
    feature_code = 'accounting.documents.create'
    required_action = 'view'

class AccountingDocumentListView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/documents/list.html'
    feature_code = 'accounting.documents.list'
    required_action = 'view'

class AccountingDocumentStatusView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/documents/status.html'
    feature_code = 'accounting.documents.status'
    required_action = 'view'

class TafsiliMovementsView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/reports/tafsili_movements.html'
    feature_code = 'accounting.documents.tafsili_movements'
    required_action = 'view'

class TreasuryReceiveView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/treasury/receive.html'
    feature_code = 'accounting.treasury.receive'
    required_action = 'view'

class TreasuryPayView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/treasury/pay.html'
    feature_code = 'accounting.treasury.pay'
    required_action = 'view'

class TreasuryTransferView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/treasury/transfer.html'
    feature_code = 'accounting.treasury.transfer'
    required_action = 'view'

class TreasuryCashReportView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/treasury/cash_report.html'
    feature_code = 'accounting.treasury.cash_report'
    required_action = 'view'

class CostAllocationView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/income_expense/cost_allocation.html'
    feature_code = 'accounting.income_expense.cost_allocation'
    required_action = 'view'

class IncomeReportView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/income_expense/income_report.html'
    feature_code = 'accounting.income_expense.income_report'
    required_action = 'view'

class ExpenseReportView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/income_expense/expense_report.html'
    feature_code = 'accounting.income_expense.expense_report'
    required_action = 'view'

class CostCenterReportView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/income_expense/cost_center_report.html'
    feature_code = 'accounting.income_expense.cost_center_report'
    required_action = 'view'

class PartyMovementsView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/parties/movements.html'
    feature_code = 'accounting.parties.movements'
    required_action = 'view'

class PartyBalanceReportView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/parties/balance_report.html'
    feature_code = 'accounting.parties.balance_report'
    required_action = 'view'

class TaxValidationView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/tax/validation.html'
    feature_code = 'accounting.tax.validation'
    required_action = 'view'

class TaxDiscrepancyReportView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/tax/discrepancy_report.html'
    feature_code = 'accounting.tax.discrepancy_report'
    required_action = 'view'

class ReportCashFlowView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/reports/cash_flow.html'
    feature_code = 'accounting.reports.cash_flow'
    required_action = 'view'

class ReportTafsiliCostCenterView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/reports/tafsili_cost_center.html'
    feature_code = 'accounting.reports.tafsili_cost_center'
    required_action = 'view'

class ReportChecksView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/reports/checks.html'
    feature_code = 'accounting.reports.check_report'
    required_action = 'view'

class ReportTreasuryView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/reports/treasury.html'
    feature_code = 'accounting.reports.treasury_report'
    required_action = 'view'

class ReportMonthlyView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/reports/monthly.html'
    feature_code = 'accounting.reports.monthly'
    required_action = 'view'

class AttachmentAttachView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/attachments/attach.html'
    feature_code = 'accounting.attachments.attach_to_document'
    required_action = 'view'

class CloseTempAccountsView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/utils/close_temp_accounts.html'
    feature_code = 'accounting.utils.close_temp'
    required_action = 'view'

class OpeningEntryView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/utils/opening_entry.html'
    feature_code = 'accounting.utils.opening'
    required_action = 'view'

class ClosingEntryView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/utils/closing_entry.html'
    feature_code = 'accounting.utils.closing'
    required_action = 'view'

class IntegrationView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/utils/integration.html'
    feature_code = 'accounting.utils.integration'
    required_action = 'view'

class BackupRestoreView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/utils/backup_restore.html'
    feature_code = 'accounting.utils.backup'
    required_action = 'view'

class SettingsTreasuryView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/settings/treasury.html'
    feature_code = 'accounting.settings.treasury'
    required_action = 'view'

class SettingsTaxView(FeaturePermissionRequiredMixin, TemplateView):
    template_name = 'accounting/settings/tax.html'
    feature_code = 'accounting.settings.tax'
    required_action = 'view'



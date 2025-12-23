"""
Views for accounting module.
"""
from django.views.generic import TemplateView, CreateView, View
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy, NoReverseMatch
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import BaseCreateView, BaseFormsetCreateView, BaseListView
from accounting.views.base import AccountingBaseView
from accounting.models import CostCenter, IncomeExpenseCategory, Party, PartyAccount, TreasuryAccount
from accounting.forms import CostCenterForm, IncomeExpenseCategoryForm, PartyForm, PartyAccountForm, TreasuryAccountForm


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
        try:
            context['create_url'] = reverse('accounting:treasury_account_create')
        except NoReverseMatch:
            context['create_url'] = None
        return context


class TreasuryAccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create treasury account view."""
    model = TreasuryAccount
    form_class = TreasuryAccountForm
    template_name = 'accounting/treasury/account_form.html'
    success_url = reverse_lazy('accounting:treasury_accounts')
    feature_code = 'accounting.treasury.accounts'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('حساب نقدی/بانکی با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ایجاد حساب نقدی/بانکی'
        context['form_title'] = 'ایجاد حساب نقدی/بانکی'
        context['breadcrumbs'] = [
            {'label': 'داشبورد', 'url': reverse('ui:dashboard')},
            {'label': 'حسابداری', 'url': reverse('accounting:dashboard')},
            {'label': 'حساب‌های نقدی و بانکی', 'url': reverse('accounting:treasury_accounts')},
            {'label': 'ایجاد'},
        ]
        context['cancel_url'] = reverse('accounting:treasury_accounts')
        context['company_id'] = self.request.session.get('active_company_id')
        return context


class TreasuryAccountSubAccountsAPIView(FeaturePermissionRequiredMixin, TemplateView):
    """API endpoint to get sub accounts for a tafsili account."""
    feature_code = 'accounting.treasury.accounts'
    required_action = 'view'

    def get(self, request, *args, **kwargs):
        tafsili_account_id = request.GET.get('tafsili_account_id')
        company_id = request.session.get('active_company_id')
        
        if not tafsili_account_id or not company_id:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        try:
            from ..models import TafsiliSubAccountRelation, Account
            relations = TafsiliSubAccountRelation.objects.filter(
                company_id=company_id,
                tafsili_account_id=tafsili_account_id,
            ).select_related('sub_account').order_by('-is_primary', 'sub_account__account_code')
            
            sub_accounts = []
            for relation in relations:
                sub_accounts.append({
                    'id': relation.sub_account.id,
                    'code': relation.sub_account.account_code,
                    'name': relation.sub_account.account_name,
                    'is_primary': relation.is_primary,
                })
            
            return JsonResponse({
                'sub_accounts': sub_accounts,
                'count': len(sub_accounts),
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class TreasuryAccountGLAccountsAPIView(FeaturePermissionRequiredMixin, TemplateView):
    """API endpoint to get GL accounts for a sub account."""
    feature_code = 'accounting.treasury.accounts'
    required_action = 'view'

    def get(self, request, *args, **kwargs):
        sub_account_id = request.GET.get('sub_account_id')
        company_id = request.session.get('active_company_id')
        
        if not sub_account_id or not company_id:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        try:
            from ..models import SubAccountGLAccountRelation, Account
            relations = SubAccountGLAccountRelation.objects.filter(
                company_id=company_id,
                sub_account_id=sub_account_id,
            ).select_related('gl_account').order_by('-is_primary', 'gl_account__account_code')
            
            gl_accounts = []
            for relation in relations:
                gl_accounts.append({
                    'id': relation.gl_account.id,
                    'code': relation.gl_account.account_code,
                    'name': relation.gl_account.account_name,
                    'is_primary': relation.is_primary,
                })
            
            return JsonResponse({
                'gl_accounts': gl_accounts,
                'count': len(gl_accounts),
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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
        context['create_url'] = reverse('accounting:income_expense_category_create')
        return context


class IncomeExpenseCategoryCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create income/expense category view."""
    model = IncomeExpenseCategory
    form_class = IncomeExpenseCategoryForm
    template_name = 'accounting/income_expense/category_form.html'
    success_url = reverse_lazy('accounting:income_expense_categories')
    feature_code = 'accounting.income_expense.categories'
    required_action = 'create'

    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        """Set created_by and show success message."""
        form.instance.created_by = self.request.user
        messages.success(self.request, _('دسته‌بندی درآمد/هزینه با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for form template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ایجاد دسته‌بندی درآمد/هزینه'
        context['form_title'] = 'ایجاد دسته‌بندی درآمد/هزینه'
        context['breadcrumbs'] = [
            {'label': 'داشبورد', 'url': reverse('ui:dashboard')},
            {'label': 'حسابداری', 'url': reverse('accounting:dashboard')},
            {'label': 'دسته‌بندی درآمد و هزینه', 'url': reverse('accounting:income_expense_categories')},
            {'label': 'ایجاد'},
        ]
        context['cancel_url'] = reverse('accounting:income_expense_categories')
        return context


class CostCentersView(FeaturePermissionRequiredMixin, TemplateView):
    """Cost centers view."""
    template_name = 'accounting/income_expense/cost_centers.html'
    feature_code = 'accounting.income_expense.cost_centers'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'مراکز هزینه'
        context['create_url'] = reverse('accounting:cost_center_create')
        return context


class CostCenterCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create cost center view."""
    model = CostCenter
    form_class = CostCenterForm
    template_name = 'accounting/income_expense/cost_center_form.html'
    success_url = reverse_lazy('accounting:cost_centers')
    feature_code = 'accounting.income_expense.cost_centers'
    required_action = 'create'

    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        """Set created_by and show success message."""
        form.instance.created_by = self.request.user
        messages.success(self.request, _('مرکز هزینه با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for form template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ایجاد مرکز هزینه'
        context['form_title'] = 'ایجاد مرکز هزینه'
        context['breadcrumbs'] = [
            {'label': 'داشبورد', 'url': reverse('ui:dashboard')},
            {'label': 'حسابداری', 'url': reverse('accounting:dashboard')},
            {'label': 'مراکز هزینه', 'url': reverse('accounting:cost_centers')},
            {'label': 'ایجاد'},
        ]
        context['cancel_url'] = reverse('accounting:cost_centers')
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
        context['create_url'] = reverse('accounting:party_create')
        context['party_accounts_url'] = reverse('accounting:party_accounts')
        return context


class PartyCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create party view."""
    model = Party
    form_class = PartyForm
    template_name = 'accounting/parties/party_form.html'
    success_url = reverse_lazy('accounting:parties')
    feature_code = 'accounting.parties.list'
    required_action = 'create'

    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        """Set created_by and show success message."""
        form.instance.created_by = self.request.user
        messages.success(self.request, _('طرف حساب با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for form template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ایجاد طرف حساب'
        context['form_title'] = 'ایجاد طرف حساب'
        context['breadcrumbs'] = [
            {'label': 'داشبورد', 'url': reverse('ui:dashboard')},
            {'label': 'حسابداری', 'url': reverse('accounting:dashboard')},
            {'label': 'طرف حساب‌ها', 'url': reverse('accounting:parties')},
            {'label': 'ایجاد'},
        ]
        context['cancel_url'] = reverse('accounting:parties')
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
        context['create_url'] = reverse('accounting:party_account_create')
        context['parties_url'] = reverse('accounting:parties')
        return context


class PartyAccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create party account view."""
    model = PartyAccount
    form_class = PartyAccountForm
    template_name = 'accounting/parties/party_account_form.html'
    success_url = reverse_lazy('accounting:party_accounts')
    feature_code = 'accounting.parties.accounts'
    required_action = 'create'

    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        """Set created_by and show success message."""
        form.instance.created_by = self.request.user
        messages.success(self.request, _('حساب طرف حساب با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for form template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ایجاد حساب طرف حساب'
        context['form_title'] = 'ایجاد حساب طرف حساب'
        context['breadcrumbs'] = [
            {'label': 'داشبورد', 'url': reverse('ui:dashboard')},
            {'label': 'حسابداری', 'url': reverse('accounting:dashboard')},
            {'label': 'حساب‌های طرف حساب', 'url': reverse('accounting:party_accounts')},
            {'label': 'ایجاد'},
        ]
        context['cancel_url'] = reverse('accounting:party_accounts')
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
class AccountingDocumentCreateView(BaseFormsetCreateView):
    """Create accounting document view."""
    from accounting.models.documents import AccountingDocument
    from accounting.forms import AccountingDocumentForm, AccountingDocumentLineFormSet
    
    model = AccountingDocument
    form_class = AccountingDocumentForm
    formset_class = AccountingDocumentLineFormSet
    formset_prefix = 'lines'
    template_name = 'accounting/documents/create.html'
    feature_code = 'accounting.documents.create'
    required_action = 'create'
    success_url = reverse_lazy('accounting:document_list')
    success_message = _('سند حسابداری با موفقیت ایجاد شد.')
    
    def get_breadcrumbs(self):
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('اسناد حسابداری'), 'url': reverse('accounting:document_list')},
            {'label': _('ایجاد سند'), 'url': None},
        ]
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_formset_kwargs(self):
        kwargs = {}
        if hasattr(self, 'object') and self.object:
            kwargs['instance'] = self.object
        
        # Pass company_id to each form in formset
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['form_kwargs'] = {'company_id': company_id}
        
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add formset with company_id to each form and auto-fill document info."""
        context = super().get_context_data(**kwargs)
        company_id = self.request.session.get('active_company_id')
        
        # Auto-fill document form fields
        if 'form' in context and company_id:
            from django.utils import timezone
            from accounting.models.fiscal_years import FiscalYear
            
            form = context['form']
            
            # Set document_date to today if not set
            if not form.instance.pk and not form.initial.get('document_date'):
                today = timezone.now().date()
                form.initial['document_date'] = today
                if 'document_date' in form.fields:
                    form.fields['document_date'].widget.attrs['value'] = today.isoformat()
                context['document_date_display'] = today
            
            # Auto-select fiscal year
            if not form.instance.pk:
                document_date = form.initial.get('document_date') or timezone.now().date()
                fiscal_year = FiscalYear.objects.filter(
                    company_id=company_id,
                    is_enabled=1,
                    start_date__lte=document_date,
                    end_date__gte=document_date
                ).first()
                if not fiscal_year:
                    fiscal_year = FiscalYear.objects.filter(
                        company_id=company_id,
                        is_enabled=1
                    ).order_by('-start_date').first()
                
                if fiscal_year:
                    form.initial['fiscal_year'] = fiscal_year.pk
                    if 'fiscal_year' in form.fields:
                        form.fields['fiscal_year'].queryset = FiscalYear.objects.filter(pk=fiscal_year.pk)
                    context['fiscal_year_display'] = fiscal_year.fiscal_year_name or f"{fiscal_year.start_date.year}-{fiscal_year.end_date.year}"
            
            # Set defaults
            if not form.instance.pk:
                form.initial['status'] = 'DRAFT'
                form.initial['document_type'] = 'MANUAL'
        
        # Update formset forms with company_id and set querysets
        if 'formset' in context and company_id:
            from accounting.models.accounts import Account
            for form in context['formset'].forms:
                form.company_id = company_id
                
                # Set querysets for account fields
                if hasattr(form, 'fields'):
                    # GL Accounts (level 1)
                    if 'gl_account' in form.fields:
                        form.fields['gl_account'].queryset = Account.objects.filter(
                            company_id=company_id,
                            account_level=1,
                            is_enabled=1
                        ).order_by('account_code')
                    
                    # Sub Accounts (level 2)
                    if 'sub_account' in form.fields:
                        form.fields['sub_account'].queryset = Account.objects.filter(
                            company_id=company_id,
                            account_level=2,
                            is_enabled=1
                        ).order_by('account_code')
                    
                    # Tafsili Accounts (level 3)
                    if 'tafsili_account' in form.fields:
                        form.fields['tafsili_account'].queryset = Account.objects.filter(
                            company_id=company_id,
                            account_level=3,
                            is_enabled=1
                        ).order_by('account_code')
        
        return context
    
    def form_valid(self, form):
        """Save form and formset, calculate totals and generate document number."""
        from django.db import transaction
        from decimal import Decimal
        from django.utils import timezone
        from inventory.utils.codes import generate_sequential_code
        from accounting.models.fiscal_years import FiscalYear
        
        # Validate formset BEFORE saving anything
        formset = self.formset_class(
            self.request.POST,
            prefix=self.formset_prefix,
            **self.get_formset_kwargs()
        )
        
        # Set company_id for each form in formset
        company_id = self.request.session.get('active_company_id')
        for formset_form in formset.forms:
            if company_id:
                formset_form.company_id = company_id
        
        # Check formset validity first
        if not formset.is_valid():
            return self.form_invalid(form)
        
        with transaction.atomic():
            
            # Set created_by
            form.instance.created_by = self.request.user
            
            # Auto-fill document fields (override any user input)
            if company_id:
                # Set document_date to today
                form.instance.document_date = timezone.now().date()
                
                # Set fiscal_year based on document_date
                fiscal_year = FiscalYear.objects.filter(
                    company_id=company_id,
                    is_enabled=1,
                    start_date__lte=form.instance.document_date,
                    end_date__gte=form.instance.document_date
                ).first()
                if not fiscal_year:
                    fiscal_year = FiscalYear.objects.filter(
                        company_id=company_id,
                        is_enabled=1
                    ).order_by('-start_date').first()
                if fiscal_year:
                    form.instance.fiscal_year = fiscal_year
                
                # Set defaults
                form.instance.document_type = 'MANUAL'
                form.instance.status = 'DRAFT'
                
                # Generate document number if not set
                if not form.instance.document_number:
                    from accounting.models.documents import AccountingDocument
                    form.instance.document_number = generate_sequential_code(
                        AccountingDocument,
                        company_id=company_id,
                        field='document_number',
                        width=10,
                    )
            
            # Save main document using BaseCreateView (skip BaseFormsetCreateView to avoid double formset save)
            from shared.views.base import BaseCreateView
            response = BaseCreateView.form_valid(self, form)
            
            # Set line numbers and sort_order
            lines = formset.save(commit=False)
            
            for idx, line in enumerate(lines, start=1):
                line.line_number = idx
                line.sort_order = idx
                
                # Set document and company
                line.document = self.object
                if not line.company_id:
                    line.company = self.object.company
                
                # Ensure debit/credit are not NULL
                if line.debit is None:
                    line.debit = Decimal('0.00')
                if line.credit is None:
                    line.credit = Decimal('0.00')
                
                line.save()
            
            # Delete removed lines
            for line in formset.deleted_objects:
                line.delete()
            
            # Calculate totals
            total_debit = Decimal('0.00')
            total_credit = Decimal('0.00')
            for line in self.object.lines.all():
                total_debit += line.debit
                total_credit += line.credit
            
            self.object.total_debit = total_debit
            self.object.total_credit = total_credit
            self.object.save(update_fields=['total_debit', 'total_credit'])
        
        return response

class AccountingDocumentDetailView(FeaturePermissionRequiredMixin, TemplateView):
    """Detail view for accounting document."""
    template_name = 'accounting/documents/detail.html'
    feature_code = 'accounting.documents.detail'
    required_action = 'view'
    
    def get_context_data(self, **kwargs):
        from django.shortcuts import get_object_or_404
        from accounting.models.documents import AccountingDocument
        
        context = super().get_context_data(**kwargs)
        company_id = self.request.session.get('active_company_id')
        
        document = get_object_or_404(
            AccountingDocument.objects.filter(company_id=company_id),
            pk=kwargs['pk']
        )
        
        context['document'] = document
        context['active_module'] = 'accounting'
        context['page_title'] = f'سند حسابداری {document.document_number}'
        context['breadcrumbs'] = [
            {'label': 'داشبورد', 'url': reverse('ui:dashboard')},
            {'label': 'حسابداری', 'url': reverse('accounting:dashboard')},
            {'label': 'اسناد حسابداری', 'url': reverse('accounting:document_list')},
            {'label': 'مشاهده سند'},
        ]
        return context


class AccountingDocumentUpdateView(FeaturePermissionRequiredMixin, TemplateView):
    """Update view for accounting document - placeholder."""
    template_name = 'accounting/documents/placeholder.html'
    feature_code = 'accounting.documents.edit'
    required_action = 'edit'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'ویرایش سند حسابداری'
        context['message'] = 'قابلیت ویرایش سند در حال توسعه است.'
        context['back_url'] = reverse('accounting:document_list')
        return context


class AccountingDocumentDeleteView(FeaturePermissionRequiredMixin, View):
    """Delete view for accounting document."""
    feature_code = 'accounting.documents.delete'
    required_action = 'delete'
    
    def get(self, request, pk):
        """Show confirmation page."""
        from django.shortcuts import get_object_or_404, render
        from accounting.models.documents import AccountingDocument
        
        company_id = request.session.get('active_company_id')
        document = get_object_or_404(
            AccountingDocument.objects.filter(company_id=company_id),
            pk=pk
        )
        
        context = {
            'document': document,
            'active_module': 'accounting',
            'page_title': 'حذف سند حسابداری',
            'breadcrumbs': [
                {'label': 'داشبورد', 'url': reverse('ui:dashboard')},
                {'label': 'حسابداری', 'url': reverse('accounting:dashboard')},
                {'label': 'اسناد حسابداری', 'url': reverse('accounting:document_list')},
                {'label': 'حذف سند'},
            ]
        }
        
        return render(request, 'accounting/documents/delete_confirm.html', context)
    
    def post(self, request, pk):
        """Delete the document."""
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        from accounting.models.documents import AccountingDocument
        
        company_id = request.session.get('active_company_id')
        document = get_object_or_404(
            AccountingDocument.objects.filter(company_id=company_id),
            pk=pk
        )
        
        # Check if document is locked
        if document.status == 'LOCKED':
            messages.error(request, 'نمی‌توانید سند قفل شده را حذف کنید.')
            return redirect('accounting:document_detail', pk=pk)
        
        document_number = document.document_number
        document.delete()
        
        messages.success(request, f'سند {document_number} با موفقیت حذف شد.')
        return redirect('accounting:document_list')


class AccountingDocumentListView(BaseListView):
    """List all accounting documents."""
    from accounting.models.documents import AccountingDocument
    
    model = AccountingDocument
    template_name = 'accounting/documents/list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.documents.list'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['-document_date', '-document_number']
    default_status_filter = False
    
    def get_base_queryset(self):
        """Get base queryset filtered by company."""
        from accounting.models.documents import AccountingDocument
        queryset = AccountingDocument.objects.all()
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['document_number', 'description', 'reference_number']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('اسناد حسابداری')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('اسناد حسابداری'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:document_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('ایجاد سند حسابداری')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:document_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:document_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:document_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('هیچ سند حسابداری یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با ایجاد اولین سند حسابداری شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📄'
    
    def get_context_data(self, **kwargs):
        """Add context variables for generic_list template."""
        from accounting.models.documents import AccountingDocument
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('شماره سند'), 'field': 'document_number', 'type': 'code'},
            {'label': _('تاریخ سند'), 'field': 'document_date', 'type': 'date'},
            {'label': _('نوع سند'), 'field': 'document_type', 'type': 'custom'},
            {'label': _('شرح'), 'field': 'description'},
            {'label': _('بدهکار'), 'field': 'total_debit', 'type': 'number'},
            {'label': _('بستانکار'), 'field': 'total_credit', 'type': 'number'},
            {'label': _('وضعیت'), 'field': 'status', 'type': 'badge'},
        ]
        
        # Add custom display for document_type
        for obj in context['object_list']:
            obj.document_type_display = dict(AccountingDocument.DOCUMENT_TYPE_CHOICES).get(obj.document_type, obj.document_type)
            obj.status_display = dict(AccountingDocument.STATUS_CHOICES).get(obj.status, obj.status)
        
        context['print_enabled'] = True
        return context

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


# Warehouse Accounting (حسابداری انبار)
class WarehouseExpenseView(FeaturePermissionRequiredMixin, TemplateView):
    """Warehouse expense document view with tabs for documents and receipts."""
    template_name = 'accounting/warehouse/expense.html'
    feature_code = 'accounting.warehouse.expense'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        from .models import WarehouseExpenseDocument
        from inventory.models import ReceiptPermanent, ReceiptTemporary, ReceiptConsignment
        
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'سند هزینه انبار'
        
        # Get active tab from query parameter (default: 'documents')
        active_tab = self.request.GET.get('tab', 'documents')
        context['active_tab'] = active_tab
        
        company_id = self.request.session.get('active_company_id')
        
        # Get warehouse expense documents
        expense_documents = WarehouseExpenseDocument.objects.filter(
            company_id=company_id
        ).order_by('-document_date', '-id')
        context['expense_documents'] = expense_documents
        
        # Get existing expense document receipt IDs for filtering
        existing_permanent_ids = set(
            WarehouseExpenseDocument.objects.filter(
                company_id=company_id,
                receipt_type='PERMANENT'
            ).values_list('receipt_id', flat=True)
        )
        existing_temporary_ids = set(
            WarehouseExpenseDocument.objects.filter(
                company_id=company_id,
                receipt_type='TEMPORARY'
            ).values_list('receipt_id', flat=True)
        )
        existing_consignment_ids = set(
            WarehouseExpenseDocument.objects.filter(
                company_id=company_id,
                receipt_type='CONSIGNMENT'
            ).values_list('receipt_id', flat=True)
        )
        
        # Get receipts (permanent, temporary, consignment)
        permanent_receipts = ReceiptPermanent.objects.filter(
            company_id=company_id
        ).order_by('-document_date', '-id')[:100]  # Limit to 100 most recent
        
        temporary_receipts = ReceiptTemporary.objects.filter(
            company_id=company_id
        ).order_by('-document_date', '-id')[:100]
        
        consignment_receipts = ReceiptConsignment.objects.filter(
            company_id=company_id
        ).order_by('-document_date', '-id')[:100]
        
        # Add has_expense_document attribute to each receipt
        for receipt in permanent_receipts:
            receipt.has_expense_document = receipt.pk in existing_permanent_ids
        
        for receipt in temporary_receipts:
            receipt.has_expense_document = receipt.pk in existing_temporary_ids
        
        for receipt in consignment_receipts:
            receipt.has_expense_document = receipt.pk in existing_consignment_ids
        
        context['permanent_receipts'] = permanent_receipts
        context['temporary_receipts'] = temporary_receipts
        context['consignment_receipts'] = consignment_receipts
        
        return context


class WarehouseExpenseCreateView(BaseFormsetCreateView):
    """Create warehouse expense document view."""
    from .models import WarehouseExpenseDocument
    from .forms import WarehouseExpenseDocumentForm, WarehouseExpenseDocumentLineFormSet
    
    model = WarehouseExpenseDocument
    form_class = WarehouseExpenseDocumentForm
    formset_class = WarehouseExpenseDocumentLineFormSet
    formset_prefix = 'lines'
    template_name = 'accounting/warehouse/expense_form.html'
    feature_code = 'accounting.warehouse.expense'
    success_url = reverse_lazy('accounting:warehouse_expense')
    success_message = _('سند هزینه انبار با موفقیت ایجاد شد.')
    
    def get_breadcrumbs(self):
        return [
            {'label': _('حسابداری'), 'url': reverse('accounting:dashboard')},
            {'label': _('سند هزینه انبار'), 'url': reverse('accounting:warehouse_expense')},
            {'label': _('ایجاد سند هزینه'), 'url': None},
        ]
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def form_valid(self, form):
        """Save form and formset, calculate total_amount."""
        from django.db import transaction
        from decimal import Decimal
        
        with transaction.atomic():
            # Save main document first
            response = super().form_valid(form)
            
            # Save formset
            formset = self.formset_class(
                self.request.POST,
                instance=self.object,
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
            
            if formset.is_valid():
                formset.save()
                
                # Calculate total_amount from lines
                total = Decimal('0.00')
                for line in self.object.lines.all():
                    if line.total_price:
                        total += line.total_price
                
                self.object.total_amount = total
                self.object.save(update_fields=['total_amount'])
            else:
                # Formset validation failed
                return self.form_invalid(form)
        
        return response


class WarehouseExpenseDetailView(FeaturePermissionRequiredMixin, TemplateView):
    """Detail view for warehouse expense document."""
    template_name = 'accounting/warehouse/expense_detail.html'
    feature_code = 'accounting.warehouse.expense'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        from .models import WarehouseExpenseDocument
        from django.shortcuts import get_object_or_404
        
        context = super().get_context_data(**kwargs)
        company_id = self.request.session.get('active_company_id')
        expense_doc = get_object_or_404(
            WarehouseExpenseDocument.objects.filter(company_id=company_id),
            pk=kwargs['pk']
        )
        context['expense_document'] = expense_doc
        context['active_module'] = 'accounting'
        context['page_title'] = f'مشاهده سند هزینه: {expense_doc.document_code}'
        return context


class WarehouseExpenseCreateFromReceiptView(BaseFormsetCreateView):
    """Create warehouse expense document from receipt."""
    from .models import WarehouseExpenseDocument
    from .forms import WarehouseExpenseDocumentForm, WarehouseExpenseDocumentLineFormSet
    
    model = WarehouseExpenseDocument
    form_class = WarehouseExpenseDocumentForm
    formset_class = WarehouseExpenseDocumentLineFormSet
    formset_prefix = 'lines'
    template_name = 'accounting/warehouse/expense_form.html'
    feature_code = 'accounting.warehouse.expense'
    success_url = reverse_lazy('accounting:warehouse_expense')
    success_message = _('سند هزینه انبار با موفقیت ایجاد شد.')
    
    def get_receipt(self):
        """Get receipt object from URL parameters."""
        from django.shortcuts import get_object_or_404
        from django.http import Http404
        from inventory.models import ReceiptPermanent, ReceiptTemporary, ReceiptConsignment
        
        company_id = self.request.session.get('active_company_id')
        receipt_type = self.kwargs.get('receipt_type')
        receipt_id = self.kwargs.get('receipt_id')
        
        if receipt_type == 'permanent':
            return get_object_or_404(
                ReceiptPermanent.objects.filter(company_id=company_id),
                pk=receipt_id
            )
        elif receipt_type == 'temporary':
            return get_object_or_404(
                ReceiptTemporary.objects.filter(company_id=company_id),
                pk=receipt_id
            )
        elif receipt_type == 'consignment':
            return get_object_or_404(
                ReceiptConsignment.objects.filter(company_id=company_id),
                pk=receipt_id
            )
        else:
            raise Http404("Invalid receipt type")
    
    def get_receipt_lines(self):
        """Get receipt lines based on receipt type."""
        receipt = self.get_receipt()
        
        if hasattr(receipt, 'lines'):
            return receipt.lines.all().order_by('sort_order', 'id')
        return []
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        receipt = self.get_receipt()
        kwargs['receipt'] = receipt
        return kwargs
    
    def get_formset_kwargs(self):
        """Initialize formset with receipt lines data."""
        kwargs = super().get_formset_kwargs()
        
        if self.request.method == 'GET':
            # Pre-populate formset with receipt lines
            receipt = self.get_receipt()
            receipt_lines = self.get_receipt_lines()
            
            initial_data = []
            for line in receipt_lines:
                # Determine unit: use entered_unit if exists, otherwise unit
                unit = line.entered_unit if line.entered_unit else line.unit
                quantity = line.entered_quantity if line.entered_quantity else line.quantity
                
                initial_data.append({
                    'item': line.item,
                    'item_code': line.item_code,
                    'warehouse': line.warehouse,
                    'warehouse_code': line.warehouse_code,
                    'unit': unit,
                    'quantity': quantity,
                    'base_unit': line.item.default_unit if line.item else '',
                })
            
            kwargs['initial'] = initial_data
        
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receipt = self.get_receipt()
        receipt_lines = self.get_receipt_lines()
        
        context['receipt'] = receipt
        context['receipt_type'] = self.kwargs.get('receipt_type')
        context['receipt_lines'] = receipt_lines
        
        return context
    
    def get_breadcrumbs(self):
        receipt = self.get_receipt()
        return [
            {'label': _('حسابداری'), 'url': reverse('accounting:dashboard')},
            {'label': _('سند هزینه انبار'), 'url': reverse('accounting:warehouse_expense')},
            {'label': _('ایجاد سند هزینه از رسید'), 'url': None},
        ]
    
    def form_valid(self, form):
        """Save form and formset, calculate total_amount."""
        from django.db import transaction
        from decimal import Decimal
        
        receipt = self.get_receipt()
        form.instance.receipt_id = receipt.pk
        form.instance.receipt_code = receipt.document_code
        
        with transaction.atomic():
            # Save main document first
            response = super().form_valid(form)
            
            # Save formset
            formset = self.formset_class(
                self.request.POST,
                instance=self.object,
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
            
            if formset.is_valid():
                formset.save()
                
                # Calculate total_amount from lines
                total = Decimal('0.00')
                for line in self.object.lines.all():
                    if line.total_price:
                        total += line.total_price
                
                self.object.total_amount = total
                self.object.save(update_fields=['total_amount'])
            else:
                # Formset validation failed
                return self.form_invalid(form)
        
        return response


class WarehouseExpenseReceiptsAPIView(FeaturePermissionRequiredMixin, View):
    """API endpoint to get receipts list by type for warehouse expense document."""
    feature_code = 'accounting.warehouse.expense'
    required_action = 'view'
    
    def get(self, request):
        """Return list of receipts by type that don't have expense document yet."""
        from django.http import JsonResponse
        from inventory.models import ReceiptPermanent, ReceiptTemporary, ReceiptConsignment
        
        receipt_type = request.GET.get('receipt_type')
        company_id = request.session.get('active_company_id')
        
        if not receipt_type or not company_id:
            return JsonResponse({'error': 'Missing receipt_type or company_id'}, status=400)
        
        # Get existing expense documents to exclude
        from .models import WarehouseExpenseDocument
        existing_receipt_ids = set(
            WarehouseExpenseDocument.objects.filter(
                company_id=company_id,
                receipt_type=receipt_type.upper()
            ).values_list('receipt_id', flat=True)
        )
        
        receipts = []
        
        if receipt_type.upper() == 'PERMANENT':
            queryset = ReceiptPermanent.objects.filter(
                company_id=company_id
            ).exclude(pk__in=existing_receipt_ids).order_by('-document_date', '-id')[:100]
            
            for receipt in queryset:
                receipts.append({
                    'id': receipt.pk,
                    'code': receipt.document_code,
                    'date': receipt.document_date.strftime('%Y-%m-%d') if receipt.document_date else '',
                })
        
        elif receipt_type.upper() == 'TEMPORARY':
            queryset = ReceiptTemporary.objects.filter(
                company_id=company_id
            ).exclude(pk__in=existing_receipt_ids).order_by('-document_date', '-id')[:100]
            
            for receipt in queryset:
                receipts.append({
                    'id': receipt.pk,
                    'code': receipt.document_code,
                    'date': receipt.document_date.strftime('%Y-%m-%d') if receipt.document_date else '',
                })
        
        elif receipt_type.upper() == 'CONSIGNMENT':
            queryset = ReceiptConsignment.objects.filter(
                company_id=company_id
            ).exclude(pk__in=existing_receipt_ids).order_by('-document_date', '-id')[:100]
            
            for receipt in queryset:
                receipts.append({
                    'id': receipt.pk,
                    'code': receipt.document_code,
                    'date': receipt.document_date.strftime('%Y-%m-%d') if receipt.document_date else '',
                })
        
        return JsonResponse({'receipts': receipts})


class WarehouseExpenseReceiptLinesAPIView(FeaturePermissionRequiredMixin, View):
    """API endpoint to get receipt lines for warehouse expense document."""
    feature_code = 'accounting.warehouse.expense'
    required_action = 'view'
    
    def get(self, request):
        """Return receipt lines for a specific receipt."""
        from django.http import JsonResponse
        from django.shortcuts import get_object_or_404
        from django.http import Http404
        from inventory.models import ReceiptPermanent, ReceiptTemporary, ReceiptConsignment
        
        receipt_type = request.GET.get('receipt_type')
        receipt_id = request.GET.get('receipt_id')
        company_id = request.session.get('active_company_id')
        
        if not receipt_type or not receipt_id or not company_id:
            return JsonResponse({'error': 'Missing receipt_type, receipt_id or company_id'}, status=400)
        
        # Get receipt object
        try:
            if receipt_type.upper() == 'PERMANENT':
                receipt = get_object_or_404(
                    ReceiptPermanent.objects.filter(company_id=company_id),
                    pk=receipt_id
                )
            elif receipt_type.upper() == 'TEMPORARY':
                receipt = get_object_or_404(
                    ReceiptTemporary.objects.filter(company_id=company_id),
                    pk=receipt_id
                )
            elif receipt_type.upper() == 'CONSIGNMENT':
                receipt = get_object_or_404(
                    ReceiptConsignment.objects.filter(company_id=company_id),
                    pk=receipt_id
                )
            else:
                return JsonResponse({'error': 'Invalid receipt_type'}, status=400)
        except Http404:
            return JsonResponse({'error': 'Receipt not found'}, status=404)
        
        # Get receipt lines
        lines = []
        if hasattr(receipt, 'lines'):
            for line in receipt.lines.all().order_by('sort_order', 'id'):
                # Determine unit: use entered_unit if exists, otherwise unit
                unit = line.entered_unit if line.entered_unit else line.unit
                quantity = line.entered_quantity if line.entered_quantity else line.quantity
                
                lines.append({
                    'item_id': line.item.pk if line.item else None,
                    'item_code': line.item_code,
                    'item_name': line.item.name if line.item else '',
                    'warehouse_id': line.warehouse.pk if line.warehouse else None,
                    'warehouse_code': line.warehouse_code,
                    'unit': unit,
                    'quantity': str(quantity),
                    'base_unit': line.item.default_unit if line.item else '',
                })
        
        return JsonResponse({
            'receipt_code': receipt.document_code,
            'receipt_date': receipt.document_date.strftime('%Y-%m-%d') if receipt.document_date else '',
            'lines': lines,
        })


class WarehouseIncomeView(FeaturePermissionRequiredMixin, TemplateView):
    """Warehouse income document view."""
    template_name = 'accounting/warehouse/income.html'
    feature_code = 'accounting.warehouse.income'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'سند درآمد انبار'
        return context


class WarehouseOpeningClosingView(FeaturePermissionRequiredMixin, TemplateView):
    """Warehouse opening and closing entries view."""
    template_name = 'accounting/warehouse/opening_closing.html'
    feature_code = 'accounting.warehouse.opening_closing'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'افتتاحیه و اختتامیه'
        return context


class WarehouseSettingsView(FeaturePermissionRequiredMixin, TemplateView):
    """Warehouse accounting settings view."""
    template_name = 'accounting/warehouse/settings.html'
    feature_code = 'accounting.warehouse.settings'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        context['page_title'] = 'تنظیمات حسابداری انبار'
        return context



"""
Views for office automation module.
"""
from django.views.generic import TemplateView
from shared.mixins import FeaturePermissionRequiredMixin


class OfficeAutomationDashboardView(FeaturePermissionRequiredMixin, TemplateView):
    """Dashboard view for office automation module."""
    template_name = 'office_automation/dashboard.html'
    feature_code = 'office_automation.dashboard'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'office_automation'
        context['page_title'] = 'اتوماسیون اداری'
        return context


# Inbox Section (کارتابل)
class InboxIncomingLettersView(FeaturePermissionRequiredMixin, TemplateView):
    """View for incoming letters."""
    template_name = 'office_automation/inbox/incoming_letters.html'
    feature_code = 'office_automation.inbox.incoming'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'office_automation'
        context['page_title'] = 'نامه‌های ورودی'
        return context


class InboxWriteLetterView(FeaturePermissionRequiredMixin, TemplateView):
    """View for writing letters."""
    template_name = 'office_automation/inbox/write_letter.html'
    feature_code = 'office_automation.inbox.write'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'office_automation'
        context['page_title'] = 'نوشتن نامه'
        return context


class InboxFillFormView(FeaturePermissionRequiredMixin, TemplateView):
    """View for filling forms."""
    template_name = 'office_automation/inbox/fill_form.html'
    feature_code = 'office_automation.inbox.fill_form'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'office_automation'
        context['page_title'] = 'پر کردن فرم'
        return context


# Processes Section (فرایندها)
class ProcessEngineView(FeaturePermissionRequiredMixin, TemplateView):
    """View for process engine."""
    template_name = 'office_automation/processes/engine.html'
    feature_code = 'office_automation.processes.engine'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'office_automation'
        context['page_title'] = 'موتور تولید فرایند'
        return context


class ProcessFormConnectionView(FeaturePermissionRequiredMixin, TemplateView):
    """View for connecting processes and forms."""
    template_name = 'office_automation/processes/form_connection.html'
    feature_code = 'office_automation.processes.form_connection'
    required_action = 'edit_own'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'office_automation'
        context['page_title'] = 'ارتباط فرایند و فرم‌ها'
        return context


# Forms Section (فرم‌ها)
class FormBuilderView(FeaturePermissionRequiredMixin, TemplateView):
    """View for form builder."""
    template_name = 'office_automation/forms/builder.html'
    feature_code = 'office_automation.forms.builder'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'office_automation'
        context['page_title'] = 'ساخت فرم'
        return context

"""
Automation views for accounting module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
)
from accounting.models.automation import (
    AutomationProcess,
    AutomationCondition,
    AutomationVariable,
    AutomationDocumentStep,
    AutomationDocumentLine,
    AutomationExecutionLog,
    AutomationDocumentApproval,
)
from accounting.forms.automation import (
    AutomationProcessForm,
    AutomationConditionForm,
    AutomationVariableForm,
)
from accounting.forms.document_steps import (
    AutomationDocumentStepForm,
    AutomationDocumentLineForm,
)
from accounting.views.base import AccountingBaseView


class AutomationProcessListView(BaseListView):
    """
    List all automation processes for the active company.
    """
    model = AutomationProcess
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.automation.processes'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['-created_at']
    default_status_filter = False
    
    def get_base_queryset(self):
        """Get base queryset filtered by company."""
        queryset = super().get_base_queryset()
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['name', 'description', 'trigger_module', 'trigger_document_type']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Automation Processes')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': None},
            {'label': _('Processes'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:automation_process_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Automation Process')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:automation_process_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:automation_process_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:automation_process_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Automation Processes Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first automation process.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '⚙️'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('Name'), 'field': 'name'},
            {'label': _('Trigger Module'), 'field': 'trigger_module'},
            {'label': _('Trigger Document'), 'field': 'trigger_document_type'},
            {'label': _('Status'), 'field': 'is_active', 'type': 'badge',
             'true_label': _('Active'), 'false_label': _('Inactive')},
            {'label': _('Created At'), 'field': 'created_at', 'type': 'datetime'},
        ]
        context['print_enabled'] = True
        return context


class AutomationProcessCreateView(BaseCreateView):
    """Create a new automation process."""
    model = AutomationProcess
    form_class = AutomationProcessForm
    template_name = 'accounting/automation/process_form.html'
    success_url = reverse_lazy('accounting:automation_processes')
    feature_code = 'accounting.automation.processes'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('Automation process created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set created_by and save conditions."""
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Save conditions if provided
        conditions_data = self.request.POST.get('conditions_data')
        if conditions_data:
            import json
            try:
                conditions = json.loads(conditions_data)
                from accounting.models.automation import AutomationCondition
                company_id = self.request.session.get('active_company_id')
                
                for condition_data in conditions:
                    condition = AutomationCondition.objects.create(
                        process=form.instance,
                        company_id=company_id,
                        filter_type=condition_data.get('filter_type'),
                        filter_category=condition_data.get('filter_category'),
                        field_name=condition_data.get('field_name') or None,
                        field_type=condition_data.get('field_type', ''),
                        operator=condition_data.get('operator'),
                        value=condition_data.get('value'),
                        value_type=condition_data.get('value_type', 'static'),
                        logical_operator=condition_data.get('logical_operator', 'AND'),
                        sort_order=condition_data.get('sort_order', 1),
                        is_active=condition_data.get('is_active', True),
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Log error but don't fail the form submission
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error saving automation conditions: {e}')
        
        # Save variables if provided
        variables_data = self.request.POST.get('variables_data')
        if variables_data:
            import json
            try:
                variables = json.loads(variables_data)
                from accounting.models.automation import AutomationVariable
                company_id = self.request.session.get('active_company_id')
                
                for variable_data in variables:
                    variable = AutomationVariable.objects.create(
                        process=form.instance,
                        company_id=company_id,
                        name=variable_data.get('name'),
                        display_name=variable_data.get('display_name', variable_data.get('name')),
                        source_type=variable_data.get('source_type', 'field'),
                        field_path=variable_data.get('field_path'),
                        field_type=variable_data.get('field_type', 'header_field'),
                        aggregation_type=variable_data.get('aggregation_type') or None,
                        data_type=variable_data.get('data_type', 'string'),
                        related_model=variable_data.get('related_model') or None,
                        sort_order=variable_data.get('sort_order', 1),
                        is_active=variable_data.get('is_active', True),
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Log error but don't fail the form submission
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error saving automation variables: {e}')
        
        return response
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_processes')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Automation Process')


class AutomationProcessDetailView(BaseDetailView):
    """View automation process details."""
    model = AutomationProcess
    template_name = 'accounting/automation/process_detail.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'view_all'
    active_module = 'accounting'
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': self.object.name, 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['conditions'] = self.object.conditions.filter(is_active=True).order_by('sort_order')
        context['variables'] = self.object.variables.filter(is_active=True).order_by('sort_order')
        context['document_steps'] = self.object.document_steps.filter(is_active=True).order_by('step_number')
        return context


class AutomationProcessUpdateView(BaseUpdateView):
    """Update an automation process."""
    model = AutomationProcess
    form_class = AutomationProcessForm
    template_name = 'accounting/automation/process_form.html'
    success_url = reverse_lazy('accounting:automation_processes')
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Automation process updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set updated_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': self.object.name, 'url': reverse('accounting:automation_process_detail', args=[self.object.pk])},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.object.pk])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Automation Process')


class AutomationProcessDeleteView(BaseDeleteView):
    """Delete an automation process."""
    model = AutomationProcess
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('accounting:automation_processes')
    feature_code = 'accounting.automation.processes'
    required_action = 'delete'
    active_module = 'accounting'
    success_message = _('Automation process deleted successfully.')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': self.object.name, 'url': reverse('accounting:automation_process_detail', args=[self.object.pk])},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.object.pk])


class AutomationExecutionLogListView(BaseListView):
    """
    List all automation execution logs for the active company.
    """
    model = AutomationExecutionLog
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.automation.logs'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['-executed_at']
    default_status_filter = False
    
    def get_base_queryset(self):
        """Get base queryset filtered by company."""
        queryset = super().get_base_queryset()
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['process__name', 'trigger_document_type', 'status']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Automation Execution Logs')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': None},
            {'label': _('Execution Logs'), 'url': None},
        ]
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:automation_execution_log_detail'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Execution Logs Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Execution logs will appear here when automation processes run.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📋'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('Process'), 'field': 'process__name'},
            {'label': _('Trigger Document'), 'field': 'trigger_document_type'},
            {'label': _('Status'), 'field': 'status', 'type': 'badge'},
            {'label': _('Executed At'), 'field': 'executed_at', 'type': 'datetime'},
            {'label': _('Completed At'), 'field': 'completed_at', 'type': 'datetime'},
        ]
        context['print_enabled'] = True
        return context


class AutomationExecutionLogDetailView(BaseDetailView):
    """View automation execution log details."""
    model = AutomationExecutionLog
    template_name = 'accounting/automation/execution_log_detail.html'
    feature_code = 'accounting.automation.logs'
    required_action = 'view_all'
    active_module = 'accounting'
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_execution_logs')},
            {'label': _('Execution Log'), 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['document_approvals'] = self.object.document_approvals.all().order_by('created_at')
        return context


# Condition Views
class AutomationConditionCreateView(BaseCreateView):
    """Create a new automation condition."""
    model = AutomationCondition
    form_class = AutomationConditionForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Condition created successfully.')
    
    def get_process(self):
        """Get the process from URL."""
        process_id = self.kwargs.get('process_id')
        return AutomationProcess.objects.get(pk=process_id)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add process_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['process_id'] = self.kwargs.get('process_id')
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.kwargs.get('process_id')])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.get_process()
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Add Condition'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.kwargs.get('process_id')])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Add Condition')


class AutomationConditionUpdateView(BaseUpdateView):
    """Update an automation condition."""
    model = AutomationCondition
    form_class = AutomationConditionForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Condition updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add process_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['process_id'] = self.object.process_id
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set updated_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.object.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Edit Condition'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Condition')


class AutomationConditionDeleteView(BaseDeleteView):
    """Delete an automation condition."""
    model = AutomationCondition
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Condition deleted successfully.')
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.object.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Delete Condition'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])


# Variable Views
class AutomationVariableCreateView(BaseCreateView):
    """Create a new automation variable."""
    model = AutomationVariable
    form_class = AutomationVariableForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Variable created successfully.')
    
    def get_process(self):
        """Get the process from URL."""
        process_id = self.kwargs.get('process_id')
        return AutomationProcess.objects.get(pk=process_id)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add process_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['process_id'] = self.kwargs.get('process_id')
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.kwargs.get('process_id')])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.get_process()
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Add Variable'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.kwargs.get('process_id')])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Add Variable')


class AutomationVariableUpdateView(BaseUpdateView):
    """Update an automation variable."""
    model = AutomationVariable
    form_class = AutomationVariableForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Variable updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add process_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['process_id'] = self.object.process_id
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set updated_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.object.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Edit Variable'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Variable')


class AutomationVariableDeleteView(BaseDeleteView):
    """Delete an automation variable."""
    model = AutomationVariable
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Variable deleted successfully.')
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.object.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Delete Variable'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])



# Document Step Views
class AutomationDocumentStepCreateView(BaseCreateView):
    """Create a new automation document step."""
    model = AutomationDocumentStep
    form_class = AutomationDocumentStepForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Document step created successfully.')
    
    def get_process(self):
        """Get the process from URL."""
        process_id = self.kwargs.get('process_id')
        return AutomationProcess.objects.get(pk=process_id)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add process_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['process_id'] = self.kwargs.get('process_id')
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.kwargs.get('process_id')])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.get_process()
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Add Document Step'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.kwargs.get('process_id')])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Add Document Step')


class AutomationDocumentStepDetailView(BaseDetailView):
    """View automation document step details."""
    model = AutomationDocumentStep
    template_name = 'accounting/automation/document_step_detail.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'view_all'
    active_module = 'accounting'
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.object.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Step') + f' {self.object.step_number}', 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.filter(is_active=True).order_by('line_number')
        return context


class AutomationDocumentStepUpdateView(BaseUpdateView):
    """Update an automation document step."""
    model = AutomationDocumentStep
    form_class = AutomationDocumentStepForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Document step updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add process_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['process_id'] = self.object.process_id
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set updated_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to step detail page."""
        return reverse('accounting:automation_document_step_detail', args=[self.object.process_id, self.object.pk])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.object.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Step') + f' {self.object.step_number}', 'url': reverse('accounting:automation_document_step_detail', args=[process.pk, self.object.pk])},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_document_step_detail', args=[self.object.process_id, self.object.pk])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Document Step')


class AutomationDocumentStepDeleteView(BaseDeleteView):
    """Delete an automation document step."""
    model = AutomationDocumentStep
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Document step deleted successfully.')
    
    def get_success_url(self):
        """Redirect to process detail page."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        process = self.object.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Delete Step'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_process_detail', args=[self.object.process_id])


# Document Line Views
class AutomationDocumentLineCreateView(BaseCreateView):
    """Create a new automation document line."""
    model = AutomationDocumentLine
    form_class = AutomationDocumentLineForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Document line created successfully.')
    
    def get_step(self):
        """Get the step from URL."""
        step_id = self.kwargs.get('step_id')
        return AutomationDocumentStep.objects.get(pk=step_id)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add step_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['step_id'] = self.kwargs.get('step_id')
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to step detail page."""
        step = self.get_step()
        return reverse('accounting:automation_document_step_detail', args=[step.process_id, step.pk])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        step = self.get_step()
        process = step.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Step') + f' {step.step_number}', 'url': reverse('accounting:automation_document_step_detail', args=[process.pk, step.pk])},
            {'label': _('Add Line'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        step = self.get_step()
        return reverse('accounting:automation_document_step_detail', args=[step.process_id, step.pk])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Add Document Line')


class AutomationDocumentLineUpdateView(BaseUpdateView):
    """Update an automation document line."""
    model = AutomationDocumentLine
    form_class = AutomationDocumentLineForm
    template_name = 'shared/generic/generic_form.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Document line updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add step_id and company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['step_id'] = self.object.step_id
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form) -> HttpResponseRedirect:
        """Set updated_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to step detail page."""
        return reverse('accounting:automation_document_step_detail', args=[self.object.step.process_id, self.object.step_id])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        step = self.object.step
        process = step.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Step') + f' {step.step_number}', 'url': reverse('accounting:automation_document_step_detail', args=[process.pk, step.pk])},
            {'label': _('Edit Line'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_document_step_detail', args=[self.object.step.process_id, self.object.step_id])
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Document Line')


class AutomationDocumentLineDeleteView(BaseDeleteView):
    """Delete an automation document line."""
    model = AutomationDocumentLine
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.automation.processes'
    required_action = 'update'
    active_module = 'accounting'
    success_message = _('Document line deleted successfully.')
    
    def get_success_url(self):
        """Redirect to step detail page."""
        return reverse('accounting:automation_document_step_detail', args=[self.object.step.process_id, self.object.step_id])
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        step = self.object.step
        process = step.process
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Automation'), 'url': reverse('accounting:automation_processes')},
            {'label': process.name, 'url': reverse('accounting:automation_process_detail', args=[process.pk])},
            {'label': _('Step') + f' {step.step_number}', 'url': reverse('accounting:automation_document_step_detail', args=[process.pk, step.pk])},
            {'label': _('Delete Line'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:automation_document_step_detail', args=[self.object.step.process_id, self.object.step_id])

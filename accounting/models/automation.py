"""
Automation models for accounting document automation system.
"""
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from shared.models import (
    CompanyScopedModel,
    TimeStampedModel,
    MetadataModel,
    SortableModel,
)

from .base import AccountingBaseModel
from .documents import AccountingDocument
from .accounts import Account
from .cost_centers import CostCenter


class AutomationProcess(CompanyScopedModel, TimeStampedModel, MetadataModel):
    """
    Automation process - defines a workflow for automatic document creation.
    """
    name = models.CharField(
        max_length=200,
        help_text=_("Process name"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Process description"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this process is active"),
    )
    trigger_module = models.CharField(
        max_length=100,
        help_text=_("Module name of the trigger document (e.g., 'sales', 'inventory')"),
    )
    trigger_document_type = models.CharField(
        max_length=100,
        help_text=_("Document type that triggers this process (e.g., 'Invoice', 'Receipt')"),
    )
    trigger_model = models.CharField(
        max_length=200,
        help_text=_("Django model path (e.g., 'sales.Invoice')"),
    )

    class Meta:
        verbose_name = _("Automation Process")
        verbose_name_plural = _("Automation Processes")
        ordering = ['-created_at']
        unique_together = [['company', 'name']]

    def __str__(self):
        return f"{self.name} ({self.company})"


class AutomationCondition(CompanyScopedModel, TimeStampedModel, SortableModel):
    """
    Condition/filter for automation process.
    """
    FILTER_TYPE_CHOICES = [
        ('global', _('Global Filter')),
        ('document_specific', _('Document-Specific Filter')),
    ]

    FILTER_CATEGORY_CHOICES = [
        ('user', _('User')),
        ('user_group', _('User Group')),
        ('date', _('Date')),
        ('date_range', _('Date Range')),
        ('status', _('Status')),
        ('document_field', _('Document Field')),
    ]

    OPERATOR_CHOICES = [
        ('==', _('Equals')),
        ('!=', _('Not Equals')),
        ('>', _('Greater Than')),
        ('<', _('Less Than')),
        ('>=', _('Greater Than or Equal')),
        ('<=', _('Less Than or Equal')),
        ('in', _('In')),
        ('not_in', _('Not In')),
        ('contains', _('Contains')),
        ('starts_with', _('Starts With')),
        ('ends_with', _('Ends With')),
        ('between', _('Between')),
        ('hierarchy_level', _('Hierarchy Level')),
        ('hierarchy_parent', _('Hierarchy Parent')),
        ('hierarchy_descendant', _('Hierarchy Descendant')),
        ('is_null', _('Is Null')),
        ('is_not_null', _('Is Not Null')),
    ]

    VALUE_TYPE_CHOICES = [
        ('static', _('Static')),
        ('variable', _('Variable')),
        ('calculated', _('Calculated')),
    ]

    LOGICAL_OPERATOR_CHOICES = [
        ('AND', _('AND')),
        ('OR', _('OR')),
    ]

    process = models.ForeignKey(
        AutomationProcess,
        on_delete=models.CASCADE,
        related_name='conditions',
        help_text=_("Related automation process"),
    )
    filter_type = models.CharField(
        max_length=20,
        choices=FILTER_TYPE_CHOICES,
        help_text=_("Filter type"),
    )
    filter_category = models.CharField(
        max_length=20,
        choices=FILTER_CATEGORY_CHOICES,
        help_text=_("Filter category"),
    )
    field_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Field name for document-specific filters"),
    )
    field_type = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Field type (string, number, date, foreign_key, many_to_many)"),
    )
    operator = models.CharField(
        max_length=30,
        choices=OPERATOR_CHOICES,
        help_text=_("Comparison operator"),
    )
    value = models.JSONField(
        help_text=_("Comparison value (can be single value or array)"),
    )
    value_type = models.CharField(
        max_length=20,
        choices=VALUE_TYPE_CHOICES,
        default='static',
        help_text=_("Value type"),
    )
    logical_operator = models.CharField(
        max_length=3,
        choices=LOGICAL_OPERATOR_CHOICES,
        default='AND',
        help_text=_("Logical operator for combining with next condition"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this condition is active"),
    )

    class Meta:
        verbose_name = _("Automation Condition")
        verbose_name_plural = _("Automation Conditions")
        ordering = ['process', 'sort_order']

    def __str__(self):
        return f"{self.process.name} - {self.filter_category} ({self.operator})"


class AutomationVariable(CompanyScopedModel, TimeStampedModel, SortableModel):
    """
    Variable extracted from trigger document for use in automation steps.
    """
    SOURCE_TYPE_CHOICES = [
        ('field', _('Field')),
        ('related_field', _('Related Field')),
        ('aggregated', _('Aggregated')),
        ('computed', _('Computed')),
    ]

    FIELD_TYPE_CHOICES = [
        ('header_field', _('Header Field')),
        ('line_field', _('Line Field')),
        ('related_field', _('Related Field')),
    ]

    AGGREGATION_TYPE_CHOICES = [
        ('sum', _('Sum')),
        ('count', _('Count')),
        ('avg', _('Average')),
        ('max', _('Maximum')),
        ('min', _('Minimum')),
    ]

    DATA_TYPE_CHOICES = [
        ('string', _('String')),
        ('number', _('Number')),
        ('date', _('Date')),
        ('boolean', _('Boolean')),
        ('foreign_key', _('Foreign Key')),
    ]

    process = models.ForeignKey(
        AutomationProcess,
        on_delete=models.CASCADE,
        related_name='variables',
        help_text=_("Related automation process"),
    )
    name = models.CharField(
        max_length=100,
        help_text=_("Variable name (for use in steps)"),
    )
    display_name = models.CharField(
        max_length=200,
        help_text=_("Display name (Persian)"),
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        help_text=_("Source type"),
    )
    field_path = models.CharField(
        max_length=500,
        help_text=_("Field path (e.g., 'customer' or 'customer.name' or 'lines.amount')"),
    )
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPE_CHOICES,
        help_text=_("Field type in document"),
    )
    aggregation_type = models.CharField(
        max_length=10,
        choices=AGGREGATION_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text=_("Aggregation type (for aggregated variables)"),
    )
    computation_expression = models.TextField(
        blank=True,
        null=True,
        help_text=_("Computation expression (for computed variables)"),
    )
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        help_text=_("Data type"),
    )
    related_model = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Related model (if related_field)"),
    )
    default_value = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Default value (optional)"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Variable description"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this variable is active"),
    )

    class Meta:
        verbose_name = _("Automation Variable")
        verbose_name_plural = _("Automation Variables")
        ordering = ['process', 'sort_order']
        unique_together = [['process', 'name']]

    def __str__(self):
        return f"{self.process.name} - {self.name}"


class AutomationDocumentStep(CompanyScopedModel, TimeStampedModel, SortableModel):
    """
    Document creation step in automation process.
    """
    DOCUMENT_TYPE_CHOICES = [
        ('accounting_document', _('Accounting Document')),
        ('warehouse_expense', _('Warehouse Expense')),
        ('treasury_receive', _('Treasury Receive')),
        ('treasury_pay', _('Treasury Pay')),
        ('treasury_transfer', _('Treasury Transfer')),
    ]

    APPROVAL_TYPE_CHOICES = [
        ('auto', _('Automatic')),
        ('manual', _('Manual')),
        ('none', _('None')),
    ]

    process = models.ForeignKey(
        AutomationProcess,
        on_delete=models.CASCADE,
        related_name='document_steps',
        help_text=_("Related automation process"),
    )
    step_number = models.PositiveIntegerField(
        help_text=_("Step number (execution order)"),
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text=_("Document type to create"),
    )
    document_template_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_("Document template ID (optional)"),
    )
    execution_condition = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Execution condition (must be met for this step to execute)"),
    )
    requires_approval = models.CharField(
        max_length=10,
        choices=APPROVAL_TYPE_CHOICES,
        default='auto',
        help_text=_("Approval requirement"),
    )
    wait_for_previous_approval = models.BooleanField(
        default=False,
        help_text=_("Wait for previous step approval before executing"),
    )
    header_config = models.JSONField(
        help_text=_("Header configuration (field values with static or variable sources)"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this step is active"),
    )

    class Meta:
        verbose_name = _("Automation Document Step")
        verbose_name_plural = _("Automation Document Steps")
        ordering = ['process', 'step_number']
        unique_together = [['process', 'step_number']]

    def __str__(self):
        return f"{self.process.name} - Step {self.step_number}"


class AutomationDocumentLine(CompanyScopedModel, TimeStampedModel, SortableModel):
    """
    Line item in automation document step.
    """
    VALUE_TYPE_CHOICES = [
        ('static', _('Static')),
        ('variable', _('Variable')),
        ('computed', _('Computed')),
    ]

    TAFSILI_TYPE_CHOICES = [
        ('static', _('Static')),
        ('variable', _('Variable')),
        ('none', _('None')),
    ]

    step = models.ForeignKey(
        AutomationDocumentStep,
        on_delete=models.CASCADE,
        related_name='lines',
        help_text=_("Related document step"),
    )
    line_number = models.PositiveIntegerField(
        help_text=_("Line number (order in document)"),
    )
    
    # Debit Account
    debit_account_type = models.CharField(
        max_length=10,
        choices=VALUE_TYPE_CHOICES,
        help_text=_("Debit account type"),
    )
    debit_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='automation_debit_account_lines',
        blank=True,
        null=True,
        help_text=_("Debit account (if static)"),
    )
    debit_account_variable = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Debit account variable name (if variable)"),
    )
    
    # Debit Tafsili
    debit_tafsili_type = models.CharField(
        max_length=10,
        choices=TAFSILI_TYPE_CHOICES,
        default='none',
        help_text=_("Debit tafsili type"),
    )
    debit_tafsili = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='automation_debit_tafsili_lines',
        blank=True,
        null=True,
        limit_choices_to={'account_level': 3},
        help_text=_("Debit tafsili (if static)"),
    )
    debit_tafsili_variable = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Debit tafsili variable name (if variable)"),
    )
    
    # Credit Account
    credit_account_type = models.CharField(
        max_length=10,
        choices=VALUE_TYPE_CHOICES,
        help_text=_("Credit account type"),
    )
    credit_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='automation_credit_account_lines',
        blank=True,
        null=True,
        help_text=_("Credit account (if static)"),
    )
    credit_account_variable = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Credit account variable name (if variable)"),
    )
    
    # Credit Tafsili
    credit_tafsili_type = models.CharField(
        max_length=10,
        choices=TAFSILI_TYPE_CHOICES,
        default='none',
        help_text=_("Credit tafsili type"),
    )
    credit_tafsili = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='automation_credit_tafsili_lines',
        blank=True,
        null=True,
        limit_choices_to={'account_level': 3},
        help_text=_("Credit tafsili (if static)"),
    )
    credit_tafsili_variable = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Credit tafsili variable name (if variable)"),
    )
    
    # Amount
    amount_type = models.CharField(
        max_length=10,
        choices=VALUE_TYPE_CHOICES,
        help_text=_("Amount type"),
    )
    amount_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Amount value (if static)"),
    )
    amount_variable = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Amount variable name (if variable)"),
    )
    amount_expression = models.TextField(
        blank=True,
        null=True,
        help_text=_("Amount expression (if computed)"),
    )
    
    # Cost Center
    cost_center_type = models.CharField(
        max_length=10,
        choices=TAFSILI_TYPE_CHOICES,
        default='none',
        help_text=_("Cost center type"),
    )
    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.PROTECT,
        related_name='automation_lines',
        blank=True,
        null=True,
        help_text=_("Cost center (if static)"),
    )
    cost_center_variable = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Cost center variable name (if variable)"),
    )
    
    # Description
    description_type = models.CharField(
        max_length=10,
        choices=[('static', _('Static')), ('computed', _('Computed'))],
        help_text=_("Description type"),
    )
    description_value = models.TextField(
        blank=True,
        null=True,
        help_text=_("Description value (if static)"),
    )
    description_expression = models.TextField(
        blank=True,
        null=True,
        help_text=_("Description expression (if computed - can include variables)"),
    )
    
    # Execution Condition
    execution_condition = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Execution condition for this line (optional)"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this line is active"),
    )

    class Meta:
        verbose_name = _("Automation Document Line")
        verbose_name_plural = _("Automation Document Lines")
        ordering = ['step', 'line_number']
        unique_together = [['step', 'line_number']]

    def __str__(self):
        return f"{self.step} - Line {self.line_number}"


class AutomationExecutionLog(CompanyScopedModel, TimeStampedModel):
    """
    Execution log for automation process runs.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('success', _('Success')),
        ('failed', _('Failed')),
        ('partial', _('Partial')),
        ('cancelled', _('Cancelled')),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    process = models.ForeignKey(
        AutomationProcess,
        on_delete=models.CASCADE,
        related_name='execution_logs',
        help_text=_("Related automation process"),
    )
    trigger_document_id = models.BigIntegerField(
        help_text=_("Trigger document ID"),
    )
    trigger_document_type = models.CharField(
        max_length=200,
        help_text=_("Trigger document type"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Execution status"),
    )
    executed_at = models.DateTimeField(
        help_text=_("Execution start time"),
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Execution completion time"),
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text=_("Error message (if any)"),
    )
    execution_data = models.JSONField(
        default=dict,
        help_text=_("Execution data including extracted variables"),
    )
    created_documents = models.JSONField(
        default=list,
        help_text=_("List of created documents"),
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        blank=True,
        null=True,
        help_text=_("Approval status"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='automation_approvals',
        blank=True,
        null=True,
        help_text=_("User who approved"),
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Approval time"),
    )

    class Meta:
        verbose_name = _("Automation Execution Log")
        verbose_name_plural = _("Automation Execution Logs")
        ordering = ['-executed_at']

    def __str__(self):
        return f"{self.process.name} - {self.status} ({self.executed_at})"


class AutomationDocumentApproval(CompanyScopedModel, TimeStampedModel):
    """
    Approval record for automation-created documents.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    execution_log = models.ForeignKey(
        AutomationExecutionLog,
        on_delete=models.CASCADE,
        related_name='document_approvals',
        help_text=_("Related execution log"),
    )
    step = models.ForeignKey(
        AutomationDocumentStep,
        on_delete=models.CASCADE,
        related_name='approvals',
        help_text=_("Related document step"),
    )
    document_id = models.BigIntegerField(
        help_text=_("Created document ID"),
    )
    document_type = models.CharField(
        max_length=50,
        help_text=_("Document type"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Approval status"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='automation_document_approvals',
        blank=True,
        null=True,
        help_text=_("User who approved/rejected"),
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Approval/rejection time"),
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text=_("Rejection reason (if rejected)"),
    )

    class Meta:
        verbose_name = _("Automation Document Approval")
        verbose_name_plural = _("Automation Document Approvals")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.step} - {self.status}"


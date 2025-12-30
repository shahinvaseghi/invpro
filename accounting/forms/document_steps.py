"""
Forms for automation document steps and lines.
"""
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
import json

from accounting.models.automation import AutomationDocumentStep, AutomationDocumentLine
from accounting.models import Account, CostCenter


class AutomationDocumentStepForm(forms.ModelForm):
    """Form for creating/editing automation document steps."""
    
    class Meta:
        model = AutomationDocumentStep
        fields = [
            'step_number',
            'document_type',
            'document_template_id',
            'execution_condition',
            'requires_approval',
            'wait_for_previous_approval',
            'header_config',
            'is_active',
        ]
        widgets = {
            'step_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'document_template_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Optional template ID'),
            }),
            'execution_condition': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('JSON condition (optional)'),
            }),
            'requires_approval': forms.Select(attrs={'class': 'form-control'}),
            'wait_for_previous_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'header_config': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': _('JSON header configuration'),
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, process_id=None, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.process_id = process_id
        self.company_id = company_id
        
        if process_id:
            from accounting.models.automation import AutomationProcess
            try:
                self.instance.process = AutomationProcess.objects.get(pk=process_id)
            except AutomationProcess.DoesNotExist:
                pass
        
        # Auto-set step_number if creating new
        if not self.instance.pk and process_id:
            from accounting.models.automation import AutomationProcess
            try:
                process = AutomationProcess.objects.get(pk=process_id)
                max_step = process.document_steps.aggregate(
                    max_step=models.Max('step_number')
                )['max_step'] or 0
                self.initial['step_number'] = max_step + 1
            except AutomationProcess.DoesNotExist:
                pass
        
        # Format JSON fields for display
        if self.instance.pk:
            if self.instance.header_config:
                self.initial['header_config'] = json.dumps(self.instance.header_config, indent=2, ensure_ascii=False)
            if self.instance.execution_condition:
                self.initial['execution_condition'] = json.dumps(self.instance.execution_condition, indent=2, ensure_ascii=False)
    
    def clean_header_config(self):
        """Validate header_config is valid JSON."""
        header_config = self.cleaned_data.get('header_config')
        if header_config:
            if isinstance(header_config, str):
                try:
                    header_config = json.loads(header_config)
                except json.JSONDecodeError:
                    raise forms.ValidationError(_('Invalid JSON format'))
            elif not isinstance(header_config, dict):
                raise forms.ValidationError(_('Header config must be a JSON object'))
        return header_config or {}
    
    def clean_execution_condition(self):
        """Validate execution_condition is valid JSON."""
        execution_condition = self.cleaned_data.get('execution_condition')
        if execution_condition:
            if isinstance(execution_condition, str):
                try:
                    execution_condition = json.loads(execution_condition)
                except json.JSONDecodeError:
                    raise forms.ValidationError(_('Invalid JSON format'))
        return execution_condition
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.process_id and not instance.process_id:
            from accounting.models.automation import AutomationProcess
            instance.process = AutomationProcess.objects.get(pk=self.process_id)
        if self.company_id:
            from shared.models import Company
            instance.company = Company.objects.get(pk=self.company_id)
        if commit:
            instance.save()
        return instance


class AutomationDocumentLineForm(forms.ModelForm):
    """Form for creating/editing automation document lines."""
    
    class Meta:
        model = AutomationDocumentLine
        fields = [
            'line_number',
            'debit_account_type',
            'debit_account',
            'debit_account_variable',
            'debit_tafsili_type',
            'debit_tafsili',
            'debit_tafsili_variable',
            'credit_account_type',
            'credit_account',
            'credit_account_variable',
            'credit_tafsili_type',
            'credit_tafsili',
            'credit_tafsili_variable',
            'amount_type',
            'amount_value',
            'amount_variable',
            'amount_expression',
            'cost_center_type',
            'cost_center',
            'cost_center_variable',
            'description_type',
            'description_value',
            'description_expression',
            'execution_condition',
            'is_active',
        ]
        widgets = {
            'line_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'debit_account_type': forms.Select(attrs={'class': 'form-control'}),
            'debit_account': forms.Select(attrs={'class': 'form-control'}),
            'debit_account_variable': forms.TextInput(attrs={'class': 'form-control'}),
            'debit_tafsili_type': forms.Select(attrs={'class': 'form-control'}),
            'debit_tafsili': forms.Select(attrs={'class': 'form-control'}),
            'debit_tafsili_variable': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_account_type': forms.Select(attrs={'class': 'form-control'}),
            'credit_account': forms.Select(attrs={'class': 'form-control'}),
            'credit_account_variable': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_tafsili_type': forms.Select(attrs={'class': 'form-control'}),
            'credit_tafsili': forms.Select(attrs={'class': 'form-control'}),
            'credit_tafsili_variable': forms.TextInput(attrs={'class': 'form-control'}),
            'amount_type': forms.Select(attrs={'class': 'form-control'}),
            'amount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount_variable': forms.TextInput(attrs={'class': 'form-control'}),
            'amount_expression': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cost_center_type': forms.Select(attrs={'class': 'form-control'}),
            'cost_center': forms.Select(attrs={'class': 'form-control'}),
            'cost_center_variable': forms.TextInput(attrs={'class': 'form-control'}),
            'description_type': forms.Select(attrs={'class': 'form-control'}),
            'description_value': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description_expression': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'execution_condition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, step_id=None, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_id = step_id
        self.company_id = company_id
        
        if step_id:
            from accounting.models.automation import AutomationDocumentStep
            try:
                self.instance.step = AutomationDocumentStep.objects.get(pk=step_id)
            except AutomationDocumentStep.DoesNotExist:
                pass
        
        # Filter accounts and tafsili by company
        if company_id:
            if 'debit_account' in self.fields:
                self.fields['debit_account'].queryset = Account.objects.filter(company_id=company_id)
            if 'credit_account' in self.fields:
                self.fields['credit_account'].queryset = Account.objects.filter(company_id=company_id)
            if 'debit_tafsili' in self.fields:
                self.fields['debit_tafsili'].queryset = Account.objects.filter(
                    company_id=company_id,
                    account_level=3
                )
            if 'credit_tafsili' in self.fields:
                self.fields['credit_tafsili'].queryset = Account.objects.filter(
                    company_id=company_id,
                    account_level=3
                )
            if 'cost_center' in self.fields:
                self.fields['cost_center'].queryset = CostCenter.objects.filter(company_id=company_id)
        
        # Auto-set line_number if creating new
        if not self.instance.pk and step_id:
            from accounting.models.automation import AutomationDocumentStep
            try:
                step = AutomationDocumentStep.objects.get(pk=step_id)
                max_line = step.lines.aggregate(
                    max_line=models.Max('line_number')
                )['max_line'] or 0
                self.initial['line_number'] = max_line + 1
            except AutomationDocumentStep.DoesNotExist:
                pass
        
        # Format JSON fields for display
        if self.instance.pk:
            if self.instance.execution_condition:
                self.initial['execution_condition'] = json.dumps(self.instance.execution_condition, indent=2, ensure_ascii=False)
    
    def clean_execution_condition(self):
        """Validate execution_condition is valid JSON."""
        execution_condition = self.cleaned_data.get('execution_condition')
        if execution_condition:
            if isinstance(execution_condition, str):
                try:
                    execution_condition = json.loads(execution_condition)
                except json.JSONDecodeError:
                    raise forms.ValidationError(_('Invalid JSON format'))
        return execution_condition
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.step_id and not instance.step_id:
            from accounting.models.automation import AutomationDocumentStep
            instance.step = AutomationDocumentStep.objects.get(pk=self.step_id)
        if self.company_id:
            from shared.models import Company
            instance.company = Company.objects.get(pk=self.company_id)
        if commit:
            instance.save()
        return instance


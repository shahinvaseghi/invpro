"""
Forms for automation module.
"""
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounting.models.automation import (
    AutomationProcess,
    AutomationCondition,
    AutomationVariable,
    AutomationDocumentStep,
    AutomationDocumentLine,
)
from accounting.models import Account, CostCenter
from accounting.utils.automation_registry import get_automatable_documents, get_document_by_id


class AutomationProcessForm(forms.ModelForm):
    """Form for creating/editing automation processes."""
    
    # Custom field for document selection
    trigger_document = forms.ChoiceField(
        label=_('سند ماشه‌کننده'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_trigger_document',
        }),
        help_text=_('نوع سندی که این فرایند خودکار را فعال می‌کند را انتخاب کنید'),
    )
    
    class Meta:
        model = AutomationProcess
        fields = [
            'name',
            'description',
            'is_active',
            'trigger_module',
            'trigger_document_type',
            'trigger_model',
        ]
        # Field order - trigger_document will be inserted manually in template
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('نام فرایند'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('توضیحات فرایند'),
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'trigger_module': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'id': 'id_trigger_module',
            }),
            'trigger_document_type': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'id': 'id_trigger_document_type',
            }),
            'trigger_model': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'id': 'id_trigger_model',
            }),
        }
        labels = {
            'name': _('نام فرایند'),
            'description': _('توضیحات'),
            'is_active': _('فعال'),
            'trigger_module': _('ماژول ماشه‌کننده'),
            'trigger_document_type': _('نوع سند ماشه‌کننده'),
            'trigger_model': _('مدل ماشه‌کننده'),
        }
        help_texts = {
            'name': _('نام یکتا برای این فرایند خودکار'),
            'description': _('توضیحی درباره کاری که این فرایند انجام می‌دهد'),
            'is_active': _('آیا این فرایند فعال است و اجرا خواهد شد'),
            'trigger_module': _('نام ماژولی که سند ماشه‌کننده در آن قرار دارد (خودکار پر می‌شود)'),
            'trigger_document_type': _('نوع سندی که این فرایند را فعال می‌کند (خودکار پر می‌شود)'),
            'trigger_model': _('مسیر کامل مدل Django (خودکار پر می‌شود)'),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id
        
        # Get all automatable documents grouped by category
        documents_by_category = get_automatable_documents()
        
        # Build choices for trigger_document dropdown with optgroups
        choices = [('', _('-- انتخاب نوع سند --'))]
        for category, docs in sorted(documents_by_category.items()):
            # Add category separator
            choices.append((f'__category__{category}', f'--- {category} ---'))
            for doc in docs:
                choices.append((doc['id'], doc['label']))
        
        self.fields['trigger_document'].choices = choices
        
        # If editing existing process, set the selected document
        if self.instance.pk:
            # Find the document ID that matches current values
            for doc_id, doc_label in choices:
                if doc_id and not doc_id.startswith('__category__'):
                    doc = get_document_by_id(doc_id)
                    if doc and doc['module'] == self.instance.trigger_module and \
                       doc['document_type'] == self.instance.trigger_document_type and \
                       doc['model'] == self.instance.trigger_model:
                        self.initial['trigger_document'] = doc_id
                        break
    
    def clean_trigger_document(self):
        """Validate trigger document selection."""
        document_id = self.cleaned_data.get('trigger_document')
        if not document_id or document_id.startswith('__category__'):
            raise forms.ValidationError(_('لطفاً نوع سند را انتخاب کنید'))
        return document_id
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set trigger fields from selected document
        document_id = self.cleaned_data.get('trigger_document')
        if document_id:
            doc = get_document_by_id(document_id)
            if doc:
                instance.trigger_module = doc['module']
                instance.trigger_document_type = doc['document_type']
                instance.trigger_model = doc['model']
        
        if self.company_id:
            from shared.models import Company
            instance.company = Company.objects.get(pk=self.company_id)
        if commit:
            instance.save()
        return instance


class AutomationConditionForm(forms.ModelForm):
    """Form for creating/editing automation conditions."""
    
    class Meta:
        model = AutomationCondition
        fields = [
            'filter_type',
            'filter_category',
            'field_name',
            'field_type',
            'operator',
            'value',
            'value_type',
            'logical_operator',
            'is_active',
            'sort_order',
        ]
        widgets = {
            'filter_type': forms.Select(attrs={'class': 'form-control'}),
            'filter_category': forms.Select(attrs={'class': 'form-control'}),
            'field_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Field name (for document-specific filters)'),
            }),
            'field_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., string, number, date'),
            }),
            'operator': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('JSON value or array'),
            }),
            'value_type': forms.Select(attrs={'class': 'form-control'}),
            'logical_operator': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
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


class AutomationVariableForm(forms.ModelForm):
    """Form for creating/editing automation variables."""
    
    class Meta:
        model = AutomationVariable
        fields = [
            'name',
            'display_name',
            'source_type',
            'field_path',
            'field_type',
            'aggregation_type',
            'computation_expression',
            'data_type',
            'related_model',
            'default_value',
            'description',
            'is_active',
            'sort_order',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Variable name (e.g., customer_tafsili)'),
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Display name (Persian)'),
            }),
            'source_type': forms.Select(attrs={'class': 'form-control'}),
            'field_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., customer or customer.name or lines.amount'),
            }),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'aggregation_type': forms.Select(attrs={'class': 'form-control'}),
            'computation_expression': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Computation expression (for computed variables)'),
            }),
            'data_type': forms.Select(attrs={'class': 'form-control'}),
            'related_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., accounting.TafsiliAccount'),
            }),
            'default_value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Default value (JSON)'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
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


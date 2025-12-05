"""
Base form classes for all modules.

These base classes provide common functionality like automatic widget styling
and formset management.
"""
from typing import Optional, Any
from django import forms
from django.forms.formsets import BaseFormSet


class BaseModelForm(forms.ModelForm):
    """
    Base ModelForm with automatic widget styling.
    
    This form automatically applies default CSS classes to all form fields:
    - Checkbox inputs → 'form-check-input' class
    - Other inputs → 'form-control' class
    
    Usage:
        class MyForm(BaseModelForm):
            class Meta:
                model = MyModel
                fields = ['name', 'is_enabled']
                # No need to define widgets - styling is automatic
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize form and apply default widget styling."""
        super().__init__(*args, **kwargs)
        self._apply_default_widget_styling()
    
    def _apply_default_widget_styling(self):
        """Apply default CSS classes to all form fields."""
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Skip if widget already has class attribute set
            if hasattr(widget, 'attrs') and 'class' in widget.attrs:
                continue
            
            # Apply default class based on widget type
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs.setdefault('class', 'form-check-input')
            else:
                # All other inputs (TextInput, Select, Textarea, etc.)
                widget.attrs.setdefault('class', 'form-control')


class BaseFormset(BaseFormSet):
    """
    Base formset helper class.
    
    This class provides common functionality for formsets like setting
    request on all forms and saving with company context.
    
    Usage:
        class MyFormset(BaseFormset):
            form = MyForm
            
            def __init__(self, *args, **kwargs):
                self.request = kwargs.pop('request', None)
                super().__init__(*args, **kwargs)
                if self.request:
                    self._set_request_on_forms()
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize formset and set request on all forms if provided."""
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request:
            self._set_request_on_forms()
    
    def _set_request_on_forms(self):
        """Set request object on all forms in the formset."""
        for form in self.forms:
            if hasattr(form, 'request'):
                form.request = self.request
    
    def save_with_company(self, company_id: Optional[int], commit: bool = True):
        """
        Save all forms in the formset with company_id.
        
        Args:
            company_id: Company ID to set on all form instances
            commit: Whether to save to database
            
        Returns:
            List of saved instances
        """
        instances = []
        for form in self.forms:
            if form.is_valid() and not form.cleaned_data.get('DELETE', False):
                instance = form.save(commit=False)
                if company_id and hasattr(instance, 'company_id'):
                    instance.company_id = company_id
                if commit:
                    instance.save()
                instances.append(instance)
        return instances


"""
Process Operations forms for production module.
"""
from typing import Optional
from django import forms
from django.utils.translation import gettext_lazy as _

from production.models import ProcessOperation, ProcessOperationMaterial, BOMMaterial, WorkLine


class ProcessOperationMaterialForm(forms.ModelForm):
    """Form for Process Operation Material (materials used in an operation)."""
    
    class Meta:
        model = ProcessOperationMaterial
        fields = [
            'bom_material',
            'quantity_used',
        ]
        widgets = {
            'bom_material': forms.Select(attrs={'class': 'form-control operation-material-bom-material'}),
            'quantity_used': forms.NumberInput(attrs={
                'class': 'form-control operation-material-quantity',
                'step': '0.000001',
                'min': '0',
            }),
        }
        labels = {
            'bom_material': _('Material from BOM'),
            'quantity_used': _('Quantity Used'),
        }
    
    def __init__(self, *args: tuple, bom_id: Optional[int] = None, process_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with BOM filtering from Process or direct BOM ID."""
        super().__init__(*args, **kwargs)
        
        # Get BOM ID from process if available, otherwise use provided bom_id
        final_bom_id = bom_id
        
        # Try to get BOM from instance's operation's process
        if not final_bom_id and hasattr(self, 'instance') and self.instance and self.instance.operation_id:
            try:
                operation = self.instance.operation
                if operation.process_id and operation.process.bom_id:
                    final_bom_id = operation.process.bom_id
            except Exception:
                pass
        
        # Try to get BOM from process_id if provided
        if not final_bom_id and process_id:
            try:
                from production.models import Process
                process = Process.objects.get(pk=process_id)
                if process.bom_id:
                    final_bom_id = process.bom_id
            except Exception:
                pass
        
        if final_bom_id:
            # Filter BOM materials by BOM
            self.fields['bom_material'].queryset = BOMMaterial.objects.filter(
                bom_id=final_bom_id,
                is_enabled=1,
            ).select_related('material_item').order_by('line_number')
        else:
            self.fields['bom_material'].queryset = BOMMaterial.objects.none()
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        
        # If material is selected, ensure quantity is provided
        bom_material = cleaned_data.get('bom_material')
        quantity_used = cleaned_data.get('quantity_used')
        
        if bom_material and not quantity_used:
            raise forms.ValidationError({
                'quantity_used': _('Quantity is required when material is selected.')
            })
        
        return cleaned_data


class ProcessOperationMaterialFormSetBase(forms.BaseInlineFormSet):
    """Custom formset with validation for operation materials."""
    
    def __init__(self, *args, process_id: Optional[int] = None, **kwargs):
        """Initialize formset with process_id to pass to forms."""
        super().__init__(*args, **kwargs)
        self.process_id = process_id
        
        # Pass process_id to all forms in the formset
        if process_id:
            form_kwargs = kwargs.get('form_kwargs', {})
            form_kwargs['process_id'] = process_id
            kwargs['form_kwargs'] = form_kwargs
    
    def clean(self) -> None:
        """Validate that materials are not duplicated."""
        if any(self.errors):
            return
        
        bom_materials = []
        for form in self.forms:
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                if not form.cleaned_data.get('DELETE', False):
                    bom_material = form.cleaned_data.get('bom_material')
                    if bom_material:
                        if bom_material in bom_materials:
                            raise forms.ValidationError(
                                _('Each material can only be selected once per operation.')
                            )
                        bom_materials.append(bom_material)


# Formset factory for operation materials
ProcessOperationMaterialFormSet = forms.inlineformset_factory(
    ProcessOperation,
    ProcessOperationMaterial,
    form=ProcessOperationMaterialForm,
    formset=ProcessOperationMaterialFormSetBase,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class ProcessOperationForm(forms.ModelForm):
    """Form for Process Operation."""
    
    class Meta:
        model = ProcessOperation
        fields = [
            'name',
            'description',
            'sequence_order',
            'labor_minutes_per_unit',
            'machine_minutes_per_unit',
            'work_line',
            'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control operation-name'}),
            'description': forms.TextInput(attrs={'class': 'form-control operation-description'}),
            'sequence_order': forms.NumberInput(attrs={
                'class': 'form-control operation-sequence',
                'min': '1',
            }),
            'labor_minutes_per_unit': forms.NumberInput(attrs={
                'class': 'form-control operation-labor-minutes',
                'step': '0.000001',
                'min': '0',
            }),
            'machine_minutes_per_unit': forms.NumberInput(attrs={
                'class': 'form-control operation-machine-minutes',
                'step': '0.000001',
                'min': '0',
            }),
            'work_line': forms.Select(attrs={'class': 'form-control operation-work-line'}),
            'notes': forms.Textarea(attrs={'class': 'form-control operation-notes', 'rows': 2}),
        }
        labels = {
            'name': _('Operation Name'),
            'description': _('Description'),
            'sequence_order': _('Sequence Order'),
            'labor_minutes_per_unit': _('Labor Minutes per Unit'),
            'machine_minutes_per_unit': _('Machine Minutes per Unit'),
            'work_line': _('Work Line (خط کاری)'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args: tuple, bom_id: Optional[int] = None, company_id: Optional[int] = None, **kwargs: dict):
        """Initialize form with BOM ID and company ID for nested formset and work line filtering."""
        super().__init__(*args, **kwargs)
        self.bom_id = bom_id
        
        # Filter work lines by company
        if company_id:
            self.fields['work_line'].queryset = WorkLine.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
        else:
            self.fields['work_line'].queryset = WorkLine.objects.none()


class ProcessOperationFormSetBase(forms.BaseFormSet):
    """Custom formset with validation for process operations."""
    
    def clean(self) -> None:
        """Validate that at least one operation exists."""
        if any(self.errors):
            return
        
        # Count non-empty forms
        non_empty_forms = 0
        for form in self.forms:
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                if not form.cleaned_data.get('DELETE', False):
                    # Check if at least name or sequence_order is provided
                    name = form.cleaned_data.get('name')
                    sequence_order = form.cleaned_data.get('sequence_order')
                    if name or sequence_order:
                        non_empty_forms += 1
        
        # Note: We allow empty operations (they will be filtered out)
        # But each operation must have at least name or sequence_order


# Formset factory for operations
ProcessOperationFormSet = forms.formset_factory(
    ProcessOperationForm,
    formset=ProcessOperationFormSetBase,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


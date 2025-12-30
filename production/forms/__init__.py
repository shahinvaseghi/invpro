"""
Forms package for production module.

This package contains refactored forms organized by functionality:
- person: Personnel forms
- machine: Machine forms
- bom: BOM (Bill of Materials) forms
- work_line: WorkLine forms
- process: Process forms
"""
__all__ = []

# Import person forms
from production.forms.person import PersonForm

# Import machine forms
from production.forms.machine import MachineForm

# Import BOM forms
from production.forms.bom import (
    BOMForm,
    BOMMaterialLineForm,
    BOMMaterialLineFormSet,
    BOMMaterialAlternativeForm,
    BOMMaterialAlternativeFormSet,
)

# Import work line forms
from production.forms.work_line import WorkLineForm

# Import process forms
from production.forms.process import ProcessForm

# Import process operations forms
from production.forms.process_operations import (
    ProcessOperationForm,
    ProcessOperationMaterialForm,
    ProcessOperationFormSet,
    ProcessOperationMaterialFormSet,
)

# Import product order forms
from production.forms.product_order import ProductOrderForm

# Import transfer to line forms
from production.forms.transfer_to_line import (
    TransferToLineForm,
    TransferToLineItemForm,
    TransferToLineItemFormSet,
)

# Import performance record forms
from production.forms.performance_record import (
    PerformanceRecordForm,
    PerformanceRecordMaterialForm,
    PerformanceRecordPersonForm,
    PerformanceRecordMachineForm,
    PerformanceRecordMaterialFormSet,
    PerformanceRecordPersonFormSet,
    PerformanceRecordMachineFormSet,
)

__all__ = [
    # Person forms
    'PersonForm',
    # Machine forms
    'MachineForm',
    # BOM forms
    'BOMForm',
    'BOMMaterialLineForm',
    'BOMMaterialLineFormSet',
    'BOMMaterialAlternativeForm',
    'BOMMaterialAlternativeFormSet',
    # WorkLine forms
    'WorkLineForm',
    # Process forms
    'ProcessForm',
    # Process Operations forms
    'ProcessOperationForm',
    'ProcessOperationMaterialForm',
    'ProcessOperationFormSet',
    'ProcessOperationMaterialFormSet',
    # Product Order forms
    'ProductOrderForm',
    # Transfer to Line forms
    'TransferToLineForm',
    'TransferToLineItemForm',
    'TransferToLineItemFormSet',
    # Performance Record forms
    'PerformanceRecordForm',
    'PerformanceRecordMaterialForm',
    'PerformanceRecordPersonForm',
    'PerformanceRecordMachineForm',
    'PerformanceRecordMaterialFormSet',
    'PerformanceRecordPersonFormSet',
    'PerformanceRecordMachineFormSet',
]


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
)

# Import work line forms
from production.forms.work_line import WorkLineForm

# Import process forms
from production.forms.process import ProcessForm

__all__ = [
    # Person forms
    'PersonForm',
    # Machine forms
    'MachineForm',
    # BOM forms
    'BOMForm',
    'BOMMaterialLineForm',
    'BOMMaterialLineFormSet',
    # WorkLine forms
    'WorkLineForm',
    # Process forms
    'ProcessForm',
]


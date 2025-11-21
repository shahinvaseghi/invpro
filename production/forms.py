"""
Forms for production module.

This file is kept for backward compatibility.
All forms have been refactored into production.forms package.
"""
# Import all forms from the refactored package
from production.forms import (
    PersonForm,
    MachineForm,
    BOMForm,
    BOMMaterialLineForm,
    BOMMaterialLineFormSet,
    WorkLineForm,
    ProcessForm,
)

__all__ = [
    'PersonForm',
    'MachineForm',
    'BOMForm',
    'BOMMaterialLineForm',
    'BOMMaterialLineFormSet',
    'WorkLineForm',
    'ProcessForm',
]

"""
Views for production module.

This file is kept for backward compatibility.
All views have been refactored into production.views package.
"""
# Import all views from the refactored package
from production.views import (
    PersonnelListView,
    PersonCreateView,
    PersonUpdateView,
    PersonDeleteView,
    MachineListView,
    MachineCreateView,
    MachineUpdateView,
    MachineDeleteView,
    BOMListView,
    BOMCreateView,
    BOMUpdateView,
    BOMDeleteView,
    WorkLineListView,
    WorkLineCreateView,
    WorkLineUpdateView,
    WorkLineDeleteView,
    ProcessListView,
    ProcessCreateView,
    ProcessUpdateView,
    ProcessDeleteView,
    TransferToLineRequestListView,
    PerformanceRecordListView,
)

__all__ = [
    'PersonnelListView',
    'PersonCreateView',
    'PersonUpdateView',
    'PersonDeleteView',
    'MachineListView',
    'MachineCreateView',
    'MachineUpdateView',
    'MachineDeleteView',
    'BOMListView',
    'BOMCreateView',
    'BOMUpdateView',
    'BOMDeleteView',
    'WorkLineListView',
    'WorkLineCreateView',
    'WorkLineUpdateView',
    'WorkLineDeleteView',
    'ProcessListView',
    'ProcessCreateView',
    'ProcessUpdateView',
    'ProcessDeleteView',
    'TransferToLineRequestListView',
    'PerformanceRecordListView',
]

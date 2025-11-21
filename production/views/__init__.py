"""
Views package for production module.

This package contains refactored views organized by functionality:
- personnel: Personnel (Person) CRUD views
- machine: Machine CRUD views
- bom: BOM (Bill of Materials) CRUD views
- work_line: WorkLine CRUD views
- process: Process CRUD views
- placeholders: Placeholder views (TransferToLineRequest, PerformanceRecord)
"""
__all__ = []

# Import personnel views
from production.views.personnel import (
    PersonnelListView,
    PersonCreateView,
    PersonUpdateView,
    PersonDeleteView,
)

# Import machine views
from production.views.machine import (
    MachineListView,
    MachineCreateView,
    MachineUpdateView,
    MachineDeleteView,
)

# Import BOM views
from production.views.bom import (
    BOMListView,
    BOMCreateView,
    BOMUpdateView,
    BOMDeleteView,
)

# Import work line views
from production.views.work_line import (
    WorkLineListView,
    WorkLineCreateView,
    WorkLineUpdateView,
    WorkLineDeleteView,
)

# Import process views
from production.views.process import (
    ProcessListView,
    ProcessCreateView,
    ProcessUpdateView,
    ProcessDeleteView,
)

# Import placeholder views
from production.views.placeholders import (
    TransferToLineRequestListView,
    PerformanceRecordListView,
)

__all__ = [
    # Personnel views
    'PersonnelListView',
    'PersonCreateView',
    'PersonUpdateView',
    'PersonDeleteView',
    # Machine views
    'MachineListView',
    'MachineCreateView',
    'MachineUpdateView',
    'MachineDeleteView',
    # BOM views
    'BOMListView',
    'BOMCreateView',
    'BOMUpdateView',
    'BOMDeleteView',
    # WorkLine views
    'WorkLineListView',
    'WorkLineCreateView',
    'WorkLineUpdateView',
    'WorkLineDeleteView',
    # Process views
    'ProcessListView',
    'ProcessCreateView',
    'ProcessUpdateView',
    'ProcessDeleteView',
    # Placeholder views
    'TransferToLineRequestListView',
    'PerformanceRecordListView',
]


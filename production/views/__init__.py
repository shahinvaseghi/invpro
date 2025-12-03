"""
Views package for production module.

This package contains refactored views organized by functionality:
- personnel: Personnel (Person) CRUD views
- machine: Machine CRUD views
- bom: BOM (Bill of Materials) CRUD views
- work_line: WorkLine CRUD views
- process: Process CRUD views
- placeholders: Placeholder views (TransferToLineRequest, PerformanceRecord, TrackingIdentification)
"""
__all__ = []

# Import placeholder views
from production.views.placeholders import (
    TrackingIdentificationView,
)

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

# Import product order views
from production.views.product_order import (
    ProductOrderListView,
    ProductOrderCreateView,
    ProductOrderUpdateView,
    ProductOrderDeleteView,
)

# Import transfer to line views
from production.views.transfer_to_line import (
    TransferToLineListView,
    TransferToLineCreateView,
    TransferToLineUpdateView,
    TransferToLineDeleteView,
    TransferToLineApproveView,
    TransferToLineRejectView,
    TransferToLineQCApproveView,
    TransferToLineQCRejectView,
)

# Import performance record views
from production.views.performance_record import (
    PerformanceRecordListView,
    PerformanceRecordCreateView,
    PerformanceRecordUpdateView,
    PerformanceRecordDeleteView,
    PerformanceRecordApproveView,
    PerformanceRecordRejectView,
    PerformanceRecordCreateReceiptView,
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
    # Product Order views
    'ProductOrderListView',
    'ProductOrderCreateView',
    'ProductOrderUpdateView',
    'ProductOrderDeleteView',
    # Transfer to Line views
    'TransferToLineListView',
    'TransferToLineCreateView',
    'TransferToLineUpdateView',
    'TransferToLineDeleteView',
    'TransferToLineApproveView',
    'TransferToLineRejectView',
    'TransferToLineQCApproveView',
    'TransferToLineQCRejectView',
    # Performance Record views
    'PerformanceRecordListView',
    'PerformanceRecordCreateView',
    'PerformanceRecordUpdateView',
    'PerformanceRecordDeleteView',
    'PerformanceRecordApproveView',
    'PerformanceRecordRejectView',
    'PerformanceRecordCreateReceiptView',
    # Placeholder views
    'TrackingIdentificationView',
]


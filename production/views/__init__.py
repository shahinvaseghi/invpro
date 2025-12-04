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
    PersonDetailView,
    PersonUpdateView,
    PersonDeleteView,
)

# Import machine views
from production.views.machine import (
    MachineListView,
    MachineCreateView,
    MachineDetailView,
    MachineUpdateView,
    MachineDeleteView,
)

# Import BOM views
from production.views.bom import (
    BOMListView,
    BOMCreateView,
    BOMDetailView,
    BOMUpdateView,
    BOMDeleteView,
)

# Import work line views
from production.views.work_line import (
    WorkLineListView,
    WorkLineCreateView,
    WorkLineDetailView,
    WorkLineUpdateView,
    WorkLineDeleteView,
)

# Import process views
from production.views.process import (
    ProcessListView,
    ProcessCreateView,
    ProcessDetailView,
    ProcessUpdateView,
    ProcessDeleteView,
)

# Import product order views
from production.views.product_order import (
    ProductOrderListView,
    ProductOrderCreateView,
    ProductOrderDetailView,
    ProductOrderUpdateView,
    ProductOrderDeleteView,
)

# Import transfer to line views
from production.views.transfer_to_line import (
    TransferToLineListView,
    TransferToLineCreateView,
    TransferToLineDetailView,
    TransferToLineUpdateView,
    TransferToLineDeleteView,
    TransferToLineApproveView,
    TransferToLineRejectView,
    TransferToLineQCApproveView,
    TransferToLineQCRejectView,
    TransferToLineCreateWarehouseTransferView,
    TransferToLineUnlockView,
)

# Import performance record views
from production.views.performance_record import (
    PerformanceRecordListView,
    PerformanceRecordCreateView,
    PerformanceRecordDetailView,
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
    'PersonDetailView',
    'PersonUpdateView',
    'PersonDeleteView',
    # Machine views
    'MachineListView',
    'MachineCreateView',
    'MachineDetailView',
    'MachineUpdateView',
    'MachineDeleteView',
    # BOM views
    'BOMListView',
    'BOMCreateView',
    'BOMDetailView',
    'BOMUpdateView',
    'BOMDeleteView',
    # WorkLine views
    'WorkLineListView',
    'WorkLineCreateView',
    'WorkLineDetailView',
    'WorkLineUpdateView',
    'WorkLineDeleteView',
    # Process views
    'ProcessListView',
    'ProcessCreateView',
    'ProcessDetailView',
    'ProcessUpdateView',
    'ProcessDeleteView',
    # Product Order views
    'ProductOrderListView',
    'ProductOrderCreateView',
    'ProductOrderDetailView',
    'ProductOrderUpdateView',
    'ProductOrderDeleteView',
    # Transfer to Line views
    'TransferToLineListView',
    'TransferToLineCreateView',
    'TransferToLineDetailView',
    'TransferToLineUpdateView',
    'TransferToLineDeleteView',
    'TransferToLineApproveView',
    'TransferToLineRejectView',
    'TransferToLineQCApproveView',
    'TransferToLineQCRejectView',
    'TransferToLineCreateWarehouseTransferView',
    'TransferToLineUnlockView',
    # Performance Record views
    'PerformanceRecordListView',
    'PerformanceRecordCreateView',
    'PerformanceRecordDetailView',
    'PerformanceRecordUpdateView',
    'PerformanceRecordDeleteView',
    'PerformanceRecordApproveView',
    'PerformanceRecordRejectView',
    'PerformanceRecordCreateReceiptView',
    # Placeholder views
    'TrackingIdentificationView',
]


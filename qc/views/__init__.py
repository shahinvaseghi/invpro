"""
Views package for QC module.

This package contains refactored views organized by functionality:
- base: Base view classes
- inspections: Temporary receipt QC inspection views
"""
__all__ = []

# Import base views
from qc.views.base import QCBaseView

# Import inspection views
from qc.views.inspections import (
    TemporaryReceiptQCListView,
    TemporaryReceiptQCLineSelectionView,
    TemporaryReceiptQCApproveView,
    TemporaryReceiptQCRejectView,
    TemporaryReceiptQCRejectionManagementView,
    TemporaryReceiptQCRejectionManagementSaveView,
)

# Import serial assignment views
from qc.views.serials import (
    QCSerialAssignmentListView,
    QCSerialAssignmentView,
    QCSerialAssignmentLineView,
)

# Import batch assignment views
from qc.views.batches import (
    QCBatchAssignmentListView,
    QCBatchAssignmentView,
    QCBatchAssignmentLineView,
)

__all__ = [
    # Base views
    'QCBaseView',
    # Inspection views
    'TemporaryReceiptQCListView',
    'TemporaryReceiptQCLineSelectionView',
    'TemporaryReceiptQCApproveView',
    'TemporaryReceiptQCRejectView',
    'TemporaryReceiptQCRejectionManagementView',
    'TemporaryReceiptQCRejectionManagementSaveView',
    # Serial assignment views
    'QCSerialAssignmentListView',
    'QCSerialAssignmentView',
    'QCSerialAssignmentLineView',
    # Batch assignment views
    'QCBatchAssignmentListView',
    'QCBatchAssignmentView',
    'QCBatchAssignmentLineView',
]


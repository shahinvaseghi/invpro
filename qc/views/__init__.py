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
)

__all__ = [
    # Base views
    'QCBaseView',
    # Inspection views
    'TemporaryReceiptQCListView',
    'TemporaryReceiptQCLineSelectionView',
    'TemporaryReceiptQCApproveView',
    'TemporaryReceiptQCRejectView',
]


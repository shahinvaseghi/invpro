"""
Views for the QC module.

This file is kept for backward compatibility.
All views have been refactored into qc.views package.
"""
# Import all views from the refactored package
from qc.views import (
    QCBaseView,
    TemporaryReceiptQCListView,
    TemporaryReceiptQCApproveView,
    TemporaryReceiptQCRejectView,
)

__all__ = [
    'QCBaseView',
    'TemporaryReceiptQCListView',
    'TemporaryReceiptQCApproveView',
    'TemporaryReceiptQCRejectView',
]

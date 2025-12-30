from django.urls import path
from . import views

app_name = 'qc'

urlpatterns = [
    # Existing QC inspection URLs
    path('temporary-receipts/', views.TemporaryReceiptQCListView.as_view(), name='temporary_receipts'),
    path('temporary-receipts/<int:pk>/approve-lines/', views.TemporaryReceiptQCLineSelectionView.as_view(), name='temporary_receipt_line_selection'),
    path('temporary-receipts/<int:pk>/approve/', views.TemporaryReceiptQCApproveView.as_view(), name='temporary_receipt_approve'),
    path('temporary-receipts/<int:pk>/reject/', views.TemporaryReceiptQCRejectView.as_view(), name='temporary_receipt_reject'),
    path('temporary-receipts/<int:pk>/rejection-reasons/', views.TemporaryReceiptQCRejectionManagementView.as_view(), name='temporary_receipt_rejection_management'),
    path('temporary-receipts/<int:pk>/rejection-reasons/save/', views.TemporaryReceiptQCRejectionManagementSaveView.as_view(), name='temporary_receipt_rejection_management_save'),

    # Serial Assignment URLs
    path('serial-assignment/', views.QCSerialAssignmentListView.as_view(), name='serial_assignment_list'),
    path('temporary-receipts/<int:pk>/assign-serials/', views.QCSerialAssignmentView.as_view(), name='temporary_receipt_serial_assignment'),
    path('temporary-receipts/<int:pk>/line/<int:line_id>/assign-serials/', views.QCSerialAssignmentLineView.as_view(), name='temporary_receipt_line_serial_assignment'),

    # Batch Assignment URLs
    path('batch-assignment/', views.QCBatchAssignmentListView.as_view(), name='batch_assignment_list'),
    path('temporary-receipts/<int:pk>/assign-batches/', views.QCBatchAssignmentView.as_view(), name='temporary_receipt_batch_assignment'),
    path('temporary-receipts/<int:pk>/line/<int:line_id>/assign-batch/', views.QCBatchAssignmentLineView.as_view(), name='temporary_receipt_line_batch_assignment'),
]


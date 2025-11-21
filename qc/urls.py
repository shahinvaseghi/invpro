from django.urls import path
from . import views

app_name = 'qc'

urlpatterns = [
    path('temporary-receipts/', views.TemporaryReceiptQCListView.as_view(), name='temporary_receipts'),
    path('temporary-receipts/<int:pk>/approve/', views.TemporaryReceiptQCApproveView.as_view(), name='temporary_receipt_approve'),
    path('temporary-receipts/<int:pk>/reject/', views.TemporaryReceiptQCRejectView.as_view(), name='temporary_receipt_reject'),
]


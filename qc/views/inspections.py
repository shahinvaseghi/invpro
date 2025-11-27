"""
Temporary Receipt QC Inspection views.
"""
from typing import Dict, Any
from django.contrib import messages
from django.views.generic import ListView, View
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from inventory import models as inventory_models
from qc.views.base import QCBaseView
from shared.mixins import FeaturePermissionRequiredMixin


class TemporaryReceiptQCListView(FeaturePermissionRequiredMixin, QCBaseView, ListView):
    """List view for temporary receipts awaiting QC inspection."""
    model = inventory_models.ReceiptTemporary
    template_name = 'qc/temporary_receipts.html'
    context_object_name = 'receipts'
    paginate_by = 50
    feature_code = 'qc.inspections'
    required_action = 'view'
    
    def get_queryset(self):
        """Filter to only show receipts awaiting inspection and not locked."""
        queryset = super().get_queryset()
        # Only show receipts that are awaiting inspection and not locked
        # Note: item and warehouse are in ReceiptTemporaryLine, not in ReceiptTemporary
        queryset = queryset.filter(
            status=inventory_models.ReceiptTemporary.Status.AWAITING_INSPECTION,
            is_locked=0,
            is_enabled=1
        ).select_related('supplier', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Temporary Receipts - QC Inspection')
        return context


class TemporaryReceiptQCApproveView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to approve a temporary receipt for QC."""
    feature_code = 'qc.inspections'
    required_action = 'approve'
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Approve a temporary receipt for QC."""
        receipt = get_object_or_404(
            inventory_models.ReceiptTemporary,
            pk=kwargs['pk'],
            company_id=request.session.get('active_company_id'),
            is_enabled=1
        )
        
        # Check if already locked
        if receipt.is_locked:
            messages.error(request, _('This receipt is already locked.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipts'))
        
        # Check if already converted
        if receipt.is_converted:
            messages.error(request, _('This receipt has already been converted to a permanent receipt.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipts'))
        
        # Get approval notes from POST data
        approval_notes: str = request.POST.get('approval_notes', '').strip()
        
        with transaction.atomic():
            # Update receipt with QC approval
            receipt.qc_approved_by = request.user
            receipt.qc_approved_at = timezone.now()
            receipt.qc_approval_notes = approval_notes
            receipt.status = inventory_models.ReceiptTemporary.Status.APPROVED
            receipt.is_locked = 1  # Lock the receipt after approval
            receipt.save(update_fields=['qc_approved_by', 'qc_approved_at', 'qc_approval_notes', 'status', 'is_locked'])
            
            messages.success(request, _('Temporary receipt approved for QC. The receipt is now locked and can be converted to a permanent receipt.'))
        
        return HttpResponseRedirect(reverse('qc:temporary_receipts'))


class TemporaryReceiptQCRejectView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to reject a temporary receipt for QC."""
    feature_code = 'qc.inspections'
    required_action = 'reject'
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Reject a temporary receipt for QC."""
        receipt = get_object_or_404(
            inventory_models.ReceiptTemporary,
            pk=kwargs['pk'],
            company_id=request.session.get('active_company_id'),
            is_enabled=1
        )
        
        # Check if already locked
        if receipt.is_locked:
            messages.error(request, _('This receipt is already locked.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipts'))
        
        # Get rejection notes from POST data
        rejection_notes: str = request.POST.get('rejection_notes', '').strip()
        if not rejection_notes:
            messages.error(request, _('Rejection notes are required.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipts'))
        
        with transaction.atomic():
            # Update receipt with QC rejection
            receipt.qc_approved_by = None  # Clear approval
            receipt.qc_approved_at = None
            receipt.qc_approval_notes = rejection_notes
            receipt.status = inventory_models.ReceiptTemporary.Status.CLOSED  # Mark as closed/rejected
            receipt.is_locked = 1  # Lock the receipt after rejection
            receipt.save()
            
            messages.success(request, _('Temporary receipt rejected for QC. The receipt is now locked and cannot be converted to a permanent receipt.'))
        
        return HttpResponseRedirect(reverse('qc:temporary_receipts'))


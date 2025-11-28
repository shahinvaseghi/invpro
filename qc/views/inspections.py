"""
Temporary Receipt QC Inspection views.
"""
from typing import Dict, Any
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.views.generic import ListView, View, TemplateView
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
        """Show all receipts (awaiting, approved, rejected) - locked ones are read-only."""
        queryset = super().get_queryset()
        # Show all receipts (awaiting, approved, rejected) - they should all be visible
        # Locked receipts (approved/rejected) will be shown but without action buttons
        # Note: item and warehouse are in ReceiptTemporaryLine, not in ReceiptTemporary
        queryset = queryset.filter(
            is_enabled=1
        ).select_related('supplier', 'created_by', 'qc_approved_by').prefetch_related('lines__item', 'lines__warehouse')
        # Order by: awaiting first (status=1), then approved (status=3), then rejected/closed (status=2), then by date
        queryset = queryset.order_by(
            'status',  # 1 (AWAITING_INSPECTION) < 2 (CLOSED) < 3 (APPROVED)
            '-document_date',
            'document_code'
        )
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add page title and stats to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Temporary Receipts - QC Inspection')
        
        # Calculate stats
        queryset = self.get_queryset()
        context['stats'] = {
            'awaiting_qc': queryset.filter(status=inventory_models.ReceiptTemporary.Status.AWAITING_INSPECTION).count(),
            'approved': queryset.filter(status=inventory_models.ReceiptTemporary.Status.APPROVED).count(),
            'rejected': queryset.filter(status=inventory_models.ReceiptTemporary.Status.CLOSED).count(),
        }
        
        return context


class TemporaryReceiptQCLineSelectionView(FeaturePermissionRequiredMixin, QCBaseView, TemplateView):
    """View to select lines and quantities for QC approval."""
    template_name = 'qc/temporary_receipt_line_selection.html'
    feature_code = 'qc.inspections'
    required_action = 'approve'
    
    def get_receipt(self):
        """Get temporary receipt from URL."""
        return get_object_or_404(
            inventory_models.ReceiptTemporary,
            pk=self.kwargs['pk'],
            company_id=self.request.session.get('active_company_id'),
            is_enabled=1
        )
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add receipt and lines to context."""
        context = super().get_context_data(**kwargs)
        receipt = self.get_receipt()
        
        # Check if already locked
        if receipt.is_locked:
            messages.error(self.request, _('This receipt is already locked.'))
            return context
        
        # Check if already converted
        if receipt.is_converted:
            messages.error(self.request, _('This receipt has already been converted to a permanent receipt.'))
            return context
        
        # Get all lines with prefetch
        lines = receipt.lines.filter(is_enabled=1).select_related('item', 'warehouse').order_by('sort_order', 'id')
        
        context['receipt'] = receipt
        context['lines'] = lines
        context['page_title'] = _('QC Approval - Select Lines')
        
        return context


class TemporaryReceiptQCApproveView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to approve selected lines of a temporary receipt for QC."""
    feature_code = 'qc.inspections'
    required_action = 'approve'
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Approve selected lines of a temporary receipt for QC."""
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
        
        # Get selected lines with approved quantities
        selected_lines = []
        for line in receipt.lines.filter(is_enabled=1):
            line_id = str(line.pk)
            quantity_key = f'approved_quantity_{line_id}'
            selected_key = f'selected_{line_id}'
            
            if request.POST.get(selected_key) == 'on':
                quantity_str = request.POST.get(quantity_key, '0')
                try:
                    quantity = Decimal(str(quantity_str))
                    if quantity > 0:
                        # Validate quantity doesn't exceed line quantity
                        if quantity > line.quantity:
                            quantity = line.quantity
                        line_notes = request.POST.get(f'line_notes_{line_id}', '').strip()
                        selected_lines.append({
                            'line': line,
                            'quantity': quantity,
                            'notes': line_notes,
                        })
                except (ValueError, InvalidOperation):
                    pass
        
        if not selected_lines:
            messages.error(request, _('Please select at least one line to approve.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipt_line_selection', kwargs={'pk': receipt.pk}))
        
        with transaction.atomic():
            # Update each selected line with QC approval
            for item in selected_lines:
                line = item['line']
                line.is_qc_approved = 1
                line.qc_approved_quantity = item['quantity']
                line.qc_approval_notes = item['notes']
                line.save(update_fields=['is_qc_approved', 'qc_approved_quantity', 'qc_approval_notes'])
            
            # Update receipt header with QC approval
            receipt.qc_approved_by = request.user
            receipt.qc_approved_at = timezone.now()
            receipt.qc_approval_notes = approval_notes
            receipt.status = inventory_models.ReceiptTemporary.Status.APPROVED
            receipt.is_locked = 1  # Lock the receipt after approval
            receipt.save(update_fields=['qc_approved_by', 'qc_approved_at', 'qc_approval_notes', 'status', 'is_locked'])
            
            messages.success(request, _('Selected lines approved for QC. The receipt is now locked and can be converted to a permanent receipt.'))
        
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


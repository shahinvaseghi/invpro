"""
Views for the QC module.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from inventory import models as inventory_models
from shared.mixins import FeaturePermissionRequiredMixin


class QCBaseView(LoginRequiredMixin):
    """Base view with common context for QC module."""
    login_url = '/admin/login/'
    
    def get_queryset(self):
        """Filter queryset by active company."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(queryset.model, 'company'):
            queryset = queryset.filter(company_id=company_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'qc'
        return context


class TemporaryReceiptQCListView(FeaturePermissionRequiredMixin, QCBaseView, ListView):
    """List view for temporary receipts awaiting QC inspection."""
    model = inventory_models.ReceiptTemporary
    template_name = 'qc/temporary_receipts.html'
    context_object_name = 'receipts'
    paginate_by = 50
    feature_code = 'qc.inspections'
    required_action = 'view'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show receipts that are awaiting inspection and not locked
        queryset = queryset.filter(
            status=inventory_models.ReceiptTemporary.Status.AWAITING_INSPECTION,
            is_locked=0,
            is_enabled=1
        ).select_related('item', 'warehouse', 'supplier', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Temporary Receipts - QC Inspection')
        return context


class TemporaryReceiptQCApproveView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to approve a temporary receipt for QC."""
    feature_code = 'qc.inspections'
    required_action = 'approve'
    
    def post(self, request, *args, **kwargs):
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
        approval_notes = request.POST.get('approval_notes', '').strip()
        
        with transaction.atomic():
            # Update receipt with QC approval
            receipt.qc_approved_by = request.user
            receipt.qc_approved_at = timezone.now()
            receipt.qc_approval_notes = approval_notes
            receipt.status = inventory_models.ReceiptTemporary.Status.AWAITING_INSPECTION  # Keep status as awaiting inspection, but mark as approved
            receipt.is_locked = 1  # Lock the receipt after approval
            receipt.save()
            
            messages.success(request, _('Temporary receipt approved for QC. The receipt is now locked and can be converted to a permanent receipt.'))
        
        return HttpResponseRedirect(reverse('qc:temporary_receipts'))


class TemporaryReceiptQCRejectView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to reject a temporary receipt for QC."""
    feature_code = 'qc.inspections'
    required_action = 'reject'
    
    def post(self, request, *args, **kwargs):
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
        rejection_notes = request.POST.get('rejection_notes', '').strip()
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

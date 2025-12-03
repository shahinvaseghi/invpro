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
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'qc.inspections'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Show all receipts (awaiting, approved, rejected) - locked ones are read-only."""
        queryset = super().get_queryset()
        # Show all receipts (awaiting, approved, rejected) - they should all be visible
        # Locked receipts (approved/rejected) will be shown but without action buttons
        # Note: item and warehouse are in ReceiptTemporaryLine, not in ReceiptTemporary
        queryset = queryset.filter(
            is_enabled=1
        ).select_related('supplier', 'created_by', 'qc_approved_by').prefetch_related(
            'lines__item', 
            'lines__warehouse'
        )
        # Order by: awaiting first (status=1), then approved (status=3), then rejected/closed (status=2), then by date
        queryset = queryset.order_by(
            'status',  # 1 (AWAITING_INSPECTION) < 2 (CLOSED) < 3 (APPROVED)
            '-document_date',
            'document_code'
        )
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        from django.urls import reverse_lazy
        
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Temporary Receipts - QC Inspection')
        context['breadcrumbs'] = [
            {'label': _('QC'), 'url': None},
            {'label': _('Temporary Receipts'), 'url': None},
        ]
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['view_url_name'] = 'inventory:receipt_temporary_detail'  # Use detail view from inventory
        context['empty_state_title'] = _('No Receipts')
        context['empty_state_message'] = _('There are no temporary receipts.')
        context['empty_state_icon'] = '📋'
        context['print_enabled'] = True
        context['show_filters'] = False  # No filters for now
        
        # Calculate stats
        queryset = self.get_queryset()
        context['stats'] = {
            'awaiting_qc': queryset.filter(status=inventory_models.ReceiptTemporary.Status.AWAITING_INSPECTION).count(),
            'approved': queryset.filter(status=inventory_models.ReceiptTemporary.Status.APPROVED).count(),
            'rejected': queryset.filter(status=inventory_models.ReceiptTemporary.Status.CLOSED).count(),
        }
        
        # Prefetch rejected lines count for each receipt to show management button
        object_list = context.get('object_list', [])
        for receipt in object_list:
            # Count rejected lines and add as attribute (without underscore for template access)
            receipt.rejected_lines_count = receipt.lines.filter(is_enabled=1, is_qc_rejected=1).count()
        
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
        
        # Get selected lines with approved and rejected quantities
        approved_lines = []
        rejected_lines = []
        
        for line in receipt.lines.filter(is_enabled=1):
            line_id = str(line.pk)
            approve_key = f'selected_approve_{line_id}'
            reject_key = f'selected_reject_{line_id}'
            approved_quantity_key = f'approved_quantity_{line_id}'
            rejected_quantity_key = f'rejected_quantity_{line_id}'
            
            # Process approved lines
            if request.POST.get(approve_key) == 'on':
                quantity_str = request.POST.get(approved_quantity_key, '0')
                try:
                    quantity = Decimal(str(quantity_str))
                    if quantity > 0:
                        # Validate quantity doesn't exceed line quantity
                        if quantity > line.quantity:
                            quantity = line.quantity
                        line_notes = request.POST.get(f'line_notes_{line_id}', '').strip()
                        approved_lines.append({
                            'line': line,
                            'quantity': quantity,
                            'notes': line_notes,
                        })
                except (ValueError, InvalidOperation):
                    pass
            
            # Process rejected lines
            # Check if checkbox is checked OR if quantity is greater than 0
            reject_checkbox_checked = request.POST.get(reject_key) == 'on'
            quantity_str = request.POST.get(rejected_quantity_key, '0')
            try:
                quantity = Decimal(str(quantity_str))
                if quantity > 0:
                    # If quantity > 0, treat as rejected even if checkbox not checked
                    if reject_checkbox_checked or quantity > 0:
                        # Validate quantity doesn't exceed line quantity
                        if quantity > line.quantity:
                            quantity = line.quantity
                        rejected_lines.append({
                            'line': line,
                            'quantity': quantity,
                        })
            except (ValueError, InvalidOperation):
                pass
        
        # Validate that approved + rejected quantities don't exceed original for each line
        # Check all lines that have either approval or rejection
        all_processed_lines = {}
        for item in approved_lines:
            line_id = item['line'].pk
            all_processed_lines[line_id] = {
                'line': item['line'],
                'approved': item['quantity'],
                'rejected': Decimal('0')
            }
        for item in rejected_lines:
            line_id = item['line'].pk
            if line_id in all_processed_lines:
                all_processed_lines[line_id]['rejected'] = item['quantity']
            else:
                all_processed_lines[line_id] = {
                    'line': item['line'],
                    'approved': Decimal('0'),
                    'rejected': item['quantity']
                }
        
        # Validate each processed line
        for line_id, data in all_processed_lines.items():
            total = data['approved'] + data['rejected']
            if total > data['line'].quantity:
                messages.error(request, _('For line {item}, total approved and rejected quantities ({total}) exceed original quantity ({original}).').format(
                    item=data['line'].item.name,
                    total=total,
                    original=data['line'].quantity
                ))
                return HttpResponseRedirect(reverse('qc:temporary_receipt_line_selection', kwargs={'pk': receipt.pk}))
        
        if not approved_lines and not rejected_lines:
            messages.error(request, _('Please select at least one line to approve or reject.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipt_line_selection', kwargs={'pk': receipt.pk}))
        
        with transaction.atomic():
            # Update each approved line
            for item in approved_lines:
                line = item['line']
                line.is_qc_approved = 1
                line.qc_approved_quantity = item['quantity']
                line.qc_approval_notes = item['notes']
                line.save(update_fields=['is_qc_approved', 'qc_approved_quantity', 'qc_approval_notes'])
            
            # Update each rejected line
            for item in rejected_lines:
                line = item['line']
                line.is_qc_rejected = 1
                line.qc_rejected_quantity = item['quantity']
                # rejection_reason will be set later in rejection management view
                line.save(update_fields=['is_qc_rejected', 'qc_rejected_quantity'])
            
            # Determine receipt status based on lines
            # If all lines are approved, status = APPROVED
            # If all lines are rejected, status = CLOSED
            # If mixed, status = APPROVED (but some lines are rejected)
            has_approved = len(approved_lines) > 0
            has_rejected = len(rejected_lines) > 0
            
            if has_approved and not has_rejected:
                receipt.status = inventory_models.ReceiptTemporary.Status.APPROVED
            elif has_rejected and not has_approved:
                receipt.status = inventory_models.ReceiptTemporary.Status.CLOSED
            else:
                # Mixed: some approved, some rejected
                receipt.status = inventory_models.ReceiptTemporary.Status.APPROVED
            
            # Update receipt header
            receipt.qc_approved_by = request.user
            receipt.qc_approved_at = timezone.now()
            receipt.qc_approval_notes = approval_notes
            receipt.is_locked = 1  # Lock the receipt after approval/rejection
            receipt.save(update_fields=['qc_approved_by', 'qc_approved_at', 'qc_approval_notes', 'status', 'is_locked'])
            
            if has_approved and has_rejected:
                messages.success(request, _('Lines processed. Some lines were approved and some were rejected. You can now manage rejection reasons.'))
            elif has_approved:
                messages.success(request, _('Selected lines approved for QC. The receipt is now locked and can be converted to a permanent receipt.'))
            else:
                messages.success(request, _('Selected lines rejected for QC. You can now manage rejection reasons.'))
        
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


class TemporaryReceiptQCRejectionManagementView(FeaturePermissionRequiredMixin, QCBaseView, TemplateView):
    """View to manage rejection reasons for rejected lines."""
    template_name = 'qc/temporary_receipt_rejection_management.html'
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
        """Add receipt and rejected lines to context."""
        context = super().get_context_data(**kwargs)
        receipt = self.get_receipt()
        
        # Get only rejected lines with their rejection details
        rejected_lines = receipt.lines.filter(
            is_enabled=1,
            is_qc_rejected=1
        ).select_related('item', 'warehouse').prefetch_related('rejection_details').order_by('sort_order', 'id')
        
        context['receipt'] = receipt
        context['rejected_lines'] = rejected_lines
        context['page_title'] = _('QC Rejection Reasons Management')
        
        return context


class TemporaryReceiptQCRejectionManagementSaveView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to save rejection reasons for rejected lines."""
    feature_code = 'qc.inspections'
    required_action = 'approve'
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Save rejection reasons and details for rejected lines."""
        receipt = get_object_or_404(
            inventory_models.ReceiptTemporary,
            pk=kwargs['pk'],
            company_id=request.session.get('active_company_id'),
            is_enabled=1
        )
        
        # Get rejected lines
        rejected_lines = receipt.lines.filter(is_enabled=1, is_qc_rejected=1)
        company_id = request.session.get('active_company_id')
        
        if not company_id:
            messages.error(request, _('No active company selected.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipts'))
        
        updated_count = 0
        detail_count = 0
        
        with transaction.atomic():
            for line in rejected_lines:
                line_id = str(line.pk)
                
                # Get detail quantities and reasons
                detail_quantities = request.POST.getlist(f'detail_quantity_{line_id}[]')
                detail_reasons = request.POST.getlist(f'detail_reason_{line_id}[]')
                detail_ids = request.POST.getlist(f'detail_id_{line_id}[]')
                
                # Validate total quantity
                total_detail_quantity = sum(Decimal(str(qty)) for qty in detail_quantities if qty)
                
                if abs(total_detail_quantity - line.qc_rejected_quantity) > Decimal('0.001'):
                    messages.error(request, _('For line {item}, total detail quantities ({total}) must equal rejected quantity ({rejected}).').format(
                        item=line.item.name,
                        total=total_detail_quantity,
                        rejected=line.qc_rejected_quantity
                    ))
                    return HttpResponseRedirect(reverse('qc:temporary_receipt_rejection_management', kwargs={'pk': receipt.pk}))
                
                # Delete existing details that are not in the new list
                existing_detail_ids = [str(d.id) for d in line.rejection_details.all()]
                detail_ids_to_keep = [did for did in detail_ids if did and did in existing_detail_ids]
                line.rejection_details.exclude(pk__in=detail_ids_to_keep).delete()
                
                # Update or create details
                for i, (quantity_str, reason) in enumerate(zip(detail_quantities, detail_reasons)):
                    if not quantity_str or not reason.strip():
                        continue
                    
                    try:
                        quantity = Decimal(str(quantity_str))
                        if quantity <= 0:
                            continue
                        
                        reason = reason.strip()
                        if not reason:
                            continue
                        
                        detail_id = detail_ids[i] if i < len(detail_ids) and detail_ids[i] else None
                        
                        if detail_id:
                            # Update existing detail
                            detail = line.rejection_details.filter(pk=detail_id).first()
                            if detail:
                                detail.quantity = quantity
                                detail.reason = reason
                                detail.save(update_fields=['quantity', 'reason'])
                                detail_count += 1
                        else:
                            # Create new detail
                            inventory_models.QCRejectionDetail.objects.create(
                                line=line,
                                company_id=company_id,
                                quantity=quantity,
                                reason=reason,
                                created_by=request.user
                            )
                            detail_count += 1
                    except (ValueError, InvalidOperation):
                        continue
                
                updated_count += 1
        
        if detail_count > 0:
            messages.success(request, _('Rejection details saved: {count} detail(s) for {lines} line(s).').format(
                count=detail_count,
                lines=updated_count
            ))
        else:
            messages.warning(request, _('No rejection details were provided.'))
        
        return HttpResponseRedirect(reverse('qc:temporary_receipts'))


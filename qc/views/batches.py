"""
QC Batch Assignment views.
Handles batch number assignment for items received through temporary receipts after QC approval.
"""
from typing import Dict, Any, Optional, List
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils import timezone
from django.template import Template, Context
from django.utils.safestring import mark_safe

from inventory import models as inventory_models
from qc.models import ItemBatch
from qc.views.base import QCBaseView
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import BaseListView


class QCBatchAssignmentListView(BaseListView):
    """List temporary receipts that need batch assignment after QC approval."""
    model = inventory_models.ReceiptTemporary
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'qc.batch_assignment'
    required_action = 'view_own'
    active_module = 'qc'
    default_status_filter = False
    default_order_by = ['-qc_approved_at', '-document_date', 'document_code']

    def get_table_headers(self) -> List[Dict[str, Any]]:
        """Define table headers for the generic template."""
        return [
            {
                'label': _('Document Code'),
                'field': 'document_code',
                'type': 'code',
            },
            {
                'label': _('Date'),
                'field': 'document_date',
                'type': 'date',
            },
            {
                'label': _('Supplier'),
                'field': 'supplier.name',
                'type': 'text',
            },
            {
                'label': _('Lines'),
                'custom_content': '{{ object.lines_needing_batches }} lines need batches',
            },
            {
                'label': _('Batch Status'),
                'custom_content': '{% if object.batches_complete %}<span class="badge badge-success">Complete</span>{% else %}<span class="badge badge-warning">{{ object.lines_with_complete_batches }}/{{ object.lines_needing_batches }} complete</span>{% endif %}',
            },
        ]

    def get_show_actions(self) -> bool:
        """Show actions column."""
        return True

    def get_row_actions(self, obj) -> List[Dict[str, Any]]:
        """Define row actions for each object."""
        return [
            {
                'label': _('Assign Batches'),
                'url': reverse('qc:temporary_receipt_batch_assignment', kwargs={'pk': obj.pk}),
                'icon': 'icon-tag',
                'class': 'btn-primary',
            },
        ]

    def get_base_queryset(self):
        """Get base queryset with QC approved receipts that have items requiring temporary receipt."""
        return self.model.objects.filter(
            is_enabled=1,
            status=self.model.Status.APPROVED,  # QC approved
            is_locked=1,  # Locked after QC
            is_converted=0,  # Not yet converted to permanent
        ).filter(
            # Has at least one line that is QC approved
            lines__is_enabled=1,
            lines__is_qc_approved=1
        ).distinct()

    def get_select_related(self) -> List[str]:
        return [
            'supplier', 'created_by', 'qc_approved_by'
        ]

    def get_prefetch_related(self) -> List[str]:
        return ['lines__item', 'lines__warehouse']

    def get_page_title(self) -> str:
        return _('QC Batch Assignment')

    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        return [
            {'label': _('QC'), 'url': None},
            {'label': _('Batch Assignment'), 'url': None},
        ]

    def get_empty_state_title(self) -> str:
        return _('No Receipts Need Batch Assignment')

    def get_empty_state_message(self) -> str:
        return _('There are no QC-approved receipts that require batch assignment.')

    def get_empty_state_icon(self) -> str:
        return '🏷️'

    def get_detail_url_name(self) -> Optional[str]:
        return 'qc:temporary_receipt_batch_assignment'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['show_filters'] = False
        context['print_enabled'] = True
        context['view_url_name'] = 'qc:temporary_receipt_batch_assignment'
        context['table_headers'] = self.get_table_headers()

        # Add batch assignment status and custom actions for each receipt
        object_list = context.get('object_list', [])
        table_headers = context.get('table_headers', [])
        
        for receipt in object_list:
            # Count lines that need batches vs lines that have batches
            total_lines_needing_batches = 0
            lines_with_complete_batches = 0

            for line in receipt.lines.filter(is_enabled=1, is_qc_approved=1):
                # All lines in temporary receipt need batches
                total_lines_needing_batches += 1
                # Check if batch exists for this line
                existing_batches = ItemBatch.objects.filter(
                    receipt_temporary_line=line,
                    company=receipt.company,
                    is_enabled=1
                ).count()
                if existing_batches > 0:
                    lines_with_complete_batches += 1

            receipt.lines_needing_batches = total_lines_needing_batches
            receipt.lines_with_complete_batches = lines_with_complete_batches
            receipt.batches_complete = (lines_with_complete_batches == total_lines_needing_batches and total_lines_needing_batches > 0)
            
            # Add custom actions for this object
            receipt.custom_actions = self.get_row_actions(receipt)
            
            # Render custom_content for headers that have it
            if not hasattr(receipt, 'custom_content_rendered'):
                receipt.custom_content_rendered = {}
            for header in table_headers:
                if header.get('custom_content'):
                    try:
                        template_str = header['custom_content']
                        template_obj = Template(template_str)
                        context_obj = Context({'object': receipt})
                        rendered = template_obj.render(context_obj)
                        # Store rendered content in object with header label as key
                        receipt.custom_content_rendered[header['label']] = mark_safe(rendered)
                    except Exception as e:
                        receipt.custom_content_rendered[header['label']] = '-'

        return context


class QCBatchAssignmentView(FeaturePermissionRequiredMixin, QCBaseView, TemplateView):
    """View to assign batches to all lines of a QC-approved temporary receipt."""
    template_name = 'qc/batch_assignment.html'
    feature_code = 'qc.batch_assignment'
    required_action = 'approve'

    def get_receipt(self):
        return get_object_or_404(
            inventory_models.ReceiptTemporary,
            pk=self.kwargs['pk'],
            company_id=self.request.session.get('active_company_id'),
            is_enabled=1,
            status=inventory_models.ReceiptTemporary.Status.APPROVED,
            is_locked=1,
            is_converted=0
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        receipt = self.get_receipt()

        # Get lines that need batch assignment
        lines_needing_batches = []
        for line in receipt.lines.filter(is_enabled=1, is_qc_approved=1).select_related('item', 'warehouse'):
            # All lines in temporary receipt need batch assignment
            # Get existing batch for this line
            existing_batch = ItemBatch.objects.filter(
                receipt_temporary_line=line,
                company=receipt.company,
                is_enabled=1
            ).first()

            lines_needing_batches.append({
                'line': line,
                'existing_batch': existing_batch,
                'has_batch': existing_batch is not None,
            })

        context['receipt'] = receipt
        context['lines_needing_batches'] = lines_needing_batches
        context['page_title'] = _('QC Batch Assignment')

        return context


class QCBatchAssignmentLineView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to assign batch number to a specific line of a QC-approved temporary receipt."""
    feature_code = 'qc.batch_assignment'
    required_action = 'approve'

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        receipt = get_object_or_404(
            inventory_models.ReceiptTemporary,
            pk=kwargs['pk'],
            company_id=request.session.get('active_company_id'),
            is_enabled=1
        )

        line = get_object_or_404(
            inventory_models.ReceiptTemporaryLine,
            pk=kwargs['line_id'],
            document=receipt,
            is_enabled=1
        )

        # All items in temporary receipts need batch assignment
        # No additional validation needed since temporary receipt only accepts items that require QC

        # Get batch number from POST
        batch_number = request.POST.get('batch_number', '').strip()

        if not batch_number:
            messages.error(request, _('Batch number is required.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipt_batch_assignment', kwargs={'pk': receipt.pk}))

        # Validate batch number is unique within company
        existing_batch = ItemBatch.objects.filter(
            company=receipt.company,
            batch_number=batch_number,
            is_enabled=1
        ).exclude(receipt_temporary_line=line).first()

        if existing_batch:
            messages.error(request, _('Batch number "%(batch)s" already exists for another line.') % {'batch': batch_number})
            return HttpResponseRedirect(reverse('qc:temporary_receipt_batch_assignment', kwargs={'pk': receipt.pk}))

        # Get quantity (use QC approved quantity if available, otherwise original quantity)
        quantity = line.qc_approved_quantity or line.quantity

        # Create or update batch
        with transaction.atomic():
            # Remove existing batch for this line (should only be one per line)
            ItemBatch.objects.filter(
                receipt_temporary_line=line,
                company=receipt.company
            ).update(is_enabled=0)

            # Create new batch
            batch = ItemBatch.objects.create(
                company=receipt.company,
                item=line.item,
                item_code=line.item_code,
                batch_number=batch_number,
                receipt_temporary=receipt,
                receipt_temporary_code=receipt.document_code,
                receipt_temporary_line=line,
                quantity=quantity,
                unit=line.unit,
                warehouse=line.warehouse,
                warehouse_code=line.warehouse_code,
                status=ItemBatch.Status.AVAILABLE,
                created_by=request.user,
                edited_by=request.user,
            )

        messages.success(request, _('Batch number "%(batch)s" assigned successfully for line %(item)s.') % {
            'batch': batch_number,
            'item': line.item.name
        })
        return HttpResponseRedirect(reverse('qc:temporary_receipt_batch_assignment', kwargs={'pk': receipt.pk}))


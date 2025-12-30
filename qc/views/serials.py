"""
QC Serial Assignment views.
Handles serial number assignment for items with QC serial tracking after QC approval.
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
from qc.views.base import QCBaseView
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import BaseListView


class QCSerialAssignmentListView(BaseListView):
    """List temporary receipts that need serial assignment after QC approval."""
    model = inventory_models.ReceiptTemporary
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'qc.serials'
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
                'custom_content': '{{ object.lines_needing_serials }} lines need serials',
            },
            {
                'label': _('Serial Status'),
                'custom_content': '{% if object.serials_complete %}<span class="badge badge-success">Complete</span>{% else %}<span class="badge badge-warning">{{ object.lines_with_complete_serials }}/{{ object.lines_needing_serials }} complete</span>{% endif %}',
            },
        ]

    def get_show_actions(self) -> bool:
        """Show actions column."""
        return True

    def get_row_actions(self, obj) -> List[Dict[str, Any]]:
        """Define row actions for each object."""
        return [
            {
                'label': _('Assign Serials'),
                'url': reverse('qc:temporary_receipt_serial_assignment', kwargs={'pk': obj.pk}),
                'icon': 'icon-tag',
                'class': 'btn-primary',
            },
        ]

    def get_base_queryset(self):
        """Get base queryset with QC approved receipts that have serial-tracked items."""
        return self.model.objects.filter(
            is_enabled=1,
            status=self.model.Status.APPROVED,  # QC approved
            is_locked=1,  # Locked after QC
            is_converted=0,  # Not yet converted to permanent
        ).filter(
            # Has at least one line with item that has serial_in_qc=1
            lines__item__serial_in_qc=1,
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
        return _('QC Serial Assignment')

    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        return [
            {'label': _('QC'), 'url': None},
            {'label': _('Serial Assignment'), 'url': None},
        ]

    def get_empty_state_title(self) -> str:
        return _('No Receipts Need Serial Assignment')

    def get_empty_state_message(self) -> str:
        return _('There are no QC-approved receipts that require serial assignment.')

    def get_empty_state_icon(self) -> str:
        return '🏷️'

    def get_detail_url_name(self) -> Optional[str]:
        return 'qc:temporary_receipt_serial_assignment'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['show_filters'] = False
        context['print_enabled'] = True
        context['view_url_name'] = 'qc:temporary_receipt_serial_assignment'
        context['table_headers'] = self.get_table_headers()

        # Add serial assignment status and custom actions for each receipt
        object_list = context.get('object_list', [])
        table_headers = context.get('table_headers', [])
        
        for receipt in object_list:
            # Count lines that need serials vs lines that have serials
            total_lines_needing_serials = 0
            lines_with_complete_serials = 0

            for line in receipt.lines.filter(is_enabled=1, is_qc_approved=1):
                if line.item and line.item.serial_in_qc == 1:
                    total_lines_needing_serials += 1
                    # Query serials by receipt_line_reference
                    existing_serials = inventory_models.ItemSerial.objects.filter(
                        receipt_line_reference=f"QC:{line.pk}",
                        company=receipt.company,
                        is_enabled=1
                    ).count()
                    required_quantity = int(line.qc_approved_quantity or line.quantity)
                    if existing_serials >= required_quantity:
                        lines_with_complete_serials += 1

            receipt.lines_needing_serials = total_lines_needing_serials
            receipt.lines_with_complete_serials = lines_with_complete_serials
            receipt.serials_complete = (lines_with_complete_serials == total_lines_needing_serials)
            
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


class QCSerialAssignmentView(FeaturePermissionRequiredMixin, QCBaseView, TemplateView):
    """View to assign serials to all lines of a QC-approved temporary receipt."""
    template_name = 'qc/serial_assignment.html'
    feature_code = 'qc.serials'
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

        # Get lines that need serial assignment
        lines_needing_serials = []
        for line in receipt.lines.filter(is_enabled=1, is_qc_approved=1).select_related('item', 'warehouse'):
            if line.item and line.item.serial_in_qc == 1:
                # Query serials by receipt_line_reference
                existing_serials = list(inventory_models.ItemSerial.objects.filter(
                    receipt_line_reference=f"QC:{line.pk}",
                    company=receipt.company,
                    is_enabled=1
                ).values_list('serial_code', flat=True))
                required_quantity = int(line.qc_approved_quantity or line.quantity)
                lines_needing_serials.append({
                    'line': line,
                    'existing_serials': existing_serials,
                    'quantity_needed': required_quantity,
                    'serials_assigned': len(existing_serials),
                    'is_complete': len(existing_serials) >= required_quantity
                })

        context['receipt'] = receipt
        context['lines_needing_serials'] = lines_needing_serials
        context['page_title'] = _('QC Serial Assignment')

        return context


class QCSerialAssignmentLineView(FeaturePermissionRequiredMixin, QCBaseView, View):
    """View to assign serials to a specific line of a QC-approved temporary receipt."""
    feature_code = 'qc.serials'
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

        # Check if item requires QC serial tracking
        if not line.item or line.item.serial_in_qc != 1:
            messages.error(request, _('This item does not require QC serial assignment.'))
            return HttpResponseRedirect(reverse('qc:serial_assignment_list'))

        # Get serial codes from POST
        serial_codes = []
        for key, value in request.POST.items():
            if key.startswith('serial_') and value.strip():
                serial_codes.append(value.strip())

        required_quantity = int(line.qc_approved_quantity or line.quantity)

        if len(serial_codes) != required_quantity:
            messages.error(request, _('You must provide exactly %(count)s serial codes.') % {'count': required_quantity})
            return HttpResponseRedirect(reverse('qc:temporary_receipt_serial_assignment', kwargs={'pk': receipt.pk}))

        # Validate serial codes are unique
        if len(set(serial_codes)) != len(serial_codes):
            messages.error(request, _('Serial codes must be unique.'))
            return HttpResponseRedirect(reverse('qc:temporary_receipt_serial_assignment', kwargs={'pk': receipt.pk}))

        # Create serials
        with transaction.atomic():
            # Remove existing serials for this line
            inventory_models.ItemSerial.objects.filter(
                receipt_line_reference=f"QC:{line.pk}",
                company=receipt.company
            ).update(is_enabled=0)

            for serial_code in serial_codes:
                # Check if serial already exists
                existing_serial = inventory_models.ItemSerial.objects.filter(
                    serial_code=serial_code,
                    company=receipt.company,
                    is_enabled=1
                ).first()

                if existing_serial:
                    messages.error(request, _('Serial code "%(code)s" already exists.') % {'code': serial_code})
                    return HttpResponseRedirect(reverse('qc:temporary_receipt_serial_assignment', kwargs={'pk': receipt.pk}))

                # Create new serial
                serial = inventory_models.ItemSerial.objects.create(
                    company=receipt.company,
                    item=line.item,
                    item_code=line.item_code,
                    serial_code=serial_code,
                    receipt_document=None,  # Will be set when converted to permanent
                    receipt_document_code='',  # Will be set when converted to permanent
                    receipt_line_reference=f"QC:{line.pk}",
                    current_status=inventory_models.ItemSerial.Status.AVAILABLE,
                    current_warehouse=line.warehouse,
                    current_warehouse_code=line.warehouse_code,
                    created_by=request.user,
                    edited_by=request.user,
                )

                # Create history
                inventory_models.ItemSerialHistory.objects.create(
                    company=receipt.company,
                    item=line.item,
                    item_code=line.item_code,
                    serial=serial,
                    event_type=inventory_models.ItemSerialHistory.EventType.CREATED,
                    event_at=timezone.now(),
                    to_status=serial.current_status,
                    to_warehouse_code=serial.current_warehouse_code,
                    created_by=request.user,
                    edited_by=request.user,
                )

        messages.success(request, _('Serials assigned successfully for line %(item)s.') % {'item': line.item.name})
        return HttpResponseRedirect(reverse('qc:temporary_receipt_serial_assignment', kwargs={'pk': receipt.pk}))

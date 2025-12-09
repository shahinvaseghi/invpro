"""
Transfer to Line Request CRUD views for production module.
"""
from decimal import Decimal
from typing import Any, Dict, Optional, List
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django.views import View
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseDocumentListView,
    BaseDetailView,
    BaseDeleteView,
    BaseFormsetUpdateView,
    EditLockProtectedMixin,
)
from shared.views.base_additional import BaseMultipleDocumentCreateView
from inventory.forms.base import generate_document_code
from production.forms import TransferToLineForm, TransferToLineItemFormSet
from production.models import TransferToLine, TransferToLineItem, ProductOrder
from production.utils.transfer import generate_transfer_code


class TransferToLineListView(BaseDocumentListView):
    """List all transfer to line requests for the active company."""
    model = TransferToLine
    template_name = 'production/transfer_to_line_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.transfer_requests'
    required_action = 'view_own'
    active_module = 'production'
    default_status_filter = False
    default_order_by = ['-transfer_date', 'transfer_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['order', 'order__bom', 'order__finished_item', 'approved_by']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        from inventory.models import IssueWarehouseTransfer
        return [
            'items',
            Prefetch(
                'warehouse_transfers',
                queryset=IssueWarehouseTransfer.objects.filter(is_enabled=1),
                to_attr='active_warehouse_transfers'
            ),
        ]
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Transfer to Line Requests')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('production:transfer_request_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Transfer Request +')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:transfer_request_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:transfer_request_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:transfer_request_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Transfer Requests Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Create your first transfer request to get started.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📦'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['show_filters'] = False
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            from shared.utils.permissions import get_user_feature_permissions
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
        return context


class TransferToLineCreateView(BaseMultipleDocumentCreateView):
    """Create a new transfer to line request."""
    model = TransferToLine
    form_class = TransferToLineForm
    template_name = 'production/transfer_to_line_form.html'
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    required_action = 'create'
    active_module = 'production'
    success_message = _('Transfer requests created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': reverse_lazy('production:transfer_requests')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:transfer_requests')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Transfer Request')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formset and context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_id'] = 'transfer-form'
        
        # In CreateView, self.object is None initially, so we need to create a temporary instance
        instance = self.object if hasattr(self, 'object') and self.object else None
        
        if self.request.POST:
            context['formset'] = TransferToLineItemFormSet(
                self.request.POST,
                instance=instance,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        else:
            context['formset'] = TransferToLineItemFormSet(
                instance=instance,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        
        return context
    
    @transaction.atomic
    def form_valid(self, form: TransferToLineForm) -> HttpResponseRedirect:
        """Save transfer and create items from BOM - creates separate transfer for each operation."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        order = form.instance.order
        transfer_type = form.cleaned_data.get('transfer_type', 'full')
        selected_operations = form.cleaned_data.get('selected_operations', [])
        
        # Validate that order has process (required for operations)
        if not order.process:
            messages.error(self.request, _('Product order must have an associated process.'))
            return self.form_invalid(form)
        
        # Get formset for extra items (will be processed later)
        formset = TransferToLineItemFormSet(
            self.request.POST,
            instance=None,  # Will be set later for each transfer
            form_kwargs={'company_id': active_company_id}
        )
        
        # Collect extra items data (will be processed in section 3)
        extra_items_data = []
        if formset.is_valid():
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    extra_items_data.append(item_form.cleaned_data)
        
        # Identify operations to process
        from production.models import ProcessOperation
        from production.utils.transfer import get_operation_materials
        from inventory.models import ItemWarehouse
        
        if transfer_type == 'full':
            # Get all operations from the process
            operations = order.process.operations.filter(is_enabled=1).order_by('sequence_order', 'id')
        elif transfer_type == 'operations' and selected_operations:
            # Get only selected operations
            operation_ids = [int(op_id) for op_id in selected_operations]
            operations = ProcessOperation.objects.filter(
                id__in=operation_ids,
                process=order.process,
                is_enabled=1,
            ).order_by('sequence_order', 'id')
        else:
            operations = ProcessOperation.objects.none()
        
        if not operations.exists():
            messages.error(self.request, _('No operations found to transfer.'))
            return self.form_invalid(form)
        
        quantity_planned = order.quantity_planned
        created_transfers = []
        
        # Create a separate transfer document for each operation
        for operation in operations:
            # Create transfer header for this operation
            transfer = TransferToLine.objects.create(
                company_id=active_company_id,
                order=order,
                order_code=order.order_code,
                transfer_date=form.cleaned_data.get('transfer_date') or form.instance.transfer_date,
                transfer_code=generate_transfer_code(
                    company_id=active_company_id,
                    prefix='TR',
                    width=8,
                ),
                status=TransferToLine.Status.PENDING_APPROVAL,
                approved_by=form.cleaned_data.get('approved_by') or form.instance.approved_by,
                is_scrap_replacement=form.cleaned_data.get('is_scrap_replacement', False) or (form.instance.is_scrap_replacement == 1),
                qc_approved_by=form.cleaned_data.get('qc_approved_by') or form.instance.qc_approved_by,
                notes=form.cleaned_data.get('notes', '') or form.instance.notes,
                created_by=self.request.user,
            )
            created_transfers.append(transfer)
            
            # Get materials for this operation
            operation_materials = get_operation_materials(operation, order)
            
            if not operation_materials:
                # Skip operations with no materials
                continue
            
            # Create transfer items for this operation
            for op_material in operation_materials:
                # Calculate quantity: quantity_planned × quantity_used (from ProcessOperationMaterial)
                quantity_required = quantity_planned * op_material.quantity_used
                
                # Get scrap allowance and source_warehouses from BOM material if available
                scrap_allowance = Decimal('0.00')
                source_warehouses_list = []
                if op_material.bom_material:
                    scrap_allowance = op_material.bom_material.scrap_allowance
                    source_warehouses_list = op_material.bom_material.source_warehouses or []
                    
                    # Backward compatibility: if source_warehouses is empty but source_warehouse is set
                    if not source_warehouses_list and op_material.bom_material.source_warehouse:
                        source_warehouses_list = [{
                            'warehouse_id': op_material.bom_material.source_warehouse.id,
                            'warehouse_code': op_material.bom_material.source_warehouse.public_code,
                            'priority': 1
                        }]
                
                # Select source warehouse based on priority
                source_warehouse = None
                
                if source_warehouses_list and len(source_warehouses_list) > 0:
                    # Sort by priority and get first warehouse (priority 1)
                    sorted_warehouses = sorted(
                        source_warehouses_list,
                        key=lambda x: x.get('priority', 999)
                    )
                    
                    if sorted_warehouses and sorted_warehouses[0].get('warehouse_id'):
                        from inventory.models import Warehouse
                        try:
                            source_warehouse = Warehouse.objects.get(
                                id=sorted_warehouses[0]['warehouse_id'],
                                company_id=active_company_id,
                                is_enabled=1,
                            )
                        except Warehouse.DoesNotExist:
                            pass
                
                if not source_warehouse:
                    # Fallback: Get source warehouse from ItemWarehouse (first allowed warehouse)
                    item_warehouse = ItemWarehouse.objects.filter(
                        item=op_material.material_item,
                        company_id=active_company_id,
                        is_enabled=1,
                    ).select_related('warehouse').first()
                    
                    if not item_warehouse:
                        messages.warning(
                            self.request,
                            _('No allowed warehouse found for item {item_code} in operation {operation_name}. Please configure ItemWarehouse first.').format(
                                item_code=op_material.material_item.item_code,
                                operation_name=operation.name or f"Operation {operation.sequence_order}"
                            )
                        )
                        continue
                    
                    source_warehouse = item_warehouse.warehouse
                
                # Get destination work line from operation
                destination_work_line = operation.work_line
                
                # Create transfer item
                TransferToLineItem.objects.create(
                    transfer=transfer,
                    company_id=active_company_id,
                    material_item=op_material.material_item,
                    material_item_code=op_material.material_item_code,
                    quantity_required=quantity_required,
                    unit=op_material.unit,
                    source_warehouse=source_warehouse,
                    source_warehouse_code=source_warehouse.public_code,
                    destination_work_center=destination_work_line,  # Now points to WorkLine
                    material_scrap_allowance=scrap_allowance,
                    is_extra=0,  # From BOM/Operations
                    created_by=self.request.user,
                )
        
        # Section 3: Process extra items grouped by WorkLine
        # Group extra items by destination_work_center (WorkLine)
        from collections import defaultdict
        extra_items_by_workline = defaultdict(list)
        
        for extra_item_data in extra_items_data:
            destination_work_line = extra_item_data.get('destination_work_center')
            if destination_work_line:
                extra_items_by_workline[destination_work_line].append(extra_item_data)
            else:
                # If no WorkLine specified, skip or show warning
                messages.warning(
                    self.request,
                    _('Extra item {item_code} skipped: No destination work line specified.').format(
                        item_code=extra_item_data.get('material_item').item_code if extra_item_data.get('material_item') else 'Unknown'
                    )
                )
        
        # Create a separate transfer document for each WorkLine group of extra items
        for work_line, items_data in extra_items_by_workline.items():
            # Create transfer header for this WorkLine group
            transfer = TransferToLine.objects.create(
                company_id=active_company_id,
                order=order,
                order_code=order.order_code,
                transfer_date=form.cleaned_data.get('transfer_date') or form.instance.transfer_date,
                transfer_code=generate_transfer_code(
                    company_id=active_company_id,
                    prefix='TR',
                    width=8,
                ),
                status=TransferToLine.Status.PENDING_APPROVAL,
                approved_by=form.cleaned_data.get('approved_by') or form.instance.approved_by,
                is_scrap_replacement=form.cleaned_data.get('is_scrap_replacement', False) or (form.instance.is_scrap_replacement == 1),
                qc_approved_by=form.cleaned_data.get('qc_approved_by') or form.instance.qc_approved_by,
                notes=form.cleaned_data.get('notes', '') or form.instance.notes,
                created_by=self.request.user,
            )
            created_transfers.append(transfer)
            
            # Create transfer items for this WorkLine group
            for item_data in items_data:
                material_item = item_data.get('material_item')
                quantity_required = item_data.get('quantity_required')
                unit = item_data.get('unit')
                source_warehouse = item_data.get('source_warehouse')
                scrap_allowance = item_data.get('material_scrap_allowance', Decimal('0.00'))
                notes = item_data.get('notes', '')
                
                if not material_item or not quantity_required or not unit or not source_warehouse:
                    messages.warning(
                        self.request,
                        _('Extra item skipped: Missing required fields.')
                    )
                    continue
                
                # Create transfer item
                TransferToLineItem.objects.create(
                    transfer=transfer,
                    company_id=active_company_id,
                    material_item=material_item,
                    material_item_code=material_item.item_code,
                    quantity_required=quantity_required,
                    unit=unit,
                    source_warehouse=source_warehouse,
                    source_warehouse_code=source_warehouse.public_code,
                    destination_work_center=work_line,  # WorkLine
                    material_scrap_allowance=scrap_allowance,
                    notes=notes,
                    is_extra=1,  # Extra request
                    created_by=self.request.user,
                )
        
        # Set response to redirect to list (since we created multiple transfers)
        if created_transfers:
            messages.success(
                self.request,
                _('Successfully created {count} transfer request(s).').format(count=len(created_transfers))
            )
            # Set self.object to first created transfer for compatibility with get_success_url
            self.object = created_transfers[0]
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, _('No transfer requests were created.'))
            return self.form_invalid(form)


class TransferToLineUpdateView(BaseFormsetUpdateView, EditLockProtectedMixin):
    """Update an existing transfer to line request (only extra items can be edited)."""
    model = TransferToLine
    form_class = TransferToLineForm
    template_name = 'production/transfer_to_line_form.html'
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    required_action = 'edit_own'
    active_module = 'production'
    success_message = _('Transfer request updated successfully.')
    formset_class = TransferToLineItemFormSet
    formset_prefix = 'items'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = super().get_formset_kwargs()
        kwargs['form_kwargs'] = {'company_id': self.request.session.get('active_company_id')}
        return kwargs
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formset and context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_id'] = 'transfer-form'
        
        # Filter formset to only show extra items
        if 'formset' in context:
            context['formset'].queryset = context['formset'].queryset.filter(is_extra=1)
        
        # Add BOM items (read-only)
        context['bom_items'] = self.object.items.filter(is_extra=0) if self.object else []
        context['is_locked'] = self.object.is_locked == 1 if self.object else False
        
        return context
    
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': reverse_lazy('production:transfer_requests')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:transfer_requests')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Transfer Request')
    
    def form_valid(self, form: TransferToLineForm) -> HttpResponseRedirect:
        """Save transfer and update extra items."""
        # Check if locked
        if self.object.is_locked == 1:
            messages.error(self.request, _('This transfer request is locked and cannot be edited.'))
            return HttpResponseRedirect(self.get_success_url())
        
        # Only allow editing if status is pending_approval
        if self.object.status != TransferToLine.Status.PENDING_APPROVAL:
            messages.error(self.request, _('Only pending approval transfers can be edited.'))
            return HttpResponseRedirect(self.get_success_url())
        
        # Set edited_by
        form.instance.edited_by = self.request.user
        
        # Save transfer header and formset using parent's form_valid
        # Note: formset will be filtered to only extra items in get_context_data
        response = super().form_valid(form)
        
        # Filter formset to only save extra items
        formset = self.formset_class(
            self.request.POST,
            instance=self.object,
            prefix=self.formset_prefix,
            **self.get_formset_kwargs()
        )
        formset.queryset = formset.queryset.filter(is_extra=1)
        
        if formset.is_valid():
            formset.save()
        else:
            # Formset validation failed - but we already saved the main object
            # This shouldn't happen, but handle it gracefully
            messages.warning(self.request, _('Some items could not be saved. Please check the form.'))
        
        return response


class TransferToLineDetailView(BaseDetailView):
    """Detail view for viewing transfer to line requests (read-only)."""
    model = TransferToLine
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'production.transfer_requests'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'order',
            'order__bom',
            'order__finished_item',
            'approved_by',
            'qc_approved_by',
            'created_by',
            'edited_by',
        ).prefetch_related(
            'items__material_item',
            'items__source_warehouse',
            'items__destination_work_center',
        )
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Transfer Request')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        transfer = self.object
        
        context['detail_title'] = self.get_page_title()
        info_banner = [
            {'label': _('Transfer Code'), 'value': transfer.transfer_code, 'type': 'code'},
            {'label': _('Transfer Date'), 'value': transfer.transfer_date},
            {'label': _('Status'), 'value': transfer.get_status_display()},
        ]
        if transfer.qc_status:
            info_banner.append({
                'label': _('QC Status'),
                'value': transfer.get_qc_status_display(),
            })
        context['info_banner'] = info_banner
        
        # Request Information section
        request_fields = []
        if transfer.order:
            order_value = transfer.order.order_code
            if transfer.order.finished_item:
                order_value += f" ({transfer.order.finished_item.name})"
            request_fields.append({
                'label': _('Product Order'),
                'value': order_value,
            })
        if transfer.approved_by:
            request_fields.append({
                'label': _('Approved By'),
                'value': transfer.approved_by.get_full_name() or transfer.approved_by.username,
            })
        if transfer.notes:
            request_fields.append({
                'label': _('Notes'),
                'value': transfer.notes,
            })
        
        detail_sections = [
            {
                'title': _('Request Information'),
                'fields': request_fields,
            },
        ]
        
        # Transfer Items section (table)
        if transfer.items.exists():
            headers = [
                _('Material Item'),
                _('Quantity Required'),
                _('Unit'),
                _('Source Warehouse'),
                _('Scrap Allowance'),
                _('Extra'),
            ]
            data = []
            for item in transfer.items.all():
                data.append([
                    f"{item.material_item.name} ({item.material_item.item_code})",
                    f"{item.quantity_required:.2f}",
                    item.unit,
                    item.source_warehouse.name if item.source_warehouse else "—",
                    f"{item.material_scrap_allowance:.2f}%",
                    _('Yes') if item.is_extra else _('No'),
                ])
            
            detail_sections.append({
                'title': _('Transfer Items'),
                'type': 'table',
                'headers': headers,
                'data': data,
            })
        
        # Notes section
        if transfer.notes:
            detail_sections.append({
                'title': _('Notes'),
                'fields': [
                    {'label': _('Notes'), 'value': transfer.notes},
                ],
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:transfer_requests')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:transfer_request_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class TransferToLineDeleteView(BaseDeleteView):
    """Delete a transfer to line request."""
    model = TransferToLine
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Transfer request deleted successfully.')
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('order')
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Check if locked before deletion."""
        self.object = self.get_object()
        
        if self.object.is_locked == 1:
            messages.error(request, _('This transfer request is locked and cannot be deleted.'))
            return HttpResponseRedirect(self.get_success_url())
        
        return super().delete(request, *args, **kwargs)
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Transfer Request')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this transfer request? This action cannot be undone.')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        from production.utils.jalali import gregorian_to_jalali
        
        details = [
            {'label': _('Transfer Code'), 'value': self.object.transfer_code},
            {'label': _('Product Order'), 'value': self.object.order_code},
        ]
        
        if self.object.transfer_date:
            try:
                jalali_date = gregorian_to_jalali(
                    self.object.transfer_date.year,
                    self.object.transfer_date.month,
                    self.object.transfer_date.day
                )
                date_str = f"{jalali_date[0]}/{jalali_date[1]:02d}/{jalali_date[2]:02d}"
            except:
                date_str = str(self.object.transfer_date)
            details.append({'label': _('Transfer Date'), 'value': date_str})
        
        details.extend([
            {'label': _('Status'), 'value': self.object.get_status_display()},
            {'label': _('Total Items'), 'value': str(self.object.items.count())},
        ])
        
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': reverse_lazy('production:transfer_requests')},
            {'label': _('Delete'), 'url': None},
        ]


class TransferToLineApproveView(FeaturePermissionRequiredMixin, View):
    """Approve a transfer to line request."""
    feature_code = 'production.transfer_requests'
    required_action = 'approve'
    
    def post(self, request, *args, **kwargs):
        """Approve the transfer request."""
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        try:
            transfer = TransferToLine.objects.get(
                id=transfer_id,
                company_id=active_company_id,
            )
        except TransferToLine.DoesNotExist:
            return JsonResponse({'error': _('Transfer request not found.')}, status=404)
        
        # Check if user is the approver
        if transfer.approved_by != request.user:
            return JsonResponse({'error': _('You are not authorized to approve this transfer request.')}, status=403)
        
        # Check if already approved or rejected
        if transfer.status == TransferToLine.Status.APPROVED:
            return JsonResponse({'error': _('This transfer request is already approved.')}, status=400)
        
        if transfer.status == TransferToLine.Status.REJECTED:
            return JsonResponse({'error': _('This transfer request is already rejected.')}, status=400)
        
        # Approve - workflow depends on scrap replacement flag
        with transaction.atomic():
            # Check if this is a scrap replacement that requires QC approval
            if transfer.is_scrap_replacement == 1:
                # Set status to pending QC approval
                transfer.status = TransferToLine.Status.PENDING_QC_APPROVAL
                transfer.qc_status = TransferToLine.QCStatus.PENDING_APPROVAL
                transfer.save()
                
                messages.success(
                    request,
                    _('Transfer request approved. Waiting for QC approval.')
                )
            else:
                # Regular approval - lock and create consumption issue
                transfer.status = TransferToLine.Status.APPROVED
                transfer.is_locked = 1
                transfer.locked_at = timezone.now()
                transfer.locked_by = request.user
                transfer.save()
                
                # Create consumption issue document
                try:
                    from inventory.models import IssueConsumption, IssueConsumptionLine
                    
                    # Create IssueConsumption header
                    consumption_issue = IssueConsumption.objects.create(
                        company_id=active_company_id,
                        document_code=generate_document_code(IssueConsumption, active_company_id, "ISU"),
                        document_date=transfer.transfer_date,
                        created_by=request.user,
                        edited_by=request.user,
                    )
                    
                    # Create IssueConsumptionLine for each TransferToLineItem
                    transfer_items = transfer.items.filter(is_enabled=1).order_by('id')
                    for idx, transfer_item in enumerate(transfer_items, start=1):
                        # Get work_line from destination_work_center (now points to WorkLine)
                        work_line = transfer_item.destination_work_center
                        work_line_code = work_line.public_code if work_line else ''
                        
                        IssueConsumptionLine.objects.create(
                            company_id=active_company_id,
                            document=consumption_issue,
                            item=transfer_item.material_item,
                            item_code=transfer_item.material_item_code,
                            warehouse=transfer_item.source_warehouse,
                            warehouse_code=transfer_item.source_warehouse_code,
                            unit=transfer_item.unit,
                            quantity=transfer_item.quantity_required,  # Use quantity_required
                            consumption_type='production_transfer',
                            production_transfer_id=transfer.id,
                            production_transfer_code=transfer.transfer_code,
                            work_line=work_line,
                            work_line_code=work_line_code,
                            sort_order=idx,
                            is_enabled=1,
                        )
                    
                    messages.success(
                        request,
                        _('Transfer request approved and consumption issue %(code)s created successfully.')
                        % {'code': consumption_issue.document_code}
                    )
                except Exception as e:
                    # Log error but don't fail the approval
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Error creating consumption issue for transfer {transfer.transfer_code}: {e}')
                    messages.warning(
                        request,
                        _('Transfer request approved, but failed to create consumption issue: %(error)s')
                        % {'error': str(e)}
                    )
                
                # Create warehouse transfer document (Section 2 & 4)
                try:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f'Attempting to create warehouse transfer for transfer {transfer.transfer_code}')
                    
                    from production.utils.transfer import create_warehouse_transfer_for_transfer_to_line
                    
                    warehouse_transfer, error_msg = create_warehouse_transfer_for_transfer_to_line(
                        transfer=transfer,
                        user=request.user,
                    )
                    
                    if warehouse_transfer:
                        logger.info(f'Warehouse transfer {warehouse_transfer.document_code} created successfully for transfer {transfer.transfer_code}')
                        # Store warehouse transfer info for JSON response
                        transfer._warehouse_transfer_created = warehouse_transfer
                        messages.success(
                            request,
                            _('Warehouse transfer %(code)s created successfully.')
                            % {'code': warehouse_transfer.document_code}
                        )
                    elif error_msg:
                        logger.warning(f'Failed to create warehouse transfer for transfer {transfer.transfer_code}: {error_msg}')
                        messages.warning(
                            request,
                            _('Failed to create warehouse transfer: %(error)s')
                            % {'error': error_msg}
                        )
                    else:
                        logger.warning(f'No warehouse transfer created and no error message for transfer {transfer.transfer_code}')
                        messages.warning(
                            request,
                            _('Warehouse transfer was not created. Please check the logs for details.')
                        )
                except Exception as e:
                    # Log error but don't fail the approval
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Error creating warehouse transfer for transfer {transfer.transfer_code}: {e}', exc_info=True)
                    messages.warning(
                        request,
                        _('Transfer request approved, but failed to create warehouse transfer: %(error)s')
                        % {'error': str(e)}
                    )
        
        # Collect warehouse transfer info if created
        warehouse_transfer_info = None
        if hasattr(transfer, '_warehouse_transfer_created'):
            warehouse_transfer_info = {
                'document_code': transfer._warehouse_transfer_created.document_code,
                'id': transfer._warehouse_transfer_created.id,
            }
        
        response_data = {
            'success': True,
            'message': _('Transfer request approved successfully.'),
        }
        if warehouse_transfer_info:
            response_data['warehouse_transfer'] = warehouse_transfer_info
        
        return JsonResponse(response_data)


class TransferToLineRejectView(FeaturePermissionRequiredMixin, View):
    """Reject a transfer to line request."""
    feature_code = 'production.transfer_requests'
    required_action = 'reject'
    
    def post(self, request, *args, **kwargs):
        """Reject the transfer request."""
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        try:
            transfer = TransferToLine.objects.get(
                id=transfer_id,
                company_id=active_company_id,
            )
        except TransferToLine.DoesNotExist:
            return JsonResponse({'error': _('Transfer request not found.')}, status=404)
        
        # Check if user is the approver
        if transfer.approved_by != request.user:
            return JsonResponse({'error': _('You are not authorized to reject this transfer request.')}, status=403)
        
        # Check if already approved or rejected
        if transfer.status == TransferToLine.Status.APPROVED:
            return JsonResponse({'error': _('This transfer request is already approved.')}, status=400)
        
        if transfer.status == TransferToLine.Status.REJECTED:
            return JsonResponse({'error': _('This transfer request is already rejected.')}, status=400)
        
        # Reject
        with transaction.atomic():
            transfer.status = TransferToLine.Status.REJECTED
            transfer.save()
        
        messages.success(request, _('Transfer request rejected successfully.'))
        return JsonResponse({'success': True, 'message': _('Transfer request rejected successfully.')})


class TransferToLineQCApproveView(FeaturePermissionRequiredMixin, View):
    """Approve QC for a transfer to line request (scrap replacement only)."""
    feature_code = 'production.transfer_requests.qc_approval'
    required_action = 'approve'
    
    def post(self, request, *args, **kwargs):
        """Approve QC for the transfer request."""
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        try:
            transfer = TransferToLine.objects.get(
                id=transfer_id,
                company_id=active_company_id,
            )
        except TransferToLine.DoesNotExist:
            return JsonResponse({'error': _('Transfer request not found.')}, status=404)
        
        # Check if this is a scrap replacement
        if transfer.is_scrap_replacement != 1:
            return JsonResponse({'error': _('QC approval is only required for scrap replacement transfers.')}, status=400)
        
        # Check if user is the QC approver
        if transfer.qc_approved_by != request.user:
            return JsonResponse({'error': _('You are not authorized to approve QC for this transfer request.')}, status=403)
        
        # Check if already QC approved or rejected
        if transfer.qc_status == TransferToLine.QCStatus.APPROVED:
            return JsonResponse({'error': _('QC approval for this transfer request has already been granted.')}, status=400)
        
        if transfer.qc_status == TransferToLine.QCStatus.REJECTED:
            return JsonResponse({'error': _('QC approval for this transfer request has already been rejected.')}, status=400)
        
        # Check if status is pending QC approval
        if transfer.status != TransferToLine.Status.PENDING_QC_APPROVAL:
            return JsonResponse({'error': _('Transfer request is not in pending QC approval status.')}, status=400)
        
        # Approve QC, lock, and create consumption issue
        with transaction.atomic():
            transfer.qc_status = TransferToLine.QCStatus.APPROVED
            transfer.status = TransferToLine.Status.APPROVED
            transfer.is_locked = 1
            transfer.locked_at = timezone.now()
            transfer.locked_by = request.user
            transfer.save()
            
            # Create consumption issue document
            try:
                from inventory.models import IssueConsumption, IssueConsumptionLine
                
                # Create IssueConsumption header
                consumption_issue = IssueConsumption.objects.create(
                    company_id=active_company_id,
                    document_code=generate_document_code(IssueConsumption, active_company_id, "ISU"),
                    document_date=transfer.transfer_date,
                    created_by=request.user,
                    edited_by=request.user,
                )
                
                # Create IssueConsumptionLine for each TransferToLineItem
                transfer_items = transfer.items.filter(is_enabled=1).order_by('id')
                for idx, transfer_item in enumerate(transfer_items, start=1):
                    # Get work_line from destination_work_center (now points to WorkLine)
                    work_line = transfer_item.destination_work_center
                    work_line_code = work_line.public_code if work_line else ''
                    
                    IssueConsumptionLine.objects.create(
                        company_id=active_company_id,
                        document=consumption_issue,
                        item=transfer_item.material_item,
                        item_code=transfer_item.material_item_code,
                        warehouse=transfer_item.source_warehouse,
                        warehouse_code=transfer_item.source_warehouse_code,
                        unit=transfer_item.unit,
                        quantity=transfer_item.quantity_required,
                        consumption_type='production_transfer',
                        production_transfer_id=transfer.id,
                        production_transfer_code=transfer.transfer_code,
                        work_line=work_line,
                        work_line_code=work_line_code,
                        sort_order=idx,
                        is_enabled=1,
                    )
                
                messages.success(
                    request,
                    _('QC approval granted. Transfer request approved and consumption issue %(code)s created successfully.')
                    % {'code': consumption_issue.document_code}
                )
            except Exception as e:
                # Log error but don't fail the approval
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error creating consumption issue for transfer {transfer.transfer_code}: {e}')
                messages.warning(
                    request,
                    _('QC approval granted, but failed to create consumption issue: %(error)s')
                    % {'error': str(e)}
                )
            
            # Create warehouse transfer document (Section 2 & 4)
            try:
                from production.utils.transfer import create_warehouse_transfer_for_transfer_to_line
                
                warehouse_transfer, error_msg = create_warehouse_transfer_for_transfer_to_line(
                    transfer=transfer,
                    user=request.user,
                )
                
                if warehouse_transfer:
                    messages.success(
                        request,
                        _('Warehouse transfer %(code)s created successfully.')
                        % {'code': warehouse_transfer.document_code}
                    )
                elif error_msg:
                    messages.warning(
                        request,
                        _('Failed to create warehouse transfer: %(error)s')
                        % {'error': error_msg}
                    )
            except Exception as e:
                # Log error but don't fail the approval
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error creating warehouse transfer for transfer {transfer.transfer_code}: {e}')
                messages.warning(
                    request,
                    _('QC approval granted, but failed to create warehouse transfer: %(error)s')
                    % {'error': str(e)}
                )
        
        return JsonResponse({'success': True, 'message': _('QC approval granted successfully.')})


class TransferToLineQCRejectView(FeaturePermissionRequiredMixin, View):
    """Reject QC for a transfer to line request (scrap replacement only)."""
    feature_code = 'production.transfer_requests.qc_approval'
    required_action = 'reject'
    
    def post(self, request, *args, **kwargs):
        """Reject QC for the transfer request."""
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        try:
            transfer = TransferToLine.objects.get(
                id=transfer_id,
                company_id=active_company_id,
            )
        except TransferToLine.DoesNotExist:
            return JsonResponse({'error': _('Transfer request not found.')}, status=404)
        
        # Check if this is a scrap replacement
        if transfer.is_scrap_replacement != 1:
            return JsonResponse({'error': _('QC approval is only required for scrap replacement transfers.')}, status=400)
        
        # Check if user is the QC approver
        if transfer.qc_approved_by != request.user:
            return JsonResponse({'error': _('You are not authorized to reject QC for this transfer request.')}, status=403)
        
        # Check if already QC approved or rejected
        if transfer.qc_status == TransferToLine.QCStatus.APPROVED:
            return JsonResponse({'error': _('QC approval for this transfer request has already been granted.')}, status=400)
        
        if transfer.qc_status == TransferToLine.QCStatus.REJECTED:
            return JsonResponse({'error': _('QC approval for this transfer request has already been rejected.')}, status=400)
        
        # Reject QC
        with transaction.atomic():
            transfer.qc_status = TransferToLine.QCStatus.REJECTED
            transfer.status = TransferToLine.Status.REJECTED
            transfer.save()
        
        messages.success(request, _('QC approval rejected successfully.'))
        return JsonResponse({'success': True, 'message': _('QC approval rejected successfully.')})


class TransferToLineCreateWarehouseTransferView(FeaturePermissionRequiredMixin, View):
    """Create warehouse transfer manually for a transfer to line request."""
    feature_code = 'production.transfer_requests'
    required_action = 'approve'
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to return JSON response for permission errors."""
        from django.core.exceptions import PermissionDenied
        
        if not self.has_feature_permission():
            return JsonResponse({
                'error': _('You do not have permission to perform this action.')
            }, status=403)
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Create warehouse transfer for the transfer request."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("=" * 80)
        logger.info("TransferToLineCreateWarehouseTransferView: Request received")
        logger.info(f"  User: {request.user.username}")
        logger.info(f"  Method: {request.method}")
        logger.info(f"  Transfer ID: {kwargs.get('pk')}")
        
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            logger.error("TransferToLineCreateWarehouseTransferView: No active company")
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        logger.info(f"TransferToLineCreateWarehouseTransferView: Company ID: {active_company_id}")
        
        try:
            transfer = TransferToLine.objects.get(
                id=transfer_id,
                company_id=active_company_id,
            )
            logger.info(f"TransferToLineCreateWarehouseTransferView: Transfer found: {transfer.transfer_code}")
        except TransferToLine.DoesNotExist:
            logger.error(f"TransferToLineCreateWarehouseTransferView: Transfer {transfer_id} not found")
            return JsonResponse({'error': _('Transfer request not found.')}, status=404)
        
        # Check if transfer is approved
        if transfer.status != TransferToLine.Status.APPROVED:
            logger.warning(f"TransferToLineCreateWarehouseTransferView: Transfer {transfer.transfer_code} status is {transfer.status}, not APPROVED")
            return JsonResponse({'error': _('Transfer request must be approved before creating warehouse transfer.')}, status=400)
        
        # Check if warehouse transfer already exists (only active ones)
        existing_wt = transfer.warehouse_transfers.filter(is_enabled=1).first()
        if existing_wt:
            logger.warning(f"TransferToLineCreateWarehouseTransferView: Warehouse transfer already exists: {existing_wt.document_code}")
            return JsonResponse({
                'error': _('Warehouse transfer already exists: %(code)s') % {'code': existing_wt.document_code},
                'warehouse_transfer_code': existing_wt.document_code,
                'warehouse_transfer_url': reverse('inventory:issue_warehouse_transfer_detail', kwargs={'pk': existing_wt.pk}),
            }, status=400)
        
        # Create warehouse transfer
        try:
            from production.utils.transfer import create_warehouse_transfer_for_transfer_to_line
            
            logger.info(f"TransferToLineCreateWarehouseTransferView: Calling create_warehouse_transfer_for_transfer_to_line")
            warehouse_transfer, error_msg = create_warehouse_transfer_for_transfer_to_line(
                transfer=transfer,
                user=request.user,
            )
            
            if warehouse_transfer:
                logger.info(f"TransferToLineCreateWarehouseTransferView: Warehouse transfer created successfully: {warehouse_transfer.document_code}")
                messages.success(
                    request,
                    _('Warehouse transfer %(code)s created successfully.')
                    % {'code': warehouse_transfer.document_code}
                )
                response_data = {
                    'success': True,
                    'message': _('Warehouse transfer created successfully.'),
                    'warehouse_transfer_code': warehouse_transfer.document_code,
                    'warehouse_transfer_url': reverse('inventory:issue_warehouse_transfer_detail', kwargs={'pk': warehouse_transfer.pk}),
                }
                logger.info(f"TransferToLineCreateWarehouseTransferView: Returning success response: {response_data}")
                logger.info("=" * 80)
                return JsonResponse(response_data)
            elif error_msg:
                logger.error(f"TransferToLineCreateWarehouseTransferView: Error creating warehouse transfer: {error_msg}")
                error_response = {
                    'error': _('Failed to create warehouse transfer: %(error)s') % {'error': error_msg}
                }
                logger.info(f"TransferToLineCreateWarehouseTransferView: Returning error response: {error_response}")
                logger.info("=" * 80)
                return JsonResponse(error_response, status=400)
            else:
                logger.error("TransferToLineCreateWarehouseTransferView: Warehouse transfer was not created and no error message")
                error_response = {
                    'error': _('Warehouse transfer was not created. Please check the logs for details.')
                }
                logger.info(f"TransferToLineCreateWarehouseTransferView: Returning error response: {error_response}")
                logger.info("=" * 80)
                return JsonResponse(error_response, status=400)
        except Exception as e:
            logger.error(f'TransferToLineCreateWarehouseTransferView: Exception creating warehouse transfer for transfer {transfer.transfer_code}: {e}', exc_info=True)
            error_response = {
                'error': _('Error creating warehouse transfer: %(error)s') % {'error': str(e)}
            }
            logger.info(f"TransferToLineCreateWarehouseTransferView: Returning exception response: {error_response}")
            logger.info("=" * 80)
            return JsonResponse(error_response, status=500)


class TransferToLineUnlockView(FeaturePermissionRequiredMixin, View):
    """Unlock a transfer to line request."""
    feature_code = 'production.transfer_requests'
    required_action = 'unlock'
    
    def post(self, request, *args, **kwargs):
        """Unlock the transfer request."""
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        try:
            transfer = TransferToLine.objects.get(
                id=transfer_id,
                company_id=active_company_id,
            )
        except TransferToLine.DoesNotExist:
            return JsonResponse({'error': _('Transfer request not found.')}, status=404)
        
        # Check if transfer is locked
        if transfer.is_locked != 1:
            return JsonResponse({'error': _('Transfer request is not locked.')}, status=400)
        
        # Unlock transfer
        with transaction.atomic():
            transfer.is_locked = 0
            transfer.unlocked_at = timezone.now()
            transfer.unlocked_by = request.user
            transfer.save()
        
        messages.success(request, _('Transfer request unlocked successfully.'))
        return JsonResponse({'success': True, 'message': _('Transfer request unlocked successfully.')})


class CreatePurchaseRequestFromTransferRequestView(FeaturePermissionRequiredMixin, View):
    """View to select items from transfer request to create purchase request."""
    feature_code = 'production.transfer_requests'
    required_action = 'view_own'
    
    def get(self, request, *args, **kwargs):
        """Display form to select items from transfer request."""
        
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            messages.error(request, _('Please select a company first.'))
            return HttpResponseRedirect(reverse('production:transfer_requests'))
        
        transfer = get_object_or_404(
            TransferToLine,
            id=transfer_id,
            company_id=active_company_id,
            is_enabled=1
        )
        
        # Check if transfer is approved and locked
        if transfer.status != TransferToLine.Status.APPROVED or transfer.is_locked != 1:
            messages.error(request, _('Transfer request must be approved and locked before creating purchase request.'))
            return HttpResponseRedirect(reverse('production:transfer_requests'))
        
        # Get transfer items
        items = transfer.items.filter(is_enabled=1).order_by('material_item_code')
        
        context = {
            'transfer': transfer,
            'items': items,
        }
        
        return render(request, 'production/create_purchase_request_from_transfer_request.html', context)
    
    def post(self, request, *args, **kwargs):
        """Process selected items and redirect to purchase request creation."""
        from decimal import InvalidOperation
        
        transfer_id = kwargs.get('pk')
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            messages.error(request, _('Please select a company first.'))
            return HttpResponseRedirect(reverse('production:transfer_requests'))
        
        transfer = get_object_or_404(
            TransferToLine,
            id=transfer_id,
            company_id=active_company_id,
            is_enabled=1
        )
        
        # Check if transfer is approved and locked
        if transfer.status != TransferToLine.Status.APPROVED or transfer.is_locked != 1:
            messages.error(request, _('Transfer request must be approved and locked before creating purchase request.'))
            return HttpResponseRedirect(reverse('production:transfer_requests'))
        
        # Process selected items
        selected_items = []
        for item in transfer.items.filter(is_enabled=1):
            item_id = str(item.pk)
            quantity_key = f'quantity_{item_id}'
            selected_key = f'selected_{item_id}'
            
            if request.POST.get(selected_key) == 'on':
                quantity = request.POST.get(quantity_key, '0')
                try:
                    quantity = Decimal(str(quantity))
                    if quantity > 0:
                        # Use quantity_required as max
                        if quantity > item.quantity_required:
                            quantity = item.quantity_required
                        selected_items.append({
                            'item': item.material_item,
                            'item_code': item.material_item_code,
                            'quantity': quantity,
                            'unit': item.unit,
                            'notes': request.POST.get(f'notes_{item_id}', '').strip(),
                        })
                except (ValueError, InvalidOperation):
                    pass
        
        if not selected_items:
            messages.error(request, _('Please select at least one item.'))
            return HttpResponseRedirect(reverse('production:transfer_request_create_purchase_request', kwargs={'pk': transfer_id}))
        
        # Store in session
        session_key = f'transfer_request_{transfer_id}_purchase_request_lines'
        session_data = [
            {
                'item_id': item['item'].id,
                'item_code': item['item_code'],
                'quantity': str(item['quantity']),
                'unit': item['unit'],
                'notes': item['notes'],
            }
            for item in selected_items
        ]
        request.session[session_key] = session_data
        request.session[f'transfer_request_{transfer_id}_purchase_request_reference'] = {
            'transfer_code': transfer.transfer_code,
            'transfer_id': transfer.id,
        }
        
        # Redirect to purchase request creation
        return HttpResponseRedirect(reverse('inventory:purchase_request_create_from_transfer_request', kwargs={'transfer_id': transfer_id}))


"""
Transfer to Line Request CRUD views for production module.
"""
from decimal import Decimal
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views import View

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from inventory.utils.codes import generate_sequential_code
from inventory.forms.base import generate_document_code
from production.forms import TransferToLineForm, TransferToLineItemFormSet
from production.models import TransferToLine, TransferToLineItem, ProductOrder


class TransferToLineListView(FeaturePermissionRequiredMixin, ListView):
    """List all transfer to line requests for the active company."""
    model = TransferToLine
    template_name = 'production/transfer_to_line_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.transfer_requests'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter transfers by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return TransferToLine.objects.none()
        
        queryset = TransferToLine.objects.filter(
            company_id=active_company_id
        ).select_related(
            'order',
            'order__bom',
            'order__finished_item',
            'approved_by',
        ).prefetch_related(
            'items',
        ).order_by('-transfer_date', 'transfer_code')
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Transfer to Line Requests')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('production:transfer_request_create')
        context['create_button_text'] = _('Create Transfer Request +')
        context['show_filters'] = False
        context['show_actions'] = True
        context['feature_code'] = 'production.transfer_requests'
        context['detail_url_name'] = 'production:transfer_request_detail'
        context['edit_url_name'] = 'production:transfer_request_edit'
        context['delete_url_name'] = 'production:transfer_request_delete'
        context['empty_state_title'] = _('No Transfer Requests Found')
        context['empty_state_message'] = _('Create your first transfer request to get started.')
        context['empty_state_icon'] = '📦'
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            from shared.utils.permissions import get_user_feature_permissions
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
        return context


class TransferToLineCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new transfer to line request."""
    model = TransferToLine
    form_class = TransferToLineForm
    template_name = 'production/transfer_to_line_form.html'
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formset and context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Transfer Request')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': reverse_lazy('production:transfer_requests')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:transfer_requests')
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
        """Save transfer and create items from BOM."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        # Set company and created_by
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        form.instance.status = TransferToLine.Status.PENDING_APPROVAL
        
        # Generate transfer code
        if not form.instance.transfer_code:
            form.instance.transfer_code = generate_sequential_code(
                TransferToLine,
                company_id=active_company_id,
                field='transfer_code',
                prefix='TR',
                width=8,
            )
        
        # Save transfer header
        response = super().form_valid(form)
        
        # Get formset
        formset = TransferToLineItemFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': active_company_id}
        )
        
        if formset.is_valid():
            # Save extra items (is_extra=1)
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    item = item_form.save(commit=False)
                    item.transfer = self.object
                    item.company_id = active_company_id
                    item.is_extra = 1  # Mark as extra request
                    item.created_by = self.request.user
                    item.save()
        
        # Create items based on transfer type
        order = form.instance.order
        transfer_type = form.cleaned_data.get('transfer_type', 'full')
        selected_operations = form.cleaned_data.get('selected_operations', [])
        
        if order and order.bom:
            from inventory.models import ItemWarehouse
            from production.utils.transfer import get_operation_materials
            from production.models import ProcessOperation
            
            quantity_planned = order.quantity_planned
            
            # Collect materials to transfer
            materials_to_transfer = []  # List of (material_item, quantity, unit, scrap_allowance)
            
            if transfer_type == 'full':
                # Transfer all BOM materials
                bom = order.bom
                bom_materials = bom.materials.filter(is_enabled=1).select_related('material_item')
                
                for bom_material in bom_materials:
                    quantity_required = quantity_planned * bom_material.quantity_per_unit
                    materials_to_transfer.append((
                        bom_material.material_item,
                        quantity_required,
                        bom_material.unit,
                        bom_material.scrap_allowance,
                    ))
            
            elif transfer_type == 'operations' and selected_operations:
                # Transfer materials from selected operations
                operation_ids = [int(op_id) for op_id in selected_operations]
                operations = ProcessOperation.objects.filter(
                    id__in=operation_ids,
                    is_enabled=1,
                ).select_related('process')
                
                for operation in operations:
                    operation_materials = get_operation_materials(operation, order)
                    
                    for op_material in operation_materials:
                        # Calculate quantity: quantity_planned × quantity_used (from ProcessOperationMaterial)
                        quantity_required = quantity_planned * op_material.quantity_used
                        
                        # Get scrap allowance from BOM material if available
                        scrap_allowance = Decimal('0.00')
                        if op_material.bom_material:
                            scrap_allowance = op_material.bom_material.scrap_allowance
                        
                        materials_to_transfer.append((
                            op_material.material_item,
                            quantity_required,
                            op_material.unit,
                            scrap_allowance,
                        ))
            
            # Create transfer items
            for material_item, quantity_required, unit, scrap_allowance in materials_to_transfer:
                # Get source warehouse from ItemWarehouse (first allowed warehouse)
                item_warehouse = ItemWarehouse.objects.filter(
                    item=material_item,
                    company_id=active_company_id,
                    is_enabled=1,
                ).select_related('warehouse').first()
                
                if not item_warehouse:
                    messages.warning(
                        self.request,
                        _('No allowed warehouse found for item {item_code}. Please configure ItemWarehouse first.').format(
                            item_code=material_item.item_code
                        )
                    )
                    continue
                
                source_warehouse = item_warehouse.warehouse
                
                # Get destination work center from order's process if available
                destination_work_center = None
                if order.process:
                    # Get first work line from process
                    work_lines = order.process.work_lines.filter(is_enabled=1).first()
                    if work_lines:
                        # Get work center from work line (if available)
                        # Note: WorkLine doesn't have work_center, so we'll leave it None for now
                        pass
                
                # Create transfer item
                TransferToLineItem.objects.create(
                    transfer=self.object,
                    company_id=active_company_id,
                    material_item=material_item,
                    material_item_code=material_item.item_code,
                    quantity_required=quantity_required,
                    unit=unit,
                    source_warehouse=source_warehouse,
                    source_warehouse_code=source_warehouse.public_code,
                    destination_work_center=destination_work_center,
                    material_scrap_allowance=scrap_allowance,
                    is_extra=0,  # From BOM or Operations
                    created_by=self.request.user,
                )
        
        messages.success(self.request, _('Transfer request created successfully.'))
        return response


class TransferToLineUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing transfer to line request (only extra items can be edited)."""
    model = TransferToLine
    form_class = TransferToLineForm
    template_name = 'production/transfer_to_line_form.html'
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formset and context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Transfer Request')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': reverse_lazy('production:transfer_requests')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:transfer_requests')
        context['form_id'] = 'transfer-form'
        
        # Only show extra items (is_extra=1) in formset
        if self.request.POST:
            formset = TransferToLineItemFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        else:
            formset = TransferToLineItemFormSet(
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        
        # Filter formset to only show extra items
        formset.queryset = formset.queryset.filter(is_extra=1)
        
        context['formset'] = formset
        context['bom_items'] = self.object.items.filter(is_extra=0)  # BOM items (read-only)
        context['is_locked'] = self.object.is_locked == 1
        
        return context
    
    @transaction.atomic
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
        
        # Save transfer header
        response = super().form_valid(form)
        
        # Get formset (only extra items)
        formset = TransferToLineItemFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': self.request.session.get('active_company_id')}
        )
        
        # Filter to only extra items
        formset.queryset = formset.queryset.filter(is_extra=1)
        
        if formset.is_valid():
            formset.save()
        
        messages.success(self.request, _('Transfer request updated successfully.'))
        return response


class TransferToLineDetailView(FeaturePermissionRequiredMixin, DetailView):
    """Detail view for viewing transfer to line requests (read-only)."""
    model = TransferToLine
    template_name = 'production/transfer_to_line_detail.html'
    context_object_name = 'transfer'
    feature_code = 'production.transfer_requests'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return TransferToLine.objects.none()
        queryset = TransferToLine.objects.filter(company_id=active_company_id)
        queryset = queryset.select_related(
            'order',
            'order__bom',
            'order__finished_item',
            'approved_by',
            'created_by',
            'edited_by',
        ).prefetch_related(
            'items__material_item',
            'items__source_warehouse',
        )
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('production:transfer_requests')
        context['edit_url'] = reverse_lazy('production:transfer_request_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'production.transfer_requests'
        return context


class TransferToLineDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a transfer to line request."""
    model = TransferToLine
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return TransferToLine.objects.none()
        return TransferToLine.objects.filter(company_id=active_company_id).select_related('order')
    
    def delete(self, request, *args, **kwargs):
        """Check if locked before deletion."""
        self.object = self.get_object()
        
        if self.object.is_locked == 1:
            messages.error(request, _('This transfer request is locked and cannot be deleted.'))
            return HttpResponseRedirect(self.get_success_url())
        
        messages.success(request, _('Transfer request deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Transfer Request')
        context['confirmation_message'] = _('Are you sure you want to delete this transfer request? This action cannot be undone.')
        
        from django.template.defaultfilters import date as date_filter
        from production.utils.jalali import gregorian_to_jalali
        
        object_details = [
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
            object_details.append({'label': _('Transfer Date'), 'value': date_str})
        
        object_details.extend([
            {'label': _('Status'), 'value': self.object.get_status_display()},
            {'label': _('Total Items'), 'value': str(self.object.items.count())},
        ])
        
        context['object_details'] = object_details
        context['cancel_url'] = reverse_lazy('production:transfer_requests')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Transfer to Line Requests'), 'url': reverse_lazy('production:transfer_requests')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


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
                        # Note: destination_work_center is a WorkCenter, not WorkLine
                        # WorkLine is optional and can be set manually later if needed
                        work_line = None
                        work_line_code = ''
                        
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
        
        return JsonResponse({'success': True, 'message': _('Transfer request approved successfully.')})


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
                    work_line = None
                    work_line_code = ''
                    
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


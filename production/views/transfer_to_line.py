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
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views import View

from shared.mixins import FeaturePermissionRequiredMixin
from inventory.utils.codes import generate_sequential_code
from production.forms import TransferToLineForm, TransferToLineItemFormSet
from production.models import TransferToLine, TransferToLineItem, ProductOrder


class TransferToLineListView(FeaturePermissionRequiredMixin, ListView):
    """List all transfer to line requests for the active company."""
    model = TransferToLine
    template_name = 'production/transfer_to_line_list.html'
    context_object_name = 'transfers'
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
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
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
        """Add formset to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Transfer Request')
        
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
        
        # Create items from BOM
        order = form.instance.order
        if order and order.bom:
            bom = order.bom
            quantity_planned = order.quantity_planned
            
            # Get BOM materials
            bom_materials = bom.materials.all().select_related('material_item')
            
            for bom_material in bom_materials:
                # Calculate required quantity: quantity_planned × quantity_per_unit
                quantity_required = quantity_planned * bom_material.quantity_per_unit
                
                # Get source warehouse from ItemWarehouse (first allowed warehouse)
                from inventory.models import ItemWarehouse
                item_warehouse = ItemWarehouse.objects.filter(
                    item=bom_material.material_item,
                    company_id=active_company_id,
                    is_enabled=1,
                ).select_related('warehouse').first()
                
                if not item_warehouse:
                    messages.warning(
                        self.request,
                        _('No allowed warehouse found for item {item_code}. Please configure ItemWarehouse first.').format(
                            item_code=bom_material.material_item.item_code
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
                
                # Create transfer item from BOM
                TransferToLineItem.objects.create(
                    transfer=self.object,
                    company_id=active_company_id,
                    material_item=bom_material.material_item,
                    material_item_code=bom_material.material_item.item_code,
                    quantity_required=quantity_required,
                    unit=bom_material.unit,
                    source_warehouse=source_warehouse,
                    source_warehouse_code=source_warehouse.public_code,
                    destination_work_center=destination_work_center,
                    material_scrap_allowance=bom_material.scrap_allowance,
                    is_extra=0,  # From BOM
                    created_by=self.request.user,
                )
        
        messages.success(self.request, _('Transfer request created successfully.'))
        return response


class TransferToLineUpdateView(FeaturePermissionRequiredMixin, UpdateView):
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
        """Add formset to context (only extra items)."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Transfer Request')
        
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


class TransferToLineDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a transfer to line request."""
    model = TransferToLine
    template_name = 'production/transfer_to_line_confirm_delete.html'
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return TransferToLine.objects.none()
        return TransferToLine.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        """Check if locked before deletion."""
        self.object = self.get_object()
        
        if self.object.is_locked == 1:
            messages.error(request, _('This transfer request is locked and cannot be deleted.'))
            return HttpResponseRedirect(self.get_success_url())
        
        return super().delete(request, *args, **kwargs)


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
        
        # Approve and lock
        with transaction.atomic():
            transfer.status = TransferToLine.Status.APPROVED
            transfer.is_locked = 1
            transfer.locked_at = timezone.now()
            transfer.locked_by = request.user
            transfer.save()
        
        messages.success(request, _('Transfer request approved and locked successfully.'))
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


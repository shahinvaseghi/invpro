"""
Performance Record CRUD views for production module.
"""
from decimal import Decimal
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views import View

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
from inventory.utils.codes import generate_sequential_code
from production.forms import (
    PerformanceRecordForm,
    PerformanceRecordMaterialFormSet,
    PerformanceRecordPersonFormSet,
    PerformanceRecordMachineFormSet,
)
from production.models import (
    PerformanceRecord,
    PerformanceRecordMaterial,
    PerformanceRecordPerson,
    PerformanceRecordMachine,
    ProductOrder,
    TransferToLine,
    TransferToLineItem,
    Process,
)


class PerformanceRecordListView(FeaturePermissionRequiredMixin, ListView):
    """List all performance records for the active company."""
    model = PerformanceRecord
    template_name = 'production/performance_record_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.performance_records'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter performance records by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return PerformanceRecord.objects.none()
        
        queryset = PerformanceRecord.objects.filter(
            company_id=active_company_id
        ).select_related(
            'order',
            'order__bom',
            'order__finished_item',
            'order__process',
            'transfer',
            'approved_by',
        ).prefetch_related(
            'materials',
            'persons',
            'machines',
        ).order_by('-performance_date', 'performance_code')
        
        # Check if user has view_all permission
        permissions = get_user_feature_permissions(self.request.user, active_company_id)
        if not has_feature_permission(permissions, 'production.performance_records', action='view_all'):
            # Only show own records
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic template."""
        context = super().get_context_data(**kwargs)
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            context['object_list'] = list(context['object_list'])
        
        context['page_title'] = _('Performance Records')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': None},
        ]
        
        # Check permissions for create button
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if active_company_id:
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            if has_feature_permission(permissions, 'production.performance_records', action='create') or self.request.user.is_superuser:
                context['create_url'] = reverse_lazy('production:performance_record_create')
                context['create_button_text'] = _('Create Performance Record')
        
        context['show_filters'] = False
        context['show_actions'] = True
        context['edit_url_name'] = 'production:performance_record_edit'
        context['delete_url_name'] = 'production:performance_record_delete'
        context['empty_state_title'] = _('No Performance Records Found')
        context['empty_state_message'] = _('Create your first performance record to get started.')
        context['empty_state_icon'] = '📊'
        
        # Add user_feature_permissions for template
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
        return context


class PerformanceRecordCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new performance record."""
    model = PerformanceRecord
    form_class = PerformanceRecordForm
    template_name = 'production/performance_record_form.html'
    success_url = reverse_lazy('production:performance_records')
    feature_code = 'production.performance_records'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formsets to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Performance Record')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': reverse_lazy('production:performance_records')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:performance_records')
        context['form_id'] = 'performance-form'
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
        # In CreateView, self.object is None initially
        instance = self.object if hasattr(self, 'object') and self.object else None
        
        active_company_id = self.request.session.get('active_company_id')
        
        if self.request.POST:
            context['material_formset'] = PerformanceRecordMaterialFormSet(
                self.request.POST,
                instance=instance,
                form_kwargs={'company_id': active_company_id},
                prefix='materials',
            )
            context['person_formset'] = PerformanceRecordPersonFormSet(
                self.request.POST,
                instance=instance,
                form_kwargs={'company_id': active_company_id, 'process_id': None},  # Will be set from order if available
                prefix='persons',
            )
            context['machine_formset'] = PerformanceRecordMachineFormSet(
                self.request.POST,
                instance=instance,
                form_kwargs={'company_id': active_company_id},
                prefix='machines',
            )
        else:
            context['material_formset'] = PerformanceRecordMaterialFormSet(
                instance=instance,
                form_kwargs={'company_id': active_company_id},
                prefix='materials',
            )
            context['person_formset'] = PerformanceRecordPersonFormSet(
                instance=instance,
                form_kwargs={'company_id': active_company_id, 'process_id': None},  # Will be set from order if available
                prefix='persons',
            )
            context['machine_formset'] = PerformanceRecordMachineFormSet(
                instance=instance,
                form_kwargs={'company_id': active_company_id, 'process_id': None},  # Will be set from order if available
                prefix='machines',
            )
        
        return context
    
    @transaction.atomic
    def form_valid(self, form: PerformanceRecordForm) -> HttpResponseRedirect:
        """Save performance record and related items."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        # Set company and created_by
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        # Generate performance_code if not provided
        if not form.instance.performance_code:
            base_code = generate_sequential_code(
                PerformanceRecord,
                company_id=active_company_id,
                field='performance_code',
                width=8,
            )
            form.instance.performance_code = f"PR-{base_code}"
        
        # Auto-populate from order
        order = form.cleaned_data.get('order')
        if order:
            form.instance.quantity_planned = order.quantity_planned
            form.instance.finished_item = order.finished_item
            form.instance.unit = order.unit
        
        # Save performance record header
        response = super().form_valid(form)
        
        # Get formsets
        material_formset = PerformanceRecordMaterialFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': active_company_id},
            prefix='materials',
        )
        person_formset = PerformanceRecordPersonFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': active_company_id, 'process_id': order.process_id if order else None},
            prefix='persons',
        )
        machine_formset = PerformanceRecordMachineFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': active_company_id, 'process_id': order.process_id if order else None},
            prefix='machines',
        )
        
        # Populate materials from transfer if transfer is selected
        transfer = form.cleaned_data.get('transfer')
        if transfer and material_formset.is_valid():
            # Clear existing materials and populate from transfer
            PerformanceRecordMaterial.objects.filter(performance=self.object).delete()
            
            for transfer_item in transfer.items.all():
                material = PerformanceRecordMaterial.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    material_item=transfer_item.material_item,
                    material_item_code=transfer_item.material_item_code,
                    quantity_required=transfer_item.quantity_required,
                    quantity_waste=Decimal('0'),
                    unit=transfer_item.unit,
                    is_extra=transfer_item.is_extra,
                    created_by=self.request.user,
                )
        elif material_formset.is_valid():
            # Save materials from formset
            material_formset.instance = self.object
            material_formset.save()
        else:
            messages.error(self.request, _('Error saving materials. Please check the form.'))
            return self.form_invalid(form)
        
        # Save persons and machines
        if person_formset.is_valid():
            person_formset.instance = self.object
            person_formset.save()
        else:
            messages.error(self.request, _('Error saving persons. Please check the form.'))
            return self.form_invalid(form)
        
        if machine_formset.is_valid():
            machine_formset.instance = self.object
            machine_formset.save()
        else:
            messages.error(self.request, _('Error saving machines. Please check the form.'))
            return self.form_invalid(form)
        
        messages.success(self.request, _('Performance record created successfully.'))
        return response


class PerformanceRecordUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing performance record."""
    model = PerformanceRecord
    form_class = PerformanceRecordForm
    template_name = 'production/performance_record_form.html'
    success_url = reverse_lazy('production:performance_records')
    feature_code = 'production.performance_records'
    required_action = 'edit_own'
    
    def get_queryset(self):
        """Filter by company and check permissions."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return PerformanceRecord.objects.none()
        
        queryset = PerformanceRecord.objects.filter(company_id=active_company_id)
        
        # Check if user has edit_other permission
        permissions = get_user_feature_permissions(self.request.user, active_company_id)
        if not has_feature_permission(permissions, 'production.performance_records', action='edit_other'):
            # Only allow editing own records
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formsets to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Performance Record')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': reverse_lazy('production:performance_records')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:performance_records')
        context['form_id'] = 'performance-form'
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
        active_company_id = self.request.session.get('active_company_id')
        order = self.object.order
        process_id = order.process_id if order and order.process else None
        
        if self.request.POST:
            context['material_formset'] = PerformanceRecordMaterialFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': active_company_id},
                prefix='materials',
            )
            context['person_formset'] = PerformanceRecordPersonFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': active_company_id, 'process_id': process_id},
                prefix='persons',
            )
            context['machine_formset'] = PerformanceRecordMachineFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': active_company_id, 'process_id': process_id},
                prefix='machines',
            )
        else:
            context['material_formset'] = PerformanceRecordMaterialFormSet(
                instance=self.object,
                form_kwargs={'company_id': active_company_id},
                prefix='materials',
            )
            context['person_formset'] = PerformanceRecordPersonFormSet(
                instance=self.object,
                form_kwargs={'company_id': active_company_id, 'process_id': process_id},
                prefix='persons',
            )
            context['machine_formset'] = PerformanceRecordMachineFormSet(
                instance=self.object,
                form_kwargs={'company_id': active_company_id, 'process_id': process_id},
                prefix='machines',
            )
        
        return context
    
    @transaction.atomic
    def form_valid(self, form: PerformanceRecordForm) -> HttpResponseRedirect:
        """Save performance record and related items."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        # Check if record is locked
        if self.object.is_locked:
            messages.error(self.request, _('This performance record is locked and cannot be edited.'))
            return redirect('production:performance_records')
        
        # Set edited_by
        form.instance.edited_by = self.request.user
        
        # Save performance record header
        response = super().form_valid(form)
        
        # Get formsets
        material_formset = PerformanceRecordMaterialFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': active_company_id},
            prefix='materials',
        )
        person_formset = PerformanceRecordPersonFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': active_company_id, 'process_id': self.object.order.process_id if self.object.order else None},
            prefix='persons',
        )
        machine_formset = PerformanceRecordMachineFormSet(
            self.request.POST,
            instance=self.object,
            form_kwargs={'company_id': active_company_id, 'process_id': self.object.order.process_id if self.object.order else None},
            prefix='machines',
        )
        
        # Save formsets
        if material_formset.is_valid():
            material_formset.save()
        else:
            messages.error(self.request, _('Error saving materials. Please check the form.'))
            return self.form_invalid(form)
        
        if person_formset.is_valid():
            person_formset.save()
        else:
            messages.error(self.request, _('Error saving persons. Please check the form.'))
            return self.form_invalid(form)
        
        if machine_formset.is_valid():
            machine_formset.save()
        else:
            messages.error(self.request, _('Error saving machines. Please check the form.'))
            return self.form_invalid(form)
        
        messages.success(self.request, _('Performance record updated successfully.'))
        return response


class PerformanceRecordDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a performance record."""
    model = PerformanceRecord
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:performance_records')
    feature_code = 'production.performance_records'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by company and check permissions."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return PerformanceRecord.objects.none()
        
        queryset = PerformanceRecord.objects.filter(company_id=active_company_id)
        
        # Check if user has delete_other permission
        permissions = get_user_feature_permissions(self.request.user, active_company_id)
        if not has_feature_permission(permissions, 'production.performance_records', action='delete_other'):
            # Only allow deleting own records
            queryset = queryset.filter(created_by=self.request.user)
        
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Check if record is locked before deletion."""
        self.object = self.get_object()
        
        if self.object.is_locked:
            messages.error(request, _('This performance record is locked and cannot be deleted.'))
            return redirect('production:performance_records')
        
        if self.object.status != 'pending_approval':
            messages.error(request, _('Only pending approval records can be deleted.'))
            return redirect('production:performance_records')
        
        messages.success(request, _('Performance record deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        from production.utils.jalali import gregorian_to_jalali
        
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Performance Record')
        context['confirmation_message'] = _('Are you sure you want to delete this performance record?')
        
        # Format performance date using jalali
        performance_date_jalali = ''
        if self.object.performance_date:
            try:
                jalali = gregorian_to_jalali(
                    self.object.performance_date.year,
                    self.object.performance_date.month,
                    self.object.performance_date.day
                )
                performance_date_jalali = f"{jalali[0]}/{jalali[1]:02d}/{jalali[2]:02d}"
            except:
                performance_date_jalali = str(self.object.performance_date)
        
        context['object_details'] = [
            {'label': _('Performance Code'), 'value': f'<code>{self.object.performance_code}</code>'},
            {'label': _('Product Order'), 'value': self.object.order_code},
            {'label': _('Performance Date'), 'value': performance_date_jalali},
            {'label': _('Status'), 'value': self.object.get_status_display()},
            {'label': _('Planned Quantity'), 'value': f'{self.object.quantity_planned} {self.object.unit}'},
            {'label': _('Actual Quantity'), 'value': f'{self.object.quantity_actual} {self.object.unit}'},
        ]
        
        if self.object.materials.exists() or self.object.persons.exists() or self.object.machines.exists():
            warning_parts = []
            if self.object.materials.exists():
                warning_parts.append(_('{count} material line(s)').format(count=self.object.materials.count()))
            if self.object.persons.exists():
                warning_parts.append(_('{count} person(s)').format(count=self.object.persons.count()))
            if self.object.machines.exists():
                warning_parts.append(_('{count} machine(s)').format(count=self.object.machines.count()))
            
            context['warning_message'] = _('This record has {details}. They will also be deleted.').format(
                details=', '.join(warning_parts)
            )
        
        context['cancel_url'] = reverse_lazy('production:performance_records')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': reverse_lazy('production:performance_records')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


class PerformanceRecordApproveView(FeaturePermissionRequiredMixin, View):
    """Approve a performance record."""
    feature_code = 'production.performance_records'
    required_action = 'approve'
    
    def post(self, request, *args, **kwargs):
        """Approve the performance record."""
        active_company_id = request.session.get('active_company_id')
        if not active_company_id:
            messages.error(request, _('Please select a company first.'))
            return redirect('production:performance_records')
        
        performance_record = get_object_or_404(
            PerformanceRecord,
            pk=kwargs['pk'],
            company_id=active_company_id,
        )
        
        # Check if already approved or rejected
        if performance_record.status != 'pending_approval':
            messages.error(request, _('This performance record has already been processed.'))
            return redirect('production:performance_records')
        
        # Check if locked
        if performance_record.is_locked:
            messages.error(request, _('This performance record is already locked.'))
            return redirect('production:performance_records')
        
        # Approve and lock
        performance_record.status = 'approved'
        performance_record.approved_by = request.user
        performance_record.is_locked = True
        performance_record.locked_at = timezone.now()
        performance_record.locked_by = request.user
        performance_record.save()
        
        messages.success(request, _('Performance record approved and locked successfully.'))
        return redirect('production:performance_records')


class PerformanceRecordRejectView(FeaturePermissionRequiredMixin, View):
    """Reject a performance record."""
    feature_code = 'production.performance_records'
    required_action = 'reject'
    
    def post(self, request, *args, **kwargs):
        """Reject the performance record."""
        active_company_id = request.session.get('active_company_id')
        if not active_company_id:
            messages.error(request, _('Please select a company first.'))
            return redirect('production:performance_records')
        
        performance_record = get_object_or_404(
            PerformanceRecord,
            pk=kwargs['pk'],
            company_id=active_company_id,
        )
        
        # Check if already approved or rejected
        if performance_record.status != 'pending_approval':
            messages.error(request, _('This performance record has already been processed.'))
            return redirect('production:performance_records')
        
        # Reject (but don't lock - can be edited and resubmitted)
        performance_record.status = 'rejected'
        performance_record.approved_by = request.user
        performance_record.save()
        
        messages.success(request, _('Performance record rejected. It can be edited and resubmitted.'))
        return redirect('production:performance_records')


class PerformanceRecordCreateReceiptView(FeaturePermissionRequiredMixin, View):
    """Create a receipt (permanent or temporary) from an approved performance record."""
    feature_code = 'production.performance_records'
    required_action = 'create_receipt'
    
    def post(self, request, *args, **kwargs):
        """Create receipt from performance record."""
        active_company_id = request.session.get('active_company_id')
        if not active_company_id:
            messages.error(request, _('Please select a company first.'))
            return redirect('production:performance_records')
        
        performance_record = get_object_or_404(
            PerformanceRecord,
            pk=kwargs['pk'],
            company_id=active_company_id,
        )
        
        # Check if approved
        if performance_record.status != 'approved':
            messages.error(request, _('Only approved performance records can create receipts.'))
            return redirect('production:performance_records')
        
        # Get receipt type from POST data
        receipt_type = request.POST.get('receipt_type', 'permanent')  # 'permanent' or 'temporary'
        
        # Get finished item
        finished_item = performance_record.finished_item
        quantity = performance_record.quantity_actual
        
        # Check if item requires temporary receipt
        if finished_item.requires_temporary_receipt == 1:
            receipt_type = 'temporary'
        
        # Get warehouse (need to determine - maybe from order or transfer)
        from inventory.models import Warehouse, ReceiptPermanent, ReceiptPermanentLine, ReceiptTemporary
        from inventory.forms.base import generate_document_code
        
        # Try to get warehouse from transfer or use first available warehouse
        warehouse = None
        if performance_record.transfer:
            # Try to get warehouse from transfer items
            transfer_item = performance_record.transfer.items.first()
            if transfer_item and transfer_item.source_warehouse:
                warehouse = transfer_item.source_warehouse
        
        if not warehouse:
            # Get first enabled warehouse for the company
            warehouse = Warehouse.objects.filter(
                company_id=active_company_id,
                is_enabled=1,
            ).first()
        
        if not warehouse:
            messages.error(request, _('No warehouse found. Please create a warehouse first.'))
            return redirect('production:performance_records')
        
        try:
            with transaction.atomic():
                if receipt_type == 'temporary':
                    # Create temporary receipt
                    receipt = ReceiptTemporary.objects.create(
                        company_id=active_company_id,
                        document_code=generate_document_code(ReceiptTemporary, active_company_id, "TMP"),
                        document_date=timezone.now().date(),
                        item=finished_item,
                        item_code=finished_item.item_code,
                        warehouse=warehouse,
                        warehouse_code=warehouse.public_code,
                        unit=performance_record.unit,
                        quantity=quantity,
                        source_document_type='Performance Record',
                        source_document_code=performance_record.performance_code,
                        status=ReceiptTemporary.Status.DRAFT,
                        created_by=request.user,
                    )
                    messages.success(request, _('Temporary receipt created successfully: {code}').format(code=receipt.document_code))
                else:
                    # Create permanent receipt
                    receipt = ReceiptPermanent.objects.create(
                        company_id=active_company_id,
                        document_code=generate_document_code(ReceiptPermanent, active_company_id, "PRM"),
                        document_date=timezone.now().date(),
                        created_by=request.user,
                    )
                    
                    # Create receipt line
                    ReceiptPermanentLine.objects.create(
                        company_id=active_company_id,
                        document=receipt,
                        item=finished_item,
                        item_code=finished_item.item_code,
                        warehouse=warehouse,
                        warehouse_code=warehouse.public_code,
                        unit=performance_record.unit,
                        quantity=quantity,
                        entered_unit=performance_record.unit,
                        entered_quantity=quantity,
                        reference_document_type='Performance Record',
                        reference_document_code=performance_record.performance_code,
                        created_by=request.user,
                    )
                    messages.success(request, _('Permanent receipt created successfully: {code}').format(code=receipt.document_code))
                
                # Redirect to receipt detail page
                if receipt_type == 'temporary':
                    return redirect('inventory:receipt_temporary_detail', pk=receipt.pk)
                else:
                    return redirect('inventory:receipt_permanent_detail', pk=receipt.pk)
        
        except Exception as e:
            messages.error(request, _('Error creating receipt: {error}').format(error=str(e)))
            return redirect('production:performance_records')


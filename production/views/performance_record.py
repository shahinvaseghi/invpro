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
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
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
    ProcessOperation,
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
        context['feature_code'] = 'production.performance_records'
        context['detail_url_name'] = 'production:performance_record_detail'
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
        
        # Get document_type from form data or default
        document_type = None
        if self.request.POST:
            document_type = self.request.POST.get('document_type', PerformanceRecord.DocumentType.OPERATIONAL)
        elif hasattr(self, 'form') and self.form and hasattr(self.form, 'cleaned_data') and self.form.cleaned_data.get('document_type'):
            document_type = self.form.cleaned_data.get('document_type')
        else:
            document_type = PerformanceRecord.DocumentType.OPERATIONAL
        
        context['document_type'] = document_type
        context['is_general_document'] = (document_type == PerformanceRecord.DocumentType.GENERAL)
        
        if self.request.POST:
            context['material_formset'] = PerformanceRecordMaterialFormSet(
                self.request.POST,
                instance=instance,
                form_kwargs={'company_id': active_company_id},
                prefix='materials',
            )
            # For general documents, disable person and machine formsets (they will be auto-populated)
            if document_type == PerformanceRecord.DocumentType.GENERAL:
                context['person_formset'] = PerformanceRecordPersonFormSet(
                    self.request.POST,
                    instance=instance,
                    form_kwargs={'company_id': active_company_id, 'process_id': None},
                    prefix='persons',
                )
                context['machine_formset'] = PerformanceRecordMachineFormSet(
                    self.request.POST,
                    instance=instance,
                    form_kwargs={'company_id': active_company_id},
                    prefix='machines',
                )
            else:
                context['person_formset'] = PerformanceRecordPersonFormSet(
                    self.request.POST,
                    instance=instance,
                    form_kwargs={'company_id': active_company_id, 'process_id': None},
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
            # For general documents, disable person and machine formsets (they will be auto-populated)
            if document_type == PerformanceRecord.DocumentType.GENERAL:
                context['person_formset'] = PerformanceRecordPersonFormSet(
                    instance=instance,
                    form_kwargs={'company_id': active_company_id, 'process_id': None},
                    prefix='persons',
                )
                context['machine_formset'] = PerformanceRecordMachineFormSet(
                    instance=instance,
                    form_kwargs={'company_id': active_company_id, 'process_id': None},
                    prefix='machines',
                )
            else:
                context['person_formset'] = PerformanceRecordPersonFormSet(
                    instance=instance,
                    form_kwargs={'company_id': active_company_id, 'process_id': None},
                    prefix='persons',
                )
                context['machine_formset'] = PerformanceRecordMachineFormSet(
                    instance=instance,
                    form_kwargs={'company_id': active_company_id, 'process_id': None},
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
        document_type = form.cleaned_data.get('document_type')
        
        if order:
            form.instance.finished_item = order.finished_item
            form.instance.unit = order.unit
            
            # For general documents, set quantity_planned from order
            if document_type == PerformanceRecord.DocumentType.GENERAL:
                form.instance.quantity_planned = order.quantity_planned
        
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
        
        # Populate materials based on document type
        document_type = form.cleaned_data.get('document_type')
        order = form.cleaned_data.get('order')
        operation = form.cleaned_data.get('operation')
        
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            # For operational documents: get actual materials from transfer documents for this order
            # Get all approved transfer documents for this order
            transfers = TransferToLine.objects.filter(
                company_id=active_company_id,
                order=order,
                status='approved',
                is_enabled=1,
            )
            
            # Collect all materials from all transfers (actual materials used)
            # Group by material_item to handle duplicates
            materials_dict = {}
            for transfer in transfers:
                for transfer_item in transfer.items.all():
                    material_item_id = transfer_item.material_item_id
                    if material_item_id not in materials_dict:
                        materials_dict[material_item_id] = {
                            'material_item': transfer_item.material_item,
                            'material_item_code': transfer_item.material_item_code,
                            'quantity_required': transfer_item.quantity_required,
                            'unit': transfer_item.unit,
                            'is_extra': transfer_item.is_extra,
                        }
                    else:
                        # Sum quantities if same material appears in multiple transfers
                        materials_dict[material_item_id]['quantity_required'] += transfer_item.quantity_required
            
            # Create performance record materials from actual transfer materials
            PerformanceRecordMaterial.objects.filter(performance=self.object).delete()
            for material_data in materials_dict.values():
                PerformanceRecordMaterial.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    material_item=material_data['material_item'],
                    material_item_code=material_data['material_item_code'],
                    quantity_required=material_data['quantity_required'],
                    quantity_waste=Decimal('0'),
                    unit=material_data['unit'],
                    is_extra=material_data['is_extra'],
                    created_by=self.request.user,
                )
        else:
            # For general documents: populate from transfer if selected, or use formset
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
        
        # Save persons and machines (only for operational documents)
        # For general documents, persons and machines will be auto-populated from operational records
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
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
        
        # For general documents, aggregate data from all operational performance records
        if document_type == PerformanceRecord.DocumentType.GENERAL:
            # Get all operational performance records for this order
            operational_records = PerformanceRecord.objects.filter(
                company_id=active_company_id,
                order=order,
                document_type=PerformanceRecord.DocumentType.OPERATIONAL,
            ).prefetch_related('persons', 'machines', 'materials')
            
            # Aggregate persons (sum work_minutes by person)
            persons_dict = {}
            for op_record in operational_records:
                for person_record in op_record.persons.all():
                    person_id = person_record.person_id
                    if person_id not in persons_dict:
                        persons_dict[person_id] = {
                            'person': person_record.person,
                            'person_code': person_record.person_code,
                            'work_minutes': person_record.work_minutes,
                            'work_line': person_record.work_line,
                            'work_line_code': person_record.work_line_code,
                            'notes': person_record.notes,
                        }
                    else:
                        persons_dict[person_id]['work_minutes'] += person_record.work_minutes
            
            # Aggregate machines (sum work_minutes by machine)
            machines_dict = {}
            for op_record in operational_records:
                for machine_record in op_record.machines.all():
                    machine_id = machine_record.machine_id
                    if machine_id not in machines_dict:
                        machines_dict[machine_id] = {
                            'machine': machine_record.machine,
                            'machine_code': machine_record.machine_code,
                            'work_minutes': machine_record.work_minutes,
                            'work_line': machine_record.work_line,
                            'work_line_code': machine_record.work_line_code,
                            'notes': machine_record.notes,
                        }
                    else:
                        machines_dict[machine_id]['work_minutes'] += machine_record.work_minutes
            
            # Aggregate materials (sum quantity_required and quantity_waste by material_item)
            materials_dict = {}
            for op_record in operational_records:
                for material_record in op_record.materials.all():
                    material_item_id = material_record.material_item_id
                    if material_item_id not in materials_dict:
                        materials_dict[material_item_id] = {
                            'material_item': material_record.material_item,
                            'material_item_code': material_record.material_item_code,
                            'quantity_required': material_record.quantity_required,
                            'quantity_waste': material_record.quantity_waste,
                            'unit': material_record.unit,
                            'is_extra': material_record.is_extra,
                            'notes': material_record.notes,
                        }
                    else:
                        materials_dict[material_item_id]['quantity_required'] += material_record.quantity_required
                        materials_dict[material_item_id]['quantity_waste'] += material_record.quantity_waste
            
            # Update or create aggregated records
            # Clear existing and create aggregated ones
            PerformanceRecordPerson.objects.filter(performance=self.object).delete()
            for person_data in persons_dict.values():
                PerformanceRecordPerson.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    person=person_data['person'],
                    person_code=person_data['person_code'],
                    work_minutes=person_data['work_minutes'],
                    work_line=person_data.get('work_line'),
                    work_line_code=person_data.get('work_line_code', ''),
                    notes=person_data.get('notes', ''),
                    created_by=self.request.user,
                )
            
            PerformanceRecordMachine.objects.filter(performance=self.object).delete()
            for machine_data in machines_dict.values():
                PerformanceRecordMachine.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    machine=machine_data['machine'],
                    machine_code=machine_data['machine_code'],
                    work_minutes=machine_data['work_minutes'],
                    work_line=machine_data.get('work_line'),
                    work_line_code=machine_data.get('work_line_code', ''),
                    notes=machine_data.get('notes', ''),
                    created_by=self.request.user,
                )
            
            PerformanceRecordMaterial.objects.filter(performance=self.object).delete()
            for material_data in materials_dict.values():
                PerformanceRecordMaterial.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    material_item=material_data['material_item'],
                    material_item_code=material_data['material_item_code'],
                    quantity_required=material_data['quantity_required'],
                    quantity_waste=material_data['quantity_waste'],
                    unit=material_data['unit'],
                    is_extra=material_data['is_extra'],
                    notes=material_data.get('notes', ''),
                    created_by=self.request.user,
                )
        
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
        
        # Get document_type from instance or form data
        document_type = self.object.document_type if self.object and self.object.pk else None
        if self.request.POST:
            document_type = self.request.POST.get('document_type', document_type or PerformanceRecord.DocumentType.OPERATIONAL)
        elif hasattr(self, 'form') and self.form and hasattr(self.form, 'cleaned_data') and self.form.cleaned_data.get('document_type'):
            document_type = self.form.cleaned_data.get('document_type')
        
        if not document_type:
            document_type = PerformanceRecord.DocumentType.OPERATIONAL
        
        context['document_type'] = document_type
        context['is_general_document'] = (document_type == PerformanceRecord.DocumentType.GENERAL)
        
        if self.request.POST:
            context['material_formset'] = PerformanceRecordMaterialFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': active_company_id},
                prefix='materials',
            )
            # For general documents, disable person and machine formsets (they will be auto-populated)
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
        
        # Get document_type and order
        document_type = form.cleaned_data.get('document_type', self.object.document_type)
        order = form.cleaned_data.get('order', self.object.order)
        
        # Handle materials based on document type
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            # For operational documents: get actual materials from transfer documents
            transfers = TransferToLine.objects.filter(
                company_id=active_company_id,
                order=order,
                status='approved',
                is_enabled=1,
            )
            
            # Collect all materials from all transfers
            materials_dict = {}
            for transfer in transfers:
                for transfer_item in transfer.items.all():
                    material_item_id = transfer_item.material_item_id
                    if material_item_id not in materials_dict:
                        materials_dict[material_item_id] = {
                            'material_item': transfer_item.material_item,
                            'material_item_code': transfer_item.material_item_code,
                            'quantity_required': transfer_item.quantity_required,
                            'unit': transfer_item.unit,
                            'is_extra': transfer_item.is_extra,
                        }
                    else:
                        materials_dict[material_item_id]['quantity_required'] += transfer_item.quantity_required
            
            # Update performance record materials
            # Keep existing waste quantities if material already exists
            existing_materials = {
                mat.material_item_id: mat for mat in self.object.materials.all()
            }
            
            PerformanceRecordMaterial.objects.filter(performance=self.object).delete()
            for material_data in materials_dict.values():
                existing_material = existing_materials.get(material_data['material_item'].id)
                PerformanceRecordMaterial.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    material_item=material_data['material_item'],
                    material_item_code=material_data['material_item_code'],
                    quantity_required=material_data['quantity_required'],
                    quantity_waste=existing_material.quantity_waste if existing_material else Decimal('0'),
                    unit=material_data['unit'],
                    is_extra=material_data['is_extra'],
                    created_by=self.request.user,
                )
        else:
            # For general documents: use formset or recalculate from operational records
            if material_formset.is_valid():
                material_formset.save()
            else:
                messages.error(self.request, _('Error saving materials. Please check the form.'))
                return self.form_invalid(form)
        
        # Handle persons and machines
        if document_type == PerformanceRecord.DocumentType.GENERAL:
            # For general documents: recalculate from operational records
            operational_records = PerformanceRecord.objects.filter(
                company_id=active_company_id,
                order=order,
                document_type=PerformanceRecord.DocumentType.OPERATIONAL,
            ).prefetch_related('persons', 'machines')
            
            # Aggregate persons
            persons_dict = {}
            for op_record in operational_records:
                for person_record in op_record.persons.all():
                    person_id = person_record.person_id
                    if person_id not in persons_dict:
                        persons_dict[person_id] = {
                            'person': person_record.person,
                            'person_code': person_record.person_code,
                            'work_minutes': person_record.work_minutes,
                            'work_line': person_record.work_line,
                            'work_line_code': person_record.work_line_code,
                            'notes': person_record.notes,
                        }
                    else:
                        persons_dict[person_id]['work_minutes'] += person_record.work_minutes
            
            # Aggregate machines
            machines_dict = {}
            for op_record in operational_records:
                for machine_record in op_record.machines.all():
                    machine_id = machine_record.machine_id
                    if machine_id not in machines_dict:
                        machines_dict[machine_id] = {
                            'machine': machine_record.machine,
                            'machine_code': machine_record.machine_code,
                            'work_minutes': machine_record.work_minutes,
                            'work_line': machine_record.work_line,
                            'work_line_code': machine_record.work_line_code,
                            'notes': machine_record.notes,
                        }
                    else:
                        machines_dict[machine_id]['work_minutes'] += machine_record.work_minutes
            
            # Update aggregated records
            PerformanceRecordPerson.objects.filter(performance=self.object).delete()
            for person_data in persons_dict.values():
                PerformanceRecordPerson.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    person=person_data['person'],
                    person_code=person_data['person_code'],
                    work_minutes=person_data['work_minutes'],
                    work_line=person_data.get('work_line'),
                    work_line_code=person_data.get('work_line_code', ''),
                    notes=person_data.get('notes', ''),
                    created_by=self.request.user,
                )
            
            PerformanceRecordMachine.objects.filter(performance=self.object).delete()
            for machine_data in machines_dict.values():
                PerformanceRecordMachine.objects.create(
                    performance=self.object,
                    company_id=active_company_id,
                    machine=machine_data['machine'],
                    machine_code=machine_data['machine_code'],
                    work_minutes=machine_data['work_minutes'],
                    work_line=machine_data.get('work_line'),
                    work_line_code=machine_data.get('work_line_code', ''),
                    notes=machine_data.get('notes', ''),
                    created_by=self.request.user,
                )
        else:
            # For operational documents: use formsets
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


class PerformanceRecordDetailView(FeaturePermissionRequiredMixin, DetailView):
    """Detail view for viewing performance records (read-only)."""
    model = PerformanceRecord
    template_name = 'production/performance_record_detail.html'
    context_object_name = 'performance_record'
    feature_code = 'production.performance_records'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return PerformanceRecord.objects.none()
        queryset = PerformanceRecord.objects.filter(company_id=active_company_id)
        queryset = queryset.select_related(
            'order',
            'order__bom',
            'order__finished_item',
            'order__process',
            'transfer',
            'approved_by',
            'created_by',
            'edited_by',
        ).prefetch_related(
            'materials__material_item',
            'persons__person',
            'machines__machine',
        )
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('production:performance_records')
        context['edit_url'] = reverse_lazy('production:performance_record_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'production.performance_records'
        return context


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


class PerformanceRecordGetOperationsView(FeaturePermissionRequiredMixin, View):
    """AJAX view to get operations for an order (for operational performance records)."""
    feature_code = 'production.performance_records'
    required_action = 'view_own'  # Use view_own instead of create for AJAX requests
    
    def get(self, request, *args, **kwargs):
        """Return operations for the selected order."""
        active_company_id = request.session.get('active_company_id')
        if not active_company_id:
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        order_id = request.GET.get('order_id')
        if not order_id:
            return JsonResponse({'error': _('Order ID is required.')}, status=400)
        
        try:
            order = ProductOrder.objects.get(
                pk=order_id,
                company_id=active_company_id,
                is_enabled=1,
            )
        except ProductOrder.DoesNotExist:
            return JsonResponse({'error': _('Order not found.')}, status=404)
        
        if not order.process:
            return JsonResponse({'operations': []})
        
        # Get operations that don't have performance records yet
        # Filter out None values from operation_id
        operations_with_performance = list(PerformanceRecord.objects.filter(
            company_id=active_company_id,
            order=order,
            document_type=PerformanceRecord.DocumentType.OPERATIONAL,
        ).exclude(operation__isnull=True).values_list('operation_id', flat=True))
        
        operations = ProcessOperation.objects.filter(
            process=order.process,
            company_id=active_company_id,
        )
        
        # Only exclude if there are operations with performance records
        if operations_with_performance:
            operations = operations.exclude(id__in=operations_with_performance)
        
        operations = operations.order_by('sequence_order', 'id')
        
        operations_data = [
            {
                'id': op.id,
                'name': op.name or f"Operation {op.sequence_order}",
                'sequence_order': op.sequence_order,
                'description': op.description or '',
            }
            for op in operations
        ]
        
        return JsonResponse({
            'operations': operations_data,
            'total': len(operations_data),
            'order_id': order_id,
            'process_id': order.process_id if order.process else None,
        })


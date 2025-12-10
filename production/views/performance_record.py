"""
Performance Record CRUD views for production module.
"""
from decimal import Decimal
from typing import Any, Dict, Optional, List
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django.views import View

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseDocumentListView,
    BaseDetailView,
    BaseDeleteView,
    EditLockProtectedMixin,
)
from shared.views.base_additional import BaseMultipleFormsetCreateView, BaseMultipleFormsetUpdateView
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
    OperationQCStatus,
)


class PerformanceRecordListView(BaseDocumentListView):
    """List all performance records for the active company."""
    model = PerformanceRecord
    template_name = 'production/performance_record_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.performance_records'
    required_action = 'view_own'
    active_module = 'production'
    default_status_filter = False
    default_order_by = ['-performance_date', 'performance_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return [
            'order',
            'order__bom',
            'order__finished_item',
            'order__process',
            'transfer',
            'approved_by',
        ]
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['materials', 'persons', 'machines']
    
    def get_queryset(self):
        """Filter performance records by active company and permissions."""
        queryset = super().get_queryset()
        
        # Check if user has view_all permission
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            if not has_feature_permission(permissions, 'production.performance_records', action='view_all'):
                # Only show own records
                queryset = queryset.filter(created_by=self.request.user)
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Performance Records')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL if user has permission."""
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            if has_feature_permission(permissions, 'production.performance_records', action='create') or self.request.user.is_superuser:
                return reverse_lazy('production:performance_record_create')
        return None
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Performance Record')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:performance_record_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:performance_record_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:performance_record_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Performance Records Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Create your first performance record to get started.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📊'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['show_filters'] = False
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
        return context


class PerformanceRecordCreateView(BaseMultipleFormsetCreateView):
    """Create a new performance record."""
    model = PerformanceRecord
    form_class = PerformanceRecordForm
    template_name = 'production/performance_record_form.html'
    success_url = reverse_lazy('production:performance_records')
    feature_code = 'production.performance_records'
    required_action = 'create'
    active_module = 'production'
    success_message = _('Performance record created successfully.')
    
    formsets = {
        'materials': PerformanceRecordMaterialFormSet,
        'persons': PerformanceRecordPersonFormSet,
        'machines': PerformanceRecordMachineFormSet,
    }
    formset_prefixes = {
        'materials': 'materials',
        'persons': 'persons',
        'machines': 'machines',
    }
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]:
        """Return kwargs for a specific formset."""
        active_company_id = self.request.session.get('active_company_id')
        kwargs = {'form_kwargs': {'company_id': active_company_id}}
        
        # Get order, process_id, and operation_id from form if available
        if hasattr(self, 'form') and self.form and hasattr(self.form, 'cleaned_data') and self.form.cleaned_data:
            order = self.form.cleaned_data.get('order')
            operation = self.form.cleaned_data.get('operation')
            if order:
                kwargs['form_kwargs']['process_id'] = order.process_id if order else None
            if operation:
                kwargs['form_kwargs']['operation_id'] = operation.id if operation else None
        elif self.request.POST:
            order_id = self.request.POST.get('order')
            operation_id = self.request.POST.get('operation')
            if order_id:
                try:
                    order = ProductOrder.objects.get(id=int(order_id))
                    kwargs['form_kwargs']['process_id'] = order.process_id if order else None
                except (ProductOrder.DoesNotExist, ValueError, TypeError):
                    pass
            if operation_id:
                kwargs['form_kwargs']['operation_id'] = int(operation_id)
        
        if hasattr(self, 'object') and self.object:
            kwargs['instance'] = self.object
            # If object exists and has operation, add operation_id
            if self.object.operation_id:
                kwargs['form_kwargs']['operation_id'] = self.object.operation_id
        
        return kwargs
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': reverse_lazy('production:performance_records')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:performance_records')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Performance Record')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formsets to context."""
        context = super().get_context_data(**kwargs)
        context['form_id'] = 'performance-form'
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
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
        
        return context
    
    def process_formset(self, formset_name: str, formset) -> Optional[List[Any]]:
        """
        Process formset before saving. Override for custom logic.
        For materials formset, handle custom logic based on document type.
        """
        if formset_name == 'materials':
            # Materials will be handled in after_formsets_save
            # Return None to skip default saving
            return []
        return None
    
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
        
        # Check if creating general performance document is allowed
        # General documents can only be created if all operations requiring QC are approved
        if order and document_type == PerformanceRecord.DocumentType.GENERAL:
            if order.process:
                # Get all operations that require QC for this order's process
                qc_required_operations = order.process.operations.filter(
                    company_id=active_company_id,
                    requires_qc=1,
                    is_enabled=1,
                )
                
                # Check if all QC-required operations have approved QC status
                for qc_op in qc_required_operations:
                    # Check if performance record exists for this operation
                    has_performance = PerformanceRecord.objects.filter(
                        company_id=active_company_id,
                        order=order,
                        operation=qc_op,
                        document_type=PerformanceRecord.DocumentType.OPERATIONAL,
                    ).exists()
                    
                    if has_performance:
                        # Check QC status
                        qc_status = OperationQCStatus.objects.filter(
                            company_id=active_company_id,
                            order=order,
                            operation=qc_op,
                        ).first()
                        
                        if not qc_status or qc_status.qc_status != OperationQCStatus.QCStatus.APPROVED:
                            operation_name = qc_op.name or f"Operation {qc_op.sequence_order}"
                            messages.error(
                                self.request,
                                _(
                                    'Cannot create general performance document. '
                                    'Operation "%(operation)s" requires QC approval first.'
                                ) % {'operation': operation_name}
                            )
                            return self.form_invalid(form)
        
        if order:
            form.instance.finished_item = order.finished_item
            form.instance.unit = order.unit
            
            # For general documents, set quantity_planned from order
            if document_type == PerformanceRecord.DocumentType.GENERAL:
                form.instance.quantity_planned = order.quantity_planned
        
        # Store form data for use in after_formsets_save
        self._form_data = form.cleaned_data
        self._active_company_id = active_company_id
        
        # Save performance record header using parent's form_valid
        return super().form_valid(form)
    
    def validate_formsets(self) -> bool:
        """Validate formsets. Skip materials validation for custom handling."""
        context = self.get_context_data()
        document_type = self._form_data.get('document_type')
        
        # For materials, we'll handle validation in after_formsets_save
        # For persons and machines, only validate for operational documents
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            for formset_name in ['persons', 'machines']:
                formset = context.get(f'{formset_name}_formset')
                if formset and not formset.is_valid():
                    return False
        
        return True
    
    def save_formsets(self) -> Dict[str, List[Any]]:
        """Save formsets. Skip materials for custom handling."""
        context = self.get_context_data()
        saved_instances = {}
        document_type = self._form_data.get('document_type')
        
        # Save persons and machines only for operational documents
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            for formset_name in ['persons', 'machines']:
                formset = context.get(f'{formset_name}_formset')
                if formset and formset.is_valid():
                    formset.instance = self.object
                    saved_instances[formset_name] = formset.save()
                else:
                    saved_instances[formset_name] = []
        
        # Materials will be handled in after_formsets_save
        saved_instances['materials'] = []
        
        return saved_instances
    
    def after_formsets_save(self, saved_instances: Dict[str, List[Any]]) -> None:
        """Handle custom logic after formsets are saved."""
        active_company_id = self._active_company_id
        form_data = self._form_data
        document_type = form_data.get('document_type')
        order = form_data.get('order')
        operation = form_data.get('operation')
        transfer = form_data.get('transfer')
        
        # Handle materials based on document type
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            # For operational documents: get actual materials from warehouse transfer documents
            # Materials come from IssueWarehouseTransferLine where destination_warehouse == operation.work_line.warehouse
            if not operation:
                messages.warning(self.request, _('Operation must be selected for operational performance records.'))
                return
            
            # Refresh operation from database to get work_line relationship
            try:
                operation = ProcessOperation.objects.select_related('work_line', 'work_line__warehouse').get(
                    pk=operation.pk,
                    company_id=active_company_id,
                )
            except ProcessOperation.DoesNotExist:
                messages.error(self.request, _('Operation not found.'))
                return
            
            if not operation.work_line:
                messages.warning(self.request, _('Operation must have a work line assigned to populate materials.'))
                return
            
            if not operation.work_line.warehouse:
                messages.warning(self.request, _('Operation work line must have a warehouse assigned to populate materials.'))
                return
            
            from inventory.models import IssueWarehouseTransferLine
            
            # Get warehouse transfer lines for this operation's work line warehouse
            warehouse_transfer_lines = IssueWarehouseTransferLine.objects.filter(
                company_id=active_company_id,
                destination_warehouse=operation.work_line.warehouse,
                document__production_transfer__order=order,
                document__production_transfer__status='approved',
                document__production_transfer__is_enabled=1,
            ).select_related('item', 'document', 'document__production_transfer')
            
            if not warehouse_transfer_lines.exists():
                messages.info(self.request, _('No warehouse transfer documents found for this operation. Materials will be empty.'))
            
            # Collect all materials from warehouse transfer lines
            materials_dict = {}
            for transfer_line in warehouse_transfer_lines:
                material_item_id = transfer_line.item_id
                if material_item_id not in materials_dict:
                    materials_dict[material_item_id] = {
                        'material_item': transfer_line.item,
                        'material_item_code': transfer_line.item_code,
                        'quantity_required': transfer_line.quantity,
                        'unit': transfer_line.unit,
                        'is_extra': 0,  # Materials from warehouse transfer are from BOM (not extra)
                    }
                else:
                    materials_dict[material_item_id]['quantity_required'] += transfer_line.quantity
            
            # Create performance record materials
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
            if transfer:
                PerformanceRecordMaterial.objects.filter(performance=self.object).delete()
                for transfer_item in transfer.items.all():
                    PerformanceRecordMaterial.objects.create(
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
            else:
                # Use formset
                material_formset = PerformanceRecordMaterialFormSet(
                    self.request.POST,
                    instance=self.object,
                    form_kwargs={'company_id': active_company_id},
                    prefix='materials',
                )
                if material_formset.is_valid():
                    material_formset.save()
                else:
                    messages.error(self.request, _('Error saving materials. Please check the form.'))
        
        # For general documents, aggregate data from all operational performance records
        if document_type == PerformanceRecord.DocumentType.GENERAL:
            operational_records = PerformanceRecord.objects.filter(
                company_id=active_company_id,
                order=order,
                document_type=PerformanceRecord.DocumentType.OPERATIONAL,
            ).prefetch_related('persons', 'machines', 'materials')
            
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
            
            # Aggregate materials
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
            
            # Create aggregated records
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
            
            # Update materials (aggregate with existing if any)
            existing_materials = PerformanceRecordMaterial.objects.filter(performance=self.object)
            for material_data in materials_dict.values():
                existing = existing_materials.filter(material_item=material_data['material_item']).first()
                if existing:
                    existing.quantity_required += material_data['quantity_required']
                    existing.quantity_waste += material_data['quantity_waste']
                    existing.save()
                else:
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
        
        # Create OperationQCStatus if this is an operational document for an operation that requires QC
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL and operation:
            if operation.requires_qc == 1:
                OperationQCStatus.objects.get_or_create(
                    company_id=active_company_id,
                    order=order,
                    operation=operation,
                    performance=self.object,
                    defaults={
                        'qc_status': OperationQCStatus.QCStatus.PENDING,
                        'created_by': self.request.user,
                    }
                )


class PerformanceRecordUpdateView(BaseMultipleFormsetUpdateView, EditLockProtectedMixin):
    """Update an existing performance record."""
    model = PerformanceRecord
    form_class = PerformanceRecordForm
    template_name = 'production/performance_record_form.html'
    success_url = reverse_lazy('production:performance_records')
    feature_code = 'production.performance_records'
    required_action = 'edit_own'
    active_module = 'production'
    success_message = _('Performance record updated successfully.')
    
    formsets = {
        'materials': PerformanceRecordMaterialFormSet,
        'persons': PerformanceRecordPersonFormSet,
        'machines': PerformanceRecordMachineFormSet,
    }
    formset_prefixes = {
        'materials': 'materials',
        'persons': 'persons',
        'machines': 'machines',
    }
    
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
    
    def get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]:
        """Return kwargs for a specific formset."""
        active_company_id = self.request.session.get('active_company_id')
        kwargs = {'form_kwargs': {'company_id': active_company_id}}
        
        # Get process_id from order
        if self.object and self.object.order:
            kwargs['form_kwargs']['process_id'] = self.object.order.process_id if self.object.order.process else None
        
        kwargs['instance'] = self.object
        
        return kwargs
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': reverse_lazy('production:performance_records')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:performance_records')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Performance Record')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add formsets to context."""
        context = super().get_context_data(**kwargs)
        context['form_id'] = 'performance-form'
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
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
        
        return context
    
    def process_formset(self, formset_name: str, formset) -> Optional[List[Any]]:
        """
        Process formset before saving. Override for custom logic.
        For materials formset, handle custom logic based on document type.
        """
        if formset_name == 'materials':
            # Materials will be handled in after_formsets_save
            # Return empty list to skip default saving
            return []
        return None
    
    def validate_formsets(self) -> bool:
        """Validate formsets. Skip materials validation for custom handling."""
        context = self.get_context_data()
        document_type = self.object.document_type if self.object else PerformanceRecord.DocumentType.OPERATIONAL
        
        # For materials, we'll handle validation in after_formsets_save
        # For persons and machines, only validate for operational documents
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            for formset_name in ['persons', 'machines']:
                formset = context.get(f'{formset_name}_formset')
                if formset and not formset.is_valid():
                    return False
        
        return True
    
    def save_formsets(self) -> Dict[str, List[Any]]:
        """Save formsets. Skip materials for custom handling."""
        context = self.get_context_data()
        saved_instances = {}
        document_type = self.object.document_type if self.object else PerformanceRecord.DocumentType.OPERATIONAL
        
        # Save persons and machines only for operational documents
        if document_type == PerformanceRecord.DocumentType.OPERATIONAL:
            for formset_name in ['persons', 'machines']:
                formset = context.get(f'{formset_name}_formset')
                if formset and formset.is_valid():
                    formset.instance = self.object
                    saved_instances[formset_name] = formset.save()
                else:
                    saved_instances[formset_name] = []
        
        # Materials will be handled in after_formsets_save
        saved_instances['materials'] = []
        
        return saved_instances
    
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
        
        # Store form data for use in after_formsets_save
        self._form_data = form.cleaned_data
        self._active_company_id = active_company_id
        
        # Save performance record header using parent's form_valid
        return super().form_valid(form)
    
    def after_formsets_save(self, saved_instances: Dict[str, List[Any]]) -> None:
        """Handle custom logic after formsets are saved."""
        active_company_id = self._active_company_id
        form_data = self._form_data
        document_type = form_data.get('document_type', self.object.document_type)
        order = form_data.get('order', self.object.order)
        
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
            # For general documents: use formset
            material_formset = PerformanceRecordMaterialFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': active_company_id},
                prefix='materials',
            )
            if material_formset.is_valid():
                material_formset.save()
            else:
                messages.error(self.request, _('Error saving materials. Please check the form.'))
        
        # Handle persons and machines for general documents
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


class PerformanceRecordDetailView(BaseDetailView):
    """Detail view for viewing performance records (read-only)."""
    model = PerformanceRecord
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'production.performance_records'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
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
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Performance Record')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        record = self.object
        
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = [
            {'label': _('Performance Code'), 'value': record.performance_code, 'type': 'code'},
            {'label': _('Performance Date'), 'value': record.performance_date},
            {'label': _('Status'), 'value': record.get_status_display()},
        ]
        
        # Order Information section
        order_fields = []
        if record.order:
            order_value = record.order.order_code
            if record.order.finished_item:
                order_value += f" ({record.order.finished_item.name})"
            order_fields.append({
                'label': _('Product Order'),
                'value': order_value,
            })
        if record.transfer:
            order_fields.append({
                'label': _('Transfer Request'),
                'value': record.transfer.transfer_code,
            })
        
        detail_sections = [
            {
                'title': _('Order Information'),
                'fields': order_fields,
            },
        ]
        
        # Production Quantities section
        detail_sections.append({
            'title': _('Production Quantities'),
            'fields': [
                {'label': _('Quantity Produced'), 'value': f"{record.quantity_produced:.2f}"},
                {'label': _('Quantity Received'), 'value': f"{record.quantity_received:.2f}"},
                {'label': _('Quantity Scrapped'), 'value': f"{record.quantity_scrapped:.2f}"},
            ],
        })
        
        # Time Information section
        detail_sections.append({
            'title': _('Time Information'),
            'fields': [
                {'label': _('Unit Cycle Minutes'), 'value': f"{record.unit_cycle_minutes:.2f}"},
                {'label': _('Total Run Minutes'), 'value': f"{record.total_run_minutes:.2f}"},
                {'label': _('Machine Usage Minutes'), 'value': f"{record.machine_usage_minutes:.2f}"},
            ],
        })
        
        # Material Usage section (table)
        if record.materials.exists():
            headers = [
                _('Material Item'),
                _('Quantity Used'),
                _('Unit'),
                _('Scrap Quantity'),
            ]
            data = []
            for material in record.materials.all():
                data.append([
                    f"{material.material_item.name} ({material.material_item.item_code})",
                    f"{material.quantity_used:.2f}",
                    material.unit,
                    f"{material.scrap_quantity:.2f}",
                ])
            
            detail_sections.append({
                'title': _('Material Usage'),
                'type': 'table',
                'headers': headers,
                'data': data,
            })
        
        # Personnel Usage section (table)
        if record.persons.exists():
            headers = [
                _('Person'),
                _('Minutes'),
            ]
            data = []
            for person in record.persons.all():
                data.append([
                    f"{person.person.first_name} {person.person.last_name}",
                    f"{person.minutes:.2f}",
                ])
            
            detail_sections.append({
                'title': _('Personnel Usage'),
                'type': 'table',
                'headers': headers,
                'data': data,
            })
        
        # Machine Usage section (table)
        if record.machines.exists():
            headers = [
                _('Machine'),
                _('Minutes'),
            ]
            data = []
            for machine in record.machines.all():
                data.append([
                    machine.machine.name,
                    f"{machine.minutes:.2f}",
                ])
            
            detail_sections.append({
                'title': _('Machine Usage'),
                'type': 'table',
                'headers': headers,
                'data': data,
            })
        
        # Approval Information section
        if record.approved_by:
            approval_fields = [
                {
                    'label': _('Approved By'),
                    'value': record.approved_by.get_full_name() or record.approved_by.username,
                },
            ]
            if record.approved_at:
                approval_fields.append({
                    'label': _('Approved At'),
                    'value': record.approved_at,
                })
            detail_sections.append({
                'title': _('Approval Information'),
                'fields': approval_fields,
            })
        
        # Notes section
        if record.notes:
            detail_sections.append({
                'title': _('Notes'),
                'fields': [
                    {'label': _('Notes'), 'value': record.notes},
                ],
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:performance_records')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:performance_record_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class PerformanceRecordDeleteView(BaseDeleteView):
    """Delete a performance record."""
    model = PerformanceRecord
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:performance_records')
    feature_code = 'production.performance_records'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Performance record deleted successfully.')
    
    def get_queryset(self):
        """Filter by company and check permissions."""
        queryset = super().get_queryset()
        
        # Check if user has delete_other permission
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
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
        
        return super().delete(request, *args, **kwargs)
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Performance Record')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this performance record?')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        from production.utils.jalali import gregorian_to_jalali
        
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
        
        details = [
            {'label': _('Performance Code'), 'value': f'<code>{self.object.performance_code}</code>'},
            {'label': _('Product Order'), 'value': self.object.order_code},
            {'label': _('Performance Date'), 'value': performance_date_jalali},
            {'label': _('Status'), 'value': self.object.get_status_display()},
            {'label': _('Planned Quantity'), 'value': f'{self.object.quantity_planned} {self.object.unit}'},
            {'label': _('Actual Quantity'), 'value': f'{self.object.quantity_actual} {self.object.unit}'},
        ]
        
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Performance Records'), 'url': reverse_lazy('production:performance_records')},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        
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


class PerformanceRecordGetOperationDataView(FeaturePermissionRequiredMixin, View):
    """AJAX view to get materials, personnel, and machines for a selected operation."""
    feature_code = 'production.performance_records'
    required_action = 'view_own'
    
    def get(self, request, *args, **kwargs):
        """Return materials, personnel, and machines for the selected operation."""
        active_company_id = request.session.get('active_company_id')
        if not active_company_id:
            return JsonResponse({'error': _('Please select a company first.')}, status=400)
        
        operation_id = request.GET.get('operation_id')
        order_id = request.GET.get('order_id')
        
        if not operation_id:
            return JsonResponse({'error': _('Operation ID is required.')}, status=400)
        
        if not order_id:
            return JsonResponse({'error': _('Order ID is required.')}, status=400)
        
        try:
            operation = ProcessOperation.objects.select_related('work_line', 'work_line__warehouse').get(
                pk=operation_id,
                company_id=active_company_id,
            )
        except ProcessOperation.DoesNotExist:
            return JsonResponse({'error': _('Operation not found.')}, status=404)
        
        try:
            order = ProductOrder.objects.get(
                pk=order_id,
                company_id=active_company_id,
                is_enabled=1,
            )
        except ProductOrder.DoesNotExist:
            return JsonResponse({'error': _('Order not found.')}, status=404)
        
        response_data = {
            'materials': [],
            'personnel': [],
            'machines': [],
        }
        
        # Get materials from IssueWarehouseTransferLine
        if operation.work_line and operation.work_line.warehouse:
            from inventory.models import IssueWarehouseTransferLine
            
            warehouse_transfer_lines = IssueWarehouseTransferLine.objects.filter(
                company_id=active_company_id,
                destination_warehouse=operation.work_line.warehouse,
                document__production_transfer__order=order,
                document__production_transfer__status='approved',
                document__production_transfer__is_enabled=1,
            ).select_related('item', 'document', 'document__production_transfer').order_by('item_code')
            
            # Group materials by item (sum quantities)
            materials_dict = {}
            for transfer_line in warehouse_transfer_lines:
                material_item_id = transfer_line.item_id
                if material_item_id not in materials_dict:
                    materials_dict[material_item_id] = {
                        'item_id': transfer_line.item_id,
                        'item_code': transfer_line.item_code,
                        'item_name': transfer_line.item.name,
                        'quantity_required': float(transfer_line.quantity),
                        'unit': transfer_line.unit,
                    }
                else:
                    materials_dict[material_item_id]['quantity_required'] += float(transfer_line.quantity)
            
            response_data['materials'] = list(materials_dict.values())
        else:
            response_data['error'] = _('Operation must have a work line with warehouse to get materials.')
        
        # Get personnel from work_line
        if operation.work_line:
            personnel = operation.work_line.personnel.filter(
                company_id=active_company_id,
                is_enabled=1,
            ).order_by('first_name', 'last_name')
            
            response_data['personnel'] = [
                {
                    'id': person.id,
                    'code': person.public_code,
                    'name': f"{person.first_name} {person.last_name}",
                }
                for person in personnel
            ]
        else:
            response_data['warning'] = _('Operation must have a work line to get personnel.')
        
        # Get machines from work_line
        if operation.work_line:
            machines = operation.work_line.machines.filter(
                company_id=active_company_id,
                is_enabled=1,
            ).order_by('name')
            
            response_data['machines'] = [
                {
                    'id': machine.id,
                    'code': machine.public_code,
                    'name': machine.name,
                }
                for machine in machines
            ]
        else:
            if 'warning' not in response_data:
                response_data['warning'] = _('Operation must have a work line to get machines.')
        
        # Add work_line info
        if operation.work_line:
            response_data['work_line'] = {
                'id': operation.work_line.id,
                'code': operation.work_line.public_code,
                'name': operation.work_line.name,
                'warehouse_id': operation.work_line.warehouse_id if operation.work_line.warehouse else None,
            }
        
        # Add operation info (labor_minutes_per_unit, machine_minutes_per_unit)
        response_data['operation'] = {
            'id': operation.id,
            'labor_minutes_per_unit': float(operation.labor_minutes_per_unit) if operation.labor_minutes_per_unit else 0,
            'machine_minutes_per_unit': float(operation.machine_minutes_per_unit) if operation.machine_minutes_per_unit else 0,
        }
        
        # Add order quantity for calculation
        response_data['order'] = {
            'quantity_planned': float(order.quantity_planned) if order.quantity_planned else 0,
        }
        
        return JsonResponse(response_data)


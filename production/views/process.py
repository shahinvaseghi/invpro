"""
Process CRUD views for production module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from production.forms import (
    ProcessForm,
    ProcessOperationFormSet,
    ProcessOperationMaterialFormSet,
)
from production.models import Process, ProcessOperation, ProcessOperationMaterial


def save_operation_materials_from_post(request, operation, operation_index, company_id, bom_id=None):
    """
    Save materials for an operation by parsing POST data manually.
    
    Format in POST: materials-{operation_index}-{material_index}-{field_name}
    """
    from production.models import BOMMaterial
    
    # Parse materials manually from POST data
    # Format: materials-{operation_index}-{material_index}-{field_name}
    materials_data = {}
    
    # Collect all material data from POST
    for key, value in request.POST.items():
        if key.startswith(f'materials-{operation_index}-'):
            # Extract material index and field name
            parts = key.split('-')
            if len(parts) >= 4:
                material_index = parts[2]
                field_name = '-'.join(parts[3:])
                
                if material_index not in materials_data:
                    materials_data[material_index] = {}
                
                materials_data[material_index][field_name] = value
    
    # Track which materials should be kept (updated or newly created)
    kept_material_ids = set()
    
    # Save materials from POST data
    for material_index, mat_data in materials_data.items():
        bom_material_id = mat_data.get('bom_material', '').strip()
        quantity_used = mat_data.get('quantity_used', '').strip()
        
        # Skip empty materials
        if not bom_material_id or not quantity_used:
            continue
        
        try:
            bom_material = BOMMaterial.objects.get(
                id=int(bom_material_id),
                is_enabled=1,
            )
            
            # Get or create material
            material_id = mat_data.get('id', '').strip()
            if material_id:
                try:
                    material = ProcessOperationMaterial.objects.get(
                        id=int(material_id),
                        operation=operation,
                    )
                    # Update existing
                    material.bom_material = bom_material
                    material.material_item = bom_material.material_item
                    material.material_item_code = bom_material.material_item_code
                    material.quantity_used = quantity_used
                    material.unit = bom_material.unit
                    material.is_enabled = 1
                    if hasattr(material, 'edited_by'):
                        material.edited_by = request.user
                    material.save()
                    kept_material_ids.add(material.id)
                except (ProcessOperationMaterial.DoesNotExist, ValueError):
                    # Create new if ID doesn't exist
                    material = ProcessOperationMaterial.objects.create(
                        operation=operation,
                        company_id=company_id,
                        created_by=request.user,
                        bom_material=bom_material,
                        material_item=bom_material.material_item,
                        material_item_code=bom_material.material_item_code,
                        quantity_used=quantity_used,
                        unit=bom_material.unit,
                    )
                    kept_material_ids.add(material.id)
            else:
                # Create new material
                material = ProcessOperationMaterial.objects.create(
                    operation=operation,
                    company_id=company_id,
                    created_by=request.user,
                    bom_material=bom_material,
                    material_item=bom_material.material_item,
                    material_item_code=bom_material.material_item_code,
                    quantity_used=quantity_used,
                    unit=bom_material.unit,
                )
                kept_material_ids.add(material.id)
        except (BOMMaterial.DoesNotExist, ValueError, TypeError) as e:
            messages.error(request, f"❌ {_('Material')} {operation_index + 1}: {_('Invalid material selected.')}")
            return False
    
    # Hard delete materials that were not in the POST data (truly removed)
    if operation.pk:
        all_existing_ids = set(
            ProcessOperationMaterial.objects.filter(
                operation=operation,
                is_enabled=1,
            ).values_list('id', flat=True)
        )
        ids_to_delete = all_existing_ids - kept_material_ids
        if ids_to_delete:
            ProcessOperationMaterial.objects.filter(
                id__in=ids_to_delete,
                operation=operation,
            ).delete()
    
    return True


class ProcessListView(FeaturePermissionRequiredMixin, ListView):
    """List all processes for the active company."""
    model = Process
    template_name = 'production/processes.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.processes'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter processes by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Process.objects.none()
        
        queryset = Process.objects.filter(
            company_id=active_company_id
        )
        
        queryset = queryset.select_related(
            'finished_item',
            'bom',
            'approved_by',  # Now FK to User, not Person
        ).prefetch_related('work_lines')
        
        # Try to prefetch operations if table exists
        # This is a safety check in case migration hasn't been run yet
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Check if ProcessOperation table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'production_processoperation'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
            if table_exists:
                queryset = queryset.prefetch_related(
                    'operations',
                    'operations__operation_materials',
                    'operations__operation_materials__bom_material',
                )
        except Exception:
            # If check fails (e.g., table doesn't exist), skip operations prefetch
            # This allows the page to load even if migration hasn't been run
            pass
        
        return queryset.order_by('finished_item__name', 'revision', 'sort_order')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Processes')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('production:process_create')
        context['create_button_text'] = _('+ Create Process')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['feature_code'] = 'production.processes'
        context['detail_url_name'] = 'production:process_detail'
        context['edit_url_name'] = 'production:process_edit'
        context['delete_url_name'] = 'production:process_delete'
        context['empty_state_title'] = _('No Processes Found')
        context['empty_state_message'] = _('Start by creating your first process.')
        context['empty_state_icon'] = '⚙️'
        return context


class ProcessCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new process."""
    model = Process
    form_class = ProcessForm
    template_name = 'production/process_form.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    @transaction.atomic
    def form_valid(self, form: ProcessForm) -> HttpResponseRedirect:
        """Auto-set company, created_by, finished_item, save M2M relationships and operations."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        # Set finished_item from BOM
        bom = form.cleaned_data.get('bom')
        if bom:
            form.instance.finished_item = bom.finished_item
        
        # Save process first
        response = super().form_valid(form)
        
        # Save Many-to-Many relationships
        form.save_m2m()
        
        # Get BOM ID for operations
        bom_id = bom.id if bom else None
        
        # Handle operations formset
        operations_formset = ProcessOperationFormSet(
            self.request.POST,
            prefix='operations',
            form_kwargs={'bom_id': bom_id, 'company_id': active_company_id},
        )
        
        if operations_formset.is_valid():
            # Save operations
            operations = []
            for operation_form in operations_formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    # Check if operation has required fields
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if name or sequence_order:
                        operation = operation_form.save(commit=False)
                        operation.process = self.object
                        operation.company_id = active_company_id
                        operation.created_by = self.request.user
                        operation.save()
                        operations.append(operation)
            
            # Now save materials for each operation
            operation_index = 0
            for operation_form in operations_formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if (name or sequence_order) and operation_index < len(operations):
                        operation = operations[operation_index]
                        
                        # Save materials manually from POST data
                        save_operation_materials_from_post(
                            self.request,
                            operation,
                            operation_index,
                            active_company_id,
                            bom_id,
                        )
                        
                        operation_index += 1
        else:
            # Show operations formset errors
            if operations_formset.non_form_errors():
                for error in operations_formset.non_form_errors():
                    messages.error(self.request, f"❌ {error}")
            for i, op_form in enumerate(operations_formset):
                if op_form.errors:
                    for field, errors in op_form.errors.items():
                        for error in errors:
                            field_label = op_form.fields[field].label if field in op_form.fields else field
                            messages.error(self.request, f"❌ {_('Operation')} {i + 1} - {field_label}: {error}")
        
        messages.success(self.request, _('Process created successfully.'))
        return response
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form title, breadcrumbs, and operations formset to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Process')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': reverse_lazy('production:processes')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:processes')
        context['form_id'] = 'process-form'
        
        # Get BOM ID from form if available
        bom_id = None
        if hasattr(context.get('form'), 'cleaned_data') and context['form'].cleaned_data:
            bom = context['form'].cleaned_data.get('bom')
            if bom:
                bom_id = bom.id
        elif self.request.POST:
            bom_id_str = self.request.POST.get('bom')
            if bom_id_str:
                try:
                    bom_id = int(bom_id_str)
                except (ValueError, TypeError):
                    pass
        
        # Create operations formset
        active_company_id = self.request.session.get('active_company_id')
        if self.request.POST:
            operations_formset = ProcessOperationFormSet(
                self.request.POST,
                prefix='operations',
                form_kwargs={'bom_id': bom_id, 'company_id': active_company_id},
            )
        else:
            operations_formset = ProcessOperationFormSet(
                prefix='operations',
                form_kwargs={'bom_id': bom_id, 'company_id': active_company_id},
            )
        
        context['operations_formset'] = operations_formset
        context['process_id'] = self.object.id if hasattr(self, 'object') and self.object else None
        
        # Add work lines to context for JavaScript
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            from production.models import WorkLine
            work_lines = WorkLine.objects.filter(
                company_id=active_company_id,
                is_enabled=1,
            ).order_by('name')
            context['work_lines'] = [
                {'id': wl.id, 'name': wl.name, 'public_code': wl.public_code}
                for wl in work_lines
            ]
        else:
            context['work_lines'] = []
        
        return context


class ProcessUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing process."""
    model = Process
    form_class = ProcessForm
    template_name = 'production/process_form.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return Process.objects.none()
        return Process.objects.filter(company_id=active_company_id)
    
    @transaction.atomic
    def form_valid(self, form: ProcessForm) -> HttpResponseRedirect:
        """Auto-set edited_by, finished_item, save M2M relationships and operations."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.edited_by = self.request.user
        # Set finished_item from BOM if changed
        bom = form.cleaned_data.get('bom')
        if bom:
            form.instance.finished_item = bom.finished_item
        
        # Save process
        response = super().form_valid(form)
        
        # Save Many-to-Many relationships
        form.save_m2m()
        
        # Get BOM ID for operations
        bom_id = bom.id if bom else (self.object.bom_id if self.object else None)
        
        # Handle operations formset
        operations_formset = ProcessOperationFormSet(
            self.request.POST,
            prefix='operations',
            form_kwargs={'bom_id': bom_id, 'company_id': active_company_id},
        )
        
        if operations_formset.is_valid():
            # Delete existing operations that are not in formset
            existing_operation_ids = set(
                ProcessOperation.objects.filter(process=self.object).values_list('id', flat=True)
            )
            
            # Save operations
            operations = []
            for operation_form in operations_formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if name or sequence_order:
                        # Check if this is an existing operation (by checking if we have an ID in form)
                        operation_id = self.request.POST.get(f'{operation_form.prefix}-id')
                        
                        if operation_id:
                            try:
                                operation = ProcessOperation.objects.get(
                                    id=int(operation_id),
                                    process=self.object,
                                )
                                # Update existing
                                for field in ['name', 'description', 'sequence_order', 
                                            'labor_minutes_per_unit', 'machine_minutes_per_unit', 'work_line', 'notes']:
                                    if field in operation_form.cleaned_data:
                                        setattr(operation, field, operation_form.cleaned_data[field])
                                operation.edited_by = self.request.user
                                operation.save()
                                operations.append(operation)
                                existing_operation_ids.discard(operation.id)
                            except (ProcessOperation.DoesNotExist, ValueError, TypeError):
                                # Create new
                                operation = operation_form.save(commit=False)
                                operation.process = self.object
                                operation.company_id = active_company_id
                                operation.created_by = self.request.user
                                operation.save()
                                operations.append(operation)
                        else:
                            # Create new
                            operation = operation_form.save(commit=False)
                            operation.process = self.object
                            operation.company_id = active_company_id
                            operation.created_by = self.request.user
                            operation.save()
                            operations.append(operation)
            
            # Delete operations that were removed
            if existing_operation_ids:
                ProcessOperation.objects.filter(
                    id__in=existing_operation_ids,
                    process=self.object,
                ).delete()
            
            # Now save materials for each operation
            operation_index = 0
            for operation_form in operations_formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if (name or sequence_order) and operation_index < len(operations):
                        operation = operations[operation_index]
                        
                        # Save materials manually from POST data
                        save_operation_materials_from_post(
                            self.request,
                            operation,
                            operation_index,
                            active_company_id,
                            bom_id,
                        )
                        
                        operation_index += 1
        else:
            # Show operations formset errors
            if operations_formset.non_form_errors():
                for error in operations_formset.non_form_errors():
                    messages.error(self.request, f"❌ {error}")
            for i, op_form in enumerate(operations_formset):
                if op_form.errors:
                    for field, errors in op_form.errors.items():
                        for error in errors:
                            field_label = op_form.fields[field].label if field in op_form.fields else field
                            messages.error(self.request, f"❌ {_('Operation')} {i + 1} - {field_label}: {error}")
        
        messages.success(self.request, _('Process updated successfully.'))
        return response
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form title, breadcrumbs, and operations formset to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Process')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': reverse_lazy('production:processes')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:processes')
        context['form_id'] = 'process-form'
        
        # Get BOM ID from form or object
        bom_id = None
        if self.object and self.object.bom_id:
            bom_id = self.object.bom_id
        elif hasattr(context.get('form'), 'cleaned_data') and context['form'].cleaned_data:
            bom = context['form'].cleaned_data.get('bom')
            if bom:
                bom_id = bom.id
        elif self.request.POST:
            bom_id_str = self.request.POST.get('bom')
            if bom_id_str:
                try:
                    bom_id = int(bom_id_str)
                except (ValueError, TypeError):
                    pass
        
        # Create operations formset
        active_company_id = self.request.session.get('active_company_id')
        if self.request.POST:
            operations_formset = ProcessOperationFormSet(
                self.request.POST,
                prefix='operations',
                form_kwargs={'bom_id': bom_id, 'company_id': active_company_id},
            )
            # POST request - no existing operations data needed
            context['existing_operations_data'] = None
            context['operation_id_to_index'] = {}
        else:
            # Load existing operations
            existing_operations = ProcessOperation.objects.filter(
                process=self.object,
                is_enabled=1,
            ).order_by('sequence_order', 'id')
            
            initial_data = []
            operation_id_to_index = {}
            for index, op in enumerate(existing_operations):
                initial_data.append({
                    'name': op.name,
                    'description': op.description,
                    'sequence_order': op.sequence_order,
                    'labor_minutes_per_unit': op.labor_minutes_per_unit,
                    'machine_minutes_per_unit': op.machine_minutes_per_unit,
                    'work_line': op.work_line_id,
                    'notes': op.notes,
                })
                operation_id_to_index[op.id] = index
            
            operations_formset = ProcessOperationFormSet(
                prefix='operations',
                form_kwargs={'bom_id': bom_id, 'company_id': self.object.company_id},
                initial=initial_data,
            )
            
            # Store existing operations and their materials for template
            existing_operations_data = []
            for op in existing_operations:
                materials = ProcessOperationMaterial.objects.filter(
                    operation=op,
                    is_enabled=1,
                ).select_related('bom_material', 'material_item').order_by('id')
                
                existing_operations_data.append({
                    'operation': op,
                    'materials': [
                        {
                            'id': mat.id,
                            'bom_material_id': mat.bom_material_id,
                            'quantity_used': str(mat.quantity_used),
                            'unit': mat.unit,
                        }
                        for mat in materials
                    ]
                })
            
            context['existing_operations_data'] = existing_operations_data
            context['operation_id_to_index'] = operation_id_to_index
        
        context['operations_formset'] = operations_formset
        context['process_id'] = self.object.id if hasattr(self, 'object') and self.object else None
        
        # Add work lines to context for JavaScript
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            from production.models import WorkLine
            work_lines = WorkLine.objects.filter(
                company_id=active_company_id,
                is_enabled=1,
            ).order_by('name')
            context['work_lines'] = [
                {'id': wl.id, 'name': wl.name, 'public_code': wl.public_code}
                for wl in work_lines
            ]
        else:
            context['work_lines'] = []
        
        return context


class ProcessDetailView(FeaturePermissionRequiredMixin, DetailView):
    """Detail view for viewing processes (read-only)."""
    model = Process
    template_name = 'production/process_detail.html'
    context_object_name = 'process'
    feature_code = 'production.processes'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return Process.objects.none()
        queryset = Process.objects.filter(company_id=active_company_id)
        queryset = queryset.select_related(
            'finished_item',
            'bom',
            'approved_by',
            'created_by',
            'edited_by',
        ).prefetch_related(
            'work_lines',
            'operations',
            'operations__operation_materials',
            'operations__operation_materials__bom_material',
        )
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('production:processes')
        context['edit_url'] = reverse_lazy('production:process_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'production.processes'
        return context


class ProcessDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a process."""
    model = Process
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return Process.objects.none()
        return Process.objects.filter(company_id=active_company_id).select_related('finished_item', 'bom').prefetch_related('work_lines')
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete process and show success message."""
        messages.success(self.request, _('Process deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Process')
        context['confirmation_message'] = _('Are you sure you want to delete this process?')
        
        object_details = [
            {'label': _('Code'), 'value': self.object.process_code},
        ]
        
        if self.object.finished_item:
            object_details.append({'label': _('Finished Item'), 'value': self.object.finished_item.name})
        
        if self.object.bom:
            object_details.append({'label': _('BOM'), 'value': self.object.bom.bom_code})
        
        object_details.append({'label': _('Revision'), 'value': str(self.object.revision)})
        
        if self.object.work_lines.exists():
            work_lines_text = ', '.join([wl.name for wl in self.object.work_lines.all()])
            object_details.append({'label': _('Work Lines'), 'value': work_lines_text})
        
        context['object_details'] = object_details
        context['cancel_url'] = reverse_lazy('production:processes')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': reverse_lazy('production:processes')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


"""
Process CRUD views for production module.
"""
from typing import Any, Dict, Optional, List
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseDetailView,
    BaseDeleteView,
    BaseFormsetCreateView,
    BaseFormsetUpdateView,
    EditLockProtectedMixin,
)
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


class ProcessListView(BaseListView):
    """List all processes for the active company."""
    model = Process
    template_name = 'production/processes.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.processes'
    required_action = 'view_own'
    active_module = 'production'
    default_status_filter = False
    default_order_by = ['finished_item__name', 'revision', 'sort_order']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['finished_item', 'bom', 'approved_by']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        prefetch = ['work_lines']
        
        # Try to prefetch operations if table exists
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'production_processoperation'
                    );
                """)
                table_exists = cursor.fetchone()[0]
            if table_exists:
                prefetch.extend([
                    'operations',
                    'operations__operation_materials',
                    'operations__operation_materials__bom_material',
                    'operations__operation_materials__material_item',
                    'operations__work_line',
                    'operations__work_line__warehouse',
                    'operations__work_line__personnel',
                    'operations__work_line__machines',
                ])
        except Exception:
            pass
        
        return prefetch
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Processes')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('production:process_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('+ Create Process')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:process_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:process_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:process_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Processes Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first process.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '⚙️'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = []  # Overridden in template
        return context


class ProcessCreateView(BaseFormsetCreateView):
    """Create a new process."""
    model = Process
    form_class = ProcessForm
    template_name = 'production/process_form.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'create'
    active_module = 'production'
    formset_class = ProcessOperationFormSet
    formset_prefix = 'operations'
    success_message = _('Process created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = {}
        company_id = self.request.session.get('active_company_id')
        bom_id = None
        
        # Get BOM ID from form if available
        if hasattr(self, 'form') and self.form and hasattr(self.form, 'cleaned_data') and self.form.cleaned_data:
            bom = self.form.cleaned_data.get('bom')
            if bom:
                bom_id = bom.id
        elif self.request.POST:
            bom_id_str = self.request.POST.get('bom')
            if bom_id_str:
                try:
                    bom_id = int(bom_id_str)
                except (ValueError, TypeError):
                    pass
        
        if company_id:
            kwargs['form_kwargs'] = {'bom_id': bom_id, 'company_id': company_id}
        return kwargs
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': reverse_lazy('production:processes')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:processes')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Process')
    
    def process_formset_instance(self, instance):
        """
        Process formset instance before saving.
        Sets process, company_id, created_by.
        """
        active_company_id = self.request.session.get('active_company_id')
        
        # Validate required fields
        if not instance.name and not instance.sequence_order:
            return None
        
        # Set additional fields
        instance.process = self.object
        instance.company_id = active_company_id
        instance.created_by = self.request.user
        
        return instance
    
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
        
        # Save process first (from BaseCreateView)
        self.object = form.save()
        
        # Save Many-to-Many relationships
        form.save_m2m()
        
        # Get BOM ID for operations
        bom_id = bom.id if bom else None
        
        # Get formset
        formset = self.formset_class(
            self.request.POST,
            instance=self.object,
            prefix=self.formset_prefix,
            **self.get_formset_kwargs()
        )
        
        if formset.is_valid():
            # Save operations and get saved instances
            operations = []
            for operation_form in formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if name or sequence_order:
                        operation = operation_form.save(commit=False)
                        operation = self.process_formset_instance(operation)
                        if operation:
                            operation.save()
                            operations.append(operation)
            
            # Save materials for each operation (custom nested logic)
            operation_index = 0
            for operation_form in formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if (name or sequence_order) and operation_index < len(operations):
                        operation = operations[operation_index]
                        
                        # Save materials manually from POST data (custom nested formset handling)
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
            if formset.non_form_errors():
                for error in formset.non_form_errors():
                    messages.error(self.request, f"❌ {error}")
            for i, op_form in enumerate(formset):
                if op_form.errors:
                    for field, errors in op_form.errors.items():
                        for error in errors:
                            field_label = op_form.fields[field].label if field in op_form.fields else field
                            messages.error(self.request, f"❌ {_('Operation')} {i + 1} - {field_label}: {error}")
            return self.form_invalid(form)
        
        messages.success(self.request, _('Process created successfully.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form title, breadcrumbs, and operations formset to context."""
        context = super().get_context_data(**kwargs)
        
        # Rename formset to operations_formset for template compatibility
        if 'formset' in context:
            context['operations_formset'] = context['formset']
        
        # Add work lines to context for JavaScript (for operations work_line field)
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
        
        context['process_id'] = self.object.id if hasattr(self, 'object') and self.object else None
        context['form_id'] = 'process-form'
        
        return context


class ProcessUpdateView(BaseFormsetUpdateView, EditLockProtectedMixin):
    """Update an existing process."""
    model = Process
    form_class = ProcessForm
    template_name = 'production/process_form.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'edit_own'
    active_module = 'production'
    formset_class = ProcessOperationFormSet
    formset_prefix = 'operations'
    success_message = _('Process updated successfully.')
    
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
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        bom_id = None
        if self.object and self.object.bom_id:
            bom_id = self.object.bom_id
        elif self.request.POST:
            bom_id_str = self.request.POST.get('bom')
            if bom_id_str:
                try:
                    bom_id = int(bom_id_str)
                except (ValueError, TypeError):
                    pass
        
        return {
            'form_kwargs': {
                'bom_id': bom_id,
                'company_id': self.object.company_id
            }
        }
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': reverse_lazy('production:processes')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:processes')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Process')
    
    def process_formset_instance(self, instance):
        """
        Process formset instance before saving.
        Sets process, company_id, edited_by.
        """
        # Validate required fields
        if not instance.name and not instance.sequence_order:
            return None
        
        # Set additional fields
        instance.process = self.object
        instance.edited_by = self.request.user
        
        return instance
    
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
        
        # Save process first
        self.object = form.save()
        
        # Save Many-to-Many relationships
        form.save_m2m()
        
        # Get BOM ID for operations
        bom_id = bom.id if bom else (self.object.bom_id if self.object else None)
        
        # Get formset (without 'instance' parameter because ProcessOperationFormSet doesn't accept it)
        formset = self.formset_class(
            self.request.POST,
            prefix=self.formset_prefix,
            **self.get_formset_kwargs()
        )
        
        if formset.is_valid():
            # Delete existing operations that are not in formset
            existing_operation_ids = set(
                ProcessOperation.objects.filter(process=self.object).values_list('id', flat=True)
            )
            
            # Save operations
            operations = []
            for operation_form in formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if name or sequence_order:
                        # Check if this is an existing operation
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
                                operation = self.process_formset_instance(operation)
                                if operation:
                                    operation.save()
                                    operations.append(operation)
                        else:
                            # Create new
                            operation = operation_form.save(commit=False)
                            operation = self.process_formset_instance(operation)
                            if operation:
                                operation.save()
                                operations.append(operation)
            
            # Delete operations that were removed
            if existing_operation_ids:
                ProcessOperation.objects.filter(
                    id__in=existing_operation_ids,
                    process=self.object,
                ).delete()
            
            # Save materials for each operation (custom nested logic)
            operation_index = 0
            for operation_form in formset:
                if operation_form.cleaned_data and not operation_form.cleaned_data.get('DELETE', False):
                    name = operation_form.cleaned_data.get('name')
                    sequence_order = operation_form.cleaned_data.get('sequence_order')
                    
                    if (name or sequence_order) and operation_index < len(operations):
                        operation = operations[operation_index]
                        
                        # Save materials manually from POST data (custom nested formset handling)
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
            if formset.non_form_errors():
                for error in formset.non_form_errors():
                    messages.error(self.request, f"❌ {error}")
            for i, op_form in enumerate(formset):
                if op_form.errors:
                    for field, errors in op_form.errors.items():
                        for error in errors:
                            field_label = op_form.fields[field].label if field in op_form.fields else field
                            messages.error(self.request, f"❌ {_('Operation')} {i + 1} - {field_label}: {error}")
            return self.form_invalid(form)
        
        messages.success(self.request, _('Process updated successfully.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form title, breadcrumbs, and operations formset to context."""
        # Don't call BaseFormsetUpdateView.get_context_data() because it tries to pass 'instance'
        # which ProcessOperationFormSet doesn't accept. Call BaseUpdateView instead.
        from django.views.generic.edit import UpdateView
        context = super(BaseFormsetUpdateView, self).get_context_data(**kwargs)
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
                    'requires_qc': bool(op.requires_qc == 1),
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


class ProcessDetailView(BaseDetailView):
    """Detail view for viewing processes (read-only)."""
    model = Process
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'production.processes'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
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
            'operations__operation_materials__material_item',
            'operations__work_line',
            'operations__work_line__warehouse',
            'operations__work_line__personnel',
            'operations__work_line__machines',
        )
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Process')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        process = self.object
        
        # Info banner
        info_banner = [
            {'label': _('Process Code'), 'value': process.process_code, 'type': 'code'},
        ]
        if process.revision:
            info_banner.append({'label': _('Revision'), 'value': process.revision})
        
        # Approval status badge
        if process.approval_status == 'approved':
            status_label = _('Approved')
            status_value = True
        elif process.approval_status == 'draft':
            status_label = _('Draft')
            status_value = False
        else:
            status_label = process.get_approval_status_display()
            status_value = False
        info_banner.append({
            'label': _('Status'),
            'value': status_value,
            'type': 'badge',
            'true_label': status_label if process.approval_status == 'approved' else None,
            'false_label': status_label,
        })
        
        if process.is_primary:
            info_banner.append({
                'label': _('Primary'),
                'value': True,
                'type': 'badge',
                'true_label': _('Yes'),
            })
        
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = info_banner
        
        # Basic Information section
        basic_fields = [
            {
                'label': _('Finished Item'),
                'value': f"{process.finished_item.name} ({process.finished_item.item_code})",
            },
        ]
        if process.bom:
            basic_fields.append({
                'label': _('BOM'),
                'value': f"{process.bom.bom_code} ({process.bom.version})",
            })
        if process.description:
            basic_fields.append({'label': _('Description'), 'value': process.description})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Work Lines section
        if process.work_lines.exists():
            work_lines_text = ', '.join([wl.name for wl in process.work_lines.all()])
            detail_sections.append({
                'title': _('Work Lines'),
                'fields': [
                    {'label': _('Work Lines'), 'value': work_lines_text},
                ],
            })
        
        # Operations section (detailed with materials, personnel, machines, warehouse)
        if process.operations.exists():
            operations_data = []
            for operation in process.operations.all().order_by('sequence_order', 'id'):
                operation_info = {
                    'operation': operation,
                    'materials': list(operation.operation_materials.all().select_related('bom_material', 'material_item')),
                    'personnel': list(operation.work_line.personnel.all()) if operation.work_line else [],
                    'machines': list(operation.work_line.machines.all()) if operation.work_line else [],
                    'warehouse': operation.work_line.warehouse if operation.work_line and operation.work_line.warehouse else None,
                }
                operations_data.append(operation_info)
            
            detail_sections.append({
                'title': _('Operations'),
                'type': 'operations_detail',
                'operations': operations_data,
            })
        
        # Approval Information section
        if process.approved_by:
            approval_fields = [
                {
                    'label': _('Approved By'),
                    'value': process.approved_by.get_full_name() or process.approved_by.username,
                },
            ]
            if process.approved_at:
                approval_fields.append({
                    'label': _('Approved At'),
                    'value': process.approved_at,
                })
            detail_sections.append({
                'title': _('Approval Information'),
                'fields': approval_fields,
            })
        
        # Notes section
        if process.notes:
            detail_sections.append({
                'title': _('Notes'),
                'fields': [
                    {'label': _('Notes'), 'value': process.notes},
                ],
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:processes')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:process_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class ProcessDeleteView(BaseDeleteView):
    """Delete a process."""
    model = Process
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Process deleted successfully.')
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('finished_item', 'bom').prefetch_related('work_lines')
        return queryset
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Process')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this process?')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        details = [
            {'label': _('Code'), 'value': self.object.process_code},
        ]
        
        if self.object.finished_item:
            details.append({'label': _('Finished Item'), 'value': self.object.finished_item.name})
        
        if self.object.bom:
            details.append({'label': _('BOM'), 'value': self.object.bom.bom_code})
        
        details.append({'label': _('Revision'), 'value': str(self.object.revision)})
        
        if self.object.work_lines.exists():
            work_lines_text = ', '.join([wl.name for wl in self.object.work_lines.all()])
            details.append({'label': _('Work Lines'), 'value': work_lines_text})
        
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Processes'), 'url': reverse_lazy('production:processes')},
            {'label': _('Delete'), 'url': None},
        ]


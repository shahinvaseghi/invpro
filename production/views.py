"""
Views for production module.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from .forms import BOMForm, BOMMaterialLineFormSet, MachineForm, PersonForm, WorkLineForm
from .models import BOM, BOMMaterial, Machine, Person, WorkLine


class PersonnelListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all personnel (Person objects) for the active company.
    """
    model = Person
    template_name = 'production/personnel.html'
    context_object_name = 'personnel'
    paginate_by = 50
    feature_code = 'production.personnel'
    
    def get_queryset(self):
        """Filter personnel by active company."""
        active_company_id = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Person.objects.none()
        
        return Person.objects.filter(
            company_id=active_company_id,
            is_enabled=1
        ).select_related('company').prefetch_related('company_units').order_by('public_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


class PersonCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        # Auto-set company and created_by
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Person created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create Person')
        return context


class PersonUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'edit_own'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form):
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Person updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit Person')
        return context


class PersonDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a person."""
    model = Person
    success_url = reverse_lazy('production:personnel')
    template_name = 'production/person_confirm_delete.html'
    feature_code = 'production.personnel'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Person deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


class MachineListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all machines for the active company.
    """
    model = Machine
    template_name = 'production/machines.html'
    context_object_name = 'machines'
    paginate_by = 50
    feature_code = 'production.machines'
    
    def get_queryset(self):
        """Filter machines by active company."""
        active_company_id = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Machine.objects.none()
        
        queryset = Machine.objects.filter(
            company_id=active_company_id,
            is_enabled=1
        ).select_related('company', 'work_center').order_by('public_code')
        
        # Filter by work center if provided
        work_center_id = self.request.GET.get('work_center')
        if work_center_id:
            queryset = queryset.filter(work_center_id=work_center_id)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        from .models import WorkCenter
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['work_centers'] = WorkCenter.objects.filter(company_id=active_company_id, is_enabled=1)
        return context


class MachineCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        # Auto-set company and created_by
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Machine created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create Machine')
        return context


class MachineUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'edit_own'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Machine.objects.none()
        return Machine.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form):
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Machine updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit Machine')
        return context


class MachineDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a machine."""
    model = Machine
    success_url = reverse_lazy('production:machines')
    template_name = 'production/machine_confirm_delete.html'
    feature_code = 'production.machines'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Machine.objects.none()
        return Machine.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Machine deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


# ============================================================================
# Transfer to Line Requests (درخواست انتقال به پای کار)
# ============================================================================

class TransferToLineRequestListView(LoginRequiredMixin, ListView):
    """
    List all transfer to line requests.
    Placeholder view - full implementation pending.
    """
    model = Machine  # Temporary placeholder model
    template_name = 'production/transfer_requests.html'
    context_object_name = 'requests'
    paginate_by = 50
    
    def get_queryset(self):
        """Return empty queryset for now."""
        return Machine.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['page_title'] = _('Transfer to Line Requests')
        return context


# ============================================================================
# Performance Records (سند عملکرد)
# ============================================================================

class PerformanceRecordListView(LoginRequiredMixin, ListView):
    """
    List all performance records.
    Placeholder view - full implementation pending.
    """
    model = Machine  # Temporary placeholder model
    template_name = 'production/performance_records.html'
    context_object_name = 'records'
    paginate_by = 50
    
    def get_queryset(self):
        """Return empty queryset for now."""
        return Machine.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['page_title'] = _('Performance Records')
        return context


# ============================================================================
# BOM (Bill of Materials) - فهرست مواد اولیه
# ============================================================================

class BOMListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all BOMs for the active company.
    """
    model = BOM
    template_name = 'production/bom_list.html'
    context_object_name = 'boms'
    paginate_by = 50
    feature_code = 'production.bom'
    
    def get_queryset(self):
        """Filter BOMs by active company."""
        active_company_id = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return BOM.objects.none()
        
        queryset = BOM.objects.filter(
            company_id=active_company_id,
            is_enabled=1
        ).select_related('finished_item', 'company').prefetch_related('materials').order_by(
            'finished_item__item_code', '-version'
        )
        
        # Filter by finished_item if provided
        finished_item_id = self.request.GET.get('finished_item')
        if finished_item_id:
            queryset = queryset.filter(finished_item_id=finished_item_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        
        # Get list of finished items for filter dropdown
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            from inventory.models import Item
            # Get unique finished items that have BOM records
            finished_items = BOM.objects.filter(
                company_id=active_company_id
            ).values_list('finished_item_id', 'finished_item__item_code', 'finished_item__name').distinct()
            context['finished_items'] = [
                {'id': item[0], 'code': item[1], 'name': item[2]} 
                for item in finished_items
            ]
        
        return context


class BOMCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new BOM with materials (multi-line)."""
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create BOM')
        
        company_id = self.request.session.get('active_company_id')
        
        if self.request.POST:
            # Create formset from POST data without instance (since object doesn't exist yet)
            context['formset'] = BOMMaterialLineFormSet(
                self.request.POST,
                prefix='materials',
                form_kwargs={'company_id': company_id}
            )
            
            # Show form errors if form is invalid
            form = context.get('form')
            if form and form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(self.request, f"❌ {error}")
                        else:
                            field_label = form.fields[field].label if field in form.fields else field
                            messages.error(self.request, f"❌ {field_label}: {error}")
        else:
            # Create empty formset with only 'extra' number of forms
            context['formset'] = BOMMaterialLineFormSet(
                queryset=BOMMaterial.objects.none(),
                prefix='materials',
                form_kwargs={'company_id': company_id}
            )
        return context
    
    def form_valid(self, form):
        # Auto-set company and created_by
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        # Set default is_enabled if not provided
        if not form.instance.is_enabled:
            form.instance.is_enabled = 1
        
        # Save BOM first
        try:
            self.object = form.save()
        except Exception as e:
            messages.error(self.request, f"Error saving BOM: {str(e)}")
            return self.form_invalid(form)
        
        # Now create formset with instance
        formset = BOMMaterialLineFormSet(
            self.request.POST,
            instance=self.object,
            prefix='materials',
            form_kwargs={'company_id': active_company_id}
        )
        
        # Validate formset
        is_valid = formset.is_valid()
        try:
            extra_forms = formset.extra_form_count() if hasattr(formset, 'extra_form_count') else (formset.total_form_count() - formset.initial_form_count())
        except AttributeError:
            extra_forms = formset.total_form_count() - formset.initial_form_count()
        
        if not is_valid:
            # Delete the BOM we just created since formset is invalid
            self.object.delete()
            # Recreate context with formset errors
            context = self.get_context_data(form=form)
            context['formset'] = formset  # Include formset with errors
            
            # Show formset errors prominently
            if formset.non_form_errors():
                for error in formset.non_form_errors():
                    messages.error(self.request, f"❌ {error}")
            
            # Show form errors for each form in formset
            has_errors = False
            for i, line_form in enumerate(formset):
                if line_form.errors:
                    has_errors = True
                    for field, errors in line_form.errors.items():
                        for error in errors:
                            field_label = line_form.fields[field].label if field in line_form.fields else field
                            messages.error(self.request, f"❌ ردیف {i + 1} - {field_label}: {error}")
            
            # If no specific errors shown, show generic message
            if not has_errors and not formset.non_form_errors():
                messages.error(self.request, _('Please fill in all required fields in the material lines.'))
            
            return self.render_to_response(context)
        
        # Save formset with line numbers
        
        # First, save the formset normally
        try:
            instances = formset.save(commit=False)
            
            # Now set additional fields and save each instance
            line_number = 1
            saved_count = 0
            for i, line_instance in enumerate(instances):
                
                # Validate required fields
                if not line_instance.material_item:
                    continue
                
                if not line_instance.unit:
                    continue
                
                # Set additional fields
                line_instance.bom = self.object
                line_instance.line_number = line_number
                line_instance.company_id = active_company_id
                line_instance.created_by = self.request.user
                
                # Auto-fill material_item_code
                if line_instance.material_item:
                    line_instance.material_item_code = line_instance.material_item.item_code
                
                # Set material_type if not set
                if not line_instance.material_type:
                    if line_instance.material_item and line_instance.material_item.type:
                        line_instance.material_type = line_instance.material_item.type
                    else:
                        messages.error(self.request, f"Material item {line_instance.material_item.item_code} has no type assigned.")
                        continue
                
                # Save the instance
                try:
                    line_instance.save()
                    saved_count += 1
                    line_number += 1
                except Exception as e:
                    import traceback
                    messages.error(self.request, f"Error saving material line {line_number}: {str(e)}")
            
            # Delete any forms marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()
            
            
        except Exception as e:
            import traceback
            messages.error(self.request, f"Error saving material lines: {str(e)}")
            # Delete the BOM we created
            self.object.delete()
            context = self.get_context_data(form=form)
            context['formset'] = formset
            return self.render_to_response(context)
        
        if saved_count == 0:
            messages.warning(self.request, _('BOM created but no material lines were saved. Please check the form data.'))
        else:
            messages.success(self.request, _('BOM created successfully with %(count)s material line(s).') % {'count': saved_count})
        
        return redirect(self.success_url)


class BOMUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing BOM."""
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    required_action = 'edit_own'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return BOM.objects.none()
        return BOM.objects.filter(company_id=active_company_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit BOM')
        
        if self.request.POST:
            context['formset'] = BOMMaterialLineFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': self.object.company_id}
            )
        else:
            context['formset'] = BOMMaterialLineFormSet(
                instance=self.object,
                form_kwargs={'company_id': self.object.company_id}
            )
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        
        # Validate formset
        is_valid = formset.is_valid()
        
        if not is_valid:
            # Show formset errors prominently
            if formset.non_form_errors():
                for error in formset.non_form_errors():
                    messages.error(self.request, f"❌ {error}")
            
            # Show form errors for each form in formset
            has_errors = False
            for i, line_form in enumerate(formset):
                if line_form.errors:
                    has_errors = True
                    for field, errors in line_form.errors.items():
                        for error in errors:
                            field_label = line_form.fields[field].label if field in line_form.fields else field
                            messages.error(self.request, f"❌ ردیف {i + 1} - {field_label}: {error}")
            
            return self.form_invalid(form)
        
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        
        # Save BOM
        try:
            self.object = form.save()
        except Exception as e:
            messages.error(self.request, f"Error updating BOM: {str(e)}")
            return self.form_invalid(form)
        
        # Save formset with line numbers
        
        try:
            instances = formset.save(commit=False)
            
            # Now set additional fields and save each instance
            line_number = 1
            saved_count = 0
            for i, line_instance in enumerate(instances):
                
                # Validate required fields
                if not line_instance.material_item:
                    continue
                
                if not line_instance.unit:
                    continue
                
                # Set additional fields
                line_instance.bom = self.object
                line_instance.line_number = line_number
                line_instance.edited_by = self.request.user
                
                # Auto-fill material_item_code
                if line_instance.material_item:
                    line_instance.material_item_code = line_instance.material_item.item_code
                
                # Set material_type if not set
                if not line_instance.material_type:
                    if line_instance.material_item and line_instance.material_item.type:
                        line_instance.material_type = line_instance.material_item.type
                    else:
                        messages.error(self.request, f"Material item {line_instance.material_item.item_code} has no type assigned.")
                        continue
                
                # Save the instance
                try:
                    line_instance.save()
                    saved_count += 1
                    line_number += 1
                except Exception as e:
                    import traceback
                    messages.error(self.request, f"Error saving material line {line_number}: {str(e)}")
            
            # Delete marked lines
            for deleted_obj in formset.deleted_objects:
                deleted_obj.delete()
            
            
        except Exception as e:
            import traceback
            messages.error(self.request, f"Error saving material lines: {str(e)}")
            return self.form_invalid(form)
        
        messages.success(self.request, _('BOM updated successfully.'))
        return super().form_valid(form)


class BOMDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a BOM."""
    model = BOM
    success_url = reverse_lazy('production:bom_list')
    template_name = 'production/bom_confirm_delete.html'
    feature_code = 'production.bom'
    required_action = 'delete_own'

    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return BOM.objects.none()
        return BOM.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('BOM deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


# ============================================================================
# Work Line Views
# ============================================================================

class WorkLineListView(FeaturePermissionRequiredMixin, ListView):
    """List all work lines for the active company."""
    model = WorkLine
    template_name = 'production/work_lines.html'
    context_object_name = 'work_lines'
    paginate_by = 50
    feature_code = 'production.work_lines'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter work lines by active company."""
        active_company_id = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return WorkLine.objects.none()
        
        queryset = WorkLine.objects.filter(
            company_id=active_company_id
        )
        
        # Try to select_related warehouse if inventory module is installed
        try:
            queryset = queryset.select_related('warehouse')
        except:
            pass
        
        queryset = queryset.prefetch_related('personnel', 'machines')
        
        return queryset.order_by('warehouse__name', 'sort_order', 'public_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


class WorkLineCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new work line."""
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'create'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        messages.success(self.request, _('Work line created successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create Work Line')
        return context


class WorkLineUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing work line."""
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'edit_own'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return WorkLine.objects.none()
        return WorkLine.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        messages.success(self.request, _('Work line updated successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit Work Line')
        return context


class WorkLineDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a work line."""
    model = WorkLine
    template_name = 'production/work_line_confirm_delete.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return WorkLine.objects.none()
        return WorkLine.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Work line deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context

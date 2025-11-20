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
from .forms import BOMForm, BOMMaterialLineFormSet, MachineForm, PersonForm
from .models import BOM, BOMMaterial, Machine, Person


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
        import logging
        logger = logging.getLogger(__name__)
        
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create BOM')
        
        company_id = self.request.session.get('active_company_id')
        
        if self.request.POST:
            logger.info("=" * 50)
            logger.info("BOM CREATE - POST request received")
            logger.info(f"POST data: {dict(list(self.request.POST.items())[:30])}")  # First 30 items
            
            # Create formset from POST data without instance (since object doesn't exist yet)
            context['formset'] = BOMMaterialLineFormSet(
                self.request.POST,
                prefix='materials',
                form_kwargs={'company_id': company_id}
            )
            
            # Show form errors if form is invalid
            form = context.get('form')
            if form:
                logger.info(f"Form is_valid: {form.is_valid()}")
                if form.errors:
                    logger.error("=" * 50)
                    logger.error("FORM VALIDATION FAILED")
                    logger.error(f"Form errors: {form.errors}")
                    for field, errors in form.errors.items():
                        for error in errors:
                            if field == '__all__':
                                messages.error(self.request, f"❌ {error}")
                            else:
                                field_label = form.fields[field].label if field in form.fields else field
                                messages.error(self.request, f"❌ {field_label}: {error}")
                                logger.error(f"  Field '{field}' ({field_label}): {error}")
        else:
            # Create empty formset with only 'extra' number of forms
            context['formset'] = BOMMaterialLineFormSet(
                queryset=BOMMaterial.objects.none(),
                prefix='materials',
                form_kwargs={'company_id': company_id}
            )
        return context
    
    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("=" * 50)
        logger.info("BOM CREATE - form_valid called")
        logger.info(f"Form data: {form.cleaned_data}")
        logger.info(f"Form errors: {form.errors}")
        
        # Auto-set company and created_by
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            logger.error("No active company ID in session")
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        logger.info(f"Active company ID: {active_company_id}")
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        # Set default is_enabled if not provided
        if not form.instance.is_enabled:
            form.instance.is_enabled = 1
            logger.info("Set default is_enabled=1")
        
        # Save BOM first
        try:
            self.object = form.save()
            logger.info(f"BOM saved successfully: {self.object.bom_code}")
        except Exception as e:
            logger.error(f"Error saving BOM: {str(e)}")
            messages.error(self.request, f"Error saving BOM: {str(e)}")
            return self.form_invalid(form)
        
        # Now create formset with instance
        formset = BOMMaterialLineFormSet(
            self.request.POST,
            instance=self.object,
            prefix='materials',
            form_kwargs={'company_id': active_company_id}
        )
        
        logger.info(f"Formset created with {len(formset.forms)} forms")
        logger.info(f"POST data keys: {list(self.request.POST.keys())[:20]}...")  # First 20 keys
        
        # Log all POST data for materials
        material_keys = [k for k in self.request.POST.keys() if k.startswith('materials-')]
        logger.info(f"Material-related POST keys: {len(material_keys)} keys")
        for key in material_keys[:20]:  # First 20 keys
            value = self.request.POST.get(key)
            # Log unit values prominently
            if 'unit' in key.lower():
                logger.info(f"  🔵 {key}: {value}")
            else:
                logger.info(f"  {key}: {value}")
        
        # Validate formset
        is_valid = formset.is_valid()
        logger.info(f"Formset is_valid: {is_valid}")
        logger.info(f"Formset total_forms: {formset.total_form_count()}")
        logger.info(f"Formset initial_forms: {formset.initial_form_count()}")
        # extra_form_count() may not exist for all formset types
        try:
            extra_forms = formset.extra_form_count() if hasattr(formset, 'extra_form_count') else (formset.total_form_count() - formset.initial_form_count())
            logger.info(f"Formset extra_forms: {extra_forms}")
        except AttributeError:
            extra_forms = formset.total_form_count() - formset.initial_form_count()
            logger.info(f"Formset extra_forms (calculated): {extra_forms}")
        
        if not is_valid:
            logger.error("=" * 50)
            logger.error("FORMSET VALIDATION FAILED")
            logger.error(f"Formset errors: {formset.errors}")
            logger.error(f"Formset non_form_errors: {formset.non_form_errors()}")
            
            for i, line_form in enumerate(formset):
                if line_form.errors:
                    logger.error(f"Line {i+1} errors: {line_form.errors}")
                if hasattr(line_form, 'cleaned_data') and line_form.cleaned_data:
                    logger.info(f"Line {i+1} cleaned_data: {line_form.cleaned_data}")
                else:
                    logger.warning(f"Line {i+1} has no cleaned_data")
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
        logger.info("=" * 50)
        logger.info("SAVING MATERIAL LINES")
        logger.info(f"Total forms in formset: {len(formset.forms)}")
        logger.info(f"Formset instance: {formset.instance}")
        logger.info(f"Formset instance ID: {formset.instance.id if formset.instance else 'None'}")
        
        # First, save the formset normally
        try:
            instances = formset.save(commit=False)
            logger.info(f"Formset.save(commit=False) returned {len(instances)} instances")
            
            # Now set additional fields and save each instance
            line_number = 1
            saved_count = 0
            for i, line_instance in enumerate(instances):
                logger.info(f"Processing instance {i+1}:")
                logger.info(f"  Instance: {line_instance}")
                logger.info(f"  material_item: {line_instance.material_item} (ID: {line_instance.material_item.id if line_instance.material_item else 'None'})")
                logger.info(f"  material_type: {line_instance.material_type} (ID: {line_instance.material_type.id if line_instance.material_type else 'None'})")
                logger.info(f"  unit: {line_instance.unit}")
                logger.info(f"  quantity_per_unit: {line_instance.quantity_per_unit}")
                
                # Validate required fields
                if not line_instance.material_item:
                    logger.error(f"  ❌ material_item is None, skipping line {line_number}")
                    continue
                
                if not line_instance.unit:
                    logger.error(f"  ❌ unit is None, skipping line {line_number}")
                    continue
                
                # Set additional fields
                line_instance.bom = self.object
                line_instance.line_number = line_number
                line_instance.company_id = active_company_id
                line_instance.created_by = self.request.user
                
                # Auto-fill material_item_code
                if line_instance.material_item:
                    line_instance.material_item_code = line_instance.material_item.item_code
                    logger.info(f"  material_item_code set to: {line_instance.material_item_code}")
                
                # Set material_type if not set
                if not line_instance.material_type:
                    if line_instance.material_item and line_instance.material_item.type:
                        line_instance.material_type = line_instance.material_item.type
                        logger.info(f"  ✅ material_type auto-set to: {line_instance.material_type.id} ({line_instance.material_type.name})")
                    else:
                        logger.error(f"  ❌ Cannot set material_type: material_item has no type!")
                        messages.error(self.request, f"Material item {line_instance.material_item.item_code} has no type assigned.")
                        continue
                
                # Save the instance
                try:
                    line_instance.save()
                    logger.info(f"  ✅ Line {line_number} saved successfully (ID: {line_instance.id})")
                    saved_count += 1
                    line_number += 1
                except Exception as e:
                    logger.error(f"  ❌ Error saving line {line_number}: {str(e)}")
                    logger.error(f"  Exception type: {type(e).__name__}")
                    import traceback
                    logger.error(f"  Traceback: {traceback.format_exc()}")
                    messages.error(self.request, f"Error saving material line {line_number}: {str(e)}")
            
            # Delete any forms marked for deletion
            for obj in formset.deleted_objects:
                logger.info(f"Deleting material line: {obj}")
                obj.delete()
            
            logger.info(f"Total material lines saved: {saved_count}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ Error in formset.save(): {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            messages.error(self.request, f"Error saving material lines: {str(e)}")
            # Delete the BOM we created
            self.object.delete()
            context = self.get_context_data(form=form)
            context['formset'] = formset
            return self.render_to_response(context)
        
        if saved_count == 0:
            logger.error("⚠️  WARNING: No material lines were saved!")
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
        import logging
        logger = logging.getLogger(__name__)
        logger.info("=" * 50)
        logger.info("BOM UPDATE - form_valid called")
        logger.info(f"Form data: {form.cleaned_data}")
        
        context = self.get_context_data()
        formset = context['formset']
        
        logger.info(f"Formset created with {len(formset.forms)} forms")
        logger.info(f"Formset instance: {formset.instance}")
        logger.info(f"Formset instance ID: {formset.instance.id if formset.instance else 'None'}")
        
        # Validate formset
        is_valid = formset.is_valid()
        logger.info(f"Formset is_valid: {is_valid}")
        
        if not is_valid:
            logger.error("=" * 50)
            logger.error("FORMSET VALIDATION FAILED")
            logger.error(f"Formset errors: {formset.errors}")
            logger.error(f"Formset non_form_errors: {formset.non_form_errors()}")
            
            for i, line_form in enumerate(formset):
                if line_form.errors:
                    logger.error(f"Line {i+1} errors: {line_form.errors}")
                if hasattr(line_form, 'cleaned_data') and line_form.cleaned_data:
                    logger.info(f"Line {i+1} cleaned_data: {line_form.cleaned_data}")
                else:
                    logger.warning(f"Line {i+1} has no cleaned_data")
            
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
            logger.info(f"BOM updated successfully: {self.object.bom_code}")
        except Exception as e:
            logger.error(f"Error updating BOM: {str(e)}")
            messages.error(self.request, f"Error updating BOM: {str(e)}")
            return self.form_invalid(form)
        
        # Save formset with line numbers
        logger.info("=" * 50)
        logger.info("SAVING MATERIAL LINES")
        logger.info(f"Total forms in formset: {len(formset.forms)}")
        
        try:
            instances = formset.save(commit=False)
            logger.info(f"Formset.save(commit=False) returned {len(instances)} instances")
            
            # Now set additional fields and save each instance
            line_number = 1
            saved_count = 0
            for i, line_instance in enumerate(instances):
                logger.info(f"Processing instance {i+1}:")
                logger.info(f"  Instance: {line_instance}")
                logger.info(f"  material_item: {line_instance.material_item} (ID: {line_instance.material_item.id if line_instance.material_item else 'None'})")
                logger.info(f"  material_type: {line_instance.material_type} (ID: {line_instance.material_type.id if line_instance.material_type else 'None'})")
                logger.info(f"  unit: {line_instance.unit}")
                logger.info(f"  quantity_per_unit: {line_instance.quantity_per_unit}")
                
                # Validate required fields
                if not line_instance.material_item:
                    logger.error(f"  ❌ material_item is None, skipping line {line_number}")
                    continue
                
                if not line_instance.unit:
                    logger.error(f"  ❌ unit is None, skipping line {line_number}")
                    continue
                
                # Set additional fields
                line_instance.bom = self.object
                line_instance.line_number = line_number
                line_instance.edited_by = self.request.user
                
                # Auto-fill material_item_code
                if line_instance.material_item:
                    line_instance.material_item_code = line_instance.material_item.item_code
                    logger.info(f"  material_item_code set to: {line_instance.material_item_code}")
                
                # Set material_type if not set
                if not line_instance.material_type:
                    if line_instance.material_item and line_instance.material_item.type:
                        line_instance.material_type = line_instance.material_item.type
                        logger.info(f"  ✅ material_type auto-set to: {line_instance.material_type.id} ({line_instance.material_type.name})")
                    else:
                        logger.error(f"  ❌ Cannot set material_type: material_item has no type!")
                        messages.error(self.request, f"Material item {line_instance.material_item.item_code} has no type assigned.")
                        continue
                
                # Save the instance
                try:
                    line_instance.save()
                    logger.info(f"  ✅ Line {line_number} saved successfully (ID: {line_instance.id})")
                    saved_count += 1
                    line_number += 1
                except Exception as e:
                    logger.error(f"  ❌ Error saving line {line_number}: {str(e)}")
                    logger.error(f"  Exception type: {type(e).__name__}")
                    import traceback
                    logger.error(f"  Traceback: {traceback.format_exc()}")
                    messages.error(self.request, f"Error saving material line {line_number}: {str(e)}")
            
            # Delete marked lines
            for deleted_obj in formset.deleted_objects:
                logger.info(f"Deleting material line: {deleted_obj}")
                deleted_obj.delete()
            
            logger.info(f"Total material lines saved: {saved_count}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"❌ Error saving formset: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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

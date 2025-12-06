"""
BOM (Bill of Materials) CRUD views for production module.
"""
from typing import Any, Dict, Optional, List
from django.contrib import messages
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseDetailView,
    BaseDeleteView,
    BaseNestedFormsetCreateView,
    BaseNestedFormsetUpdateView,
    EditLockProtectedMixin,
)
from production.forms import BOMForm, BOMMaterialLineFormSet, BOMMaterialAlternativeFormSet
from production.models import BOM, BOMMaterial


class BOMListView(BaseListView):
    """List all BOMs for the active company."""
    model = BOM
    template_name = 'production/bom_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.bom'
    active_module = 'production'
    default_status_filter = False
    default_order_by = ['finished_item__item_code', '-version']
    
    def get_base_queryset(self):
        """Get base queryset with is_enabled filter."""
        return self.model.objects.filter(is_enabled=1)
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['finished_item', 'company']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['materials']
    
    def apply_custom_filters(self, queryset):
        """Apply custom filters (finished_item)."""
        finished_item_id = self.request.GET.get('finished_item')
        if finished_item_id:
            queryset = queryset.filter(finished_item_id=finished_item_id)
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('BOM (Bill of Materials)')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('BOM'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('production:bom_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create BOM')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:bom_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:bom_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:bom_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No BOMs Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by defining the materials needed for your products.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📋'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['print_enabled'] = True
        
        # Get list of finished items for filter dropdown
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if active_company_id:
            # Get unique finished items that have BOM records
            finished_items = BOM.objects.filter(
                company_id=active_company_id
            ).values_list('finished_item_id', 'finished_item__item_code', 'finished_item__name').distinct()
            context['finished_items'] = [
                {'id': item[0], 'code': item[1], 'name': item[2]} 
                for item in finished_items
            ]
        
        return context


class BOMCreateView(BaseNestedFormsetCreateView):
    """Create a new BOM with materials (multi-line)."""
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    required_action = 'create'
    active_module = 'production'
    formset_class = BOMMaterialLineFormSet
    formset_prefix = 'materials'
    nested_formset_class = BOMMaterialAlternativeFormSet
    nested_formset_prefix_template = 'alternatives_{parent_pk}'
    success_message = _('BOM created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = {}
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['form_kwargs'] = {'company_id': company_id}
        return kwargs
    
    def get_nested_formset_kwargs(self, parent_instance) -> Dict[str, Any]:
        """Return kwargs for nested formset."""
        active_company_id = self.request.session.get('active_company_id')
        return {
            'form_kwargs': {
                'company_id': active_company_id,
                'bom_material_id': parent_instance.pk
            }
        }
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('BOM'), 'url': reverse_lazy('production:bom_list')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:bom_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create BOM')
    
    def process_formset_instance(self, instance):
        """
        Process formset instance before saving.
        Sets line_number, company_id, created_by, and auto-fills fields.
        """
        active_company_id = self.request.session.get('active_company_id')
        
        # Validate required fields
        if not instance.material_item or not instance.unit:
            return None
        
        # Initialize line_number counter if not exists
        if not hasattr(self, '_line_number'):
            self._line_number = 1
        
        # Set additional fields
        instance.bom = self.object
        instance.line_number = self._line_number
        instance.company_id = active_company_id
        instance.created_by = self.request.user
        
        # Auto-fill material_item_code
        if instance.material_item:
            instance.material_item_code = instance.material_item.item_code
        
        # Set material_type if not set
        if not instance.material_type:
            if instance.material_item and instance.material_item.type:
                instance.material_type = instance.material_item.type
            else:
                messages.error(
                    self.request,
                    _('Material item {item_code} has no type assigned.').format(
                        item_code=instance.material_item.item_code
                    )
                )
                return None
        
        # Increment line number for next instance
        self._line_number += 1
        
        return instance
    
    def form_valid(self, form: BOMForm) -> HttpResponseRedirect:
        """Save BOM with custom logic."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        # Set default is_enabled if not provided
        if not form.instance.is_enabled:
            form.instance.is_enabled = 1
        
        # Initialize line number counter
        self._line_number = 1
        
        # Use parent form_valid which handles formset and nested formsets
        response = super().form_valid(form)
        
        # Count saved instances for success message
        saved_count = self.object.materials.count()
        if saved_count == 0:
            messages.warning(self.request, _('BOM created but no material lines were saved. Please check the form data.'))
        else:
            messages.success(
                self.request,
                _('BOM created successfully with {count} material line(s).').format(count=saved_count)
            )
        
        return response


class BOMUpdateView(BaseNestedFormsetUpdateView, EditLockProtectedMixin):
    """Update an existing BOM."""
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
    required_action = 'edit_own'
    active_module = 'production'
    formset_class = BOMMaterialLineFormSet
    formset_prefix = 'materials'
    nested_formset_class = BOMMaterialAlternativeFormSet
    nested_formset_prefix_template = 'alternatives_{parent_pk}'
    success_message = _('BOM updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return BOM.objects.none()
        return BOM.objects.filter(company_id=active_company_id)
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        return {
            'form_kwargs': {'company_id': self.object.company_id}
        }
    
    def get_nested_formset_kwargs(self, parent_instance) -> Dict[str, Any]:
        """Return kwargs for nested formset."""
        return {
            'form_kwargs': {
                'company_id': self.object.company_id,
                'bom_material_id': parent_instance.pk
            }
        }
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('BOM'), 'url': reverse_lazy('production:bom_list')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:bom_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit BOM')
    
    def process_formset_instance(self, instance):
        """
        Process formset instance before saving.
        Sets line_number, edited_by, and auto-fills fields.
        """
        # Validate required fields
        if not instance.material_item or not instance.unit:
            return None
        
        # Initialize line_number counter if not exists
        if not hasattr(self, '_line_number'):
            # Get max line_number from existing materials
            existing_max = self.object.materials.aggregate(
                max_line=models.Max('line_number')
            )['max_line'] or 0
            self._line_number = existing_max + 1
        
        # Set additional fields
        instance.bom = self.object
        instance.line_number = self._line_number
        instance.edited_by = self.request.user
        
        # Auto-fill material_item_code
        if instance.material_item:
            instance.material_item_code = instance.material_item.item_code
        
        # Set material_type if not set
        if not instance.material_type:
            if instance.material_item and instance.material_item.type:
                instance.material_type = instance.material_item.type
            else:
                messages.error(
                    self.request,
                    _('Material item {item_code} has no type assigned.').format(
                        item_code=instance.material_item.item_code
                    )
                )
                return None
        
        # Increment line number for next instance
        self._line_number += 1
        
        return instance
    
    def form_valid(self, form: BOMForm) -> HttpResponseRedirect:
        """Save BOM with custom logic."""
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        
        # Initialize line number counter
        self._line_number = 1
        
        # Use parent form_valid which handles formset and nested formsets
        response = super().form_valid(form)
        
        # Count saved instances for success message
        saved_count = self.object.materials.count()
        if saved_count == 0:
            messages.warning(self.request, _('BOM updated but no material lines were saved. Please check the form data.'))
        else:
            messages.success(
                self.request,
                _('BOM updated successfully with {count} material line(s).').format(count=saved_count)
            )
        
        return response


class BOMDetailView(BaseDetailView):
    """Detail view for viewing BOMs (read-only)."""
    model = BOM
    template_name = 'production/bom_detail.html'
    context_object_name = 'bom'
    feature_code = 'production.bom'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'finished_item',
            'created_by',
            'edited_by',
        ).prefetch_related('materials__material_item', 'materials__material_type')
        return queryset
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:bom_list')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:bom_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class BOMDeleteView(BaseDeleteView):
    """Delete a BOM."""
    model = BOM
    success_url = reverse_lazy('production:bom_list')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'production.bom'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('BOM deleted successfully.')
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete BOM')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this BOM?')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        details = [
            {'label': _('BOM Code'), 'value': f'<code>{self.object.bom_code}</code>'},
            {'label': _('Finished Product'), 'value': f'{self.object.finished_item.item_code} - {self.object.finished_item.name}'},
            {'label': _('Version'), 'value': str(self.object.version)},
        ]
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('BOM'), 'url': reverse_lazy('production:bom_list')},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        if self.object.materials.exists():
            context['warning_message'] = _('This BOM has {count} material line(s). They will also be deleted.').format(
                count=self.object.materials.count()
            )
        return context


"""
Stocktaking views for inventory module.

This module contains views for:
- Stocktaking Deficit
- Stocktaking Surplus
- Stocktaking Records
"""
from typing import Dict, Any, Optional
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
import json

from .base import InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, LineFormsetMixin
from shared.views.base import EditLockProtectedMixin
from .receipts import DocumentDeleteViewBase
from .. import models
from .. import forms


# ============================================================================
# Stocktaking Form Mixin
# ============================================================================

class StocktakingFormMixin(InventoryBaseView):
    """Shared helpers for stocktaking create/update views."""
    template_name = 'inventory/receipt_form.html'  # Use receipt_form.html for multi-line support
    form_title = ''
    list_url_name = ''
    lock_url_name = ''

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Pass company_id and user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        kwargs['user'] = self.request.user  # Pass current user to form for permission checks
        return kwargs

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration. Override in subclasses."""
        return []

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form context for receipt_form.html template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        context['list_url'] = reverse_lazy(self.list_url_name)
        context['is_edit'] = bool(getattr(self, 'object', None))
        
        # Create fieldsets for receipt_form.html template
        form = context.get('form')
        if form:
            fieldsets = []
            used_fields = []
            
            # Document information section
            doc_fields = []
            for field_name in ['stocktaking_session_id']:
                if field_name in form.fields:
                    doc_fields.append(form[field_name])
                    used_fields.append(field_name)
            if doc_fields:
                fieldsets.append((_('اطلاعات سند'), doc_fields))
            
            # Add any remaining visible fields
            remaining_fields = []
            hidden_field_names = [f.name for f in form.hidden_fields()]
            for field_name, field in form.fields.items():
                if field_name not in used_fields and field_name not in hidden_field_names:
                    remaining_fields.append(form[field_name])
            if remaining_fields:
                fieldsets.append((_('سایر اطلاعات'), remaining_fields))
            
            context['fieldsets'] = fieldsets
            context['used_fields'] = used_fields
        
        # Add item filter data for search bar
        company_id = self.request.session.get('active_company_id')
        if company_id:
            context['item_types'] = models.ItemType.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by('name')
            context['item_categories'] = models.ItemCategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by('name')
            context['item_subcategories'] = models.ItemSubcategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by('name')
        else:
            context['item_types'] = []
            context['item_categories'] = []
            context['item_subcategories'] = []

        instance = getattr(self, 'object', None)
        context['document_instance'] = instance
        if instance and getattr(instance, 'pk', None):
            is_locked = bool(getattr(instance, 'is_locked', 0))
            context['document_is_locked'] = is_locked
            if not is_locked and getattr(self, 'lock_url_name', None):
                context['lock_url'] = reverse(self.lock_url_name, args=[instance.pk])
            else:
                context['lock_url'] = None
        else:
            context['document_is_locked'] = False
            context['lock_url'] = None

        return context


# ============================================================================
# Stocktaking Deficit Views
# ============================================================================

class StocktakingDeficitListView(InventoryBaseView, ListView):
    """List view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    template_name = 'inventory/stocktaking_deficit.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.deficit', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by')
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        # Generic list context
        context['page_title'] = _('Deficit Records')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:stocktaking_deficit_create')
        context['create_button_text'] = _('Create Deficit Record')
        context['show_actions'] = True
        
        # Stocktaking Deficit-specific context
        context['edit_url_name'] = 'inventory:stocktaking_deficit_edit'
        context['delete_url_name'] = 'inventory:stocktaking_deficit_delete'
        context['lock_url_name'] = 'inventory:stocktaking_deficit_lock'
        context['empty_state_title'] = _('No Deficit Records Found')
        context['empty_state_message'] = _('Deficit records are created during stocktaking when counted quantity is less than expected.')
        context['empty_state_icon'] = '📉'
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.deficit')
        
        # User for permission checks in template
        context['user'] = self.request.user
        
        return context


class StocktakingDeficitCreateView(LineFormsetMixin, StocktakingFormMixin, CreateView):
    """Create view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    formset_class = forms.StocktakingDeficitLineFormSet
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    form_title = _('ایجاد سند کسری انبارگردانی')
    list_url_name = 'inventory:stocktaking_deficit'
    lock_url_name = 'inventory:stocktaking_deficit_lock'

    def form_valid(self, form):
        """Save document and line formset."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            # If formset is invalid, delete the main object and re-render
            self.object.delete()
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if we have at least one valid line before saving
        valid_lines = []
        for form in lines_formset.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                valid_lines.append(form)
        
        if not valid_lines:
            self.object.delete()
            form.add_error(None, _('حداقل یک ردیف کالا الزامی است.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        messages.success(self.request, _('سند کسری انبارگردانی با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())


class StocktakingDeficitUpdateView(EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    """Update view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    formset_class = forms.StocktakingDeficitLineFormSet
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    form_title = _('ویرایش سند کسری انبارگردانی')
    list_url_name = 'inventory:stocktaking_deficit'
    lock_url_name = 'inventory:stocktaking_deficit_lock'
    lock_redirect_url_name = 'inventory:stocktaking_deficit'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.deficit', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by')
        return queryset

    def form_valid(self, form):
        """Save document and line formset."""
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        messages.success(self.request, _('سند کسری انبارگردانی با موفقیت بروزرسانی شد.'))
        return HttpResponseRedirect(self.get_success_url())


class StocktakingDeficitDeleteView(DocumentDeleteViewBase):
    """Delete view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    feature_code = 'inventory.stocktaking.deficit'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('سند کسری موجودی با موفقیت حذف شد.')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Deficit Record')
        context['confirmation_message'] = _('Do you really want to delete this deficit record?')
        context['object_details'] = [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:stocktaking_deficit')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Deficit Records'), 'url': reverse_lazy('inventory:stocktaking_deficit')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


class StocktakingDeficitLockView(DocumentLockView):
    """Lock view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    success_url_name = 'inventory:stocktaking_deficit'
    success_message = _('سند کسری شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Stocktaking Surplus Views
# ============================================================================

class StocktakingSurplusListView(InventoryBaseView, ListView):
    """List view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    template_name = 'inventory/stocktaking_surplus.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.surplus', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by')
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        # Generic list context
        context['page_title'] = _('Surplus Records')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:stocktaking_surplus_create')
        context['create_button_text'] = _('Create Surplus Record')
        context['show_actions'] = True
        
        # Stocktaking Surplus-specific context
        context['edit_url_name'] = 'inventory:stocktaking_surplus_edit'
        context['delete_url_name'] = 'inventory:stocktaking_surplus_delete'
        context['lock_url_name'] = 'inventory:stocktaking_surplus_lock'
        context['empty_state_title'] = _('No Surplus Records Found')
        context['empty_state_message'] = _('Surplus records are created during stocktaking when counted quantity is more than expected.')
        context['empty_state_icon'] = '📈'
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.surplus')
        
        # User for permission checks in template
        context['user'] = self.request.user
        
        return context


class StocktakingSurplusCreateView(LineFormsetMixin, StocktakingFormMixin, CreateView):
    """Create view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    formset_class = forms.StocktakingSurplusLineFormSet
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    form_title = _('ایجاد سند مازاد انبارگردانی')
    list_url_name = 'inventory:stocktaking_surplus'
    lock_url_name = 'inventory:stocktaking_surplus_lock'

    def form_valid(self, form):
        """Save document and line formset."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            # If formset is invalid, delete the main object and re-render
            self.object.delete()
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if we have at least one valid line before saving
        valid_lines = []
        for form in lines_formset.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                valid_lines.append(form)
        
        if not valid_lines:
            self.object.delete()
            form.add_error(None, _('حداقل یک ردیف کالا الزامی است.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        messages.success(self.request, _('سند مازاد انبارگردانی با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())


class StocktakingSurplusUpdateView(EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    """Update view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    formset_class = forms.StocktakingSurplusLineFormSet
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    form_title = _('ویرایش سند مازاد انبارگردانی')
    list_url_name = 'inventory:stocktaking_surplus'
    lock_url_name = 'inventory:stocktaking_surplus_lock'
    lock_redirect_url_name = 'inventory:stocktaking_surplus'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.surplus', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by')
        return queryset

    def form_valid(self, form):
        """Save document and line formset."""
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        messages.success(self.request, _('سند مازاد انبارگردانی با موفقیت بروزرسانی شد.'))
        return HttpResponseRedirect(self.get_success_url())


class StocktakingSurplusDeleteView(DocumentDeleteViewBase):
    """Delete view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    feature_code = 'inventory.stocktaking.surplus'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('سند مازاد موجودی با موفقیت حذف شد.')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Surplus Record')
        context['confirmation_message'] = _('Do you really want to delete this surplus record?')
        context['object_details'] = [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:stocktaking_surplus')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Surplus Records'), 'url': reverse_lazy('inventory:stocktaking_surplus')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


class StocktakingSurplusLockView(DocumentLockView):
    """Lock view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    success_url_name = 'inventory:stocktaking_surplus'
    success_message = _('سند مازاد شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Stocktaking Record Views
# ============================================================================

class StocktakingRecordListView(InventoryBaseView, ListView):
    """List view for stocktaking records."""
    model = models.StocktakingRecord
    template_name = 'inventory/stocktaking_records.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.records', 'created_by')
        queryset = queryset.select_related('confirmed_by', 'created_by')
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        # Generic list context
        context['page_title'] = _('Stocktaking Records')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:stocktaking_record_create')
        context['create_button_text'] = _('Create Stocktaking Record')
        context['show_actions'] = True
        
        # Stocktaking Record-specific context
        context['edit_url_name'] = 'inventory:stocktaking_record_edit'
        context['delete_url_name'] = 'inventory:stocktaking_record_delete'
        context['lock_url_name'] = 'inventory:stocktaking_record_lock'
        context['empty_state_title'] = _('No Stocktaking Records Found')
        context['empty_state_message'] = _('Stocktaking records confirm the accuracy of inventory counts.')
        context['empty_state_icon'] = '📋'
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.records')
        
        # User for permission checks in template
        context['user'] = self.request.user
        
        return context


class StocktakingRecordCreateView(StocktakingFormMixin, CreateView):
    """Create view for stocktaking records."""
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    form_title = _('ایجاد سند نهایی انبارگردانی')
    list_url_name = 'inventory:stocktaking_records'
    lock_url_name = 'inventory:stocktaking_record_lock'

    def form_valid(self, form):
        """Set company and created_by before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند نهایی انبارگردانی با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approver', 'approval_status', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]


class StocktakingRecordUpdateView(EditLockProtectedMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    """Update view for stocktaking records."""
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    form_title = _('ویرایش سند نهایی انبارگردانی')
    list_url_name = 'inventory:stocktaking_records'
    lock_url_name = 'inventory:stocktaking_record_lock'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.stocktaking.records', 'created_by')
        return queryset

    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند نهایی انبارگردانی با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approver', 'approval_status', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]


class StocktakingRecordDeleteView(DocumentDeleteViewBase):
    """Delete view for stocktaking records."""
    model = models.StocktakingRecord
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_records')
    feature_code = 'inventory.stocktaking.records'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('سند شمارش موجودی با موفقیت حذف شد.')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Stocktaking Record')
        context['confirmation_message'] = _('Do you really want to delete this stocktaking record?')
        context['object_details'] = [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Session ID'), 'value': str(self.object.stocktaking_session_id) if self.object.stocktaking_session_id else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:stocktaking_records')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Stocktaking Records'), 'url': reverse_lazy('inventory:stocktaking_records')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


class StocktakingRecordLockView(DocumentLockView):
    """Lock view for stocktaking records."""
    model = models.StocktakingRecord
    success_url_name = 'inventory:stocktaking_records'
    success_message = _('سند شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


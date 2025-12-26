"""
Stocktaking views for inventory module.

This module contains views for:
- Stocktaking Deficit
- Stocktaking Surplus
- Stocktaking Records
"""
from typing import Dict, Any, Optional
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
import json

from .base import InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, LineFormsetMixin
from shared.views.base import (
    EditLockProtectedMixin,
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDocumentUpdateView,
    BaseDocumentListView,
    BaseDocumentCreateView,
    BaseDetailView,
    BaseDeleteView,
)
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
        # #region agent log
        import json, time
        try:
            with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A,E",
                    "location": "stocktaking.py:56",
                    "message": "StocktakingFormMixin.get_context_data entry",
                    "data": {
                        "kwargs_keys": list(kwargs.keys()),
                        "kwargs_has_form": 'form' in kwargs,
                        "kwargs_has_lines_formset": 'lines_formset' in kwargs,
                        "form_is_bound": kwargs.get('form').is_bound if kwargs.get('form') else None,
                        "form_data_keys": list(kwargs.get('form').data.keys())[:5] if kwargs.get('form') and hasattr(kwargs.get('form'), 'data') and kwargs.get('form').data else None
                    },
                    "timestamp": int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        context = super().get_context_data(**kwargs)
        # #region agent log
        try:
            with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A,E",
                    "location": "stocktaking.py:58",
                    "message": "StocktakingFormMixin.get_context_data after super()",
                    "data": {
                        "context_keys": list(context.keys()),
                        "context_has_form": 'form' in context,
                        "context_has_lines_formset": 'lines_formset' in context,
                        "form_is_bound": context.get('form').is_bound if context.get('form') else None,
                        "form_data_keys": list(context.get('form').data.keys())[:5] if context.get('form') and hasattr(context.get('form'), 'data') and context.get('form').data else None,
                        "form_from_kwargs_is_same": context.get('form') is kwargs.get('form') if 'form' in kwargs else None
                    },
                    "timestamp": int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        # Ensure form from kwargs is preserved (Django's CreateView.get_context_data may override it)
        if 'form' in kwargs:
            context['form'] = kwargs['form']
        # #region agent log
        try:
            with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A,E",
                    "location": "stocktaking.py:61",
                    "message": "StocktakingFormMixin.get_context_data after preserving form",
                    "data": {
                        "context_has_form": 'form' in context,
                        "form_is_bound": context.get('form').is_bound if context.get('form') else None,
                        "form_data_keys": list(context.get('form').data.keys())[:5] if context.get('form') and hasattr(context.get('form'), 'data') and context.get('form').data else None,
                        "form_from_kwargs_is_same": context.get('form') is kwargs.get('form') if 'form' in kwargs else None
                    },
                    "timestamp": int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
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

class StocktakingDeficitListView(InventoryBaseView, BaseDocumentListView):
    """List view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    template_name = 'inventory/stocktaking_deficit.html'
    feature_code = 'inventory.stocktaking.deficit'
    permission_field = 'created_by'
    paginate_by = 50

    def get_prefetch_related(self):
        """Prefetch related objects."""
        return ['lines__item', 'lines__warehouse']

    def get_select_related(self):
        """Select related objects."""
        return ['created_by']

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Deficit Records')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:stocktaking_deficit_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Deficit Record')

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:stocktaking_deficit_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:stocktaking_deficit_edit'

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:stocktaking_deficit_delete'

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Deficit Records Found')

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Deficit records are created during stocktaking when counted quantity is less than expected.')

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📉'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add stocktaking deficit specific context."""
        context = super().get_context_data(**kwargs)
        context['lock_url_name'] = 'inventory:stocktaking_deficit_lock'
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.deficit')
        # User for permission checks in template
        context['user'] = self.request.user
        return context


class StocktakingDeficitCreateView(LineFormsetMixin, StocktakingFormMixin, BaseDocumentCreateView):
    """Create view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    formset_class = forms.StocktakingDeficitLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    feature_code = 'inventory.stocktaking.deficit'
    success_message = _('سند کسری انبارگردانی با موفقیت ایجاد شد.')
    form_title = _('ایجاد سند کسری انبارگردانی')
    list_url_name = 'inventory:stocktaking_deficit'
    lock_url_name = 'inventory:stocktaking_deficit_lock'

    def form_valid(self, form):
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseCreateView
        
        with transaction.atomic():
            # Create a temporary instance for formset validation (don't save yet)
            # We need to set the instance temporarily to validate the formset
            # Use form.save(commit=False) to get properly initialized instance
            # Then clear document_code from form.instance so it will be regenerated on final save
            temp_instance = form.save(commit=False)
            temp_instance.pk = None  # Ensure it's treated as new
            # Clear document_code from form.instance so it will be regenerated when form is saved later
            form.instance.document_code = ''
            # Also clear from cleaned_data if it exists
            if 'document_code' in form.cleaned_data:
                form.cleaned_data['document_code'] = ''
            
            # Validate formset BEFORE saving the document
            lines_formset = self.build_line_formset(data=self.request.POST, instance=temp_instance)
            if not lines_formset.is_valid():
                # Formset is invalid, don't save the document
                # Rebuild formset with None instance to show errors properly
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )
            
            # Check if there are any valid lines
            valid_lines = 0
            for line_form in lines_formset.forms:
                if (line_form.cleaned_data and 
                    not line_form.errors and
                    line_form.cleaned_data.get('item') and 
                    not line_form.cleaned_data.get('DELETE', False)):
                    valid_lines += 1
            
            if valid_lines == 0:
                # No valid lines, don't save the document
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
                lines_formset.add_error(None, _('حداقل یک ردیف کالا الزامی است.'))
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )
            
            # Save document first (AutoSetFieldsMixin handles company_id and created_by)
            # Call BaseCreateView.form_valid directly to skip BaseFormsetCreateView's formset.save()
            response = BaseCreateView.form_valid(self, form)
            
            # Rebuild formset with the saved instance
            lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
            # Formset should still be valid, but validate again to be safe
            if not lines_formset.is_valid():
                # This should not happen, but if it does, delete the document
                self.object.delete()
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )
            
            # Save formset using LineFormsetMixin's _save_line_formset
            self._save_line_formset(lines_formset)
        
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        # Use StocktakingFormMixin's get_fieldsets if available
        if hasattr(StocktakingFormMixin, 'get_fieldsets'):
            return super(StocktakingFormMixin, self).get_fieldsets()
        return []

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Deficit Records'), 'url': reverse_lazy('inventory:stocktaking_deficit')},
            {'label': _('Create'), 'url': None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:stocktaking_deficit')


class StocktakingDeficitDetailView(InventoryBaseView, BaseDetailView):
    """Detail view for viewing stocktaking deficit records (read-only)."""
    model = models.StocktakingDeficit
    template_name = 'inventory/stocktaking_deficit_detail.html'
    context_object_name = 'deficit'
    feature_code = 'inventory.stocktaking.deficit'
    permission_field = 'created_by'

    def get_prefetch_related(self):
        """Prefetch related objects."""
        return ['lines__item', 'lines__warehouse']

    def get_select_related(self):
        """Select related objects."""
        return ['created_by']

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Deficit Record')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Deficit Records'), 'url': reverse_lazy('inventory:stocktaking_deficit')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('inventory:stocktaking_deficit')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('inventory:stocktaking_deficit_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Add detail_title and info_banner for generic_detail.html."""
        context = super().get_context_data(**kwargs)
        context['detail_title'] = self.get_page_title()
        # Add empty info_banner list to enable info_banner_extra block
        context['info_banner'] = []
        return context


class StocktakingDeficitUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, BaseDocumentUpdateView):
    """Update view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    formset_class = forms.StocktakingDeficitLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    feature_code = 'inventory.stocktaking.deficit'
    success_message = _('سند کسری انبارگردانی با موفقیت بروزرسانی شد.')
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

    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = super().get_formset_kwargs()
        instance = getattr(self, 'object', None)
        if instance:
            company_id = instance.company_id
        else:
            company_id = self.request.session.get('active_company_id')
        kwargs['company_id'] = company_id
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Save document and line formset."""
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        # Call parent to handle success message and redirect
        return super().form_valid(form)


class StocktakingDeficitDeleteView(InventoryBaseView, BaseDeleteView):
    """Delete view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    feature_code = 'inventory.stocktaking.deficit'
    success_message = _('سند کسری موجودی با موفقیت حذف شد.')
    owner_field = 'created_by'

    def dispatch(self, request, *args, **kwargs):
        """Check permissions before allowing delete."""
        from django.core.exceptions import PermissionDenied
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        
        # Superuser bypass
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        obj = self.get_object()
        
        # Check permissions
        company_id: Optional[int] = request.session.get('active_company_id')
        permissions = get_user_feature_permissions(request.user, company_id)
        
        # Check if user is owner and has DELETE_OWN permission
        is_owner = obj.created_by == request.user if obj.created_by else False
        can_delete_own = has_feature_permission(permissions, self.feature_code, 'delete_own', allow_own_scope=True)
        can_delete_other = has_feature_permission(permissions, self.feature_code, 'delete_other', allow_own_scope=False)
        
        if is_owner and not can_delete_own:
            raise PermissionDenied(_('شما اجازه حذف اسناد خود را ندارید.'))
        elif not is_owner and not can_delete_other:
            raise PermissionDenied(_('شما اجازه حذف اسناد سایر کاربران را ندارید.'))
        
        return super().dispatch(request, *args, **kwargs)

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Deficit Record')

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this deficit record?')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Deficit Records'), 'url': reverse_lazy('inventory:stocktaking_deficit')},
            {'label': _('Delete'), 'url': None},
        ]

    def get_object_details(self):
        """Return object details."""
        return [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:stocktaking_deficit')


class StocktakingDeficitLockView(DocumentLockView):
    """Lock view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    success_url_name = 'inventory:stocktaking_deficit'
    success_message = _('سند کسری شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Stocktaking Surplus Views
# ============================================================================

class StocktakingSurplusListView(InventoryBaseView, BaseDocumentListView):
    """List view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    template_name = 'inventory/stocktaking_surplus.html'
    feature_code = 'inventory.stocktaking.surplus'
    permission_field = 'created_by'
    paginate_by = 50

    def get_prefetch_related(self):
        """Prefetch related objects."""
        return ['lines__item', 'lines__warehouse']

    def get_select_related(self):
        """Select related objects."""
        return ['created_by']

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Surplus Records')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:stocktaking_surplus_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Surplus Record')

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:stocktaking_surplus_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:stocktaking_surplus_edit'

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:stocktaking_surplus_delete'

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Surplus Records Found')

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Surplus records are created during stocktaking when counted quantity is more than expected.')

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📈'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add stocktaking surplus specific context."""
        context = super().get_context_data(**kwargs)
        context['lock_url_name'] = 'inventory:stocktaking_surplus_lock'
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.surplus')
        # User for permission checks in template
        context['user'] = self.request.user
        return context


class StocktakingSurplusCreateView(LineFormsetMixin, StocktakingFormMixin, BaseDocumentCreateView):
    """Create view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    formset_class = forms.StocktakingSurplusLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    feature_code = 'inventory.stocktaking.surplus'
    success_message = _('سند مازاد انبارگردانی با موفقیت ایجاد شد.')
    form_title = _('ایجاد سند مازاد انبارگردانی')
    list_url_name = 'inventory:stocktaking_surplus'
    lock_url_name = 'inventory:stocktaking_surplus_lock'

    def form_valid(self, form):
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseCreateView
        import json
        
        # #region agent log
        try:
            with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A,C",
                    "location": "stocktaking.py:561",
                    "message": "form_valid entry - form.instance state",
                    "data": {
                        "form_instance_doc_code": getattr(form.instance, 'document_code', None),
                        "form_instance_pk": getattr(form.instance, 'pk', None),
                        "form_cleaned_data_doc_code": form.cleaned_data.get('document_code', None) if hasattr(form, 'cleaned_data') else None
                    },
                    "timestamp": int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        with transaction.atomic():
            # Create a temporary instance for formset validation (don't save yet)
            # We need to set the instance temporarily to validate the formset
            # Don't use form.save(commit=False) here because it generates document_code
            # Instead, create a fresh instance with just company_id for validation
            company_id = self.request.session.get('active_company_id')
            temp_instance = self.model(company_id=company_id)
            temp_instance.pk = None  # Ensure it's treated as new
            
            # #region agent log
            try:
                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "E",
                        "location": "stocktaking.py:572",
                        "message": "Created temp_instance without calling form.save()",
                        "data": {
                            "form_instance_doc_code": getattr(form.instance, 'document_code', None),
                            "temp_instance_doc_code": getattr(temp_instance, 'document_code', None),
                            "temp_instance_is_same_as_form_instance": temp_instance is form.instance,
                            "temp_instance_id": id(temp_instance),
                            "form_instance_id": id(form.instance),
                            "company_id": company_id
                        },
                        "timestamp": int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            # Validate formset BEFORE saving the document
            lines_formset = self.build_line_formset(data=self.request.POST, instance=temp_instance)
            
            # #region agent log
            try:
                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A,C",
                        "location": "stocktaking.py:638",
                        "message": "Formset validation result",
                        "data": {
                            "formset_is_valid": lines_formset.is_valid(),
                            "formset_errors": lines_formset.errors if hasattr(lines_formset, 'errors') else None
                        },
                        "timestamp": int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            if not lines_formset.is_valid():
                # Formset is invalid, don't save the document
                # Rebuild formset with None instance to show errors properly
                # #region agent log
                try:
                    with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "A,B,C",
                            "location": "stocktaking.py:636",
                            "message": "Formset invalid - before rebuild",
                            "data": {
                                "form_instance_pk": getattr(form.instance, 'pk', None),
                                "form_instance_doc_code": getattr(form.instance, 'document_code', None),
                                "form_has_cleaned_data": hasattr(form, 'cleaned_data'),
                                "form_cleaned_data_keys": list(form.cleaned_data.keys()) if hasattr(form, 'cleaned_data') else None,
                                "form_data_keys": list(form.data.keys())[:10] if hasattr(form, 'data') else None,
                                "post_data_keys": list(self.request.POST.keys())[:10] if self.request.POST else None
                            },
                            "timestamp": int(__import__('time').time() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
                # #region agent log
                try:
                    import json, time
                    formset_form_data = {}
                    if lines_formset.forms:
                        first_form = lines_formset.forms[0]
                        for field_name in ['item', 'unit', 'warehouse', 'quantity_counted', 'quantity_expected', 'quantity_adjusted']:
                            if field_name in first_form.fields:
                                post_key = f"{first_form.prefix}-{field_name}"
                                formset_form_data[field_name] = {
                                    "post_value": self.request.POST.get(post_key, 'NOT_FOUND'),
                                    "form_value": first_form[field_name].value() if hasattr(first_form, field_name) else None,
                                    "form_data_value": first_form.data.get(post_key) if hasattr(first_form, 'data') and first_form.data else None,
                                    "form_errors": first_form.errors.get(field_name, []) if hasattr(first_form, 'errors') else []
                                }
                    with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "D",
                            "location": "stocktaking.py:724",
                            "message": "After rebuild formset - formset form data check",
                            "data": {
                                "formset_forms_count": len(lines_formset.forms),
                                "formset_has_data": lines_formset.data is not None,
                                "formset_form_data": formset_form_data,
                                "post_keys_lines": [k for k in self.request.POST.keys() if k.startswith('lines-')][:10]
                            },
                            "timestamp": int(time.time() * 1000)
                        }) + '\n')
                except Exception as e:
                    try:
                        with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                            f.write(json.dumps({
                                "sessionId": "debug-session",
                                "runId": "run1",
                                "hypothesisId": "D",
                                "location": "stocktaking.py:724",
                                "message": "Error logging formset data",
                                "data": {"error": str(e)},
                                "timestamp": int(time.time() * 1000)
                            }) + '\n')
                    except: pass
                # #endregion
                # Rebind form with POST data to preserve user input in template
                # Even though form is valid, we need to rebind it so form.data contains POST values
                # This ensures template can display the values using form.field.value()
                form_kwargs = self.get_form_kwargs()
                form_kwargs.pop('instance', None)  # Remove instance if present to avoid duplicate
                form_kwargs.pop('data', None)  # Remove data if present since we're passing it as positional argument
                form = self.form_class(self.request.POST, instance=form.instance, **form_kwargs)
                # #region agent log
                try:
                    import json, time
                    with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "D",
                            "location": "stocktaking.py:760",
                            "message": "After rebind form - form state check",
                            "data": {
                                "form_is_bound": form.is_bound,
                                "form_has_data": hasattr(form, 'data') and form.data is not None,
                                "form_data_stocktaking_session_id": form.data.get('stocktaking_session_id') if hasattr(form, 'data') and form.data else None,
                                "post_stocktaking_session_id": self.request.POST.get('stocktaking_session_id'),
                                "form_cleaned_data_stocktaking_session_id": form.cleaned_data.get('stocktaking_session_id') if hasattr(form, 'cleaned_data') else None,
                                "form_field_stocktaking_session_id_value": form['stocktaking_session_id'].value() if 'stocktaking_session_id' in form.fields else None
                            },
                            "timestamp": int(time.time() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                context = self.get_context_data(form=form, lines_formset=lines_formset)
                # #region agent log
                try:
                    context_form = context.get('form')
                    form_field_values = {}
                    if context_form:
                        for field_name in ['stocktaking_session_id', 'document_code', 'document_date']:
                            if field_name in context_form.fields:
                                field = context_form[field_name]
                                form_field_values[field_name] = {
                                    "value": field.value() if hasattr(field, 'value') else None,
                                    "data": context_form.data.get(field_name) if hasattr(context_form, 'data') and context_form.data else None,
                                    "initial": context_form.initial.get(field_name) if hasattr(context_form, 'initial') else None
                                }
                    with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "C",
                            "location": "stocktaking.py:643",
                            "message": "After get_context_data - form state with field values",
                            "data": {
                                "context_has_form": 'form' in context,
                                "context_has_lines_formset": 'lines_formset' in context,
                                "form_instance_pk": getattr(context_form.instance, 'pk', None) if context_form else None,
                                "form_instance_doc_code": getattr(context_form.instance, 'document_code', None) if context_form else None,
                                "form_has_cleaned_data": hasattr(context_form, 'cleaned_data') if context_form else None,
                                "form_data_keys": list(context_form.data.keys())[:10] if context_form and hasattr(context_form, 'data') and context_form.data else None,
                                "form_is_bound": context_form.is_bound if context_form and hasattr(context_form, 'is_bound') else None,
                                "form_field_values": form_field_values
                            },
                            "timestamp": int(__import__('time').time() * 1000)
                        }) + '\n')
                except Exception as e:
                    try:
                        with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                            f.write(json.dumps({
                                "sessionId": "debug-session",
                                "runId": "run1",
                                "hypothesisId": "C",
                                "location": "stocktaking.py:643",
                                "message": "Error logging form state",
                                "data": {"error": str(e)},
                                "timestamp": int(__import__('time').time() * 1000)
                            }) + '\n')
                    except: pass
                # #endregion
                return self.render_to_response(context)
            
            # Check if there are any valid lines
            valid_lines = 0
            for line_form in lines_formset.forms:
                if (line_form.cleaned_data and 
                    not line_form.errors and
                    line_form.cleaned_data.get('item') and 
                    not line_form.cleaned_data.get('DELETE', False)):
                    valid_lines += 1
            
            # #region agent log
            try:
                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A,C",
                        "location": "stocktaking.py:658",
                        "message": "Valid lines count",
                        "data": {
                            "valid_lines": valid_lines
                        },
                        "timestamp": int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            if valid_lines == 0:
                # No valid lines, don't save the document
                # #region agent log
                try:
                    with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "A,B,C",
                            "location": "stocktaking.py:730",
                            "message": "No valid lines - before rebuild",
                            "data": {
                                "form_instance_pk": getattr(form.instance, 'pk', None),
                                "form_instance_doc_code": getattr(form.instance, 'document_code', None),
                                "form_has_cleaned_data": hasattr(form, 'cleaned_data'),
                                "form_cleaned_data_keys": list(form.cleaned_data.keys()) if hasattr(form, 'cleaned_data') else None
                            },
                            "timestamp": int(__import__('time').time() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
                lines_formset.add_error(None, _('حداقل یک ردیف کالا الزامی است.'))
                context = self.get_context_data(form=form, lines_formset=lines_formset)
                # #region agent log
                try:
                    with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "C",
                            "location": "stocktaking.py:736",
                            "message": "After get_context_data - no valid lines",
                            "data": {
                                "context_has_form": 'form' in context,
                                "form_instance_pk": getattr(context.get('form').instance, 'pk', None) if context.get('form') else None,
                                "form_instance_doc_code": getattr(context.get('form').instance, 'document_code', None) if context.get('form') else None
                            },
                            "timestamp": int(__import__('time').time() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                return self.render_to_response(context)
            
            # #region agent log
            try:
                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A,C,D",
                        "location": "stocktaking.py:674",
                        "message": "Before BaseCreateView.form_valid - form.instance state",
                        "data": {
                            "form_instance_doc_code": getattr(form.instance, 'document_code', None),
                            "form_cleaned_data_doc_code": form.cleaned_data.get('document_code', None) if hasattr(form, 'cleaned_data') else None
                        },
                        "timestamp": int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            # Save document first (AutoSetFieldsMixin handles company_id and created_by)
            # Call BaseCreateView.form_valid directly to skip BaseFormsetCreateView's formset.save()
            response = BaseCreateView.form_valid(self, form)
            
            # #region agent log
            try:
                import json
                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "A,C",
                        "location": "stocktaking.py:683",
                        "message": "After BaseCreateView.form_valid - object saved",
                        "data": {
                            "object_pk": getattr(self.object, 'pk', None),
                            "object_doc_code": getattr(self.object, 'document_code', None) if self.object else None
                        },
                        "timestamp": int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            # Rebuild formset with the saved instance
            lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
            # Formset should still be valid, but validate again to be safe
            if not lines_formset.is_valid():
                # This should not happen, but if it does, delete the document
                self.object.delete()
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )
            
            # Save formset using LineFormsetMixin's _save_line_formset
            self._save_line_formset(lines_formset)
        
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        # Use StocktakingFormMixin's get_fieldsets if available
        if hasattr(StocktakingFormMixin, 'get_fieldsets'):
            return super(StocktakingFormMixin, self).get_fieldsets()
        return []

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Surplus Records'), 'url': reverse_lazy('inventory:stocktaking_surplus')},
            {'label': _('Create'), 'url': None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:stocktaking_surplus')


class StocktakingSurplusDetailView(InventoryBaseView, BaseDetailView):
    """Detail view for viewing stocktaking surplus records (read-only)."""
    model = models.StocktakingSurplus
    template_name = 'inventory/stocktaking_surplus_detail.html'
    context_object_name = 'surplus'
    feature_code = 'inventory.stocktaking.surplus'
    permission_field = 'created_by'

    def get_prefetch_related(self):
        """Prefetch related objects."""
        return ['lines__item', 'lines__warehouse']

    def get_select_related(self):
        """Select related objects."""
        return ['created_by']

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Surplus Record')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Surplus Records'), 'url': reverse_lazy('inventory:stocktaking_surplus')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('inventory:stocktaking_surplus')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('inventory:stocktaking_surplus_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Add detail_title and info_banner for generic_detail.html."""
        context = super().get_context_data(**kwargs)
        context['detail_title'] = self.get_page_title()
        # Add empty info_banner list to enable info_banner_extra block
        context['info_banner'] = []
        return context


class StocktakingSurplusUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, BaseDocumentUpdateView):
    """Update view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    formset_class = forms.StocktakingSurplusLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    feature_code = 'inventory.stocktaking.surplus'
    success_message = _('سند مازاد انبارگردانی با موفقیت بروزرسانی شد.')
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

    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = super().get_formset_kwargs()
        instance = getattr(self, 'object', None)
        if instance:
            company_id = instance.company_id
        else:
            company_id = self.request.session.get('active_company_id')
        kwargs['company_id'] = company_id
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Save document and line formset."""
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        # Call parent to handle success message and redirect
        return super().form_valid(form)


class StocktakingSurplusDeleteView(InventoryBaseView, BaseDeleteView):
    """Delete view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    feature_code = 'inventory.stocktaking.surplus'
    success_message = _('سند مازاد موجودی با موفقیت حذف شد.')
    owner_field = 'created_by'

    def dispatch(self, request, *args, **kwargs):
        """Check permissions before allowing delete."""
        from django.core.exceptions import PermissionDenied
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        
        # Superuser bypass
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        obj = self.get_object()
        
        # Check permissions
        company_id: Optional[int] = request.session.get('active_company_id')
        permissions = get_user_feature_permissions(request.user, company_id)
        
        # Check if user is owner and has DELETE_OWN permission
        is_owner = obj.created_by == request.user if obj.created_by else False
        can_delete_own = has_feature_permission(permissions, self.feature_code, 'delete_own', allow_own_scope=True)
        can_delete_other = has_feature_permission(permissions, self.feature_code, 'delete_other', allow_own_scope=False)
        
        if is_owner and not can_delete_own:
            raise PermissionDenied(_('شما اجازه حذف اسناد خود را ندارید.'))
        elif not is_owner and not can_delete_other:
            raise PermissionDenied(_('شما اجازه حذف اسناد سایر کاربران را ندارید.'))
        
        return super().dispatch(request, *args, **kwargs)

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Surplus Record')

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this surplus record?')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Surplus Records'), 'url': reverse_lazy('inventory:stocktaking_surplus')},
            {'label': _('Delete'), 'url': None},
        ]

    def get_object_details(self):
        """Return object details."""
        return [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:stocktaking_surplus')


class StocktakingSurplusLockView(DocumentLockView):
    """Lock view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    success_url_name = 'inventory:stocktaking_surplus'
    success_message = _('سند مازاد شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Stocktaking Record Views
# ============================================================================

class StocktakingRecordListView(InventoryBaseView, BaseListView):
    """List view for stocktaking records."""
    model = models.StocktakingRecord
    template_name = 'inventory/stocktaking_records.html'
    feature_code = 'inventory.stocktaking.records'
    permission_field = 'created_by'
    paginate_by = 50

    def get_select_related(self):
        """Select related objects."""
        return ['confirmed_by', 'created_by']

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Stocktaking Records')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:stocktaking_record_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Stocktaking Record')

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:stocktaking_record_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:stocktaking_record_edit'

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:stocktaking_record_delete'

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Stocktaking Records Found')

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Stocktaking records confirm the accuracy of inventory counts.')

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📋'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add stocktaking record specific context."""
        context = super().get_context_data(**kwargs)
        context['lock_url_name'] = 'inventory:stocktaking_record_lock'
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.records')
        # User for permission checks in template
        context['user'] = self.request.user
        return context


class StocktakingRecordCreateView(StocktakingFormMixin, BaseCreateView):
    """Create view for stocktaking records."""
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    feature_code = 'inventory.stocktaking.records'
    success_message = _('سند نهایی انبارگردانی با موفقیت ایجاد شد.')
    form_title = _('ایجاد سند نهایی انبارگردانی')
    list_url_name = 'inventory:stocktaking_records'
    lock_url_name = 'inventory:stocktaking_record_lock'

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approver', 'approval_status', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Stocktaking Records'), 'url': reverse_lazy('inventory:stocktaking_records')},
            {'label': _('Create'), 'url': None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:stocktaking_records')


class StocktakingRecordDetailView(InventoryBaseView, BaseDetailView):
    """Detail view for viewing stocktaking records (read-only)."""
    model = models.StocktakingRecord
    template_name = 'inventory/stocktaking_record_detail.html'
    context_object_name = 'record'
    feature_code = 'inventory.stocktaking.records'
    permission_field = 'created_by'

    def get_select_related(self):
        """Select related objects."""
        return ['confirmed_by', 'created_by']

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Stocktaking Record')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Stocktaking Records'), 'url': reverse_lazy('inventory:stocktaking_records')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('inventory:stocktaking_records')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('inventory:stocktaking_record_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Add detail_title and info_banner for generic_detail.html."""
        context = super().get_context_data(**kwargs)
        context['detail_title'] = self.get_page_title()
        # Add empty info_banner list to enable info_banner_extra block
        context['info_banner'] = []
        return context


class StocktakingRecordUpdateView(DocumentLockProtectedMixin, StocktakingFormMixin, BaseUpdateView):
    """Update view for stocktaking records."""
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    feature_code = 'inventory.stocktaking.records'
    success_message = _('سند نهایی انبارگردانی با موفقیت بروزرسانی شد.')
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
        """Set created_by if not set."""
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approver', 'approval_status', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]


class StocktakingRecordDeleteView(InventoryBaseView, BaseDeleteView):
    """Delete view for stocktaking records."""
    model = models.StocktakingRecord
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_records')
    feature_code = 'inventory.stocktaking.records'
    success_message = _('سند شمارش موجودی با موفقیت حذف شد.')
    owner_field = 'created_by'

    def dispatch(self, request, *args, **kwargs):
        """Check permissions before allowing delete."""
        from django.core.exceptions import PermissionDenied
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        
        # Superuser bypass
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        obj = self.get_object()
        
        # Check permissions
        company_id: Optional[int] = request.session.get('active_company_id')
        permissions = get_user_feature_permissions(request.user, company_id)
        
        # Check if user is owner and has DELETE_OWN permission
        is_owner = obj.created_by == request.user if obj.created_by else False
        can_delete_own = has_feature_permission(permissions, self.feature_code, 'delete_own', allow_own_scope=True)
        can_delete_other = has_feature_permission(permissions, self.feature_code, 'delete_other', allow_own_scope=False)
        
        if is_owner and not can_delete_own:
            raise PermissionDenied(_('شما اجازه حذف اسناد خود را ندارید.'))
        elif not is_owner and not can_delete_other:
            raise PermissionDenied(_('شما اجازه حذف اسناد سایر کاربران را ندارید.'))
        
        return super().dispatch(request, *args, **kwargs)

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Stocktaking Record')

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this stocktaking record?')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Stocktaking'), 'url': None},
            {'label': _('Stocktaking Records'), 'url': reverse_lazy('inventory:stocktaking_records')},
            {'label': _('Delete'), 'url': None},
        ]

    def get_object_details(self):
        """Return object details."""
        return [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Session ID'), 'value': str(self.object.stocktaking_session_id) if self.object.stocktaking_session_id else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:stocktaking_records')


class StocktakingRecordLockView(DocumentLockView):
    """Lock view for stocktaking records."""
    model = models.StocktakingRecord
    success_url_name = 'inventory:stocktaking_records'
    success_message = _('سند شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


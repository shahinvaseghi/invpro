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
            # Save document first (AutoSetFieldsMixin handles company_id and created_by)
            # Call BaseCreateView.form_valid directly to skip BaseFormsetCreateView's formset.save()
            response = BaseCreateView.form_valid(self, form)
            
            # Handle line formset with custom validation
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
                lines_formset = self.build_line_formset(instance=None)
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
        
        with transaction.atomic():
            # Save document first (AutoSetFieldsMixin handles company_id and created_by)
            # Call BaseCreateView.form_valid directly to skip BaseFormsetCreateView's formset.save()
            response = BaseCreateView.form_valid(self, form)
            
            # Handle line formset with custom validation
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
                lines_formset = self.build_line_formset(instance=None)
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


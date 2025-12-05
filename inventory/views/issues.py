"""
Issue views for inventory module.

This module contains views for:
- Permanent Issues
- Consumption Issues
- Consignment Issues
- Warehouse Transfer Issues
- Serial Assignment for Issues
"""
from typing import Dict, Any, Optional
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, FormView, DetailView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, InvalidOperation

from .base import InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, DocumentUnlockView, LineFormsetMixin
from shared.views.base import (
    EditLockProtectedMixin, 
    BaseDocumentUpdateView,
    BaseDocumentListView,
    BaseDocumentCreateView,
    BaseDeleteView,
    BaseDetailView,
)
from .receipts import DocumentDeleteViewBase, ReceiptFormMixin
from shared.mixins import FeaturePermissionRequiredMixin
from .. import models
from .. import forms
from ..services import serials as serial_service


# ============================================================================
# Permanent Issue Views
# ============================================================================

class IssuePermanentListView(InventoryBaseView, BaseDocumentListView):
    """List view for permanent issues."""
    model = models.IssuePermanent
    template_name = 'inventory/issue_permanent.html'
    feature_code = 'inventory.issues.permanent'
    permission_field = 'created_by'
    search_fields = ['document_code']
    default_status_filter = False  # We handle status filtering manually
    default_order_by = ['-id']
    paginate_by = 50
    stats_enabled = True

    def get_select_related(self):
        """Select related objects."""
        return ['created_by', 'department_unit', 'warehouse_request']

    def get_prefetch_related(self):
        """Prefetch lines with related objects."""
        return ['lines__item', 'lines__warehouse']

    def apply_custom_filters(self, queryset):
        """Apply posted status and search filters."""
        queryset = super().apply_custom_filters(queryset)
        
        # Posted status filter
        posted_param = self.request.GET.get('posted')
        if posted_param == '1':
            queryset = queryset.filter(is_locked=1)
        elif posted_param == '0':
            queryset = queryset.filter(is_locked=0)
        
        # Search in lines (item name and code)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            )
        
        return queryset.distinct()

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Permanent Issues')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:issue_permanent_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Permanent Issue')

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:issue_permanent_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:issue_permanent_edit'

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:issue_permanent_delete'

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Issues Found')

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first issue document.')

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📤'

    def get_stats(self) -> Dict[str, int]:
        """Return aggregate stats for summary cards."""
        stats = {
            'total': 0,
            'posted': 0,
            'draft': 0,
        }
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return stats
        base_qs = models.IssuePermanent.objects.filter(company_id=company_id)
        stats['total'] = base_qs.count()
        stats['posted'] = base_qs.filter(is_locked=1).count()
        stats['draft'] = base_qs.filter(is_locked=0).count()
        return stats

    def get_stats_labels(self) -> Dict[str, str]:
        """Return stats labels."""
        return {
            'total': _('Total'),
            'posted': _('Posted'),
            'draft': _('Draft'),
        }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        
        # Issue-specific context
        context['create_label'] = _('Permanent Issue')
        context['print_enabled'] = True
        context['view_url_name'] = 'inventory:issue_permanent_detail'
        context['lock_url_name'] = 'inventory:issue_permanent_lock'
        context['show_warehouse_request'] = True
        context['warehouse_request_url_name'] = 'inventory:warehouse_request_edit'
        context['empty_heading'] = _('No Issues Found')
        context['empty_text'] = _('Start by creating your first issue document.')
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.issues.permanent')
        
        # Filters (for template)
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        return context


class IssuePermanentDetailView(InventoryBaseView, BaseDetailView):
    """Detail view for viewing permanent issues (read-only)."""
    model = models.IssuePermanent
    template_name = 'inventory/issue_detail.html'
    context_object_name = 'issue'
    feature_code = 'inventory.issues.permanent'
    permission_field = 'created_by'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'warehouse_request', 'department_unit')
        return queryset

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Permanent Issue')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Permanent Issues'), 'url': reverse_lazy('inventory:issue_permanent')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('inventory:issue_permanent')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse('inventory:issue_permanent_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['issue_variant'] = 'permanent'
        return context


class IssuePermanentCreateView(LineFormsetMixin, ReceiptFormMixin, BaseDocumentCreateView):
    """Create view for permanent issues."""
    model = models.IssuePermanent
    form_class = forms.IssuePermanentForm
    formset_class = forms.IssuePermanentLineFormSet
    success_url = reverse_lazy('inventory:issue_permanent')
    feature_code = 'inventory.issues.permanent'
    form_title = _('ایجاد حواله دائم')
    receipt_variant = 'issue_permanent'
    list_url_name = 'inventory:issue_permanent'
    lock_url_name = 'inventory:issue_permanent_lock'
    formset_prefix = 'lines'
    success_message = _('حواله دائم با موفقیت ایجاد شد.')

    def form_valid(self, form):
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseCreateView
        
        with transaction.atomic():
            # Create a temporary instance for formset validation (don't save yet)
            # We need to set the instance temporarily to validate the formset
            temp_instance = form.save(commit=False)
            temp_instance.pk = None  # Ensure it's treated as new
            
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
                lines_formset.add_error(None, _('Please add at least one line with an item.'))
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
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_permanent')},
            {'label': _('Create Permanent Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_permanent')


class IssuePermanentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView):
    """Update view for permanent issues."""
    model = models.IssuePermanent
    form_class = forms.IssuePermanentForm
    formset_class = forms.IssuePermanentLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:issue_permanent')
    feature_code = 'inventory.issues.permanent'
    success_message = _('حواله دائم با موفقیت ویرایش شد.')
    form_title = _('ویرایش حواله دائم')
    receipt_variant = 'issue_permanent'
    list_url_name = 'inventory:issue_permanent'
    lock_url_name = 'inventory:issue_permanent_lock'
    lock_redirect_url_name = 'inventory:issue_permanent'

    def get_queryset(self):
        """Prefetch related objects and filter by permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'warehouse_request', 'department_unit')
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
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseUpdateView
        
        with transaction.atomic():
            # Save document first (AutoSetFieldsMixin handles edited_by)
            # Call BaseUpdateView.form_valid directly to skip BaseFormsetUpdateView's formset.save()
            response = BaseUpdateView.form_valid(self, form)

            # Handle line formset with custom validation
            lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
            if not lines_formset.is_valid():
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
                lines_formset.add_error(None, _('Please add at least one line with an item.'))
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )

            # Save formset using LineFormsetMixin's _save_line_formset
            self._save_line_formset(lines_formset)
        
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_permanent')},
            {'label': _('Edit Permanent Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_permanent')


class IssuePermanentDeleteView(DocumentLockProtectedMixin, InventoryBaseView, BaseDeleteView):
    """Delete view for permanent issues."""
    model = models.IssuePermanent
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:issue_permanent')
    feature_code = 'inventory.issues.permanent'
    success_message = _('حواله دائم با موفقیت حذف شد.')
    lock_redirect_url_name = 'inventory:issue_permanent'
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

    def get_queryset(self):
        """Filter by permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')
        return queryset

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Permanent Issue')

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this permanent issue?')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Permanent Issues'), 'url': reverse_lazy('inventory:issue_permanent')},
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
        return reverse_lazy('inventory:issue_permanent')


class IssuePermanentLockView(DocumentLockView):
    """Lock view for permanent issues with serial validation."""
    model = models.IssuePermanent
    success_url_name = 'inventory:issue_permanent'
    success_message = _('حواله دائم قفل شد و دیگر قابل ویرایش نیست.')

    def before_lock(self, obj, request):
        """Validate serials for all lines with lot-tracked items."""
        lines = models.IssuePermanentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            if line.item and line.item.has_lot_tracking == 1:
                try:
                    required = int(Decimal(line.quantity))
                except (InvalidOperation, TypeError):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                if Decimal(line.quantity) != Decimal(required):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                selected = line.serials.count()
                if selected != required:
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، پیش از قفل کردن باید %(expected)s سریال انتخاب شود (الان %(selected)s عدد ثبت شده است).')
                        % {'item': line.item.name, 'expected': required, 'selected': selected}
                    )
                    return False
        return True

    def after_lock(self, obj, request):
        """Finalize serials for all lines."""
        lines = models.IssuePermanentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            try:
                serial_service.finalize_issue_line_serials(line, user=request.user)
            except serial_service.SerialTrackingError as exc:
                messages.error(request, str(exc))


# ============================================================================
# Consumption Issue Views
# ============================================================================

class IssueConsumptionListView(InventoryBaseView, BaseDocumentListView):
    """List view for consumption issues."""
    model = models.IssueConsumption
    template_name = 'inventory/issue_consumption.html'
    feature_code = 'inventory.issues.consumption'
    permission_field = 'created_by'
    search_fields = ['document_code']
    default_status_filter = False  # We handle status filtering manually
    default_order_by = ['-id']
    paginate_by = 50
    stats_enabled = True

    def get_select_related(self):
        """Select related objects."""
        return ['created_by', 'department_unit']

    def get_prefetch_related(self):
        """Prefetch lines with related objects."""
        return ['lines__item', 'lines__warehouse']

    def apply_custom_filters(self, queryset):
        """Apply posted status and search filters."""
        queryset = super().apply_custom_filters(queryset)
        
        # Posted status filter
        posted_param = self.request.GET.get('posted')
        if posted_param == '1':
            queryset = queryset.filter(is_locked=1)
        elif posted_param == '0':
            queryset = queryset.filter(is_locked=0)
        
        # Search in lines (item name and code)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            )
        
        return queryset.distinct()

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Consumption Issues')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:issue_consumption_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Consumption Issue')

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:issue_consumption_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:issue_consumption_edit'

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:issue_consumption_delete'

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Issues Found')

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first consumption issue document.')

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📤'

    def get_stats(self) -> Dict[str, int]:
        """Return aggregate stats for summary cards."""
        stats = {
            'total': 0,
            'posted': 0,
            'draft': 0,
        }
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return stats
        base_qs = models.IssueConsumption.objects.filter(company_id=company_id)
        stats['total'] = base_qs.count()
        stats['posted'] = base_qs.filter(is_locked=1).count()
        stats['draft'] = base_qs.filter(is_locked=0).count()
        return stats

    def get_stats_labels(self) -> Dict[str, str]:
        """Return stats labels."""
        return {
            'total': _('Total'),
            'posted': _('Posted'),
            'draft': _('Draft'),
        }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        
        # Issue-specific context
        context['create_label'] = _('Consumption Issue')
        context['print_enabled'] = True
        context['view_url_name'] = 'inventory:issue_consumption_detail'
        context['lock_url_name'] = 'inventory:issue_consumption_lock'
        context['empty_heading'] = _('No Issues Found')
        context['empty_text'] = _('Start by creating your first consumption issue document.')
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.issues.consumption')
        
        # Filters (for template)
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        return context


class IssueConsumptionDetailView(InventoryBaseView, BaseDetailView):
    """Detail view for viewing consumption issues (read-only)."""
    model = models.IssueConsumption
    template_name = 'inventory/issue_detail.html'
    context_object_name = 'issue'
    feature_code = 'inventory.issues.consumption'
    permission_field = 'created_by'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
        return queryset

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Consumption Issue')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Consumption Issues'), 'url': reverse_lazy('inventory:issue_consumption')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('inventory:issue_consumption')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse('inventory:issue_consumption_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['issue_variant'] = 'consumption'
        return context


class IssueConsumptionCreateView(LineFormsetMixin, ReceiptFormMixin, BaseDocumentCreateView):
    """Create view for consumption issues."""
    model = models.IssueConsumption
    form_class = forms.IssueConsumptionForm
    formset_class = forms.IssueConsumptionLineFormSet
    success_url = reverse_lazy('inventory:issue_consumption')
    feature_code = 'inventory.issues.consumption'
    form_title = _('ایجاد حواله مصرف')
    receipt_variant = 'issue_consumption'
    list_url_name = 'inventory:issue_consumption'
    lock_url_name = 'inventory:issue_consumption_lock'
    formset_prefix = 'lines'
    success_message = _('حواله مصرف با موفقیت ایجاد شد.')
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        return super().form_invalid(form)

    def form_valid(self, form):
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseCreateView
        
        with transaction.atomic():
            # Create a temporary instance for formset validation (don't save yet)
            # We need to set the instance temporarily to validate the formset
            temp_instance = form.save(commit=False)
            temp_instance.pk = None  # Ensure it's treated as new
            
            # Validate formset BEFORE saving the document
            lines_formset = self.build_line_formset(data=self.request.POST, instance=temp_instance)
            if not lines_formset.is_valid():
                # Formset is invalid, don't save the document
                # Rebuild formset with None instance to show errors properly
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )
            
            # Check if we have at least one valid line before saving
            valid_lines = 0
            for line_form in lines_formset.forms:
                if (line_form.cleaned_data and 
                    not line_form.errors and
                    line_form.cleaned_data.get('item') and 
                    not line_form.cleaned_data.get('DELETE', False)):
                    valid_lines += 1
            
            if valid_lines == 0:
                # No valid lines, don't save the document
                form.add_error(None, _('Please add at least one line with an item.'))
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
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
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consumption')},
            {'label': _('Create Consumption Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_consumption')


class IssueConsumptionUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView):
    """Update view for consumption issues."""
    model = models.IssueConsumption
    form_class = forms.IssueConsumptionForm
    formset_class = forms.IssueConsumptionLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:issue_consumption')
    feature_code = 'inventory.issues.consumption'
    success_message = _('حواله مصرف با موفقیت ویرایش شد.')
    form_title = _('ویرایش حواله مصرف')
    receipt_variant = 'issue_consumption'
    list_url_name = 'inventory:issue_consumption'
    lock_url_name = 'inventory:issue_consumption_lock'
    lock_redirect_url_name = 'inventory:issue_consumption'

    def get_queryset(self):
        """Prefetch related objects and filter by permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
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
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseUpdateView
        
        with transaction.atomic():
            # Save document first (AutoSetFieldsMixin handles edited_by)
            # Call BaseUpdateView.form_valid directly to skip BaseFormsetUpdateView's formset.save()
            response = BaseUpdateView.form_valid(self, form)

            # Handle line formset with custom validation
            lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
            if not lines_formset.is_valid():
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )

            # Save formset using LineFormsetMixin's _save_line_formset
            self._save_line_formset(lines_formset)
        
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consumption')},
            {'label': _('Edit Consumption Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_consumption')


class IssueConsumptionDeleteView(DocumentLockProtectedMixin, InventoryBaseView, BaseDeleteView):
    """Delete view for consumption issues."""
    model = models.IssueConsumption
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:issue_consumption')
    feature_code = 'inventory.issues.consumption'
    success_message = _('حواله مصرفی با موفقیت حذف شد.')
    lock_redirect_url_name = 'inventory:issue_consumption'
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

    def get_queryset(self):
        """Filter by permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')
        return queryset

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Consumption Issue')

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this consumption issue?')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Consumption Issues'), 'url': reverse_lazy('inventory:issue_consumption')},
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
        return reverse_lazy('inventory:issue_consumption')


class IssueConsumptionLockView(DocumentLockView):
    """Lock view for consumption issues with serial validation."""
    model = models.IssueConsumption
    success_url_name = 'inventory:issue_consumption'
    success_message = _('حواله مصرفی قفل شد و دیگر قابل ویرایش نیست.')

    def before_lock(self, obj, request):
        """Validate serials for all lines with lot-tracked items."""
        lines = models.IssueConsumptionLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            if line.item and line.item.has_lot_tracking == 1:
                try:
                    required = int(Decimal(line.quantity))
                except (InvalidOperation, TypeError):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                if Decimal(line.quantity) != Decimal(required):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                selected = line.serials.count()
                if selected != required:
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، پیش از قفل کردن باید %(expected)s سریال انتخاب شود (الان %(selected)s عدد ثبت شده است).')
                        % {'item': line.item.name, 'expected': required, 'selected': selected}
                    )
                    return False
        return True

    def after_lock(self, obj, request):
        """Finalize serials for all lines."""
        lines = models.IssueConsumptionLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            try:
                serial_service.finalize_issue_line_serials(line, user=request.user)
            except serial_service.SerialTrackingError as exc:
                messages.error(request, str(exc))


# ============================================================================
# Consignment Issue Views
# ============================================================================

class IssueConsignmentListView(InventoryBaseView, BaseDocumentListView):
    """List view for consignment issues."""
    model = models.IssueConsignment
    template_name = 'inventory/issue_consignment.html'
    feature_code = 'inventory.issues.consignment'
    permission_field = 'created_by'
    search_fields = ['document_code']
    default_status_filter = False  # We handle status filtering manually
    default_order_by = ['-id']
    paginate_by = 50
    stats_enabled = True

    def get_select_related(self):
        """Select related objects."""
        return ['created_by', 'department_unit']

    def get_prefetch_related(self):
        """Prefetch lines with related objects."""
        return ['lines__item', 'lines__warehouse', 'lines__supplier']

    def apply_custom_filters(self, queryset):
        """Apply posted status and search filters."""
        queryset = super().apply_custom_filters(queryset)
        
        # Posted status filter
        posted_param = self.request.GET.get('posted')
        if posted_param == '1':
            queryset = queryset.filter(is_locked=1)
        elif posted_param == '0':
            queryset = queryset.filter(is_locked=0)
        
        # Search in lines (item name and code)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            )
        
        return queryset.distinct()

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Consignment Issues')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:issue_consignment_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Consignment Issue')

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:issue_consignment_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:issue_consignment_edit'

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:issue_consignment_delete'

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Issues Found')

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first consignment issue document.')

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📤'

    def get_stats(self) -> Dict[str, int]:
        """Return aggregate stats for summary cards."""
        stats = {
            'total': 0,
            'posted': 0,
            'draft': 0,
        }
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return stats
        base_qs = models.IssueConsignment.objects.filter(company_id=company_id)
        stats['total'] = base_qs.count()
        stats['posted'] = base_qs.filter(is_locked=1).count()
        stats['draft'] = base_qs.filter(is_locked=0).count()
        return stats

    def get_stats_labels(self) -> Dict[str, str]:
        """Return stats labels."""
        return {
            'total': _('Total'),
            'posted': _('Posted'),
            'draft': _('Draft'),
        }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        
        # Issue-specific context
        context['create_label'] = _('Consignment Issue')
        context['print_enabled'] = True
        context['view_url_name'] = 'inventory:issue_consignment_detail'
        context['lock_url_name'] = 'inventory:issue_consignment_lock'
        context['empty_heading'] = _('No Issues Found')
        context['empty_text'] = _('Start by creating your first consignment issue document.')
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.issues.consignment')
        
        # Filters (for template)
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        return context


class IssueConsignmentDetailView(InventoryBaseView, BaseDetailView):
    """Detail view for viewing consignment issues (read-only)."""
    model = models.IssueConsignment
    template_name = 'inventory/issue_detail.html'
    context_object_name = 'issue'
    feature_code = 'inventory.issues.consignment'
    permission_field = 'created_by'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
        return queryset

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Consignment Issue')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Consignment Issues'), 'url': reverse_lazy('inventory:issue_consignment')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('inventory:issue_consignment')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse('inventory:issue_consignment_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['issue_variant'] = 'consignment'
        return context


class IssueConsignmentCreateView(LineFormsetMixin, ReceiptFormMixin, BaseDocumentCreateView):
    """Create view for consignment issues."""
    model = models.IssueConsignment
    form_class = forms.IssueConsignmentForm
    formset_class = forms.IssueConsignmentLineFormSet
    success_url = reverse_lazy('inventory:issue_consignment')
    feature_code = 'inventory.issues.consignment'
    form_title = _('ایجاد حواله امانی')
    receipt_variant = 'issue_consignment'
    list_url_name = 'inventory:issue_consignment'
    lock_url_name = 'inventory:issue_consignment_lock'
    formset_prefix = 'lines'
    success_message = _('حواله امانی با موفقیت ایجاد شد.')

    def form_valid(self, form):
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseCreateView
        
        with transaction.atomic():
            # Create a temporary instance for formset validation (don't save yet)
            # We need to set the instance temporarily to validate the formset
            temp_instance = form.save(commit=False)
            temp_instance.pk = None  # Ensure it's treated as new
            
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
                form.add_error(None, _('Please add at least one line with an item.'))
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
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
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consignment')},
            {'label': _('Create Consignment Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_consignment')


class IssueConsignmentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView):
    """Update view for consignment issues."""
    model = models.IssueConsignment
    form_class = forms.IssueConsignmentForm
    formset_class = forms.IssueConsignmentLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:issue_consignment')
    feature_code = 'inventory.issues.consignment'
    success_message = _('حواله امانی با موفقیت ویرایش شد.')
    form_title = _('ویرایش حواله امانی')
    receipt_variant = 'issue_consignment'
    list_url_name = 'inventory:issue_consignment'
    lock_url_name = 'inventory:issue_consignment_lock'
    lock_redirect_url_name = 'inventory:issue_consignment'

    def get_queryset(self):
        """Prefetch related objects and filter by permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
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
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseUpdateView
        
        with transaction.atomic():
            # Save document first (AutoSetFieldsMixin handles edited_by)
            # Call BaseUpdateView.form_valid directly to skip BaseFormsetUpdateView's formset.save()
            response = BaseUpdateView.form_valid(self, form)

            # Handle line formset with custom validation
            lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
            if not lines_formset.is_valid():
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )

            # Save formset using LineFormsetMixin's _save_line_formset
            self._save_line_formset(lines_formset)
        
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_consignment')},
            {'label': _('Edit Consignment Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_consignment')


class IssueConsignmentDeleteView(DocumentLockProtectedMixin, InventoryBaseView, BaseDeleteView):
    """Delete view for consignment issues."""
    model = models.IssueConsignment
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:issue_consignment')
    feature_code = 'inventory.issues.consignment'
    success_message = _('حواله امانی با موفقیت حذف شد.')
    lock_redirect_url_name = 'inventory:issue_consignment'
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

    def get_queryset(self):
        """Filter by permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')
        return queryset

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Consignment Issue')

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this consignment issue?')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Consignment Issues'), 'url': reverse_lazy('inventory:issue_consignment')},
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
        return reverse_lazy('inventory:issue_consignment')


class IssueConsignmentLockView(DocumentLockView):
    """Lock view for consignment issues with serial validation."""
    model = models.IssueConsignment
    success_url_name = 'inventory:issue_consignment'
    success_message = _('حواله امانی قفل شد و دیگر قابل ویرایش نیست.')

    def before_lock(self, obj, request):
        """Validate serials for all lines with lot-tracked items."""
        lines = models.IssueConsignmentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            if line.item and line.item.has_lot_tracking == 1:
                try:
                    required = int(Decimal(line.quantity))
                except (InvalidOperation, TypeError):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                if Decimal(line.quantity) != Decimal(required):
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، مقدار باید پیش از قفل‌شدن عدد صحیح باشد.')
                        % {'item': line.item.name}
                    )
                    return False
                selected = line.serials.count()
                if selected != required:
                    messages.error(
                        request,
                        _('برای ردیف %(item)s، پیش از قفل کردن باید %(expected)s سریال انتخاب شود (الان %(selected)s عدد ثبت شده است).')
                        % {'item': line.item.name, 'expected': required, 'selected': selected}
                    )
                    return False
        return True

    def after_lock(self, obj, request):
        """Finalize serials for all lines."""
        lines = models.IssueConsignmentLine.objects.filter(document=obj, is_enabled=1)
        for line in lines:
            try:
                serial_service.finalize_issue_line_serials(line, user=request.user)
            except serial_service.SerialTrackingError as exc:
                messages.error(request, str(exc))


# ============================================================================
# Issue Line Serial Assignment Views
# ============================================================================

class IssueLineSerialAssignmentBaseView(FeaturePermissionRequiredMixin, FormView):
    """Base view for assigning serials to a specific issue line."""
    template_name = 'inventory/issue_serial_assignment.html'
    form_class = forms.IssueLineSerialAssignmentForm
    line_model = None
    document_model = None
    feature_code = None
    serial_url_name = ''
    list_url_name = ''
    edit_url_name = ''
    lock_url_name = ''

    def dispatch(self, request, *args, **kwargs):
        """Check if item requires serial tracking and document is not locked."""
        self.document = self.get_document()
        self.line = self.get_line()
        if self.line.item and self.line.item.has_lot_tracking != 1:
            messages.info(request, _('این کالا نیازی به سریال ندارد.'))
            return HttpResponseRedirect(reverse(self.edit_url_name, args=[self.document.pk]))
        if getattr(self.document, 'is_locked', 0):
            messages.info(request, _('برای سند قفل‌شده امکان تغییر سریال وجود ندارد.'))
            return HttpResponseRedirect(reverse(self.list_url_name))
        return super().dispatch(request, *args, **kwargs)

    def get_document(self):
        """Get document object."""
        queryset = self.document_model.objects.all()
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if company_id and hasattr(self.document_model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))

    def get_line(self):
        """Get line object."""
        queryset = self.line_model.objects.filter(document=self.document)
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if company_id and hasattr(self.line_model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('line_id'))

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Pass line to form."""
        kwargs = super().get_form_kwargs()
        kwargs['line'] = self.line
        return kwargs

    def form_valid(self, form):
        """Save serial assignments."""
        form.save(user=self.request.user)
        messages.success(self.request, _('سریال‌های ردیف با موفقیت ذخیره شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        """Get success URL after serial assignment."""
        return reverse(self.edit_url_name, args=[self.document.pk])

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Get context for serial assignment page."""
        context = super().get_context_data(**kwargs)
        context['line'] = self.line
        context['document'] = self.document
        context['list_url'] = reverse(self.list_url_name)
        context['edit_url'] = reverse(self.edit_url_name, args=[self.document.pk])
        context['lock_url'] = reverse(self.lock_url_name, args=[self.document.pk]) if self.lock_url_name else None
        try:
            required = int(Decimal(self.line.quantity))
        except (InvalidOperation, TypeError):
            required = None
        context['required_serials'] = required
        context['selected_serials_count'] = self.line.serials.count()
        available_queryset = context['form'].fields['serials'].queryset
        context['available_serials_count'] = available_queryset.count()
        context['available_serials'] = available_queryset
        return context


class IssuePermanentLineSerialAssignmentView(IssueLineSerialAssignmentBaseView):
    """Serial assignment view for permanent issue lines."""
    line_model = models.IssuePermanentLine
    document_model = models.IssuePermanent
    feature_code = 'inventory.issues.permanent'
    serial_url_name = 'inventory:issue_permanent_line_serials'
    list_url_name = 'inventory:issue_permanent'
    edit_url_name = 'inventory:issue_permanent_edit'
    lock_url_name = 'inventory:issue_permanent_lock'


class IssueConsumptionLineSerialAssignmentView(IssueLineSerialAssignmentBaseView):
    """Serial assignment view for consumption issue lines."""
    line_model = models.IssueConsumptionLine
    document_model = models.IssueConsumption
    feature_code = 'inventory.issues.consumption'
    serial_url_name = 'inventory:issue_consumption_line_serials'
    list_url_name = 'inventory:issue_consumption'
    edit_url_name = 'inventory:issue_consumption_edit'
    lock_url_name = 'inventory:issue_consumption_lock'


class IssueConsignmentLineSerialAssignmentView(IssueLineSerialAssignmentBaseView):
    """Serial assignment view for consignment issue lines."""
    line_model = models.IssueConsignmentLine
    document_model = models.IssueConsignment
    feature_code = 'inventory.issues.consignment'
    serial_url_name = 'inventory:issue_consignment_line_serials'
    list_url_name = 'inventory:issue_consignment'
    edit_url_name = 'inventory:issue_consignment_edit'
    lock_url_name = 'inventory:issue_consignment_lock'


# ============================================================================
# Warehouse Transfer Issue Views
# ============================================================================

class IssueWarehouseTransferListView(InventoryBaseView, BaseDocumentListView):
    """List view for warehouse transfer issues."""
    model = models.IssueWarehouseTransfer
    template_name = 'inventory/issue_warehouse_transfer.html'
    feature_code = 'inventory.issues.warehouse_transfer'
    permission_field = 'created_by'
    search_fields = ['document_code']
    default_status_filter = False  # We handle status filtering manually
    default_order_by = ['-id']
    paginate_by = 50
    stats_enabled = True

    def get_base_queryset(self):
        """Get base queryset including production transfers."""
        queryset = super().get_base_queryset()
        
        # Filter by user permissions (own vs all)
        # But also include warehouse transfers created from TransferToLine
        from django.db.models import Q
        
        # Get base filtered queryset
        base_queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.warehouse_transfer', 'created_by')
        
        # Always include warehouse transfers created from TransferToLine
        # These are part of the production workflow and should be visible
        company_id = self.request.session.get('active_company_id')
        if company_id:
            # Include warehouse transfers created from TransferToLine
            production_transfer_queryset = queryset.filter(
                production_transfer__isnull=False,
                company_id=company_id,
            )
            # Combine both querysets (union removes duplicates)
            queryset = (base_queryset | production_transfer_queryset).distinct()
        else:
            queryset = base_queryset
        
        return queryset

    def get_select_related(self):
        """Select related objects."""
        return ['created_by', 'production_transfer']

    def get_prefetch_related(self):
        """Prefetch lines with related objects."""
        return ['lines__item', 'lines__source_warehouse', 'lines__destination_warehouse']

    def apply_custom_filters(self, queryset):
        """Apply posted status and search filters."""
        queryset = super().apply_custom_filters(queryset)
        
        # Posted status filter
        posted_param = self.request.GET.get('posted')
        if posted_param == '1':
            queryset = queryset.filter(is_locked=1)
        elif posted_param == '0':
            queryset = queryset.filter(is_locked=0)
        
        # Search in lines (item name and code)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            )
        
        return queryset.distinct()

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Warehouse Transfer Issues')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:issue_warehouse_transfer_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Warehouse Transfer Issue')

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:issue_warehouse_transfer_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:issue_warehouse_transfer_edit'

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Issues Found')

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first warehouse transfer issue document.')

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📤'

    def get_stats(self) -> Dict[str, int]:
        """Return aggregate stats for summary cards."""
        stats = {
            'total': 0,
            'posted': 0,
            'draft': 0,
        }
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return stats
        base_qs = models.IssueWarehouseTransfer.objects.filter(company_id=company_id)
        stats['total'] = base_qs.count()
        stats['posted'] = base_qs.filter(is_locked=1).count()
        stats['draft'] = base_qs.filter(is_locked=0).count()
        return stats

    def get_stats_labels(self) -> Dict[str, str]:
        """Return stats labels."""
        return {
            'total': _('Total'),
            'posted': _('Posted'),
            'draft': _('Draft'),
        }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        
        # Issue-specific context
        context['create_label'] = _('Warehouse Transfer Issue')
        context['print_enabled'] = True
        context['delete_url_name'] = None  # Delete not implemented yet
        
        return context


class IssueWarehouseTransferCreateView(LineFormsetMixin, ReceiptFormMixin, BaseDocumentCreateView):
    """Create view for warehouse transfer issues."""
    model = models.IssueWarehouseTransfer
    form_class = forms.IssueWarehouseTransferForm
    formset_class = forms.IssueWarehouseTransferLineFormSet
    success_url = reverse_lazy('inventory:issue_warehouse_transfer')
    feature_code = 'inventory.issues.warehouse_transfer'
    form_title = _('ایجاد حواله انتقال بین انبارها')
    receipt_variant = 'issue_warehouse_transfer'
    list_url_name = 'inventory:issue_warehouse_transfer'
    lock_url_name = 'inventory:issue_warehouse_transfer_lock'
    formset_prefix = 'lines'
    success_message = _('حواله انتقال بین انبارها با موفقیت ایجاد شد.')

    def form_valid(self, form):
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseCreateView
        
        with transaction.atomic():
            # Create a temporary instance for formset validation (don't save yet)
            # We need to set the instance temporarily to validate the formset
            temp_instance = form.save(commit=False)
            temp_instance.pk = None  # Ensure it's treated as new
            
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
                form.add_error(None, _('Please add at least one line with an item.'))
                lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
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
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_warehouse_transfer')},
            {'label': _('Create Warehouse Transfer Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_warehouse_transfer')


class IssueWarehouseTransferUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView):
    """Update view for warehouse transfer issues."""
    model = models.IssueWarehouseTransfer
    form_class = forms.IssueWarehouseTransferForm
    formset_class = forms.IssueWarehouseTransferLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:issue_warehouse_transfer')
    feature_code = 'inventory.issues.warehouse_transfer'
    success_message = _('حواله انتقال بین انبارها با موفقیت به‌روزرسانی شد.')
    form_title = _('ویرایش حواله انتقال بین انبارها')
    receipt_variant = 'issue_warehouse_transfer'
    list_url_name = 'inventory:issue_warehouse_transfer'
    lock_url_name = 'inventory:issue_warehouse_transfer_lock'

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

    def get_queryset(self):
        """Prefetch related objects and filter by permissions."""
        queryset = super().get_queryset()
        # Include production transfers
        from django.db.models import Q
        company_id = self.request.session.get('active_company_id')
        if company_id:
            base_queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.warehouse_transfer', 'created_by')
            production_transfer_queryset = queryset.filter(
                production_transfer__isnull=False,
                company_id=company_id,
            )
            queryset = (base_queryset | production_transfer_queryset).distinct()
        else:
            queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.warehouse_transfer', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__source_warehouse',
            'lines__destination_warehouse'
        ).select_related('created_by', 'production_transfer')
        return queryset

    def form_valid(self, form):
        """Save document and line formset with custom validation."""
        from django.db import transaction
        from shared.views.base import BaseUpdateView
        
        with transaction.atomic():
            # Save document first (AutoSetFieldsMixin handles edited_by)
            # Call BaseUpdateView.form_valid directly to skip BaseFormsetUpdateView's formset.save()
            response = BaseUpdateView.form_valid(self, form)

            # Handle line formset with custom validation
            lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
            if not lines_formset.is_valid():
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
                lines_formset.add_error(None, _('Please add at least one line with an item.'))
                return self.render_to_response(
                    self.get_context_data(form=form, lines_formset=lines_formset)
                )

            # Save formset using LineFormsetMixin's _save_line_formset
            self._save_line_formset(lines_formset)
        
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': reverse_lazy('inventory:issue_warehouse_transfer')},
            {'label': _('Edit Warehouse Transfer Issue'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:issue_warehouse_transfer')




class IssueWarehouseTransferDetailView(InventoryBaseView, BaseDetailView):
    """Detail view for warehouse transfer issues (read-only)."""
    model = models.IssueWarehouseTransfer
    template_name = 'inventory/issue_warehouse_transfer_detail.html'
    context_object_name = 'warehouse_transfer'
    feature_code = 'inventory.issues.warehouse_transfer'
    permission_field = 'created_by'

    def get_queryset(self):
        """Filter by active company and include production transfers."""
        from django.db.models import Q
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            base_queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.warehouse_transfer', 'created_by')
            production_transfer_queryset = queryset.filter(
                production_transfer__isnull=False,
                company_id=company_id,
            )
            queryset = (base_queryset | production_transfer_queryset).distinct()
        else:
            queryset = models.IssueWarehouseTransfer.objects.none()
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__source_warehouse',
            'lines__destination_warehouse'
        ).select_related('created_by', 'production_transfer')
        return queryset

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Warehouse Transfer Issue')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Warehouse Transfer Issues'), 'url': reverse_lazy('inventory:issue_warehouse_transfer')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('inventory:issue_warehouse_transfer')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('inventory:issue_warehouse_transfer_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add issue-specific context."""
        context = super().get_context_data(**kwargs)
        return context


class IssueWarehouseTransferLockView(DocumentLockView):
    """Lock view for warehouse transfer issues."""
    model = models.IssueWarehouseTransfer
    success_url_name = 'inventory:issue_warehouse_transfer'
    success_message = _('حواله انتقال بین انبارها قفل شد و دیگر قابل ویرایش نیست.')


class IssueWarehouseTransferUnlockView(DocumentUnlockView):
    """Unlock view for warehouse transfer issues."""
    model = models.IssueWarehouseTransfer
    success_url_name = 'inventory:issue_warehouse_transfer'
    success_message = _('حواله انتقال بین انبارها از قفل خارج شد و قابل ویرایش است.')
    feature_code = 'inventory.issues.warehouse_transfer'
    required_action = 'unlock_own'

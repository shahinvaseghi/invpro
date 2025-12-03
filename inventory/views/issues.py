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

from .base import InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, LineFormsetMixin
from shared.views.base import EditLockProtectedMixin
from .receipts import DocumentDeleteViewBase, ReceiptFormMixin
from shared.mixins import FeaturePermissionRequiredMixin
from .. import models
from .. import forms
from ..services import serials as serial_service


# ============================================================================
# Permanent Issue Views
# ============================================================================

class IssuePermanentListView(InventoryBaseView, ListView):
    """List view for permanent issues."""
    model = models.IssuePermanent
    template_name = 'inventory/issue_permanent.html'
    context_object_name = 'object_list'
    paginate_by = 50
    ordering = ['-id']  # Show newest documents first

    def get_queryset(self):
        """Prefetch related objects for efficient display and apply filters."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')
        queryset = queryset.select_related('created_by', 'department_unit', 'warehouse_request').prefetch_related(
            'lines__item',
            'lines__warehouse',
        )
        
        # Apply filters
        posted_param = self.request.GET.get('posted')
        if posted_param == '1':
            queryset = queryset.filter(is_locked=1)
        elif posted_param == '0':
            queryset = queryset.filter(is_locked=0)
        
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            ).distinct()
        
        return queryset

    def _get_stats(self) -> Dict[str, int]:
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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        # Generic list context
        context['page_title'] = _('Permanent Issues')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:issue_permanent_create')
        context['create_button_text'] = _('Create Permanent Issue')
        context['create_label'] = _('Permanent Issue')
        context['show_filters'] = True
        context['print_enabled'] = True
        context['show_actions'] = True
        
        # Issue-specific context
        context['edit_url_name'] = 'inventory:issue_permanent_edit'
        context['delete_url_name'] = 'inventory:issue_permanent_delete'
        context['lock_url_name'] = 'inventory:issue_permanent_lock'
        context['detail_url_name'] = 'inventory:issue_permanent_detail'
        context['show_warehouse_request'] = True
        context['warehouse_request_url_name'] = 'inventory:warehouse_request_edit'
        context['empty_state_title'] = _('No Issues Found')
        context['empty_state_message'] = _('Start by creating your first issue document.')
        context['empty_state_icon'] = '📤'
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.issues.permanent')
        
        # Filters
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        # Stats
        context['stats'] = self._get_stats()
        
        # User for permission checks in template
        context['user'] = self.request.user
        
        return context


class IssuePermanentDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing permanent issues (read-only)."""
    model = models.IssuePermanent
    template_name = 'inventory/issue_detail.html'
    context_object_name = 'issue'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'warehouse_request', 'department_unit')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['issue_variant'] = 'permanent'
        context['list_url'] = reverse('inventory:issue_permanent')
        context['edit_url'] = reverse('inventory:issue_permanent_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class IssuePermanentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create view for permanent issues."""
    model = models.IssuePermanent
    form_class = forms.IssuePermanentForm
    formset_class = forms.IssuePermanentLineFormSet
    success_url = reverse_lazy('inventory:issue_permanent')
    form_title = _('ایجاد حواله دائم')
    receipt_variant = 'issue_permanent'
    list_url_name = 'inventory:issue_permanent'
    lock_url_name = 'inventory:issue_permanent_lock'

    def form_valid(self, form):
        """Save document and line formset."""
        form.instance.company_id = self.request.session.get('active_company_id')
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
        
        # Check if there are any valid lines
        valid_lines = 0
        for line_form in lines_formset.forms:
            if (line_form.cleaned_data and 
                not line_form.errors and
                line_form.cleaned_data.get('item') and 
                not line_form.cleaned_data.get('DELETE', False)):
                valid_lines += 1
        
        if valid_lines == 0:
            # Delete the document if no valid lines
            self.object.delete()
            lines_formset.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله دائم با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]


class IssuePermanentUpdateView(EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    """Update view for permanent issues."""
    model = models.IssuePermanent
    form_class = forms.IssuePermanentForm
    formset_class = forms.IssuePermanentLineFormSet
    success_url = reverse_lazy('inventory:issue_permanent')
    form_title = _('ویرایش حواله دائم')
    receipt_variant = 'issue_permanent'
    list_url_name = 'inventory:issue_permanent'
    lock_url_name = 'inventory:issue_permanent_lock'
    lock_redirect_url_name = 'inventory:issue_permanent'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.permanent', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'warehouse_request', 'department_unit')
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
        
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله دائم با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]


class IssuePermanentDeleteView(DocumentDeleteViewBase):
    """Delete view for permanent issues."""
    model = models.IssuePermanent
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:issue_permanent')
    feature_code = 'inventory.issues.permanent'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('حواله دائم با موفقیت حذف شد.')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Permanent Issue')
        context['confirmation_message'] = _('Do you really want to delete this permanent issue?')
        context['object_details'] = [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:issue_permanent')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Permanent Issues'), 'url': reverse_lazy('inventory:issue_permanent')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


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

class IssueConsumptionListView(InventoryBaseView, ListView):
    """List view for consumption issues."""
    model = models.IssueConsumption
    template_name = 'inventory/issue_consumption.html'
    context_object_name = 'object_list'
    paginate_by = 50
    ordering = ['-id']  # Show newest documents first

    def get_queryset(self):
        """Prefetch related objects for efficient display and apply filters."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')
        queryset = queryset.select_related('created_by', 'department_unit').prefetch_related(
            'lines__item',
            'lines__warehouse',
        )
        
        # Apply filters
        posted_param = self.request.GET.get('posted')
        if posted_param == '1':
            queryset = queryset.filter(is_locked=1)
        elif posted_param == '0':
            queryset = queryset.filter(is_locked=0)
        
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            ).distinct()
        
        return queryset

    def _get_stats(self) -> Dict[str, int]:
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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        # Generic list context
        context['page_title'] = _('Consumption Issues')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:issue_consumption_create')
        context['create_button_text'] = _('Create Consumption Issue')
        context['create_label'] = _('Consumption Issue')
        context['show_filters'] = True
        context['print_enabled'] = True
        context['show_actions'] = True
        
        # Issue-specific context
        context['edit_url_name'] = 'inventory:issue_consumption_edit'
        context['delete_url_name'] = 'inventory:issue_consumption_delete'
        context['lock_url_name'] = 'inventory:issue_consumption_lock'
        context['detail_url_name'] = 'inventory:issue_consumption_detail'
        context['empty_state_title'] = _('No Issues Found')
        context['empty_state_message'] = _('Start by creating your first issue document.')
        context['empty_state_icon'] = '📤'
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.issues.consumption')
        
        # Filters
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        # Stats
        context['stats'] = self._get_stats()
        
        # User for permission checks in template
        context['user'] = self.request.user
        
        return context


class IssueConsumptionDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing consumption issues (read-only)."""
    model = models.IssueConsumption
    template_name = 'inventory/issue_detail.html'
    context_object_name = 'issue'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['issue_variant'] = 'consumption'
        context['list_url'] = reverse('inventory:issue_consumption')
        context['edit_url'] = reverse('inventory:issue_consumption_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class IssueConsumptionCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create view for consumption issues."""
    model = models.IssueConsumption
    form_class = forms.IssueConsumptionForm
    formset_class = forms.IssueConsumptionLineFormSet
    success_url = reverse_lazy('inventory:issue_consumption')
    form_title = _('ایجاد حواله مصرف')
    receipt_variant = 'issue_consumption'
    list_url_name = 'inventory:issue_consumption'
    lock_url_name = 'inventory:issue_consumption_lock'
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        return super().form_invalid(form)

    def form_valid(self, form):
        """Save document and line formset."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            # Add formset errors to form for display
            if lines_formset.non_form_errors():
                for error in lines_formset.non_form_errors():
                    form.add_error(None, error)
            # Also add individual form errors for better debugging
            for idx, line_form in enumerate(lines_formset.forms):
                if line_form.errors:
                    for field, errors in line_form.errors.items():
                        for error in errors:
                            error_msg = _('Line %(line)d - %(field)s: %(error)s') % {
                                'line': idx + 1,
                                'field': field,
                                'error': error
                            }
                            form.add_error(None, error_msg)
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if we have at least one valid line before saving
        valid_lines = []
        form_errors = []
        for idx, line_form in enumerate(lines_formset.forms):
            # Skip empty forms (no item)
            if not line_form.cleaned_data:
                continue
            # Skip deleted forms
            if line_form.cleaned_data.get('DELETE', False):
                continue
            # Skip forms without item
            if not line_form.cleaned_data.get('item'):
                continue
            # Check if form has validation errors
            if line_form.errors:
                # Collect error messages for display
                item_name = str(line_form.cleaned_data.get('item', 'Item'))
                for field, errors in line_form.errors.items():
                    for error in errors:
                        form_errors.append(f"{item_name}: {field}: {error}")
                # Form has errors, don't count it as valid but keep the formset to show errors
                continue
            # This form is valid
            valid_lines.append(line_form)
        
        if not valid_lines:
            # No valid lines, show error and delete the document
            self.object.delete()
            if form_errors:
                for error_msg in form_errors:
                    form.add_error(None, error_msg)
            else:
                form.add_error(None, _('Please add at least one line with an item and complete all required fields.'))
            # Rebuild formset with POST data to preserve user input and show errors
            lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('حواله مصرف با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]


class IssueConsumptionUpdateView(EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    """Update view for consumption issues."""
    model = models.IssueConsumption
    form_class = forms.IssueConsumptionForm
    formset_class = forms.IssueConsumptionLineFormSet
    success_url = reverse_lazy('inventory:issue_consumption')
    form_title = _('ویرایش حواله مصرف')
    receipt_variant = 'issue_consumption'
    list_url_name = 'inventory:issue_consumption'
    lock_url_name = 'inventory:issue_consumption_lock'
    lock_redirect_url_name = 'inventory:issue_consumption'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consumption', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
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
        
        messages.success(self.request, _('حواله مصرف با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]


class IssueConsumptionDeleteView(DocumentDeleteViewBase):
    """Delete view for consumption issues."""
    model = models.IssueConsumption
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:issue_consumption')
    feature_code = 'inventory.issues.consumption'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('حواله مصرفی با موفقیت حذف شد.')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Consumption Issue')
        context['confirmation_message'] = _('Do you really want to delete this consumption issue?')
        context['object_details'] = [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:issue_consumption')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Consumption Issues'), 'url': reverse_lazy('inventory:issue_consumption')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


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

class IssueConsignmentListView(InventoryBaseView, ListView):
    """List view for consignment issues."""
    model = models.IssueConsignment
    template_name = 'inventory/issue_consignment.html'
    context_object_name = 'object_list'
    paginate_by = 50
    ordering = ['-id']  # Show newest documents first

    def get_queryset(self):
        """Prefetch related objects for efficient display and apply filters."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')
        queryset = queryset.select_related('created_by', 'department_unit').prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__supplier',
        )
        
        # Apply filters
        posted_param = self.request.GET.get('posted')
        if posted_param == '1':
            queryset = queryset.filter(is_locked=1)
        elif posted_param == '0':
            queryset = queryset.filter(is_locked=0)
        
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            ).distinct()
        
        return queryset

    def _get_stats(self) -> Dict[str, int]:
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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        # Generic list context
        context['page_title'] = _('Consignment Issues')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:issue_consignment_create')
        context['create_button_text'] = _('Create Consignment Issue')
        context['create_label'] = _('Consignment Issue')
        context['show_filters'] = True
        context['print_enabled'] = True
        context['show_actions'] = True
        
        # Issue-specific context
        context['edit_url_name'] = 'inventory:issue_consignment_edit'
        context['delete_url_name'] = 'inventory:issue_consignment_delete'
        context['lock_url_name'] = 'inventory:issue_consignment_lock'
        context['detail_url_name'] = 'inventory:issue_consignment_detail'
        context['empty_state_title'] = _('No Issues Found')
        context['empty_state_message'] = _('Start by creating your first issue document.')
        context['empty_state_icon'] = '📤'
        
        # Permissions
        self.add_delete_permissions_to_context(context, 'inventory.issues.consignment')
        
        # Filters
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        # Stats
        context['stats'] = self._get_stats()
        
        # User for permission checks in template
        context['user'] = self.request.user
        
        return context


class IssueConsignmentDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing consignment issues (read-only)."""
    model = models.IssueConsignment
    template_name = 'inventory/issue_detail.html'
    context_object_name = 'issue'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['issue_variant'] = 'consignment'
        context['list_url'] = reverse('inventory:issue_consignment')
        context['edit_url'] = reverse('inventory:issue_consignment_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class IssueConsignmentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create view for consignment issues."""
    model = models.IssueConsignment
    form_class = forms.IssueConsignmentForm
    formset_class = forms.IssueConsignmentLineFormSet
    success_url = reverse_lazy('inventory:issue_consignment')
    form_title = _('ایجاد حواله امانی')
    receipt_variant = 'issue_consignment'
    list_url_name = 'inventory:issue_consignment'
    lock_url_name = 'inventory:issue_consignment_lock'

    def form_valid(self, form):
        """Save document and line formset."""
        form.instance.company_id = self.request.session.get('active_company_id')
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
        
        messages.success(self.request, _('حواله امانی با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]


class IssueConsignmentUpdateView(EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    """Update view for consignment issues."""
    model = models.IssueConsignment
    form_class = forms.IssueConsignmentForm
    formset_class = forms.IssueConsignmentLineFormSet
    success_url = reverse_lazy('inventory:issue_consignment')
    form_title = _('ویرایش حواله امانی')
    receipt_variant = 'issue_consignment'
    list_url_name = 'inventory:issue_consignment'
    lock_url_name = 'inventory:issue_consignment_lock'
    lock_redirect_url_name = 'inventory:issue_consignment'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.issues.consignment', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'department_unit')
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
        
        messages.success(self.request, _('حواله امانی با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),  # document_date is hidden, auto-generated
        ]


class IssueConsignmentDeleteView(DocumentDeleteViewBase):
    """Delete view for consignment issues."""
    model = models.IssueConsignment
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:issue_consignment')
    feature_code = 'inventory.issues.consignment'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('حواله امانی با موفقیت حذف شد.')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Consignment Issue')
        context['confirmation_message'] = _('Do you really want to delete this consignment issue?')
        context['object_details'] = [
            {'label': _('Document Code'), 'value': self.object.document_code},
            {'label': _('Document Date'), 'value': self.object.document_date.strftime('%Y-%m-%d') if self.object.document_date else '-'},
            {'label': _('Created By'), 'value': self.object.created_by.get_full_name() if self.object.created_by else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:issue_consignment')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
            {'label': _('Consignment Issues'), 'url': reverse_lazy('inventory:issue_consignment')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


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

class IssueWarehouseTransferListView(InventoryBaseView, ListView):
    """List view for warehouse transfer issues."""
    template_name = 'inventory/issue_warehouse_transfer.html'
    context_object_name = 'object_list'
    paginate_by = 50
    ordering = ['-id']  # Show newest documents first

    def get_queryset(self):
        """Return empty queryset for now - placeholder view."""
        # Placeholder: return empty queryset until model is defined
        return models.IssuePermanent.objects.none()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        context['page_title'] = _('حواله انتقال بین انبارها')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Issues'), 'url': None},
        ]
        context['create_url'] = None  # Will be set when create view is implemented
        context['create_button_text'] = _('ایجاد حواله انتقال')
        context['create_label'] = _('حواله انتقال بین انبارها')
        context['show_filters'] = True
        context['print_enabled'] = True
        context['show_actions'] = True
        
        return context


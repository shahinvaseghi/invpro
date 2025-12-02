"""
Views for creating Issue documents from Warehouse Request.

This module contains views that allow creating Issue documents directly from Warehouse Request.
Since Warehouse Request is single-line, we directly create the Issue with the line populated.
"""
from typing import Dict, Any
from django.contrib import messages
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from .base import LineFormsetMixin
from .receipts import ReceiptFormMixin
from shared.mixins import FeaturePermissionRequiredMixin
from .. import models
from .. import forms


# ============================================================================
# Create Issue from Warehouse Request Views
# ============================================================================

class IssuePermanentCreateFromWarehouseRequestView(FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create permanent issue from warehouse request."""
    model = models.IssuePermanent
    form_class = forms.IssuePermanentForm
    formset_class = forms.IssuePermanentLineFormSet
    success_url = reverse_lazy('inventory:issue_permanent')
    form_title = _('ایجاد حواله دائم از درخواست انبار')
    receipt_variant = 'issue_permanent'
    list_url_name = 'inventory:issue_permanent'
    lock_url_name = 'inventory:issue_permanent_lock'
    feature_code = 'inventory.issues.permanent'
    required_action = 'create'
    
    def get_warehouse_request(self):
        """Get warehouse request from URL."""
        company_id = self.request.session.get('active_company_id')
        return get_object_or_404(
            models.WarehouseRequest,
            pk=self.kwargs['pk'],
            company_id=company_id,
            request_status='approved',
            is_enabled=1
        )
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add warehouse request to context and populate formset with initial data from session."""
        warehouse_request = self.get_warehouse_request()
        
        # Get quantity and notes from session (set by intermediate selection view)
        session_key = f'warehouse_request_{warehouse_request.pk}_issue_permanent_data'
        session_data = self.request.session.get(session_key, {})
        quantity = session_data.get('quantity', str(warehouse_request.quantity_requested))
        notes = session_data.get('notes', '')
        
        # Build initial data for the line from warehouse request
        initial_data = [{
            'item': warehouse_request.item.pk if warehouse_request.item else None,
            'warehouse': warehouse_request.warehouse.pk if warehouse_request.warehouse else None,
            'unit': warehouse_request.unit,
            'quantity': quantity,
            'line_notes': notes,
            'destination_type': 'company_unit' if warehouse_request.department_unit else '',
            'destination_id': warehouse_request.department_unit.pk if warehouse_request.department_unit else None,
            'destination_code': warehouse_request.department_unit_code,
        }]
        
        # Store initial_data for use in formset
        self._initial_data_for_formset = initial_data
        
        context = super().get_context_data(**kwargs)
        context['warehouse_request'] = warehouse_request
        
        # Override formset with initial data
        if initial_data:
            lines_formset = self.build_line_formset(instance=self.object, initial=initial_data)
            context['lines_formset'] = lines_formset
        
        # Pre-fill form with warehouse request data
        if 'form' in context:
            context['form'].initial['warehouse_request'] = warehouse_request.pk
            if warehouse_request.department_unit:
                context['form'].initial['department_unit'] = warehouse_request.department_unit.pk
        
        return context
    
    def form_valid(self, form):
        """Save document and line formset, linking to warehouse request."""
        warehouse_request = self.get_warehouse_request()
        
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        form.instance.warehouse_request = warehouse_request
        if warehouse_request.department_unit:
            form.instance.department_unit = warehouse_request.department_unit
        
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
        
        # Clear session data after successful creation
        session_key = f'warehouse_request_{warehouse_request.pk}_issue_permanent_data'
        if session_key in self.request.session:
            del self.request.session[session_key]
        
        messages.success(self.request, _('حواله دائم از درخواست انبار با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),
        ]


class IssueConsumptionCreateFromWarehouseRequestView(FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create consumption issue from warehouse request."""
    model = models.IssueConsumption
    form_class = forms.IssueConsumptionForm
    formset_class = forms.IssueConsumptionLineFormSet
    success_url = reverse_lazy('inventory:issue_consumption')
    form_title = _('ایجاد حواله مصرف از درخواست انبار')
    receipt_variant = 'issue_consumption'
    list_url_name = 'inventory:issue_consumption'
    lock_url_name = 'inventory:issue_consumption_lock'
    feature_code = 'inventory.issues.consumption'
    required_action = 'create'
    
    def get_warehouse_request(self):
        """Get warehouse request from URL."""
        company_id = self.request.session.get('active_company_id')
        return get_object_or_404(
            models.WarehouseRequest,
            pk=self.kwargs['pk'],
            company_id=company_id,
            request_status='approved',
            is_enabled=1
        )
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add warehouse request to context and populate formset with initial data from session."""
        warehouse_request = self.get_warehouse_request()
        
        # Get quantity and notes from session (set by intermediate selection view)
        session_key = f'warehouse_request_{warehouse_request.pk}_issue_consumption_data'
        session_data = self.request.session.get(session_key, {})
        quantity = session_data.get('quantity', str(warehouse_request.quantity_requested))
        notes = session_data.get('notes', '')
        
        # Determine consumption_type based on what's available
        consumption_type = 'company_unit'
        destination_id = None
        destination_code = ''
        if warehouse_request.department_unit:
            destination_id = warehouse_request.department_unit.pk
            destination_code = warehouse_request.department_unit_code
        
        # Build initial data for the line from warehouse request
        initial_data = [{
            'item': warehouse_request.item.pk if warehouse_request.item else None,
            'warehouse': warehouse_request.warehouse.pk if warehouse_request.warehouse else None,
            'unit': warehouse_request.unit,
            'quantity': quantity,
            'line_notes': notes,
            'consumption_type': consumption_type,
            'destination_type_choice': consumption_type,
            'destination_id': destination_id,
            'destination_code': destination_code,
        }]
        
        # Store initial_data for use in formset
        self._initial_data_for_formset = initial_data
        
        context = super().get_context_data(**kwargs)
        context['warehouse_request'] = warehouse_request
        
        # Override formset with initial data
        if initial_data:
            lines_formset = self.build_line_formset(instance=self.object, initial=initial_data)
            context['lines_formset'] = lines_formset
        
        # Pre-fill form with warehouse request data
        if 'form' in context:
            if warehouse_request.department_unit:
                context['form'].initial['department_unit'] = warehouse_request.department_unit.pk
        
        return context
    
    def form_valid(self, form):
        """Save document and line formset, linking to warehouse request."""
        warehouse_request = self.get_warehouse_request()
        
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        if warehouse_request.department_unit:
            form.instance.department_unit = warehouse_request.department_unit
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if there are any valid lines
        valid_lines = []
        for line_form in lines_formset.forms:
            if (line_form.cleaned_data and 
                not line_form.errors and
                line_form.cleaned_data.get('item') and 
                not line_form.cleaned_data.get('DELETE', False)):
                valid_lines.append(line_form)
        
        if not valid_lines:
            self.object.delete()
            lines_formset.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        # Clear session data after successful creation
        session_key = f'warehouse_request_{warehouse_request.pk}_issue_consumption_data'
        if session_key in self.request.session:
            del self.request.session[session_key]
        
        messages.success(self.request, _('حواله مصرف از درخواست انبار با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),
        ]


class IssueConsignmentCreateFromWarehouseRequestView(FeaturePermissionRequiredMixin, LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create consignment issue from warehouse request."""
    model = models.IssueConsignment
    form_class = forms.IssueConsignmentForm
    formset_class = forms.IssueConsignmentLineFormSet
    success_url = reverse_lazy('inventory:issue_consignment')
    form_title = _('ایجاد حواله امانی از درخواست انبار')
    receipt_variant = 'issue_consignment'
    list_url_name = 'inventory:issue_consignment'
    lock_url_name = 'inventory:issue_consignment_lock'
    feature_code = 'inventory.issues.consignment'
    required_action = 'create'
    
    def get_warehouse_request(self):
        """Get warehouse request from URL."""
        company_id = self.request.session.get('active_company_id')
        return get_object_or_404(
            models.WarehouseRequest,
            pk=self.kwargs['pk'],
            company_id=company_id,
            request_status='approved',
            is_enabled=1
        )
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add warehouse request to context and populate formset with initial data from session."""
        warehouse_request = self.get_warehouse_request()
        
        # Get quantity and notes from session (set by intermediate selection view)
        session_key = f'warehouse_request_{warehouse_request.pk}_issue_consignment_data'
        session_data = self.request.session.get(session_key, {})
        quantity = session_data.get('quantity', str(warehouse_request.quantity_requested))
        notes = session_data.get('notes', '')
        
        # Build initial data for the line from warehouse request
        initial_data = [{
            'item': warehouse_request.item.pk if warehouse_request.item else None,
            'warehouse': warehouse_request.warehouse.pk if warehouse_request.warehouse else None,
            'unit': warehouse_request.unit,
            'quantity': quantity,
            'line_notes': notes,
            'destination_type': 'company_unit' if warehouse_request.department_unit else '',
            'destination_id': warehouse_request.department_unit.pk if warehouse_request.department_unit else None,
            'destination_code': warehouse_request.department_unit_code,
        }]
        
        # Store initial_data for use in formset
        self._initial_data_for_formset = initial_data
        
        context = super().get_context_data(**kwargs)
        context['warehouse_request'] = warehouse_request
        
        # Override formset with initial data
        if initial_data:
            lines_formset = self.build_line_formset(instance=self.object, initial=initial_data)
            context['lines_formset'] = lines_formset
        
        # Pre-fill form with warehouse request data
        if 'form' in context:
            if warehouse_request.department_unit:
                context['form'].initial['department_unit'] = warehouse_request.department_unit.pk
        
        return context
    
    def form_valid(self, form):
        """Save document and line formset, linking to warehouse request."""
        warehouse_request = self.get_warehouse_request()
        
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        if warehouse_request.department_unit:
            form.instance.department_unit = warehouse_request.department_unit
        
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
        
        # Clear session data after successful creation
        session_key = f'warehouse_request_{warehouse_request.pk}_issue_consignment_data'
        if session_key in self.request.session:
            del self.request.session[session_key]
        
        messages.success(self.request, _('حواله امانی از درخواست انبار با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code']),
        ]


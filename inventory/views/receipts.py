"""
Receipt views for inventory module.

This module contains views for:
- Temporary Receipts
- Permanent Receipts
- Consignment Receipts
- Serial Assignment for Receipts
"""
from typing import Dict, Any, Optional
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from decimal import Decimal, InvalidOperation
import json

from .base import InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, LineFormsetMixin
from shared.mixins import FeaturePermissionRequiredMixin
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
from .. import models
from .. import forms
from ..services import serials as serial_service


# ============================================================================
# Base Classes
# ============================================================================

class DocumentDeleteViewBase(FeaturePermissionRequiredMixin, DocumentLockProtectedMixin, InventoryBaseView, DeleteView):
    """Base class for document delete views with permission checking."""
    owner_field = None  # Disable owner check, we handle it manually
    success_message = _('سند با موفقیت حذف شد.')

    def dispatch(self, request, *args, **kwargs):
        """Check permissions before allowing delete."""
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

    def delete(self, request, *args, **kwargs):
        """Show success message after deletion."""
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        return context


class ReceiptFormMixin(InventoryBaseView):
    """Shared helpers for receipt create/update views."""
    template_name = 'inventory/receipt_form.html'
    form_title = ''
    receipt_variant = ''
    list_url_name = ''
    lock_url_name = ''

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form context including fieldsets and unit options."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        context['receipt_variant'] = self.receipt_variant
        form = context.get('form')
        raw_fieldsets = self.get_fieldsets()
        render_fieldsets = []
        used_fields = []
        if form:
            for title, names in raw_fieldsets:
                bound_fields = []
                for name in names:
                    if name in form.fields:
                        bound_fields.append(form[name])
                        used_fields.append(name)
                if bound_fields:
                    render_fieldsets.append((title, bound_fields))
        context['fieldsets'] = render_fieldsets
        context['used_fields'] = used_fields
        context['list_url'] = reverse_lazy(self.list_url_name)
        context['is_edit'] = bool(getattr(self, 'object', None))

        if form and 'item' in form.fields and 'unit' in form.fields:
            unit_map: Dict[str, list] = {}
            item_queryset = form.fields['item'].queryset
            for item in item_queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
            context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
        else:
            context['unit_options_json'] = mark_safe('{}')

        placeholder_label = str(forms.UNIT_CHOICES[0][1])
        context['unit_placeholder'] = placeholder_label

        instance = getattr(form, 'instance', None)
        context['document_instance'] = instance
        if instance and getattr(instance, 'pk', None):
            if hasattr(instance, 'get_status_display'):
                try:
                    context['document_status_display'] = instance.get_status_display()
                except TypeError:
                    context['document_status_display'] = None
            else:
                context['document_status_display'] = None
            is_locked = bool(getattr(instance, 'is_locked', 0))
            context['document_is_locked'] = is_locked
            if not is_locked and getattr(self, 'lock_url_name', None):
                context['lock_url'] = reverse(self.lock_url_name, args=[instance.pk])
            else:
                context['lock_url'] = None
        else:
            context['document_status_display'] = None
            context['document_is_locked'] = False
            context['lock_url'] = None

        return context

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration. Override in subclasses."""
        return []


# ============================================================================
# Temporary Receipt Views
# ============================================================================

class ReceiptTemporaryListView(InventoryBaseView, ListView):
    """List view for temporary receipts."""
    model = models.ReceiptTemporary
    template_name = 'inventory/receipt_temporary.html'
    context_object_name = 'receipts'
    paginate_by = 50

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Prefetch converted_receipt for linking
        queryset = queryset.select_related('created_by', 'converted_receipt')
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:receipt_temporary_create')
        context['edit_url_name'] = 'inventory:receipt_temporary_edit'
        context['delete_url_name'] = 'inventory:receipt_temporary_delete'
        context['lock_url_name'] = 'inventory:receipt_temporary_lock'
        context['create_label'] = _('Temporary Receipt')
        context['show_qc'] = True
        context['show_conversion'] = True
        context['permanent_receipt_url_name'] = 'inventory:receipt_permanent_edit'
        context['empty_heading'] = _('No Temporary Receipts Found')
        context['empty_text'] = _('Start by creating your first temporary receipt.')
        self.add_delete_permissions_to_context(context, 'inventory.receipts.temporary')
        return context


class ReceiptTemporaryCreateView(ReceiptFormMixin, CreateView):
    """Create view for temporary receipts."""
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    success_url = reverse_lazy('inventory:receipt_temporary')
    form_title = _('ایجاد رسید موقت')
    receipt_variant = 'temporary'
    list_url_name = 'inventory:receipt_temporary'
    lock_url_name = 'inventory:receipt_temporary_lock'

    def form_valid(self, form):
        """Set company, created_by, and status before saving."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        # Set status to AWAITING_INSPECTION so it appears in QC module
        form.instance.status = models.ReceiptTemporary.Status.AWAITING_INSPECTION
        response = super().form_valid(form)
        messages.success(self.request, _('رسید موقت با موفقیت ایجاد شد و برای بازرسی QC ارسال شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Item & Warehouse'), ['item', 'warehouse', 'unit', 'quantity', 'expected_receipt_date']),
            (_('Supplier & References'), ['supplier', 'source_document_type', 'source_document_code', 'qc_approval_notes']),
        ]


class ReceiptTemporaryUpdateView(DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    """Update view for temporary receipts."""
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    success_url = reverse_lazy('inventory:receipt_temporary')
    form_title = _('ویرایش رسید موقت')
    receipt_variant = 'temporary'
    list_url_name = 'inventory:receipt_temporary'
    lock_url_name = 'inventory:receipt_temporary_lock'
    lock_redirect_url_name = 'inventory:receipt_temporary'

    def form_valid(self, form):
        """Set created_by and edited_by before saving."""
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('رسید موقت با موفقیت ویرایش شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Item & Warehouse'), ['item', 'warehouse', 'unit', 'quantity', 'expected_receipt_date']),
            (_('Supplier & References'), ['supplier', 'source_document_type', 'source_document_code', 'qc_approval_notes']),
        ]


class ReceiptTemporaryDeleteView(DocumentDeleteViewBase):
    """Delete view for temporary receipts."""
    model = models.ReceiptTemporary
    template_name = 'inventory/receipt_temporary_confirm_delete.html'
    success_url = reverse_lazy('inventory:receipt_temporary')
    feature_code = 'inventory.receipts.temporary'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('رسید موقت با موفقیت حذف شد.')


class ReceiptTemporaryLockView(DocumentLockView):
    """Lock view for temporary receipts."""
    model = models.ReceiptTemporary
    success_url_name = 'inventory:receipt_temporary'
    success_message = _('رسید موقت قفل شد و دیگر قابل ویرایش نیست.')


class ReceiptTemporarySendToQCView(FeaturePermissionRequiredMixin, InventoryBaseView, View):
    """View to send a temporary receipt to QC inspection."""
    feature_code = 'inventory.receipts.temporary'
    required_action = 'edit_own'
    allow_own_scope = True
    
    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Send receipt to QC."""
        receipt = get_object_or_404(
            models.ReceiptTemporary,
            pk=kwargs['pk'],
            company_id=request.session.get('active_company_id'),
            is_enabled=1
        )
        
        # Check if already locked
        if receipt.is_locked:
            messages.error(request, _('This receipt is already locked and cannot be sent to QC.'))
            return HttpResponseRedirect(reverse('inventory:receipt_temporary'))
        
        # Check if already converted
        if receipt.is_converted:
            messages.error(request, _('This receipt has already been converted to a permanent receipt.'))
            return HttpResponseRedirect(reverse('inventory:receipt_temporary'))
        
        # Check if already in QC
        if receipt.status == models.ReceiptTemporary.Status.AWAITING_INSPECTION:
            messages.info(request, _('This receipt is already awaiting QC inspection.'))
            return HttpResponseRedirect(reverse('inventory:receipt_temporary'))
        
        # Update status to AWAITING_INSPECTION
        receipt.status = models.ReceiptTemporary.Status.AWAITING_INSPECTION
        receipt.edited_by = request.user
        receipt.save(update_fields=['status', 'edited_by'])
        
        messages.success(request, _('Temporary receipt has been sent to QC inspection.'))
        return HttpResponseRedirect(reverse('inventory:receipt_temporary'))


# ============================================================================
# Permanent Receipt Views
# ============================================================================

class ReceiptPermanentListView(InventoryBaseView, ListView):
    """List view for permanent receipts."""
    model = models.ReceiptPermanent
    template_name = 'inventory/receipt_permanent.html'
    context_object_name = 'receipts'
    paginate_by = 50

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Prefetch lines with related items, warehouses, and suppliers for efficient display
        # Also prefetch temporary_receipt and purchase_request for linking
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__supplier'
        ).select_related('created_by', 'temporary_receipt', 'purchase_request')
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:receipt_permanent_create')
        context['edit_url_name'] = 'inventory:receipt_permanent_edit'
        context['delete_url_name'] = 'inventory:receipt_permanent_delete'
        context['lock_url_name'] = 'inventory:receipt_permanent_lock'
        context['create_label'] = _('Permanent Receipt')
        context['show_qc'] = False
        context['show_conversion'] = False
        context['show_temporary_receipt'] = True
        context['show_purchase_request'] = True
        context['empty_heading'] = _('No Permanent Receipts Found')
        context['empty_text'] = _('Start by creating your first permanent receipt.')
        context['serial_url_name'] = 'inventory:receipt_permanent_serials'
        context['temporary_receipt_url_name'] = 'inventory:receipt_temporary_edit'
        context['purchase_request_url_name'] = 'inventory:purchase_request_edit'
        
        self.add_delete_permissions_to_context(context, 'inventory.receipts.permanent')
        return context


class ReceiptPermanentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create view for permanent receipts."""
    model = models.ReceiptPermanent
    form_class = forms.ReceiptPermanentForm
    formset_class = forms.ReceiptPermanentLineFormSet
    success_url = reverse_lazy('inventory:receipt_permanent')
    form_title = _('ایجاد رسید دائم')
    receipt_variant = 'permanent'
    list_url_name = 'inventory:receipt_permanent'
    lock_url_name = 'inventory:receipt_permanent_lock'

    def form_valid(self, form):
        """Save document and line formset."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if we have at least one valid line before saving
        valid_lines = []
        for form in lines_formset.forms:
            if form.cleaned_data and form.cleaned_data.get('item') and not form.cleaned_data.get('DELETE', False):
                valid_lines.append(form)
        
        if not valid_lines:
            # No valid lines, show error and delete the document
            self.object.delete()
            form.add_error(None, _('Please add at least one line with an item.'))
            lines_formset = self.build_line_formset(instance=None)
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید دائم با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code', 'document_date', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request']),
        ]


class ReceiptPermanentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    """Update view for permanent receipts."""
    model = models.ReceiptPermanent
    form_class = forms.ReceiptPermanentForm
    formset_class = forms.ReceiptPermanentLineFormSet
    success_url = reverse_lazy('inventory:receipt_permanent')
    form_title = _('ویرایش رسید دائم')
    receipt_variant = 'permanent'
    list_url_name = 'inventory:receipt_permanent'
    lock_url_name = 'inventory:receipt_permanent_lock'
    lock_redirect_url_name = 'inventory:receipt_permanent'

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
        
        # Check if we have at least one valid line before saving
        valid_lines = []
        for form in lines_formset.forms:
            if form.cleaned_data and form.cleaned_data.get('item') and not form.cleaned_data.get('DELETE', False):
                valid_lines.append(form)
        
        if not valid_lines:
            # No valid lines, show error
            lines_formset.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید دائم با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code', 'document_date', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request']),
        ]


class ReceiptPermanentDeleteView(DocumentDeleteViewBase):
    """Delete view for permanent receipts."""
    model = models.ReceiptPermanent
    template_name = 'inventory/receipt_permanent_confirm_delete.html'
    success_url = reverse_lazy('inventory:receipt_permanent')
    feature_code = 'inventory.receipts.permanent'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('رسید دائم با موفقیت حذف شد.')


class ReceiptPermanentLockView(DocumentLockView):
    """Lock view for permanent receipts."""
    model = models.ReceiptPermanent
    success_url_name = 'inventory:receipt_permanent'
    success_message = _('رسید دائم قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Consignment Receipt Views
# ============================================================================

class ReceiptConsignmentListView(InventoryBaseView, ListView):
    """List view for consignment receipts."""
    model = models.ReceiptConsignment
    template_name = 'inventory/receipt_consignment.html'
    context_object_name = 'receipts'
    paginate_by = 50

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Prefetch lines with related items, warehouses, and suppliers for efficient display
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__supplier'
        ).select_related('created_by')
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:receipt_consignment_create')
        context['edit_url_name'] = 'inventory:receipt_consignment_edit'
        context['delete_url_name'] = 'inventory:receipt_consignment_delete'
        context['lock_url_name'] = 'inventory:receipt_consignment_lock'
        context['create_label'] = _('Consignment Receipt')
        context['show_qc'] = False
        context['show_conversion'] = False
        context['empty_heading'] = _('No Consignment Receipts Found')
        context['empty_text'] = _('Start by creating your first consignment receipt.')
        context['serial_url_name'] = 'inventory:receipt_consignment_serials'
        self.add_delete_permissions_to_context(context, 'inventory.receipts.consignment')
        return context


class ReceiptConsignmentCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create view for consignment receipts."""
    model = models.ReceiptConsignment
    form_class = forms.ReceiptConsignmentForm
    formset_class = forms.ReceiptConsignmentLineFormSet
    success_url = reverse_lazy('inventory:receipt_consignment')
    form_title = _('ایجاد رسید امانی')
    receipt_variant = 'consignment'
    list_url_name = 'inventory:receipt_consignment'
    lock_url_name = 'inventory:receipt_consignment_lock'

    def form_valid(self, form):
        """Save document and line formset."""
        form.instance.company_id = self.request.session.get('active_company_id')
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
        
        messages.success(self.request, _('رسید امانی با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code', 'document_date', 'consignment_contract_code', 'expected_return_date', 'valuation_method', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request', 'ownership_status', 'conversion_receipt', 'conversion_date', 'return_document_id']),
        ]


class ReceiptConsignmentUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    """Update view for consignment receipts."""
    model = models.ReceiptConsignment
    form_class = forms.ReceiptConsignmentForm
    formset_class = forms.ReceiptConsignmentLineFormSet
    success_url = reverse_lazy('inventory:receipt_consignment')
    form_title = _('ویرایش رسید امانی')
    receipt_variant = 'consignment'
    list_url_name = 'inventory:receipt_consignment'
    lock_url_name = 'inventory:receipt_consignment_lock'
    lock_redirect_url_name = 'inventory:receipt_consignment'

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
        
        messages.success(self.request, _('رسید امانی با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['document_code', 'document_date', 'consignment_contract_code', 'expected_return_date', 'valuation_method', 'requires_temporary_receipt', 'temporary_receipt', 'purchase_request', 'warehouse_request', 'ownership_status', 'conversion_receipt', 'conversion_date', 'return_document_id']),
        ]


class ReceiptConsignmentDeleteView(DocumentDeleteViewBase):
    """Delete view for consignment receipts."""
    model = models.ReceiptConsignment
    template_name = 'inventory/receipt_consignment_confirm_delete.html'
    success_url = reverse_lazy('inventory:receipt_consignment')
    feature_code = 'inventory.receipts.consignment'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('رسید امانی با موفقیت حذف شد.')


class ReceiptConsignmentLockView(DocumentLockView):
    """Lock view for consignment receipts."""
    model = models.ReceiptConsignment
    success_url_name = 'inventory:receipt_consignment'
    success_message = _('رسید امانی قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Receipt Serial Assignment Views (Legacy - Single-line receipts)
# ============================================================================

class ReceiptSerialAssignmentBaseView(FeaturePermissionRequiredMixin, View):
    """Base view for managing serials for a receipt (legacy single-line support)."""
    template_name = 'inventory/receipt_serial_assignment.html'
    model = None
    feature_code = None
    serial_url_name = ''
    list_url_name = ''
    edit_url_name = ''
    lock_url_name = ''

    def dispatch(self, request, *args, **kwargs):
        """Check if item requires serial tracking."""
        self.receipt = self.get_receipt()
        if self.receipt.item and self.receipt.item.has_lot_tracking != 1:
            messages.info(request, _('این کالا نیازی به سریال ندارد.'))
            return HttpResponseRedirect(reverse(self.list_url_name))
        return super().dispatch(request, *args, **kwargs)

    def get_receipt(self):
        """Get receipt object."""
        queryset = self.model.objects.all()
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if company_id and hasattr(self.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))

    def get_required_serials(self) -> Optional[int]:
        """Get required number of serials."""
        try:
            return int(Decimal(self.receipt.quantity))
        except (InvalidOperation, TypeError):
            return None

    def get_context_data(self) -> Dict[str, Any]:
        """Get context for serial assignment page."""
        required = self.get_required_serials()
        # Get serials by receipt_document, not ManyToMany (serials may not be linked via M2M yet)
        serials = models.ItemSerial.objects.filter(
            receipt_document=self.receipt,
            company=self.receipt.company,
            is_enabled=1
        ).order_by('serial_code')
        context = {
            'receipt': self.receipt,
            'serials': serials,
            'required_serials': required,
            'serials_count': serials.count(),
            'list_url': reverse(self.list_url_name),
            'edit_url': reverse(self.edit_url_name, args=[self.receipt.pk]),
            'lock_url': reverse(self.lock_url_name, args=[self.receipt.pk]) if self.lock_url_name else None,
            'can_generate': not getattr(self.receipt, 'is_locked', 0),
            'missing_serials': max(required - serials.count(), 0) if required is not None else None,
        }
        return context

    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Handle POST request to generate serials."""
        if getattr(self.receipt, 'is_locked', 0):
            messages.info(request, _('رسید قفل شده و امکان تولید سریال جدید وجود ندارد.'))
            return HttpResponseRedirect(self.get_success_url())

        try:
            created = serial_service.generate_receipt_serials(self.receipt, user=request.user)
        except serial_service.SerialTrackingError as exc:
            messages.error(request, str(exc))
        else:
            if created:
                messages.success(request, _('%(count)s سریال جدید ایجاد شد.') % {'count': created})
            else:
                messages.info(request, _('سریال جدیدی برای ایجاد وجود نداشت.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        """Get success URL after serial generation."""
        return reverse(self.serial_url_name, args=[self.receipt.pk])


class ReceiptPermanentSerialAssignmentView(ReceiptSerialAssignmentBaseView):
    """Serial assignment view for permanent receipts (legacy)."""
    model = models.ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    serial_url_name = 'inventory:receipt_permanent_serials'
    list_url_name = 'inventory:receipt_permanent'
    edit_url_name = 'inventory:receipt_permanent_edit'
    lock_url_name = 'inventory:receipt_permanent_lock'


class ReceiptConsignmentSerialAssignmentView(ReceiptSerialAssignmentBaseView):
    """Serial assignment view for consignment receipts (legacy)."""
    model = models.ReceiptConsignment
    feature_code = 'inventory.receipts.consignment'
    serial_url_name = 'inventory:receipt_consignment_serials'
    list_url_name = 'inventory:receipt_consignment'
    edit_url_name = 'inventory:receipt_consignment_edit'
    lock_url_name = 'inventory:receipt_consignment_lock'


# ============================================================================
# Receipt Line Serial Assignment Views (Multi-line support)
# ============================================================================

class ReceiptLineSerialAssignmentBaseView(FeaturePermissionRequiredMixin, View):
    """Base view for managing serials for a specific receipt line."""
    template_name = 'inventory/receipt_serial_assignment.html'
    line_model = None
    document_model = None
    feature_code = None
    serial_url_name = ''
    list_url_name = ''
    edit_url_name = ''
    lock_url_name = ''

    def dispatch(self, request, *args, **kwargs):
        """Check if item requires serial tracking."""
        self.document = self.get_document()
        self.line = self.get_line()
        if self.line.item and self.line.item.has_lot_tracking != 1:
            messages.info(request, _('این کالا نیازی به سریال ندارد.'))
            return HttpResponseRedirect(reverse(self.edit_url_name, args=[self.document.pk]))
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

    def get_required_serials(self) -> Optional[int]:
        """Get required number of serials."""
        try:
            return int(Decimal(self.line.quantity))
        except (InvalidOperation, TypeError):
            return None

    def get_context_data(self) -> Dict[str, Any]:
        """Get context for serial assignment page."""
        required = self.get_required_serials()
        # Get serials by receipt_line_reference, not ManyToMany (serials may not be linked via M2M yet)
        line_reference = f"{self.line.__class__.__name__}:{self.line.pk}"
        serials = models.ItemSerial.objects.filter(
            receipt_line_reference=line_reference,
            company=self.line.company,
            is_enabled=1
        ).order_by('serial_code')
        context = {
            'line': self.line,
            'document': self.document,
            'serials': serials,
            'required_serials': required,
            'serials_count': serials.count(),
            'list_url': reverse(self.list_url_name),
            'edit_url': reverse(self.edit_url_name, args=[self.document.pk]),
            'lock_url': reverse(self.lock_url_name, args=[self.document.pk]) if self.lock_url_name else None,
            'can_generate': not getattr(self.document, 'is_locked', 0),
            'missing_serials': max(required - serials.count(), 0) if required is not None else None,
        }
        return context

    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Handle POST request to generate serials."""
        if getattr(self.document, 'is_locked', 0):
            messages.info(request, _('رسید قفل شده و امکان تولید سریال جدید وجود ندارد.'))
            return HttpResponseRedirect(self.get_success_url())

        try:
            created = serial_service.generate_receipt_line_serials(self.line, user=request.user)
        except serial_service.SerialTrackingError as exc:
            messages.error(request, str(exc))
        else:
            if created:
                messages.success(request, _('%(count)s سریال جدید ایجاد شد.') % {'count': created})
            else:
                messages.info(request, _('سریال جدیدی برای ایجاد وجود نداشت.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        """Get success URL after serial generation."""
        return reverse(self.edit_url_name, args=[self.document.pk])


class ReceiptPermanentLineSerialAssignmentView(ReceiptLineSerialAssignmentBaseView):
    """Serial assignment view for permanent receipt lines."""
    line_model = models.ReceiptPermanentLine
    document_model = models.ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    serial_url_name = 'inventory:receipt_permanent_line_serials'
    list_url_name = 'inventory:receipt_permanent'
    edit_url_name = 'inventory:receipt_permanent_edit'
    lock_url_name = 'inventory:receipt_permanent_lock'


class ReceiptConsignmentLineSerialAssignmentView(ReceiptLineSerialAssignmentBaseView):
    """Serial assignment view for consignment receipt lines."""
    line_model = models.ReceiptConsignmentLine
    document_model = models.ReceiptConsignment
    feature_code = 'inventory.receipts.consignment'
    serial_url_name = 'inventory:receipt_consignment_line_serials'
    list_url_name = 'inventory:receipt_consignment'
    edit_url_name = 'inventory:receipt_consignment_edit'
    lock_url_name = 'inventory:receipt_consignment_lock'


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
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from decimal import Decimal, InvalidOperation
import json

from .base import InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView, DocumentUnlockView, LineFormsetMixin
from shared.mixins import FeaturePermissionRequiredMixin
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
from .. import models
from .. import forms
from ..services import serials as serial_service
from django.db.models import Q
import logging

logger = logging.getLogger('inventory.views.receipts')


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
        logger.info("=" * 80)
        logger.info("ReceiptFormMixin.get_context_data() called")
        logger.info(f"Request method: {self.request.method}")
        logger.info(f"Has object: {hasattr(self, 'object')}")
        if hasattr(self, 'object') and self.object:
            logger.info(f"Object: {self.object}")
            logger.info(f"Object pk: {self.object.pk}")
            logger.info(f"Object is_locked: {getattr(self.object, 'is_locked', 'N/A')}")
        context = super().get_context_data(**kwargs)
        logger.info(f"Context keys: {list(context.keys())}")
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

        # Add item types, categories, and subcategories for filtering
        company_id = self.request.session.get('active_company_id')
        if company_id:
            context['item_types'] = models.ItemType.objects.filter(company_id=company_id, is_enabled=1).order_by('name')
            context['item_categories'] = models.ItemCategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')
            context['item_subcategories'] = models.ItemSubcategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')
        else:
            context['item_types'] = models.ItemType.objects.none()
            context['item_categories'] = models.ItemCategory.objects.none()
            context['item_subcategories'] = models.ItemSubcategory.objects.none()
        
        # Add current filter selections to context
        context['current_item_type'] = self.request.GET.get('item_type')
        context['current_category'] = self.request.GET.get('category')
        context['current_subcategory'] = self.request.GET.get('subcategory')
        context['current_item_search'] = self.request.GET.get('item_search')

        instance = getattr(form, 'instance', None)
        context['document_instance'] = instance
        logger.info(f"Document instance from form: {instance}")
        if instance and getattr(instance, 'pk', None):
            logger.info(f"Document instance pk: {instance.pk}")
            logger.info(f"Document instance is_locked: {getattr(instance, 'is_locked', 'N/A')}")
            if hasattr(instance, 'get_status_display'):
                try:
                    context['document_status_display'] = instance.get_status_display()
                except TypeError:
                    context['document_status_display'] = None
            else:
                context['document_status_display'] = None
            is_locked = bool(getattr(instance, 'is_locked', 0))
            context['document_is_locked'] = is_locked
            logger.info(f"document_is_locked set to: {is_locked}")
            if not is_locked and getattr(self, 'lock_url_name', None):
                context['lock_url'] = reverse(self.lock_url_name, args=[instance.pk])
            else:
                context['lock_url'] = None
        else:
            logger.info("No document instance or no pk")
            context['document_status_display'] = None
            context['document_is_locked'] = False
            context['lock_url'] = None
        
        # Log lines_formset info
        if 'lines_formset' in context:
            lines_formset = context['lines_formset']
            logger.info(f"lines_formset in context, forms count: {len(lines_formset.forms)}")
            for i, form in enumerate(lines_formset.forms):
                if form.instance.pk:
                    logger.info(f"  Formset form {i}: instance pk={form.instance.pk}, item_id={getattr(form.instance, 'item_id', None)}")
                    if hasattr(form, 'fields') and 'item' in form.fields:
                        item_field = form.fields['item']
                        logger.info(f"    Item field queryset count: {item_field.queryset.count()}")
                        logger.info(f"    Item field value: {form['item'].value()}")
                        item_id = getattr(form.instance, 'item_id', None)
                        if item_id:
                            try:
                                in_queryset = item_field.queryset.filter(pk=item_id).exists()
                                logger.info(f"    Instance item_id={item_id} in queryset: {in_queryset}")
                            except Exception as e:
                                logger.warning(f"    Error checking item in queryset: {e}")
        else:
            logger.info("lines_formset NOT in context")

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
        """Prefetch related objects for efficient display and apply filters."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        queryset = queryset.filter(is_enabled=1)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.temporary', 'created_by')
        # Prefetch lines with related items, warehouses, and suppliers for efficient display
        # Also prefetch converted_receipt for linking
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
        ).select_related('created_by', 'converted_receipt')
        queryset = self._apply_filters(queryset)
        return queryset.distinct()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:receipt_temporary_create')
        context['detail_url_name'] = 'inventory:receipt_temporary_detail'
        context['edit_url_name'] = 'inventory:receipt_temporary_edit'
        context['delete_url_name'] = 'inventory:receipt_temporary_delete'
        context['lock_url_name'] = 'inventory:receipt_temporary_lock'
        context['unlock_url_name'] = 'inventory:receipt_temporary_unlock'
        context['create_label'] = _('Temporary Receipt')
        context['show_qc'] = True
        context['show_conversion'] = True
        context['permanent_receipt_url_name'] = 'inventory:receipt_permanent_edit'
        context['empty_heading'] = _('No Temporary Receipts Found')
        context['empty_text'] = _('Start by creating your first temporary receipt.')
        self.add_delete_permissions_to_context(context, 'inventory.receipts.temporary')
        # Add unlock permissions
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        context['can_unlock_own'] = self.request.user.is_superuser or has_feature_permission(
            permissions, 'inventory.receipts.temporary', 'unlock_own', allow_own_scope=True
        )
        context['can_unlock_other'] = self.request.user.is_superuser or has_feature_permission(
            permissions, 'inventory.receipts.temporary', 'unlock_other', allow_own_scope=False
        )
        context['status_filter'] = self.request.GET.get('status', '')
        context['converted_filter'] = self.request.GET.get('converted', '')
        context['search_query'] = self.request.GET.get('search', '').strip()
        context['stats'] = self._get_stats()
        return context

    def _apply_filters(self, queryset):
        """Apply status, conversion, and search filters."""
        status_param = self.request.GET.get('status')
        status_map = {
            'draft': models.ReceiptTemporary.Status.DRAFT,
            'awaiting_qc': models.ReceiptTemporary.Status.AWAITING_INSPECTION,
            'qc_passed': models.ReceiptTemporary.Status.APPROVED,
            'qc_failed': models.ReceiptTemporary.Status.CLOSED,
        }
        if status_param in status_map:
            queryset = queryset.filter(status=status_map[status_param])
        
        converted_param = self.request.GET.get('converted')
        if converted_param == '1':
            queryset = queryset.filter(is_converted=1)
        elif converted_param == '0':
            queryset = queryset.filter(is_converted=0)
        
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(document_code__icontains=search_query) |
                Q(lines__item__name__icontains=search_query) |
                Q(lines__item__item_code__icontains=search_query)
            )
        return queryset

    def _get_stats(self) -> Dict[str, int]:
        """Return aggregate stats for summary cards."""
        stats = {
            'total': 0,
            'awaiting_qc': 0,
            'qc_passed': 0,
            'converted': 0,
        }
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return stats
        base_qs = models.ReceiptTemporary.objects.filter(company_id=company_id, is_enabled=1)
        stats['total'] = base_qs.count()
        stats['awaiting_qc'] = base_qs.filter(status=models.ReceiptTemporary.Status.AWAITING_INSPECTION).count()
        stats['qc_passed'] = base_qs.filter(status=models.ReceiptTemporary.Status.APPROVED).count()
        stats['converted'] = base_qs.filter(is_converted=1).count()
        return stats


class ReceiptTemporaryCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    """Create view for temporary receipts."""
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    formset_class = forms.ReceiptTemporaryLineFormSet
    success_url = reverse_lazy('inventory:receipt_temporary')
    form_title = _('ایجاد رسید موقت')
    receipt_variant = 'temporary'
    list_url_name = 'inventory:receipt_temporary'
    lock_url_name = 'inventory:receipt_temporary_lock'

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
            if form.cleaned_data and form.cleaned_data.get('item') and not form.cleaned_data.get('DELETE', False):
                valid_lines.append(form)
        
        if not valid_lines:
            self.object.delete()
            form.add_error(None, _('Please add at least one line with an item.'))
            lines_formset = self.build_line_formset(instance=None)
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )

        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید موقت با موفقیت ایجاد شد. برای ارسال به QC از دکمه‌ی "ارسال به QC" استفاده کنید.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['expected_receipt_date', 'supplier', 'source_document_type', 'source_document_code', 'qc_approval_notes']),
        ]


class ReceiptTemporaryDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing temporary receipts (read-only)."""
    model = models.ReceiptTemporary
    template_name = 'inventory/receipt_detail.html'
    context_object_name = 'receipt'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.temporary', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'supplier')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['receipt_variant'] = 'temporary'
        context['list_url'] = reverse('inventory:receipt_temporary')
        context['edit_url'] = reverse('inventory:receipt_temporary_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class ReceiptPermanentDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing permanent receipts (read-only)."""
    model = models.ReceiptPermanent
    template_name = 'inventory/receipt_detail.html'
    context_object_name = 'receipt'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.permanent', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__supplier'
        ).select_related('created_by', 'temporary_receipt', 'purchase_request')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['receipt_variant'] = 'permanent'
        context['list_url'] = reverse('inventory:receipt_permanent')
        context['edit_url'] = reverse('inventory:receipt_permanent_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class ReceiptConsignmentDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing consignment receipts (read-only)."""
    model = models.ReceiptConsignment
    template_name = 'inventory/receipt_detail.html'
    context_object_name = 'receipt'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.consignment', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__supplier'
        ).select_related('created_by')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        context['receipt_variant'] = 'consignment'
        context['list_url'] = reverse('inventory:receipt_consignment')
        context['edit_url'] = reverse('inventory:receipt_consignment_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class ReceiptTemporaryUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    """Update view for temporary receipts."""
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    formset_class = forms.ReceiptTemporaryLineFormSet
    success_url = reverse_lazy('inventory:receipt_temporary')
    form_title = _('ویرایش رسید موقت')
    receipt_variant = 'temporary'
    list_url_name = 'inventory:receipt_temporary'
    lock_url_name = 'inventory:receipt_temporary_lock'
    lock_redirect_url_name = 'inventory:receipt_temporary'

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        logger.info("=" * 80)
        logger.info("ReceiptTemporaryUpdateView.get_queryset() called")
        logger.info(f"Request method: {self.request.method}")
        logger.info(f"Request path: {self.request.path}")
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.temporary', 'created_by')
        # ReceiptTemporaryLine doesn't have supplier field (supplier is on ReceiptTemporary header)
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse'
        ).select_related('created_by', 'supplier')
        logger.info(f"Queryset count: {queryset.count()}")
        return queryset
    
    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        logger.info("=" * 80)
        logger.info("ReceiptTemporaryUpdateView.get() called")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"URL kwargs: {kwargs}")
        result = super().get(request, *args, **kwargs)
        logger.info(f"Response status code: {result.status_code}")
        return result

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
            lines_formset.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )

        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('رسید موقت با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('Document Info'), ['expected_receipt_date', 'supplier', 'source_document_type', 'source_document_code', 'qc_approval_notes']),
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


class ReceiptTemporaryUnlockView(DocumentUnlockView):
    """Unlock view for temporary receipts."""
    model = models.ReceiptTemporary
    success_url_name = 'inventory:receipt_temporary'
    success_message = _('رسید موقت از قفل خارج شد و قابل ویرایش است.')
    feature_code = 'inventory.receipts.temporary'
    required_action = 'unlock_own'


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
        
        # Check current status
        if receipt.status == models.ReceiptTemporary.Status.AWAITING_INSPECTION:
            messages.info(request, _('This receipt is already awaiting QC inspection.'))
            return HttpResponseRedirect(reverse('inventory:receipt_temporary'))
        if receipt.status == models.ReceiptTemporary.Status.APPROVED:
            messages.info(request, _('This receipt has already been approved by QC.'))
            return HttpResponseRedirect(reverse('inventory:receipt_temporary'))
        if receipt.status == models.ReceiptTemporary.Status.CLOSED:
            messages.error(request, _('This receipt is closed/rejected and cannot be sent to QC.'))
            return HttpResponseRedirect(reverse('inventory:receipt_temporary'))
        if receipt.status != models.ReceiptTemporary.Status.DRAFT:
            messages.error(request, _('Only draft receipts can be sent to QC.'))
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
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.permanent', 'created_by')
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
        context['detail_url_name'] = 'inventory:receipt_permanent_detail'
        context['edit_url_name'] = 'inventory:receipt_permanent_edit'
        context['delete_url_name'] = 'inventory:receipt_permanent_delete'
        context['lock_url_name'] = 'inventory:receipt_permanent_lock'
        context['unlock_url_name'] = 'inventory:receipt_permanent_unlock'
        context['create_label'] = _('Permanent Receipt')
        context['show_qc'] = False
        context['show_conversion'] = False
        context['show_temporary_receipt'] = True
        context['show_purchase_request'] = True
        self.add_delete_permissions_to_context(context, 'inventory.receipts.permanent')
        # Add unlock permissions
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        context['can_unlock_own'] = self.request.user.is_superuser or has_feature_permission(
            permissions, 'inventory.receipts.permanent', 'unlock_own', allow_own_scope=True
        )
        context['can_unlock_other'] = self.request.user.is_superuser or has_feature_permission(
            permissions, 'inventory.receipts.permanent', 'unlock_other', allow_own_scope=False
        )
        context['empty_heading'] = _('No Permanent Receipts Found')
        context['empty_text'] = _('Start by creating your first permanent receipt.')
        # serial_url_name removed - serials are managed per line in edit view
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
        
        # Get temporary_receipt from form to pass to formset forms
        temp_receipt = form.cleaned_data.get('temporary_receipt') if hasattr(form, 'cleaned_data') else None
        
        # Also check POST data directly in case cleaned_data is not available
        if not temp_receipt:
            temp_receipt_id = self.request.POST.get('temporary_receipt', '')
            if temp_receipt_id:
                try:
                    temp_receipt = models.ReceiptTemporary.objects.get(pk=temp_receipt_id, company_id=self.object.company_id)
                except (models.ReceiptTemporary.DoesNotExist, ValueError):
                    pass
        
        # Also check if temporary_receipt is set on the saved object
        if not temp_receipt and self.object.temporary_receipt_id:
            temp_receipt = self.object.temporary_receipt
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object)
        
        # Pass temporary_receipt to all forms in formset for validation BEFORE validation
        # Also set document on all instances so they can access it in clean_item
        if temp_receipt:
            for form in lines_formset.forms:
                form._temp_receipt = temp_receipt
                # Set document on instance so clean_item can access it
                if hasattr(form, 'instance') and form.instance:
                    form.instance.document = self.object
        
        if not lines_formset.is_valid():
            # Delete the document since formset validation failed
            self.object.delete()
            # Reset form.instance to None so template renders in create mode
            form.instance = self.model()
            form.instance.pk = None
            # Rebuild formset with None instance but keep the same POST data to preserve validation errors
            lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
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

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.permanent', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__supplier'
        ).select_related('created_by', 'temporary_receipt', 'purchase_request', 'warehouse_request')
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


class ReceiptPermanentUnlockView(DocumentUnlockView):
    """Unlock view for permanent receipts."""
    model = models.ReceiptPermanent
    success_url_name = 'inventory:receipt_permanent'
    success_message = _('رسید دائم از قفل خارج شد و قابل ویرایش است.')
    feature_code = 'inventory.receipts.permanent'
    required_action = 'unlock_own'


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
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.consignment', 'created_by')
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
        context['detail_url_name'] = 'inventory:receipt_consignment_detail'
        context['edit_url_name'] = 'inventory:receipt_consignment_edit'
        context['delete_url_name'] = 'inventory:receipt_consignment_delete'
        context['lock_url_name'] = 'inventory:receipt_consignment_lock'
        context['unlock_url_name'] = 'inventory:receipt_consignment_unlock'
        context['create_label'] = _('Consignment Receipt')
        context['show_qc'] = False
        context['show_conversion'] = False
        context['empty_heading'] = _('No Consignment Receipts Found')
        context['empty_text'] = _('Start by creating your first consignment receipt.')
        # serial_url_name removed - serials are managed per line in edit view
        self.add_delete_permissions_to_context(context, 'inventory.receipts.consignment')
        # Add unlock permissions
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        context['can_unlock_own'] = self.request.user.is_superuser or has_feature_permission(
            permissions, 'inventory.receipts.consignment', 'unlock_own', allow_own_scope=True
        )
        context['can_unlock_other'] = self.request.user.is_superuser or has_feature_permission(
            permissions, 'inventory.receipts.consignment', 'unlock_other', allow_own_scope=False
        )
        context['temporary_receipt_url_name'] = 'inventory:receipt_temporary_edit'
        context['purchase_request_url_name'] = 'inventory:purchase_request_edit'
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


# ============================================================================
# Create Receipt from Purchase Request Views
# ============================================================================

class ReceiptTemporaryCreateFromPurchaseRequestView(ReceiptTemporaryCreateView):
    """Create temporary receipt from purchase request."""
    
    def get_purchase_request(self):
        """Get purchase request from URL."""
        from inventory.models import PurchaseRequest
        company_id = self.request.session.get('active_company_id')
        return get_object_or_404(
            PurchaseRequest,
            pk=self.kwargs['pk'],
            company_id=company_id,
            status=PurchaseRequest.Status.APPROVED,
            is_enabled=1
        )
    
    def get_context_data(self, **kwargs):
        """Add purchase request to context and pre-populate formset."""
        import logging
        logger = logging.getLogger('inventory.views.receipts')
        logger.info("=" * 80)
        logger.info("ReceiptTemporaryCreateFromPurchaseRequestView.get_context_data called")
        
        purchase_request = self.get_purchase_request()
        logger.info(f"Purchase request: {purchase_request.request_code} (pk={purchase_request.pk})")
        
        # Get selected lines from session BEFORE calling super().get_context_data
        session_key = f'purchase_request_{purchase_request.pk}_receipt_temporary_lines'
        logger.info(f"Looking for session key: {session_key}")
        logger.info(f"All session keys: {list(self.request.session.keys())}")
        selected_lines_data = self.request.session.get(session_key, [])
        logger.info(f"Retrieved from session: {selected_lines_data}")
        logger.info(f"Number of selected lines: {len(selected_lines_data)}")
        
        # Build initial data BEFORE calling super().get_context_data
        initial_data = []
        if selected_lines_data:
            logger.info("=" * 80)
            logger.info("Building initial_data BEFORE super().get_context_data")
            from inventory.models import PurchaseRequestLine
            from decimal import Decimal
            
            for idx, line_data in enumerate(selected_lines_data):
                logger.info(f"Processing line_data[{idx}]: {line_data}")
                try:
                    line_id = line_data.get('line_id')
                    quantity = line_data.get('quantity')
                    logger.info(f"  Looking for PurchaseRequestLine pk={line_id}, document={purchase_request.pk}")
                    
                    line = PurchaseRequestLine.objects.get(
                        pk=line_id,
                        document=purchase_request
                    )
                    logger.info(f"  Found line: item={line.item.name if line.item else 'None'} (pk={line.item.pk if line.item else None}), "
                               f"unit={line.unit}, quantity_requested={line.quantity_requested}")
                    
                    # Don't set warehouse - let user select it
                    # Warehouse should be empty so user can choose from allowed warehouses
                    
                    initial_item = {
                        'item': line.item.pk if line.item else None,
                        'warehouse': None,  # Leave empty for user to select
                        'unit': line.unit,
                        'quantity': str(Decimal(quantity)),
                        'entered_unit': line.unit,
                        'entered_quantity': str(Decimal(quantity)),
                    }
                    initial_data.append(initial_item)
                    logger.info(f"  Added initial data: {initial_item}")
                except PurchaseRequestLine.DoesNotExist as e:
                    logger.error(f"  PurchaseRequestLine {line_data.get('line_id')} not found: {e}")
                    pass
                except Exception as e:
                    logger.error(f"  Error processing line_data[{idx}]: {e}", exc_info=True)
                    pass
            
            logger.info(f"Total initial_data items: {len(initial_data)}")
            logger.info(f"Initial data summary: {[{'item': d.get('item'), 'warehouse': d.get('warehouse'), 'quantity': d.get('quantity')} for d in initial_data]}")
        
        # Store initial_data as instance attribute so we can use it after super().get_context_data
        self._initial_data_for_formset = initial_data
        
        # Now call super().get_context_data - this will call LineFormsetMixin.get_context_data
        # which will build the formset, but we'll override it after
        context = super().get_context_data(**kwargs)
        context['purchase_request'] = purchase_request
        
        # Now override the formset with our initial data
        if initial_data and 'lines_formset' in context:
            logger.info("=" * 80)
            logger.info("OVERRIDING formset with initial data")
            logger.info(f"Current formset has {len(context['lines_formset'].forms)} forms")
            logger.info(f"Using initial_data with {len(initial_data)} items")
            
            # Build formset with initial data
            logger.info("Building formset with initial data")
            company_id = self.request.session.get('active_company_id')
            # Build formset with initial data - Django formsets accept initial as a list of dicts
            # But we need to ensure enough forms are created (Django only creates forms based on extra + initial)
            # So we need to manually adjust the formset after creation
            formset_kwargs = {
                'instance': None,
                'prefix': self.formset_prefix,
                'company_id': company_id,
                'initial': initial_data,  # Pass initial data to formset constructor
            }
            lines_formset = self.formset_class(**formset_kwargs)
            
            # Django creates forms based on: initial data + extra
            # If we have 3 initial items and extra=1, Django creates 4 forms (3 from initial + 1 extra)
            # But we want exactly len(initial_data) forms, so we need to adjust
            logger.info(f"Formset created with {len(lines_formset.forms)} forms (initial_data has {len(initial_data)} items)")
            
            # Ensure we have exactly len(initial_data) forms
            while len(lines_formset.forms) < len(initial_data):
                # Add more forms if needed
                lines_formset.forms.append(lines_formset._construct_form(len(lines_formset.forms)))
                logger.info(f"Added form {len(lines_formset.forms) - 1}")
            
            # Remove extra forms beyond initial_data length
            while len(lines_formset.forms) > len(initial_data):
                lines_formset.forms.pop()
                logger.info(f"Removed extra form, now {len(lines_formset.forms)} forms")
            
            # Update management form TOTAL_FORMS to match initial_data length
            if lines_formset.management_form:
                lines_formset.management_form.initial['TOTAL_FORMS'] = len(initial_data)
                lines_formset.management_form.fields['TOTAL_FORMS'].initial = len(initial_data)
                # Also update the bound value if form is bound
                if hasattr(lines_formset.management_form, 'data'):
                    lines_formset.management_form.data = lines_formset.management_form.data.copy()
                    lines_formset.management_form.data[lines_formset.management_form.add_prefix('TOTAL_FORMS')] = str(len(initial_data))
            
            # Ensure querysets include selected items (for item field)
            from django.db.models import Q
            
            for idx, form in enumerate(lines_formset.forms):
                if idx < len(initial_data):
                    init_data = initial_data[idx]
                    logger.info(f"Processing form {idx} with initial data: {init_data}")
                    
                    # For item field, ensure it's in queryset even if user doesn't have permission
                    if 'item' in form.fields and init_data.get('item'):
                        item_id = init_data['item']
                        field = form.fields['item']
                        if hasattr(field, 'queryset') and hasattr(field.queryset, 'model'):
                            # Check if item is in queryset
                            if not field.queryset.filter(pk=item_id).exists():
                                # Add it to queryset
                                field.queryset = field.queryset.model.objects.filter(
                                    Q(pk=item_id) | Q(pk__in=field.queryset.values_list('pk', flat=True))
                                )
                                logger.info(f"  Added item {item_id} to queryset")
                            
                            # Set initial to the actual object
                            try:
                                obj = field.queryset.model.objects.get(pk=item_id)
                                field.initial = obj
                                form.initial['item'] = obj
                                logger.info(f"  Set item initial to object: {obj}")
                            except field.queryset.model.DoesNotExist:
                                logger.warning(f"  Item {item_id} not found")
                    
                    # Keep form unbound so initial values are displayed
                    form.is_bound = False
                    logger.info(f"  Form {idx} kept unbound, is_bound: {form.is_bound}")
                else:
                    form.is_bound = False
                    logger.info(f"Form {idx} has no initial data, keeping unbound")
            
            logger.info(f"Formset created with {len(lines_formset.forms)} forms")
            logger.info("=" * 80)
            context['lines_formset'] = lines_formset
        else:
            logger.warning("No initial_data, building empty formset")
            lines_formset = self.build_line_formset(instance=None)
            context['lines_formset'] = lines_formset
        
        # Set purchase_request in form
        if 'form' in context:
            logger.info("Setting purchase_request in form initial")
            context['form'].initial['source_document_type'] = 'Purchase Request'
            context['form'].initial['source_document_code'] = purchase_request.request_code
            logger.info(f"Form initial source_document_type: Purchase Request")
            logger.info(f"Form initial source_document_code: {purchase_request.request_code}")
        
        logger.info("=" * 80)
        logger.info("get_context_data completed")
        logger.info(f"Context keys: {list(context.keys())}")
        logger.info(f"lines_formset in context: {'lines_formset' in context}")
        if 'lines_formset' in context:
            logger.info(f"lines_formset has {len(context['lines_formset'].forms)} forms")
        logger.info("=" * 80)
        return context
    
    def form_valid(self, form):
        """Save receipt and update purchase request line."""
        purchase_request = self.get_purchase_request()
        
        # Get selected lines from session
        session_key = f'purchase_request_{purchase_request.pk}_receipt_temporary_lines'
        selected_lines_data = self.request.session.get(session_key, [])
        
        if not selected_lines_data:
            messages.error(self.request, _('خطا: اطلاعات ردیف‌های انتخاب شده یافت نشد.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))
        
        # Save receipt
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        self.object = form.save()
        
        # Update purchase request line quantity_fulfilled
        from inventory.models import PurchaseRequestLine
        from decimal import Decimal
        for line_data in selected_lines_data:
            try:
                line = PurchaseRequestLine.objects.get(
                    pk=line_data['line_id'],
                    document=purchase_request
                )
                quantity = Decimal(line_data['quantity'])
                line.quantity_fulfilled += quantity
                if line.quantity_fulfilled > line.quantity_requested:
                    line.quantity_fulfilled = line.quantity_requested
                line.save()
            except PurchaseRequestLine.DoesNotExist:
                pass
        
        # Clear session
        if session_key in self.request.session:
            del self.request.session[session_key]
        
        messages.success(self.request, _('رسید موقت با موفقیت از درخواست خرید ایجاد شد.'))
        return HttpResponseRedirect(reverse('inventory:receipt_temporary'))


class ReceiptPermanentCreateFromPurchaseRequestView(ReceiptPermanentCreateView):
    """Create permanent receipt from purchase request."""
    
    def get_purchase_request(self):
        """Get purchase request from URL."""
        from inventory.models import PurchaseRequest
        company_id = self.request.session.get('active_company_id')
        return get_object_or_404(
            PurchaseRequest,
            pk=self.kwargs['pk'],
            company_id=company_id,
            status=PurchaseRequest.Status.APPROVED,
            is_enabled=1
        )
    
    def get_context_data(self, **kwargs):
        """Add purchase request to context."""
        import logging
        logger = logging.getLogger('inventory.views.receipts')
        logger.info("=" * 80)
        logger.info("ReceiptPermanentCreateFromPurchaseRequestView.get_context_data called")
        
        purchase_request = self.get_purchase_request()
        logger.info(f"Purchase request: {purchase_request.request_code} (pk={purchase_request.pk})")
        
        # Get selected lines from session BEFORE calling super().get_context_data
        # This way we can build formset with initial data before LineFormsetMixin builds it
        session_key = f'purchase_request_{purchase_request.pk}_receipt_permanent_lines'
        logger.info(f"Looking for session key: {session_key}")
        logger.info(f"All session keys: {list(self.request.session.keys())}")
        selected_lines_data = self.request.session.get(session_key, [])
        logger.info(f"Retrieved from session: {selected_lines_data}")
        logger.info(f"Number of selected lines: {len(selected_lines_data)}")
        
        # Build initial data BEFORE calling super().get_context_data
        initial_data = []
        if selected_lines_data:
            logger.info("=" * 80)
            logger.info("Building initial_data BEFORE super().get_context_data")
            from inventory.models import PurchaseRequestLine
            from decimal import Decimal
            
            for idx, line_data in enumerate(selected_lines_data):
                logger.info(f"Processing line_data[{idx}]: {line_data}")
                try:
                    line_id = line_data.get('line_id')
                    quantity = line_data.get('quantity')
                    logger.info(f"  Looking for PurchaseRequestLine pk={line_id}, document={purchase_request.pk}")
                    
                    line = PurchaseRequestLine.objects.get(
                        pk=line_id,
                        document=purchase_request
                    )
                    logger.info(f"  Found line: item={line.item.name if line.item else 'None'} (pk={line.item.pk if line.item else None}), "
                               f"unit={line.unit}, quantity_requested={line.quantity_requested}")
                    
                    # Don't set warehouse - let user select it
                    # Warehouse should be empty so user can choose from allowed warehouses
                    
                    initial_item = {
                        'item': line.item.pk if line.item else None,
                        'warehouse': None,  # Leave empty for user to select
                        'unit': line.unit,
                        'quantity': str(Decimal(quantity)),
                        'entered_unit': line.unit,
                        'entered_quantity': str(Decimal(quantity)),
                    }
                    initial_data.append(initial_item)
                    logger.info(f"  Added initial data: {initial_item}")
                except PurchaseRequestLine.DoesNotExist as e:
                    logger.error(f"  PurchaseRequestLine {line_data.get('line_id')} not found: {e}")
                    pass
                except Exception as e:
                    logger.error(f"  Error processing line_data[{idx}]: {e}", exc_info=True)
                    pass
            
            logger.info(f"Total initial_data items: {len(initial_data)}")
            logger.info(f"Initial data summary: {[{'item': d.get('item'), 'warehouse': d.get('warehouse'), 'quantity': d.get('quantity')} for d in initial_data]}")
        
        # Store initial_data as instance attribute so we can use it after super().get_context_data
        self._initial_data_for_formset = initial_data
        
        # Now call super().get_context_data - this will call LineFormsetMixin.get_context_data
        # which will build the formset, but we'll override it after
        context = super().get_context_data(**kwargs)
        context['purchase_request'] = purchase_request
        
        # Now override the formset with our initial data
        if initial_data and 'lines_formset' in context:
            logger.info("=" * 80)
            logger.info("OVERRIDING formset with initial data")
            logger.info(f"Current formset has {len(context['lines_formset'].forms)} forms")
            logger.info(f"Using initial_data with {len(initial_data)} items")
            
            # Build formset with initial data - Django formsets accept initial as a list of dicts
            # But we need to ensure enough forms are created (Django only creates forms based on extra + initial)
            # So we need to manually adjust the formset after creation
            logger.info("Building formset with initial data")
            company_id = self.request.session.get('active_company_id')
            formset_kwargs = {
                'instance': None,
                'prefix': self.formset_prefix,
                'company_id': company_id,
                'initial': initial_data,  # Pass initial data to formset constructor
            }
            lines_formset = self.formset_class(**formset_kwargs)
            
            # Django creates forms based on: initial data + extra
            # If we have 3 initial items and extra=1, Django creates 4 forms (3 from initial + 1 extra)
            # But we want exactly len(initial_data) forms, so we need to adjust
            logger.info(f"Formset created with {len(lines_formset.forms)} forms (initial_data has {len(initial_data)} items)")
            
            # Ensure we have exactly len(initial_data) forms
            while len(lines_formset.forms) < len(initial_data):
                # Add more forms if needed
                lines_formset.forms.append(lines_formset._construct_form(len(lines_formset.forms)))
                logger.info(f"Added form {len(lines_formset.forms) - 1}")
            
            # Remove extra forms beyond initial_data length
            while len(lines_formset.forms) > len(initial_data):
                lines_formset.forms.pop()
                logger.info(f"Removed extra form, now {len(lines_formset.forms)} forms")
            
            # Update management form TOTAL_FORMS to match initial_data length
            if lines_formset.management_form:
                lines_formset.management_form.initial['TOTAL_FORMS'] = len(initial_data)
                lines_formset.management_form.fields['TOTAL_FORMS'].initial = len(initial_data)
                # Also update the bound value if form is bound
                if hasattr(lines_formset.management_form, 'data'):
                    lines_formset.management_form.data = lines_formset.management_form.data.copy()
                    lines_formset.management_form.data[lines_formset.management_form.add_prefix('TOTAL_FORMS')] = str(len(initial_data))
            
            # Ensure querysets include selected items (for item field)
            from django.db.models import Q
            
            for idx, form in enumerate(lines_formset.forms):
                if idx < len(initial_data):
                    init_data = initial_data[idx]
                    logger.info(f"Processing form {idx} with initial data: {init_data}")
                    
                    # For item field, ensure it's in queryset even if user doesn't have permission
                    if 'item' in form.fields and init_data.get('item'):
                        item_id = init_data['item']
                        field = form.fields['item']
                        if hasattr(field, 'queryset') and hasattr(field.queryset, 'model'):
                            # Check if item is in queryset
                            if not field.queryset.filter(pk=item_id).exists():
                                # Add it to queryset
                                field.queryset = field.queryset.model.objects.filter(
                                    Q(pk=item_id) | Q(pk__in=field.queryset.values_list('pk', flat=True))
                                )
                                logger.info(f"  Added item {item_id} to queryset")
                            
                            # Set initial to the actual object
                            try:
                                obj = field.queryset.model.objects.get(pk=item_id)
                                field.initial = obj
                                form.initial['item'] = obj
                                logger.info(f"  Set item initial to object: {obj}")
                            except field.queryset.model.DoesNotExist:
                                logger.warning(f"  Item {item_id} not found")
                    
                    # Keep form unbound so initial values are displayed
                    form.is_bound = False
                    logger.info(f"  Form {idx} kept unbound, is_bound: {form.is_bound}")
                else:
                    form.is_bound = False
                    logger.info(f"Form {idx} has no initial data, keeping unbound")
            
            logger.info(f"Formset created with {len(lines_formset.forms)} forms")
            logger.info("=" * 80)
            context['lines_formset'] = lines_formset
        
        # Set purchase_request in form
        if 'form' in context:
            logger.info("Setting purchase_request in form initial")
            context['form'].initial['purchase_request'] = purchase_request
            logger.info(f"Form initial purchase_request: {context['form'].initial.get('purchase_request')}")
        
        logger.info("=" * 80)
        logger.info("get_context_data completed")
        logger.info(f"Context keys: {list(context.keys())}")
        logger.info(f"lines_formset in context: {'lines_formset' in context}")
        if 'lines_formset' in context:
            logger.info(f"lines_formset has {len(context['lines_formset'].forms)} forms")
        logger.info("=" * 80)
        return context
    
    def form_valid(self, form):
        """Save receipt and update purchase request lines."""
        purchase_request = self.get_purchase_request()
        
        # Set purchase request
        form.instance.purchase_request = purchase_request
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
        for line_form in lines_formset.forms:
            if line_form.cleaned_data and line_form.cleaned_data.get('item') and not line_form.cleaned_data.get('DELETE', False):
                valid_lines.append(line_form)
        
        if not valid_lines:
            self.object.delete()
            form.add_error(None, _('Please add at least one line with an item.'))
            lines_formset = self.build_line_formset(instance=None)
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        # Update purchase request line quantity_fulfilled
        session_key = f'purchase_request_{purchase_request.pk}_receipt_permanent_lines'
        selected_lines_data = self.request.session.get(session_key, [])
        
        from inventory.models import PurchaseRequestLine
        from decimal import Decimal
        for line_data in selected_lines_data:
            try:
                line = PurchaseRequestLine.objects.get(
                    pk=line_data['line_id'],
                    document=purchase_request
                )
                quantity = Decimal(line_data['quantity'])
                line.quantity_fulfilled += quantity
                if line.quantity_fulfilled > line.quantity_requested:
                    line.quantity_fulfilled = line.quantity_requested
                line.save()
            except PurchaseRequestLine.DoesNotExist:
                pass
        
        # Clear session
        if session_key in self.request.session:
            del self.request.session[session_key]
        
        messages.success(self.request, _('رسید دائم با موفقیت از درخواست خرید ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())


class ReceiptConsignmentCreateFromPurchaseRequestView(ReceiptConsignmentCreateView):
    """Create consignment receipt from purchase request."""
    
    def get_purchase_request(self):
        """Get purchase request from URL."""
        from inventory.models import PurchaseRequest
        company_id = self.request.session.get('active_company_id')
        return get_object_or_404(
            PurchaseRequest,
            pk=self.kwargs['pk'],
            company_id=company_id,
            status=PurchaseRequest.Status.APPROVED,
            is_enabled=1
        )
    
    def get_context_data(self, **kwargs):
        """Add purchase request to context."""
        import logging
        logger = logging.getLogger('inventory.views.receipts')
        logger.info("=" * 80)
        logger.info("ReceiptConsignmentCreateFromPurchaseRequestView.get_context_data called")
        
        purchase_request = self.get_purchase_request()
        logger.info(f"Purchase request: {purchase_request.request_code} (pk={purchase_request.pk})")
        
        # Get selected lines from session BEFORE calling super().get_context_data
        # This way we can build formset with initial data before LineFormsetMixin builds it
        session_key = f'purchase_request_{purchase_request.pk}_receipt_consignment_lines'
        logger.info(f"Looking for session key: {session_key}")
        logger.info(f"All session keys: {list(self.request.session.keys())}")
        selected_lines_data = self.request.session.get(session_key, [])
        logger.info(f"Retrieved from session: {selected_lines_data}")
        logger.info(f"Number of selected lines: {len(selected_lines_data)}")
        
        # Build initial data BEFORE calling super().get_context_data
        initial_data = []
        if selected_lines_data:
            logger.info("=" * 80)
            logger.info("Building initial_data BEFORE super().get_context_data")
            from inventory.models import PurchaseRequestLine
            from decimal import Decimal
            
            for idx, line_data in enumerate(selected_lines_data):
                logger.info(f"Processing line_data[{idx}]: {line_data}")
                try:
                    line_id = line_data.get('line_id')
                    quantity = line_data.get('quantity')
                    logger.info(f"  Looking for PurchaseRequestLine pk={line_id}, document={purchase_request.pk}")
                    
                    line = PurchaseRequestLine.objects.get(
                        pk=line_id,
                        document=purchase_request
                    )
                    logger.info(f"  Found line: item={line.item.name if line.item else 'None'} (pk={line.item.pk if line.item else None}), "
                               f"unit={line.unit}, quantity_requested={line.quantity_requested}")
                    
                    # Get warehouse from item's allowed warehouses (first one)
                    from inventory.models import ItemWarehouse
                    item_warehouse = ItemWarehouse.objects.filter(
                        item=line.item,
                        company_id=purchase_request.company_id,
                        is_enabled=1
                    ).first()
                    warehouse = item_warehouse.warehouse if item_warehouse else None
                    logger.info(f"  Warehouse: {warehouse.name if warehouse else 'None'} (pk={warehouse.pk if warehouse else None})")
                    
                    # Get supplier (required for consignment)
                    from inventory.models import SupplierItem
                    supplier_item = SupplierItem.objects.filter(
                        item=line.item,
                        company_id=purchase_request.company_id,
                        is_enabled=1
                    ).first()
                    supplier = supplier_item.supplier if supplier_item else None
                    logger.info(f"  Supplier: {supplier.name if supplier else 'None'} (pk={supplier.pk if supplier else None})")
                    
                    initial_item = {
                        'item': line.item.pk if line.item else None,
                        'warehouse': warehouse.pk if warehouse else None,
                        'supplier': supplier.pk if supplier else None,
                        'unit': line.unit,
                        'quantity': str(Decimal(quantity)),
                        'entered_unit': line.unit,
                        'entered_quantity': str(Decimal(quantity)),
                    }
                    initial_data.append(initial_item)
                    logger.info(f"  Added initial data: {initial_item}")
                except PurchaseRequestLine.DoesNotExist as e:
                    logger.error(f"  PurchaseRequestLine {line_data.get('line_id')} not found: {e}")
                    pass
                except Exception as e:
                    logger.error(f"  Error processing line_data[{idx}]: {e}", exc_info=True)
                    pass
            
            logger.info(f"Total initial_data items: {len(initial_data)}")
            logger.info(f"Initial data summary: {[{'item': d.get('item'), 'warehouse': d.get('warehouse'), 'supplier': d.get('supplier'), 'quantity': d.get('quantity')} for d in initial_data]}")
        
        # Store initial_data as instance attribute so we can use it after super().get_context_data
        self._initial_data_for_formset = initial_data
        
        # Now call super().get_context_data - this will call LineFormsetMixin.get_context_data
        # which will build the formset, but we'll override it after
        context = super().get_context_data(**kwargs)
        context['purchase_request'] = purchase_request
        
        # Now override the formset with our initial data
        if initial_data and 'lines_formset' in context:
            logger.info("=" * 80)
            logger.info("OVERRIDING formset with initial data")
            logger.info(f"Current formset has {len(context['lines_formset'].forms)} forms")
            logger.info(f"Using initial_data with {len(initial_data)} items")
            
            # Build formset with initial data - Django formsets accept initial as a list of dicts
            # But we need to ensure enough forms are created (Django only creates forms based on extra + initial)
            # So we need to manually adjust the formset after creation
            logger.info("Building formset with initial data")
            company_id = self.request.session.get('active_company_id')
            formset_kwargs = {
                'instance': None,
                'prefix': self.formset_prefix,
                'company_id': company_id,
                'initial': initial_data,  # Pass initial data to formset constructor
            }
            lines_formset = self.formset_class(**formset_kwargs)
            
            # Django creates forms based on: initial data + extra
            # If we have 3 initial items and extra=1, Django creates 4 forms (3 from initial + 1 extra)
            # But we want exactly len(initial_data) forms, so we need to adjust
            logger.info(f"Formset created with {len(lines_formset.forms)} forms (initial_data has {len(initial_data)} items)")
            
            # Ensure we have exactly len(initial_data) forms
            while len(lines_formset.forms) < len(initial_data):
                # Add more forms if needed
                lines_formset.forms.append(lines_formset._construct_form(len(lines_formset.forms)))
                logger.info(f"Added form {len(lines_formset.forms) - 1}")
            
            # Remove extra forms beyond initial_data length
            while len(lines_formset.forms) > len(initial_data):
                lines_formset.forms.pop()
                logger.info(f"Removed extra form, now {len(lines_formset.forms)} forms")
            
            # Update management form TOTAL_FORMS to match initial_data length
            if lines_formset.management_form:
                lines_formset.management_form.initial['TOTAL_FORMS'] = len(initial_data)
                lines_formset.management_form.fields['TOTAL_FORMS'].initial = len(initial_data)
                # Also update the bound value if form is bound
                if hasattr(lines_formset.management_form, 'data'):
                    lines_formset.management_form.data = lines_formset.management_form.data.copy()
                    lines_formset.management_form.data[lines_formset.management_form.add_prefix('TOTAL_FORMS')] = str(len(initial_data))
            
            # Ensure querysets include selected items (for item field)
            from django.db.models import Q
            
            for idx, form in enumerate(lines_formset.forms):
                if idx < len(initial_data):
                    init_data = initial_data[idx]
                    logger.info(f"Processing form {idx} with initial data: {init_data}")
                    
                    # For item field, ensure it's in queryset even if user doesn't have permission
                    if 'item' in form.fields and init_data.get('item'):
                        item_id = init_data['item']
                        field = form.fields['item']
                        if hasattr(field, 'queryset') and hasattr(field.queryset, 'model'):
                            # Check if item is in queryset
                            if not field.queryset.filter(pk=item_id).exists():
                                # Add it to queryset
                                field.queryset = field.queryset.model.objects.filter(
                                    Q(pk=item_id) | Q(pk__in=field.queryset.values_list('pk', flat=True))
                                )
                                logger.info(f"  Added item {item_id} to queryset")
                            
                            # Set initial to the actual object
                            try:
                                obj = field.queryset.model.objects.get(pk=item_id)
                                field.initial = obj
                                form.initial['item'] = obj
                                logger.info(f"  Set item initial to object: {obj}")
                            except field.queryset.model.DoesNotExist:
                                logger.warning(f"  Item {item_id} not found")
                    
                    # Keep form unbound so initial values are displayed
                    form.is_bound = False
                    logger.info(f"  Form {idx} kept unbound, is_bound: {form.is_bound}")
                else:
                    form.is_bound = False
                    logger.info(f"Form {idx} has no initial data, keeping unbound")
            
            logger.info(f"Formset created with {len(lines_formset.forms)} forms")
            logger.info("=" * 80)
            context['lines_formset'] = lines_formset
        
        # Set purchase_request in form
        if 'form' in context:
            logger.info("Setting purchase_request in form initial")
            context['form'].initial['purchase_request'] = purchase_request
            logger.info(f"Form initial purchase_request: {context['form'].initial.get('purchase_request')}")
        
        logger.info("=" * 80)
        logger.info("get_context_data completed")
        logger.info(f"Context keys: {list(context.keys())}")
        logger.info(f"lines_formset in context: {'lines_formset' in context}")
        if 'lines_formset' in context:
            logger.info(f"lines_formset has {len(context['lines_formset'].forms)} forms")
        logger.info("=" * 80)
        return context
    
    def form_valid(self, form):
        """Save receipt and update purchase request lines."""
        purchase_request = self.get_purchase_request()
        
        # Set purchase request
        form.instance.purchase_request = purchase_request
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
        
        # Update purchase request line quantity_fulfilled
        session_key = f'purchase_request_{purchase_request.pk}_receipt_consignment_lines'
        selected_lines_data = self.request.session.get(session_key, [])
        
        from inventory.models import PurchaseRequestLine
        from decimal import Decimal
        for line_data in selected_lines_data:
            try:
                line = PurchaseRequestLine.objects.get(
                    pk=line_data['line_id'],
                    document=purchase_request
                )
                quantity = Decimal(line_data['quantity'])
                line.quantity_fulfilled += quantity
                if line.quantity_fulfilled > line.quantity_requested:
                    line.quantity_fulfilled = line.quantity_requested
                line.save()
            except PurchaseRequestLine.DoesNotExist:
                pass
        
        # Clear session
        if session_key in self.request.session:
            del self.request.session[session_key]
        
        messages.success(self.request, _('رسید امانی با موفقیت از درخواست خرید ایجاد شد.'))
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

    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        # Filter by company_id (from InventoryBaseView)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.receipts.consignment', 'created_by')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__supplier'
        ).select_related('created_by', 'temporary_receipt', 'purchase_request', 'warehouse_request')
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


class ReceiptConsignmentUnlockView(DocumentUnlockView):
    """Unlock view for consignment receipts."""
    model = models.ReceiptConsignment
    success_url_name = 'inventory:receipt_consignment'
    success_message = _('رسید امانی از قفل خارج شد و قابل ویرایش است.')
    feature_code = 'inventory.receipts.consignment'
    required_action = 'unlock_own'


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


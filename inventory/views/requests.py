"""
Request views for inventory module.

This module contains views for:
- Purchase Requests
- Warehouse Requests
"""
from typing import Dict, Any, Set, Optional
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, View, TemplateView
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Q
import json

from .base import InventoryBaseView, LineFormsetMixin
from shared.mixins import FeaturePermissionRequiredMixin
from .. import models
from .. import forms
from ..models import Item, ItemUnit


# ============================================================================
# Purchase Request Views
# ============================================================================

class PurchaseRequestFormMixin(InventoryBaseView):
    """Mixin for Purchase Request form views."""
    template_name = 'inventory/purchase_request_form.html'
    form_title = ''

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Pass company_id and request_user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        kwargs['request_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form context including fieldsets and unit options."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        form = context.get('form')
        raw_fieldsets = self.get_fieldsets()
        render_fieldsets = []
        used_fields = []
        if form and raw_fieldsets:
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
        context['list_url'] = reverse_lazy('inventory:purchase_requests')
        context['is_edit'] = bool(getattr(self, 'object', None))
        context['purchase_request'] = getattr(self, 'object', None)
        
        # Add unit options for lines formset
        company_id = self.request.session.get('active_company_id')
        if company_id:
            unit_map: Dict[str, list] = {}
            items = Item.objects.filter(company_id=company_id, is_enabled=1)
            for item in items:
                # Get allowed units for item
                codes = []
                def add(code: str) -> None:
                    if code and code not in codes:
                        codes.append(code)
                add(item.default_unit)
                add(item.primary_unit)
                for unit in ItemUnit.objects.filter(item=item, company_id=item.company_id):
                    add(unit.from_unit)
                    add(unit.to_unit)
                if not codes:
                    codes.append('EA')
                label_map = {value: str(label) for value, label in forms.UNIT_CHOICES}
                unit_map[str(item.pk)] = [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]
            context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
        else:
            context['unit_options_json'] = mark_safe('{}')
        context['unit_placeholder'] = str(forms.UNIT_CHOICES[0][1])
        
        # Add item types, categories, and subcategories for filtering
        from ..models import ItemType, ItemCategory, ItemSubcategory
        if company_id:
            context['item_types'] = ItemType.objects.filter(company_id=company_id, is_enabled=1).order_by('name')
            context['item_categories'] = ItemCategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')
            context['item_subcategories'] = ItemSubcategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')
        else:
            context['item_types'] = ItemType.objects.none()
            context['item_categories'] = ItemCategory.objects.none()
            context['item_subcategories'] = ItemSubcategory.objects.none()
        
        return context

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration. Override in subclasses."""
        return []


class PurchaseRequestListView(InventoryBaseView, ListView):
    """List view for purchase requests."""
    model = models.PurchaseRequest
    template_name = 'inventory/purchase_requests.html'
    context_object_name = 'purchase_requests'
    paginate_by = 50

    def get_queryset(self):
        """Filter and search purchase requests."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('requested_by', 'approver').prefetch_related('lines__item')
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        search = self.request.GET.get('search')
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if search:
            value = search.strip()
            if value:
                queryset = queryset.filter(
                    Q(request_code__icontains=value)
                    | Q(item__name__icontains=value)
                    | Q(item_code__icontains=value)
                )
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add statistics and filter context."""
        context = super().get_context_data(**kwargs)
        company_id: Optional[int] = self.request.session.get('active_company_id')
        stats_queryset = models.PurchaseRequest.objects.filter(company_id=company_id)
        context['total_count'] = stats_queryset.count()
        context['draft_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.DRAFT).count()
        context['approved_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.APPROVED).count()
        context['ordered_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.ORDERED).count()
        context['fulfilled_count'] = stats_queryset.filter(status=models.PurchaseRequest.Status.FULFILLED).count()
        context['create_url'] = reverse_lazy('inventory:purchase_request_create')
        context['edit_url_name'] = 'inventory:purchase_request_edit'
        context['approve_url_name'] = 'inventory:purchase_request_approve'
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['search_term'] = self.request.GET.get('search', '')
        approver_queryset = forms.get_purchase_request_approvers(company_id)
        approver_ids: Set[int] = set(approver_queryset.values_list('id', flat=True))
        for pr in context['purchase_requests']:
            pr.can_current_user_edit = (
                pr.status == models.PurchaseRequest.Status.DRAFT
                and pr.requested_by_id == self.request.user.id
            )
            pr.can_current_user_approve = (
                pr.status == models.PurchaseRequest.Status.DRAFT
                and pr.approver_id
                and pr.approver_id == self.request.user.id
            )
        context['approver_user_ids'] = list(approver_ids)
        return context


class PurchaseRequestCreateView(LineFormsetMixin, PurchaseRequestFormMixin, CreateView):
    """Create view for purchase requests."""
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
    formset_class = forms.PurchaseRequestLineFormSet
    success_url = reverse_lazy('inventory:purchase_requests')
    form_title = _('ایجاد درخواست خرید')

    def form_valid(self, form):
        """Set company, requested_by, and status before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        form.instance.requested_by = self.request.user
        form.instance.request_date = timezone.now().date()
        form.instance.status = models.PurchaseRequest.Status.DRAFT
        
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
            # No valid lines, show error and delete the document
            self.object.delete()
            form.add_error(None, _('Please add at least one line with an item.'))
            lines_formset = self.build_line_formset(instance=None)
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('درخواست خرید با موفقیت ثبت شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('زمان بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'reason_code']),
        ]


class PurchaseRequestUpdateView(LineFormsetMixin, PurchaseRequestFormMixin, UpdateView):
    """Update view for purchase requests."""
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
    formset_class = forms.PurchaseRequestLineFormSet
    success_url = reverse_lazy('inventory:purchase_requests')
    form_title = _('ویرایش درخواست خرید')

    def get_queryset(self):
        """Filter to only draft requests created by current user."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('requested_by', 'approver').prefetch_related('lines__item')
        return queryset.filter(
            status=models.PurchaseRequest.Status.DRAFT,
            requested_by=self.request.user,
        )

    def form_valid(self, form):
        """Set company_id before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
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
        for line_form in lines_formset.forms:
            if line_form.cleaned_data and line_form.cleaned_data.get('item') and not line_form.cleaned_data.get('DELETE', False):
                valid_lines.append(line_form)
        
        if not valid_lines:
            # No valid lines, show error
            lines_formset.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        self._save_line_formset(lines_formset)
        
        messages.success(self.request, _('درخواست خرید با موفقیت بروزرسانی شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('زمان بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'reason_code']),
        ]


class PurchaseRequestApproveView(InventoryBaseView, View):
    """Approve view for purchase requests."""
    
    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Approve a purchase request."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            messages.error(request, _('شرکت فعال مشخص نشده است.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        purchase_request = get_object_or_404(
            models.PurchaseRequest,
            pk=kwargs.get('pk'),
            company_id=company_id,
        )

        if purchase_request.status == models.PurchaseRequest.Status.APPROVED:
            messages.info(request, _('این درخواست قبلاً تایید شده است.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        if not purchase_request.approver_id:
            messages.error(request, _('برای این درخواست هنوز تاییدکننده تعیین نشده است.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        if purchase_request.approver_id != request.user.id:
            messages.error(request, _('تنها تاییدکننده تعیین‌شده می‌تواند این درخواست را تایید کند.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        allowed_user_ids: Set[int] = set(forms.get_purchase_request_approvers(company_id).values_list('id', flat=True))
        if request.user.id not in allowed_user_ids:
            messages.error(request, _('شما مجوز تایید درخواست خرید را ندارید.'))
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))

        now = timezone.now()
        purchase_request.status = models.PurchaseRequest.Status.APPROVED
        purchase_request.approved_at = now
        purchase_request.is_locked = 1
        update_fields: list = ['status', 'approved_at', 'approver', 'is_locked']
        if hasattr(purchase_request, 'locked_at'):
            purchase_request.locked_at = now
            update_fields.append('locked_at')
        if hasattr(purchase_request, 'locked_by_id'):
            purchase_request.locked_by = request.user
            update_fields.append('locked_by')
        if hasattr(purchase_request, 'edited_by_id'):
            purchase_request.edited_by = request.user
            update_fields.append('edited_by')
        purchase_request.save(update_fields=update_fields)
        messages.success(request, _('درخواست خرید تایید شد و برای استفاده در رسیدها آماده است.'))
        return HttpResponseRedirect(reverse('inventory:purchase_requests'))


# ============================================================================
# Warehouse Request Views
# ============================================================================

class WarehouseRequestFormMixin(InventoryBaseView):
    """Mixin for Warehouse Request form views."""
    template_name = 'inventory/warehouse_request_form.html'
    form_title = ''

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Pass company_id and request_user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        kwargs['request_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form context including fieldsets and unit/warehouse options."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        form = context.get('form')
        raw_fieldsets = self.get_fieldsets()
        render_fieldsets = []
        used_fields = []
        if form and raw_fieldsets:
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
        context['list_url'] = reverse_lazy('inventory:warehouse_requests')
        context['is_edit'] = bool(getattr(self, 'object', None))
        context['warehouse_request'] = getattr(self, 'object', None)

        if form and 'item' in form.fields:
            unit_map: Dict[str, list] = {}
            warehouse_map: Dict[str, list] = {}
            for item in form.fields['item'].queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
                warehouse_map[str(item.pk)] = form._get_item_allowed_warehouses(item)
            context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
            context['warehouse_options_json'] = mark_safe(json.dumps(warehouse_map, ensure_ascii=False))
        else:
            context['unit_options_json'] = mark_safe('{}')
            context['warehouse_options_json'] = mark_safe('{}')
        context['unit_placeholder'] = str(forms.UNIT_CHOICES[0][1])
        context['warehouse_placeholder'] = _('--- انتخاب کنید ---')
        return context

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration. Override in subclasses."""
        return []


class WarehouseRequestListView(InventoryBaseView, ListView):
    """List view for warehouse requests."""
    model = models.WarehouseRequest
    template_name = 'inventory/warehouse_requests.html'
    context_object_name = 'requests'
    paginate_by = 50

    def get_queryset(self):
        """Filter and search warehouse requests."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('item', 'warehouse', 'requester', 'approver')
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        search = self.request.GET.get('search')
        if status:
            queryset = queryset.filter(request_status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if search:
            value = search.strip()
            if value:
                queryset = queryset.filter(
                    Q(request_code__icontains=value)
                    | Q(item__name__icontains=value)
                    | Q(item_code__icontains=value)
                )
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add statistics and filter context."""
        context = super().get_context_data(**kwargs)
        company_id: Optional[int] = self.request.session.get('active_company_id')
        stats_queryset = models.WarehouseRequest.objects.filter(company_id=company_id)
        context['total_count'] = stats_queryset.count()
        context['draft_count'] = stats_queryset.filter(request_status='draft').count()
        context['approved_count'] = stats_queryset.filter(request_status='approved').count()
        context['issued_count'] = stats_queryset.filter(request_status='issued').count()
        context['create_url'] = reverse_lazy('inventory:warehouse_request_create')
        context['edit_url_name'] = 'inventory:warehouse_request_edit'
        context['approve_url_name'] = 'inventory:warehouse_request_approve'
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['search_term'] = self.request.GET.get('search', '')
        approver_queryset = forms.get_feature_approvers("inventory.requests.warehouse", company_id)
        approver_ids: Set[int] = set(approver_queryset.values_list('id', flat=True))
        for wr in context['requests']:
            wr.can_current_user_edit = (
                wr.request_status == 'draft'
                and wr.requester_id == self.request.user.id
            )
            wr.can_current_user_approve = (
                wr.request_status == 'draft'
                and wr.approver_id
                and wr.approver_id == self.request.user.id
            )
        context['approver_user_ids'] = list(approver_ids)
        return context


class WarehouseRequestCreateView(WarehouseRequestFormMixin, CreateView):
    """Create view for warehouse requests."""
    model = models.WarehouseRequest
    form_class = forms.WarehouseRequestForm
    success_url = reverse_lazy('inventory:warehouse_requests')
    form_title = _('ایجاد درخواست انبار')

    def form_valid(self, form):
        """Set company, requester, and status before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        form.instance.requester = self.request.user
        form.instance.request_date = timezone.now().date()
        form.instance.request_status = 'draft'
        self.object = form.save()
        messages.success(self.request, _('درخواست انبار با موفقیت ثبت شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'warehouse', 'department_unit']),
            (_('زمان‌بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'purpose']),
        ]


class WarehouseRequestUpdateView(WarehouseRequestFormMixin, UpdateView):
    """Update view for warehouse requests."""
    model = models.WarehouseRequest
    form_class = forms.WarehouseRequestForm
    success_url = reverse_lazy('inventory:warehouse_requests')
    form_title = _('ویرایش درخواست انبار')

    def get_queryset(self):
        """Filter to only draft requests created by current user."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('item', 'warehouse', 'requester', 'approver')
        return queryset.filter(
            request_status='draft',
            requester=self.request.user,
        )

    def form_valid(self, form):
        """Set company_id before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        response = super().form_valid(form)
        messages.success(self.request, _('درخواست انبار با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'warehouse', 'department_unit']),
            (_('زمان‌بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'purpose']),
        ]


class WarehouseRequestApproveView(InventoryBaseView, View):
    """Approve view for warehouse requests."""
    
    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """Approve a warehouse request."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            messages.error(request, _('شرکت فعال مشخص نشده است.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        warehouse_request = get_object_or_404(
            models.WarehouseRequest,
            pk=kwargs.get('pk'),
            company_id=company_id,
        )

        if warehouse_request.request_status == 'approved':
            messages.info(request, _('این درخواست قبلاً تایید شده است.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        if not warehouse_request.approver_id:
            messages.error(request, _('برای این درخواست هنوز تاییدکننده تعیین نشده است.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        if warehouse_request.approver_id != request.user.id:
            messages.error(request, _('تنها تاییدکننده تعیین‌شده می‌تواند این درخواست را تایید کند.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        allowed_user_ids: Set[int] = set(forms.get_feature_approvers("inventory.requests.warehouse", company_id).values_list('id', flat=True))
        if request.user.id not in allowed_user_ids:
            messages.error(request, _('شما مجوز تایید درخواست انبار را ندارید.'))
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))

        now = timezone.now()
        warehouse_request.request_status = 'approved'
        warehouse_request.approved_at = now
        warehouse_request.is_locked = 1
        update_fields: list = ['request_status', 'approved_at', 'approver', 'is_locked']
        if hasattr(warehouse_request, 'locked_at'):
            warehouse_request.locked_at = now
            update_fields.append('locked_at')
        if hasattr(warehouse_request, 'locked_by_id'):
            warehouse_request.locked_by = request.user
            update_fields.append('locked_by')
        if hasattr(warehouse_request, 'edited_by_id'):
            warehouse_request.edited_by = request.user
            update_fields.append('edited_by')
        warehouse_request.save(update_fields=update_fields)
        messages.success(request, _('درخواست انبار تایید شد و برای استفاده در حواله‌ها آماده است.'))
        return HttpResponseRedirect(reverse('inventory:warehouse_requests'))


# ============================================================================
# Create Receipt from Purchase Request Views
# ============================================================================

class CreateReceiptFromPurchaseRequestView(FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView):
    """Base view for selecting lines from purchase request to create receipt."""
    receipt_type = None  # 'temporary', 'permanent', 'consignment'
    template_name = 'inventory/create_receipt_from_purchase_request.html'
    required_action = 'create_receipt_from_purchase_request'
    
    def get_purchase_request(self, pk: int):
        """Get purchase request and check permissions."""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            raise Http404(_('شرکت فعال مشخص نشده است.'))
        
        purchase_request = get_object_or_404(
            models.PurchaseRequest,
            pk=pk,
            company_id=company_id,
            status=models.PurchaseRequest.Status.APPROVED,
            is_enabled=1
        )
        return purchase_request
    
    def get_context_data(self, **kwargs):
        """Display form to select lines from purchase request."""
        context = super().get_context_data(**kwargs)
        purchase_request = self.get_purchase_request(kwargs['pk'])
        lines = purchase_request.lines.filter(is_enabled=1).order_by('sort_order', 'id')
        
        context['purchase_request'] = purchase_request
        context['lines'] = lines
        context['receipt_type'] = self.receipt_type
        
        receipt_type_names = {
            'temporary': _('رسید موقت'),
            'permanent': _('رسید دائم'),
            'consignment': _('رسید امانی'),
        }
        context['receipt_type_name'] = receipt_type_names.get(self.receipt_type, '')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Process selected lines and redirect to receipt creation."""
        import logging
        logger = logging.getLogger('inventory.views.requests')
        logger.info("=" * 80)
        logger.info(f"POST request received for CreateReceiptFromPurchaseRequestView (receipt_type={self.receipt_type})")
        logger.info(f"URL kwargs: {kwargs}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        
        purchase_request = self.get_purchase_request(kwargs['pk'])
        logger.info(f"Purchase request found: {purchase_request.request_code} (pk={purchase_request.pk})")
        
        # Get selected lines with quantities
        selected_lines = []
        for line in purchase_request.lines.filter(is_enabled=1):
            line_id = str(line.pk)
            quantity_key = f'quantity_{line_id}'
            selected_key = f'selected_{line_id}'
            
            logger.info(f"Processing line {line_id}: item={line.item.name if line.item else 'None'}, "
                       f"selected_key={selected_key}, quantity_key={quantity_key}")
            logger.info(f"  POST.get('{selected_key}') = {request.POST.get(selected_key)}")
            logger.info(f"  POST.get('{quantity_key}') = {request.POST.get(quantity_key)}")
            
            if request.POST.get(selected_key) == 'on':
                quantity = request.POST.get(quantity_key, '0')
                logger.info(f"  Line {line_id} is selected with quantity={quantity}")
                try:
                    quantity = Decimal(str(quantity))
                    if quantity > 0:
                        remaining = line.quantity_remaining
                        logger.info(f"  Line {line_id} remaining quantity: {remaining}")
                        if quantity > remaining:
                            logger.warning(f"  Line {line_id} quantity {quantity} > remaining {remaining}, adjusting to {remaining}")
                            quantity = remaining
                        selected_lines.append({
                            'line': line,
                            'quantity': quantity,
                        })
                        logger.info(f"  Line {line_id} added to selected_lines: quantity={quantity}")
                except (ValueError, InvalidOperation) as e:
                    logger.error(f"  Error parsing quantity for line {line_id}: {e}")
                    pass
            else:
                logger.info(f"  Line {line_id} is NOT selected (checkbox not checked)")
        
        logger.info(f"Total selected_lines count: {len(selected_lines)}")
        if not selected_lines:
            logger.warning("No lines selected, showing error message")
            messages.error(request, _('لطفاً حداقل یک ردیف را انتخاب کنید.'))
            return self.get(request, *args, **kwargs)
        
        # Store selected lines in session for receipt creation
        session_key = f'purchase_request_{purchase_request.pk}_receipt_{self.receipt_type}_lines'
        session_data = [
            {
                'line_id': item['line'].pk,
                'quantity': str(item['quantity']),
            }
            for item in selected_lines
        ]
        logger.info(f"Storing in session with key: {session_key}")
        logger.info(f"Session data to store: {session_data}")
        request.session[session_key] = session_data
        logger.info(f"Session data stored successfully. Session keys: {list(request.session.keys())}")
        
        # Redirect to receipt creation
        if self.receipt_type == 'temporary':
            return HttpResponseRedirect(reverse('inventory:receipt_temporary_create_from_request', kwargs={'pk': purchase_request.pk}))
        elif self.receipt_type == 'permanent':
            return HttpResponseRedirect(reverse('inventory:receipt_permanent_create_from_request', kwargs={'pk': purchase_request.pk}))
        elif self.receipt_type == 'consignment':
            return HttpResponseRedirect(reverse('inventory:receipt_consignment_create_from_request', kwargs={'pk': purchase_request.pk}))
        
        return HttpResponseRedirect(reverse('inventory:purchase_requests'))


class CreateTemporaryReceiptFromPurchaseRequestView(CreateReceiptFromPurchaseRequestView):
    """View to select lines from purchase request for temporary receipt."""
    receipt_type = 'temporary'
    feature_code = 'inventory.receipts.temporary'


class CreatePermanentReceiptFromPurchaseRequestView(CreateReceiptFromPurchaseRequestView):
    """View to select lines from purchase request for permanent receipt."""
    receipt_type = 'permanent'
    feature_code = 'inventory.receipts.permanent'


class CreateConsignmentReceiptFromPurchaseRequestView(CreateReceiptFromPurchaseRequestView):
    """View to select lines from purchase request for consignment receipt."""
    receipt_type = 'consignment'
    feature_code = 'inventory.receipts.consignment'


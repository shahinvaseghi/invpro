"""
Request views for inventory module.

This module contains views for:
- Purchase Requests
- Warehouse Requests
"""
from typing import Dict, Any, Set, Optional
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, View
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Q
import json

from .base import InventoryBaseView
from .. import models
from .. import forms


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

        if form and 'item' in form.fields and 'unit' in form.fields:
            unit_map: Dict[str, list] = {}
            for item in form.fields['item'].queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
            context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
        else:
            context['unit_options_json'] = mark_safe('{}')
        context['unit_placeholder'] = str(forms.UNIT_CHOICES[0][1])
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
        queryset = queryset.select_related('item', 'requested_by', 'approver')
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


class PurchaseRequestCreateView(PurchaseRequestFormMixin, CreateView):
    """Create view for purchase requests."""
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
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
        self.object = form.save()
        messages.success(self.request, _('درخواست خرید با موفقیت ثبت شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'needed_by_date', 'priority']),
            (_('تایید'), ['approver', 'reason_code']),
        ]


class PurchaseRequestUpdateView(PurchaseRequestFormMixin, UpdateView):
    """Update view for purchase requests."""
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
    success_url = reverse_lazy('inventory:purchase_requests')
    form_title = _('ویرایش درخواست خرید')

    def get_queryset(self):
        """Filter to only draft requests created by current user."""
        queryset = super().get_queryset()
        return queryset.filter(
            status=models.PurchaseRequest.Status.DRAFT,
            requested_by__user=self.request.user,
        )

    def form_valid(self, form):
        """Set company_id before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        form.instance.company_id = company_id
        response = super().form_valid(form)
        messages.success(self.request, _('درخواست خرید با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات درخواست'), ['item', 'unit', 'quantity_requested', 'needed_by_date', 'priority']),
            (_('تایید'), ['approver', 'reason_code']),
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
        return queryset.filter(
            request_status='draft',
            requester__user=self.request.user,
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


"""
Request views for inventory module.

This module contains views for:
- Purchase Requests
- Warehouse Requests
"""
from typing import Dict, Any, Set, Optional, List
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, View, TemplateView, DetailView
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Q
import json

from .base import InventoryBaseView, LineFormsetMixin, BaseCreateDocumentFromRequestView
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    EditLockProtectedMixin,
    BaseFormsetCreateView,
    BaseFormsetUpdateView,
    BaseListView,
    BaseCreateView,
)
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
        
        # Add current filter values from request
        context['current_item_type'] = self.request.GET.get('item_type', '') or self.request.POST.get('item_type', '')
        context['current_category'] = self.request.GET.get('category', '') or self.request.POST.get('category', '')
        context['current_subcategory'] = self.request.GET.get('subcategory', '') or self.request.POST.get('subcategory', '')
        context['current_item_search'] = self.request.GET.get('item_search', '') or self.request.POST.get('item_search', '')
        
        return context

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration. Override in subclasses."""
        return []


class PurchaseRequestListView(BaseListView):
    """List view for purchase requests."""
    model = models.PurchaseRequest
    template_name = 'inventory/purchase_requests.html'
    feature_code = 'inventory.requests.purchase'
    search_fields = ['request_code']  # Custom search in apply_custom_filters
    filter_fields = ['status', 'priority']
    default_status_filter = False  # Custom status filter
    default_order_by = ['-id', '-request_date', 'request_code']
    permission_field = 'requested_by'
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['requested_by', 'approver']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['lines__item']
    
    def apply_custom_filters(self, queryset):
        """Apply custom filters for status, priority, and search."""
        queryset = super().apply_custom_filters(queryset)
        
        # Custom search in request_code and item name/code
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(request_code__icontains=search)
                | Q(lines__item__name__icontains=search)
                | Q(lines__item__item_code__icontains=search)
            ).distinct()
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Purchase Requests')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Purchase Requests'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:purchase_request_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Purchase Request')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by code or name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse_lazy('inventory:purchase_requests')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:purchase_request_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:purchase_request_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return None  # Purchase Request doesn't have delete
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Purchase Requests Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first purchase request.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '🛒'
    
    def get_stats(self) -> Optional[Dict[str, int]]:
        """Return aggregate stats for summary cards."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            return None
        stats_queryset = models.PurchaseRequest.objects.filter(company_id=company_id)
        return {
            'total': stats_queryset.count(),
            'draft': stats_queryset.filter(status=models.PurchaseRequest.Status.DRAFT).count(),
            'approved': stats_queryset.filter(status=models.PurchaseRequest.Status.APPROVED).count(),
            'fulfilled': stats_queryset.filter(status=models.PurchaseRequest.Status.FULFILLED).count(),
        }
    
    def get_stats_labels(self) -> Dict[str, str]:
        """Return stats labels dictionary."""
        return {
            'total': _('Total'),
            'draft': _('Draft'),
            'approved': _('Approved'),
            'fulfilled': _('Fulfilled'),
        }
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context variables."""
        context = super().get_context_data(**kwargs)
        
        context['print_enabled'] = True
        context['approve_url_name'] = 'inventory:purchase_request_approve'
        
        # Filters
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Permissions and approver logic
        company_id: Optional[int] = self.request.session.get('active_company_id')
        approver_queryset = forms.get_purchase_request_approvers(company_id)
        approver_ids: Set[int] = set(approver_queryset.values_list('id', flat=True))
        
        # Add permissions to each purchase request
        for pr in context['object_list']:
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


class PurchaseRequestCreateView(LineFormsetMixin, PurchaseRequestFormMixin, BaseCreateView):
    """Create view for purchase requests."""
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
    formset_class = forms.PurchaseRequestLineFormSet
    success_url = reverse_lazy('inventory:purchase_requests')
    feature_code = 'inventory.requests.purchase'
    required_action = 'create'
    success_message = _('درخواست خرید با موفقیت ثبت شد.')
    form_title = _('ایجاد درخواست خرید')
    
    def form_valid(self, form):
        """Set company, requested_by, and status before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        
        # company_id and created_by are set by AutoSetFieldsMixin
        # But we need to set requested_by and status manually
        form.instance.requested_by = self.request.user
        form.instance.request_date = timezone.now().date()
        form.instance.status = models.PurchaseRequest.Status.DRAFT
        
        # Build line formset first to validate and get first item
        lines_formset = self.build_line_formset(data=self.request.POST, instance=None)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if we have at least one valid line before saving document
        valid_lines = []
        first_item = None
        first_unit = None
        for line_form in lines_formset.forms:
            if line_form.cleaned_data and line_form.cleaned_data.get('item') and not line_form.cleaned_data.get('DELETE', False):
                valid_lines.append(line_form)
                if first_item is None:
                    first_item = line_form.cleaned_data.get('item')
                    first_unit = line_form.cleaned_data.get('unit', 'EA')
        
        if not valid_lines:
            form.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Set legacy fields from first valid line (for backward compatibility)
        # These fields are now handled by PurchaseRequestLine, but still exist in the model
        from decimal import Decimal
        if not first_item:
            form.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        form.instance.item = first_item
        form.instance.item_code = first_item.item_code or first_item.full_item_code or ''
        form.instance.unit = first_unit or 'EA'
        # quantity_requested and quantity_fulfilled will be calculated from lines
        # Set to 0 initially to satisfy NOT NULL constraint
        form.instance.quantity_requested = Decimal("0")
        form.instance.quantity_fulfilled = Decimal("0")
        
        # Save document first (skip legacy sync for now, we'll do it after lines are saved)
        form.instance._skip_legacy_sync = True
        self.object = form.save()
        
        # Now set instance for formset and validate before saving
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object, request=self.request)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        # Calculate total quantity from lines and update legacy fields
        total_quantity = sum(
            line.quantity_requested for line in self.object.lines.all()
        )
        self.object.quantity_requested = total_quantity
        self.object.quantity_fulfilled = Decimal("0")  # Will be updated when receipts are created
        self.object._skip_legacy_sync = False
        self.object.save()
        
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('زمان بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'reason_code']),
        ]


class PurchaseRequestDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing purchase requests (read-only)."""
    model = models.PurchaseRequest
    template_name = 'inventory/purchase_request_detail.html'
    context_object_name = 'purchase_request'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.requests.purchase', 'requested_by')
        queryset = queryset.prefetch_related(
            'lines__item'
        ).select_related('requested_by', 'approver')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse('inventory:purchase_requests')
        context['edit_url'] = reverse('inventory:purchase_request_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class PurchaseRequestUpdateView(EditLockProtectedMixin, LineFormsetMixin, PurchaseRequestFormMixin, UpdateView):
    """Update view for purchase requests."""
    model = models.PurchaseRequest
    form_class = forms.PurchaseRequestForm
    formset_class = forms.PurchaseRequestLineFormSet
    success_url = reverse_lazy('inventory:purchase_requests')
    form_title = _('ویرایش درخواست خرید')

    def get_queryset(self):
        """Get queryset with proper filtering and permissions."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        queryset = queryset.filter(is_enabled=1)
        # Apply permission filtering
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.requests.purchase', 'requested_by')
        queryset = queryset.select_related('requested_by', 'approver').prefetch_related('lines__item')
        return queryset
    
    def get_object(self, queryset=None):
        """Get object and check if it can be edited."""
        obj = super().get_object(queryset)
        # Check if request is in draft status
        if obj.status != models.PurchaseRequest.Status.DRAFT:
            from django.http import Http404
            raise Http404(_('فقط درخواست‌های پیش‌نویس قابل ویرایش هستند.'))
        # Check if user has permission to edit this request
        # Only the creator can edit draft requests (unless they have edit_other permission)
        if obj.requested_by_id != self.request.user.id:
            from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
            company_id = self.request.session.get('active_company_id')
            permissions = get_user_feature_permissions(self.request.user, company_id)
            can_edit_other = self.request.user.is_superuser or has_feature_permission(
                permissions, 'inventory.requests.purchase', 'edit_other', allow_own_scope=False,
                current_user=self.request.user, resource_owner=obj.requested_by
            )
            if not can_edit_other:
                from django.http import Http404
                raise Http404(_('شما اجازه ویرایش این درخواست را ندارید.'))
        return obj

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
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object, request=self.request)
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
        
        # Calculate total quantity from lines and update legacy fields
        total_quantity = sum(
            line.quantity_requested for line in self.object.lines.all()
        )
        self.object.quantity_requested = total_quantity
        self.object.save()
        
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
        
        # Add breadcrumbs for generic_form.html
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Warehouse Requests'), 'url': reverse_lazy('inventory:warehouse_requests')},
        ]
        context['cancel_url'] = reverse_lazy('inventory:warehouse_requests')
        
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
        
        # Add formset to context (for BaseFormsetCreateView compatibility)
        # Use LineFormsetMixin's build_line_formset method
        if hasattr(self, 'formset_class') and self.formset_class and hasattr(self, 'build_line_formset'):
            if self.request.method == 'POST':
                formset = self.build_line_formset(data=self.request.POST, request=self.request)
            else:
                formset = self.build_line_formset(request=self.request)
            context['lines_formset'] = formset
            context['formset'] = formset  # Also add as 'formset' for generic_form compatibility

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
        
        return context

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration. Override in subclasses."""
        return []


class WarehouseRequestListView(InventoryBaseView, ListView):
    """List view for warehouse requests."""
    model = models.WarehouseRequest
    template_name = 'inventory/warehouse_requests.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        """Filter and search warehouse requests."""
        queryset = super().get_queryset()
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.requests.warehouse', 'requester')
        queryset = queryset.select_related('item', 'warehouse', 'requester', 'approver').prefetch_related('lines__item', 'lines__warehouse')
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
                    | Q(lines__item__name__icontains=value)
                    | Q(lines__item__item_code__icontains=value)
                ).distinct()
        return queryset

    def _get_stats(self) -> Dict[str, int]:
        """Return aggregate stats for summary cards."""
        stats = {
            'total': 0,
            'draft': 0,
            'approved': 0,
            'issued': 0,
        }
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            return stats
        stats_queryset = models.WarehouseRequest.objects.filter(company_id=company_id)
        stats['total'] = stats_queryset.count()
        stats['draft'] = stats_queryset.filter(request_status='draft').count()
        stats['approved'] = stats_queryset.filter(request_status='approved').count()
        stats['issued'] = stats_queryset.filter(request_status='issued').count()
        return stats

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        
        # Generic list context
        context['page_title'] = _('Warehouse Requests')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:warehouse_request_create')
        context['create_button_text'] = _('Create Warehouse Request')
        context['show_filters'] = True
        context['print_enabled'] = True
        context['show_actions'] = True
        
        # Warehouse Request-specific context
        context['feature_code'] = 'inventory.requests.warehouse'
        context['detail_url_name'] = 'inventory:warehouse_request_detail'
        context['edit_url_name'] = 'inventory:warehouse_request_edit'
        context['approve_url_name'] = 'inventory:warehouse_request_approve'
        context['empty_state_title'] = _('No Requests Found')
        context['empty_state_message'] = _('Start by creating your first warehouse request.')
        context['empty_state_icon'] = '📋'
        
        # Filters
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Stats
        context['stats'] = self._get_stats()
        # Stats labels for Persian display
        context['stats_labels'] = {
            'total': _('Total'),
            'draft': _('Pending Approval'),
            'approved': _('Approved'),
            'issued': _('Issued'),
        }
        
        # Permissions and approver logic
        company_id: Optional[int] = self.request.session.get('active_company_id')
        approver_queryset = forms.get_feature_approvers("inventory.requests.warehouse", company_id)
        approver_ids: Set[int] = set(approver_queryset.values_list('id', flat=True))
        
        # Add permissions to each warehouse request
        for wr in context['object_list']:
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


class WarehouseRequestCreateView(LineFormsetMixin, WarehouseRequestFormMixin, BaseFormsetCreateView):
    """Create view for warehouse requests."""
    model = models.WarehouseRequest
    form_class = forms.WarehouseRequestForm
    formset_class = forms.WarehouseRequestLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:warehouse_requests')
    form_title = _('ایجاد درخواست انبار')
    feature_code = 'inventory.requests.warehouse'

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
        
        # Build and validate formset
        lines_formset = self.build_line_formset(data=self.request.POST, request=self.request)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if we have at least one valid line before saving document
        valid_lines = []
        first_item = None
        first_unit = None
        first_warehouse = None
        for line_form in lines_formset.forms:
            if line_form.cleaned_data and line_form.cleaned_data.get('item') and not line_form.cleaned_data.get('DELETE', False):
                valid_lines.append(line_form)
                if first_item is None:
                    first_item = line_form.cleaned_data.get('item')
                    first_unit = line_form.cleaned_data.get('unit', 'EA')
                    first_warehouse = line_form.cleaned_data.get('warehouse')
        
        if not valid_lines:
            form.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Set legacy fields from first valid line (for backward compatibility)
        from decimal import Decimal
        if not first_item:
            form.add_error(None, _('Please add at least one line with an item.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        form.instance.item = first_item
        form.instance.item_code = first_item.item_code or first_item.full_item_code or ''
        form.instance.unit = first_unit or 'EA'
        form.instance.warehouse = first_warehouse
        if first_warehouse:
            form.instance.warehouse_code = first_warehouse.public_code or ''
        # quantity_requested will be calculated from lines
        form.instance.quantity_requested = Decimal("0")
        
        # Save document first
        self.object = form.save()
        
        # Now set instance for formset and validate before saving
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object, request=self.request)
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        self._save_line_formset(lines_formset)
        
        # Calculate total quantity from lines and update legacy fields
        total_quantity = sum(
            line.quantity_requested for line in self.object.lines.all()
        )
        self.object.quantity_requested = total_quantity
        self.object.save()
        
        messages.success(self.request, _('درخواست انبار با موفقیت ثبت شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات درخواست'), ['department_unit']),
            (_('زمان‌بندی و اولویت'), ['needed_by_date', 'priority']),
            (_('تایید و توضیحات'), ['approver', 'purpose']),
        ]


class WarehouseRequestDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing warehouse requests (read-only)."""
    model = models.WarehouseRequest
    template_name = 'inventory/warehouse_request_detail.html'
    context_object_name = 'warehouse_request'
    
    def get_queryset(self):
        """Prefetch related objects for efficient display."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.requests.warehouse', 'requester')
        queryset = queryset.prefetch_related(
            'lines__item',
            'lines__warehouse',
            'lines__unit'
        ).select_related('item', 'warehouse', 'requester', 'approver')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse('inventory:warehouse_requests')
        context['edit_url'] = reverse('inventory:warehouse_request_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        return context


class WarehouseRequestUpdateView(LineFormsetMixin, WarehouseRequestFormMixin, BaseFormsetUpdateView):
    """Update view for warehouse requests."""
    model = models.WarehouseRequest
    form_class = forms.WarehouseRequestForm
    formset_class = forms.WarehouseRequestLineFormSet
    formset_prefix = 'lines'
    success_url = reverse_lazy('inventory:warehouse_requests')
    form_title = _('ویرایش درخواست انبار')
    feature_code = 'inventory.requests.warehouse'

    def get_queryset(self):
        """Filter to only draft requests created by current user."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('requester', 'approver').prefetch_related('lines__item', 'lines__warehouse')
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
        form.instance.edited_by = self.request.user
        
        # Save document first
        self.object = form.save()
        
        # Handle line formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=self.object, request=self.request)
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
        
        # Calculate total quantity from lines and update legacy fields
        from decimal import Decimal
        total_quantity = sum(
            line.quantity_requested for line in self.object.lines.all()
        )
        self.object.quantity_requested = total_quantity
        
        # Update legacy fields from first valid line
        if valid_lines:
            first_line = valid_lines[0]
            first_item = first_line.cleaned_data.get('item')
            first_unit = first_line.cleaned_data.get('unit', 'EA')
            first_warehouse = first_line.cleaned_data.get('warehouse')
            if first_item:
                self.object.item = first_item
                self.object.item_code = first_item.item_code or first_item.full_item_code or ''
                self.object.unit = first_unit
            if first_warehouse:
                self.object.warehouse = first_warehouse
                self.object.warehouse_code = first_warehouse.public_code or ''
        
        self.object.save()
        
        messages.success(self.request, _('درخواست انبار با موفقیت بروزرسانی شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات درخواست'), ['department_unit']),
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

class CreateReceiptFromPurchaseRequestView(BaseCreateDocumentFromRequestView):
    """Base view for selecting lines from purchase request to create receipt."""
    document_type = 'receipt'
    request_model = models.PurchaseRequest
    is_multi_line = True
    template_name = 'inventory/create_receipt_from_purchase_request.html'
    required_action = 'create_receipt_from_purchase_request'
    
    def get_context_data(self, **kwargs):
        """Display form to select lines from purchase request."""
        context = super().get_context_data(**kwargs)
        # Add receipt_type for backward compatibility with templates
        context['receipt_type'] = self.document_subtype
        context['receipt_type_name'] = context.get('receipt_type_name', '')
        return context


class CreateTemporaryReceiptFromPurchaseRequestView(CreateReceiptFromPurchaseRequestView):
    """View to select lines from purchase request for temporary receipt."""
    document_subtype = 'temporary'
    feature_code = 'inventory.receipts.temporary'


class CreatePermanentReceiptFromPurchaseRequestView(CreateReceiptFromPurchaseRequestView):
    """View to select lines from purchase request for permanent receipt."""
    document_subtype = 'permanent'
    feature_code = 'inventory.receipts.permanent'


class CreateConsignmentReceiptFromPurchaseRequestView(CreateReceiptFromPurchaseRequestView):
    """View to select lines from purchase request for consignment receipt."""
    document_subtype = 'consignment'
    feature_code = 'inventory.receipts.consignment'


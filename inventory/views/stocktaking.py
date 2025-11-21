"""
Stocktaking views for inventory module.

This module contains views for:
- Stocktaking Deficit
- Stocktaking Surplus
- Stocktaking Records
"""
from typing import Dict, Any, Optional
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
import json

from .base import InventoryBaseView, DocumentLockProtectedMixin, DocumentLockView
from .receipts import DocumentDeleteViewBase
from .. import models
from .. import forms


# ============================================================================
# Stocktaking Form Mixin
# ============================================================================

class StocktakingFormMixin(InventoryBaseView):
    """Shared helpers for stocktaking create/update views."""
    template_name = 'inventory/stocktaking_form.html'
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
        """Add form context including fieldsets and unit/warehouse options."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
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

        unit_map: Dict[str, list] = {}
        warehouse_map: Dict[str, list] = {}
        if form and 'item' in form.fields:
            item_queryset = form.fields['item'].queryset
            for item in item_queryset:
                unit_map[str(item.pk)] = form._get_item_allowed_units(item)
                warehouse_map[str(item.pk)] = form._get_item_allowed_warehouses(item)
        context['unit_options_json'] = mark_safe(json.dumps(unit_map, ensure_ascii=False))
        context['unit_placeholder'] = str(forms.UNIT_CHOICES[0][1])
        context['warehouse_options_json'] = mark_safe(json.dumps(warehouse_map, ensure_ascii=False))
        context['warehouse_placeholder'] = _("--- انتخاب کنید ---")

        instance = getattr(form, 'instance', None)
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

class StocktakingDeficitListView(InventoryBaseView, ListView):
    """List view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    template_name = 'inventory/stocktaking_deficit.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:stocktaking_deficit_create')
        context['edit_url_name'] = 'inventory:stocktaking_deficit_edit'
        context['delete_url_name'] = 'inventory:stocktaking_deficit_delete'
        context['lock_url_name'] = 'inventory:stocktaking_deficit_lock'
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.deficit')
        return context


class StocktakingDeficitCreateView(StocktakingFormMixin, CreateView):
    """Create view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    form_title = _('ایجاد سند کسری انبارگردانی')
    list_url_name = 'inventory:stocktaking_deficit'
    lock_url_name = 'inventory:stocktaking_deficit_lock'

    def form_valid(self, form):
        """Set company and created_by before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند کسری انبارگردانی با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingDeficitUpdateView(DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    """Update view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    form_class = forms.StocktakingDeficitForm
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    form_title = _('ویرایش سند کسری انبارگردانی')
    list_url_name = 'inventory:stocktaking_deficit'
    lock_url_name = 'inventory:stocktaking_deficit_lock'

    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند کسری انبارگردانی با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingDeficitDeleteView(DocumentDeleteViewBase):
    """Delete view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    template_name = 'inventory/stocktaking_deficit_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_deficit')
    feature_code = 'inventory.stocktaking.deficit'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('سند کسری موجودی با موفقیت حذف شد.')


class StocktakingDeficitLockView(DocumentLockView):
    """Lock view for stocktaking deficit records."""
    model = models.StocktakingDeficit
    success_url_name = 'inventory:stocktaking_deficit'
    success_message = _('سند کسری شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Stocktaking Surplus Views
# ============================================================================

class StocktakingSurplusListView(InventoryBaseView, ListView):
    """List view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    template_name = 'inventory/stocktaking_surplus.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:stocktaking_surplus_create')
        context['edit_url_name'] = 'inventory:stocktaking_surplus_edit'
        context['delete_url_name'] = 'inventory:stocktaking_surplus_delete'
        context['lock_url_name'] = 'inventory:stocktaking_surplus_lock'
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.surplus')
        return context


class StocktakingSurplusCreateView(StocktakingFormMixin, CreateView):
    """Create view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    form_title = _('ایجاد سند مازاد انبارگردانی')
    list_url_name = 'inventory:stocktaking_surplus'
    lock_url_name = 'inventory:stocktaking_surplus_lock'

    def form_valid(self, form):
        """Set company and created_by before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند مازاد انبارگردانی با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingSurplusUpdateView(DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    """Update view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    form_class = forms.StocktakingSurplusForm
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    form_title = _('ویرایش سند مازاد انبارگردانی')
    list_url_name = 'inventory:stocktaking_surplus'
    lock_url_name = 'inventory:stocktaking_surplus_lock'

    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند مازاد انبارگردانی با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id', 'item', 'warehouse', 'unit']),
            (_('مقادیر'), ['quantity_expected', 'quantity_counted', 'quantity_adjusted']),
            (_('ارزش‌گذاری'), ['valuation_method', 'unit_cost', 'total_cost']),
            (_('جزئیات اضافه'), ['reason_code', 'investigation_reference']),
        ]


class StocktakingSurplusDeleteView(DocumentDeleteViewBase):
    """Delete view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    template_name = 'inventory/stocktaking_surplus_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_surplus')
    feature_code = 'inventory.stocktaking.surplus'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('سند مازاد موجودی با موفقیت حذف شد.')


class StocktakingSurplusLockView(DocumentLockView):
    """Lock view for stocktaking surplus records."""
    model = models.StocktakingSurplus
    success_url_name = 'inventory:stocktaking_surplus'
    success_message = _('سند مازاد شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


# ============================================================================
# Stocktaking Record Views
# ============================================================================

class StocktakingRecordListView(InventoryBaseView, ListView):
    """List view for stocktaking records."""
    model = models.StocktakingRecord
    template_name = 'inventory/stocktaking_records.html'
    context_object_name = 'records'
    paginate_by = 50

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('inventory:stocktaking_record_create')
        context['edit_url_name'] = 'inventory:stocktaking_record_edit'
        context['delete_url_name'] = 'inventory:stocktaking_record_delete'
        context['lock_url_name'] = 'inventory:stocktaking_record_lock'
        self.add_delete_permissions_to_context(context, 'inventory.stocktaking.records')
        return context


class StocktakingRecordCreateView(StocktakingFormMixin, CreateView):
    """Create view for stocktaking records."""
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    form_title = _('ایجاد سند نهایی انبارگردانی')
    list_url_name = 'inventory:stocktaking_records'
    lock_url_name = 'inventory:stocktaking_record_lock'

    def form_valid(self, form):
        """Set company and created_by before saving."""
        company_id: Optional[int] = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند نهایی انبارگردانی با موفقیت ایجاد شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approver', 'approval_status', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]


class StocktakingRecordUpdateView(DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView):
    """Update view for stocktaking records."""
    model = models.StocktakingRecord
    form_class = forms.StocktakingRecordForm
    success_url = reverse_lazy('inventory:stocktaking_records')
    form_title = _('ویرایش سند نهایی انبارگردانی')
    list_url_name = 'inventory:stocktaking_records'
    lock_url_name = 'inventory:stocktaking_record_lock'

    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('سند نهایی انبارگردانی با موفقیت بروزرسانی شد.'))
        return response

    def get_fieldsets(self) -> list:
        """Return fieldsets configuration."""
        return [
            (_('اطلاعات سند'), ['stocktaking_session_id']),
            (_('تأیید موجودی'), ['confirmed_by', 'confirmation_notes']),
            (_('وضعیت تایید'), ['approver', 'approval_status', 'approver_notes']),
            (_('خلاصه موجودی'), ['final_inventory_value']),
        ]


class StocktakingRecordDeleteView(DocumentDeleteViewBase):
    """Delete view for stocktaking records."""
    model = models.StocktakingRecord
    template_name = 'inventory/stocktaking_record_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktaking_records')
    feature_code = 'inventory.stocktaking.records'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('سند شمارش موجودی با موفقیت حذف شد.')


class StocktakingRecordLockView(DocumentLockView):
    """Lock view for stocktaking records."""
    model = models.StocktakingRecord
    success_url_name = 'inventory:stocktaking_records'
    success_message = _('سند شمارش موجودی قفل شد و دیگر قابل ویرایش نیست.')


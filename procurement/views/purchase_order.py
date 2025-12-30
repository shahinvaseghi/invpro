"""
Views for Purchase Order.
"""
from typing import Dict, Any, List, Optional
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .base import ProcurementBaseView
from inventory.views.base import LineFormsetMixin
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseFormsetUpdateView,
    BaseDetailView,
    BaseDeleteView,
)
from procurement.models import PurchaseOrder
from procurement import forms


class PurchaseOrderListView(ProcurementBaseView, BaseListView):
    """List view for purchase orders."""
    model = PurchaseOrder
    template_name = 'procurement/purchase_order_list.html'
    feature_code = 'procurement.orders.list'
    search_fields = ['order_code']
    filter_fields = ['order_status']
    default_order_by = ['-order_date', '-order_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['supplier']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['lines__item']
    
    def apply_custom_filters(self, queryset):
        """Apply custom filters."""
        queryset = super().apply_custom_filters(queryset)
        
        # Custom search
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(order_code__icontains=search)
                | Q(supplier__name__icontains=search)
                | Q(lines__item__name__icontains=search)
            ).distinct()
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Purchase Orders')
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('procurement:purchase_order_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Purchase Order')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'procurement:purchase_order_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'procurement:purchase_order_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'procurement:purchase_order_delete'


class PurchaseOrderFormMixin(ProcurementBaseView):
    """Form mixin for purchase order views."""
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = super().get_formset_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs


class PurchaseOrderCreateView(LineFormsetMixin, PurchaseOrderFormMixin, BaseCreateView):
    """Create view for purchase orders."""
    model = PurchaseOrder
    form_class = forms.PurchaseOrderForm
    formset_class = forms.PurchaseOrderLineFormSet
    formset_prefix = 'lines'
    template_name = 'procurement/purchase_order_form.html'
    success_url = reverse_lazy('procurement:purchase_orders')
    feature_code = 'procurement.orders.list'
    success_message = _('سفارش خرید با موفقیت ایجاد شد.')
    form_title = _('ایجاد سفارش خرید')
    
    def form_valid(self, form):
        """Save purchase order and lines."""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        
        form.instance.company_id = company_id
        
        # Build and validate formset
        lines_formset = self.build_line_formset(data=self.request.POST, instance=None, company_id=company_id)
        
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Check if we have at least one valid line
        valid_lines = [
            line_form for line_form in lines_formset.forms
            if line_form.cleaned_data and not line_form.cleaned_data.get('DELETE', False)
            and line_form.cleaned_data.get('item')
        ]
        
        if not valid_lines:
            form.add_error(None, _('حداقل یک ردیف با کالا اضافه کنید.'))
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
        # Save document first
        response = super().form_valid(form)
        
        # Save formset
        lines_formset.instance = self.object
        lines_formset.save()
        
        return response


class PurchaseOrderDetailView(ProcurementBaseView, BaseDetailView):
    """Detail view for purchase orders."""
    model = PurchaseOrder
    template_name = 'procurement/purchase_order_detail.html'
    context_object_name = 'purchase_order'
    feature_code = 'procurement.orders.list'
    
    def get_prefetch_related(self):
        """Prefetch related objects."""
        return ['lines__item']
    
    def get_select_related(self):
        """Select related objects."""
        return ['supplier', 'purchase_request']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Purchase Order')
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('procurement:purchase_orders')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('procurement:purchase_order_edit', kwargs={'pk': self.object.pk})


class PurchaseOrderUpdateView(LineFormsetMixin, PurchaseOrderFormMixin, BaseFormsetUpdateView):
    """Update view for purchase orders."""
    model = PurchaseOrder
    form_class = forms.PurchaseOrderForm
    formset_class = forms.PurchaseOrderLineFormSet
    formset_prefix = 'lines'
    template_name = 'procurement/purchase_order_form.html'
    success_url = reverse_lazy('procurement:purchase_orders')
    feature_code = 'procurement.orders.list'
    success_message = _('سفارش خرید با موفقیت بروزرسانی شد.')
    form_title = _('ویرایش سفارش خرید')
    
    def get_queryset(self):
        """Get queryset with proper filtering."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        queryset = queryset.select_related('supplier', 'purchase_request').prefetch_related('lines__item')
        return queryset


class PurchaseOrderDeleteView(ProcurementBaseView, BaseDeleteView):
    """Delete view for purchase orders."""
    model = PurchaseOrder
    template_name = 'procurement/purchase_order_confirm_delete.html'
    success_url = reverse_lazy('procurement:purchase_orders')
    feature_code = 'procurement.orders.list'
    success_message = _('سفارش خرید با موفقیت حذف شد.')


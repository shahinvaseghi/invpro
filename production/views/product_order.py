"""
Product Order CRUD views for production module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from production.forms import ProductOrderForm
from production.models import ProductOrder


class ProductOrderListView(FeaturePermissionRequiredMixin, ListView):
    """List all product orders for the active company."""
    model = ProductOrder
    template_name = 'production/product_orders.html'
    context_object_name = 'product_orders'
    paginate_by = 50
    feature_code = 'production.product_orders'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter product orders by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return ProductOrder.objects.none()
        
        queryset = ProductOrder.objects.filter(
            company_id=active_company_id
        ).select_related(
            'finished_item',
            'bom',
            'process',
            'approved_by',
        ).order_by('-order_date', 'order_code')
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


class ProductOrderCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new product order."""
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'production/product_order_form.html'
    success_url = reverse_lazy('production:product_orders')
    feature_code = 'production.product_orders'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect:
        """Auto-set company, created_by, finished_item, and bom_code."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        # Auto-set finished_item from BOM
        if form.cleaned_data.get('bom'):
            form.instance.finished_item = form.cleaned_data['bom'].finished_item
            form.instance.finished_item_code = form.cleaned_data['bom'].finished_item.item_code
            form.instance.bom_code = form.cleaned_data['bom'].bom_code
        
        # Auto-generate order_code if not provided
        if not form.instance.order_code:
            from inventory.utils.codes import generate_sequential_code
            form.instance.order_code = generate_sequential_code(
                ProductOrder,
                company_id=active_company_id,
                field='order_code',
                width=10,
            )
        
        # Set unit from finished_item if available
        if form.instance.finished_item and not form.instance.unit:
            form.instance.unit = form.instance.finished_item.primary_unit or 'pcs'
        
        messages.success(self.request, _('Product order created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create Product Order')
        return context


class ProductOrderUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing product order."""
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'production/product_order_form.html'
    success_url = reverse_lazy('production:product_orders')
    feature_code = 'production.product_orders'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return ProductOrder.objects.none()
        return ProductOrder.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect:
        """Auto-set edited_by and update related fields."""
        form.instance.edited_by = self.request.user
        
        # Update finished_item and bom_code if BOM changed
        if form.cleaned_data.get('bom'):
            form.instance.finished_item = form.cleaned_data['bom'].finished_item
            form.instance.finished_item_code = form.cleaned_data['bom'].finished_item.item_code
            form.instance.bom_code = form.cleaned_data['bom'].bom_code
        
        messages.success(self.request, _('Product order updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit Product Order')
        return context


class ProductOrderDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a product order."""
    model = ProductOrder
    success_url = reverse_lazy('production:product_orders')
    template_name = 'production/product_order_confirm_delete.html'
    feature_code = 'production.product_orders'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return ProductOrder.objects.none()
        return ProductOrder.objects.filter(company_id=active_company_id)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete product order and show success message."""
        messages.success(self.request, _('Product order deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


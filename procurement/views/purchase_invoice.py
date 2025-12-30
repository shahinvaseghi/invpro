"""
Views for Purchase Invoice.
"""
from typing import Dict, Any, List, Optional
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .base import ProcurementBaseView
from inventory.views.base import LineFormsetMixin
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseFormsetUpdateView,
    BaseDetailView,
    BaseDeleteView,
)
from procurement.models import PurchaseInvoice
from procurement import forms


class PurchaseInvoiceListView(ProcurementBaseView, BaseListView):
    """List view for purchase invoices."""
    model = PurchaseInvoice
    template_name = 'procurement/purchase_invoice_list.html'
    feature_code = 'procurement.invoices.purchase'
    search_fields = ['invoice_code']
    filter_fields = ['invoice_status']
    default_order_by = ['-invoice_date', '-invoice_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['supplier', 'party']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['lines__item']
    
    def apply_custom_filters(self, queryset):
        """Apply custom filters."""
        queryset = super().apply_custom_filters(queryset)
        
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(invoice_code__icontains=search)
                | Q(supplier__name__icontains=search)
                | Q(lines__item__name__icontains=search)
            ).distinct()
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Purchase Invoices')
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('procurement:purchase_invoice_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Purchase Invoice')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'procurement:purchase_invoice_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'procurement:purchase_invoice_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'procurement:purchase_invoice_delete'


class PurchaseInvoiceFormMixin(ProcurementBaseView):
    """Form mixin for purchase invoice views."""
    
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


class PurchaseInvoiceCreateView(LineFormsetMixin, PurchaseInvoiceFormMixin, BaseCreateView):
    """Create view for purchase invoices."""
    model = PurchaseInvoice
    form_class = forms.PurchaseInvoiceForm
    formset_class = forms.PurchaseInvoiceLineFormSet
    formset_prefix = 'lines'
    template_name = 'procurement/purchase_invoice_form.html'
    success_url = reverse_lazy('procurement:purchase_invoices')
    feature_code = 'procurement.invoices.purchase'
    success_message = _('فاکتور خرید با موفقیت ایجاد شد.')
    form_title = _('ایجاد فاکتور خرید')
    
    def form_valid(self, form):
        """Save purchase invoice and lines."""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            form.add_error(None, _('شرکت فعال مشخص نشده است.'))
            return self.form_invalid(form)
        
        form.instance.company_id = company_id
        
        lines_formset = self.build_line_formset(data=self.request.POST, instance=None, company_id=company_id)
        
        if not lines_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, lines_formset=lines_formset)
            )
        
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
        
        response = super().form_valid(form)
        lines_formset.instance = self.object
        lines_formset.save()
        return response


class PurchaseInvoiceDetailView(ProcurementBaseView, BaseDetailView):
    """Detail view for purchase invoices."""
    model = PurchaseInvoice
    template_name = 'procurement/purchase_invoice_detail.html'
    context_object_name = 'purchase_invoice'
    feature_code = 'procurement.invoices.purchase'
    
    def get_prefetch_related(self):
        """Prefetch related objects."""
        return ['lines__item']
    
    def get_select_related(self):
        """Select related objects."""
        return ['supplier', 'party', 'receipt_permanent', 'purchase_order']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Purchase Invoice')
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('procurement:purchase_invoices')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('procurement:purchase_invoice_edit', kwargs={'pk': self.object.pk})


class PurchaseInvoiceUpdateView(LineFormsetMixin, PurchaseInvoiceFormMixin, BaseFormsetUpdateView):
    """Update view for purchase invoices."""
    model = PurchaseInvoice
    form_class = forms.PurchaseInvoiceForm
    formset_class = forms.PurchaseInvoiceLineFormSet
    formset_prefix = 'lines'
    template_name = 'procurement/purchase_invoice_form.html'
    success_url = reverse_lazy('procurement:purchase_invoices')
    feature_code = 'procurement.invoices.purchase'
    success_message = _('فاکتور خرید با موفقیت بروزرسانی شد.')
    form_title = _('ویرایش فاکتور خرید')
    
    def get_queryset(self):
        """Get queryset with proper filtering."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        queryset = queryset.select_related('supplier', 'party').prefetch_related('lines__item')
        return queryset


class PurchaseInvoiceDeleteView(ProcurementBaseView, BaseDeleteView):
    """Delete view for purchase invoices."""
    model = PurchaseInvoice
    template_name = 'procurement/purchase_invoice_confirm_delete.html'
    success_url = reverse_lazy('procurement:purchase_invoices')
    feature_code = 'procurement.invoices.purchase'
    success_message = _('فاکتور خرید با موفقیت حذف شد.')


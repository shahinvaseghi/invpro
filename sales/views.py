"""
Views for sales module.
"""
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import BaseListView

from .forms import ItemPriceCardFormSet
from .models import ItemPriceCard


class SalesDashboardView(FeaturePermissionRequiredMixin, TemplateView):
    """Dashboard view for sales module."""
    template_name = 'sales/dashboard.html'
    feature_code = 'sales.dashboard'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['page_title'] = 'فروش'
        return context


class SalesInvoiceCreateView(FeaturePermissionRequiredMixin, TemplateView):
    """Create view for sales invoice."""
    template_name = 'sales/invoice_create.html'
    feature_code = 'sales.invoice'
    required_action = 'create'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['page_title'] = 'صدور فاکتور فروش'
        return context


class ItemPriceCardListView(BaseListView):
    """List view for item price cards."""
    model = ItemPriceCard
    feature_code = 'sales.price_card'
    search_fields = ['item__name', 'item__name_en', 'item_code', 'item__item_code']
    filter_fields = ['is_enabled', 'currency']
    default_order_by = ['item_code']
    paginate_by = 50

    def get_select_related(self):
        """Optimize queries by selecting related item."""
        return ['item']

    def get_breadcrumbs(self):
        """Return breadcrumbs for price card list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': None},
            {'label': _('Item Price Cards'), 'url': None},
        ]

    def get_create_url(self):
        """Return create URL for price cards."""
        return reverse('sales:price_card_create')

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Price Card')

    def get_page_title(self) -> str:
        """Return page title."""
        return _('Item Price Cards')

    def get_context_data(self, **kwargs):
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['table_headers'] = [
            {'label': _('Item Code'), 'field': 'item_code', 'type': 'code'},
            {'label': _('Item Name'), 'field': 'item.name'},
            {'label': _('Price'), 'field': 'price'},
            {'label': _('Currency'), 'field': 'currency'},
            {'label': _('Effective Date'), 'field': 'effective_date', 'type': 'date'},
            {'label': _('Expiry Date'), 'field': 'expiry_date', 'type': 'date'},
            {'label': _('Status'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('Active'), 'false_label': _('Inactive')},
        ]
        context['print_enabled'] = True
        return context


class ItemPriceCardCreateView(FeaturePermissionRequiredMixin, View):
    """Create view for item price cards with formset."""
    template_name = 'sales/price_card_form.html'
    success_url = reverse_lazy('sales:price_card_list')
    feature_code = 'sales.price_card'
    required_action = 'create'
    formset_class = ItemPriceCardFormSet
    formset_prefix = 'price_cards'
    
    def get_formset_kwargs(self):
        """Return kwargs for formset."""
        kwargs = {
            'company_id': self.request.session.get('active_company_id'),
        }
        return kwargs
    
    def get_context_data(self, formset=None):
        """Get context data for template."""
        if formset is None:
            if self.request.method == 'POST':
                formset = self.formset_class(
                    self.request.POST,
                    prefix=self.formset_prefix,
                    **self.get_formset_kwargs()
                )
            else:
                formset = self.formset_class(
                    prefix=self.formset_prefix,
                    **self.get_formset_kwargs()
                )
        
        return {
            'active_module': 'sales',
            'page_title': _('Create Item Price Cards'),
            'breadcrumbs': [
                {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
                {'label': _('Sales'), 'url': None},
                {'label': _('Item Price Cards'), 'url': reverse('sales:price_card_list')},
                {'label': _('Create'), 'url': None},
            ],
            'formset': formset,
        }
    
    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        from django.shortcuts import render
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        from django.contrib import messages
        from django.shortcuts import render
        
        formset = self.formset_class(
            request.POST,
            prefix=self.formset_prefix,
            **self.get_formset_kwargs()
        )
        
        if formset.is_valid():
            with transaction.atomic():
                company_id = request.session.get('active_company_id')
                if not company_id:
                    messages.error(request, _('No active company selected.'))
                    return render(request, self.template_name, self.get_context_data(formset=formset))
                
                # Check for duplicate items
                item_ids = []
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        item = form.cleaned_data.get('item')
                        if item:
                            if item.id in item_ids:
                                form.add_error('item', _('This item is already selected in another row.'))
                                return render(request, self.template_name, self.get_context_data(formset=formset))
                            item_ids.append(item.id)
                            
                            # Check if item already has a price card
                            existing = ItemPriceCard.objects.filter(
                                company_id=company_id,
                                item=item
                            )
                            if existing.exists():
                                form.add_error('item', _('This item already has a price card. Please update the existing one instead.'))
                                return render(request, self.template_name, self.get_context_data(formset=formset))
                
                # Save all forms in formset
                instances = formset.save(commit=False)
                for instance in instances:
                    # Set company for each instance
                    instance.company_id = company_id
                    instance.save()
                
                # Delete marked forms
                for obj in formset.deleted_objects:
                    obj.delete()
            
            messages.success(request, _('Price cards created successfully.'))
            return HttpResponseRedirect(self.success_url)
        else:
            # Formset validation failed
            return render(request, self.template_name, self.get_context_data(formset=formset))

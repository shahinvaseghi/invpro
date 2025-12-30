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
from shared.views.base import BaseListView, BaseUpdateView

from .forms import ItemPriceCardFormSet, SalesSettingsForm
from .models import ItemPriceCard, SalesSettings


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
            # #region agent log
            import json
            import time
            try:
                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({
                        'id': f'log_{int(time.time()*1000)}_formset_valid',
                        'timestamp': int(time.time()*1000),
                        'location': 'sales/views.py:155',
                        'message': 'Formset is valid, starting save process',
                        'data': {'forms_count': len(formset.forms)},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'R'
                    }) + '\n')
            except Exception:
                pass
            # #endregion

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
                
                # Save all forms in formset manually
                saved_count = 0
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        # #region agent log
                        try:
                            with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                                f.write(json.dumps({
                                    'id': f'log_{int(time.time()*1000)}_saving_form',
                                    'timestamp': int(time.time()*1000),
                                    'location': 'sales/views.py:183',
                                    'message': 'Saving form instance',
                                    'data': {
                                        'has_instance': form.instance is not None,
                                        'instance_pk': form.instance.pk if form.instance and form.instance.pk else None,
                                        'item_id': form.cleaned_data.get('item').pk if form.cleaned_data.get('item') else None
                                    },
                                    'sessionId': 'debug-session',
                                    'runId': 'run1',
                                    'hypothesisId': 'R'
                                }) + '\n')
                        except Exception:
                            pass
                        # #endregion

                        # Save form instance (ItemPriceCardForm is a ModelForm, so it has save() method)
                        try:
                            instance = form.save(commit=False)
                            instance.company_id = company_id
                            instance.save()
                            saved_count += 1
                            # #region agent log
                            try:
                                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                                    f.write(json.dumps({
                                        'id': f'log_{int(time.time()*1000)}_form_saved',
                                        'timestamp': int(time.time()*1000),
                                        'location': 'sales/views.py:187',
                                        'message': 'Form instance saved successfully',
                                        'data': {'instance_pk': instance.pk, 'item_id': instance.item.pk if instance.item else None},
                                        'sessionId': 'debug-session',
                                        'runId': 'run1',
                                        'hypothesisId': 'R'
                                    }) + '\n')
                            except Exception:
                                pass
                            # #endregion
                        except Exception as e:
                            # #region agent log
                            try:
                                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                                    f.write(json.dumps({
                                        'id': f'log_{int(time.time()*1000)}_form_save_error',
                                        'timestamp': int(time.time()*1000),
                                        'location': 'sales/views.py:187',
                                        'message': 'Form save failed',
                                        'data': {'error': str(e), 'error_type': type(e).__name__},
                                        'sessionId': 'debug-session',
                                        'runId': 'run1',
                                        'hypothesisId': 'R'
                                    }) + '\n')
                            except Exception:
                                pass
                            # #endregion
                            raise
                
                # Delete marked forms
                for form in formset:
                    if form.cleaned_data and form.cleaned_data.get('DELETE', False):
                        if form.instance and form.instance.pk:
                            form.instance.delete()
            
            # #region agent log
            try:
                with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({
                        'id': f'log_{int(time.time()*1000)}_all_saved',
                        'timestamp': int(time.time()*1000),
                        'location': 'sales/views.py:193',
                        'message': 'All forms saved successfully',
                        'data': {'saved_count': saved_count},
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'R'
                    }) + '\n')
            except Exception:
                pass
            # #endregion

            messages.success(request, _('Price cards created successfully.'))
            return HttpResponseRedirect(self.success_url)
        else:
            # Formset validation failed
            return render(request, self.template_name, self.get_context_data(formset=formset))


class SalesSettingsView(BaseUpdateView):
    """Settings view for sales module."""
    model = SalesSettings
    form_class = SalesSettingsForm
    template_name = 'sales/settings.html'
    feature_code = 'sales.settings'
    success_url = reverse_lazy('sales:settings')
    success_message = _('تنظیمات فروش با موفقیت به‌روزرسانی شد.')

    def get_object(self, queryset=None):
        """Get or create settings for current company."""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            from django.contrib import messages
            messages.error(self.request, _('هیچ شرکتی انتخاب نشده است.'))
            return None
        return SalesSettings.get_or_create_for_company(company_id)

    def get_breadcrumbs(self):
        """Return breadcrumbs for settings."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': reverse('sales:dashboard')},
            {'label': _('Settings'), 'url': None},
        ]

    def get_page_title(self) -> str:
        """Return page title."""
        return _('تنظیمات فروش')

    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['page_title'] = self.get_page_title()
        return context


class CustomersListView(FeaturePermissionRequiredMixin, TemplateView):
    """List view for customers."""
    template_name = 'sales/customers.html'
    feature_code = 'sales.customers'
    required_action = 'view'

    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['page_title'] = _('مشتریان')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': reverse('sales:dashboard')},
            {'label': _('Customers'), 'url': None},
        ]
        return context

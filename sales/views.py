"""
Views for sales module.
"""
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import BaseListView

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
        # TODO: Create view will be implemented later
        return None

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

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
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
)

from .forms import ItemPriceCardFormSet, SalesSettingsForm, ItemPriceCardForm, CustomerForm, IncomeReceiptLocationForm
from .models import ItemPriceCard, SalesSettings, IncomeReceiptLocation
from accounting.models import Party, Account, TafsiliLevelSubAccountRelation, PartyAccount
from accounting.models.accounts import TafsiliSubAccountRelation


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

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'sales:price_card_detail'

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'sales:price_card_edit'

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'sales:price_card_delete'

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


class ItemPriceCardDetailView(BaseDetailView):
    """Detail view for viewing item price card (read-only)."""
    model = ItemPriceCard
    template_name = 'sales/price_card_detail.html'
    context_object_name = 'price_card'
    feature_code = 'sales.price_card'
    permission_field = ''  # No permission field needed

    def get_select_related(self):
        """Optimize queries by selecting related item."""
        return ['item']

    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Item Price Card')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': None},
            {'label': _('Item Price Cards'), 'url': reverse('sales:price_card_list')},
            {'label': _('View'), 'url': None},
        ]

    def get_list_url(self):
        """Return list URL."""
        return reverse('sales:price_card_list')

    def get_edit_url(self):
        """Return edit URL."""
        return reverse('sales:price_card_edit', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = []
        return context


class ItemPriceCardUpdateView(BaseUpdateView):
    """Update view for editing item price card."""
    model = ItemPriceCard
    form_class = ItemPriceCardForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('sales:price_card_list')
    feature_code = 'sales.price_card'
    success_message = _('Price card updated successfully.')

    def get_select_related(self):
        """Optimize queries by selecting related item."""
        return ['item']

    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        instance = kwargs.get('instance')
        company_id = instance.company_id if instance else self.request.session.get('active_company_id')
        kwargs['company_id'] = company_id
        
        # #region agent log
        import json
        import time
        try:
            with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({
                    'id': f'log_{int(time.time()*1000)}_update_get_form_kwargs',
                    'timestamp': int(time.time()*1000),
                    'location': 'sales/views.py:get_form_kwargs',
                    'message': 'ItemPriceCardUpdateView.get_form_kwargs',
                    'data': {
                        'instance_pk': instance.pk if instance else None,
                        'company_id': company_id,
                        'has_instance': instance is not None
                    },
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'S'
                }) + '\n')
        except Exception:
            pass
        # #endregion
        
        return kwargs

    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Item Price Card')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': None},
            {'label': _('Item Price Cards'), 'url': reverse('sales:price_card_list')},
            {'label': _('Edit'), 'url': None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('sales:price_card_list')

    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'sales'
        
        # #region agent log
        import json
        import time
        try:
            with open('/home/shahin/invproj/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({
                    'id': f'log_{int(time.time()*1000)}_update_context',
                    'timestamp': int(time.time()*1000),
                    'location': 'sales/views.py:get_context_data',
                    'message': 'ItemPriceCardUpdateView.get_context_data',
                    'data': {
                        'has_form': 'form' in context,
                        'form_instance_pk': context.get('form').instance.pk if context.get('form') and context.get('form').instance else None,
                        'object_pk': self.object.pk if hasattr(self, 'object') and self.object else None,
                        'form_initial': dict(context.get('form').initial) if context.get('form') and hasattr(context.get('form'), 'initial') else None
                    },
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'S'
                }) + '\n')
        except Exception:
            pass
        # #endregion
        
        return context


class ItemPriceCardDeleteView(BaseDeleteView):
    """Delete view for item price card."""
    model = ItemPriceCard
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('sales:price_card_list')
    feature_code = 'sales.price_card'
    success_message = _('Price card deleted successfully.')
    owner_field = ''  # No owner field needed

    def get_select_related(self):
        """Optimize queries by selecting related item."""
        return ['item']

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Item Price Card')

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this price card?')

    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': None},
            {'label': _('Item Price Cards'), 'url': reverse('sales:price_card_list')},
            {'label': _('Delete'), 'url': None},
        ]

    def get_object_details(self):
        """Return object details."""
        return [
            {'label': _('Item Code'), 'value': self.object.item_code},
            {'label': _('Item Name'), 'value': self.object.item.name if self.object.item else '-'},
            {'label': _('Price'), 'value': str(self.object.price)},
            {'label': _('Currency'), 'value': self.object.get_currency_display()},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('sales:price_card_list')


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


class CustomersListView(BaseListView):
    """List view for customers."""
    model = Party
    template_name = 'shared/generic/generic_list.html'
    feature_code = 'sales.customers'
    required_action = 'view'
    active_module = 'sales'
    search_fields = ['party_code', 'party_name', 'party_name_en', 'national_id', 'tax_id', 'phone', 'email']
    filter_fields = ['is_enabled']
    default_order_by = ['party_code']
    paginate_by = 50
    
    def get_base_queryset(self):
        """Filter by customer party_type."""
        return Party.objects.filter(party_type='customer')
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': reverse('sales:dashboard')},
            {'label': _('Customers'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('sales:customer_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Customer')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'sales:customer_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'sales:customer_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'sales:customer_delete'
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('مشتریان')
    
    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد مشتری'), 'field': 'party_code', 'type': 'code'},
            {'label': _('نام مشتری'), 'field': 'party_name'},
            {'label': _('کد ملی / شماره ثبت'), 'field': 'national_id'},
            {'label': _('شناسه مالیاتی'), 'field': 'tax_id'},
            {'label': _('تلفن'), 'field': 'phone'},
            {'label': _('ایمیل'), 'field': 'email'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        context['print_enabled'] = True
        return context


class CustomerCreateView(BaseCreateView):
    """Create view for customers."""
    model = Party
    form_class = CustomerForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('sales:customers')
    feature_code = 'sales.customers'
    required_action = 'create'
    active_module = 'sales'
    success_message = _('مشتری با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        """Create customer and auto-create tafsili account."""
        from django.db import transaction
        from django.contrib import messages
        from inventory.utils.codes import generate_sequential_code
        
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            messages.error(self.request, _('لطفاً ابتدا یک شرکت را انتخاب کنید.'))
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Set party_type to customer
            form.instance.party_type = 'customer'
            form.instance.created_by = self.request.user
            
            # Save customer
            customer = form.save()
            
            # Get selected tafsili level
            tafsili_level = form.cleaned_data.get('tafsili_level')
            if not tafsili_level:
                messages.error(self.request, _('لطفاً سطح تفصیلی را انتخاب کنید.'))
                return self.form_invalid(form)
            
            # Get primary sub account from tafsili level
            primary_sub_account_relation = TafsiliLevelSubAccountRelation.objects.filter(
                tafsili_level=tafsili_level,
                company_id=company_id,
                is_primary=1
            ).first()
            
            if not primary_sub_account_relation:
                # If no primary, get first sub account
                primary_sub_account_relation = TafsiliLevelSubAccountRelation.objects.filter(
                    tafsili_level=tafsili_level,
                    company_id=company_id
                ).first()
            
            if not primary_sub_account_relation:
                messages.error(self.request, _('سطح تفصیلی انتخاب شده حساب معین مرتبط ندارد.'))
                return self.form_invalid(form)
            
            primary_sub_account = primary_sub_account_relation.sub_account
            
            # Generate account code for tafsili account
            account_code = generate_sequential_code(
                Account,
                company_id=company_id,
                field='account_code',
                width=10,
                extra_filters={'account_level': 3},
            )
            
            # Create tafsili account
            tafsili_account = Account.objects.create(
                company_id=company_id,
                account_code=account_code,
                account_name=customer.party_name,
                account_name_en=customer.party_name_en or '',
                account_level=3,
                parent_account=primary_sub_account,
                tafsili_type=None,  # Can be set later if needed
                is_enabled=1,
                created_by=self.request.user,
            )
            
            # Create relation between tafsili account and sub account
            TafsiliSubAccountRelation.objects.create(
                tafsili_account=tafsili_account,
                sub_account=primary_sub_account,
                company_id=company_id,
                is_primary=1,
                created_by=self.request.user,
            )
            
            # Create PartyAccount to link customer with tafsili account
            PartyAccount.objects.create(
                party=customer,
                account=tafsili_account,
                company_id=company_id,
                is_primary=1,
                created_by=self.request.user,
            )
        
        return super().form_valid(form)
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': reverse('sales:dashboard')},
            {'label': _('Customers'), 'url': reverse('sales:customers')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('sales:customers')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ایجاد مشتری جدید')


class IncomeReceiptLocationListView(BaseListView):
    """List view for income receipt locations."""
    model = IncomeReceiptLocation
    template_name = 'shared/generic/generic_list.html'
    feature_code = 'sales.income_receipt_location'
    required_action = 'view'
    active_module = 'sales'
    search_fields = ['location_name', 'treasury_account__account_name', 'treasury_account__bank_name']
    filter_fields = ['is_enabled', 'receipt_method']
    default_order_by = ['location_name']
    paginate_by = 50
    
    def get_select_related(self):
        """Optimize queries by selecting related treasury_account."""
        return ['treasury_account']
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': reverse('sales:dashboard')},
            {'label': _('محل دریافت درآمد'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('sales:income_receipt_location_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('ایجاد محل دریافت درآمد')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'sales:income_receipt_location_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'sales:income_receipt_location_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'sales:income_receipt_location_delete'
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('محل دریافت درآمد')
    
    def get_context_data(self, **kwargs):
        """Add context variables."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('نام محل'), 'field': 'location_name'},
            {'label': _('حساب نقدی/بانکی'), 'field': 'treasury_account.account_name'},
            {'label': _('نوع حساب'), 'field': 'treasury_account.get_account_type_display'},
            {'label': _('روش دریافت'), 'field': 'get_receipt_method_display'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        context['print_enabled'] = True
        return context


class IncomeReceiptLocationCreateView(BaseCreateView):
    """Create view for income receipt locations."""
    model = IncomeReceiptLocation
    form_class = IncomeReceiptLocationForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('sales:income_receipt_location_list')
    feature_code = 'sales.income_receipt_location'
    required_action = 'create'
    active_module = 'sales'
    success_message = _('محل دریافت درآمد با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_breadcrumbs(self):
        """Return breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Sales'), 'url': reverse('sales:dashboard')},
            {'label': _('محل دریافت درآمد'), 'url': reverse('sales:income_receipt_location_list')},
            {'label': _('ایجاد'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('sales:income_receipt_location_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ایجاد محل دریافت درآمد جدید')

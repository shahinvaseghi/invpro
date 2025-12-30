"""
Tafsili Type (نوع تفصیلی) CRUD views for accounting module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from typing import Optional
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
    EditLockProtectedMixin,
)
from accounting.models import TafsiliType
from accounting.forms import TafsiliTypeForm
from accounting.views.base import AccountingBaseView


class TafsiliTypeListView(BaseListView):
    """
    List all Tafsili Types (نوع تفصیلی) for the active company.
    """
    model = TafsiliType
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['sort_order', 'public_code']
    default_status_filter = True
    
    def get_base_queryset(self):
        """Get base queryset filtered by company."""
        queryset = TafsiliType.objects.all()
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['public_code', 'name', 'name_en']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('مدیریت انواع تفصیلی')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('مدیریت انواع تفصیلی'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:tafsili_type_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('افزودن نوع تفصیلی')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:tafsili_type_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:tafsili_type_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:tafsili_type_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('هیچ نوع تفصیلی یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با افزودن اولین نوع تفصیلی شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📋'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد'), 'field': 'public_code', 'type': 'code'},
            {'label': _('نام (فارسی)'), 'field': 'name'},
            {'label': _('نام (انگلیسی)'), 'field': 'name_en'},
            {'label': _('ترتیب نمایش'), 'field': 'sort_order'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        context['print_enabled'] = True
        
        return context


class TafsiliTypeCreateView(BaseCreateView):
    """Create a new Tafsili Type (نوع تفصیلی)."""
    model = TafsiliType
    form_class = TafsiliTypeForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_types')
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('نوع تفصیلی با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: TafsiliTypeForm) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('مدیریت انواع تفصیلی'), 'url': reverse('accounting:tafsili_types')},
            {'label': _('افزودن'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_types')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('افزودن نوع تفصیلی')


class TafsiliTypeUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing Tafsili Type (نوع تفصیلی)."""
    model = TafsiliType
    form_class = TafsiliTypeForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_types')
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('نوع تفصیلی با موفقیت به‌روزرسانی شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: TafsiliTypeForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('مدیریت انواع تفصیلی'), 'url': reverse('accounting:tafsili_types')},
            {'label': _('ویرایش'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_types')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ویرایش نوع تفصیلی')


class TafsiliTypeDetailView(BaseDetailView):
    """Detail view for viewing Tafsili Types (read-only)."""
    model = TafsiliType
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'view_own'
    active_module = 'accounting'
    
    def get_queryset(self):
        """Filter Tafsili Types by active company."""
        queryset = TafsiliType.objects.all()
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'created_by',
            'edited_by',
        )
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Tafsili Type')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        tafsili_type = self.object
        
        context['detail_title'] = self.get_page_title()
        info_banner = [
            {'label': _('Code'), 'value': tafsili_type.public_code, 'type': 'code'},
            {'label': _('Status'), 'value': tafsili_type.is_enabled, 'type': 'badge'},
        ]
        context['info_banner'] = info_banner
        
        # Basic Information section
        basic_fields = [
            {'label': _('Name (Persian)'), 'value': tafsili_type.name},
        ]
        if tafsili_type.name_en:
            basic_fields.append({'label': _('Name (English)'), 'value': tafsili_type.name_en})
        if tafsili_type.description:
            basic_fields.append({'label': _('Description'), 'value': tafsili_type.description})
        basic_fields.append({'label': _('Sort Order'), 'value': tafsili_type.sort_order})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:tafsili_types')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:tafsili_type_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class TafsiliTypeDeleteView(BaseDeleteView):
    """Delete a Tafsili Type (نوع تفصیلی)."""
    model = TafsiliType
    success_url = reverse_lazy('accounting:tafsili_types')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('نوع تفصیلی با موفقیت حذف شد.')
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if type can be deleted."""
        obj = self.get_object()
        # Check if type is used by any tafsili accounts
        from accounting.models import Account
        accounts_count = Account.objects.filter(
            tafsili_type=obj,
            account_level=3
        ).count()
        if accounts_count > 0:
            return False, _('این نوع تفصیلی در %(count)s حساب تفصیلی استفاده شده است و قابل حذف نیست.') % {'count': accounts_count}
        
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('حذف نوع تفصیلی')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('آیا مطمئن هستید که می‌خواهید این نوع تفصیلی را حذف کنید؟')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('کد'), 'value': self.object.public_code, 'type': 'code'},
            {'label': _('نام'), 'value': self.object.name},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('مدیریت انواع تفصیلی'), 'url': reverse('accounting:tafsili_types')},
            {'label': _('حذف'), 'url': None},
        ]


"""
User CRUD views for shared module.
"""
from typing import Any, Dict, List, Optional
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet, Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseDetailView,
    UserAccessFormsetMixin,
    EditLockProtectedMixin,
)
from shared.forms import UserCreateForm, UserUpdateForm
from shared.models import UserCompanyAccess

User = get_user_model()


class UserListView(BaseListView):
    """List all users."""
    model = User
    template_name = 'shared/users_list.html'
    feature_code = 'shared.users'
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filter_fields = []
    default_status_filter = False  # We handle status filter manually
    default_order_by = ['username']
    paginate_by = 20
    permission_field = ''  # Skip permission filtering for User model
    
    def get_base_queryset(self) -> QuerySet:
        """Get base queryset filtered by active company."""
        company_id = self.request.session.get('active_company_id')
        
        # Superusers can see all users
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        elif company_id:
            # Filter users who have access to the active company
            user_ids = UserCompanyAccess.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).values_list('user_id', flat=True)
            
            queryset = User.objects.filter(id__in=user_ids)
        else:
            # No active company selected - return empty queryset
            queryset = User.objects.none()
        
        return queryset.prefetch_related(
            'groups', 
            'company_accesses__company', 
            'company_accesses__access_level'
        )
    
    def get_queryset(self) -> QuerySet:
        """Filter users by search and status."""
        # Skip CompanyScopedViewMixin and BaseListView.get_queryset()
        # and use our custom logic directly
        queryset = self.get_base_queryset()
        
        # Apply search
        search_query = self.request.GET.get('search', '').strip()
        if search_query and self.search_fields:
            from shared.filters import apply_search
            queryset = apply_search(queryset, search_query, self.search_fields)
        
        # Apply custom status filter (is_active field)
        status: Optional[str] = self.request.GET.get('status')
        if status in {'active', 'inactive'}:
            queryset = queryset.filter(is_active=(status == 'active'))
        
        # Apply ordering
        if self.default_order_by:
            queryset = queryset.order_by(*self.default_order_by)
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Users')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('shared:user_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create User')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Username, email or name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse('shared:users')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'shared:user_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'shared:user_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'shared:user_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Users Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by adding your first user to the system.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '👤'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context variables."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['status_filter'] = True  # Enable status filter
        context['status_filter_value'] = self.request.GET.get('status', '')
        
        return context


class UserCreateView(BaseCreateView, UserAccessFormsetMixin):
    """Create a new user."""
    model = User
    form_class = UserCreateForm
    template_name = 'shared/user_form.html'
    success_url = reverse_lazy('shared:users')
    feature_code = 'shared.users'
    required_action = 'create'
    success_message = _('User created successfully.')
    
    # Skip company scoping for User model
    auto_set_company = False
    require_active_company = False

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add access formset and active module to context."""
        context = super().get_context_data(**kwargs)
        context.setdefault('access_formset', self.get_access_formset(context.get('form')))
        context['active_module'] = 'shared'
        context['is_create'] = True
        return context

    def form_valid(self, form: UserCreateForm) -> HttpResponseRedirect:
        """Save user and company access formset."""
        access_formset = self.get_access_formset(form)
        if not access_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, access_formset=access_formset))

        with transaction.atomic():
            # Save the core user fields (including role toggles & groups)
            self.object = form.save()
            # Persist company access rows
            access_formset.instance = self.object
            access_formset.save()
        
        return super().form_valid(form)
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create User')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': reverse('shared:users')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:users')


class UserUpdateView(BaseUpdateView, UserAccessFormsetMixin):
    """Update an existing user."""
    model = User
    form_class = UserUpdateForm
    template_name = 'shared/user_form.html'
    success_url = reverse_lazy('shared:users')
    feature_code = 'shared.users'
    required_action = 'edit_own'
    success_message = _('User updated successfully.')
    
    # Skip company scoping for User model
    auto_set_company = False
    require_active_company = False
    
    def get_queryset(self) -> QuerySet:
        """Get users filtered by active company."""
        company_id = self.request.session.get('active_company_id')
        
        # Superusers can see all users
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        elif company_id:
            # Filter users who have access to the active company
            user_ids = UserCompanyAccess.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).values_list('user_id', flat=True)
            
            queryset = User.objects.filter(id__in=user_ids)
        else:
            # No active company selected - return empty queryset
            queryset = User.objects.none()
        
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add access formset and active module to context."""
        context = super().get_context_data(**kwargs)
        context.setdefault('access_formset', self.get_access_formset(context.get('form')))
        context['active_module'] = 'shared'
        context['is_create'] = False
        return context

    def form_valid(self, form: UserUpdateForm) -> HttpResponseRedirect:
        """Save user and company access formset."""
        access_formset = self.get_access_formset(form)
        if not access_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, access_formset=access_formset))

        with transaction.atomic():
            # Persist user core data before saving company access rows
            self.object = form.save()
            access_formset.instance = self.object
            access_formset.save()
        
        return super().form_valid(form)
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit User')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': reverse('shared:users')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:users')


class UserDetailView(BaseDetailView):
    """Detail view for viewing users (read-only)."""
    model = User
    template_name = 'shared/user_detail.html'
    context_object_name = 'user_obj'
    feature_code = 'shared.users'
    required_action = 'view_own'
    
    def get_queryset(self) -> QuerySet:
        """Get users filtered by active company with prefetch related."""
        company_id = self.request.session.get('active_company_id')
        
        # Superusers can see all users
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        elif company_id:
            # Filter users who have access to the active company
            user_ids = UserCompanyAccess.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).values_list('user_id', flat=True)
            
            queryset = User.objects.filter(id__in=user_ids)
        else:
            # No active company selected - return empty queryset
            queryset = User.objects.none()
        
        queryset = queryset.select_related(
            'default_company',
        ).prefetch_related(
            'groups',
            'company_accesses__company',
            'company_accesses__access_level',
            'primary_groups',
        )
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context
    
    def get_page_title(self) -> str:
        """Return page title."""
        return str(self.object)
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': reverse('shared:users')},
            {'label': _('View'), 'url': None},
        ]
    
    def get_list_url(self):
        """Return list URL."""
        return reverse('shared:users')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse('shared:user_edit', kwargs={'pk': self.object.pk})
    
    @property
    def permission_field(self) -> str:
        """Skip permission filtering for User model."""
        return ''


class UserDeleteView(BaseDeleteView):
    """Delete a user."""
    model = User
    success_url = reverse_lazy('shared:users')
    feature_code = 'shared.users'
    required_action = 'delete_own'
    success_message = _('User deleted successfully.')
    
    def get_queryset(self) -> QuerySet:
        """Get users filtered by active company."""
        company_id = self.request.session.get('active_company_id')
        
        # Superusers can see all users
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        elif company_id:
            # Filter users who have access to the active company
            user_ids = UserCompanyAccess.objects.filter(
                company_id=company_id,
                is_enabled=1
            ).values_list('user_id', flat=True)
            
            queryset = User.objects.filter(id__in=user_ids)
        else:
            # No active company selected - return empty queryset
            queryset = User.objects.none()
        
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete User')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete user "{username}"?').format(username=self.object.username)
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': reverse('shared:users')},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_object_details(self) -> List[Dict[str, Any]]:
        """Return object details for display."""
        return [
            {'label': _('Username'), 'value': self.object.username},
            {'label': _('Email'), 'value': self.object.email or '-'},
            {'label': _('Name'), 'value': self.object.get_full_name() or '-'},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:users')


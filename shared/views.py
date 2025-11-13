"""
Views for shared module.
"""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import (
    AccessLevelForm,
    CompanyForm,
    CompanyUnitForm,
    GroupForm,
    PersonForm,
    UserCompanyAccessFormSet,
    UserCreateForm,
    UserUpdateForm,
)
from .models import AccessLevel, Company, CompanyUnit, Person, UserCompanyAccess
from .permissions import FEATURE_PERMISSION_MAP, PermissionAction

User = get_user_model()


@login_required
@require_POST
def set_active_company(request):
    """
    Set the active company for the current user session.
    
    Expects POST parameter 'company_id'.
    """
    company_id = request.POST.get('company_id')
    
    if company_id:
        try:
            company_id = int(company_id)
            
            # Verify user has access to this company
            from shared.models import UserCompanyAccess
            has_access = UserCompanyAccess.objects.filter(
                user=request.user,
                company_id=company_id,
                is_enabled=1
            ).exists()
            
            if has_access:
                request.session['active_company_id'] = company_id
        except (ValueError, TypeError):
            pass
    
    # Redirect back to the referring page or home
    return HttpResponseRedirect(request.POST.get('next', '/'))


class CompanyListView(LoginRequiredMixin, ListView):
    """
    List all companies that the current user has access to.
    """
    model = Company
    template_name = 'shared/companies.html'
    context_object_name = 'companies'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter companies based on user access."""
        # Get companies user has access to
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        
        return Company.objects.filter(
            id__in=user_company_ids,
            is_enabled=1
        ).order_by('public_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class PersonnelListView(LoginRequiredMixin, ListView):
    """
    List all personnel (Person objects) for the active company.
    """
    model = Person
    template_name = 'shared/personnel.html'
    context_object_name = 'personnel'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter personnel by active company."""
        active_company_id = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Person.objects.none()
        
        return Person.objects.filter(
            company_id=active_company_id,
            is_enabled=1
        ).select_related('company').prefetch_related('company_units').order_by('public_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class CompanyUnitListView(LoginRequiredMixin, ListView):
    """
    List all company units for the active company.
    """
    model = CompanyUnit
    template_name = 'shared/company_units.html'
    context_object_name = 'units'
    paginate_by = 50

    def get_queryset(self):
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return CompanyUnit.objects.none()

        queryset = CompanyUnit.objects.filter(
            company_id=active_company_id,
        ).select_related('parent_unit').order_by('public_code')

        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(public_code__icontains=search) |
                Q(name__icontains=search)
            )

        if status in ('0', '1'):
            queryset = queryset.filter(is_enabled=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['filters'] = {
            'search': self.request.GET.get('search', '').strip(),
            'status': self.request.GET.get('status', ''),
        }
        return context


class CompanyCreateView(LoginRequiredMixin, CreateView):
    """Create a new company."""
    model = Company
    form_class = CompanyForm
    template_name = 'shared/company_form.html'
    success_url = reverse_lazy('shared:companies')
    
    def form_valid(self, form):
        # Auto-set created_by
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create UserCompanyAccess for the creator
        UserCompanyAccess.objects.create(
            user=self.request.user,
            company=self.object,
            access_level_id=1,  # ADMIN level
            is_primary=1,  # Make it primary
            is_enabled=1
        )
        
        messages.success(self.request, _('Company created successfully.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Create Company')
        return context


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing company."""
    model = Company
    form_class = CompanyForm
    template_name = 'shared/company_form.html'
    success_url = reverse_lazy('shared:companies')
    
    def form_valid(self, form):
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Company updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Edit Company')
        return context


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a company."""
    model = Company
    success_url = reverse_lazy('shared:companies')
    template_name = 'shared/company_confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Company deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class PersonCreateView(LoginRequiredMixin, CreateView):
    """Create a new person."""
    model = Person
    form_class = PersonForm
    template_name = 'shared/person_form.html'
    success_url = reverse_lazy('shared:personnel')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        # Auto-set company and created_by
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Person created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Create Person')
        return context


class CompanyUnitCreateView(LoginRequiredMixin, CreateView):
    """Create a new company unit."""
    model = CompanyUnit
    form_class = CompanyUnitForm
    template_name = 'shared/company_unit_form.html'
    success_url = reverse_lazy('shared:company_units')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def form_valid(self, form):
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)

        form.instance.company_id = active_company_id
        messages.success(self.request, 'واحد سازمانی با موفقیت ایجاد شد.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = 'ایجاد واحد سازمانی'
        return context


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing person."""
    model = Person
    form_class = PersonForm
    template_name = 'shared/person_form.html'
    success_url = reverse_lazy('shared:personnel')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form):
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Person updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Edit Person')
        return context


class CompanyUnitUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing company unit."""
    model = CompanyUnit
    form_class = CompanyUnitForm
    template_name = 'shared/company_unit_form.html'
    success_url = reverse_lazy('shared:company_units')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'واحد سازمانی با موفقیت ویرایش شد.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = 'ویرایش واحد سازمانی'
        return context


class PersonDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a person."""
    model = Person
    success_url = reverse_lazy('shared:personnel')
    template_name = 'shared/person_confirm_delete.html'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Person deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class CompanyUnitDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a company unit."""
    model = CompanyUnit
    template_name = 'shared/company_unit_confirm_delete.html'
    success_url = reverse_lazy('shared:company_units')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'واحد سازمانی حذف شد.')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class UserAccessFormsetMixin:
    """Helper mixin to manage UserCompanyAccess formsets."""

    def get_access_formset(self, form=None):
        instance = None
        if form is not None:
            instance = form.instance
        elif hasattr(self, 'object'):
            instance = self.object
        if instance is None:
            instance = User()
        return UserCompanyAccessFormSet(
            self.request.POST if self.request.method == 'POST' else None,
            instance=instance,
        )


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'shared/users_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            User.objects.all()
            .order_by('username')
            .prefetch_related('groups', 'company_accesses__company', 'company_accesses__access_level')
        )
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        if status in {'active', 'inactive'}:
            queryset = queryset.filter(is_active=(status == 'active'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['search_term'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class UserCreateView(LoginRequiredMixin, UserAccessFormsetMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'shared/user_form.html'
    success_url = reverse_lazy('shared:users')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('access_formset', self.get_access_formset(context.get('form')))
        context['active_module'] = 'shared'
        context['page_title'] = _('Create User')
        context['is_create'] = True
        return context

    def form_valid(self, form):
        access_formset = self.get_access_formset(form)
        if not access_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, access_formset=access_formset))

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.save()
            form.save_m2m()
            access_formset.instance = self.object
            access_formset.save()
        messages.success(self.request, _('User created successfully.'))
        return HttpResponseRedirect(self.get_success_url())


class UserUpdateView(LoginRequiredMixin, UserAccessFormsetMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'shared/user_form.html'
    success_url = reverse_lazy('shared:users')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('access_formset', self.get_access_formset(context.get('form')))
        context['active_module'] = 'shared'
        context['page_title'] = _('Edit User')
        context['is_create'] = False
        return context

    def form_valid(self, form):
        access_formset = self.get_access_formset(form)
        if not access_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, access_formset=access_formset))

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.save()
            form.save_m2m()
            access_formset.instance = self.object
            access_formset.save()
        messages.success(self.request, _('User updated successfully.'))
        return HttpResponseRedirect(self.get_success_url())


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'shared/user_confirm_delete.html'
    success_url = reverse_lazy('shared:users')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('User deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'shared/groups_list.html'
    context_object_name = 'groups'
    paginate_by = 20

    def get_queryset(self):
        search = self.request.GET.get('search')
        queryset = Group.objects.all().order_by('name').prefetch_related('user_set', 'profile__access_levels')
        if search:
            queryset = queryset.filter(name__icontains=search)
        status = self.request.GET.get('status')
        if status in {'active', 'inactive'}:
            desired = 1 if status == 'active' else 0
            queryset = queryset.filter(profile__is_enabled=desired)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['search_term'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'shared/group_form.html'
    success_url = reverse_lazy('shared:groups')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['page_title'] = _('Create Group')
        context['is_create'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Group created successfully.'))
        return response


class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'shared/group_form.html'
    success_url = reverse_lazy('shared:groups')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['page_title'] = _('Edit Group')
        context['is_create'] = False
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Group updated successfully.'))
        return response


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'shared/group_confirm_delete.html'
    success_url = reverse_lazy('shared:groups')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Group deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class AccessLevelPermissionMixin:
    template_name = 'shared/access_level_form.html'

    action_labels = {
        PermissionAction.VIEW_OWN.value: _('View own records'),
        PermissionAction.VIEW_ALL.value: _('View all records'),
        PermissionAction.CREATE.value: _('Create'),
        PermissionAction.EDIT_OWN.value: _('Edit own records'),
        PermissionAction.DELETE_OWN.value: _('Delete own records'),
        PermissionAction.LOCK_OWN.value: _('Lock own documents'),
        PermissionAction.LOCK_OTHER.value: _('Lock others documents'),
        PermissionAction.UNLOCK_OWN.value: _('Unlock own documents'),
        PermissionAction.UNLOCK_OTHER.value: _('Unlock others documents'),
        PermissionAction.APPROVE.value: _('Approve'),
        PermissionAction.REJECT.value: _('Reject'),
        PermissionAction.CANCEL.value: _('Cancel'),
    }

    def _feature_key(self, code: str) -> str:
        return code.replace('.', '__')

    def _prepare_feature_context(self, instance=None):
        existing = {}
        if instance and instance.pk:
            for perm in instance.permissions.all():
                meta_actions = {}
                if isinstance(perm.metadata, dict):
                    meta_actions = perm.metadata.get('actions', {})
                existing[perm.resource_code] = {
                    'view_scope': meta_actions.get(
                        'view_scope',
                        'all' if meta_actions.get(PermissionAction.VIEW_ALL.value) else (
                            'own' if meta_actions.get(PermissionAction.VIEW_OWN.value) else ('all' if perm.can_view else 'none')
                        ),
                    ),
                    'checked': {
                        action: bool(meta_actions.get(action)) for action in meta_actions
                    },
                    'fallback_can_create': bool(perm.can_create),
                    'fallback_can_edit': bool(perm.can_edit),
                    'fallback_can_delete': bool(perm.can_delete),
                    'fallback_can_approve': bool(perm.can_approve),
                }
        features = []
        for feature in FEATURE_PERMISSION_MAP.values():
            code = feature.code
            key = self._feature_key(code)
            feature_state = existing.get(code, {})
            view_scope = feature_state.get('view_scope', 'none')
            checked_actions = feature_state.get('checked', {})
            data_actions = []
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                checked = checked_actions.get(action.value, False)
                if not feature_state and action == PermissionAction.CREATE:
                    checked = feature_state.get('fallback_can_create', False)
                if not feature_state and action == PermissionAction.EDIT_OWN:
                    checked = feature_state.get('fallback_can_edit', False)
                if not feature_state and action == PermissionAction.DELETE_OWN:
                    checked = feature_state.get('fallback_can_delete', False)
                if not feature_state and action == PermissionAction.APPROVE:
                    checked = feature_state.get('fallback_can_approve', False)
                data_actions.append(
                    {
                        'code': action.value,
                        'label': self.action_labels[action.value],
                        'checked': checked,
                    }
                )
            features.append(
                {
                    'code': code,
                    'html_id': key,
                    'label': feature.label,
                    'view_supported': PermissionAction.VIEW_OWN in feature.actions or PermissionAction.VIEW_ALL in feature.actions,
                    'view_scope': view_scope,
                    'actions': data_actions,
                }
            )
        return features

    def _save_permissions(self, form):
        active_codes = set()
        for feature in FEATURE_PERMISSION_MAP.values():
            code = feature.code
            html_key = self._feature_key(code)
            view_scope = self.request.POST.get(f'perm-{html_key}-view', 'none')
            selected_actions = []
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                if self.request.POST.get(f'perm-{html_key}-{action.value}') == 'on':
                    selected_actions.append(action)

            if view_scope == 'none' and not selected_actions:
                # Remove existing permission if it exists
                self.object.permissions.filter(resource_code=code).delete()
                continue

            perm, _created = self.object.permissions.get_or_create(
                resource_code=code,
                defaults={
                    'module_code': code.split('.')[0],
                    'resource_type': 'menu',
                },
            )
            perm.module_code = code.split('.')[0]
            perm.resource_type = 'menu'
            perm.can_view = 1 if view_scope != 'none' else 0
            perm.can_create = 1 if PermissionAction.CREATE in selected_actions else 0
            perm.can_edit = 1 if PermissionAction.EDIT_OWN in selected_actions else 0
            perm.can_delete = 1 if PermissionAction.DELETE_OWN in selected_actions else 0
            perm.can_approve = 1 if PermissionAction.APPROVE in selected_actions else 0

            metadata_actions = {
                'view_scope': view_scope,
                PermissionAction.VIEW_OWN.value: view_scope in {'own', 'all'},
                PermissionAction.VIEW_ALL.value: view_scope == 'all',
            }
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                metadata_actions[action.value] = action in selected_actions
            perm.metadata = {'actions': metadata_actions}
            perm.save()
            active_codes.add(code)

        # Remove stale permissions not present anymore
        self.object.permissions.exclude(resource_code__in=active_codes).delete()


class AccessLevelListView(LoginRequiredMixin, ListView):
    model = AccessLevel
    template_name = 'shared/access_levels_list.html'
    context_object_name = 'access_levels'
    paginate_by = 20

    def get_queryset(self):
        queryset = AccessLevel.objects.all().order_by('code').prefetch_related('permissions')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        if search:
            queryset = queryset.filter(Q(code__icontains=search) | Q(name__icontains=search))
        if status in {'active', 'inactive'}:
            queryset = queryset.filter(is_enabled=1 if status == 'active' else 0)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['search_term'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class AccessLevelCreateView(LoginRequiredMixin, AccessLevelPermissionMixin, CreateView):
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'shared/access_level_form.html'
    success_url = reverse_lazy('shared:access_levels')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['page_title'] = _('Create Access Level')
        context['is_create'] = True
        context['feature_permissions'] = self._prepare_feature_context()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.refresh_from_db()
        self._save_permissions(form)
        messages.success(self.request, _('Access level created successfully.'))
        return response


class AccessLevelUpdateView(LoginRequiredMixin, AccessLevelPermissionMixin, UpdateView):
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'shared/access_level_form.html'
    success_url = reverse_lazy('shared:access_levels')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['page_title'] = _('Edit Access Level')
        context['is_create'] = False
        context['feature_permissions'] = self._prepare_feature_context(self.object)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self._save_permissions(form)
        messages.success(self.request, _('Access level updated successfully.'))
        return response


class AccessLevelDeleteView(LoginRequiredMixin, DeleteView):
    model = AccessLevel
    template_name = 'shared/access_level_confirm_delete.html'
    success_url = reverse_lazy('shared:access_levels')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Access level deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context

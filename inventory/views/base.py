"""
Base views and mixins for inventory module.

This module contains reusable base classes and mixins that are used across
all inventory views.
"""
from typing import Optional, Dict, Any
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation
from shared.mixins import FeaturePermissionRequiredMixin
from .. import models
from .. import forms
from ..services import serials as serial_service
import logging

logger = logging.getLogger('inventory.views.base')


class InventoryBaseView(LoginRequiredMixin):
    """Base view with common context for inventory module."""
    login_url = '/admin/login/'
    
    def get_queryset(self):
        """Filter queryset by active company."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id and (hasattr(queryset.model, 'company') or hasattr(queryset.model, 'company_id')):
            queryset = queryset.filter(company_id=company_id)
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add common context data."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'inventory'
        return context
    
    def add_delete_permissions_to_context(self, context: Dict[str, Any], feature_code: str, resource_owner=None) -> Dict[str, Any]:
        """Helper method to add delete permission checks to context."""
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission, are_users_in_same_primary_group
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Superuser can always delete
        is_superuser = self.request.user.is_superuser
        
        # Check permissions
        can_delete_own = is_superuser or has_feature_permission(
            permissions, feature_code, 'delete_own', allow_own_scope=True,
            current_user=self.request.user, resource_owner=resource_owner
        )
        can_delete_other = is_superuser or has_feature_permission(
            permissions, feature_code, 'delete_other', allow_own_scope=False,
            current_user=self.request.user, resource_owner=resource_owner
        )
        can_delete_same_group = is_superuser or (
            has_feature_permission(
                permissions, feature_code, 'delete_same_group', allow_own_scope=False,
                current_user=self.request.user, resource_owner=resource_owner
            ) if resource_owner else False
        )
        
        context['can_delete_own'] = can_delete_own
        context['can_delete_other'] = can_delete_other
        context['can_delete_same_group'] = can_delete_same_group
        context['user'] = self.request.user  # Make user available in template
        return context
    
    def add_view_edit_permissions_to_context(self, context: Dict[str, Any], feature_code: str) -> Dict[str, Any]:
        """
        Helper method to add view and edit permission checks to context.
        This is used in ListView to determine which buttons to show for each object.
        
        Args:
            context: The context dictionary to update
            feature_code: Feature code for permission checking (e.g., 'inventory.receipts.temporary')
        
        Returns:
            Updated context dictionary with permission flags
        """
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Superuser can always view and edit
        is_superuser = self.request.user.is_superuser
        
        # Check view permissions
        can_view_own = is_superuser or has_feature_permission(
            permissions, feature_code, 'view_own', allow_own_scope=True,
            current_user=self.request.user, resource_owner=None
        )
        can_view_all = is_superuser or has_feature_permission(
            permissions, feature_code, 'view_all', allow_own_scope=False,
            current_user=self.request.user, resource_owner=None
        )
        can_view_same_group = is_superuser or has_feature_permission(
            permissions, feature_code, 'view_same_group', allow_own_scope=False,
            current_user=self.request.user, resource_owner=None
        )
        
        # Check edit permissions
        can_edit_own = is_superuser or has_feature_permission(
            permissions, feature_code, 'edit_own', allow_own_scope=True,
            current_user=self.request.user, resource_owner=None
        )
        can_edit_other = is_superuser or has_feature_permission(
            permissions, feature_code, 'edit_other', allow_own_scope=False,
            current_user=self.request.user, resource_owner=None
        )
        can_edit_same_group = is_superuser or has_feature_permission(
            permissions, feature_code, 'edit_same_group', allow_own_scope=False,
            current_user=self.request.user, resource_owner=None
        )
        
        # Add to context
        context['can_view_own'] = can_view_own
        context['can_view_all'] = can_view_all
        context['can_view_same_group'] = can_view_same_group
        context['can_edit_own'] = can_edit_own
        context['can_edit_other'] = can_edit_other
        context['can_edit_same_group'] = can_edit_same_group
        context['feature_code'] = feature_code  # Store feature code for per-object checks
        context['user'] = self.request.user  # Make user available in template
        
        return context
    
    def can_view_object(self, obj, feature_code: str) -> bool:
        """
        Check if current user can view a specific object.
        
        Args:
            obj: The object to check
            feature_code: Feature code for permission checking
        
        Returns:
            True if user can view the object, False otherwise
        """
        if self.request.user.is_superuser:
            return True
        
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission, are_users_in_same_primary_group
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Get resource owner
        resource_owner = None
        if hasattr(obj, 'created_by'):
            resource_owner = obj.created_by
        elif hasattr(obj, 'owner'):
            resource_owner = obj.owner
        elif hasattr(obj, 'user'):
            resource_owner = obj.user
        
        # Check view permissions
        can_view_all = has_feature_permission(
            permissions, feature_code, 'view_all', allow_own_scope=False,
            current_user=self.request.user, resource_owner=resource_owner
        )
        if can_view_all:
            return True
        
        # Check if user is owner
        is_owner = resource_owner == self.request.user if resource_owner else False
        if is_owner:
            can_view_own = has_feature_permission(
                permissions, feature_code, 'view_own', allow_own_scope=True,
                current_user=self.request.user, resource_owner=resource_owner
            )
            if can_view_own:
                return True
        
        # Check same group permission
        if resource_owner:
            can_view_same_group = has_feature_permission(
                permissions, feature_code, 'view_same_group', allow_own_scope=False,
                current_user=self.request.user, resource_owner=resource_owner
            )
            if can_view_same_group and are_users_in_same_primary_group(self.request.user, resource_owner):
                return True
        
        return False
    
    def can_edit_object(self, obj, feature_code: str) -> bool:
        """
        Check if current user can edit a specific object.
        Also checks if object is locked.
        
        Args:
            obj: The object to check
            feature_code: Feature code for permission checking
        
        Returns:
            True if user can edit the object and it's not locked, False otherwise
        """
        # Check if object is locked
        if getattr(obj, 'is_locked', 0):
            return False
        
        if self.request.user.is_superuser:
            return True
        
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission, are_users_in_same_primary_group
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Get resource owner
        resource_owner = None
        if hasattr(obj, 'created_by'):
            resource_owner = obj.created_by
        elif hasattr(obj, 'owner'):
            resource_owner = obj.owner
        elif hasattr(obj, 'user'):
            resource_owner = obj.user
        
        # Check edit permissions
        can_edit_other = has_feature_permission(
            permissions, feature_code, 'edit_other', allow_own_scope=False,
            current_user=self.request.user, resource_owner=resource_owner
        )
        if can_edit_other:
            return True
        
        # Check if user is owner
        is_owner = resource_owner == self.request.user if resource_owner else False
        if is_owner:
            can_edit_own = has_feature_permission(
                permissions, feature_code, 'edit_own', allow_own_scope=True,
                current_user=self.request.user, resource_owner=resource_owner
            )
            if can_edit_own:
                return True
        
        # Check same group permission
        if resource_owner:
            can_edit_same_group = has_feature_permission(
                permissions, feature_code, 'edit_same_group', allow_own_scope=False,
                current_user=self.request.user, resource_owner=resource_owner
            )
            if can_edit_same_group and are_users_in_same_primary_group(self.request.user, resource_owner):
                return True
        
        return False
    
    def filter_queryset_by_permissions(self, queryset, feature_code: str, owner_field: str = 'created_by'):
        """
        Filter queryset based on user permissions.
        
        Args:
            queryset: The queryset to filter
            feature_code: Feature code for permission checking (e.g., 'inventory.receipts.temporary')
            owner_field: Field name that contains the owner/creator (default: 'created_by')
        
        Returns:
            Filtered queryset
        """
        # Superuser can see all records
        if self.request.user.is_superuser:
            return queryset
        
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission, are_users_in_same_primary_group
        from django.db.models import Q
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Check view scope
        can_view_all = has_feature_permission(permissions, feature_code, 'view_all', allow_own_scope=False)
        can_view_own = has_feature_permission(permissions, feature_code, 'view_own', allow_own_scope=True)
        can_view_same_group = has_feature_permission(permissions, feature_code, 'view_same_group', allow_own_scope=False)
        
        # If user can view all, return queryset as is
        if can_view_all:
            return queryset
        
        # Build filter conditions
        filter_conditions = Q()
        
        # If user can view own records, add own records to filter
        if can_view_own:
            if hasattr(queryset.model, owner_field):
                filter_conditions |= Q(**{owner_field: self.request.user})
        
        # If user can view same group records, add same group records to filter
        if can_view_same_group:
            if hasattr(queryset.model, owner_field):
                # Get current user's primary groups
                current_user_primary_groups = set(self.request.user.primary_groups.all().values_list('id', flat=True))
                
                if current_user_primary_groups:
                    # Get users who share at least one primary group with current user
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    same_group_users = User.objects.filter(
                        primary_groups__id__in=current_user_primary_groups
                    ).distinct()
                    
                    # Add same group records to filter
                    filter_conditions |= Q(**{f'{owner_field}__in': same_group_users})
        
        # If no permissions, return empty queryset
        if not filter_conditions:
            return queryset.none()
        
        # Apply filter
        return queryset.filter(filter_conditions).distinct()


class DocumentLockProtectedMixin:
    """Prevent modifying locked inventory documents."""

    lock_redirect_url_name: str = ''
    lock_error_message = _('سند قفل شده و قابل ویرایش یا حذف نیست.')
    owner_field: str = 'created_by'
    owner_error_message = _('فقط ایجاد کننده می‌تواند این سند را ویرایش کند.')
    # Only protect modification methods, not GET (viewing)
    protected_methods = ('post', 'put', 'patch', 'delete')

    def dispatch(self, request, *args, **kwargs):
        # Only block modification methods (POST, PUT, PATCH, DELETE), not GET
        if request.method.lower() in self.protected_methods:
            obj = self.get_object()
            self.object = obj
            if getattr(obj, 'is_locked', 0):
                messages.error(request, self.lock_error_message)
                return HttpResponseRedirect(self._get_lock_redirect_url())
            if self.owner_field:
                owner = getattr(obj, self.owner_field, None)
                owner_id = getattr(owner, 'id', None) if owner else None
                if owner_id and owner_id != request.user.id:
                    # Check if user has permission to edit same group or other
                    from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
                    company_id = request.session.get('active_company_id')
                    permissions = get_user_feature_permissions(request.user, company_id)
                    
                    # Get feature code from view
                    feature_code = getattr(self, 'feature_code', None)
                    if feature_code:
                        can_edit_same_group = has_feature_permission(
                            permissions, feature_code, 'edit_same_group', allow_own_scope=False,
                            current_user=request.user, resource_owner=owner
                        )
                        can_edit_other = has_feature_permission(
                            permissions, feature_code, 'edit_other', allow_own_scope=False,
                            current_user=request.user, resource_owner=owner
                        )
                        
                        if not can_edit_same_group and not can_edit_other:
                            messages.error(request, self.owner_error_message)
                            return HttpResponseRedirect(self._get_lock_redirect_url())
                    else:
                        # If no feature_code, use default behavior
                        messages.error(request, self.owner_error_message)
                        return HttpResponseRedirect(self._get_lock_redirect_url())
        return super().dispatch(request, *args, **kwargs)

    def _get_lock_redirect_url(self) -> str:
        """Get redirect URL when document is locked."""
        if self.lock_redirect_url_name:
            return reverse(self.lock_redirect_url_name)
        if hasattr(self, 'list_url_name') and getattr(self, 'list_url_name'):
            return reverse(self.list_url_name)
        return reverse('inventory:inventory_balance')


class DocumentLockView(LoginRequiredMixin, View):
    """Generic view to lock inventory documents."""

    model = None
    success_url_name: str = ''
    success_message = _('سند با موفقیت قفل شد و دیگر قابل ویرایش نیست.')
    already_locked_message = _('این سند قبلاً قفل شده است.')
    lock_field: str = 'is_locked'

    def after_lock(self, obj, request) -> None:
        """Hook for subclasses to perform extra actions after locking."""
        return None

    def before_lock(self, obj, request) -> bool:
        """Hook executed before locking. Return False to cancel lock."""
        return True

    def post(self, request, *args, **kwargs):
        if self.model is None or not self.success_url_name:
            messages.error(request, _('پیکربندی قفل سند نامعتبر است.'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        queryset = self.model.objects.all()
        company_id = request.session.get('active_company_id')
        if company_id and hasattr(self.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)

        obj = get_object_or_404(queryset, pk=kwargs.get('pk'))

        if getattr(obj, self.lock_field, 0):
            messages.info(request, self.already_locked_message)
        else:
            if not self.before_lock(obj, request):
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse(self.success_url_name)))

            update_fields = {self.lock_field}
            setattr(obj, self.lock_field, 1)
            if hasattr(obj, 'locked_at'):
                obj.locked_at = timezone.now()
                update_fields.add('locked_at')
            if hasattr(obj, 'locked_by_id'):
                obj.locked_by = request.user
                update_fields.add('locked_by')
            if hasattr(obj, 'edited_by_id'):
                obj.edited_by = request.user
                update_fields.add('edited_by')
            obj.save(update_fields=list(update_fields))
            self.after_lock(obj, request)
            messages.success(request, self.success_message)

        return HttpResponseRedirect(reverse(self.success_url_name))


class DocumentUnlockView(LoginRequiredMixin, View):
    """Generic view to unlock inventory documents."""

    model = None
    success_url_name: str = ''
    success_message = _('سند با موفقیت از قفل خارج شد و قابل ویرایش است.')
    already_unlocked_message = _('این سند قبلاً از قفل خارج شده است.')
    lock_field: str = 'is_locked'
    feature_code: str = ''
    required_action: str = 'unlock_own'

    def after_unlock(self, obj, request) -> None:
        """Hook for subclasses to perform extra actions after unlocking."""
        return None

    def before_unlock(self, obj, request) -> bool:
        """Hook executed before unlocking. Return False to cancel unlock."""
        return True

    def dispatch(self, request, *args, **kwargs):
        """Check permissions before allowing unlock."""
        # Superuser bypass
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        if not self.feature_code:
            messages.error(request, _('پیکربندی باز کردن قفل سند نامعتبر است.'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
        obj = get_object_or_404(
            self.model,
            pk=kwargs.get('pk'),
            company_id=request.session.get('active_company_id')
        )
        
        # Check permissions
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        from django.core.exceptions import PermissionDenied
        
        company_id = request.session.get('active_company_id')
        permissions = get_user_feature_permissions(request.user, company_id)
        
        # Check if user is owner and has UNLOCK_OWN permission
        is_owner = obj.created_by == request.user if obj.created_by else False
        can_unlock_own = has_feature_permission(permissions, self.feature_code, 'unlock_own', allow_own_scope=True)
        can_unlock_other = has_feature_permission(permissions, self.feature_code, 'unlock_other', allow_own_scope=False)
        
        if is_owner and not can_unlock_own:
            raise PermissionDenied(_('شما اجازه باز کردن قفل اسناد خود را ندارید.'))
        elif not is_owner and not can_unlock_other:
            raise PermissionDenied(_('شما اجازه باز کردن قفل اسناد سایر کاربران را ندارید.'))
        
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.model is None or not self.success_url_name:
            messages.error(request, _('پیکربندی باز کردن قفل سند نامعتبر است.'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        queryset = self.model.objects.all()
        company_id = request.session.get('active_company_id')
        if company_id and hasattr(self.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)

        obj = get_object_or_404(queryset, pk=kwargs.get('pk'))

        if not getattr(obj, self.lock_field, 0):
            messages.info(request, self.already_unlocked_message)
        else:
            if not self.before_unlock(obj, request):
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse(self.success_url_name)))

            update_fields = {self.lock_field}
            setattr(obj, self.lock_field, 0)
            if hasattr(obj, 'locked_at'):
                obj.locked_at = None
                update_fields.add('locked_at')
            if hasattr(obj, 'locked_by_id'):
                obj.locked_by = None
                update_fields.add('locked_by')
            if hasattr(obj, 'edited_by_id'):
                obj.edited_by = request.user
                update_fields.add('edited_by')
            obj.save(update_fields=list(update_fields))
            self.after_unlock(obj, request)
            messages.success(request, self.success_message)

        return HttpResponseRedirect(reverse(self.success_url_name))


class LineFormsetMixin:
    """Mixin to handle line formset creation and saving for multi-line documents."""
    
    formset_class = None
    formset_prefix: str = 'lines'
    
    def build_line_formset(self, data=None, instance=None, company_id: Optional[int] = None, request=None, initial=None):
        """Build line formset for the document."""
        logger.info("=" * 80)
        logger.info("LineFormsetMixin.build_line_formset() called")
        logger.info(f"data is None: {data is None}")
        logger.info(f"instance: {instance}")
        logger.info(f"company_id: {company_id}")
        logger.info(f"initial: {initial}")
        if instance is None:
            instance = getattr(self, "object", None)
            logger.info(f"Instance from self.object: {instance}")
        if company_id is None:
            if instance and instance.company_id:
                company_id = instance.company_id
            else:
                company_id = self.request.session.get('active_company_id')
        logger.info(f"Final company_id: {company_id}")
        if request is None:
            request = getattr(self, 'request', None)
        
        if self.formset_class is None:
            raise ValueError("formset_class must be set in view class")
        
        logger.info(f"Formset class: {self.formset_class}")
        logger.info(f"Formset prefix: {self.formset_prefix}")
        
        kwargs: Dict[str, Any] = {
            'instance': instance,
            'prefix': self.formset_prefix,
            'company_id': company_id,
            'request': request,
        }
        if data is not None:
            kwargs['data'] = data
            logger.info(f"Data provided, keys: {list(data.keys())[:10]}...")
        if initial is not None:
            kwargs['initial'] = initial
            logger.info(f"Initial data provided: {initial}")
        logger.info(f"Formset kwargs: instance={instance}, prefix={self.formset_prefix}, company_id={company_id}")
        formset = self.formset_class(**kwargs)
        logger.info(f"Formset created, forms count: {len(formset.forms)}")
        for i, form in enumerate(formset.forms):
            if form.instance.pk:
                logger.info(f"  Form {i}: instance pk={form.instance.pk}, item_id={getattr(form.instance, 'item_id', None)}, item={form.instance.item if hasattr(form.instance, 'item') and form.instance.item else 'None'}")
        return formset
    
    def get_line_formset(self, data=None):
        """Get line formset for current request."""
        return self.build_line_formset(data=data)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add line formset to context."""
        logger.info("=" * 80)
        logger.info("LineFormsetMixin.get_context_data() called")
        logger.info(f"Request method: {self.request.method}")
        context = super().get_context_data(**kwargs)
        logger.info(f"Context keys before formset: {list(context.keys())}")
        if 'lines_formset' not in context:
            if self.request.method == 'POST':
                logger.info("Building formset with POST data")
                context['lines_formset'] = self.get_line_formset(data=self.request.POST)
            else:
                logger.info("Building formset without data (GET request)")
                context['lines_formset'] = self.get_line_formset()
            logger.info(f"Formset added to context, forms count: {len(context['lines_formset'].forms)}")
        else:
            logger.info("Formset already in context")
        return context
    
    def form_invalid(self, form):
        """Handle invalid form with formset."""
        company_id = getattr(form.instance, "company_id", None) or self.request.session.get('active_company_id')
        return self.render_to_response(
            self.get_context_data(
                form=form,
                lines_formset=self.build_line_formset(
                    data=self.request.POST, 
                    instance=form.instance, 
                    company_id=company_id,
                    request=self.request
                ),
            )
        )
    
    def _save_line_formset(self, formset) -> None:
        """Save line formset instances."""
        # Process each form in the formset manually to ensure all valid forms are saved
        for form in formset.forms:
            # Check if form has cleaned_data - only if form is bound and validated
            # Note: cleaned_data only exists after form.is_valid() is called
            if not hasattr(form, 'cleaned_data') or not form.cleaned_data:
                continue
            
            # Check if form should be deleted
            if form.cleaned_data.get('DELETE', False):
                if form.instance.pk:
                    form.instance.delete()
                continue
            
            # Check if form has an item (required for saving)
            item = form.cleaned_data.get('item')
            if not item:
                # Skip empty forms
                continue
            
            # Check if form has errors - if it does, skip it
            # This is important because validation errors mean the form shouldn't be saved
            if form.errors:
                continue
            
            # Save the instance
            instance = form.save(commit=False)
            instance.company = self.object.company
            instance.document = self.object
            if not hasattr(instance, 'company_id') or not instance.company_id:
                instance.company_id = self.object.company_id
            instance.save()
            form.save_m2m()  # Save ManyToMany relationships (serials)
            
            # Handle selected serials from hidden input (for new issue lines)
            if hasattr(instance, 'serials'):
                # Get selected serials from POST data
                prefix = form.prefix
                selected_serials_key = f'{prefix}-selected_serials'
                selected_serials_str = self.request.POST.get(selected_serials_key, '')
                
                if selected_serials_str:
                    try:
                        # Parse comma-separated serial IDs
                        serial_ids = [int(id.strip()) for id in selected_serials_str.split(',') if id.strip()]
                        
                        if serial_ids:
                            # Get available serials for this item and warehouse
                            if instance.item and instance.item.has_lot_tracking == 1:
                                # Filter serials: must be same company, same item, same warehouse, and available/reserved
                                available_serials = models.ItemSerial.objects.filter(
                                    company_id=instance.company_id,
                                    item=instance.item,
                                    current_warehouse=instance.warehouse,
                                    current_status__in=[
                                        models.ItemSerial.Status.AVAILABLE, 
                                        models.ItemSerial.Status.RESERVED
                                    ],
                                    pk__in=serial_ids
                                )
                                
                                # Assign serials to this line
                                instance.serials.set(available_serials)
                                
                                # Reserve serials for this line
                                if available_serials.exists():
                                    serial_service.sync_issue_line_serials(
                                        instance,
                                        [],  # No previous serials for new lines
                                        user=self.request.user
                                    )
                    except (ValueError, TypeError):
                        # Ignore invalid serial IDs
                        pass


class ItemUnitFormsetMixin:
    """Mixin to handle item unit formset creation and saving."""

    formset_prefix: str = 'units'

    def build_unit_formset(self, data=None, instance=None, company_id: Optional[int] = None):
        """Build unit formset for item."""
        if instance is None:
            instance = getattr(self, "object", None) or models.Item()
        if company_id is None:
            if instance and instance.company_id:
                company_id = instance.company_id
            else:
                company_id = self.request.session.get('active_company_id')

        kwargs: Dict[str, Any] = {
            'instance': instance,
            'prefix': self.formset_prefix,
            'company_id': company_id,
        }
        if data is not None:
            kwargs['data'] = data
        return forms.ItemUnitFormSet(**kwargs)

    def get_unit_formset(self, data=None):
        """Get unit formset for current request."""
        return self.build_unit_formset(data=data)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add unit formset to context."""
        context = super().get_context_data(**kwargs)
        if 'units_formset' not in context:
            if self.request.method == 'POST':
                context['units_formset'] = self.get_unit_formset(data=self.request.POST)
            else:
                context['units_formset'] = self.get_unit_formset()
        # Add empty form for JavaScript to clone
        if 'units_formset' in context:
            context['units_formset_empty'] = context['units_formset'].empty_form
        return context

    def form_invalid(self, form):
        """Handle invalid form with unit formset."""
        company_id = getattr(form.instance, "company_id", None) or self.request.session.get('active_company_id')
        context = self.get_context_data(
            form=form,
            units_formset=self.build_unit_formset(
                data=self.request.POST, 
                instance=form.instance, 
                company_id=company_id
            ),
        )
        # Add empty form for JavaScript
        if 'units_formset' in context:
            context['units_formset_empty'] = context['units_formset'].empty_form
        return self.render_to_response(context)

    def _generate_unit_code(self, company) -> str:
        """Generate sequential unit code."""
        last_code = (
            models.ItemUnit.objects.filter(company=company)
            .order_by("-public_code")
            .values_list("public_code", flat=True)
            .first()
        )
        if last_code and last_code.isdigit():
            return str(int(last_code) + 1).zfill(6)
        return "000001"

    def _save_unit_formset(self, formset) -> None:
        """Save unit formset instances."""
        instances = formset.save(commit=False)
        for unit in instances:
            if not unit.from_unit or not unit.to_unit:
                continue
            unit.company = self.object.company
            unit.item = self.object
            unit.item_code = self.object.item_code
            if not unit.public_code:
                unit.public_code = self._generate_unit_code(self.object.company)
            unit.save()
        for obj in formset.deleted_objects:
            obj.delete()

    def _sync_item_warehouses(self, item, warehouses, user) -> None:
        """Sync item-warehouse relationships."""
        warehouses = list(warehouses or [])
        selected_ids = {w.id for w in warehouses}
        existing = {iw.warehouse_id: iw for iw in item.warehouses.all()}

        # Delete removed warehouses
        if selected_ids:
            item.warehouses.exclude(warehouse_id__in=selected_ids).delete()
        else:
            item.warehouses.all().delete()

        for idx, warehouse in enumerate(warehouses):
            is_primary = 1 if idx == 0 else 0
            current = existing.get(warehouse.id)
            if current:
                updated = False
                if current.is_primary != is_primary:
                    current.is_primary = is_primary
                    updated = True
                if updated:
                    current.save()
            else:
                item.warehouses.create(
                    company=item.company,
                    warehouse=warehouse,
                    is_primary=is_primary,
                )

    def _get_ordered_warehouses(self, form):
        """Get warehouses in the order they were selected."""
        selected = list(form.cleaned_data.get('allowed_warehouses') or [])
        if not selected:
            return selected
        order_keys = [key for key in self.request.POST.getlist('allowed_warehouses') if key]
        if not order_keys:
            return selected
        mapping = {str(w.id): w for w in selected}
        ordered = []
        for key in order_keys:
            warehouse = mapping.get(key)
            if warehouse and warehouse not in ordered:
                ordered.append(warehouse)
        for warehouse in selected:
            if warehouse not in ordered:
                ordered.append(warehouse)
        return ordered


class BaseCreateDocumentFromRequestView(FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView):
    """
    Base view for creating documents (receipts/issues) from requests (purchase/warehouse).
    
    This base class handles the common flow of:
    1. Getting the request object (PurchaseRequest or WarehouseRequest)
    2. Displaying a selection form (for multi-line requests) or quantity form (for single-line requests)
    3. Processing the form submission and storing data in session
    4. Redirecting to the document creation view
    
    Subclasses should define:
    - `document_type`: 'receipt' or 'issue'
    - `document_subtype`: 'temporary', 'permanent', 'consignment', 'consumption'
    - `request_model`: The request model class (PurchaseRequest or WarehouseRequest)
    - `is_multi_line`: True for PurchaseRequest (has lines), False for WarehouseRequest (single line)
    - `template_name`: Template to render
    - `feature_code`: Feature code for permissions
    - `required_action`: Required action for permissions
    
    Hook methods:
    - `get_request_object(pk)`: Get and validate the request object
    - `get_request_status_filter()`: Get the status filter for the request (e.g., 'approved')
    - `get_context_data(**kwargs)`: Add context data (can override)
    - `process_multi_line_post(request, request_obj)`: Process POST for multi-line requests
    - `process_single_line_post(request, request_obj)`: Process POST for single-line requests
    - `get_redirect_url(request_obj)`: Get the redirect URL after processing
    - `get_session_key(request_obj)`: Get the session key for storing data
    - `get_type_name()`: Get the display name for the document type
    """
    
    document_type = None  # 'receipt' or 'issue'
    document_subtype = None  # 'temporary', 'permanent', 'consignment', 'consumption'
    request_model = None  # PurchaseRequest or WarehouseRequest
    is_multi_line = None  # True for PurchaseRequest, False for WarehouseRequest
    template_name = None
    required_action = None
    
    def get_company_id(self):
        """Get active company ID from session."""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            raise Http404(_('شرکت فعال مشخص نشده است.'))
        return company_id
    
    def get_request_status_filter(self):
        """Get the status filter for the request. Override in subclasses."""
        return 'approved'
    
    def get_request_object(self, pk: int):
        """Get request object and check permissions. Override for custom logic."""
        company_id = self.get_company_id()
        status_filter = self.get_request_status_filter()
        
        filter_kwargs = {
            'pk': pk,
            'company_id': company_id,
            'is_enabled': 1
        }
        
        if status_filter:
            if hasattr(self.request_model, 'Status'):
                # For PurchaseRequest with Status enum
                filter_kwargs['status'] = getattr(self.request_model.Status, status_filter.upper())
            else:
                # For WarehouseRequest with string status
                filter_kwargs['request_status'] = status_filter
        
        return get_object_or_404(self.request_model, **filter_kwargs)
    
    def get_type_name(self):
        """Get display name for document type. Override in subclasses."""
        type_names = {
            'receipt': {
                'temporary': _('رسید موقت'),
                'permanent': _('رسید دائم'),
                'consignment': _('رسید امانی'),
            },
            'issue': {
                'permanent': _('حواله دائم'),
                'consumption': _('حواله مصرف'),
                'consignment': _('حواله امانی'),
            },
        }
        return type_names.get(self.document_type, {}).get(self.document_subtype, '')
    
    def get_session_key(self, request_obj):
        """Get session key for storing data. Override in subclasses."""
        if self.document_type == 'receipt':
            return f'purchase_request_{request_obj.pk}_receipt_{self.document_subtype}_lines'
        elif self.document_type == 'issue':
            return f'warehouse_request_{request_obj.pk}_issue_{self.document_subtype}_data'
        return None
    
    def get_redirect_url(self, request_obj):
        """Get redirect URL after processing. Override in subclasses."""
        if self.document_type == 'receipt':
            url_names = {
                'temporary': 'inventory:receipt_temporary_create_from_request',
                'permanent': 'inventory:receipt_permanent_create_from_request',
                'consignment': 'inventory:receipt_consignment_create_from_request',
            }
        elif self.document_type == 'issue':
            url_names = {
                'permanent': 'inventory:issue_permanent_create_from_warehouse_request',
                'consumption': 'inventory:issue_consumption_create_from_warehouse_request',
                'consignment': 'inventory:issue_consignment_create_from_warehouse_request',
            }
        else:
            return None
        
        url_name = url_names.get(self.document_subtype)
        if url_name:
            return reverse(url_name, kwargs={'pk': request_obj.pk})
        return None
    
    def get_context_data(self, **kwargs):
        """Display form to select lines/quantity from request."""
        context = super().get_context_data(**kwargs)
        request_obj = self.get_request_object(kwargs['pk'])
        
        context[f'{self.document_type}_type'] = self.document_subtype
        context[f'{self.document_type}_type_name'] = self.get_type_name()
        
        if self.is_multi_line:
            # For PurchaseRequest: get lines
            lines = request_obj.lines.filter(is_enabled=1).order_by('sort_order', 'id')
            context['lines'] = lines
            context['purchase_request'] = request_obj
        else:
            # For WarehouseRequest: calculate remaining quantity
            context['warehouse_request'] = request_obj
            remaining_quantity = request_obj.quantity_requested
            if hasattr(request_obj, 'quantity_issued') and request_obj.quantity_issued:
                remaining_quantity = request_obj.quantity_requested - request_obj.quantity_issued
            context['remaining_quantity'] = remaining_quantity
            context['default_quantity'] = remaining_quantity
        
        return context
    
    def process_multi_line_post(self, request, request_obj):
        """Process POST for multi-line requests (PurchaseRequest)."""
        selected_lines = []
        for line in request_obj.lines.filter(is_enabled=1):
            line_id = str(line.pk)
            quantity_key = f'quantity_{line_id}'
            selected_key = f'selected_{line_id}'
            
            if request.POST.get(selected_key) == 'on':
                quantity = request.POST.get(quantity_key, '0')
                try:
                    quantity = Decimal(str(quantity))
                    if quantity > 0:
                        remaining = getattr(line, 'quantity_remaining', line.quantity_requested)
                        if quantity > remaining:
                            quantity = remaining
                        selected_lines.append({
                            'line': line,
                            'quantity': quantity,
                        })
                except (ValueError, InvalidOperation):
                    pass
        
        if not selected_lines:
            messages.error(request, _('لطفاً حداقل یک ردیف را انتخاب کنید.'))
            return None
        
        # Store in session
        session_key = self.get_session_key(request_obj)
        session_data = [
            {
                'line_id': item['line'].pk,
                'quantity': str(item['quantity']),
            }
            for item in selected_lines
        ]
        request.session[session_key] = session_data
        return True
    
    def process_single_line_post(self, request, request_obj):
        """Process POST for single-line requests (WarehouseRequest)."""
        quantity_key = 'quantity'
        quantity_value = request.POST.get(quantity_key, '0')
        
        try:
            quantity = Decimal(str(quantity_value))
            
            # Calculate remaining quantity
            remaining_quantity = request_obj.quantity_requested
            if hasattr(request_obj, 'quantity_issued') and request_obj.quantity_issued:
                remaining_quantity = request_obj.quantity_requested - request_obj.quantity_issued
            
            if quantity <= 0:
                messages.error(request, _('مقدار باید بیشتر از صفر باشد.'))
                return None
            
            if quantity > remaining_quantity:
                quantity = remaining_quantity
                messages.warning(request, _('مقدار بیشتر از مقدار باقیمانده بود و به مقدار باقیمانده تنظیم شد.'))
            
            # Get optional notes
            notes = request.POST.get('notes', '').strip()
            
            # Store in session
            session_key = self.get_session_key(request_obj)
            session_data = {
                'warehouse_request_id': request_obj.pk,
                'quantity': str(quantity),
                'notes': notes,
            }
            request.session[session_key] = session_data
            return True
            
        except (ValueError, InvalidOperation):
            messages.error(request, _('مقدار وارد شده معتبر نیست.'))
            return None
    
    def post(self, request, *args, **kwargs):
        """Process selected lines/quantity and redirect to document creation."""
        request_obj = self.get_request_object(kwargs['pk'])
        
        if self.is_multi_line:
            result = self.process_multi_line_post(request, request_obj)
        else:
            result = self.process_single_line_post(request, request_obj)
        
        if result is None:
            # Error occurred, re-render form
            return self.get(request, *args, **kwargs)
        
        # Redirect to document creation
        redirect_url = self.get_redirect_url(request_obj)
        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        
        # Fallback: redirect to request list
        if self.document_type == 'receipt':
            return HttpResponseRedirect(reverse('inventory:purchase_requests'))
        elif self.document_type == 'issue':
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))
        return HttpResponseRedirect(reverse('inventory:index'))


"""
Additional Base Classes for complex view patterns.
"""
from typing import Optional, Any, Dict, List
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from shared.views.base import BaseCreateView, BaseUpdateView


class TransferRequestCreationMixin:
    """
    Mixin for creating transfer requests from orders.
    
    This mixin provides functionality to create transfer requests after creating
    an order, with permission checking and conditional logic.
    
    Usage:
        class ProductOrderCreateView(TransferRequestCreationMixin, BaseFormsetCreateView):
            feature_code = 'production.product_orders'
            
            def get_transfer_request_feature_code(self):
                return 'production.product_orders'
            
            def get_transfer_request_action(self):
                return 'create_transfer_from_order'
    """
    
    def should_create_transfer_request(self, form) -> bool:
        """
        Check if transfer request should be created.
        Override for custom logic.
        
        Returns:
            True if transfer request should be created
        """
        return form.cleaned_data.get('create_transfer_request', False)
    
    def get_transfer_request_feature_code(self) -> str:
        """
        Return feature code for transfer request permission check.
        Override for custom feature code.
        """
        return self.feature_code
    
    def get_transfer_request_action(self) -> str:
        """
        Return action name for transfer request permission check.
        Override for custom action.
        """
        return 'create_transfer_from_order'
    
    def get_transfer_request_kwargs(self, form) -> Dict[str, Any]:
        """
        Return kwargs for transfer request creation.
        Override for custom kwargs.
        
        Returns:
            Dictionary of kwargs for _create_transfer_request
        """
        return {
            'approved_by': form.cleaned_data.get('transfer_approved_by'),
            'transfer_type': form.cleaned_data.get('transfer_type', 'full'),
            'selected_operations': form.cleaned_data.get('selected_operations', []),
        }
    
    def create_transfer_request_if_needed(self, form, order) -> Optional[Any]:
        """
        Create transfer request if conditions are met.
        
        Args:
            form: The validated form
            order: The created order object
            
        Returns:
            Created transfer request or None
        """
        if not self.should_create_transfer_request(form):
            return None
        
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return None
        
        # Check permission
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        
        permissions = get_user_feature_permissions(self.request.user, active_company_id)
        has_permission = has_feature_permission(
            permissions,
            self.get_transfer_request_feature_code(),
            action=self.get_transfer_request_action(),
        )
        
        if not has_permission:
            messages.warning(
                self.request,
                _('You do not have permission to create transfer requests.')
            )
            return None
        
        # Get kwargs for transfer request creation
        kwargs = self.get_transfer_request_kwargs(form)
        kwargs['order'] = order
        kwargs['company_id'] = active_company_id
        
        try:
            transfer_request = self._create_transfer_request(**kwargs)
            messages.success(
                self.request,
                _('Transfer request created successfully.')
            )
            return transfer_request
        except Exception as e:
            messages.warning(
                self.request,
                _('Transfer request creation failed: {error}').format(error=str(e))
            )
            return None
    
    def _create_transfer_request(self, order, approved_by, company_id: int, **kwargs) -> Any:
        """
        Create transfer request. Override for custom implementation.
        
        Args:
            order: The order object
            approved_by: User who approves the transfer
            company_id: Company ID
            **kwargs: Additional kwargs
            
        Returns:
            Created transfer request object
        """
        raise NotImplementedError("Subclasses must implement _create_transfer_request")


class BaseMultipleFormsetCreateView(BaseCreateView):
    """
    Base CreateView with multiple formsets support.
    
    This class extends BaseCreateView to handle multiple formsets
    (e.g., PerformanceRecord with materials, persons, and machines formsets).
    
    Usage:
        class PerformanceRecordCreateView(BaseMultipleFormsetCreateView):
            model = PerformanceRecord
            form_class = PerformanceRecordForm
            formsets = {
                'materials': PerformanceRecordMaterialFormSet,
                'persons': PerformanceRecordPersonFormSet,
                'machines': PerformanceRecordMachineFormSet,
            }
            formset_prefixes = {
                'materials': 'materials',
                'persons': 'persons',
                'machines': 'machines',
            }
            success_url = reverse_lazy('production:performance_records')
            feature_code = 'production.performance_records'
    """
    
    formsets: Dict[str, Any] = {}
    formset_prefixes: Dict[str, str] = {}
    
    def get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]:
        """
        Return kwargs for a specific formset. Override for custom kwargs.
        
        Args:
            formset_name: Name of the formset
            
        Returns:
            Dictionary of kwargs for formset
        """
        kwargs = {}
        if hasattr(self, 'object') and self.object:
            kwargs['instance'] = self.object
        return kwargs
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add multiple formsets to context."""
        context = super().get_context_data(**kwargs)
        
        # Add formsets to context
        for formset_name, formset_class in self.formsets.items():
            prefix = self.formset_prefixes.get(formset_name, formset_name)
            
            if self.request.method == 'POST':
                formset = formset_class(
                    self.request.POST,
                    prefix=prefix,
                    **self.get_formset_kwargs(formset_name)
                )
            else:
                formset = formset_class(
                    prefix=prefix,
                    **self.get_formset_kwargs(formset_name)
                )
            
            context[f'{formset_name}_formset'] = formset
        
        return context
    
    def validate_formsets(self) -> bool:
        """
        Validate all formsets. Override for custom validation logic.
        
        Returns:
            True if all formsets are valid
        """
        context = self.get_context_data()
        for formset_name in self.formsets.keys():
            formset = context.get(f'{formset_name}_formset')
            if formset and not formset.is_valid():
                return False
        return True
    
    def save_formsets(self) -> Dict[str, List[Any]]:
        """
        Save all formsets. Override for custom saving logic.
        
        Returns:
            Dictionary mapping formset names to saved instances
        """
        context = self.get_context_data()
        saved_instances = {}
        
        for formset_name in self.formsets.keys():
            formset = context.get(f'{formset_name}_formset')
            if formset and formset.is_valid():
                # Hook for custom formset processing
                instances = self.process_formset(formset_name, formset)
                if instances is not None:
                    saved_instances[formset_name] = instances
                else:
                    # Default: save formset normally
                    saved_instances[formset_name] = formset.save()
            else:
                saved_instances[formset_name] = []
        
        return saved_instances
    
    def process_formset(self, formset_name: str, formset) -> Optional[List[Any]]:
        """
        Process formset before saving. Override for custom logic.
        
        Args:
            formset_name: Name of the formset
            formset: The formset instance
            
        Returns:
            List of saved instances, or None to use default saving
        """
        return None
    
    def form_valid(self, form):
        """Save form and all formsets."""
        from django.db import transaction
        from django.http import HttpResponseRedirect
        
        with transaction.atomic():
            # Save main object first
            self.object = form.save()
            
            # Update formset kwargs with new instance
            for formset_name in self.formsets.keys():
                # Recreate formsets with instance
                prefix = self.formset_prefixes.get(formset_name, formset_name)
                formset_class = self.formsets[formset_name]
                
                formset = formset_class(
                    self.request.POST,
                    instance=self.object,
                    prefix=prefix,
                    **self.get_formset_kwargs(formset_name)
                )
                
                if not formset.is_valid():
                    # Formset validation failed
                    return self.form_invalid(form)
            
            # Save all formsets
            saved_instances = self.save_formsets()
            
            # Hook for post-save processing
            self.after_formsets_save(saved_instances)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def after_formsets_save(self, saved_instances: Dict[str, List[Any]]) -> None:
        """
        Hook called after all formsets are saved. Override for custom logic.
        
        Args:
            saved_instances: Dictionary mapping formset names to saved instances
        """
        pass


class BaseMultipleFormsetUpdateView(BaseUpdateView):
    """
    Base UpdateView with multiple formsets support.
    
    This class extends BaseUpdateView to handle multiple formsets.
    
    Usage:
        class PerformanceRecordUpdateView(BaseMultipleFormsetUpdateView):
            model = PerformanceRecord
            form_class = PerformanceRecordForm
            formsets = {
                'materials': PerformanceRecordMaterialFormSet,
                'persons': PerformanceRecordPersonFormSet,
                'machines': PerformanceRecordMachineFormSet,
            }
            formset_prefixes = {
                'materials': 'materials',
                'persons': 'persons',
                'machines': 'machines',
            }
            success_url = reverse_lazy('production:performance_records')
            feature_code = 'production.performance_records'
    """
    
    formsets: Dict[str, Any] = {}
    formset_prefixes: Dict[str, str] = {}
    
    def get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]:
        """Return kwargs for a specific formset. Override for custom kwargs."""
        kwargs = {}
        if hasattr(self, 'object') and self.object:
            kwargs['instance'] = self.object
        return kwargs
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add multiple formsets to context."""
        context = super().get_context_data(**kwargs)
        
        # Add formsets to context
        for formset_name, formset_class in self.formsets.items():
            prefix = self.formset_prefixes.get(formset_name, formset_name)
            
            if self.request.method == 'POST':
                formset = formset_class(
                    self.request.POST,
                    instance=self.object,
                    prefix=prefix,
                    **self.get_formset_kwargs(formset_name)
                )
            else:
                formset = formset_class(
                    instance=self.object,
                    prefix=prefix,
                    **self.get_formset_kwargs(formset_name)
                )
            
            context[f'{formset_name}_formset'] = formset
        
        return context
    
    def validate_formsets(self) -> bool:
        """Validate all formsets. Override for custom validation logic."""
        context = self.get_context_data()
        for formset_name in self.formsets.keys():
            formset = context.get(f'{formset_name}_formset')
            if formset and not formset.is_valid():
                return False
        return True
    
    def save_formsets(self) -> Dict[str, List[Any]]:
        """Save all formsets. Override for custom saving logic."""
        context = self.get_context_data()
        saved_instances = {}
        
        for formset_name in self.formsets.keys():
            formset = context.get(f'{formset_name}_formset')
            if formset and formset.is_valid():
                # Hook for custom formset processing
                instances = self.process_formset(formset_name, formset)
                if instances is not None:
                    saved_instances[formset_name] = instances
                else:
                    # Default: save formset normally
                    saved_instances[formset_name] = formset.save()
            else:
                saved_instances[formset_name] = []
        
        return saved_instances
    
    def process_formset(self, formset_name: str, formset) -> Optional[List[Any]]:
        """
        Process formset before saving. Override for custom logic.
        
        Returns:
            List of saved instances, or None to use default saving
        """
        return None
    
    def form_valid(self, form):
        """Save form and all formsets."""
        from django.db import transaction
        from django.http import HttpResponseRedirect
        
        with transaction.atomic():
            # Save main object first
            self.object = form.save()
            
            # Validate all formsets
            if not self.validate_formsets():
                return self.form_invalid(form)
            
            # Save all formsets
            saved_instances = self.save_formsets()
            
            # Hook for post-save processing
            self.after_formsets_save(saved_instances)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def after_formsets_save(self, saved_instances: Dict[str, List[Any]]) -> None:
        """Hook called after all formsets are saved. Override for custom logic."""
        pass


class BaseMultipleDocumentCreateView(BaseCreateView):
    """
    Base CreateView for creating multiple documents from a single form.
    
    This class extends BaseCreateView to handle creation of multiple documents
    (e.g., TransferToLine creating one document per operation).
    
    Usage:
        class TransferToLineCreateView(BaseMultipleDocumentCreateView):
            model = TransferToLine
            form_class = TransferToLineForm
            success_url = reverse_lazy('production:transfer_requests')
            feature_code = 'production.transfer_requests'
            
            def get_documents_to_create(self, form):
                # Return list of document data dictionaries
                return [...]
            
            def create_document(self, document_data):
                # Create and return a document
                return TransferToLine.objects.create(**document_data)
    """
    
    def get_documents_to_create(self, form) -> List[Dict[str, Any]]:
        """
        Return list of document data dictionaries to create.
        Override for custom logic.
        
        Args:
            form: The validated form
            
        Returns:
            List of dictionaries, each containing data for one document
        """
        raise NotImplementedError("Subclasses must implement get_documents_to_create")
    
    def create_document(self, document_data: Dict[str, Any]) -> Any:
        """
        Create a single document from document_data.
        Override for custom document creation logic.
        
        Args:
            document_data: Dictionary of data for the document
            
        Returns:
            Created document object
        """
        raise NotImplementedError("Subclasses must implement create_document")
    
    def after_document_created(self, document: Any, document_data: Dict[str, Any]) -> None:
        """
        Hook called after each document is created. Override for custom logic.
        
        Args:
            document: The created document
            document_data: The data used to create the document
        """
        pass
    
    def after_all_documents_created(self, documents: List[Any]) -> None:
        """
        Hook called after all documents are created. Override for custom logic.
        
        Args:
            documents: List of all created documents
        """
        pass
    
    def form_valid(self, form):
        """Create multiple documents from form data."""
        from django.db import transaction
        from django.http import HttpResponseRedirect
        
        with transaction.atomic():
            # Get list of documents to create
            documents_data = self.get_documents_to_create(form)
            
            if not documents_data:
                messages.error(
                    self.request,
                    _('No documents to create.')
                )
                return self.form_invalid(form)
            
            # Create all documents
            created_documents = []
            for document_data in documents_data:
                try:
                    document = self.create_document(document_data)
                    created_documents.append(document)
                    
                    # Hook for post-creation processing
                    self.after_document_created(document, document_data)
                except Exception as e:
                    messages.error(
                        self.request,
                        _('Error creating document: {error}').format(error=str(e))
                    )
                    # Rollback transaction
                    raise
            
            # Hook for post-all-creation processing
            self.after_all_documents_created(created_documents)
            
            # Set self.object to first created document (for compatibility)
            if created_documents:
                self.object = created_documents[0]
        
        return HttpResponseRedirect(self.get_success_url())

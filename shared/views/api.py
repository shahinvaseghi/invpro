"""
Base API view classes for JSON endpoints across all modules.

These classes provide common functionality for API endpoints like:
- Company validation
- JSON response formatting
- Error handling
- Permission checks
"""
from typing import Optional, Dict, Any, List
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet, Model
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger('shared.views.api')


class BaseAPIView(LoginRequiredMixin, View):
    """
    Base API view with common functionality for JSON endpoints.
    
    This class provides:
    - Company validation
    - JSON response formatting
    - Error handling
    - User authentication
    
    Usage:
        class MyAPIView(BaseAPIView):
            def get(self, request):
                company_id = self.get_company_id()
                if not company_id:
                    return self.error_response('No active company', status=400)
                
                data = {'result': 'success'}
                return self.json_response(data)
    """
    
    def get_company_id(self) -> Optional[int]:
        """
        Get active company ID from session.
        
        Returns:
            Company ID or None if no company is active
        """
        return self.request.session.get('active_company_id')
    
    def validate_company(self) -> tuple[bool, Optional[str]]:
        """
        Validate that active company exists.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        company_id = self.get_company_id()
        if not company_id:
            return False, _('No active company selected.')
        return True, None
    
    def get_user(self):
        """Get current authenticated user."""
        return self.request.user
    
    def json_response(self, data: Dict[str, Any], status: int = 200) -> JsonResponse:
        """
        Return JSON response with data.
        
        Args:
            data: Dictionary to serialize as JSON
            status: HTTP status code (default: 200)
            
        Returns:
            JsonResponse object
        """
        return JsonResponse(data, status=status)
    
    def error_response(self, message: str, status: int = 400, **kwargs) -> JsonResponse:
        """
        Return error JSON response.
        
        Args:
            message: Error message
            status: HTTP status code (default: 400)
            **kwargs: Additional error data
            
        Returns:
            JsonResponse with error format
        """
        response_data = {
            'error': message,
            **kwargs
        }
        return JsonResponse(response_data, status=status)
    
    def success_response(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None, **kwargs) -> JsonResponse:
        """
        Return success JSON response.
        
        Args:
            message: Success message (optional)
            data: Additional data (optional)
            **kwargs: Additional response data
            
        Returns:
            JsonResponse with success format
        """
        response_data = {
            'success': True,
            **kwargs
        }
        if message:
            response_data['message'] = message
        if data:
            response_data.update(data)
        return self.json_response(response_data, status=200)


class BaseListAPIView(BaseAPIView):
    """
    Base API view for listing objects as JSON.
    
    This class provides:
    - List serialization
    - Filtering
    - Pagination support
    
    Usage:
        class ItemListAPIView(BaseListAPIView):
            model = Item
            
            def get_queryset(self):
                company_id = self.get_company_id()
                return self.model.objects.filter(company_id=company_id)
            
            def serialize_object(self, obj):
                return {
                    'id': obj.id,
                    'name': obj.name,
                    'code': obj.public_code,
                }
    """
    
    model: Optional[Model] = None
    paginate_by: Optional[int] = None
    
    def get(self, request: HttpRequest) -> JsonResponse:
        """Return list of objects as JSON."""
        # Validate company
        is_valid, error_message = self.validate_company()
        if not is_valid:
            return self.error_response(error_message, status=400)
        
        # Get queryset
        queryset = self.get_queryset()
        
        # Apply filters
        queryset = self.filter_queryset(queryset)
        
        # Serialize objects
        results = [self.serialize_object(obj) for obj in queryset]
        
        # Pagination (if enabled)
        if self.paginate_by:
            from django.core.paginator import Paginator
            paginator = Paginator(queryset, self.paginate_by)
            page_number = request.GET.get('page', 1)
            try:
                page = paginator.page(page_number)
            except Exception:
                page = paginator.page(1)
            
            return self.json_response({
                'results': [self.serialize_object(obj) for obj in page.object_list],
                'count': paginator.count,
                'page': page.number,
                'num_pages': paginator.num_pages,
                'has_next': page.has_next(),
                'has_previous': page.has_previous(),
            })
        
        return self.json_response({
            'results': results,
            'count': len(results),
        })
    
    def get_queryset(self) -> QuerySet:
        """
        Get queryset for listing.
        
        Override this method to customize queryset.
        """
        if self.model is None:
            raise ValueError("model attribute must be set")
        return self.model.objects.all()
    
    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """
        Filter queryset based on request parameters.
        
        Override this method to add custom filtering.
        """
        return queryset
    
    def serialize_object(self, obj: Model) -> Dict[str, Any]:
        """
        Serialize single object to dictionary.
        
        Override this method to customize serialization.
        
        Args:
            obj: Model instance to serialize
            
        Returns:
            Dictionary representation of object
        """
        return {
            'id': obj.pk,
            'str': str(obj),
        }


class BaseDetailAPIView(BaseAPIView):
    """
    Base API view for retrieving single object as JSON.
    
    This class provides:
    - Object retrieval
    - Serialization
    - Error handling
    
    Usage:
        class ItemDetailAPIView(BaseDetailAPIView):
            model = Item
            
            def serialize_object(self, obj):
                return {
                    'id': obj.id,
                    'name': obj.name,
                    'code': obj.public_code,
                }
    """
    
    model: Optional[Model] = None
    lookup_field: str = 'pk'
    lookup_url_kwarg: str = 'pk'
    
    def get(self, request: HttpRequest, **kwargs) -> JsonResponse:
        """Return single object as JSON."""
        # Validate company
        is_valid, error_message = self.validate_company()
        if not is_valid:
            return self.error_response(error_message, status=400)
        
        # Get object
        try:
            obj = self.get_object(**kwargs)
        except ObjectDoesNotExist:
            return self.error_response(_('Object not found'), status=404)
        except Exception as e:
            logger.error(f"Error retrieving object: {e}")
            return self.error_response(_('Error retrieving object'), status=500)
        
        # Serialize and return
        data = self.serialize_object(obj)
        return self.json_response(data)
    
    def get_object(self, **kwargs) -> Model:
        """
        Get object instance.
        
        Override this method to customize object retrieval.
        """
        if self.model is None:
            raise ValueError("model attribute must be set")
        
        lookup_value = kwargs.get(self.lookup_url_kwarg)
        if lookup_value is None:
            raise ValueError(f"Lookup value not found in kwargs: {self.lookup_url_kwarg}")
        
        # Build lookup
        lookup = {self.lookup_field: lookup_value}
        
        # Add company filter if model has company_id
        company_id = self.get_company_id()
        if company_id and hasattr(self.model, 'company_id'):
            lookup['company_id'] = company_id
        
        return self.model.objects.get(**lookup)
    
    def serialize_object(self, obj: Model) -> Dict[str, Any]:
        """
        Serialize single object to dictionary.
        
        Override this method to customize serialization.
        
        Args:
            obj: Model instance to serialize
            
        Returns:
            Dictionary representation of object
        """
        return {
            'id': obj.pk,
            'str': str(obj),
        }


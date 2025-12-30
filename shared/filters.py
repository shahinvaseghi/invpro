"""
Common filter functions for queryset filtering across all modules.

These functions provide reusable filtering logic for search, status, company,
date range, and multi-field filters.
"""
from typing import List, Optional, Dict, Any
from django.db.models import Q, QuerySet
from django.http import HttpRequest


def apply_search(queryset: QuerySet, search_query: str, fields: List[str]) -> QuerySet:
    """
    Apply search across multiple fields using Q objects.
    
    Args:
        queryset: Django queryset to filter
        search_query: String search query (will be stripped)
        fields: List of field names to search in
        
    Returns:
        Filtered queryset
        
    Example:
        queryset = apply_search(queryset, "test", ['name', 'code', 'description'])
        # Will search for "test" in name, code, and description fields
    """
    if not search_query:
        return queryset
    
    search_query = search_query.strip()
    if not search_query:
        return queryset
    
    if not fields:
        return queryset
    
    q_objects = Q()
    for field in fields:
        q_objects |= Q(**{f"{field}__icontains": search_query})
    
    return queryset.filter(q_objects)


def apply_status_filter(queryset: QuerySet, status_value: str) -> QuerySet:
    """
    Apply status filter (active/inactive).
    
    Args:
        queryset: Django queryset to filter
        status_value: '0' (inactive), '1' (active), or empty string (no filter)
        
    Returns:
        Filtered queryset
        
    Example:
        queryset = apply_status_filter(queryset, '1')  # Only active records
        queryset = apply_status_filter(queryset, '0')  # Only inactive records
        queryset = apply_status_filter(queryset, '')   # No filter
    """
    if status_value in ('0', '1'):
        return queryset.filter(is_enabled=int(status_value))
    return queryset


def apply_company_filter(queryset: QuerySet, company_id: Optional[int]) -> QuerySet:
    """
    Apply company filter.
    
    Args:
        queryset: Django queryset to filter
        company_id: Company ID from session (None if no company selected)
        
    Returns:
        Filtered queryset (empty queryset if company_id is None and model has company_id field)
        
    Example:
        queryset = apply_company_filter(queryset, 123)
    """
    if company_id is None:
        # Check if model has company_id field
        if hasattr(queryset.model, 'company_id'):
            return queryset.none()
        return queryset
    
    # Check if model has company_id field
    if hasattr(queryset.model, 'company_id'):
        return queryset.filter(company_id=company_id)
    
    # Check if model has company field (ForeignKey)
    if hasattr(queryset.model, 'company'):
        return queryset.filter(company_id=company_id)
    
    return queryset


def apply_date_range_filter(
    queryset: QuerySet,
    date_from: Optional[str],
    date_to: Optional[str],
    field_name: str = 'created_at'
) -> QuerySet:
    """
    Apply date range filter.
    
    Args:
        queryset: Django queryset to filter
        date_from: Start date (string format, will be parsed)
        date_to: End date (string format, will be parsed)
        field_name: Field name to filter on (default: 'created_at')
        
    Returns:
        Filtered queryset
        
    Example:
        queryset = apply_date_range_filter(queryset, '2024-01-01', '2024-12-31', 'document_date')
    """
    from django.utils.dateparse import parse_date
    
    if date_from:
        try:
            parsed_date_from = parse_date(date_from)
            if parsed_date_from:
                queryset = queryset.filter(**{f"{field_name}__gte": parsed_date_from})
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            parsed_date_to = parse_date(date_to)
            if parsed_date_to:
                queryset = queryset.filter(**{f"{field_name}__lte": parsed_date_to})
        except (ValueError, TypeError):
            pass
    
    return queryset


def apply_multi_field_filter(
    queryset: QuerySet,
    request: HttpRequest,
    filter_map: Dict[str, str]
) -> QuerySet:
    """
    Apply multiple filters based on request.GET parameters.
    
    Args:
        queryset: Django queryset to filter
        request: Django request object
        filter_map: Dictionary mapping GET parameter names to model field names
                    Example: {'status': 'is_enabled', 'type': 'item_type_id'}
        
    Returns:
        Filtered queryset
        
    Example:
        filter_map = {
            'status': 'is_enabled',
            'type': 'item_type_id',
            'warehouse': 'warehouse_id'
        }
        queryset = apply_multi_field_filter(queryset, request, filter_map)
    """
    for param_name, field_name in filter_map.items():
        param_value = request.GET.get(param_name, '').strip()
        if param_value:
            # Try to convert to int if field name suggests it's a foreign key
            if field_name.endswith('_id') or field_name.endswith('_pk'):
                try:
                    param_value = int(param_value)
                except (ValueError, TypeError):
                    continue
            
            queryset = queryset.filter(**{field_name: param_value})
    
    return queryset


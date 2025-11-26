"""
Template filters for JSON conversion.
"""
import json
from django import template

register = template.Library()


@register.filter(name='to_json')
def to_json(value):
    """
    Convert a Python object (dict, list, etc.) to JSON string.
    
    Usage in templates:
        {{ field_config|to_json }}
    """
    if value is None:
        return '{}'
    
    if isinstance(value, str):
        # If it's already a string, try to parse it to validate JSON
        try:
            json.loads(value)
            return value
        except (json.JSONDecodeError, TypeError):
            return '{}'
    
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return '{}'


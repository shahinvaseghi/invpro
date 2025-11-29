"""
Generic template tags for reusable templates
"""
from django import template

register = template.Library()


@register.filter
def getattr(obj, attr):
    """
    Get attribute from object, supports nested attributes.
    
    Usage in template:
        {{ object|getattr:"field_name" }}
        {{ object|getattr:"nested.field" }}
    """
    try:
        if not obj:
            return None
            
        if '.' in attr:
            # Support nested attributes like "type.name"
            parts = attr.split('.')
            value = obj
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part, None)
                elif hasattr(value, '__getitem__'):
                    # Support dictionary access
                    try:
                        value = value[part]
                    except (KeyError, TypeError):
                        return None
                else:
                    return None
                if value is None:
                    return None
            return value
        else:
            # Simple attribute access
            if hasattr(obj, attr):
                return getattr(obj, attr, None)
            elif hasattr(obj, '__getitem__'):
                # Support dictionary access
                try:
                    return obj[attr]
                except (KeyError, TypeError):
                    return None
            return None
    except (AttributeError, TypeError, KeyError):
        return None


@register.filter
def get_field_value(obj, field_path):
    """
    Get field value from object using dot notation.
    Similar to getattr but with better error handling.
    
    Usage:
        {{ object|get_field_value:"type.name" }}
    """
    return getattr(obj, field_path)


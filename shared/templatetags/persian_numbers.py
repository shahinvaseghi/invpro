"""Template filters for Persian number conversion."""

from django import template

register = template.Library()

# Persian digits mapping
PERSIAN_DIGITS = {
    '0': '۰',
    '1': '۱',
    '2': '۲',
    '3': '۳',
    '4': '۴',
    '5': '۵',
    '6': '۶',
    '7': '۷',
    '8': '۸',
    '9': '۹',
}


@register.filter
def persian_numbers(value):
    """Convert English digits to Persian digits."""
    if value is None:
        return ''
    
    # Convert to string
    text = str(value)
    
    # Replace each English digit with Persian digit
    for eng, per in PERSIAN_DIGITS.items():
        text = text.replace(eng, per)
    
    return text


@register.filter
def persian_int(value):
    """Convert integer to Persian digits."""
    if value is None:
        return ''
    return persian_numbers(str(value))


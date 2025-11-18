"""
Template tags for displaying Jalali (Persian) dates.
"""
from django import template
from datetime import date, datetime
from inventory.utils.jalali import gregorian_to_jalali

register = template.Library()


@register.filter(name='jalali_date')
def jalali_date(value, format_str='%Y/%m/%d'):
    """
    Convert Gregorian date to Jalali date string for display.
    
    Usage in templates:
        {{ receipt.document_date|jalali_date }}
        {{ receipt.document_date|jalali_date:"%Y/%m/%d" }}
        {{ receipt.document_date|jalali_date:"%d %B %Y" }}
    """
    if not value:
        return ''
    
    # Convert to date if datetime
    if isinstance(value, datetime):
        value = value.date()
    
    if not isinstance(value, date):
        return value
    
    jalali_str = gregorian_to_jalali(value, format_str)
    return jalali_str or ''


@register.filter(name='jalali_date_short')
def jalali_date_short(value):
    """Short format: 1403/09/15"""
    return jalali_date(value, '%Y/%m/%d')


@register.filter(name='jalali_date_long')
def jalali_date_long(value):
    """Long format: 15 آذر 1403"""
    if not value:
        return ''
    
    if isinstance(value, datetime):
        value = value.date()
    
    if not isinstance(value, date):
        return value
    
    jalali_str = gregorian_to_jalali(value)
    if not jalali_str:
        return ''
    
    # Parse Jalali date to get day, month, year
    try:
        import jdatetime
        jalali = jdatetime.date.fromgregorian(date=value)
        
        # Persian month names
        month_names = [
            '', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]
        
        month_name = month_names[jalali.month] if 1 <= jalali.month <= 12 else ''
        return f'{jalali.day} {month_name} {jalali.year}'
    except (ValueError, AttributeError):
        return jalali_str


@register.filter(name='jalali_datetime')
def jalali_datetime(value, format_str='%Y/%m/%d %H:%M'):
    """
    Convert Gregorian datetime to Jalali datetime string for display.
    
    Usage in templates:
        {{ serial.created_at|jalali_datetime }}
        {{ serial.created_at|jalali_datetime:"%Y/%m/%d %H:%M:%S" }}
    """
    if not value:
        return ''
    
    # If value is a datetime, extract date and time
    if isinstance(value, datetime):
        date_part = value.date()
        time_part = value.time()
        jalali_date_str = gregorian_to_jalali(date_part, '%Y/%m/%d')
        if jalali_date_str:
            return f'{jalali_date_str} {time_part.strftime("%H:%M")}'
        return ''
    
    # If value is a date, just convert date part
    if isinstance(value, date):
        return gregorian_to_jalali(value, format_str) or ''
    
    return value


"""
Custom widgets for Jalali (Persian) date fields.
"""
from django import forms
from django.utils import timezone
from inventory.utils.jalali import gregorian_to_jalali, jalali_to_gregorian, today_jalali


class JalaliDateInput(forms.DateInput):
    """
    Custom date input widget that displays and accepts Jalali (Persian) dates.
    Stores Gregorian dates in the database, but shows Jalali in the UI.
    """
    input_type = 'text'
    template_name = 'inventory/widgets/jalali_date_input.html'
    
    def __init__(self, attrs=None, format=None):
        if attrs is None:
            attrs = {}
        # Add Jalali date picker attributes
        attrs.setdefault('class', 'jalali-date-input')
        attrs.setdefault('data-jalali', 'true')
        super().__init__(attrs, format)
    
    def format_value(self, value):
        """
        Convert Gregorian date to Jalali string for display.
        """
        if value is None:
            return ''
        
        # If value is already a string (Jalali), return as-is
        if isinstance(value, str):
            return value
        
        # If value is a date/datetime object, convert to Jalali
        from datetime import date, datetime
        if isinstance(value, (date, datetime)):
            return gregorian_to_jalali(value) or ''
        
        return ''
    
    def value_from_datadict(self, data, files, name):
        """
        Convert Jalali date string from form to Gregorian date.
        """
        value = data.get(name)
        if not value:
            return None
        
        # Convert Jalali to Gregorian
        gregorian = jalali_to_gregorian(value)
        if gregorian:
            return gregorian
        
        # If conversion fails, return None (will trigger validation error)
        return None


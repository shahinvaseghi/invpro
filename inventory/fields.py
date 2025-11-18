"""
Custom form fields for Jalali (Persian) dates.
"""
from django import forms
from django.core.exceptions import ValidationError
from inventory.utils.jalali import jalali_to_gregorian, gregorian_to_jalali
from inventory.widgets import JalaliDateInput


class JalaliDateField(forms.DateField):
    """
    Custom DateField that accepts Jalali (Persian) date strings
    and converts them to Gregorian dates for storage in the database.
    
    Usage:
        document_date = JalaliDateField(
            label='تاریخ سند',
            required=True,
            initial=jdatetime.date.today().strftime('%Y/%m/%d')
        )
    """
    widget = JalaliDateInput
    
    def __init__(self, *, input_formats=None, **kwargs):
        super().__init__(input_formats=input_formats, **kwargs)
        self.widget = JalaliDateInput(attrs=self.widget.attrs)
    
    def to_python(self, value):
        """
        Convert Jalali date string to Python date object (Gregorian).
        """
        if value in self.empty_values:
            return None
        
        if isinstance(value, (str, type(None))):
            # Convert Jalali string to Gregorian date
            gregorian = jalali_to_gregorian(value)
            if gregorian is None:
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
            return gregorian
        
        # If already a date object, return as-is
        if hasattr(value, 'year'):
            return value
        
        return super().to_python(value)
    
    def prepare_value(self, value):
        """
        Convert Gregorian date to Jalali string for display in form.
        """
        if value is None:
            return ''
        
        # Convert Gregorian to Jalali for display
        jalali_str = gregorian_to_jalali(value)
        return jalali_str or ''


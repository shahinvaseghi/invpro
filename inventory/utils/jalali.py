"""
Jalali (Persian) date utility functions for converting between Jalali and Gregorian dates.
All dates are stored as Gregorian in the database, but displayed and entered as Jalali in the UI.
"""
from datetime import date, datetime
from typing import Optional, Union
import jdatetime


def gregorian_to_jalali(gregorian_date: Union[date, datetime, str, None], format_str: str = '%Y/%m/%d') -> Optional[str]:
    """
    Convert Gregorian date to Jalali date string.
    
    Args:
        gregorian_date: Gregorian date (date, datetime, or YYYY-MM-DD string)
        format_str: Output format (default: '%Y/%m/%d' for 1403/09/15)
    
    Returns:
        Jalali date string or None if input is None/empty
    
    Examples:
        >>> gregorian_to_jalali(date(2024, 12, 5))
        '1403/09/15'
        >>> gregorian_to_jalali('2024-12-05')
        '1403/09/15'
    """
    if not gregorian_date:
        return None
    
    # Convert string to date if needed
    if isinstance(gregorian_date, str):
        try:
            gregorian_date = date.fromisoformat(gregorian_date)
        except ValueError:
            return None
    elif isinstance(gregorian_date, datetime):
        gregorian_date = gregorian_date.date()
    
    if not isinstance(gregorian_date, date):
        return None
    
    try:
        jalali = jdatetime.date.fromgregorian(date=gregorian_date)
        return jalali.strftime(format_str)
    except (ValueError, AttributeError):
        return None


def jalali_to_gregorian(jalali_date: Union[str, None], format_str: str = '%Y/%m/%d') -> Optional[date]:
    """
    Convert Jalali date string to Gregorian date.
    
    Args:
        jalali_date: Jalali date string (e.g., '1403/09/15' or '1403-09-15')
        format_str: Input format (default: '%Y/%m/%d' for 1403/09/15)
    
    Returns:
        Gregorian date object or None if input is None/empty/invalid
    
    Examples:
        >>> jalali_to_gregorian('1403/09/15')
        datetime.date(2024, 12, 5)
        >>> jalali_to_gregorian('1403-09-15', '%Y-%m-%d')
        datetime.date(2024, 12, 5)
    """
    if not jalali_date:
        return None
    
    # Clean and normalize input
    jalali_date = jalali_date.strip()
    
    # Try multiple formats
    formats_to_try = [
        '%Y/%m/%d',      # 1403/09/15
        '%Y-%m-%d',      # 1403-09-15
        '%Y/%m/%d',      # 1403/9/5 (single digit)
        '%Y-%m-%d',      # 1403-9-5
    ]
    
    # If input contains / or -, use appropriate format
    if '/' in jalali_date:
        formats_to_try = ['%Y/%m/%d', '%Y/%-m/%-d'] + formats_to_try
    elif '-' in jalali_date:
        formats_to_try = ['%Y-%m-%d', '%Y-%-m-%-d'] + formats_to_try
    
    for fmt in formats_to_try:
        try:
            jalali = jdatetime.datetime.strptime(jalali_date, fmt)
            return jalali.togregorian().date()
        except (ValueError, AttributeError):
            continue
    
    # If all formats fail, try parsing with default format
    try:
        jalali = jdatetime.datetime.strptime(jalali_date, format_str)
        return jalali.togregorian().date()
    except (ValueError, AttributeError):
        return None


def get_jalali_date_input_format() -> str:
    """Get the format string for Jalali date input in HTML date input."""
    return '%Y/%m/%d'


def get_jalali_date_display_format() -> str:
    """Get the format string for Jalali date display in templates."""
    return '%Y/%m/%d'


def today_jalali() -> str:
    """Get today's date as Jalali string."""
    today = jdatetime.date.today()
    return today.strftime('%Y/%m/%d')


def today_gregorian() -> date:
    """Get today's date as Gregorian date (same as date.today())."""
    return jdatetime.date.today().togregorian()


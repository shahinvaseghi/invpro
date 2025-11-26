"""
Utility functions for checking module availability and optional dependencies.
"""
from django.apps import apps


def is_production_installed() -> bool:
    """
    Check if the production module is installed.
    
    Returns:
        True if production module is installed, False otherwise.
    """
    return apps.is_installed('production')


def is_qc_installed() -> bool:
    """
    Check if the QC module is installed.
    
    Returns:
        True if QC module is installed, False otherwise.
    """
    return apps.is_installed('qc')


def get_work_line_model():
    """
    Get the WorkLine model from production module if available.
    
    Returns:
        WorkLine model class if production is installed, None otherwise.
    """
    if not is_production_installed():
        return None
    
    try:
        from production.models import WorkLine
        return WorkLine
    except ImportError:
        return None


def get_person_model():
    """
    Get the Person model from production module if available.
    
    Returns:
        Person model class if production is installed, None otherwise.
    """
    if not is_production_installed():
        return None
    
    try:
        from production.models import Person
        return Person
    except ImportError:
        return None


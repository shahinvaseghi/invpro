"""
Models for accounting module - Wrapper for backward compatibility.

This file is a wrapper that imports all models from the models/ package.
The actual model definitions are in the models/ directory for better organization.
"""
# Import all models from models package for backward compatibility
from .models import *  # noqa: F401, F403


"""
Forms for inventory module.

This file is kept for backward compatibility.
All forms have been refactored into inventory.forms package.

For new code, use:
    from inventory.forms import FormName
    from inventory.forms.base import BaseForm
    from inventory.forms.master_data import ItemForm
    etc.
"""
# Import everything from the package for backward compatibility
from inventory.forms import *  # noqa: F401, F403

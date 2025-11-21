"""
Forms for shared module.

This file is kept for backward compatibility.
All forms have been refactored into shared.forms package.

For new code, use:
    from shared.forms import FormName
    from shared.forms.companies import CompanyForm
    from shared.forms.users import UserCreateForm
    etc.
"""
# Import everything from the package for backward compatibility
from shared.forms import *  # noqa: F401, F403

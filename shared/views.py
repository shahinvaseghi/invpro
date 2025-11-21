"""
Views for shared module.

This file is kept for backward compatibility.
All views have been refactored into shared.views package.

For new code, use:
    from shared.views import ViewName
    from shared.views.companies import CompanyListView
    from shared.views.auth import set_active_company
    etc.
"""
# Import everything from the package for backward compatibility
from shared.views import *  # noqa: F401, F403

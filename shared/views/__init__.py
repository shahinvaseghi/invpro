"""
Views package for shared module.

This package contains refactored views organized by functionality:
- base: Base mixins and helper classes
- auth: Authentication views
- companies: Company CRUD views
- company_units: CompanyUnit CRUD views
- users: User CRUD views
- groups: Group CRUD views
- access_levels: AccessLevel CRUD views
"""
__all__ = []

# Import base mixins
from shared.views.base import UserAccessFormsetMixin, AccessLevelPermissionMixin, EditLockProtectedMixin

# Import auth views
from shared.views.auth import set_active_company, custom_login

# Import company views
from shared.views.companies import (
    CompanyListView,
    CompanyCreateView,
    CompanyDetailView,
    CompanyUpdateView,
    CompanyDeleteView,
)

# Import company unit views
from shared.views.company_units import (
    CompanyUnitListView,
    CompanyUnitCreateView,
    CompanyUnitDetailView,
    CompanyUnitUpdateView,
    CompanyUnitDeleteView,
)

# Import user views
from shared.views.users import (
    UserListView,
    UserCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
)

# Import group views
from shared.views.groups import (
    GroupListView,
    GroupCreateView,
    GroupDetailView,
    GroupUpdateView,
    GroupDeleteView,
)

# Import access level views
from shared.views.access_levels import (
    AccessLevelListView,
    AccessLevelCreateView,
    AccessLevelDetailView,
    AccessLevelUpdateView,
    AccessLevelDeleteView,
)

# Import SMTP server views
from shared.views.smtp_server import (
    SMTPServerListView,
    SMTPServerCreateView,
    SMTPServerDetailView,
    SMTPServerUpdateView,
    SMTPServerDeleteView,
)

__all__ = [
    # Base mixins
    'UserAccessFormsetMixin',
    'AccessLevelPermissionMixin',
    'EditLockProtectedMixin',
    # Auth views
    'set_active_company',
    'custom_login',
    # Company views
    'CompanyListView',
    'CompanyCreateView',
    'CompanyDetailView',
    'CompanyUpdateView',
    'CompanyDeleteView',
    # Company unit views
    'CompanyUnitListView',
    'CompanyUnitCreateView',
    'CompanyUnitDetailView',
    'CompanyUnitUpdateView',
    'CompanyUnitDeleteView',
    # User views
    'UserListView',
    'UserCreateView',
    'UserDetailView',
    'UserUpdateView',
    'UserDeleteView',
    # Group views
    'GroupListView',
    'GroupCreateView',
    'GroupDetailView',
    'GroupUpdateView',
    'GroupDeleteView',
    # Access level views
    'AccessLevelListView',
    'AccessLevelCreateView',
    'AccessLevelDetailView',
    'AccessLevelUpdateView',
    'AccessLevelDeleteView',
    # SMTP server views
    'SMTPServerListView',
    'SMTPServerCreateView',
    'SMTPServerDetailView',
    'SMTPServerUpdateView',
    'SMTPServerDeleteView',
]


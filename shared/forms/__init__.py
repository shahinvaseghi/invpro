"""
Forms package for shared module.

This package contains all forms for the shared module, organized by functionality:
- companies.py: Company and CompanyUnit forms
- users.py: User and UserCompanyAccess forms
- groups.py: Group forms
- access_levels.py: AccessLevel forms
"""
__all__ = []

# Import company forms
from shared.forms.companies import (
    CompanyForm,
    CompanyUnitForm,
)

__all__.extend([
    'CompanyForm',
    'CompanyUnitForm',
])

# Import user forms
from shared.forms.users import (
    UserBaseForm,
    UserCreateForm,
    UserUpdateForm,
    UserCompanyAccessForm,
    BaseUserCompanyAccessFormSet,
    UserCompanyAccessFormSet,
)

__all__.extend([
    'UserBaseForm',
    'UserCreateForm',
    'UserUpdateForm',
    'UserCompanyAccessForm',
    'BaseUserCompanyAccessFormSet',
    'UserCompanyAccessFormSet',
])

# Import group forms
from shared.forms.groups import (
    GroupForm,
)

__all__.extend([
    'GroupForm',
])

# Import access level forms
from shared.forms.access_levels import (
    AccessLevelForm,
)

__all__.extend([
    'AccessLevelForm',
])


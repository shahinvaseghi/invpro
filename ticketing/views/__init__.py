"""
Views package for ticketing module.

This package contains all views for the ticketing module, organized by functionality.
All views follow the package-based structure for better organization and maintainability.
"""

__all__ = []

# Import base classes
from .base import (
    TicketingBaseView,
    TicketLockProtectedMixin,
)

# Import ticket views
from .tickets import (
    TicketListView,
    TicketCreateView,
    TicketEditView,
)

# Import placeholder views
from .placeholders import (
    TicketRespondView,
    TemplateCreateView,
    AutoResponseView,
)

# Import category views
from .categories import (
    TicketCategoryListView,
    TicketCategoryCreateView,
    TicketCategoryUpdateView,
    TicketCategoryDeleteView,
)

# Import subcategory views
from .subcategories import (
    TicketSubcategoryListView,
    TicketSubcategoryCreateView,
    TicketSubcategoryUpdateView,
    TicketSubcategoryDeleteView,
)

# Future imports will be added here as views are implemented
# from .templates import (
#     TicketTemplateListView,
#     TicketTemplateCreateView,
#     ...
# )

__all__ = [
    "TicketingBaseView",
    "TicketLockProtectedMixin",
    "TicketListView",
    "TicketCreateView",
    "TicketEditView",
    "TicketRespondView",
    "TemplateCreateView",
    "TicketCategoryListView",
    "TicketCategoryCreateView",
    "TicketCategoryUpdateView",
    "TicketCategoryDeleteView",
    "TicketSubcategoryListView",
    "TicketSubcategoryCreateView",
    "TicketSubcategoryUpdateView",
    "TicketSubcategoryDeleteView",
    "AutoResponseView",
]


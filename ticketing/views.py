"""
Views for ticketing module.

This file is kept for backward compatibility.
All views have been refactored into ticketing.views package.
"""
from ticketing.views import (
    TicketingBaseView,
    TicketLockProtectedMixin,
    TicketListView,
    TicketCreateView,
    TicketEditView,
    TicketRespondView,
    TicketTemplateListView,
    TicketTemplateCreateView,
    TicketTemplateUpdateView,
    TicketTemplateDeleteView,
    TicketCategoryListView,
    TicketCategoryCreateView,
    TicketCategoryUpdateView,
    TicketCategoryDeleteView,
    TicketSubcategoryListView,
    TicketSubcategoryCreateView,
    TicketSubcategoryUpdateView,
    TicketSubcategoryDeleteView,
    AutoResponseView,
)

__all__ = [
    "TicketingBaseView",
    "TicketLockProtectedMixin",
    "TicketListView",
    "TicketCreateView",
    "TicketEditView",
    "TicketRespondView",
    "TicketTemplateListView",
    "TicketTemplateCreateView",
    "TicketTemplateUpdateView",
    "TicketTemplateDeleteView",
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

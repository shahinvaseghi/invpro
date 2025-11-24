"""
Forms for ticketing module.

This file is kept for backward compatibility.
All forms have been refactored into ticketing.forms package.
"""
from ticketing.forms.tickets import (
    TicketForm,
    TicketCreateForm,
)

__all__ = [
    "TicketForm",
    "TicketCreateForm",
]


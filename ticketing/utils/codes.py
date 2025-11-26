"""
Code generation utilities for ticketing module.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from django.db import transaction


def generate_sequential_code(
    model,
    *,
    company_id: Optional[int],
    field: str = "public_code",
    width: int = 3,
    extra_filters: Optional[Dict] = None,
) -> str:
    """Return the next sequential numeric code for the given model.

    The code is scoped by company and optional extra filters.
    """
    filters = dict(extra_filters or {})
    if company_id is not None and any(f.name == "company" for f in model._meta.fields):
        filters["company_id"] = company_id

    with transaction.atomic():
        last_code = (
            model.objects.filter(**filters)
            .order_by(f"-{field}")
            .values_list(field, flat=True)
            .first()
        )
        next_value = 1
        if last_code and str(last_code).isdigit():
            next_value = int(last_code) + 1

        while True:
            candidate = str(next_value).zfill(width)
            if not model.objects.filter(**filters, **{field: candidate}).exists():
                return candidate
            next_value += 1


def generate_template_code(company_id: Optional[int]) -> str:
    """Generate template code in format: TMP-YYYYMMDD-XXXXXX."""
    from ticketing.models import TicketTemplate
    
    date_prefix = datetime.now().strftime("%Y%m%d")
    
    filters = {}
    if company_id is not None:
        filters["company_id"] = company_id
    
    with transaction.atomic():
        # Find the last template code for today
        last_code = (
            TicketTemplate.objects.filter(**filters)
            .filter(template_code__startswith=f"TMP-{date_prefix}-")
            .order_by("-template_code")
            .values_list("template_code", flat=True)
            .first()
        )
        
        if last_code:
            # Extract sequence number from last code
            try:
                sequence_part = last_code.split("-")[-1]
                next_sequence = int(sequence_part) + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        # Generate code with 6-digit sequence
        sequence = str(next_sequence).zfill(6)
        candidate = f"TMP-{date_prefix}-{sequence}"
        
        # Ensure uniqueness
        while TicketTemplate.objects.filter(**filters, template_code=candidate).exists():
            next_sequence += 1
            sequence = str(next_sequence).zfill(6)
            candidate = f"TMP-{date_prefix}-{sequence}"
        
        return candidate


def generate_ticket_code(company_id: Optional[int]) -> str:
    """Generate ticket code in format: TKT-YYYYMMDD-XXXXXX."""
    from ticketing.models import Ticket
    
    date_prefix = datetime.now().strftime("%Y%m%d")
    
    filters = {}
    if company_id is not None:
        filters["company_id"] = company_id
    
    with transaction.atomic():
        # Find the last ticket code for today
        last_code = (
            Ticket.objects.filter(**filters)
            .filter(ticket_code__startswith=f"TKT-{date_prefix}-")
            .order_by("-ticket_code")
            .values_list("ticket_code", flat=True)
            .first()
        )
        
        if last_code:
            # Extract sequence number from last code
            try:
                sequence_part = last_code.split("-")[-1]
                next_sequence = int(sequence_part) + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        # Generate code with 6-digit sequence
        sequence = str(next_sequence).zfill(6)
        candidate = f"TKT-{date_prefix}-{sequence}"
        
        # Ensure uniqueness
        while Ticket.objects.filter(**filters, ticket_code=candidate).exists():
            next_sequence += 1
            sequence = str(next_sequence).zfill(6)
            candidate = f"TKT-{date_prefix}-{sequence}"
        
        return candidate


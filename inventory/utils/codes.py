from __future__ import annotations

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

    The code is scoped by company and optional extra filters (e.g. category/warehouse).
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

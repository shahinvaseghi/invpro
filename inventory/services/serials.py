from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Iterable, Sequence, Set

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from inventory.models import ItemSerial, ItemSerialHistory


class SerialTrackingError(Exception):
    """Base exception for serial tracking errors."""


class SerialQuantityMismatch(SerialTrackingError):
    """Raised when document quantity cannot be mapped to discrete serials."""


def _build_serial_code(receipt, sequence: int) -> str:
    prefix = receipt.document_code or "SER"
    return f"{prefix}-{sequence:04d}"


@transaction.atomic
def generate_receipt_serials(receipt, user=None) -> int:
    """Ensure all required serials exist for a receipt."""
    item = getattr(receipt, "item", None)
    if not item or item.has_lot_tracking != 1:
        return 0

    quantity = getattr(receipt, "quantity", None)
    if quantity is None:
        return 0

    try:
        quantity_decimal = Decimal(quantity)
    except (InvalidOperation, TypeError):
        raise SerialQuantityMismatch(_("Quantity must be a number for serialised items."))

    if quantity_decimal != quantity_decimal.to_integral_value():
        raise SerialQuantityMismatch(_("Quantity must be a whole number when tracking serials."))

    required = int(quantity_decimal)
    # Count serials by receipt_document, not ManyToMany (serials may not be linked via M2M yet)
    existing = ItemSerial.objects.filter(
        receipt_document=receipt,
        company=receipt.company,
        is_enabled=1
    ).count()
    if existing >= required:
        return 0

    now = timezone.now()
    created = 0

    for sequence in range(existing + 1, required + 1):
        # Find a unique serial_code by incrementing sequence if needed
        max_attempts = 100  # Prevent infinite loop
        attempt = 0
        current_sequence = sequence
        
        while attempt < max_attempts:
            serial_code = _build_serial_code(receipt, current_sequence)
            
            # Check if serial_code already exists
            if not ItemSerial.objects.filter(serial_code=serial_code).exists():
                break  # Found unique serial_code
            
            # Try next sequence
            current_sequence += 1
            attempt += 1
        
        if attempt >= max_attempts:
            # Could not find unique serial_code after max attempts
            raise SerialTrackingError(_("Could not generate unique serial code after %(attempts)s attempts.") % {'attempts': max_attempts})
        
        serial = ItemSerial.objects.create(
            company=receipt.company,
            item=item,
            item_code=receipt.item_code,
            serial_code=serial_code,
            receipt_document=receipt,
            receipt_document_code=receipt.document_code,
            current_status=ItemSerial.Status.AVAILABLE,
            current_warehouse=receipt.warehouse,
            current_warehouse_code=receipt.warehouse_code,
            last_moved_at=now,
            created_by=user,
            edited_by=user,
        )
        # Also add to ManyToMany relationship if receipt has serials field
        if hasattr(receipt, 'serials'):
            receipt.serials.add(serial)
        ItemSerialHistory.objects.create(
            company=receipt.company,
            item=item,
            item_code=receipt.item_code,
            serial=serial,
            event_type=ItemSerialHistory.EventType.CREATED,
            event_at=now,
            to_status=serial.current_status,
            to_warehouse_code=serial.current_warehouse_code,
            created_by=user,
            edited_by=user,
        )
        created += 1

    return created


def sync_issue_serials(issue, previous_serial_ids: Sequence[int], user=None) -> None:
    """Reserve or release serials for an issue before finalisation."""
    previous_ids = set(previous_serial_ids or [])
    if not hasattr(issue, "serials"):
        return

    item = getattr(issue, "item", None)
    if not item or item.has_lot_tracking != 1:
        if previous_ids:
            _release_serials(previous_ids, issue, user=user)
        return

    current_ids = set(issue.serials.values_list("id", flat=True))
    added = current_ids - previous_ids
    removed = previous_ids - current_ids

    if removed:
        _release_serials(removed, issue, user=user)
    if added:
        _reserve_serials(added, issue, user=user)


def finalize_issue_serials(issue, user=None) -> None:
    """Update serials when an issue document is locked."""
    if not hasattr(issue, "serials"):
        return

    item = getattr(issue, "item", None)
    if not item or item.has_lot_tracking != 1:
        return

    serial_ids = list(issue.serials.values_list("id", flat=True))
    if not serial_ids:
        return

    final_status = _determine_final_status(issue)
    now = timezone.now()

    with transaction.atomic():
        serials = (
            ItemSerial.objects.select_for_update()
            .filter(id__in=serial_ids)
            .order_by("serial_code")
        )
        for serial in serials:
            old_status = serial.current_status
            old_warehouse_code = serial.current_warehouse_code
            old_company_unit_code = serial.current_company_unit_code

            serial.current_status = final_status
            serial.current_document_type = issue.__class__.__name__
            serial.current_document_id = issue.pk
            serial.current_document_code = issue.document_code
            serial.current_warehouse = None
            serial.current_warehouse_code = ""

            department_unit = getattr(issue, "department_unit", None)
            if final_status == ItemSerial.Status.CONSUMED and department_unit:
                serial.current_company_unit = department_unit
                serial.current_company_unit_code = department_unit.public_code
            elif final_status == ItemSerial.Status.ISSUED and department_unit:
                serial.current_company_unit = department_unit
                serial.current_company_unit_code = department_unit.public_code
            else:
                serial.current_company_unit = None
                serial.current_company_unit_code = ""

            serial.last_moved_at = now
            serial.edited_by = user
            serial.save(
                update_fields=[
                    "current_status",
                    "current_document_type",
                    "current_document_id",
                    "current_document_code",
                    "current_warehouse",
                    "current_warehouse_code",
                    "current_company_unit",
                    "current_company_unit_code",
                    "last_moved_at",
                    "edited_by",
                ]
            )

            ItemSerialHistory.objects.create(
                company=serial.company,
                item=serial.item,
                item_code=serial.item_code,
                serial=serial,
                event_type=_history_event_for_status(final_status),
                event_at=now,
                from_status=old_status,
                to_status=serial.current_status,
                reference_document_type=serial.current_document_type,
                reference_document_code=serial.current_document_code,
                reference_document_id=serial.current_document_id,
                from_warehouse_code=old_warehouse_code,
                to_warehouse_code=serial.current_warehouse_code,
                from_company_unit_code=old_company_unit_code,
                to_company_unit_code=serial.current_company_unit_code,
                created_by=user,
                edited_by=user,
            )


@transaction.atomic
def _reserve_serials(serial_ids: Iterable[int], issue, user=None) -> None:
    now = timezone.now()
    serials = (
        ItemSerial.objects.select_for_update()
        .filter(id__in=list(serial_ids))
        .order_by("serial_code")
    )

    for serial in serials:
        old_status = serial.current_status
        old_warehouse_code = serial.current_warehouse_code
        old_company_unit_code = serial.current_company_unit_code

        serial.current_status = ItemSerial.Status.RESERVED
        serial.current_document_type = issue.__class__.__name__
        serial.current_document_id = issue.pk
        serial.current_document_code = issue.document_code
        serial.current_warehouse = getattr(issue, "warehouse", None)
        serial.current_warehouse_code = getattr(issue, "warehouse_code", "")

        department_unit = getattr(issue, "department_unit", None)
        if department_unit:
            serial.current_company_unit = department_unit
            serial.current_company_unit_code = department_unit.public_code
        else:
            serial.current_company_unit = None
            serial.current_company_unit_code = ""

        serial.last_moved_at = now
        serial.edited_by = user
        serial.save(
            update_fields=[
                "current_status",
                "current_document_type",
                "current_document_id",
                "current_document_code",
                "current_warehouse",
                "current_warehouse_code",
                "current_company_unit",
                "current_company_unit_code",
                "last_moved_at",
                "edited_by",
            ]
        )

        ItemSerialHistory.objects.create(
            company=serial.company,
            item=serial.item,
            item_code=serial.item_code,
            serial=serial,
            event_type=ItemSerialHistory.EventType.RESERVED,
            event_at=now,
            from_status=old_status,
            to_status=serial.current_status,
            reference_document_type=serial.current_document_type,
            reference_document_code=serial.current_document_code,
            reference_document_id=serial.current_document_id,
            from_warehouse_code=old_warehouse_code,
            to_warehouse_code=serial.current_warehouse_code,
            from_company_unit_code=old_company_unit_code,
            to_company_unit_code=serial.current_company_unit_code,
            created_by=user,
            edited_by=user,
        )


@transaction.atomic
def _release_serials(serial_ids: Iterable[int], issue, user=None) -> None:
    if not serial_ids:
        return

    now = timezone.now()
    serials = (
        ItemSerial.objects.select_for_update()
        .filter(id__in=list(serial_ids))
        .order_by("serial_code")
    )

    for serial in serials:
        old_status = serial.current_status
        old_warehouse_code = serial.current_warehouse_code
        old_company_unit_code = serial.current_company_unit_code

        serial.current_status = ItemSerial.Status.AVAILABLE
        serial.current_document_type = ""
        serial.current_document_id = None
        serial.current_document_code = ""
        serial.current_warehouse = getattr(issue, "warehouse", serial.current_warehouse)
        serial.current_warehouse_code = getattr(issue, "warehouse_code", serial.current_warehouse_code)
        serial.current_company_unit = None
        serial.current_company_unit_code = ""
        serial.last_moved_at = now
        serial.edited_by = user
        serial.save(
            update_fields=[
                "current_status",
                "current_document_type",
                "current_document_id",
                "current_document_code",
                "current_warehouse",
                "current_warehouse_code",
                "current_company_unit",
                "current_company_unit_code",
                "last_moved_at",
                "edited_by",
            ]
        )

        ItemSerialHistory.objects.create(
            company=serial.company,
            item=serial.item,
            item_code=serial.item_code,
            serial=serial,
            event_type=ItemSerialHistory.EventType.RELEASED,
            event_at=now,
            from_status=old_status,
            to_status=serial.current_status,
            reference_document_type=issue.__class__.__name__,
            reference_document_code=getattr(issue, "document_code", ""),
            reference_document_id=getattr(issue, "pk", None),
            from_warehouse_code=old_warehouse_code,
            to_warehouse_code=serial.current_warehouse_code,
            from_company_unit_code=old_company_unit_code,
            to_company_unit_code=serial.current_company_unit_code,
            created_by=user,
            edited_by=user,
        )


def _determine_final_status(issue) -> str:
    name = issue.__class__.__name__
    if name == "IssueConsumption":
        return ItemSerial.Status.CONSUMED
    return ItemSerial.Status.ISSUED


def _history_event_for_status(status: str) -> str:
    if status == ItemSerial.Status.CONSUMED:
        return ItemSerialHistory.EventType.CONSUMED
    if status == ItemSerial.Status.RETURNED:
        return ItemSerialHistory.EventType.RETURNED
    return ItemSerialHistory.EventType.ISSUED


# ============================================================================
# Line-based Serial Management (Multi-line support)
# ============================================================================

@transaction.atomic
def generate_receipt_line_serials(receipt_line, user=None) -> int:
    """Ensure all required serials exist for a receipt line."""
    item = getattr(receipt_line, "item", None)
    if not item or item.has_lot_tracking != 1:
        return 0

    quantity = getattr(receipt_line, "quantity", None)
    if quantity is None:
        return 0

    try:
        quantity_decimal = Decimal(quantity)
    except (InvalidOperation, TypeError):
        raise SerialQuantityMismatch(_("Quantity must be a number for serialised items."))

    if quantity_decimal != quantity_decimal.to_integral_value():
        raise SerialQuantityMismatch(_("Quantity must be a whole number when tracking serials."))

    required = int(quantity_decimal)
    # Count serials by receipt_line_reference, not ManyToMany (serials may not be linked via M2M yet)
    line_reference = f"{receipt_line.__class__.__name__}:{receipt_line.pk}"
    existing = ItemSerial.objects.filter(
        receipt_line_reference=line_reference,
        company=receipt_line.company,
        is_enabled=1
    ).count()
    if existing >= required:
        return 0

    now = timezone.now()
    created = 0
    document = receipt_line.document

    for sequence in range(existing + 1, required + 1):
        # Find a unique serial_code by incrementing sequence if needed
        max_attempts = 100  # Prevent infinite loop
        attempt = 0
        current_sequence = sequence
        
        while attempt < max_attempts:
            serial_code = _build_serial_code_for_line(receipt_line, current_sequence)
            
            # Check if serial_code already exists
            if not ItemSerial.objects.filter(serial_code=serial_code).exists():
                break  # Found unique serial_code
            
            # Try next sequence
            current_sequence += 1
            attempt += 1
        
        if attempt >= max_attempts:
            # Could not find unique serial_code after max attempts
            raise SerialTrackingError(_("Could not generate unique serial code after %(attempts)s attempts.") % {'attempts': max_attempts})
        
        serial = ItemSerial.objects.create(
            company=receipt_line.company,
            item=item,
            item_code=receipt_line.item_code,
            serial_code=serial_code,
            receipt_document=document,
            receipt_document_code=document.document_code,
            receipt_line_reference=f"{receipt_line.__class__.__name__}:{receipt_line.pk}",
            current_status=ItemSerial.Status.AVAILABLE,
            current_warehouse=receipt_line.warehouse,
            current_warehouse_code=receipt_line.warehouse_code,
            last_moved_at=now,
            created_by=user,
            edited_by=user,
        )
        # Also add to ManyToMany relationship
        receipt_line.serials.add(serial)
        ItemSerialHistory.objects.create(
            company=receipt_line.company,
            item=item,
            item_code=receipt_line.item_code,
            serial=serial,
            event_type=ItemSerialHistory.EventType.CREATED,
            event_at=now,
            to_status=serial.current_status,
            to_warehouse_code=serial.current_warehouse_code,
            created_by=user,
            edited_by=user,
        )
        created += 1

    return created


def _build_serial_code_for_line(line, sequence: int) -> str:
    """Build serial code for a line item."""
    document = line.document
    prefix = document.document_code or "SER"
    return f"{prefix}-L{line.pk}-{sequence:04d}"


def sync_issue_line_serials(line, previous_serial_ids: Sequence[int], user=None) -> None:
    """Reserve or release serials for an issue line before finalisation."""
    previous_ids = set(previous_serial_ids or [])
    if not hasattr(line, "serials"):
        return

    item = getattr(line, "item", None)
    if not item or item.has_lot_tracking != 1:
        if previous_ids:
            _release_line_serials(previous_ids, line, user=user)
        return

    current_ids = set(line.serials.values_list("id", flat=True))
    added = current_ids - previous_ids
    removed = previous_ids - current_ids

    if removed:
        _release_line_serials(removed, line, user=user)
    if added:
        _reserve_line_serials(added, line, user=user)


def finalize_issue_line_serials(line, user=None) -> None:
    """Update serials when an issue line's document is locked."""
    if not hasattr(line, "serials"):
        return

    item = getattr(line, "item", None)
    if not item or item.has_lot_tracking != 1:
        return

    serial_ids = list(line.serials.values_list("id", flat=True))
    if not serial_ids:
        return

    document = line.document
    final_status = _determine_final_status_for_line(line)
    now = timezone.now()

    with transaction.atomic():
        serials = (
            ItemSerial.objects.select_for_update()
            .filter(id__in=serial_ids)
            .order_by("serial_code")
        )
        for serial in serials:
            old_status = serial.current_status
            old_warehouse_code = serial.current_warehouse_code
            old_company_unit_code = serial.current_company_unit_code

            serial.current_status = final_status
            serial.current_document_type = line.__class__.__name__
            serial.current_document_id = line.pk
            serial.current_document_code = document.document_code
            serial.current_warehouse = None
            serial.current_warehouse_code = ""

            department_unit = getattr(document, "department_unit", None)
            if final_status == ItemSerial.Status.CONSUMED and department_unit:
                serial.current_company_unit = department_unit
                serial.current_company_unit_code = department_unit.public_code
            elif final_status == ItemSerial.Status.ISSUED and department_unit:
                serial.current_company_unit = department_unit
                serial.current_company_unit_code = department_unit.public_code
            else:
                serial.current_company_unit = None
                serial.current_company_unit_code = ""

            serial.last_moved_at = now
            serial.edited_by = user
            serial.save(
                update_fields=[
                    "current_status",
                    "current_document_type",
                    "current_document_id",
                    "current_document_code",
                    "current_warehouse",
                    "current_warehouse_code",
                    "current_company_unit",
                    "current_company_unit_code",
                    "last_moved_at",
                    "edited_by",
                ]
            )

            ItemSerialHistory.objects.create(
                company=serial.company,
                item=serial.item,
                item_code=serial.item_code,
                serial=serial,
                event_type=_history_event_for_status(final_status),
                event_at=now,
                from_status=old_status,
                to_status=serial.current_status,
                reference_document_type=serial.current_document_type,
                reference_document_code=serial.current_document_code,
                reference_document_id=serial.current_document_id,
                from_warehouse_code=old_warehouse_code,
                to_warehouse_code=serial.current_warehouse_code,
                from_company_unit_code=old_company_unit_code,
                to_company_unit_code=serial.current_company_unit_code,
                created_by=user,
                edited_by=user,
            )


@transaction.atomic
def _reserve_line_serials(serial_ids: Iterable[int], line, user=None) -> None:
    """Reserve serials for an issue line."""
    now = timezone.now()
    serials = (
        ItemSerial.objects.select_for_update()
        .filter(id__in=list(serial_ids))
        .order_by("serial_code")
    )

    document = line.document
    for serial in serials:
        old_status = serial.current_status
        old_warehouse_code = serial.current_warehouse_code
        old_company_unit_code = serial.current_company_unit_code

        serial.current_status = ItemSerial.Status.RESERVED
        serial.current_document_type = line.__class__.__name__
        serial.current_document_id = line.pk
        serial.current_document_code = document.document_code
        serial.current_warehouse = line.warehouse
        serial.current_warehouse_code = line.warehouse_code

        department_unit = getattr(document, "department_unit", None)
        if department_unit:
            serial.current_company_unit = department_unit
            serial.current_company_unit_code = department_unit.public_code
        else:
            serial.current_company_unit = None
            serial.current_company_unit_code = ""

        serial.last_moved_at = now
        serial.edited_by = user
        serial.save(
            update_fields=[
                "current_status",
                "current_document_type",
                "current_document_id",
                "current_document_code",
                "current_warehouse",
                "current_warehouse_code",
                "current_company_unit",
                "current_company_unit_code",
                "last_moved_at",
                "edited_by",
            ]
        )

        ItemSerialHistory.objects.create(
            company=serial.company,
            item=serial.item,
            item_code=serial.item_code,
            serial=serial,
            event_type=ItemSerialHistory.EventType.RESERVED,
            event_at=now,
            from_status=old_status,
            to_status=serial.current_status,
            reference_document_type=serial.current_document_type,
            reference_document_code=serial.current_document_code,
            reference_document_id=serial.current_document_id,
            from_warehouse_code=old_warehouse_code,
            to_warehouse_code=serial.current_warehouse_code,
            from_company_unit_code=old_company_unit_code,
            to_company_unit_code=serial.current_company_unit_code,
            created_by=user,
            edited_by=user,
        )


@transaction.atomic
def _release_line_serials(serial_ids: Iterable[int], line, user=None) -> None:
    """Release serials from an issue line."""
    if not serial_ids:
        return

    now = timezone.now()
    serials = (
        ItemSerial.objects.select_for_update()
        .filter(id__in=list(serial_ids))
        .order_by("serial_code")
    )

    document = line.document
    for serial in serials:
        old_status = serial.current_status
        old_warehouse_code = serial.current_warehouse_code
        old_company_unit_code = serial.current_company_unit_code

        serial.current_status = ItemSerial.Status.AVAILABLE
        serial.current_document_type = ""
        serial.current_document_id = None
        serial.current_document_code = ""
        serial.current_warehouse = line.warehouse
        serial.current_warehouse_code = line.warehouse_code
        serial.current_company_unit = None
        serial.current_company_unit_code = ""
        serial.last_moved_at = now
        serial.edited_by = user
        serial.save(
            update_fields=[
                "current_status",
                "current_document_type",
                "current_document_id",
                "current_document_code",
                "current_warehouse",
                "current_warehouse_code",
                "current_company_unit",
                "current_company_unit_code",
                "last_moved_at",
                "edited_by",
            ]
        )

        ItemSerialHistory.objects.create(
            company=serial.company,
            item=serial.item,
            item_code=serial.item_code,
            serial=serial,
            event_type=ItemSerialHistory.EventType.RELEASED,
            event_at=now,
            from_status=old_status,
            to_status=serial.current_status,
            reference_document_type=line.__class__.__name__,
            reference_document_code=document.document_code,
            reference_document_id=line.pk,
            from_warehouse_code=old_warehouse_code,
            to_warehouse_code=serial.current_warehouse_code,
            from_company_unit_code=old_company_unit_code,
            to_company_unit_code=serial.current_company_unit_code,
            created_by=user,
            edited_by=user,
        )


def _determine_final_status_for_line(line) -> str:
    """Determine final status for serials in an issue line."""
    line_class = line.__class__.__name__
    if "Consumption" in line_class:
        return ItemSerial.Status.CONSUMED
    return ItemSerial.Status.ISSUED


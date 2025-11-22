"""
API endpoints for inventory module.

All endpoints return JSON responses and require authentication.
"""
from typing import Dict, Any, List, Optional
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from .. import models
from ..forms import UNIT_CHOICES


@login_required
def get_item_allowed_units(request: HttpRequest) -> JsonResponse:
    """API endpoint to get allowed units for an item."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    item_id = request.GET.get('item_id')
    if not item_id:
        return JsonResponse({'error': 'item_id is required'}, status=400)
    
    try:
        company_id = request.session.get('active_company_id')
        if not company_id:
            return JsonResponse({'error': 'No active company'}, status=400)
        
        item = get_object_or_404(models.Item, pk=item_id, company_id=company_id, is_enabled=1)
        
        # Get allowed units
        codes: List[str] = []
        def add(code: str) -> None:
            if code and code not in codes:
                codes.append(code)
        
        # Add default and primary units (always add both, even if same or None)
        add(item.default_unit)
        add(item.primary_unit)
        
        # Add units from ItemUnit conversions
        for unit in models.ItemUnit.objects.filter(item=item, company_id=item.company_id):
            add(unit.from_unit)
            add(unit.to_unit)
        
        # Map to labels
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        units = [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]
        
        return JsonResponse({'units': units, 'default_unit': item.default_unit})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_filtered_categories(request: HttpRequest) -> JsonResponse:
    """API endpoint to get categories that have items of specific type."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        type_id = request.GET.get('type_id')

        # Get categories that have at least one item
        categories_with_items = models.ItemCategory.objects.filter(
            company_id=company_id,
            is_enabled=1
        )
        
        if type_id:
            # Filter to only categories that have items of this type
            categories_with_items = categories_with_items.filter(
                items__type_id=type_id,
                items__is_enabled=1,
                items__company_id=company_id
            ).distinct()
        else:
            # Get all categories that have any items
            categories_with_items = categories_with_items.filter(
                items__is_enabled=1,
                items__company_id=company_id
            ).distinct()

        categories_with_items = categories_with_items.order_by('name')

        categories_data = [
            {'value': str(cat.pk), 'label': cat.name}
            for cat in categories_with_items
        ]

        return JsonResponse({'categories': categories_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_filtered_subcategories(request: HttpRequest) -> JsonResponse:
    """API endpoint to get subcategories filtered by category (and optionally type)."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        type_id = request.GET.get('type_id')
        category_id = request.GET.get('category_id')

        # Base query: all enabled subcategories in company
        subcategories = models.ItemSubcategory.objects.filter(
            company_id=company_id,
            is_enabled=1
        )
        
        # If category_id is provided, filter by category (REQUIRED for form)
        if category_id:
            subcategories = subcategories.filter(category_id=category_id)
        else:
            # If no category_id, return empty (category is required)
            return JsonResponse({'subcategories': []})
        
        # If type_id is provided, optionally filter by type (but don't require items to exist)
        # This is just a hint, not a strict filter
        # We still return all subcategories of the category, even if they don't have items yet
        
        subcategories = subcategories.order_by('name')

        subcategories_data = [
            {'value': str(subcat.pk), 'label': subcat.name}
            for subcat in subcategories
        ]

        return JsonResponse({'subcategories': subcategories_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_filtered_items(request: HttpRequest) -> JsonResponse:
    """API endpoint to get filtered items based on type, category, subcategory."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        type_id = request.GET.get('type_id')
        category_id = request.GET.get('category_id')
        subcategory_id = request.GET.get('subcategory_id')

        # Start with all enabled items in company
        items = models.Item.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).select_related('type', 'category', 'subcategory')

        # Apply filters
        if type_id:
            items = items.filter(type_id=type_id)
        if category_id:
            items = items.filter(category_id=category_id)
        if subcategory_id:
            items = items.filter(subcategory_id=subcategory_id)

        items = items.order_by('item_code')

        items_data = [
            {
                'value': str(item.pk),
                'label': f"{item.item_code} - {item.name}",
                'type_id': str(item.type_id) if item.type_id else '',
                'category_id': str(item.category_id) if item.category_id else '',
                'subcategory_id': str(item.subcategory_id) if item.subcategory_id else '',
            }
            for item in items
        ]

        return JsonResponse({'items': items_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_item_units(request: HttpRequest) -> JsonResponse:
    """API endpoint to get units for an item."""
    item_id = request.GET.get('item_id')
    if not item_id:
        return JsonResponse({'error': 'item_id parameter required'}, status=400)

    try:
        company_id = request.session.get('active_company_id')
        if not company_id:
            return JsonResponse({'error': 'No active company'}, status=400)

        item = get_object_or_404(models.Item, pk=item_id, company_id=company_id, is_enabled=1)

        units_data: List[Dict[str, Any]] = []
        
        # Add primary unit first (base unit)
        if item.primary_unit:
            units_data.append({
                'value': f'base_{item.primary_unit}',  # Special value to indicate base unit
                'label': f"{item.primary_unit} (واحد اصلی)",
                'is_base': True,
                'unit_name': item.primary_unit
            })

        # Get conversion units for this item
        units = models.ItemUnit.objects.filter(
            item=item,
            company_id=company_id,
            is_enabled=1
        ).order_by('to_unit')

        for u in units:
            units_data.append({
                'value': str(u.pk),
                'label': f"{u.to_unit} ({u.from_quantity} {u.from_unit} = {u.to_quantity} {u.to_unit})",
                'is_base': False,
                'unit_name': u.to_unit
            })

        # Include item type_id, category_id, subcategory_id for auto-setting material_type and filters
        response_data: Dict[str, Any] = {
            'units': units_data,
            'item_type_id': item.type_id if item.type else None,
            'item_type_name': item.type.name if item.type else None,
            'category_id': item.category_id if item.category else None,
            'subcategory_id': item.subcategory_id if item.subcategory else None,
        }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_item_allowed_warehouses(request: HttpRequest) -> JsonResponse:
    """API endpoint to get allowed warehouses for an item."""
    item_id = request.GET.get('item_id')
    if not item_id:
        return JsonResponse({'error': 'item_id parameter required'}, status=400)

    try:
        company_id = request.session.get('active_company_id')
        if not company_id:
            return JsonResponse({'error': 'No active company'}, status=400)

        item = get_object_or_404(models.Item, pk=item_id, company_id=company_id, is_enabled=1)

        # Get allowed warehouses
        relations = item.warehouses.select_related('warehouse')
        warehouses = [rel.warehouse for rel in relations if rel.warehouse.is_enabled]

        # IMPORTANT: If no warehouses configured, this means the item CANNOT be received anywhere
        # Only return warehouses if explicitly configured
        # This enforces strict warehouse restrictions

        warehouses_data = [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]

        return JsonResponse({'warehouses': warehouses_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_temporary_receipt_data(request: HttpRequest) -> JsonResponse:
    """API endpoint to get temporary receipt data for auto-filling permanent receipt lines."""
    temporary_receipt_id = request.GET.get('temporary_receipt_id')
    if not temporary_receipt_id:
        return JsonResponse({'error': 'temporary_receipt_id parameter required'}, status=400)

    try:
        company_id = request.session.get('active_company_id')
        if not company_id:
            return JsonResponse({'error': 'No active company'}, status=400)

        temp_receipt = get_object_or_404(
            models.ReceiptTemporary,
            pk=temporary_receipt_id,
            company_id=company_id
        )

        # Return temporary receipt data for auto-filling
        data: Dict[str, Any] = {
            'item_id': temp_receipt.item_id,
            'item_code': temp_receipt.item.item_code,
            'item_name': temp_receipt.item.name,
            'warehouse_id': temp_receipt.warehouse_id,
            'warehouse_code': temp_receipt.warehouse.public_code,
            'warehouse_name': temp_receipt.warehouse.name,
            'quantity': str(temp_receipt.quantity),
            'entered_quantity': str(temp_receipt.entered_quantity) if temp_receipt.entered_quantity else str(temp_receipt.quantity),
            'unit': temp_receipt.unit,
            'entered_unit': temp_receipt.entered_unit if temp_receipt.entered_unit else temp_receipt.unit,
            'supplier_id': temp_receipt.supplier_id if temp_receipt.supplier else None,
            'supplier_code': temp_receipt.supplier.public_code if temp_receipt.supplier else None,
            'supplier_name': temp_receipt.supplier.name if temp_receipt.supplier else None,
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_item_available_serials(request: HttpRequest) -> JsonResponse:
    """API endpoint to get available serial numbers for an item in a warehouse."""
    item_id = request.GET.get('item_id')
    warehouse_id = request.GET.get('warehouse_id')
    
    if not item_id:
        return JsonResponse({'error': 'item_id parameter required'}, status=400)
    
    if not warehouse_id:
        return JsonResponse({'error': 'warehouse_id parameter required'}, status=400)

    try:
        company_id = request.session.get('active_company_id')
        if not company_id:
            return JsonResponse({'error': 'No active company'}, status=400)

        item = get_object_or_404(models.Item, pk=item_id, company_id=company_id, is_enabled=1)
        
        # Check if item has lot tracking enabled
        if item.has_lot_tracking != 1:
            return JsonResponse({'serials': [], 'has_lot_tracking': False})

        warehouse = get_object_or_404(models.Warehouse, pk=warehouse_id, company_id=company_id, is_enabled=1)

        # Get available serials: same company, same item, same warehouse, status AVAILABLE only
        # Exclude RESERVED (already reserved for issues), ISSUED, CONSUMED, DAMAGED, RETURNED serials
        serials = models.ItemSerial.objects.filter(
            company_id=company_id,
            item=item,
            current_warehouse=warehouse,
            current_status=models.ItemSerial.Status.AVAILABLE  # Only show AVAILABLE serials, not RESERVED ones
        ).order_by('serial_code')

        serials_data = [
            {
                'value': str(s.pk),
                'label': s.serial_code,
                'status': s.current_status,
            }
            for s in serials
        ]

        return JsonResponse({
            'serials': serials_data,
            'has_lot_tracking': True,
            'count': len(serials_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def update_serial_secondary_code(request: HttpRequest, serial_id: int) -> JsonResponse:
    """API endpoint to update secondary serial code for a serial."""
    try:
        company_id = request.session.get('active_company_id')
        if not company_id:
            return JsonResponse({'error': 'No active company'}, status=400)
        
        import json
        data = json.loads(request.body)
        secondary_serial_code = data.get('secondary_serial_code', '').strip()
        
        serial = get_object_or_404(
            models.ItemSerial,
            pk=serial_id,
            company_id=company_id,
            is_enabled=1
        )
        
        serial.secondary_serial_code = secondary_serial_code
        serial.save(update_fields=['secondary_serial_code'])
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=500)


@require_http_methods(["GET"])
@login_required
def get_warehouse_work_lines(request: HttpRequest) -> JsonResponse:
    """API endpoint to get work lines for a warehouse."""
    warehouse_id = request.GET.get('warehouse_id')
    
    if not warehouse_id:
        return JsonResponse({'error': 'warehouse_id parameter required'}, status=400)

    try:
        company_id = request.session.get('active_company_id')
        if not company_id:
            return JsonResponse({'error': 'No active company'}, status=400)

        warehouse = get_object_or_404(models.Warehouse, pk=warehouse_id, company_id=company_id, is_enabled=1)

        # Get work lines for this warehouse (from production module)
        from shared.utils.modules import get_work_line_model
        WorkLine = get_work_line_model()
        
        if not WorkLine:
            # If production module is not installed, return empty list
            return JsonResponse({
                'work_lines': [],
                'count': 0
            })
        
        work_lines = WorkLine.objects.filter(
            company_id=company_id,
            warehouse=warehouse,
            is_enabled=1
        ).order_by('name')

        work_lines_data = [
            {
                'value': str(wl.pk),
                'label': f"{wl.public_code} · {wl.name}",
            }
            for wl in work_lines
        ]

        return JsonResponse({
            'work_lines': work_lines_data,
            'count': len(work_lines_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


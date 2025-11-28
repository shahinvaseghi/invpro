"""
API endpoints for inventory module.

All endpoints return JSON responses and require authentication.
"""
import logging
from typing import Dict, Any, List, Optional
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from .. import models
from ..forms import UNIT_CHOICES

logger = logging.getLogger('inventory.views.api')


@login_required
def get_item_allowed_units(request: HttpRequest) -> JsonResponse:
    """API endpoint to get allowed units for an item."""
    logger.info("=" * 80)
    logger.info("get_item_allowed_units: Request received")
    logger.info(f"  User: {request.user.username}")
    logger.info(f"  Method: {request.method}")
    logger.info(f"  GET params: {dict(request.GET)}")
    
    if not request.user.is_authenticated:
        logger.warning("get_item_allowed_units: Unauthorized request")
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    item_id = request.GET.get('item_id')
    logger.info(f"get_item_allowed_units: item_id from request: {item_id}")
    
    if not item_id:
        logger.error("get_item_allowed_units: item_id is missing")
        return JsonResponse({'error': 'item_id is required'}, status=400)
    
    try:
        company_id = request.session.get('active_company_id')
        logger.info(f"get_item_allowed_units: company_id from session: {company_id}")
        
        if not company_id:
            logger.error("get_item_allowed_units: No active company in session")
            return JsonResponse({'error': 'No active company'}, status=400)
        
        # Try to get item - if not found with is_enabled=1, try without is_enabled filter
        # This handles cases where item is in formset initial but might be disabled
        logger.info(f"get_item_allowed_units: Looking for item pk={item_id}, company_id={company_id}, is_enabled=1")
        try:
            item = models.Item.objects.get(pk=item_id, company_id=company_id, is_enabled=1)
            logger.info(f"get_item_allowed_units: Item found (enabled): {item.name} ({item.item_code})")
        except models.Item.DoesNotExist:
            # If item not found with is_enabled=1, try without is_enabled filter
            # This allows loading units/warehouses for items that are in formset initial
            logger.warning(f"get_item_allowed_units: Item not found with is_enabled=1, trying without filter")
            try:
                item = models.Item.objects.get(pk=item_id, company_id=company_id)
                logger.warning(f"get_item_allowed_units: Item found (disabled): {item.name} ({item.item_code}), is_enabled={item.is_enabled}, allowing anyway")
            except models.Item.DoesNotExist:
                logger.error(f"get_item_allowed_units: Item {item_id} not found in company {company_id}")
                return JsonResponse({'error': 'Item not found'}, status=404)
        
        # Get allowed units
        logger.info(f"get_item_allowed_units: Getting allowed units for item {item.name}")
        logger.info(f"  Default unit: {item.default_unit}")
        logger.info(f"  Primary unit: {item.primary_unit}")
        
        codes: List[str] = []
        def add(code: str) -> None:
            if code and code not in codes:
                codes.append(code)
        
        # Add default and primary units (always add both, even if same or None)
        add(item.default_unit)
        add(item.primary_unit)
        
        # Add units from ItemUnit conversions
        item_units = models.ItemUnit.objects.filter(item=item, company_id=item.company_id)
        logger.info(f"get_item_allowed_units: Found {item_units.count()} ItemUnit conversions")
        for unit in item_units:
            logger.info(f"  Conversion: {unit.from_unit} -> {unit.to_unit}")
            add(unit.from_unit)
            add(unit.to_unit)
        
        logger.info(f"get_item_allowed_units: Total unique unit codes: {len(codes)}")
        logger.info(f"  Codes: {codes}")
        
        # Map to labels
        label_map = {value: str(label) for value, label in UNIT_CHOICES}
        units = [{'value': code, 'label': label_map.get(code, code)} for code in codes if code]
        
        logger.info(f"get_item_allowed_units: Returning {len(units)} units")
        for unit in units:
            logger.info(f"  Unit: {unit['value']} -> {unit['label']}")
        
        response_data = {'units': units, 'default_unit': item.default_unit}
        logger.info(f"get_item_allowed_units: Response: {response_data}")
        logger.info("=" * 80)
        
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"get_item_allowed_units: Error: {e}", exc_info=True)
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
    """API endpoint to get filtered items based on type, category, subcategory, and search term."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        from django.db.models import Q
        
        type_id = request.GET.get('type_id')
        category_id = request.GET.get('category_id')
        subcategory_id = request.GET.get('subcategory_id')
        search_term = request.GET.get('search', '').strip()
        # Allow including specific item_id even if user doesn't have permission (for initial data)
        include_item_id = request.GET.get('include_item_id')

        # Start with all enabled items in company
        items = models.Item.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).select_related('type', 'category', 'subcategory')

        # Apply permission filter (own vs all) - but allow superuser to see all
        if not request.user.is_superuser:
            from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
            permissions = get_user_feature_permissions(request.user, company_id)
            can_view_all = has_feature_permission(permissions, 'inventory.master.items', 'view_all', allow_own_scope=False)
            can_view_own = has_feature_permission(permissions, 'inventory.master.items', 'view_own', allow_own_scope=True)
            
            if can_view_all:
                # User can see all items, no filter needed
                pass
            elif can_view_own:
                # User can only see own items
                items = items.filter(created_by=request.user)
            else:
                # User has no view permission, return empty
                items = items.none()
        
        # If include_item_id is provided, include it even if it doesn't match filters
        # This is useful for initial data in formsets (e.g., from purchase requests)
        if include_item_id:
            try:
                include_item = models.Item.objects.get(pk=include_item_id, company_id=company_id)
                if not items.filter(pk=include_item_id).exists():
                    # Add it to queryset using union
                    items = items.union(models.Item.objects.filter(pk=include_item_id))
                    logger.info(f"get_filtered_items: Including item_id={include_item_id} even though it doesn't match filters")
            except models.Item.DoesNotExist:
                pass

        # Apply filters
        if type_id:
            items = items.filter(type_id=type_id)
        if category_id:
            items = items.filter(category_id=category_id)
        if subcategory_id:
            items = items.filter(subcategory_id=subcategory_id)
        
        # Apply search term (optional - can search without filters)
        if search_term:
            items = items.filter(
                Q(name__icontains=search_term) |
                Q(item_code__icontains=search_term) |
                Q(full_item_code__icontains=search_term)
            )

        items = items.order_by('name')

        # Log total count for debugging
        total_count = items.count()
        logger.info(f"get_filtered_items: Found {total_count} items for company {company_id}")

        items_data = [
            {
                'value': str(item.pk),
                'label': f"{item.name} · {item.item_code}",
                'type_id': str(item.type_id) if item.type_id else '',
                'category_id': str(item.category_id) if item.category_id else '',
                'subcategory_id': str(item.subcategory_id) if item.subcategory_id else '',
            }
            for item in items
        ]

        logger.info(f"get_filtered_items: Returning {len(items_data)} items")
        return JsonResponse({'items': items_data, 'total_count': total_count})
    except Exception as e:
        logger.error(f"get_filtered_items: Error: {e}", exc_info=True)
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
    logger.info("=" * 80)
    logger.info("get_item_allowed_warehouses: Request received")
    logger.info(f"  User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    logger.info(f"  Method: {request.method}")
    logger.info(f"  GET params: {dict(request.GET)}")
    
    item_id = request.GET.get('item_id')
    logger.info(f"get_item_allowed_warehouses: item_id from request: {item_id}")
    
    if not item_id:
        logger.error("get_item_allowed_warehouses: item_id is missing")
        return JsonResponse({'error': 'item_id parameter required'}, status=400)

    try:
        company_id = request.session.get('active_company_id')
        logger.info(f"get_item_allowed_warehouses: company_id from session: {company_id}")
        
        if not company_id:
            logger.error("get_item_allowed_warehouses: No active company in session")
            return JsonResponse({'error': 'No active company'}, status=400)

        # Try to get item - if not found with is_enabled=1, try without is_enabled filter
        # This handles cases where item is in formset initial but might be disabled
        logger.info(f"get_item_allowed_warehouses: Looking for item pk={item_id}, company_id={company_id}, is_enabled=1")
        try:
            item = models.Item.objects.get(pk=item_id, company_id=company_id, is_enabled=1)
            logger.info(f"get_item_allowed_warehouses: Item found (enabled): {item.name} ({item.item_code})")
        except models.Item.DoesNotExist:
            # If item not found with is_enabled=1, try without is_enabled filter
            # This allows loading warehouses for items that are in formset initial
            logger.warning(f"get_item_allowed_warehouses: Item not found with is_enabled=1, trying without filter")
            try:
                item = models.Item.objects.get(pk=item_id, company_id=company_id)
                logger.warning(f"get_item_allowed_warehouses: Item found (disabled): {item.name} ({item.item_code}), is_enabled={item.is_enabled}, allowing anyway")
            except models.Item.DoesNotExist:
                logger.error(f"get_item_allowed_warehouses: Item {item_id} not found in company {company_id}")
                return JsonResponse({'error': 'Item not found'}, status=404)

        # Get allowed warehouses
        logger.info(f"get_item_allowed_warehouses: Getting allowed warehouses for item {item.name}")
        relations = item.warehouses.select_related('warehouse').filter(is_enabled=1)
        logger.info(f"get_item_allowed_warehouses: Found {relations.count()} ItemWarehouse relations")
        
        warehouses = [rel.warehouse for rel in relations if rel.warehouse and rel.warehouse.is_enabled == 1]
        logger.info(f"get_item_allowed_warehouses: Filtered to {len(warehouses)} enabled warehouses")
        
        for w in warehouses:
            logger.info(f"  Warehouse: {w.public_code} - {w.name} (pk={w.pk})")

        # IMPORTANT: If no warehouses configured, this means the item CANNOT be received anywhere
        # Only return warehouses if explicitly configured
        # This enforces strict warehouse restrictions

        warehouses_data = [
            {'value': str(w.pk), 'label': f"{w.public_code} - {w.name}"}
            for w in warehouses
        ]
        
        logger.info(f"get_item_allowed_warehouses: Returning {len(warehouses_data)} warehouses")
        for w_data in warehouses_data:
            logger.info(f"  Warehouse data: {w_data}")

        response_data = {'warehouses': warehouses_data}
        logger.info(f"get_item_allowed_warehouses: Response: {response_data}")
        logger.info("=" * 80)
        
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"get_item_allowed_warehouses: Error: {e}", exc_info=True)
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

        # Get only QC-approved lines from temporary receipt
        # Only include lines that are approved (is_qc_approved=1) and have approved quantity
        approved_lines = temp_receipt.lines.filter(
            is_enabled=1,
            is_qc_approved=1,
            qc_approved_quantity__isnull=False
        )
        
        if not approved_lines.exists():
            # Log for debugging
            logger.warning(
                f"Temporary receipt {temp_receipt.document_code} (ID: {temp_receipt.pk}, "
                f"Company: {temp_receipt.company_id}) has no QC-approved lines. "
                f"This receipt cannot be converted to permanent receipt."
            )
            return JsonResponse({
                'error': 'Temporary receipt has no approved lines',
                'message': _('رسید موقت انتخاب شده هیچ خط تایید شده‌ای ندارد. لطفاً ابتدا خطوط را در بخش QC تایید کنید.')
            }, status=400)

        # For backward compatibility, return first approved line data as main data
        # And include all approved lines in a 'lines' array
        first_line = approved_lines.first()
        
        # Supplier info is stored on the temporary receipt header
        supplier = temp_receipt.supplier
        supplier_id = supplier.pk if supplier else None
        supplier_code = supplier.public_code if supplier else None
        supplier_name = supplier.name if supplier else None

        # Return temporary receipt data for auto-filling
        # Use QC-approved quantities instead of original quantities
        # Main data (first line for backward compatibility)
        data: Dict[str, Any] = {
            'item_id': first_line.item_id,
            'item_code': first_line.item.item_code,
            'item_name': first_line.item.name,
            'warehouse_id': first_line.warehouse_id,
            'warehouse_code': first_line.warehouse.public_code,
            'warehouse_name': first_line.warehouse.name,
            'quantity': str(first_line.qc_approved_quantity),  # Use approved quantity
            'entered_quantity': str(first_line.qc_approved_quantity),  # Use approved quantity
            'unit': first_line.unit,
            'entered_unit': first_line.entered_unit if first_line.entered_unit else first_line.unit,
            'supplier_id': supplier_id,
            'supplier_code': supplier_code,
            'supplier_name': supplier_name,
            # Include all approved lines for multi-line support
            'lines': [
                {
                    'item_id': line.item_id,
                    'item_code': line.item.item_code,
                    'item_name': line.item.name,
                    'warehouse_id': line.warehouse_id,
                    'warehouse_code': line.warehouse.public_code,
                    'warehouse_name': line.warehouse.name,
                    'quantity': str(line.qc_approved_quantity),  # Use approved quantity
                    'entered_quantity': str(line.qc_approved_quantity),  # Use approved quantity
                    'unit': line.unit,
                    'entered_unit': line.entered_unit if line.entered_unit else line.unit,
                    'supplier_id': supplier_id,
                    'supplier_code': supplier_code,
                    'supplier_name': supplier_name,
                }
                for line in approved_lines
            ],
        }

        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in get_temporary_receipt_data: {e}", exc_info=True)
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


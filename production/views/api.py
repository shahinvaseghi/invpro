"""
API endpoints for production module.
"""
import logging
from typing import Dict, Any, List
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from production.models import BOM, BOMMaterial, ProductOrder, Process
from production.utils.transfer import (
    get_available_operations_for_order,
    is_full_order_transferred,
)

logger = logging.getLogger('production.views.api')


@require_http_methods(["GET"])
@login_required
def get_bom_materials(request: HttpRequest, bom_id: int) -> JsonResponse:
    """API endpoint to get materials for a specific BOM."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        bom = get_object_or_404(
            BOM,
            pk=bom_id,
            company_id=company_id,
            is_enabled=1,
        )

        # Get all enabled materials for this BOM
        bom_materials = BOMMaterial.objects.filter(
            bom=bom,
            is_enabled=1,
        ).select_related('material_item', 'material_type').order_by('line_number')

        materials_data = [
            {
                'id': str(bm.pk),
                'material_item_id': str(bm.material_item_id),
                'material_item_code': bm.material_item_code,
                'material_item_name': bm.material_item.name if bm.material_item else '',
                'quantity_per_unit': str(bm.quantity_per_unit),
                'unit': bm.unit,
                'line_number': bm.line_number,
                'description': bm.description or '',
            }
            for bm in bom_materials
        ]

        return JsonResponse({
            'materials': materials_data,
            'bom_code': bom.bom_code,
            'finished_item_name': bom.finished_item.name if bom.finished_item else '',
        })
    except Exception as e:
        logger.error(f"Error in get_bom_materials: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_order_operations(request: HttpRequest, order_id: int) -> JsonResponse:
    """API endpoint to get available operations for a product order."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        # Get is_scrap_replacement from query params (optional)
        include_scrap_replacement = request.GET.get('include_scrap_replacement', 'false').lower() == 'true'
        
        order = get_object_or_404(
            ProductOrder,
            pk=order_id,
            company_id=company_id,
            is_enabled=1,
        )

        # Check if order has process
        if not order.process:
            return JsonResponse({
                'operations': [],
                'has_process': False,
                'message': _('This order does not have an associated process.'),
            })

        # Get available operations
        available_operations = get_available_operations_for_order(
            order,
            include_scrap_replacement=include_scrap_replacement
        )

        # Check if full order is transferred
        is_full_transferred = is_full_order_transferred(
            order,
            exclude_scrap_replacement=not include_scrap_replacement
        )

        return JsonResponse({
            'operations': available_operations,
            'has_process': True,
            'is_full_transferred': is_full_transferred,
            'order_code': order.order_code,
            'process_code': order.process.process_code if order.process else None,
        })
    except Exception as e:
        logger.error(f"Error in get_order_operations: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_process_details(request: HttpRequest, process_id: int) -> JsonResponse:
    """API endpoint to get details for a specific process (BOM, finished item, etc.)."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        process = get_object_or_404(
            Process,
            pk=process_id,
            company_id=company_id,
            is_enabled=1,
        )

        return JsonResponse({
            'process_code': process.process_code,
            'finished_item_id': process.finished_item_id,
            'finished_item_code': process.finished_item_code,
            'finished_item_name': process.finished_item.name if process.finished_item else '',
            'bom_id': process.bom_id,
            'bom_code': process.bom_code if process.bom else None,
            'revision': process.revision or '',
        })
    except Exception as e:
        logger.error(f"Error in get_process_details: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def get_process_bom_materials(request: HttpRequest, process_id: int) -> JsonResponse:
    """API endpoint to get BOM materials for a specific process."""
    company_id = request.session.get('active_company_id')
    if not company_id:
        return JsonResponse({'error': 'No active company'}, status=400)

    try:
        process = get_object_or_404(
            Process,
            pk=process_id,
            company_id=company_id,
            is_enabled=1,
        )

        if not process.bom:
            return JsonResponse({
                'materials': [],
                'bom_code': None,
                'finished_item_name': process.finished_item.name if process.finished_item else '',
                'message': _('This process does not have an associated BOM.'),
            })

        # Get all enabled materials for this BOM
        bom_materials = BOMMaterial.objects.filter(
            bom=process.bom,
            is_enabled=1,
        ).select_related('material_item', 'material_type').order_by('line_number')

        materials_data = [
            {
                'id': str(bm.pk),
                'material_item_id': str(bm.material_item_id),
                'material_item_code': bm.material_item_code,
                'material_item_name': bm.material_item.name if bm.material_item else '',
                'quantity_per_unit': str(bm.quantity_per_unit),
                'unit': bm.unit,
                'line_number': bm.line_number,
                'description': bm.description or '',
            }
            for bm in bom_materials
        ]

        return JsonResponse({
            'materials': materials_data,
            'bom_code': process.bom.bom_code,
            'finished_item_name': process.bom.finished_item.name if process.bom.finished_item else '',
        })
    except Exception as e:
        logger.error(f"Error in get_process_bom_materials: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


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
from production.models import BOM, BOMMaterial

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


"""
Debug views for ticketing module.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger('ticketing.debug')


@csrf_exempt
@require_http_methods(["POST"])
def debug_log_view(request):
    """Receive debug logs from browser and print them to server console."""
    try:
        data = json.loads(request.body)
        level = data.get('level', 'LOG')
        message = data.get('message', '')
        log_data = data.get('data', {})
        url = data.get('url', '')
        timestamp = data.get('timestamp', '')
        
        log_message = f"[{timestamp}] [{level}] {message}"
        if url:
            log_message += f" | URL: {url}"
        if log_data:
            log_message += f" | Data: {json.dumps(log_data, indent=2)}"
        
        # Print to console (terminal)
        print(log_message)
        
        # Also log to Django logger
        if level == 'ERROR':
            logger.error(log_message)
        else:
            logger.info(log_message)
        
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        print(f"[ERROR] Failed to process debug log: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


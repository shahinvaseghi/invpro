# Generated migration to migrate existing PurchaseRequest data to PurchaseRequestLine

from django.db import migrations


def migrate_purchase_requests_to_lines(apps, schema_editor):
    """Migrate existing PurchaseRequest items to PurchaseRequestLine."""
    PurchaseRequest = apps.get_model('inventory', 'PurchaseRequest')
    PurchaseRequestLine = apps.get_model('inventory', 'PurchaseRequestLine')
    
    for request in PurchaseRequest.objects.all():
        # Only migrate if item exists (for backward compatibility)
        if request.item_id:
            PurchaseRequestLine.objects.create(
                document=request,
                company=request.company,
                item=request.item,
                item_code=request.item_code or '',
                unit=request.unit or 'EA',
                quantity_requested=request.quantity_requested or 0,
                quantity_fulfilled=request.quantity_fulfilled or 0,
                line_notes='',
                sort_order=0,
                created_by=request.requested_by,
                is_enabled=request.is_enabled,
            )


def reverse_migrate(apps, schema_editor):
    """Reverse migration - not implemented as data loss would occur."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0029_add_purchase_request_line'),
    ]

    operations = [
        migrations.RunPython(migrate_purchase_requests_to_lines, reverse_migrate),
    ]


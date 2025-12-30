# Generated manually to link existing warehouse transfers to their TransferToLine

from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def link_warehouse_transfers_to_transfers(apps, schema_editor):
    """Link existing warehouse transfers to their corresponding TransferToLine."""
    IssueWarehouseTransfer = apps.get_model('inventory', 'IssueWarehouseTransfer')
    TransferToLine = apps.get_model('production', 'TransferToLine')
    
    # Find warehouse transfers without production_transfer
    wts_without_transfer = IssueWarehouseTransfer.objects.filter(production_transfer__isnull=True)
    
    for wt in wts_without_transfer:
        # Search for TransferToLine that were approved around the same time
        date_range_start = wt.document_date - timedelta(days=1)
        date_range_end = wt.document_date + timedelta(days=1)
        
        transfers = TransferToLine.objects.filter(
            status='approved',
            is_locked=1,
            transfer_date__gte=date_range_start,
            transfer_date__lte=date_range_end,
            company_id=wt.company_id
        ).order_by('-locked_at')
        
        if transfers.exists():
            # Use the first transfer found
            transfer = transfers.first()
            wt.production_transfer = transfer
            wt.production_transfer_code = transfer.transfer_code
            wt.save()


def reverse_link_warehouse_transfers(apps, schema_editor):
    """Reverse migration - unlink warehouse transfers."""
    IssueWarehouseTransfer = apps.get_model('inventory', 'IssueWarehouseTransfer')
    IssueWarehouseTransfer.objects.filter(production_transfer__isnull=False).update(
        production_transfer=None,
        production_transfer_code=''
    )


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0043_add_production_transfer_to_warehouse_transfer'),
        ('production', '0030_change_destination_work_center_to_workline'),
    ]

    operations = [
        migrations.RunPython(link_warehouse_transfers_to_transfers, reverse_link_warehouse_transfers),
    ]


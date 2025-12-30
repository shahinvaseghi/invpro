"""
Script to check if warehouse transfers are being created for transfer to line requests.

Run this in Django shell:
    python manage.py shell
    exec(open('check_warehouse_transfers.py').read())
"""

from inventory.models import IssueWarehouseTransfer
from production.models import TransferToLine

# Get all approved transfers
approved_transfers = TransferToLine.objects.filter(
    status='approved',
    is_locked=1
).order_by('-id')[:10]

print(f"Found {approved_transfers.count()} approved transfers")
print("\n" + "="*80)

for transfer in approved_transfers:
    print(f"\nTransfer: {transfer.transfer_code}")
    print(f"  Order: {transfer.order_code}")
    print(f"  Status: {transfer.status}")
    print(f"  Locked: {transfer.is_locked}")
    print(f"  Created by: {transfer.created_by}")
    
    # Check if warehouse transfer exists
    warehouse_transfers = IssueWarehouseTransfer.objects.filter(
        company_id=transfer.company_id,
        created_by=transfer.created_by,
        document_date=transfer.transfer_date
    ).order_by('-id')
    
    # Try to find by date proximity (within same day)
    matching_transfers = []
    for wt in warehouse_transfers:
        if wt.document_date == transfer.transfer_date:
            matching_transfers.append(wt)
    
    if matching_transfers:
        print(f"  ✓ Found {len(matching_transfers)} warehouse transfer(s):")
        for wt in matching_transfers[:3]:  # Show first 3
            print(f"    - {wt.document_code} (ID: {wt.id}, Date: {wt.document_date})")
    else:
        print(f"  ✗ No warehouse transfer found")
        print(f"    (Checked {warehouse_transfers.count()} transfers with same company/user/date)")

print("\n" + "="*80)
print("\nTo check all warehouse transfers:")
print("  IssueWarehouseTransfer.objects.filter(company_id=YOUR_COMPANY_ID).count()")


#!/usr/bin/env python
"""
Check if warehouse transfer was created for a specific transfer to line request.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from production.models import TransferToLine
from inventory.models import IssueWarehouseTransfer

# Check transfer TR00000001
transfer_code = 'TR00000001'
transfer = TransferToLine.objects.filter(transfer_code=transfer_code).first()

if not transfer:
    print(f"Transfer {transfer_code} not found!")
    exit(1)

print(f"Transfer: {transfer.transfer_code}")
print(f"  Status: {transfer.status}")
print(f"  Locked: {transfer.is_locked}")
print(f"  Company ID: {transfer.company_id}")
print(f"  Created by: {transfer.created_by}")
print(f"  Date: {transfer.transfer_date}")
print(f"  Items count: {transfer.items.filter(is_enabled=1).count()}")

print("\n" + "="*80)
print("Checking warehouse transfers...")

# Check all warehouse transfers for this company
all_wts = IssueWarehouseTransfer.objects.filter(company_id=transfer.company_id).order_by('-id')[:10]
print(f"\nTotal warehouse transfers for company {transfer.company_id}: {IssueWarehouseTransfer.objects.filter(company_id=transfer.company_id).count()}")

# Check transfers created around the same time
recent_wts = IssueWarehouseTransfer.objects.filter(
    company_id=transfer.company_id,
    document_date=transfer.transfer_date
).order_by('-id')[:5]

print(f"\nWarehouse transfers with same date ({transfer.transfer_date}): {recent_wts.count()}")
for wt in recent_wts:
    print(f"  - {wt.document_code} (ID: {wt.id}, Created by: {wt.created_by}, Date: {wt.document_date}, Lines: {wt.lines.count()})")

# Check transfers created by the same user
user_wts = IssueWarehouseTransfer.objects.filter(
    company_id=transfer.company_id,
    created_by=transfer.created_by
).order_by('-id')[:5]

print(f"\nWarehouse transfers created by {transfer.created_by}: {user_wts.count()}")
for wt in user_wts:
    print(f"  - {wt.document_code} (ID: {wt.id}, Date: {wt.document_date}, Lines: {wt.lines.count()})")


#!/usr/bin/env python
"""
Check why warehouse transfer is not showing in the list.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventory.models import IssueWarehouseTransfer
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='admin')

print('Checking warehouse transfers...')
print('='*80)

all_wts = IssueWarehouseTransfer.objects.filter(company_id=1)
print(f'\nAll warehouse transfers (company 1): {all_wts.count()}')

own_wts = IssueWarehouseTransfer.objects.filter(company_id=1, created_by=admin)
print(f'Own warehouse transfers (created by admin): {own_wts.count()}')

print('\nWarehouse transfers:')
for wt in all_wts:
    print(f'  - {wt.document_code}')
    print(f'    Created by: {wt.created_by} (ID: {wt.created_by_id})')
    print(f'    Is enabled: {wt.is_enabled}')
    print(f'    Is locked: {wt.is_locked}')
    print(f'    Company ID: {wt.company_id}')
    print(f'    Lines count: {wt.lines.count()}')
    print()





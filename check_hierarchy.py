#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/home/shahin/invproj')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

from accounting.models import TafsiliAccountHierarchy, SubAccountTafsiliTypeRelation

print("=== اتصالات سلسله مراتبی تفصیلی ===")
hierarchies = TafsiliAccountHierarchy.objects.all()
print(f"تعداد روابط سلسله مراتبی: {hierarchies.count()}")

if hierarchies.exists():
    for h in hierarchies:
        print(f"{h.parent_account.account_code} ({h.parent_account.account_name}) -> {h.child_account.account_code} ({h.child_account.account_name})")
else:
    print("هیچ رابطه سلسله مراتبی تعریف نشده است.")

print("\n=== اتصالات معین به نوع تفصیلی ===")
relations = SubAccountTafsiliTypeRelation.objects.all()
print(f"تعداد روابط معین به نوع تفصیلی: {relations.count()}")

if relations.exists():
    for r in relations[:20]:  # نمایش حداکثر ۲۰ مورد اول
        print(f"{r.sub_account.account_code} ({r.sub_account.account_name}) - سطح {r.level} - {r.tafsili_type.name}")
else:
    print("هیچ رابطه معین به نوع تفصیلی تعریف نشده است.")

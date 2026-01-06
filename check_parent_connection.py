#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/home/shahin/invproj')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

from accounting.models import Account, SubAccountTafsiliLevel1Relation

print("=== بررسی اتصال حساب والد به معین ===")
print()

# پیدا کردن حساب والد (کد 5)
parent_account = Account.objects.filter(account_code='5').first()
if not parent_account:
    print("❌ حساب والد (کد 5) یافت نشد")
    sys.exit(1)

print(f"حساب والد: {parent_account.account_code} ({parent_account.account_name})")
print(f"سطح: {parent_account.account_level}, سطح تفصیلی: {parent_account.tafsili_level}")
print()

# پیدا کردن حساب معین بانک‌ها (کد 1102)
sub_account = Account.objects.filter(account_code='1102').first()
if not sub_account:
    print("❌ حساب معین بانک‌ها (کد 1102) یافت نشد")
    sys.exit(1)

print(f"حساب معین: {sub_account.account_code} ({sub_account.account_name})")
print(f"سطح: {sub_account.account_level}")
print()

# بررسی اتصال سطح ۱
level1_relations = SubAccountTafsiliLevel1Relation.objects.filter(
    sub_account=sub_account,
    tafsili_level1_account=parent_account
)

print("=== بررسی اتصال سطح ۱ ===")
if level1_relations.exists():
    print("✅ حساب والد به حساب معین بانک‌ها متصل است")
    for rel in level1_relations:
        print(f"   اتصال: {rel.sub_account.account_code} -> {rel.tafsili_level1_account.account_code}")
        print(f"   اصلی: {'بله' if rel.is_primary else 'خیر'}")
        print(f"   یادداشت: {rel.notes or 'ندارد'}")
else:
    print("❌ حساب والد به حساب معین بانک‌ها متصل نیست")

print()
print("=== همه اتصالات سطح ۱ حساب معین بانک‌ها ===")
all_level1_relations = SubAccountTafsiliLevel1Relation.objects.filter(sub_account=sub_account)
if all_level1_relations.exists():
    for rel in all_level1_relations:
        print(f"   {rel.sub_account.account_code} -> {rel.tafsili_level1_account.account_code} ({rel.tafsili_level1_account.account_name})")
else:
    print("   هیچ اتصالی وجود ندارد")

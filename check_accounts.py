#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/home/shahin/invproj')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setup Django
django.setup()

from accounting.models import Account, TafsiliAccountHierarchy

print("=== اطلاعات حساب‌های مورد نظر ===")
accounts = Account.objects.filter(account_code__in=['5', '110201'])
for acc in accounts:
    parent_code = acc.parent_account.account_code if acc.parent_account else None
    print(f"کد: {acc.account_code}, نام: {acc.account_name}, سطح: {acc.account_level}, تفصیلی سطح: {acc.tafsili_level}, والد: {parent_code}")

print("\n=== بررسی hierarchy ===")
hierarchies = TafsiliAccountHierarchy.objects.all()
for h in hierarchies:
    print(f"والد: {h.parent_account.account_code} ({h.parent_account.account_name}) -> فرزند: {h.child_account.account_code} ({h.child_account.account_name})")

print("\n=== بررسی اینکه آیا حساب 110201 در درختچه نمایش داده می‌شود ===")
# پیدا کردن حساب 110201
child_account = Account.objects.filter(account_code='110201').first()
if child_account:
    print(f"حساب فرزند پیدا شد: {child_account.account_code} ({child_account.account_name})")

    # بررسی اینکه آیا این حساب در ساختار درختچه حساب‌ها قرار می‌گیرد
    # طبق کد API، حساب‌های تفصیلی از طریق SubAccountTafsiliLevel1Relation یا استفاده در اسناد پیدا می‌شوند
    from accounting.models import SubAccountTafsiliLevel1Relation

    # بررسی اتصال مستقیم سطح ۱
    level1_relations = SubAccountTafsiliLevel1Relation.objects.filter(tafsili_level1_account=child_account)
    if level1_relations.exists():
        print("این حساب از طریق SubAccountTafsiliLevel1Relation متصل است")
        for rel in level1_relations:
            print(f"  متصل به معین: {rel.sub_account.account_code} ({rel.sub_account.account_name})")
    else:
        print("این حساب از طریق SubAccountTafsiliLevel1Relation متصل نیست")

    # بررسی استفاده در اسناد
    document_usage = child_account.document_lines_as_tafsili_2.exists() or child_account.document_lines_as_tafsili_3.exists()
    print(f"استفاده در اسناد: {'بله' if document_usage else 'خیر'}")

    # نتیجه‌گیری
    if level1_relations.exists() or document_usage:
        print("✅ این حساب در درختچه حساب‌ها نمایش داده می‌شود")
    else:
        print("❌ این حساب در درختچه حساب‌ها نمایش داده نمی‌شود")

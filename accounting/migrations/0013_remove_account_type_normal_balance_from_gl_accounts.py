# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0012_warehouseexpensedocumentline_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_type',
            field=models.CharField(
                blank=True,
                choices=[('ASSET', 'Asset'), ('LIABILITY', 'Liability'), ('EQUITY', 'Equity'), ('REVENUE', 'Revenue'), ('EXPENSE', 'Expense')],
                help_text='نوع حساب (در سند حسابداری تعریف می‌شود)',
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='account',
            name='normal_balance',
            field=models.CharField(
                blank=True,
                choices=[('DEBIT', 'Debit'), ('CREDIT', 'Credit')],
                help_text='طرف تراز مورد انتظار (در سند حسابداری تعریف می‌شود)',
                max_length=10,
                null=True,
            ),
        ),
    ]


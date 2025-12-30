# Generated manually on 2025-12-02

from django.conf import settings
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0014_add_editable_model_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0008_add_party_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreasuryAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('enabled_at', models.DateTimeField(blank=True, null=True)),
                ('disabled_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('company_code', models.CharField(blank=True, editable=False, max_length=8)),
                ('account_type', models.CharField(choices=[('cash', 'نقدی'), ('bank', 'بانکی')], help_text='Type of treasury account', max_length=20)),
                ('account_name', models.CharField(help_text='نام حساب نقدی/بانکی', max_length=200)),
                ('account_name_en', models.CharField(blank=True, help_text='نام حساب (انگلیسی)', max_length=200)),
                ('bank_name', models.CharField(blank=True, help_text='نام بانک (برای حساب‌های بانکی)', max_length=200)),
                ('account_number', models.CharField(blank=True, help_text='شماره حساب', max_length=50)),
                ('branch_name', models.CharField(blank=True, help_text='نام شعبه', max_length=200)),
                ('branch_code', models.CharField(blank=True, help_text='کد شعبه', max_length=50)),
                ('iban', models.CharField(blank=True, help_text='شماره شبا (IBAN)', max_length=34)),
                ('currency', models.CharField(default='IRR', help_text='واحد پول', max_length=3)),
                ('initial_balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='موجودی اولیه', max_digits=18)),
                ('notes', models.TextField(blank=True, help_text='توضیحات و یادداشت‌ها')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('disabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_disabled', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_edited', to=settings.AUTH_USER_MODEL)),
                ('enabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_enabled', to=settings.AUTH_USER_MODEL)),
                ('gl_account', models.ForeignKey(blank=True, help_text='حساب کل (خودکار از معین)', limit_choices_to={'account_level': 1}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='treasury_accounts_as_gl', to='accounting.account')),
                ('sub_account', models.ForeignKey(blank=True, help_text='معین حساب (خودکار از تفصیلی)', limit_choices_to={'account_level': 2}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='treasury_accounts_as_sub', to='accounting.account')),
                ('tafsili_account', models.ForeignKey(help_text='تفصیلی حساب', limit_choices_to={'account_level': 3}, on_delete=django.db.models.deletion.PROTECT, related_name='treasury_accounts', to='accounting.account')),
            ],
            options={
                'verbose_name': 'حساب نقدی/بانکی',
                'verbose_name_plural': 'حساب\u200cهای نقدی و بانکی',
                'ordering': ('company', 'account_type', 'sort_order', 'account_name'),
            },
        ),
        migrations.AddConstraint(
            model_name='treasuryaccount',
            constraint=models.UniqueConstraint(fields=('company', 'tafsili_account'), name='accounting_treasury_account_tafsili_unique'),
        ),
    ]


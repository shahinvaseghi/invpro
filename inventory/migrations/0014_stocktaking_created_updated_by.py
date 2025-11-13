from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0006_issueconsignment_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktakingdeficit',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='inventory_stocktakingdeficit_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stocktakingdeficit',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='inventory_stocktakingdeficit_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stocktakingrecord',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='inventory_stocktakingrecord_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stocktakingrecord',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='inventory_stocktakingrecord_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stocktakingsurplus',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='inventory_stocktakingsurplus_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stocktakingsurplus',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='inventory_stocktakingsurplus_updated', to=settings.AUTH_USER_MODEL),
        ),
    ]


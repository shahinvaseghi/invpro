# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0024_bom_editing_by_bom_editing_session_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfertoline',
            name='is_scrap_replacement',
            field=models.PositiveSmallIntegerField(
                choices=[(0, 'Disabled'), (1, 'Enabled')],
                default=0,
                help_text='Whether this transfer is for replacing scrap/waste materials',
                verbose_name='Scrap Replacement',
            ),
        ),
    ]


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0005_remove_accesslevel_activated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='company_units',
            field=models.ManyToManyField(blank=True, related_name='people', to='shared.companyunit'),
        ),
    ]


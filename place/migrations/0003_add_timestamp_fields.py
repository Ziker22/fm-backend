# Generated manually
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0002_alter_place_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='place',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

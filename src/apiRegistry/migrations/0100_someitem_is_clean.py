from django.db import migrations, models

class Migration(migrations.Migration):
    """Migration to add ``is_clean`` field to ``Organization``"""

    dependencies = [
        ('apiRegistry', '0006_auto_20210909_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='is_clean',
            field=models.BooleanField(default=True)
        )
    ]
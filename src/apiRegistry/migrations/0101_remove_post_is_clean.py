from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiRegistry', '0100_someitem_is_clean'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='is_clean',
        ),
    ]
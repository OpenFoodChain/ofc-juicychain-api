import pytest
import os
import django
from django.conf import settings
from dotenv import load_dotenv
from django_test_migrations.migrator import Migrator
from django_test_migrations.plan import all_migrations, nodes_to_tuples

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

def test_run_migration():
    migrator = Migrator(database='default')

    old_state = migrator.apply_initial_migration(('apiRegistry', '0006_auto_20210909_1018'))
    Organization = old_state.apps.get_model('apiRegistry', 'Organization')

    Organization.objects.create(name='a')
    assert len(Organization._meta.get_fields()) == 8

    new_state = migrator.apply_tested_migration(('apiRegistry', '0100_someitem_is_clean'))
    Organization = new_state.apps.get_model('apiRegistry', 'Organization')

    assert len(Organization._meta.get_fields()) == 9

    migrator.reset()

"""def test_reset_migration():
    migrator = Migrator(database='default')

    new_state = migrator.apply_tested_migration(('apiRegistry', '0100_someitem_is_clean'))
    Organization = new_state.apps.get_model('apiRegistry', 'Organization')

    assert len(Organization._meta.get_fields()) == 9

    migrator.reset()"""
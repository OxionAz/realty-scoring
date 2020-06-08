import fnmatch
import importlib
import os

from peewee import DoesNotExist

from realty_scoring.database import db
from realty_scoring.database.models import public_schema
from realty_scoring.database.models.public_schema import MigrationHistory
from realty_scoring.utils.data import DatabaseManager


def do_migrate():
    print("# Updating database structure...")

    migration_modules = []
    try:
        migration_modules = sorted(map(lambda fn: fn[:-3],
                                       fnmatch.filter(os.listdir("realty_scoring/database/migrations"), "????_*.py")))
    except FileNotFoundError:
        print(". missing /migrations folder")
        pass

    first_run = not MigrationHistory.table_exists()

    # create tables
    for model_class in DatabaseManager.get_model_classes(public_schema):
        try:
            if not model_class.table_exists():
                print(". create table for {} model".format(model_class.__name__))
                model_class.create_table()
        except (AssertionError, KeyError, TypeError):
            pass

    if first_run:
        # create fake migrations
        with db.atomic():
            for migration_module in migration_modules:
                MigrationHistory.create(migration=migration_module)
    else:
        # run real migrations
        try:
            last_migration = (MigrationHistory
                              .select()
                              .order_by(MigrationHistory.id.desc())
                              .limit(1)
                              .get())
            migration_modules = filter(lambda fn: fn > last_migration.migration,
                                       migration_modules)
        except DoesNotExist:
            pass

        for migration_module in migration_modules:
            print(". run migration %s" % migration_module)
            with db.atomic():
                importlib.import_module("realty_scoring.database.migrations.%s" % migration_module)
                MigrationHistory.create(migration=migration_module)


if __name__ == "__main__":
    do_migrate()

"""
Simple rules of migrations

1. Migration files are regular python files. Their name is "special":
   XXXX_migration_name.py
   XXXX: a numeric ID right padded with 0s
   migration_name: nomen est omen

2. Sample migrations

   No migration script is needed when new model is created. It's required only when
   existing strucure should be modified.

2a. A simple one using peewee migration methods

    from playhouse.migrate import migrate
    from .. import db_migrator

    migrate(
        db_migrator.drop_column("<model_name>", "<field_name>"),
        db_migrator.add_column("<model_name>", "<field_name>", TextField(default="{}")),
    )

2b. When you have to create custom SQL migration script

    from .. import db

    db.execute_sql("ALTER TABLE <table_name> DROP COLUMN IF EXISTS <column_name>")

   For documentation and additional samples see
   https://peewee.readthedocs.io/en/latest/peewee/playhouse.html#schema-migrations

3. Running migration

   $ ./bin/migrate command

   The script will load scripts from the migrations folder and
   runs the new ones in the order what their prefix number suggests.

"""

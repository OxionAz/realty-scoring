from playhouse.db_url import connect
from playhouse.migrate import PostgresqlMigrator

from realty_scoring import settings

db = connect(settings.DATABASE_URL, register_hstore=False, autorollback=True, max_connections=32, stale_timeout=60)
db_migrator = PostgresqlMigrator(db)

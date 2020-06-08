import logging

import psycopg2

from peewee import Model
from playhouse.db_url import parseresult_to_dict
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger()


class DatabaseManager:

    @staticmethod
    def get_model_classes(module, exclude_models=()):
        model_classes = []
        for attr in dir(module):
            try:
                model_class = getattr(module, attr)
                if issubclass(model_class, Model) \
                        and model_class.__module__ == module.__name__ \
                        and model_class not in exclude_models:
                    model_classes.append(model_class)
            except (AttributeError, KeyError, TypeError):
                pass
        return model_classes

    @staticmethod
    def create_test_db_url(db_url):
        parsed_url = urlparse(db_url)._asdict()
        parsed_url["path"] += "_test"
        return urlunparse(parsed_url.values())

    def __init__(self, db_url):
        parsed_url = urlparse(db_url)
        if "postgres" not in parsed_url.scheme:
            raise ValueError("TestDatabase works only with PostgreSQL")
        self._db_params = parseresult_to_dict(parsed_url)
        self._db_name = self._db_params["database"]

    def _connect(self):
        try:
            # connection without database parameter works only if
            # the current user has a default database
            conn = psycopg2.connect(host=self._db_params["host"],
                                    user=self._db_params["user"],
                                    password=self._db_params["password"])
        except psycopg2.OperationalError:
            # if connect failed and trying to create a test database
            # then use the original database for connecting
            if self._db_name.endswith("_test"):
                db_for_connection = self._db_name[:-5]
                conn = psycopg2.connect(host=self._db_params["host"],
                                        user=self._db_params["user"],
                                        password=self._db_params["password"],
                                        database=db_for_connection)
            elif self._db_name:
                conn = psycopg2.connect(host=self._db_params["host"],
                                        user=self._db_params["user"],
                                        password=self._db_params["password"],
                                        database=self._db_params["database"])
            else:
                raise
        return conn

    @staticmethod
    def create_schema(db_url, schema, drop_if_exists=True):
        parsed_url = urlparse(db_url)
        if "postgres" not in parsed_url.scheme:
            raise ValueError("TestDatabase works only with PostgreSQL")
        db_params = parseresult_to_dict(parsed_url)

        with psycopg2.connect(host=db_params["host"],
                              user=db_params["user"],
                              password=db_params["password"],
                              database=db_params["database"]) as conn:
            with conn.cursor() as cursor:
                if drop_if_exists:
                    cursor.execute("DROP SCHEMA IF EXISTS {} CASCADE;".format(schema))
                cursor.execute("CREATE SCHEMA {};".format(schema))

    def create_database(self, drop_if_exists=True):
        try:
            conn = self._connect()
            conn.autocommit = True
            cur = conn.cursor()
            if drop_if_exists:
                cur.execute("DROP DATABASE IF EXISTS {};".format(self._db_name))
            cur.execute("CREATE DATABASE {};".format(self._db_name))
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def drop_database(self):
        try:
            conn = self._connect()
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("DROP DATABASE IF EXISTS {};".format(self._db_name))
        finally:
            try:
                conn.close()
            except Exception:
                pass

    @property
    def connect_params(self):
        return self._db_params

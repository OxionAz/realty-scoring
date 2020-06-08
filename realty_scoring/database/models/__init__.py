from peewee import Model

from realty_scoring.database import db


class BaseModel(Model):

    class Meta:
        database = db

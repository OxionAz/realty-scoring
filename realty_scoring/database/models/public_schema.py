from datetime import datetime

from playhouse.postgres_ext import IntegerField, CharField, DateTimeField, BooleanField, FloatField

from realty_scoring.database.models import BaseModel


class MigrationHistory(BaseModel):

    migration = CharField()
    applied_at = DateTimeField(default=datetime.utcnow)


class Sale(BaseModel):

    id = IntegerField(primary_key=True)
    city = CharField(null=True)
    district = CharField(null=True)
    address = CharField(null=True)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    floor = IntegerField(null=True)
    number_of_floors = IntegerField(null=True)
    number_of_rooms = IntegerField(null=True)
    kitchen_area = FloatField(null=True)
    living_area = FloatField(null=True)
    total_area = FloatField(null=True)
    walling = CharField(null=True)
    price_amount = FloatField(null=True)
    price_currency = CharField(null=True)
    seller = CharField(null=True)
    resale = BooleanField(null=True)
    image = CharField(null=True)
    url = CharField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

import logging

import pandas as pd

from realty_scoring.database import db
from realty_scoring.database.models.public_schema import Sale

logger = logging.getLogger('realty_scoring')


class Scraper:

    BASE_URL_SALE = 'https://pk.api.onliner.by/search/apartments'
    BASE_URL_RENT = 'https://ak.api.onliner.by/search/apartments'

    WALL_TYPE = {
        'panel': 'walling[]=panel',
        'brick': 'walling[]=brick',
        'monolith': 'walling[]=monolith',
        'block': 'walling[]=block'
    }
    NUMBER_OF_ROOMS = [
        'number_of_rooms[]=1',
        'number_of_rooms[]=2',
        'number_of_rooms[]=3',
        'number_of_rooms[]=4&number_of_rooms[]=5&number_of_rooms[]=6'
    ]
    RESALE = [
        'resale=true',
        'resale=false'
    ]
    CITY_BOUNDS = {
        'Брест': 'bounds[lb][lat]=51.941725203142&bounds[lb][long]=23.492889404297&bounds[rt][lat]=52.234528294214&bounds[rt][long]=23.927536010742&v=0.34283289161620756',
        'Гродно': 'bounds[lb][lat]=53.538267122397&bounds[lb][long]=23.629531860352&bounds[rt][lat]=53.820517109806&bounds[rt][long]=24.064178466797&v=0.8871158894104579',
        'Витебск': 'bounds[lb][lat]=55.085834940707&bounds[lb][long]=29.979629516602&bounds[rt][lat]=55.357648391381&bounds[rt][long]=30.414276123047&v=0.9685201294207474',
        'Могилев': 'bounds[lb][lat]=53.74261986683&bounds[lb][long]=30.132064819336&bounds[rt][lat]=54.023503252809&bounds[rt][long]=30.566711425781&v=0.7011001502804747',
        'Гомель': 'bounds[lb][lat]=52.302600726968&bounds[lb][long]=30.732192993164&bounds[rt][lat]=52.593037841157&bounds[rt][long]=31.166839599609&v=0.782118379013744',
        'Минск': 'bounds[lb][lat]=53.820922446131&bounds[lb][long]=27.344970703125&bounds[rt][lat]=53.97547425743&bounds[rt][long]=27.77961730957&v=0.14873064332447494'
    }

    @staticmethod
    def scrap():
        try:
            raw_frame = pd.read_csv('full_apartments_frame.csv')
            with db.atomic():
                Sale.truncate_table()
                for row in raw_frame.to_dict(orient="row"):
                    Sale.create(**row)
        except Exception as e:
            logger.exception(str(e))

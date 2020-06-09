import logging

import pandas as pd
import re
import requests
import time

from lxml import etree

from realty_scoring.database import db
from realty_scoring.database.models.public_schema import Sale

logger = logging.getLogger('realty_scoring')


def get_cleaned_district(address):
    try:
        return re.findall(r'(\w+ район),', address)[0]
    except Exception:
        return None


def get_district(lat, lon):
    result = requests.get('https://www.openstreetmap.org/geocoder/search_osm_nominatim_reverse?lat={}&latlon_digits=true&lon={}&zoom=19'.format(lat, lon))
    tree = etree.fromstring(result.content)
    district = tree.xpath('//a')
    district = district[0]
    return district.text


class Scraper:

    BASE_URL = 'https://pk.api.onliner.by/search/apartments'

    WALL_FILTER = {
        'panel': 'walling[]=panel',
        'brick': 'walling[]=brick',
        'monolith': 'walling[]=monolith',
        'block': 'walling[]=block'
    }
    ROOMS_FILTER = [
        'number_of_rooms[]=1',
        'number_of_rooms[]=2',
        'number_of_rooms[]=3',
        'number_of_rooms[]=4&number_of_rooms[]=5&number_of_rooms[]=6'
    ]
    RESALE_FILTER = [
        'resale=true',
        'resale=false'
    ]
    CITY_FILTER = {
        'Брест': 'bounds[lb][lat]=51.941725203142&bounds[lb][long]=23.492889404297&bounds[rt][lat]=52.234528294214&bounds[rt][long]=23.927536010742&v=0.34283289161620756',
        'Гродно': 'bounds[lb][lat]=53.538267122397&bounds[lb][long]=23.629531860352&bounds[rt][lat]=53.820517109806&bounds[rt][long]=24.064178466797&v=0.8871158894104579',
        'Витебск': 'bounds[lb][lat]=55.085834940707&bounds[lb][long]=29.979629516602&bounds[rt][lat]=55.357648391381&bounds[rt][long]=30.414276123047&v=0.9685201294207474',
        'Могилев': 'bounds[lb][lat]=53.74261986683&bounds[lb][long]=30.132064819336&bounds[rt][lat]=54.023503252809&bounds[rt][long]=30.566711425781&v=0.7011001502804747',
        'Гомель': 'bounds[lb][lat]=52.302600726968&bounds[lb][long]=30.732192993164&bounds[rt][lat]=52.593037841157&bounds[rt][long]=31.166839599609&v=0.782118379013744',
        'Минск': 'bounds[lb][lat]=53.820922446131&bounds[lb][long]=27.344970703125&bounds[rt][lat]=53.97547425743&bounds[rt][long]=27.77961730957&v=0.14873064332447494'
    }

    @staticmethod
    def scrap():
        logger.info('--- Scrapping started ---')

        scrapped_frame = pd.DataFrame()

        logger.info('requesting train data...')
        for c, b in Scraper.CITY_FILTER.items():
            for n in Scraper.ROOMS_FILTER:
                for r in Scraper.RESALE_FILTER:
                    for w, t in Scraper.WALL_FILTER.items():
                        base_url = '{}?{}'.format(Scraper.BASE_URL, '&'.join([b, n, r, t]))
                        result = requests.get(base_url)
                        result = result.json()
                        if result['apartments']:
                            print(base_url)
                            pages = result['page']['last'] + 1
                            for p in range(1, pages):
                                time.sleep(0.5)
                                result = requests.get('{}&page={}'.format(base_url, p))
                                query_json = result.json()
                                for item in query_json['apartments']:
                                    row = {'id': item['id'],
                                           'city': c,
                                           'address': item['location']['address'],
                                           'latitude': item['location']['latitude'],
                                           'longitude': item['location']['longitude'],
                                           'kitchen_area': item['area']['kitchen'],
                                           'living_area': item['area']['living'],
                                           'total_area': item['area']['total'],
                                           'walling': w,
                                           'floor': item['floor'],
                                           'number_of_floors': item['number_of_floors'],
                                           'number_of_rooms': item['number_of_rooms'],
                                           'price_amount': item['price']['amount'],
                                           'price_currency': item['price']['currency'],
                                           'seller': item['seller']['type'],
                                           'resale': item['resale'],
                                           'image': item['photo'],
                                           'url': item['url'],
                                           'created_at': item['created_at']}
                                    scrapped_frame = scrapped_frame.append(row, ignore_index=True)

        logger.info('enriching scrapped data...')
        scrapped_frame['district'] = scrapped_frame.apply(lambda x: get_district(x['latitude'], x['longitude']), axis=1)
        scrapped_frame['district'] = scrapped_frame['district'].apply(get_cleaned_district)

        logger.info('saving scrapped data...')
        with db.atomic():
            Sale.truncate_table()
            for row in scrapped_frame.to_dict(orient="row"):
                Sale.create(**row)

        logger.info('--- Scrapping ended ---')

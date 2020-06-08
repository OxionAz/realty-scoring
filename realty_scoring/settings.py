import os
import json

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')  # development|staging|production

DATABASE_URL = os.environ.get('DATABASE_URL')

CITIES_DICT = json.loads(os.environ.get('CITIES_DICT', '{}'))
DISTRICTS_DICT = json.loads(os.environ.get('DISTRICTS_DICT', '{}'))
WALL_TYPE_DICT = json.loads(os.environ.get('WALL_TYPE_DICT', '{}'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s(%(lineno)d) %(message)s'
        },
        'simple': {
            'format': '%(levelname)s - %(name)s - %(message)s'
        },
    },
    'filters': {},
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'realty_scoring': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'peewee': {
            'level': 'ERROR',
            'propagate': False,
            'handlers': ['console']
        }
    }
}

try:
    from settings_local import *
except ImportError as e:
    print(e)

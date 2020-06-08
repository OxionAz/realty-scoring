from logging import config

import falcon

from realty_scoring import settings
from realty_scoring.middlewares import error_serializer
from realty_scoring.urls import setup_endpoints

config.dictConfig(settings.LOGGING)


application = falcon.API()
application.set_error_serializer(error_serializer)
setup_endpoints(application)

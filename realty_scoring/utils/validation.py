import logging

import falcon

from realty_scoring import settings

logger = logging.getLogger('realty_scoring')


class RequestValidator:

    @staticmethod
    def check_score_data(req, resp, resource, params):
        try:
            params["to_predict"] = [[
                settings.CITIES_DICT[req.params['city']],
                settings.DISTRICTS_DICT[req.params['city']][req.params['district']],
                float(req.params['total_area']),
                int(req.params['number_of_rooms']),
                settings.WALL_TYPE_DICT[req.params['walling']],
                bool(req.params['resale'])
            ]]
        except KeyError as e:
            logger.warning(str(e))
            raise falcon.HTTPBadRequest(title="Bad request", description=str(e))
        except Exception as e:
            logger.exception(str(e))
            raise falcon.HTTPInternalServerError(title="Something went wrong", description=str(e))

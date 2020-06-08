import falcon

from realty_scoring.control.scoring import SaleScorer
from realty_scoring.utils.validation import RequestValidator


class ScoreApi:

    @falcon.before(RequestValidator.check_score_data)
    def on_get(self, req, resp, to_predict):
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200
        resp.media = SaleScorer.predict(to_predict)

import logging

import os
import joblib

logger = logging.getLogger('realty_scoring')


def load_model(name):
    try:
        return joblib.load(os.getcwd() + '/ml_models/' + name)
    except Exception as e:
        logger.exception(str(e))
        return None


class SaleScorer:

    _model = load_model('sale_deep.model')

    @classmethod
    def predict(cls, to_predict):
        prediction = cls._model.predict(to_predict)
        return prediction[0]

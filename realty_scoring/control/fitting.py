import logging

import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
from sklearn.neural_network import MLPRegressor

from realty_scoring import settings
from realty_scoring.database.models.public_schema import Sale

logger = logging.getLogger('realty_scoring')


def load_train_data():
    try:
        query = Sale.select(Sale.city,
                            Sale.district,
                            Sale.total_area,
                            Sale.number_of_rooms,
                            Sale.walling,
                            Sale.resale,
                            Sale.price_amount)
        return pd.DataFrame(list(query.dicts()))
    except Exception as e:
        logger.exception(str(e))
        return None


def save_model(model, name):
    models_folder = os.getcwd() + '/ml_models/'
    if not os.path.exists(models_folder):
        os.makedirs(models_folder)
    joblib.dump(model, models_folder + name)


class ModelBuilder:

    @staticmethod
    def build():
        logger.info('--- Building started ---')

        logger.info('loading train data...')
        train_frame = load_train_data()

        logger.info('data cleaning and validation...')
        train_frame['district'] = train_frame[['city', 'district']].apply(
            lambda x: settings.DISTRICTS_DICT.get(x['city'], {}).get(x['district']), axis=1)
        train_frame['city'] = train_frame['city'].apply(settings.CITIES_DICT.get)
        train_frame['number_of_rooms'] = train_frame['number_of_rooms'].apply(int)
        train_frame['walling'] = train_frame['walling'].apply(settings.WALL_TYPE_DICT.get)
        train_frame['resale'] = train_frame['resale'].apply(bool)
        train_frame['price_amount'] = train_frame['price_amount'].apply(float)
        train_frame = train_frame.dropna()
        train_frame['district'] = train_frame['district'].apply(int)

        logger.info('fitting model...')
        x = train_frame.drop(columns=['price_amount']).to_numpy()
        y = train_frame['price_amount'].to_numpy()
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.01, random_state=12)

        deep_model = MLPRegressor(hidden_layer_sizes=(12, 12, 12, 12, 12, 6),
                                  random_state=3, max_iter=1000,
                                  solver='adam', activation='relu',
                                  verbose=True).fit(x_train, y_train)
        print(f'Model score: {deep_model.score(x_test, y_test)}')

        print('Variable importance:')
        r = permutation_importance(deep_model, x_test, y_test,
                                   n_repeats=30,
                                   random_state=0)
        for i in r.importances_mean.argsort()[::-1]:
            if r.importances_mean[i] - 2 * r.importances_std[i] > 0:
                print(f"{train_frame.columns[i]:<8}"
                      f"{r.importances_mean[i]:.3f}"
                      f" +/- {r.importances_std[i]:.3f}")

        logger.info('saving model...')
        save_model(deep_model, 'sale_deep.model')

        logger.info('--- Building ended ---')

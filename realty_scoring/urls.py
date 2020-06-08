from realty_scoring.views.score_api import ScoreApi


def setup_endpoints(app):
    app.add_route("/api/v1/realty-scorer/score/sale", ScoreApi())

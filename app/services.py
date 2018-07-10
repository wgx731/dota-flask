from datetime import date
from app.models import Score


def get_player_scores(player_id_list):
    player_list = Score.query\
            .filter(Score.score_date == date.today())\
            .filter(Score.account_id.in_(player_id_list))\
            .order_by(Score.overall_score.desc())\
            .all()
    if len(player_list) > 0:
        return player_list
    # TODO: add fetch from API here
    return player_list

from datetime import date
from app.models import Score


def accept_json(request):
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


def sort_score_list(score_list, sort_by):
    if sort_by == 'W':
        return sorted(score_list, key=lambda s: s.week_score, reverse=True)
    elif sort_by == 'M':
        return sorted(score_list, key=lambda s: s.month_score, reverse=True)
    elif sort_by == 'Y':
        return sorted(score_list, key=lambda s: s.year_score, reverse=True)
    else:
        return sorted(score_list, key=lambda s: s.overall_score, reverse=True)


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

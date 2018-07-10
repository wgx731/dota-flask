from datetime import date
from app.models import MatchScore


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
    elif sort_by == 'C':
        return sorted(score_list, key=lambda s: s.overall_count, reverse=True)
    else:
        return sorted(score_list, key=lambda s: s.overall_score, reverse=True)


def get_player_match_scores(player_id_list):
    player_list = MatchScore.query\
            .filter(MatchScore.score_date == date.today())\
            .filter(MatchScore.account_id.in_(player_id_list))\
            .order_by(MatchScore.overall_score.desc())\
            .all()
    if len(player_list) > 0:
        return player_list
    # TODO: add fetch from API here
    return player_list


def get_player_match_score_by_id(player_id):
    return MatchScore.query.filter(MatchScore.account_id == player_id).first()

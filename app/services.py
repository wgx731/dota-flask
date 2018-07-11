import json
from datetime import date

from app import app, db
from app.models import Player, MatchScore
from app.apis import get_dota_open_api


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


def get_match_score_from_json(
        player_json,
        week_json,
        month_json,
        year_json,
        overall_json
):
    p_dict = json.loads(player_json)
    w_dict = json.loads(week_json)
    m_dict = json.loads(month_json)
    y_dict = json.loads(year_json)
    o_dict = json.loads(overall_json)
    player = Player(
        account_id=p_dict['profile']['account_id'],
        steam_id=p_dict['profile']['steamid'],
        personaname=p_dict['profile']['personaname'],
        name=p_dict['profile']['name'],
        avatar=p_dict['profile']['avatar']
    )
    score = MatchScore(
        player=player
    )
    if w_dict['lose'] == 0:
        score.week_score = 0.0
    else:
        score.week_score = w_dict['win'] / w_dict['lose']
    if m_dict['lose'] == 0:
        score.month_score = 0.0
    else:
        score.month_score = m_dict['win'] / m_dict['lose']
    if y_dict['lose'] == 0:
        score.year_score = 0.0
    else:
        score.year_score = y_dict['win'] / y_dict['lose']
    if o_dict['lose'] == 0:
        score.overall_score = 0.0
    else:
        score.overall_score = o_dict['win'] / o_dict['lose']
    score.overall_count = o_dict['win'] + o_dict['lose']
    return score


def fetch_player_match_score(player_id):
    player_json = get_dota_open_api('api/players/{}'.format(player_id))
    week_json = get_dota_open_api('api/players/{}/wl'.format(player_id), params={'date': 7})
    month_json = get_dota_open_api('api/players/{}/wl'.format(player_id), params={'date': 30})
    year_json = get_dota_open_api('api/players/{}/wl'.format(player_id), params={'date': 365})
    overall_json = get_dota_open_api('api/players/{}/wl'.format(player_id))
    if player_json is None:
        app.logger.warning("Missing player json for {}".format(player_id))
        return None
    if week_json is None:
        app.logger.warning("Missing week json for {}".format(player_id))
        return None
    if month_json is None:
        app.logger.warning("Missing month json for {}".format(player_id))
        return None
    if year_json is None:
        app.logger.warning("Missing year json for {}".format(player_id))
        return None
    if overall_json is None:
        app.logger.warning("Missing overall json for {}".format(player_id))
        return None
    return get_match_score_from_json(
        player_json,
        week_json,
        month_json,
        year_json,
        overall_json
    )


def get_player_match_scores(player_id_list):
    player_list = MatchScore.query \
        .filter(MatchScore.score_date == date.today()) \
        .filter(MatchScore.account_id.in_(player_id_list)) \
        .order_by(MatchScore.overall_score.desc()) \
        .all()
    if len(player_list) == len(player_id_list):
        return player_list
    # only fetch from API if id is not in database
    player_id_list = set(player_id_list) - set([p.account_id for p in player_list])
    app.logger.info("load from API for " + str(player_id_list))
    for player_id in player_id_list:
        score = fetch_player_match_score(player_id)
        if score is None:
            app.logger.warning("Missing score data for {}".format(player_id))
            continue
        # save to db
        db.session.add(score)
        db.session.commit()
        # add to list
        player_list.append(score)
    return player_list


def get_player_match_score_by_id(player_id):
    player = MatchScore.query.filter(MatchScore.account_id == player_id).first()
    if player is None:
        app.logger.info("load from API for " + str(player_id))
        score = fetch_player_match_score(player_id)
        if score is None:
            return None
        # save to db
        db.session.add(score)
        db.session.commit()
        # set player
        player = score.player
    return player

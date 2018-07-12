import json
from datetime import date

from app import app, db
from app.models import Player, MatchScore, HeroScore, Hero
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
    w_total = w_dict['win'] + w_dict['lose']
    if w_total == 0:
        score.week_score = 0.0
    else:
        score.week_score = w_dict['win'] / float(w_total)
    m_total = m_dict['win'] + m_dict['lose']
    if m_total == 0:
        score.month_score = 0.0
    else:
        score.month_score = m_dict['win'] / float(m_total)
    y_total = y_dict['win'] + y_dict['lose']
    if y_total == 0:
        score.year_score = 0.0
    else:
        score.year_score = y_dict['win'] / float(y_total)
    o_total = o_dict['win'] + o_dict['lose']
    if o_total == 0:
        score.overall_score = 0.0
    else:
        score.overall_score = o_dict['win'] / float(o_total)
    score.overall_count = o_total
    return score


def fetch_player_match_score(player_id, func=get_dota_open_api):
    player_json = func('api/players/{}'.format(player_id))
    if player_json is None:
        app.logger.warning("Missing player json for {}".format(player_id))
        return None
    week_json = func('api/players/{}/wl'.format(player_id), params={'date': 7})
    if week_json is None:
        app.logger.warning("Missing week json for {}".format(player_id))
        return None
    month_json = func('api/players/{}/wl'.format(player_id), params={'date': 30})
    if month_json is None:
        app.logger.warning("Missing month json for {}".format(player_id))
        return None
    year_json = func('api/players/{}/wl'.format(player_id), params={'date': 365})
    if year_json is None:
        app.logger.warning("Missing year json for {}".format(player_id))
        return None
    overall_json = func('api/players/{}/wl'.format(player_id))
    if overall_json is None:
        app.logger.warning("missing overall json for {}".format(player_id))
        return None
    return get_match_score_from_json(
        player_json,
        week_json,
        month_json,
        year_json,
        overall_json
    )


def get_player_match_scores(player_id_list):
    player_score_list = MatchScore.query \
        .filter(MatchScore.score_date == date.today()) \
        .filter(MatchScore.player_id.in_(player_id_list)) \
        .order_by(MatchScore.overall_score.desc()) \
        .all()
    if len(player_score_list) == len(player_id_list):
        return player_score_list
    # only fetch from API if id is not in database
    player_id_list = set(player_id_list) - set([p.player_id for p in player_score_list])
    app.logger.info("load match score from API for " + str(player_id_list))
    for player_id in player_id_list:
        score = fetch_player_match_score(player_id)
        if score is None:
            app.logger.warning("missing score data for {}".format(player_id))
            continue
        # save to db
        db.session.add(score)
        db.session.commit()
        # add to list
        player_score_list.append(score)
    return player_score_list


def get_player_match_score_by_id(player_id):
    score = MatchScore.query\
        .filter(MatchScore.player_id == player_id)\
        .order_by(MatchScore.score_date.desc())\
        .first()
    if score is not None:
        return score
    app.logger.info("load match score from API for " + str(player_id))
    score = fetch_player_match_score(player_id)
    if score is None:
        return None
    # save to db
    db.session.add(score)
    db.session.commit()
    return score


def populate_player_hero_scores_from_json(
        hero_ranking_json,
        hero_match_json,
        heroes_json,
        player_json,
        player_id
):
    hs_dict = {}
    for h in json.loads(heroes_json):
        hs_dict[h['id']] = h
    app.logger.info("heroes dict: {}".format(hs_dict))
    hm_dict = {}
    for hm in json.loads(hero_match_json):
        # NOTE: in player hero API, hero_id is string type, wired! :(
        hm_dict[int(hm['hero_id'])] = hm
    app.logger.info("hero match dict: {}".format(hm_dict))
    hr_dict = {}
    for hr in json.loads(hero_ranking_json):
        hr_dict[hr['hero_id']] = hr
    app.logger.info("hero rank dict: {}".format(hm_dict))
    player = Player.query.filter(Player.account_id == player_id).first()
    if player is None:
        p_dict = json.loads(player_json)
        player = Player(
            account_id=p_dict['profile']['account_id'],
            steam_id=p_dict['profile']['steamid'],
            personaname=p_dict['profile']['personaname'],
            name=p_dict['profile']['name'],
            avatar=p_dict['profile']['avatar']
        )
        db.session.add(player)
        db.session.commit()
    for hero_id in hs_dict.keys():
        hero = Hero.query.filter(Hero.hero_id == hero_id).first()
        if hero is None:
            hero = Hero(
                hero_id=hero_id,
                name=hs_dict[hero_id]['name'],
                localized_name=hs_dict[hero_id]['localized_name'],
                primary_attr=hs_dict[hero_id]['primary_attr'],
                attack_type=hs_dict[hero_id]['attack_type'],
                roles=",".join(hs_dict[hero_id]['roles']),
                legs=hs_dict[hero_id]['legs']
            )
            db.session.add(hero)
            db.session.commit()
        hero_score = HeroScore(
            player=player,
            hero=hero
        )
        if hero_id not in hm_dict:
            hero_score.last_played_score = 0.0
            hero_score.win_score = 0.0
        else:
            last_played = hm_dict[hero_id]['last_played']
            hero_score.last_played_score = float(last_played) / (10 ** len(str(last_played)))
            win = hm_dict[hero_id]['win']
            hero_score.win_score = float(win) / (10 ** len(str(win)))
        if hero_id not in hr_dict:
            hero_score.rank_score = 0.0
        else:
            hero_score.rank_score = hr_dict[hero_id]['percent_rank']
        hero_score.overall_score = hero_score.get_overall_score()
        db.session.add(hero_score)
        db.session.commit()


def fetch_player_hero_scores(player_id, func=get_dota_open_api):
    hero_ranking_json = func('api/players/{}/rankings'.format(player_id))
    if hero_ranking_json is None:
        app.logger.warning("missing hero ranking json for {}".format(player_id))
        return None
    hero_match_json = func('api/players/{}/heroes'.format(player_id))
    if hero_match_json is None:
        app.logger.warning("missing hero match json for {}".format(player_id))
        return None
    # TODO: lazy load heroes data and player data
    heroes_json = func('api/heroes')
    if heroes_json is None:
        app.logger.warning("missing heroes json")
        return None
    player_json = func('api/players/{}'.format(player_id))
    if player_json is None:
        app.logger.warning("Missing player json for {}".format(player_id))
        return None
    return populate_player_hero_scores_from_json(
        hero_ranking_json,
        hero_match_json,
        heroes_json,
        player_json,
        player_id
    )


def get_player_hero_score_by_id(player_id):
    score = HeroScore.query\
        .filter(HeroScore.player_id == player_id) \
        .order_by(HeroScore.score_date.desc()) \
        .order_by(HeroScore.overall_score.desc())\
        .first()
    if score is not None:
        return score
    app.logger.info("load hero score from API for " + str(player_id))
    fetch_player_hero_scores(player_id)
    return HeroScore.query \
        .filter(HeroScore.player_id == player_id) \
        .order_by(HeroScore.score_date.desc()) \
        .order_by(HeroScore.overall_score.desc()) \
        .first()

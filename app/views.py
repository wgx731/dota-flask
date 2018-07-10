from app import app
from app.services import get_player_scores
from flask import request, abort, render_template, jsonify


def accept_json():
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

@app.route('/leaderboard', methods=['GET'])
def leader_board():
    try:
        player_id_list = [int(n) for n in request.args.get("ids").split(",")]
    except (ValueError, AttributeError) as e:
        app.logger.warning(e)
        return abort(400)
    if len(player_id_list) < 1 or len(player_id_list) > 10:
        return abort(400)
    score_list = get_player_scores(player_id_list)
    if len(score_list) == 0:
        return abort(404)
    try:
        sort_by = request.args.get("sort").upper()
    except AttributeError as e:
        sort_by = 'O'
        app.logger.warning(e)
    score_list = sort_score_list(score_list, sort_by)
    if accept_json():
        return jsonify([s.to_dict() for s in score_list])
    else:
        return render_template(
            'leaderboard.html',
            scores=score_list
        )

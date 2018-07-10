from app import app
from app.services import get_player_scores
from flask import request, abort, render_template, jsonify


def accept_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


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
    # TODO: add sort here
    if accept_json():
        return jsonify([s.to_dict() for s in score_list])
    else:
        return render_template(
            'leaderboard.html',
            scores=score_list
        )

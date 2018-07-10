from app import app
from app.services import get_player_scores, accept_json, sort_score_list
from flask import request, abort, render_template, jsonify


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
    if accept_json(request):
        return jsonify([s.to_dict() for s in score_list])
    else:
        return render_template(
            'leader_board.html',
            scores=score_list
        )

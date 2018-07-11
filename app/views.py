from app import app
from app.services import get_player_match_scores, accept_json,\
    sort_score_list, get_player_match_score_by_id
from flask import request, abort, render_template, jsonify


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def error(e):
    app.logger.error("error occurred: %s" % e)
    try:
        print(e.code)
        return render_template(
            'error.html',
            code=e.code,
            message=str(e)
        )
    except Exception as e:
        app.logger.error('exception is %s' % e)
    finally:
        return render_template(
            'error.html',
            code=500,
            message='unknown error.'
        )


@app.route('/leaderboard', methods=['GET'])
def leader_board():
    try:
        player_id_list = [int(n) for n in request.args.get("ids").split(",")]
    except (ValueError, AttributeError) as e:
        app.logger.warning(e)
        return abort(400)
    if len(player_id_list) < 1 or len(player_id_list) > 10:
        return abort(400)
    score_list = get_player_match_scores(player_id_list)
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
            title='Leader Board',
            scores=score_list
        )


@app.route('/compare', methods=['GET'])
def compare_players():
    try:
        p1 = int(request.args.get("p1"))
        p2 = int(request.args.get("p2"))
    except (ValueError, AttributeError) as e:
        app.logger.warning(e)
        return abort(400)
    s1 = get_player_match_score_by_id(p1)
    if s1 is None:
        return abort(404)
    s2 = get_player_match_score_by_id(p2)
    if s2 is None:
        return abort(404)
    compare_result = s1.get_compare_score() - s2.get_compare_score()
    if accept_json(request):
        return {
            'result': compare_result,
            'player1': s1.to_dict(),
            'player2': s2.to_dict()
        }
    else:
        return render_template(
            'compare_players.html',
            title='Compare {} with {}'.format(s1.player.name, s2.player.name),
            result=compare_result,
            s1=s1,
            s2=s2
        )

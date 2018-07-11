import unittest
import os
import logging
from datetime import date
from unittest.mock import Mock
from app import app, db, default_db_path, default_db_uri
from app.models import Player, MatchScore
from app.services import get_match_score_from_json, fetch_player_match_score


app.logger.setLevel(logging.ERROR)


class ServiceTest(unittest.TestCase):

    def test_get_match_score_from_json(self):
        score = get_match_score_from_json(
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}'
        )
        self.assertEqual(score.week_score, 0)
        self.assertEqual(score.month_score, 0)
        self.assertEqual(score.year_score, 0)
        self.assertEqual(score.overall_score, 0)
        self.assertEqual(score.overall_count, 0)
        self.assertEqual(score.player.account_id, 1)
        score = get_match_score_from_json(
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":1,"lose":3}',
            '{"win":1,"lose":1}',
            '{"win":1,"lose":0}',
            '{"win":10,"lose":90}'
        )
        self.assertEqual(score.week_score, 0.25)
        self.assertEqual(score.month_score, 0.5)
        self.assertEqual(score.year_score, 1.0)
        self.assertEqual(score.overall_score, 0.1)
        self.assertEqual(score.overall_count, 100)
        self.assertEqual(score.player.account_id, 1)

    def test_fetch_player_match_score(self):
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}'
        ])
        self.assertIsNotNone(fetch_player_match_score([1], mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            None
        ])
        self.assertIsNone(fetch_player_match_score([1], mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            None
        ])
        self.assertIsNone(fetch_player_match_score([1], mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            None
        ])
        self.assertIsNone(fetch_player_match_score([1], mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            None
        ])
        self.assertIsNone(fetch_player_match_score([1], mock))
        mock = Mock(side_effect=[
            None
        ])
        self.assertIsNone(fetch_player_match_score([1], mock))


class DotaFlaskTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            default_db_uri.replace("local", "test")
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        db.drop_all()
        os.unlink(default_db_path.replace("local", "test"))
        del self.app

    def __clean_test_data(self):
        del self.p1
        del self.p2
        del self.s1
        del self.s2

    def __setup_test_data(self):
        # setup
        self.p1 = Player(
            account_id=1,
            steam_id="1",
            personaname="p1",
            name="player1",
            avatar="p1.jpg"
        )
        self.s1 = MatchScore(
            week_score=0.5,
            month_score=0.6,
            year_score=0.3,
            overall_count=10,
            overall_score=0.5313,
            player=self.p1
        )
        self.p2 = Player(
            account_id=2,
            steam_id="2",
            personaname="p2",
            name="player2",
            avatar="p2.jpg"
        )
        self.s2 = MatchScore(
            week_score=0.6,
            month_score=0.5,
            year_score=0.2,
            overall_count=100,
            overall_score=0.4313,
            player=self.p2
        )
        db.session.add(self.p1)
        db.session.add(self.p2)
        db.session.commit()

    def test_leader_board(self):
        # setup
        self.__setup_test_data()
        # test model
        self.assertEqual(str(self.p1), 'Player - id: 1 name: player1 avatar: p1.jpg')
        self.assertEqual(str(self.s2), 'Score - id: 2 date: ' + str(date.today()) + ' \
                week: 0.6 month: 0.5 year: 0.2 overall: 0.4313')
        # test wrong id
        result = self.app.get('/leaderboard?ids=d')
        self.assertEqual(result.status_code, 400)
        # test missing id
        result = self.app.get('/leaderboard')
        self.assertEqual(result.status_code, 400)
        # test too many ids
        result = self.app.get('/leaderboard?ids=1,2,3,4,5,6,7,8,9,10,11')
        self.assertEqual(result.status_code, 400)
        # test correct ids
        result = self.app.get('/leaderboard?ids=1,2')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'player1', result.data)
        self.assertIn(b'player2', result.data)
        # test sort
        self.app.get('/leaderboard?ids=1,2&sort=W')
        self.assertEqual(result.status_code, 200)
        self.app.get('/leaderboard?ids=1,2&sort=M')
        self.assertEqual(result.status_code, 200)
        self.app.get('/leaderboard?ids=1,2&sort=Y')
        self.assertEqual(result.status_code, 200)
        self.app.get('/leaderboard?ids=1,2&sort=c')
        self.assertEqual(result.status_code, 200)
        # test json response
        result = self.app.get('/leaderboard?ids=1,2', headers={
            'Accept': 'application/json'
        })
        self.assertEqual(result.status_code, 200)
        self.assertIn('application/json', result.headers['Content-Type'])
        self.assertIn(b'player1', result.data)
        self.assertIn(b'player2', result.data)
        # clean up
        self.__clean_test_data()

    def test_compare(self):
        # setup
        self.__setup_test_data()
        # test wrong p1
        result = self.app.get('/compare?p1=d')
        self.assertEqual(result.status_code, 400)
        # test wrong p2
        result = self.app.get('/compare?p1=1&p2=d')
        self.assertEqual(result.status_code, 400)
        # test correct p1 and p2
        result = self.app.get('/compare?p1=1&p2=2')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'player1', result.data)
        self.assertIn(b'player2', result.data)
        self.assertIn(b'-35.96', result.data)
        # clean up
        self.__clean_test_data()


if __name__ == '__main__':
    unittest.main()

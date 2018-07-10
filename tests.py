import unittest
import os
from datetime import date
from app import app, db, default_db_path, default_db_uri
from app.models import Player, Score


class DotaFlaskTest(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = \
                default_db_uri.replace("local", "test")
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        db.drop_all()
        os.unlink(default_db_path.replace("local", "test"))
        del self.app

    def test_leader_board(self):
        """Assert that leader board is loaded correctly"""
        # setup
        p1 = Player(
            account_id=1,
            steam_id="1",
            personaname="p1",
            name="player1",
            avatar="p1.jpg"
        )
        Score(
            week_score=0.5,
            month_score=0.6,
            year_score=0.3,
            overall_score=0.5313,
            player=p1
        )
        p2 = Player(
            account_id=2,
            steam_id="2",
            personaname="p2",
            name="player2",
            avatar="p2.jpg"
        )
        s2 = Score(
            week_score=0.6,
            month_score=0.5,
            year_score=0.2,
            overall_score=0.4313,
            player=p2
        )
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        # test model
        self.assertEqual(str(p1), 'Player - id: 1 name: player1 avatar: p1.jpg')
        self.assertEqual(str(s2), 'Score - id: 2 date: ' + str(date.today()) + ' \
                week: 0.6 month: 0.5 year: 0.2 overall: 0.4313')
        # test wrong id
        result = self.app.get('/leaderboard?ids=3')
        self.assertEqual(result.status_code, 404)
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
        # test only 1 correct id
        result = self.app.get('/leaderboard?ids=1,3')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'player1', result.data)
        self.assertNotIn(b'player2', result.data)
        # test json response
        result = self.app.get('/leaderboard?ids=1,2', headers={
            'Accept': 'application/json'
        })
        self.assertEqual(result.status_code, 200)
        self.assertIn('application/json', result.headers['Content-Type'])
        self.assertIn(b'player1', result.data)
        self.assertIn(b'player2', result.data)


if __name__ == '__main__':
    unittest.main()

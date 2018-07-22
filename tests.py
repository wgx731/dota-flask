import unittest
import os
import logging
from urllib.error import URLError
from unittest.mock import Mock
from datetime import date
from app import app, db, default_db_path, default_db_uri
from app.models import Player, Hero, HeroScore, MatchScore
from app.services import get_match_score_from_json, fetch_player_match_score, \
    populate_player_hero_scores_from_json, fetch_player_hero_scores
from app.apis import get_dota_open_api


app.logger.setLevel(logging.ERROR)


class APITest(unittest.TestCase):

    def test_api(self):
        response_attrs = {'getcode.return_value': 200, 'read.return_value': 'test'}
        mock_response = Mock(**response_attrs)
        request_attrs = {'urlopen.return_value': mock_response, 'Request.return_value': None}
        mock_request = Mock(**request_attrs)
        self.assertEqual(get_dota_open_api('123', r=mock_request), 'test')
        response_attrs = {'getcode.return_value': 401, 'read.return_value': 'test'}
        mock_response = Mock(**response_attrs)
        request_attrs = {'urlopen.return_value': mock_response, 'Request.return_value': None}
        mock_request = Mock(**request_attrs)
        self.assertIsNone(get_dota_open_api('234', params={'a': 'b'}, r=mock_request))
        request_attrs = {'urlopen.side_effect': URLError('wrong url')}
        mock_request = Mock(**request_attrs)
        self.assertIsNone(get_dota_open_api('234', params={'a': 'b'}, r=mock_request))


class ModelTest(unittest.TestCase):

    def setUp(self):
        self.p = Player(
            account_id=1,
            steam_id='1',
            personaname='p1',
            name='player1',
            avatar='p1.jpg'
        )
        self.h = Hero(
            hero_id=1,
            name='h1',
            localized_name='hero1',
            primary_attr='magic',
            attack_type='fire',
            roles='a,b,c',
            legs=0
        )
        self.hs = HeroScore(
            hero_score_id=1,
            rank_score=0.1,
            last_played_score=0.1,
            win_score=0.1,
            overall_score=0.1,
            score_date=date.today(),
            player_id=self.p.account_id,
            hero_id=self.h.hero_id,
            player=self.p,
            hero=self.h
        )
        self.ms = MatchScore(
            match_score_id=1,
            week_score=0.1,
            month_score=0.1,
            year_score=0.1,
            overall_score=0.1,
            overall_count=10,
            score_date=date.today(),
            player_id=self.p.account_id,
            player=self.p
        )

    def tearDown(self):
        del self.hs
        del self.ms
        del self.p
        del self.h

    def test_player_and_hero(self):
        self.assertEqual(self.p.to_dict(), {
            'account_id': 1,
            'steam_id': '1',
            'person_name': 'p1',
            'name': 'player1',
            'avatar_url': 'p1.jpg'
        })
        self.assertEqual(
            str(self.p),
            'Player - id: 1 name: player1 avatar: p1.jpg'
        )

    def test_hero(self):
        self.assertEqual(self.h.to_dict(), {
            'hero_id': 1,
            'name': 'h1',
            'localized_name': 'hero1',
            'primary_attr': 'magic',
            'attack_type': 'fire',
            'roles': 'a,b,c',
            'legs': 0
        })
        self.assertEqual(
            str(self.h),
            'Hero - id: 1 name: hero1 type: fire roles: a,b,c'
        )

    def test_hero_score(self):
        self.assertEqual(self.hs.to_dict(), {
            'hero_score_id': 1,
            'rank_score': 0.1,
            'last_played_score': 0.1,
            'win_score': 0.1,
            'overall_score': 0.1,
            'score_date': str(date.today()),
            'player': self.p.to_dict(),
            'hero': self.h.to_dict()
        })
        self.assertEqual(self.hs.get_overall_score(), 0.1)
        self.assertEqual(
            str(self.hs),
            'Hero Score - hero id: 1 player id: 1 '
            'overall score: 0.1 score date: {}'.format(str(date.today()))
        )

    def test_match_score(self):
        self.assertEqual(self.ms.to_dict(), {
            'match_score_id': 1,
            'week_score': 0.1,
            'month_score': 0.1,
            'year_score': 0.1,
            'overall_score': 0.1,
            'overall_count': 10,
            'score_date': str(date.today()),
            'player': self.p.to_dict()
        })
        self.assertAlmostEqual(self.ms.get_compare_score(10), 0.82)
        self.assertEqual(
            str(self.ms),
            'Match Score - player id: {} date: {} '
            'week: {} month: {} year: {} overall: {}'.format(
                1, str(date.today()), 0.1, 0.1, 0.1, 0.1)
        )


class ServiceTest(unittest.TestCase):

    def setUp(self):
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            app.config['SQLALCHEMY_DATABASE_URI'] = default_db_uri.replace(
                "local", "test"
            )
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            os.unlink(default_db_path.replace("local", "test"))
        del self.app

    def test_get_match_score_from_json(self):
        score = get_match_score_from_json(
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            1
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
            '{"win":10,"lose":90}',
            1
        )
        self.assertEqual(score.week_score, 0.25)
        self.assertEqual(score.month_score, 0.5)
        self.assertEqual(score.year_score, 1.0)
        self.assertEqual(score.overall_score, 0.1)
        self.assertEqual(score.overall_count, 10)
        self.assertEqual(score.player.account_id, 1)

    def test_fetch_player_match_score(self):
        mock = Mock(side_effect=[
            None
        ])
        self.assertIsNone(fetch_player_match_score(1, mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            None
        ])
        self.assertIsNone(fetch_player_match_score(1, mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            None
        ])
        self.assertIsNone(fetch_player_match_score(1, mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            None
        ])
        self.assertIsNone(fetch_player_match_score(1, mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            None
        ])
        self.assertIsNone(fetch_player_match_score(1, mock))
        mock = Mock(side_effect=[
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}',
            '{"win":0,"lose":0}'
        ])
        self.assertIsNotNone(fetch_player_match_score(1, mock))

    def test_populate_player_hero_scores_from_json(self):
        score = HeroScore.query \
            .filter(HeroScore.player_id == 1) \
            .order_by(HeroScore.score_date.desc()) \
            .order_by(HeroScore.overall_score.desc()) \
            .first()
        self.assertIsNone(score)
        populate_player_hero_scores_from_json(
            '[{"hero_id": 1, "score": 4398.79441087885, "percent_rank": 0.9, "card": 954500}]',
            '[{"hero_id":"1","last_played":9,"games":10,"win":9}]',
            '[{"id":1,"name":"h1","localized_name":"hero1","primary_attr":"agi","attack_type":"fire",\
            "roles":["Carry","Escape","Nuker"],"legs":2}]',
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}',
            1
        )
        score = HeroScore.query \
            .filter(HeroScore.player_id == 1) \
            .order_by(HeroScore.score_date.desc()) \
            .order_by(HeroScore.overall_score.desc()) \
            .first()
        self.assertEqual(score.player.account_id, 1)
        populate_player_hero_scores_from_json(
            '[{"hero_id": 1, "score": 4398.79441087885, "percent_rank": 0.9, "card": 954500}]',
            '[{"hero_id":"1","last_played":9,"games":10,"win":9}]',
            '[{"id":2,"name":"h2","localized_name":"hero2","primary_attr":"agi","attack_type":"fire",\
            "roles":["Carry","Escape","Nuker"],"legs":2}]',
            '{"profile":{"account_id":2,"steamid":2,"personaname":"player2","name":"p2","avatar":"p2.jpg"}}',
            2
        )
        score = HeroScore.query \
            .filter(HeroScore.player_id == 2) \
            .order_by(HeroScore.score_date.desc()) \
            .order_by(HeroScore.overall_score.desc()) \
            .first()
        self.assertEqual(score.player.account_id, 2)

    def test_fetch_player_hero_scores(self):
        mock = Mock(side_effect=[
            None
        ])
        fetch_player_hero_scores(1, mock)
        score = HeroScore.query \
            .filter(HeroScore.player_id == 1) \
            .first()
        self.assertIsNone(score)
        mock = Mock(side_effect=[
            '[{"hero_id": 1, "score": 4398.79441087885, "percent_rank": 0.9, "card": 954500}]',
            None
        ])
        fetch_player_hero_scores(1, mock)
        score = HeroScore.query \
            .filter(HeroScore.player_id == 1) \
            .first()
        self.assertIsNone(score)
        mock = Mock(side_effect=[
            '[{"hero_id": 1, "score": 4398.79441087885, "percent_rank": 0.9, "card": 954500}]',
            '[{"hero_id":"1","last_played":9,"games":10,"win":9}]',
            None
        ])
        fetch_player_hero_scores(1, mock)
        score = HeroScore.query \
            .filter(HeroScore.player_id == 1) \
            .first()
        self.assertIsNone(score)
        mock = Mock(side_effect=[
            '[{"hero_id": 1, "score": 4398.79441087885, "percent_rank": 0.9, "card": 954500}]',
            '[{"hero_id":"1","last_played":9,"games":10,"win":9}]',
            '[{"id":1,"name":"h1","localized_name":"hero1","primary_attr":"agi","attack_type":"fire",\
            "roles":["Carry","Escape","Nuker"],"legs":2}]',
            None
        ])
        fetch_player_hero_scores(1, mock)
        score = HeroScore.query \
            .filter(HeroScore.player_id == 1) \
            .first()
        self.assertIsNone(score)
        mock = Mock(side_effect=[
            '[{"hero_id": 1, "score": 4398.79441087885, "percent_rank": 0.9, "card": 954500}]',
            '[{"hero_id":"1","last_played":9,"games":10,"win":9}]',
            '[{"id":1,"name":"h1","localized_name":"hero1","primary_attr":"agi","attack_type":"fire",\
            "roles":["Carry","Escape","Nuker"],"legs":2}]',
            '{"profile":{"account_id":1,"steamid":1,"personaname":"player1","name":"p1","avatar":"p1.jpg"}}'
        ])
        fetch_player_hero_scores(1, mock)
        score = HeroScore.query \
            .filter(HeroScore.player_id == 1) \
            .first()
        self.assertIsNotNone(score)


class ViewTest(unittest.TestCase):

    def setUp(self):
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            app.config['SQLALCHEMY_DATABASE_URI'] = default_db_uri.replace(
                "local", "test"
            )
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            os.unlink(default_db_path.replace("local", "test"))
        del self.app

    def __clean_test_data(self):
        del self.p1
        del self.p2
        del self.ms1
        del self.ms2
        del self.h1
        del self.hs1

    def __setup_test_data(self):
        # setup
        self.p1 = Player(
            account_id=1,
            steam_id="1",
            personaname="p1",
            name="player1",
            avatar="p1.jpg"
        )
        self.ms1 = MatchScore(
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
        self.ms2 = MatchScore(
            week_score=0.6,
            month_score=0.5,
            year_score=0.2,
            overall_count=100,
            overall_score=0.4313,
            player=self.p2
        )
        self.h1 = Hero(
            hero_id=1,
            name='h1',
            localized_name='hero1',
            primary_attr='magic',
            attack_type='fire',
            roles='a,b,c',
            legs=0
        )
        self.hs1 = HeroScore(
            hero_score_id=1,
            rank_score=0.1,
            last_played_score=0.1,
            win_score=0.1,
            overall_score=0.78,
            score_date=date.today(),
            player_id=self.p1.account_id,
            hero_id=self.h1.hero_id,
            player=self.p1,
            hero=self.h1
        )
        db.session.add(self.ms1)
        db.session.add(self.ms2)
        db.session.add(self.hs1)
        db.session.commit()

    def test_index(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'LeaderBoard', result.data)
        self.assertIn(b'Comparison', result.data)
        self.assertIn(b'Recommendation', result.data)

    def test_leader_board(self):
        # setup
        self.__setup_test_data()
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

    def test_compare_players(self):
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
        self.assertIn(b'-7.2', result.data)
        # clean up
        self.__clean_test_data()

    def test_recommend_hero(self):
        # setup
        self.__setup_test_data()
        # test wrong player id
        result = self.app.get('/recommend?p=d')
        self.assertEqual(result.status_code, 400)
        # test correct player id
        result = self.app.get('/recommend?p=1')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'hero1', result.data)
        self.assertIn(b'0.78', result.data)
        # clean up
        self.__clean_test_data()


if __name__ == '__main__':
    unittest.main()

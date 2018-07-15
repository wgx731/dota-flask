from datetime import date
from app import db


class Player(db.Model):
    """A Player class"""
    __tablename__ = 'player'

    account_id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String)
    personaname = db.Column(db.String)
    name = db.Column(db.String)
    avatar = db.Column(db.String)

    def to_dict(self):
        return {
            'account_id': self.account_id,
            'steam_id': self.steam_id,
            'person_name': self.personaname,
            'name': self.name,
            'avatar_url': self.avatar
        }

    def __repr__(self):
        return '<Player %r>' % self.name

    def __str__(self):
        return 'Player - id: {} name: {} avatar: {}'.format(
            self.account_id,
            self.name,
            self.avatar
        )


class Hero(db.Model):
    """A Hero class"""
    __tablename__ = 'hero'

    hero_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    localized_name = db.Column(db.String)
    primary_attr = db.Column(db.String)
    attack_type = db.Column(db.String)
    roles = db.Column(db.String)
    legs = db.Column(db.Integer)

    def to_dict(self):
        return {
            'hero_id': self.hero_id,
            'name': self.name,
            'localized_name': self.localized_name,
            'primary_attr': self.primary_attr,
            'attack_type': self.attack_type,
            'roles': self.roles,
            'legs': self.legs
        }

    def __repr__(self):
        return '<Hero %r>' % self.name

    def __str__(self):
        return 'Hero - id: {} name: {} type: {} roles: {}'.format(
            self.hero_id,
            self.localized_name,
            self.attack_type,
            self.roles
        )


class HeroScore(db.Model):
    """A Hero Score class"""
    __tablename__ = 'hero_score'

    hero_score_id = db.Column(db.Integer, primary_key=True)
    rank_score = db.Column(db.Float(10))
    last_played_score = db.Column(db.Float(10))
    win_score = db.Column(db.Float(10))
    overall_score = db.Column(db.Float(10), nullable=False)
    score_date = db.Column(db.Date, nullable=False,
                           default=date.today)
    player_id = db.Column(db.Integer, db.ForeignKey('player.account_id'),
                          nullable=False)
    player = db.relationship('Player',
                             backref=db.backref('player_hero_scores', lazy=True))
    hero_id = db.Column(db.Integer, db.ForeignKey('hero.hero_id'),
                        nullable=False)
    hero = db.relationship('Hero',
                           backref=db.backref('hero_scores', lazy=True))

    def to_dict(self):
        return {
            'hero_score_id': self.hero_score_id,
            'rank_score': self.rank_score,
            'last_played_score': self.last_played_score,
            'win_score': self.win_score,
            'overall_score': self.overall_score,
            'score_date': str(self.score_date),
            'player': self.player.to_dict(),
            'hero': self.hero.to_dict()
        }

    def get_overall_score(self):
        return self.rank_score * 0.5 + self.win_score * 0.45 + self.last_played_score * 0.05

    def __repr__(self):
        return '<Hero Score %r>' % self.overall_score

    def __str__(self):
        return 'Hero Score - hero id: {} player id: {} overall score: {} score date: {}'.format(
            self.hero_id,
            self.player_id,
            self.overall_score,
            self.score_date
        )


class MatchScore(db.Model):
    """A Match Score class"""
    __tablename__ = 'match_score'

    match_score_id = db.Column(db.Integer, primary_key=True)
    week_score = db.Column(db.Float(10))
    month_score = db.Column(db.Float(10))
    year_score = db.Column(db.Float(10))
    overall_score = db.Column(db.Float(10))
    overall_count = db.Column(db.Integer)
    score_date = db.Column(db.Date, nullable=False,
                           default=date.today)
    player_id = db.Column(db.Integer, db.ForeignKey('player.account_id'),
                          nullable=False)
    player = db.relationship('Player',
                             backref=db.backref('player_match_scores', lazy=True))

    def to_dict(self):
        return {
            'match_score_id': self.match_score_id,
            'week_score': self.week_score,
            'month_score': self.month_score,
            'year_score': self.year_score,
            'overall_score': self.overall_score,
            'overall_count': self.overall_count,
            'score_date': str(self.score_date),
            'player': self.player.to_dict()
        }

    def get_compare_score(self, max_count):
        return (float(self.overall_count) / max_count) * 0.8 \
            + self.week_score * 0.1 + self.month_score * 0.05 \
            + self.year_score * 0.05

    def __repr__(self):
        return '<Match Score %r>' % self.overall_score

    def __str__(self):
        return 'Match Score - player id: {} date: {} week: {} month: {} year: {} overall: {}'.format(
            self.player_id,
            self.score_date,
            self.week_score,
            self.month_score,
            self.year_score,
            self.overall_score
        )

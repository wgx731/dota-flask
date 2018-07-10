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


class Score(db.Model):
    """A Score class"""
    __tablename__ = 'score'

    score_id = db.Column(db.Integer, primary_key=True)
    week_score = db.Column(db.Float)
    month_score = db.Column(db.Float)
    year_score = db.Column(db.Float)
    overall_score = db.Column(db.Float)
    score_date = db.Column(db.Date, nullable=False,
                           default=date.today)
    account_id = db.Column(db.Integer, db.ForeignKey('player.account_id'),
                           nullable=False)
    player = db.relationship('Player',
                             backref=db.backref('scores', lazy=True))

    def to_dict(self):
        return {
            'score_id': self.score_id,
            'week_score': self.week_score,
            'month_score': self.month_score,
            'year_score': self.year_score,
            'overall_score': self.overall_score,
            'score_date': str(self.score_date),
            'player': self.player.to_dict()
        }

    def __repr__(self):
        return '<Score %r>' % self.overall_score

    def __str__(self):
        return 'Score - id: {} date: {} \
                week: {} month: {} year: {} overall: {}'.format(
                    self.account_id,
                    self.score_date,
                    self.week_score,
                    self.month_score,
                    self.year_score,
                    self.overall_score
                )

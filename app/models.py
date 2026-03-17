from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(150), unique=True, nullable=False)
    password       = db.Column(db.String(256), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Profile stats
    height         = db.Column(db.Float, nullable=True)       # cm
    start_weight   = db.Column(db.Float, nullable=True)       # kg
    goal_weight    = db.Column(db.Float, nullable=True)       # kg
    age            = db.Column(db.Integer, nullable=True)
    split_pref     = db.Column(db.String(10), nullable=True)  # 'bro' or 'ppl'

    # Relationships
    weight_logs    = db.relationship('WeightLog', backref='user', lazy=True, cascade='all, delete-orphan')
    daily_logs     = db.relationship('DailyLog',  backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f'<User {self.email}>'


class WeightLog(db.Model):
    __tablename__ = 'weight_logs'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight     = db.Column(db.Float, nullable=False)
    logged_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WeightLog {self.weight}kg on {self.logged_at.date()}>'


class DailyLog(db.Model):
    __tablename__ = 'daily_logs'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date             = db.Column(db.Date, default=datetime.utcnow().date)
    strength_rating  = db.Column(db.Integer, nullable=True)   # 1–5
    completion       = db.Column(db.String(20), nullable=True) # 'full', 'partial', 'rest'
    note             = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<DailyLog {self.date} rating={self.strength_rating}>'

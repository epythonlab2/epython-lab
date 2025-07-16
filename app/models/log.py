# /models/log.py
from datetime import datetime
from app.extensions import db

class SessionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    user_agent = db.Column(db.String(256))
    browser = db.Column(db.String(64))
    os = db.Column(db.String(64))
    device = db.Column(db.String(64))
    country = db.Column(db.String(64))

    user = db.relationship('User', backref='session_logs')


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50))  # create, update, delete
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    actor = db.relationship('User', foreign_keys=[actor_id], backref='performed_actions')
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='audit_records')

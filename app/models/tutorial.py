from app import db
from datetime import datetime, timezone
from sqlalchemy import Enum

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    subtopics = db.relationship('SubTopic', backref='topic', cascade="all, delete-orphan")

class SubTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text)
    status = db.Column(Enum('draft', 'published', name='content_status'), default='draft')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True))
    
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='subtopic', cascade="all, delete-orphan")

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    subtopic_id = db.Column(db.Integer, db.ForeignKey('sub_topic.id'), nullable=False)

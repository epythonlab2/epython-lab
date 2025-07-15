# app/models/content.py

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from app import db

class Topic(db.Model):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # One-to-many: Topic -> SubTopics
    subtopics = db.relationship(
        'SubTopic',
        backref='topic',
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Topic {self.title}>"


class SubTopic(db.Model):
    __tablename__ = 'sub_topic'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    status = db.Column(
        Enum('draft', 'published', name='content_status'),
        default='draft',
        nullable=False
    )

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)

    # One-to-many: SubTopic -> Quizzes
    quizzes = db.relationship(
        'Quiz',
        backref='subtopic',
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<SubTopic {self.title}>"


class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)

    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D

    subtopic_id = db.Column(db.Integer, db.ForeignKey('sub_topic.id'), nullable=False)

    def __repr__(self):
        return f"<Quiz {self.question[:30]}...>"

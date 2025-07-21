# app/models/content.py

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from app.extensions import db

# ----------------------------
# SQLAlchemy ORM (Flask-db.Modeld Models)
# ----------------------------

class Topic(db.Model):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    subtopics = db.relationship(
        'SubTopic',
        backref='topic',
        cascade='all, delete-orphan',
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

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)

    quizzes = db.relationship(
        'Quiz',
        backref='subtopic',
        cascade='all, delete-orphan',
        lazy=True
    )

    # Add these relationships if analytics & views are used
    views = relationship("SubTopicView", back_populates="subtopic")
    analytics = relationship("SubTopicAnalytics", back_populates="subtopic", uselist=False)

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

    correct_answer = db.Column(db.String(1), nullable=False)  # One of: A, B, C, D

    subtopic_id = db.Column(db.Integer, db.ForeignKey('sub_topic.id'), nullable=False)

    def __repr__(self):
        return f"<Quiz {self.question[:30]}...>"


# ----------------------------
# Analytics & Tracking Models (Non-Flask db.Model)
# ----------------------------

class Session(db.Model):
    """
    Tracks anonymous user sessions (used for analytics, search, and error correlation).
    """
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False)
    ip_address = Column(String)
    browser = Column(String)
    os = Column(String)
    device_type = Column(String, nullable=True)
    country = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)


    tutorial_views = relationship("SubTopicView", back_populates="session")
    search_queries = relationship("SearchQuery", back_populates="session")
    error_logs = relationship("ErrorLog", back_populates="session")


class SubTopicView(db.Model):
    """
    Represents a subtopic view by a user session.
    Tracks time spent and scroll depth.
    """
    __tablename__ = 'subtopic_views'

    id = Column(Integer, primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('sub_topic.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow)
    time_spent_seconds = Column(Float, nullable=True)
    scroll_depth_percent = Column(Float, nullable=True)

    subtopic = relationship("SubTopic", back_populates="views")
    session = relationship("Session", back_populates="tutorial_views")


class SubTopicAnalytics(db.Model):
    """
    Aggregated metrics per subtopic, derived from user interactions.
    """
    __tablename__ = 'subtopic_analytics'

    id = Column(Integer, primary_key=True)
    subtopic_id = Column(Integer, ForeignKey('sub_topic.id'), nullable=False, unique=True)
    total_views = Column(Integer, default=0)
    total_time_spent = Column(Float, default=0.0)
    average_scroll_depth = Column(Float, default=0.0)

    subtopic = relationship("SubTopic", back_populates="analytics")


class SearchQuery(db.Model):
    """
    Stores search terms entered by users for analysis and UX improvements.
    """
    __tablename__ = 'search_queries'

    id = Column(Integer, primary_key=True)
    query_text = Column(String, nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    searched_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="search_queries")


class ErrorLog(db.Model):
    """
    Logs client-side or API errors to help with debugging and quality tracking.
    """
    __tablename__ = 'error_logs'

    id = Column(Integer, primary_key=True)
    error_message = Column(String, nullable=False)
    url = Column(String, nullable=True)
    stack_trace = Column(Text, nullable=True)
    error_type = Column(String, nullable=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="error_logs")

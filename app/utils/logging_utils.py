from datetime import datetime, timezone
from flask import request
from dateutil import tz
from user_agents import parse as parse_ua

from app.models.log import SessionLog, AuditLog
from app.models.tutorial import Session
from app.extensions import db
import geoip2.database

# Load database once for performance
GEOIP_DB_PATH = 'app/data/GeoLite2-City.mmdb'
geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)


def get_country_from_ip(ip_address: str) -> str:
    """Return the country name from an IP address using GeoLite2."""
    try:
        if ip_address.startswith("127.") or ip_address == "localhost":
            return "Localhost"
        response = geoip_reader.city(ip_address)
        return response.country.name or "Unknown"
    except Exception:
        return "Unknown"

def get_device_type(user_agent_string: str) -> str:
    tv_keywords = ['smart-tv', 'hbbtv', 'netcast',
     'appletv', 'googletv', 'tizen', 'webos',
     'roku', 'aquos', 'sonybravia',
    'androidtv', 'pov_tv', 'smarttv', 'tv']

    """Return the device type (Mobile, Tablet, Desktop, TV, Other)."""
    ua = parse_ua(user_agent_string)
    if ua.is_mobile:
        return 'Mobile'
    if ua.is_tablet:
        return 'Tablet'
    if ua.is_pc:
        return 'Desktop'
    if any(keyword in ua.ua_string for keyword in tv_keywords):
        return 'TV'

    return 'Other'


def parse_user_agent_info() -> dict:
    """Parse User-Agent string and return browser, OS, and device info."""
    ua_string = request.headers.get('User-Agent', '')
    ua = parse_ua(ua_string)
    return {
        'user_agent': ua_string,
        'browser': f"{ua.browser.family} {ua.browser.version_string}",
        'os': f"{ua.os.family} {ua.os.version_string}",
        'device': get_device_type(ua_string)
    }


def get_client_ip(req) -> str:
    """Extract real client IP address, considering proxies."""
    if req.headers.get('X-Forwarded-For'):
        return req.headers.get('X-Forwarded-For').split(',')[0].strip()
    return req.remote_addr or '0.0.0.0'


def get_or_create_session(session_id, **env_data):
    session = Session.query.filter_by(session_id=session_id).first()
    if session:
        # Update environment data on revisit
        session.last_seen = datetime.now(timezone.utc)
        for key, value in env_data.items():
            if value is not None:
                setattr(session, key, value)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Database error updating session", exc_info=True)
        return session, False  # False means session existed
    else:
        session = Session(
            session_id=session_id,
            started_at=datetime.now(timezone.utc),
            **env_data
        )
        db.session.add(session)
        try:
            db.session.commit()
            return session, True  # True means session created now
        except Exception as e:
            db.session.rollback()
            logger.error("Database error creating session", exc_info=True)
            return None, None

def log_session(user):
    """Log a new user session."""
    ua_info = parse_user_agent_info()
    ip_address = get_client_ip(request)

    session = SessionLog(
        user_id=user.id,
        ip_address=ip_address,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        user_agent=ua_info['user_agent'],
        browser=ua_info['browser'],
        os=ua_info['os'],
        device=ua_info['device'],
        country=get_country_from_ip(ip_address)
    )
    db.session.add(session)
    db.session.commit()


def update_last_activity(user):
    """Update the last_activity timestamp for the user's most recent session."""
    latest_session = SessionLog.query.filter_by(user_id=user.id)\
        .order_by(SessionLog.login_time.desc()).first()
    if latest_session:
        latest_session.last_activity = datetime.utcnow()
        db.session.commit()


def log_audit_action(actor_id, action_type, target_user_id=None, description=""):
    """Log an audit event for tracking user actions."""
    audit = AuditLog(
        actor_id=actor_id,
        action_type=action_type,
        target_user_id=target_user_id,
        description=description
    )
    db.session.add(audit)
    db.session.commit()


def format_last_login(dt_iso_str: str) -> str:
    """Convert ISO date or datetime string to a human-readable format."""
    if not dt_iso_str:
        return "Never logged in"

    try:
        if 'T' in dt_iso_str or ':' in dt_iso_str:
            # ISO datetime with time
            dt = datetime.fromisoformat(dt_iso_str)
            local_dt = dt.astimezone(tz.tzlocal())
            return local_dt.strftime("%b %d, %Y · %I:%M %p")
        else:
            # Date-only string
            dt = datetime.fromisoformat(dt_iso_str)
            return dt.strftime("%b %d, %Y")
    except Exception:
        return "Invalid date format"

# app/utils/logging_utils.py
from datetime import datetime
from flask import request
from user_agents import parse as parse_ua
from app.models.log import SessionLog, AuditLog
from app.extensions import db

from datetime import datetime
from dateutil import tz

def parse_user_agent_info():
    ua_string = request.headers.get('User-Agent', '')
    ua = parse_ua(ua_string)
    return {
        'user_agent': ua_string,
        'browser': f"{ua.browser.family} {ua.browser.version_string}",
        'os': f"{ua.os.family} {ua.os.version_string}",
        'device': ua.device.family or 'Unknown'
    }


def log_session(user):
    ua_info = parse_user_agent_info()
    ip_address = request.remote_addr or 'Unknown'

    session = SessionLog(
        user_id=user.id,
        ip_address=ip_address,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        user_agent=ua_info['user_agent'],
        browser=ua_info['browser'],
        os=ua_info['os'],
        device=ua_info['device'],
        country='Localhost'  # Replace with GeoIP lookup if needed
    )
    db.session.add(session)
    db.session.commit()


def update_last_activity(user):
    latest_session = SessionLog.query.filter_by(user_id=user.id).order_by(SessionLog.login_time.desc()).first()
    if latest_session:
        latest_session.last_activity = datetime.utcnow()
        db.session.commit()


def log_audit_action(actor_id, action_type, target_user_id=None, description=""):
    audit = AuditLog(
        actor_id=actor_id,
        action_type=action_type,
        target_user_id=target_user_id,
        description=description
    )
    db.session.add(audit)
    db.session.commit()

def get_client_ip(request):
    """Extract the real IP address from request headers (including behind proxies)."""
    if request.headers.get('X-Forwarded-For'):
        # Handles proxies/load balancers; takes the first in list
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr or '0.0.0.0'
    return ip


def format_last_login(dt_iso_str):
    if not dt_iso_str:
        return "Never logged in"
    from datetime import datetime
    from dateutil import tz
    dt = datetime.fromisoformat(dt_iso_str)
    local_dt = dt.astimezone(tz.tzlocal())
    return local_dt.strftime("%b %d, %Y · %I:%M %p")

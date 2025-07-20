# app/routes/audit_route.py

from flask import Blueprint, jsonify, current_app, request, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta
from sqlalchemy.orm import aliased
from app.models.log import AuditLog, SessionLog
from app.models.user import User, Role
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logging_utils import format_last_login

bp = Blueprint("audit", __name__)

# =======================
# Summary and Metrics
# =======================

@bp.route("/audit-summary")
@jwt_required()
def audit_summary():
    counts = db.session.query(
        AuditLog.action_type, func.count(AuditLog.id)
    ).group_by(AuditLog.action_type).all()
    return jsonify({k: v for k, v in counts})


@bp.route("/inactive-users")
@jwt_required()
def inactive_users():
    """
    Return paginated list of users who have had no audit log activity
    in the last 14 days, including their roles and last seen info.
    Supports pagination via query params: ?page=1&per_page=20
    """
    try:
        threshold = datetime.utcnow() - timedelta(days=14)

        # Pagination parameters with validation
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=5, type=int)
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)  # Limit max per_page to 100

        # IDs of users active in audit logs within threshold
        active_audit_ids = db.session.query(AuditLog.actor_id).filter(
            AuditLog.timestamp >= threshold
        ).distinct()

        # Subquery for last login and last seen per user
        last_seen_subq = db.session.query(
            SessionLog.user_id.label("uid"),
            func.max(SessionLog.login_time).label("last_login"),
            func.max(SessionLog.last_activity).label("last_seen")
        ).group_by(SessionLog.user_id).subquery()

        # Subquery for concatenated role names per user
        roles_subq = db.session.query(
            User.id.label("uid"),
            func.group_concat(Role.name, ', ').label("role_names")
        ).join(User.roles).group_by(User.id).subquery()

        # Main query: users excluding recent active ones
        query = db.session.query(
            User.id,
            User.username,
            roles_subq.c.role_names,
            last_seen_subq.c.last_seen
        ).outerjoin(
            last_seen_subq, User.id == last_seen_subq.c.uid
        ).outerjoin(
            roles_subq, User.id == roles_subq.c.uid
        ).filter(
            ~User.id.in_(active_audit_ids)
        ).order_by(User.username.asc())

        # Paginate the query
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        users = paginated.items

        # Compose JSON response
        result = [
            {
                "user_id": uid,
                "username": username,
                "role": role_names or "None",
                "last_seen": last_seen.strftime("%Y-%m-%d %H:%M") if last_seen else "Never"
            }
            for uid, username, role_names, last_seen in users
        ]

        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages,
            "users": result
        })

    except Exception as e:
        current_app.logger.error(f"Error in /inactive-users: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal Server Error"}), 500



# =======================
# Login Analytics
# =======================

@bp.route("/login-trend")
@jwt_required()
def login_trend():
    today = datetime.utcnow()
    start = today - timedelta(days=29)

    trend = db.session.query(
        func.date(SessionLog.login_time), func.count()
    ).filter(SessionLog.login_time >= start).group_by(
        func.date(SessionLog.login_time)
    ).order_by(func.date(SessionLog.login_time)).all()

    date_map = { (start + timedelta(days=i)).date(): 0 for i in range(30) }
    for date, count in trend:
        date_map[date] = count

    return jsonify({
        "labels": [str(d) for d in date_map],
        "data": list(date_map.values())
    })


@bp.route("/weekly-activity")
@jwt_required()
def weekly_activity():
    today = datetime.utcnow().date()
    start = today - timedelta(weeks=5)

    # Week number using %Y-%W (week starts on Monday, not ISO standard but works in SQLite)
    weekly_counts = db.session.query(
        func.strftime('%Y-%W', AuditLog.timestamp).label('week'),
        func.count()
    ).filter(
        AuditLog.timestamp >= start
    ).group_by('week').order_by('week').all()

    results = []

    for week_str, count in weekly_counts:
        try:
            # Convert "2025-29" to ISO week start date (Monday of that week)
            year, week = map(int, week_str.split("-"))
            week_start = date.fromisocalendar(year, week, 1)  # Monday
            results.append({
                "week": week_start.isoformat(),
                "count": count
            })
        except Exception as e:
            print("Invalid week format:", week_str, "Error:", e)

    return jsonify(results)

@bp.route("/frequent-actions")
@jwt_required()
def frequent_actions():
    try:
        data = db.session.query(
            AuditLog.action_type.label("action"),
            func.count(AuditLog.id).label("count")
        ).group_by(AuditLog.action_type).order_by(db.desc("count")).all()

        results = [
            {"action": action or "Unknown", "count": count}
            for action, count in data
        ]

        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error in /frequent-actions: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@bp.route("/geo-logins")
@jwt_required()
def geo_logins():
    data = (
        db.session.query(SessionLog.country, func.count())
        .group_by(SessionLog.country)
        .order_by(desc(func.count()))
        .limit(10).all()
    )
    return jsonify([
        {"country": country or "Unknown", "count": count} for country, count in data
    ])


# =======================
# Device, OS, Browser
# =======================

@bp.route("/device-analytics")
@jwt_required()
def device_analytics():
    def get_distribution(column):
        results = db.session.query(column, func.count()).group_by(column).all()
        return [{"label": label or "Unknown", "count": count} for label, count in results]

    return jsonify({
        "devices": get_distribution(SessionLog.device),
        "browsers": get_distribution(SessionLog.browser),
        "os": get_distribution(SessionLog.os),
    })


# =======================
# User-specific & Top Admins
# =======================

@bp.route("/top-admins")
@jwt_required()
def top_admins():
    result = db.session.query(
        User.username,
        func.count(AuditLog.id).label("total")
    ).join(AuditLog, User.id == AuditLog.actor_id
    ).group_by(User.username
    ).order_by(func.count(AuditLog.id).desc()
    ).limit(10).all()

    return jsonify([
        {"username": username, "total": total}
        for username, total in result
    ])


@bp.route("/user-login-history/<int:user_id>")
@jwt_required()
def user_login_history(user_id):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '').lower()

        query = SessionLog.query.filter_by(user_id=user_id)

        if search:
            search_filter = (SessionLog.ip_address.ilike(f"%{search}%")) | \
                            (SessionLog.country.ilike(f"%{search}%")) | \
                            (SessionLog.browser.ilike(f"%{search}%"))
            query = query.filter(search_filter)

        total = query.count()
        logs = query.order_by(SessionLog.login_time.desc()).offset((page - 1) * limit).limit(limit).all()

        results = [{
            "login_time": format_last_login(log.login_time.strftime("%Y-%m-%d %H:%M")) if log.login_time else "N/A",
            "ip": log.ip_address or "N/A",
            "country": log.country or "N/A",
            "device": log.device or "N/A",
            "os": log.os or "N/A",
            "browser": log.browser or "N/A"
        } for log in logs]

        return jsonify({"total": total, "data": results})
    except Exception as e:
        print(f"[ERROR] Failed to fetch login history: {e}")
        return make_response(jsonify({"error": "Internal server error"}), 500)



# =======================
# Recent Logs
# =======================

@bp.route("/recent-audit-logs")
@jwt_required()
def recent_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

    return jsonify([
        {
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M"),
            "actor": log.actor.username,
            "action_type": log.action_type,
            "target": log.target_user.username if log.target_user else None,
            "description": log.description
        }
        for log in logs
    ])

import logging
from sqlalchemy import func, extract, distinct, cast, Date, String
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.tutorial import SubTopic, Session, SubTopicView, SearchQuery, ErrorLog
from app.extensions import db
from user_agents import parse
from datetime import datetime, date
from app.utils.logging_utils import (
    get_country_from_ip,
    format_last_login,
    get_client_ip,
    get_or_create_session
    )


logger = logging.getLogger(__name__)
bp = Blueprint('analytics', __name__)


@bp.route('/session/start', methods=['POST'])
def start_session():
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    user_agent_str = request.headers.get('User-Agent', '')
    user_agent = parse(user_agent_str)

    ip_addr = get_client_ip(request)
    country = get_country_from_ip(ip_addr)

    env_data = {
        'ip_address': ip_addr,
        'browser': user_agent.browser.family,
        'os': user_agent.os.family,
        'device_type': data.get('device_type'),
        'country': country,
    }

    session, created = get_or_create_session(session_id, **env_data)
    if session is None:
        return jsonify({"error": "Failed to start or update session"}), 500

    if created:
        return jsonify({"message": "Session started"}), 201
    else:
        return jsonify({"message": "Session updated"}), 200


@bp.route('/subtopic/view', methods=['POST'])
def record_subtopic_view():
    """
    Record a user's view on a subtopic.
    Expected JSON:
    {
        "session_id": "string",
        "subtopic_id": int,
        "time_spent_seconds": float (optional),
        "scroll_depth_percent": float (optional)
    }
    """
    data = request.get_json() or {}

    session_id = data.get('session_id')
    subtopic_id = data.get('subtopic_id')

    if not session_id or not subtopic_id:
        return jsonify({"error": "session_id and subtopic_id are required"}), 400

    session = Session.query.filter_by(session_id=session_id).first()
    if not session:
        return jsonify({"error": "Session not found"}), 404

    time_spent = data.get('time_spent_seconds')
    scroll_percent = data.get('scroll_depth_percent')

    # if time_spent < 30 or scroll_percent < 25:
    #     return jsonify({"message": "View ignored — not enough engagement"}), 200

    view = SubTopicView(
        subtopic_id=subtopic_id,
        session_id=session.id,
        viewed_at=datetime.now(timezone.utc),
        time_spent_seconds=time_spent,
        scroll_depth_percent=scroll_percent
    )

    db.session.add(view)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error recording subtopic view", exc_info=True)
        return jsonify({"error": "Failed to record view"}), 500

    return jsonify({"message": "Subtopic view recorded"}), 201


@bp.route('/search', methods=['POST'])
def record_search_query():
    """
    Record a user search query.
    Expected JSON:
    {
        "session_id": "string" (optional),
        "query_text": "string"
    }
    """
    data = request.get_json() or {}
    query_text = data.get('query_text')
    if not query_text or not query_text.strip():
        return jsonify({"error": "query_text is required"}), 400

    session = None
    session_id = data.get('session_id')
    if session_id:
        session = Session.query.filter_by(session_id=session_id).first()

    search_query = SearchQuery(
        query_text=query_text.strip(),
        session_id=session.id if session else None,
        searched_at=datetime.now(timezone.utc)
    )

    db.session.add(search_query)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error recording search query", exc_info=True)
        return jsonify({"error": "Failed to record search query"}), 500

    return jsonify({"message": "Search query recorded"}), 201


@bp.route('/error', methods=['POST'])
def record_error_log():
    """
    Log an error encountered by the user.
    Expected JSON:
    {
        "session_id": "string" (optional),
        "error_message": "string",
        "url": "string" (optional),
        "stack_trace": "string" (optional),
        "error_type": "string" (optional)
    }
    """
    data = request.get_json() or {}
    error_message = data.get('error_message')
    if not error_message or not error_message.strip():
        return jsonify({"error": "error_message is required"}), 400

    session = None
    session_id = data.get('session_id')
    if session_id:
        session = Session.query.filter_by(session_id=session_id).first()

    error_log = ErrorLog(
        error_message=error_message.strip(),
        url=data.get('url'),
        stack_trace=data.get('stack_trace'),
        error_type=data.get('error_type'),
        session_id=session.id if session else None,
        logged_at=datetime.now(timezone.utc)
    )

    db.session.add(error_log)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error recording error log", exc_info=True)
        return jsonify({"error": "Failed to record error log"}), 500

    return jsonify({"message": "Error log recorded"}), 201


@bp.route("/metrics", methods=["GET"])
@jwt_required()
def get_summary_metrics():
    today = date.today()

    # Total sessions = proxy for users (unless you have a user model)
    total_users = db.session.query(func.count(Session.id)).scalar()

    # Subtopic views today
    views_today = db.session.query(func.count(SubTopicView.id)) \
        .filter(func.date(SubTopicView.viewed_at) == today).scalar()

    # All subtopics = "Topic Contents"
    total_topic_contents = db.session.query(func.count(SubTopic.id)).scalar()

    # Placeholder blog post count (replace with actual model if exists)
    total_blog_posts = 52  # <-- or query BlogPost table if available

    return jsonify({
        "users": total_users,
        "views_today": views_today,
        "topic_contents": total_topic_contents,
        "blog_posts": total_blog_posts
    })

@bp.route('/engagement-summary', methods=['GET'])
@jwt_required()
def engagement_summary():
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)

    # 🧍 Unique Visitors This Week
    unique_visitors = db.session.query(
        func.count(distinct(Session.session_id))
    ).filter(Session.started_at >= week_start).scalar()

    # 🕐 Peak Activity Hour (e.g., 14 → 2PM)
    peak_hour_data = db.session.query(
        extract('hour', SubTopicView.viewed_at).label('hour'),
        func.count().label('views')
    ).filter(SubTopicView.viewed_at >= week_start) \
     .group_by('hour') \
     .order_by(func.count().desc()) \
     .first()

    peak_hour_range = (
        f"{peak_hour_data.hour}:00 - {peak_hour_data.hour + 1}:00"
        if peak_hour_data else "N/A"
    )

    # 📈 Highest Day of the Week (e.g., Friday)
    peak_day_data = db.session.query(
        extract('dow', SubTopicView.viewed_at).label('day_of_week'),
        func.count().label('views')
    ).filter(SubTopicView.viewed_at >= week_start) \
     .group_by('day_of_week') \
     .order_by(func.count().desc()) \
     .first()

    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    peak_day = (
        day_names[int(peak_day_data.day_of_week)] if peak_day_data else "N/A"
    )

    return jsonify({
        "unique_visitors": unique_visitors,
        "peak_hour_range": peak_hour_range,
        "peak_day": peak_day
    })
@bp.route('/engagement-rate', methods=['GET'])
@jwt_required()
def engagement_rate():
    week_ago = datetime.utcnow() - timedelta(days=7)

    # Total unique visitors in the last week
    total_visitors = db.session.query(
        func.count(distinct(Session.session_id))
    ).filter(Session.started_at >= week_ago).scalar()

    # Unique visitors who viewed at least one subtopic
    engaged_visitors = db.session.query(
        func.count(distinct(SubTopicView.session_id))
    ).filter(SubTopicView.viewed_at >= week_ago).scalar()

    rate = (engaged_visitors / total_visitors * 100) if total_visitors else 0

    return jsonify({
        "engagement_rate_percent": round(rate, 1),
        "engaged_visitors": engaged_visitors,
        "total_visitors": total_visitors
    })

@bp.route('/page-views')
@jwt_required()
def get_page_views():
    range_type = request.args.get('range', 'daily')  # daily, weekly, monthly
    now = datetime.now(timezone.utc)

    if range_type == 'daily':
        since = now - timedelta(days=1)
    elif range_type == 'weekly':
        since = now - timedelta(weeks=1)
    elif range_type == 'monthly':
        since = now - timedelta(days=30)
    else:
        return jsonify({'error': 'Invalid range'}), 400

    views = (
        db.session.query(SubTopic.title, func.count(SubTopicView.id))
        .join(SubTopic, SubTopic.id == SubTopicView.subtopic_id)
        .filter(SubTopicView.viewed_at >= since)
        .group_by(SubTopic.title)
        .limit(10).all()
    )

    return jsonify({
        "views": [
            {"title": title, "views": count}
            for title, count in views
        ]
    })

@bp.route('/daily-trends')
@jwt_required()
def daily_trends():
    range_param = request.args.get('range', '28d')
    range_days_map = {"7d": 7, "28d": 28, "90d": 90, "365d": 365}
    days = range_days_map.get(range_param)
    if days is None:
        return jsonify({"error": "Invalid range value"}), 400

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    results = (
    db.session.query(
        SubTopicView.viewed_at.label('viewed_at'),
        func.count(SubTopicView.id).label('views'),
        func.coalesce(func.sum(SubTopicView.time_spent_seconds), 0).label('time_spent'),
        func.count(func.distinct(SubTopicView.session_id)).label('unique_users')
    )
    .filter(SubTopicView.viewed_at >= start_date)
    .group_by(func.date(SubTopicView.viewed_at))
    .order_by(func.date(SubTopicView.viewed_at))
    .all()
    )

    response = {"labels": [], "views": [], "time_spent": [], "users": []}
    last_date = None
    aggregate = {"views": 0, "time_spent": 0, "users": 0}

    for row in results:
        # Extract date part from datetime
        day = row.viewed_at.date()
        # Prepare the response as usual
        response["labels"].append(format_last_login(day.strftime("%Y-%m-%d")))
        response["views"].append(row.views)
        response["time_spent"].append(row.time_spent)
        response["users"].append(row.unique_users)

    return jsonify(response)

# app/routes/dashboard.py

from flask import Blueprint, render_template, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.tutorial import SubTopic

bp = Blueprint('dashboard', __name__)


# -------------------------------
# Authentication Pages
# -------------------------------

@bp.route('/dcp/auth/login', methods=['GET'])
def login_page():
    """
    Serve the login page for admin users.
    """
    return render_template('dcp/auth/login.html')


# -------------------------------
# Dashboard and Admin Views
# -------------------------------

@bp.route('/dcp/dashboard')
@jwt_required()
def dashboard():
    """
    Render the main admin dashboard view.
    JWT-protected route.
    """
    current_user = get_jwt_identity()

    return render_template("dcp/dashboard.html", user=current_user)


@bp.route('/dcp/admin/topics')
@jwt_required()
def manage_topics():
    """
    Render the admin interface to manage tutorial topics.
    JWT-protected route.
    """
    current_user = get_jwt_identity()
    return render_template("dcp/tutorials/manage_topics.html", user=current_user)


@bp.route('/dcp/admin/<int:topic_id>/subtopics')
@jwt_required()
def manage_subtopics(topic_id):
    """
    Render the admin interface to manage subtopics for a given topic.

    Args:
        topic_id (int): ID of the parent topic.
    """
    return render_template("dcp/tutorials/subtopics.html", topic_id=topic_id)


@bp.route('/dcp/admin/subtopics/create')
@jwt_required()
def create_content():
    """
    Render the subtopic creation/editing interface.

    Query Parameters:
        topic_id (int): Required. ID of the parent topic.
        subtopic_id (int, optional): If provided, pre-loads the subtopic for editing.
    """
    topic_id = request.args.get('topic_id', type=int)
    if topic_id is None:
        return "Topic ID not provided", 400

    subtopic_id = request.args.get('subtopic_id', type=int)
    return render_template(
        "dcp/tutorials/manage_content.html",
        topic_id=topic_id,
        subtopic_id=subtopic_id
    )


# -------------------------------
# Public Tutorial Route
# -------------------------------

@bp.route('/python/<subtopic_slug>')
def show_subtopic_short(subtopic_slug):
    """
    Render a public tutorial subtopic page using the subtopic slug.

    Args:
        subtopic_slug (str): Slug for the subtopic.

    Returns:
        content.html template if subtopic is published, 404 otherwise.
    """
    subtopic = SubTopic.query.filter_by(slug=subtopic_slug, status='published').first()
    if not subtopic:
        abort(404)

    topic = subtopic.topic
    topic_slug = topic.slug if topic else None

    return render_template(
        "frontend/content.html",
        topic_slug=topic_slug,
        subtopic_slug=subtopic_slug
    )
@bp.route('/dcp/auth/users')
@jwt_required()
def user_management():
    """
    Render the main admin dashboard view.
    JWT-protected route.
    """
    current_user = get_jwt_identity()
    return render_template("dcp/user/user_management.html")

from flask import Blueprint, render_template, request, abort
from app.models.tutorial import SubTopic

bp = Blueprint('dashboard', __name__)

# -------------------------------
# DCP Dashboard and Admin Views
# -------------------------------

@bp.route('/dcp/dashboard')
def dashboard():
    """Render the main dashboard view."""
    return render_template("dcp/dashboard.html")


@bp.route('/dcp/admin/topics')
def manage_topics():
    """Render the interface for managing tutorial topics."""
    return render_template("dcp/tutorials/manage_topics.html")


@bp.route('/dcp/admin/<int:topic_id>/subtopics')
def manage_subtopics(topic_id):
    """
    Render the subtopics management interface for a given topic.
    :param topic_id: ID of the parent topic
    """
    return render_template("dcp/tutorials/subtopics.html", topic_id=topic_id)


@bp.route('/dcp/admin/subtopics/create')
def create_content():
    """
    Render the subtopic content creation/editing interface.
    Query Parameters:
        - topic_id (int): Required. ID of the parent topic.
        - subtopic_id (int, optional): ID of the subtopic (for editing).
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
    Render a tutorial subtopic page using only the subtopic slug.
    Automatically resolves the associated topic slug for API and template use.
    """
    subtopic = SubTopic.query.filter_by(slug=subtopic_slug, status='published').first()
    if not subtopic:
        abort(404)

    topic = subtopic.topic  # Requires proper relationship definition
    topic_slug = topic.slug if topic else None

    return render_template(
        "frontend/content.html",
        topic_slug=topic_slug,
        subtopic_slug=subtopic_slug
    )

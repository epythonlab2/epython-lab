from flask import Blueprint, render_template, request, abort

bp = Blueprint('dashboard', __name__)

@bp.route('/dcp/dashboard')
def dashboard():
    return render_template("dcp/dashboard.html")


@bp.route('/dcp/admin/topics')
def manage_topics():
    return render_template("dcp/tutorials/manage_topics.html")


@bp.route('/dcp/admin/<int:topic_id>/subtopics')
def manage_subtopics(topic_id):
    # topic_id is available; render subtopics list
    return render_template("dcp/tutorials/subtopics.html", topic_id=topic_id)


@bp.route('/dcp/admin/subtopics/create')
def create_content():
    # Always pick up topic_id from the query string
    topic_id = request.args.get('topic_id', type=int)
    if topic_id is None:
        return "Topic ID not provided", 400

    # Also pick up subtopic_id if this is "edit" mode
    subtopic_id = request.args.get('subtopic_id', type=int)

    return render_template(
        "dcp/tutorials/manage_content.html",
        topic_id=topic_id,
        subtopic_id=subtopic_id
    )

@bp.route('/python/<topic_slug>/<subtopic_slug>')
def show_subtopic(topic_slug, subtopic_slug):
    print(topic_slug) # e.g introduction
    return render_template("frontend/content.html", topic_slug=topic_slug, subtopic_slug=subtopic_slug)

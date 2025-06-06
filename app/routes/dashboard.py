from flask import Blueprint, render_template, request

bp = Blueprint('dashboard', __name__)

@bp.route('/dcp/dashboard')
def dashboard():
       return render_template("/dcp/dashboard.html")


@bp.route('/dcp/admin/topics')
def manage_topics():

    return render_template("/dcp/tutorials/manage_topics.html")

@bp.route('/dcp/admin/<int:topic_id>/subtopics')
def manage_subtopics(topic_id):
       print(topic_id) #1
       
       return render_template("/dcp/tutorials/subtopics.html", topic_id=topic_id)

@bp.route('/dcp/admin/subtopics/create')
def create_content():
    topic_id = request.args.get('topic_id', type=int)
    print(topic_id)  # Should print the correct ID if provided

    if topic_id is None:
        return "Topic ID not provided", 400

    return render_template("/dcp/tutorials/manage_content.html", topic_id=topic_id)
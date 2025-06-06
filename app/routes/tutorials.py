from flask import Blueprint, request, jsonify, abort
from app.models.tutorial import db, Topic, SubTopic, Quiz
from schemas import TopicSchema, SubTopicSchema, QuizSchema
from datetime import datetime, timezone

bp = Blueprint('tutorials', __name__, url_prefix='/api/v1/topics')

# ----------------------------------------
# TOPIC ENDPOINTS
# ----------------------------------------

@bp.route('/', methods=['GET'])
def get_all_topics():
    """
    Fetch all topics with pagination.
    Query params: page (default=1), limit (default=5)
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
    except ValueError:
        page, limit = 1, 5

    pagination = Topic.query.paginate(page=page, per_page=limit, error_out=False)
    topics = pagination.items

    topics_data = TopicSchema(many=True).dump(topics)

    return jsonify({
        'topics':      topics_data,
        'page':        page,
        'total_pages': pagination.pages,
        'total_items': pagination.total
    }), 200


@bp.route('/', methods=['POST'])
def create_topic():
    """
    Create a new topic. Expects JSON payload with 'title'.
    """
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    new_topic = Topic(
        title      = data['title'].strip(),
        created_at = datetime.now(timezone.utc)
    )
    db.session.add(new_topic)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify(TopicSchema().dump(new_topic)), 201


@bp.route('/<int:topic_id>', methods=['GET'])
def get_topic_detail(topic_id):
    """
    Retrieve a single topic, including its subtopics and quizzes.
    """
    topic = Topic.query.get_or_404(topic_id)
    topic_data = TopicSchema().dump(topic)

    subtopics = SubTopic.query.filter_by(topic_id=topic_id).all()
    topic_data['subtopics'] = SubTopicSchema(many=True).dump(subtopics)

    for sub in topic_data['subtopics']:
        quizzes = Quiz.query.filter_by(subtopic_id=sub['id']).all()
        sub['quizzes'] = QuizSchema(many=True).dump(quizzes)

    return jsonify(topic_data), 200


@bp.route('/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    """
    Update an existing topic's title. Expects JSON payload with 'title'.
    """
    topic = Topic.query.get_or_404(topic_id)
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    topic.title = data['title'].strip()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({
        'message': 'Topic updated successfully',
        'topic':   TopicSchema().dump(topic)
    }), 200


@bp.route('/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    """
    Delete a topic and cascade-delete its subtopics and quizzes (if configured).
    """
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'message': 'Topic deleted successfully'}), 200


# ----------------------------------------
# SUBTOPIC (CONTENT) ENDPOINTS
# ----------------------------------------

@bp.route('/<int:topic_id>/subtopics', methods=['POST'])
def create_content(topic_id):
    """
    Create a new subtopic (content) under the specified topic.
    Expects JSON: { title, content, status (optional), code_snippet (optional) }.
    """
    # Ensure parent topic exists
    Topic.query.get_or_404(topic_id)

    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Both title and content are required'}), 400

    new_subtopic = SubTopic(
        title        = data['title'].strip(),
        content      = data['content'].strip(),
        status       = data.get('status', 'draft'),
        code_snippet = data.get('code_snippet', None),
        topic_id     = topic_id
    )
    db.session.add(new_subtopic)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify(SubTopicSchema().dump(new_subtopic)), 201


@bp.route('/subtopic/<int:subtopic_id>', methods=['GET'])
def get_single_subtopic(subtopic_id):
    """
    Fetch a single subtopic by its ID.
    """
    sub = SubTopic.query.get_or_404(subtopic_id)
    return jsonify(SubTopicSchema().dump(sub)), 200


@bp.route('/subtopic/<int:subtopic_id>', methods=['PUT'])
def update_content(subtopic_id):
    """
    Update an existing subtopic. Expects JSON: { title, content, status, code_snippet }.
    """
    subtopic = SubTopic.query.get_or_404(subtopic_id)
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Both title and content are required'}), 400

    subtopic.title        = data['title'].strip()
    subtopic.content      = data['content'].strip()
    subtopic.status       = data.get('status', subtopic.status)
    subtopic.code_snippet = data.get('code_snippet', subtopic.code_snippet)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({
        'message':  'Content updated successfully',
        'subtopic': SubTopicSchema().dump(subtopic)
    }), 200


@bp.route('/subtopic/<int:subtopic_id>', methods=['DELETE'])
def delete_content(subtopic_id):
    """
    Delete a subtopic and cascade-delete its quizzes (if configured).
    """
    subtopic = SubTopic.query.get_or_404(subtopic_id)
    db.session.delete(subtopic)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'message': 'Subtopic deleted successfully'}), 200


# ----------------------------------------
# QUIZ ENDPOINTS
# ----------------------------------------

@bp.route('/subtopics/<int:subtopic_id>/quizzes', methods=['POST'])
def add_quizzes(subtopic_id):
    """
    Add multiple quizzes under a specific subtopic.
    Expects JSON array of objects with fields:
    { question, option_a, option_b, option_c, option_d, correct_answer }
    """
    # Ensure parent subtopic exists
    SubTopic.query.get_or_404(subtopic_id)

    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of quizzes'}), 400

    required_fields = {
        'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'
    }
    quizzes_to_add = []

    for i, item in enumerate(data):
        if not isinstance(item, dict) or not required_fields.issubset(item):
            return jsonify({'error': f'Missing fields in quiz at index {i}'}), 400

        quiz = Quiz(
            question       = item['question'].strip(),
            option_a       = item['option_a'].strip(),
            option_b       = item['option_b'].strip(),
            option_c       = item['option_c'].strip(),
            option_d       = item['option_d'].strip(),
            correct_answer = item['correct_answer'].strip(),
            subtopic_id    = subtopic_id
        )
        quizzes_to_add.append(quiz)
        db.session.add(quiz)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'message': 'Quizzes added successfully'}), 201

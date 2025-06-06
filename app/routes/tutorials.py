from flask import Blueprint, request, jsonify
from app.models.tutorial import db, Topic, SubTopic, Quiz
from schemas import TopicSchema, SubTopicSchema, QuizSchema
from datetime import datetime, timezone

bp = Blueprint('tutorials', __name__, url_prefix='/api/v1/topics')

# Fetch all topics
@bp.route('/', methods=['GET'])
def get_all_topics():
    # Get query parameters for pagination, default page=1, limit=10
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 5))
    except ValueError:
        # fallback to defaults if invalid input
        page = 1
        limit = 10

    # Query with pagination
    pagination = Topic.query.paginate(page=page, per_page=limit, error_out=False)

    topics = pagination.items
    total_pages = pagination.pages
    total_items = pagination.total

    # Serialize topics
    topics_data = TopicSchema(many=True).dump(topics)

    # Compose response with pagination info
    response = {
        "topics": topics_data,
        "page": page,
        "total_pages": total_pages,
        "total_items": total_items
    }

    return jsonify(response), 200

# Create a new topic
@bp.route('/', methods=['POST'])
def create_topic():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    topic = Topic(title=data['title'], created_at=datetime.now(timezone.utc))
    db.session.add(topic)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500
    
    return jsonify(TopicSchema().dump(topic)), 201


# Update an existing topic
@bp.route('/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    topic.title = data['title']
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500
    
    return jsonify({'message': 'Topic updated successfully', 'topic': TopicSchema().dump(topic)}), 200


# Delete a topic (and cascade delete its subtopics and quizzes if set in model)
@bp.route('/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)
    db.session.commit()
    return jsonify({'message': 'Topic deleted successfully'}), 200


# Get a single topic (with subtopics and optionally quizzes)
@bp.route('/<int:topic_id>', methods=['GET'])
def get_topic_detail(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    topic_data = TopicSchema().dump(topic)
    
    subtopics = SubTopic.query.filter_by(topic_id=topic_id).all()
    topic_data['subtopics'] = SubTopicSchema(many=True).dump(subtopics)

    for sub in topic_data['subtopics']:
        quizzes = Quiz.query.filter_by(subtopic_id=sub['id']).all()
        sub['quizzes'] = QuizSchema(many=True).dump(quizzes)

    return jsonify(topic_data), 200


# Add content under a topic
@bp.route('/<int:topic_id>/subtopics', methods=['POST'])
def create_content(topic_id):
    data = request.json
    sub = SubTopic(
        title=data['title'],
        content=data['content'],
        status=data.get('status', 'draft'),  # Default to 'draft' if not provided
        topic_id=topic_id
    )
    db.session.add(sub)
    db.session.commit()
    return jsonify({'message': 'Content Created'}), 201


# Add quizzes to a subtopic
@bp.route('/subtopics/<int:subtopic_id>/quizzes', methods=['POST'])
def add_quizzes(subtopic_id):
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of quizzes'}), 400
    
    required_fields = {'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'}
    for i, q in enumerate(data):
        if not all(field in q for field in required_fields):
            return jsonify({'error': f'Missing fields in quiz index {i}'}), 400
        quiz = Quiz(
            question=q['question'],
            option_a=q['option_a'],
            option_b=q['option_b'],
            option_c=q['option_c'],
            option_d=q['option_d'],
            correct_answer=q['correct_answer'],
            subtopic_id=subtopic_id
        )
        db.session.add(quiz)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500
    
    return jsonify({'message': 'Quizzes added'}), 201

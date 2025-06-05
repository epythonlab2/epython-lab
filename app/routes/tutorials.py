from flask import Blueprint, request, jsonify
from app.models.tutorial import db, Topic, SubTopic, Quiz
from schemas import TopicSchema, SubTopicSchema, QuizSchema

bp = Blueprint('tutorials', __name__, url_prefix='/api/tutorials')

# Fetch all topics
@bp.route('/', methods=['GET'])
def get_all_topics():
    topics = Topic.query.all()
    return jsonify(TopicSchema(many=True).dump(topics)), 200

# Create a new topic
@bp.route('/', methods=['POST'])
def create_topic():
    data = request.json
    topic = Topic(title=data['title'])
    db.session.add(topic)
    db.session.commit()
    return jsonify(TopicSchema().dump(topic)), 201

# Update an existing topic
@bp.route('/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    data = request.json
    topic.title = data['title']
    db.session.commit()
    return jsonify({'message': 'Topic updated successfully'}), 200

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

    # Optional: Include quizzes nested within each subtopic
    for sub in topic_data['subtopics']:
        quizzes = Quiz.query.filter_by(subtopic_id=sub['id']).all()
        sub['quizzes'] = QuizSchema(many=True).dump(quizzes)

    return jsonify(topic_data), 200

# Add subtopic under a topic
@bp.route('/<int:topic_id>/subtopics', methods=['POST'])
def add_subtopic(topic_id):
    data = request.json
    sub = SubTopic(
        title=data['title'],
        content=data['content'],
        code_snippet=data.get('code_snippet'),
        topic_id=topic_id
    )
    db.session.add(sub)
    db.session.commit()
    return jsonify({'message': 'Subtopic added'}), 201

# Add quizzes to a subtopic
@bp.route('/subtopics/<int:subtopic_id>/quizzes', methods=['POST'])
def add_quizzes(subtopic_id):
    data = request.json  # Expecting a list of 10 quiz dicts
    for q in data:
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
    db.session.commit()
    return jsonify({'message': 'Quizzes added'}), 201

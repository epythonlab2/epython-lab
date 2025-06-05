from flask import Blueprint, request, jsonify
from app.models.tutorial import db, Topic, SubTopic, Quiz
from schemas import TopicSchema

bp = Blueprint('tutorials', __name__, url_prefix='/api/tutorials')

@bp.route('/', methods=['GET'])
def get_all_topics():
    topics = Topic.query.all()
    return jsonify(TopicSchema(many=True).dump(topics))

@bp.route('/', methods=['POST'])
def create_topic():
    data = request.json
    topic = Topic(title=data['title'])
    db.session.add(topic)
    db.session.commit()
    return jsonify(TopicSchema().dump(topic)), 201

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

import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required

from app.models.tutorial import db, Topic, SubTopic, Quiz
from app.routes.schemas import TopicSchema, SubTopicSchema, QuizSchema
from app.routes.utils import slugify

bp = Blueprint('tutorials', __name__)
logger = logging.getLogger(__name__)


def get_subtopic_by_slug(topic_slug: str, subtopic_slug: str) -> SubTopic | None:
    """Retrieve a published SubTopic by topic and subtopic slug."""
    return (
        SubTopic.query
        .join(Topic)
        .filter(
            Topic.slug == topic_slug,
            SubTopic.slug == subtopic_slug,
            SubTopic.status == 'published'
        )
        .first()
    )


# -----------------------
# TOPIC ENDPOINTS
# -----------------------

@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_topics():
    """
    Retrieve paginated list of topics.
    Query parameters:
      - page (int, default=1)
      - limit (int, default=5)
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
        'topics': topics_data,
        'page': page,
        'total_pages': pagination.pages,
        'total_items': pagination.total
    }), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_topic():
    """Create a new Topic."""
    json_data = request.get_json()
    if not json_data:
        logger.error("Create Topic failed: No input data provided")
        return jsonify({"error": "No input data provided"}), 400

    schema = TopicSchema()
    try:
        validated = schema.load(json_data)
    except ValidationError as err:
        logger.error(f"Create Topic validation error: {err.messages}")
        return jsonify({"errors": err.messages}), 400

    validated['slug'] = slugify(validated['title'])
    validated['created_at'] = datetime.now(timezone.utc)

    topic = Topic(**validated)
    db.session.add(topic)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error during Topic creation", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify(schema.dump(topic)), 201


@bp.route('/<int:topic_id>', methods=['GET'])
@jwt_required()
def get_topic_detail(topic_id: int):
    """Retrieve a Topic with its subtopics and quizzes."""
    topic = Topic.query.get_or_404(topic_id)
    topic_data = TopicSchema().dump(topic)

    subtopics = SubTopic.query.filter_by(topic_id=topic_id).all()
    topic_data['subtopics'] = SubTopicSchema(many=True).dump(subtopics)

    for sub in topic_data['subtopics']:
        quizzes = Quiz.query.filter_by(subtopic_id=sub['id']).all()
        sub['quizzes'] = QuizSchema(many=True).dump(quizzes)

    return jsonify(topic_data), 200


@bp.route('/<int:topic_id>', methods=['PUT'])
@jwt_required()
def update_topic(topic_id: int):
    """Update an existing Topic's title."""
    topic = Topic.query.get_or_404(topic_id)
    json_data = request.get_json()
    if not json_data:
        logger.error("Update Topic failed: No input data provided")
        return jsonify({"error": "No input data provided"}), 400

    schema = TopicSchema(partial=True)
    try:
        validated = schema.load(json_data, partial=True)
    except ValidationError as err:
        logger.error(f"Update Topic validation error: {err.messages}")
        return jsonify({"errors": err.messages}), 400

    if 'title' in validated:
        topic.title = validated['title'].strip()
        topic.slug = slugify(topic.title)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error during Topic update", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({
        "message": "Topic updated successfully",
        "topic": TopicSchema().dump(topic)
    }), 200


@bp.route('/<int:topic_id>', methods=['DELETE'])
@jwt_required()
def delete_topic(topic_id: int):
    """Delete a Topic (cascades subtopics and quizzes if configured)."""
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error during Topic deletion", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({"message": "Topic deleted successfully"}), 200


# -----------------------
# SUBTOPIC ENDPOINTS
# -----------------------

@bp.route('/<int:topic_id>/subtopics', methods=['POST'])
@jwt_required()
def create_content(topic_id: int):
    """Create a new SubTopic under specified Topic."""
    Topic.query.get_or_404(topic_id)

    json_data = request.get_json()
    if not json_data:
        logger.error("Create SubTopic failed: No input data provided")
        return jsonify({"error": "No input data provided"}), 400

    # Use snake_case key for schema validation
    json_data['topicId'] = topic_id

    schema = SubTopicSchema()
    try:
        validated = schema.load(json_data)
    except ValidationError as err:
        logger.error(f"Create SubTopic validation error: {err.messages}")
        return jsonify({"errors": err.messages}), 400

    validated['slug'] = slugify(validated['title'])

    subtopic = SubTopic(**validated)
    db.session.add(subtopic)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error during SubTopic creation", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify(schema.dump(subtopic)), 201


@bp.route('/subtopic/<int:subtopic_id>', methods=['GET'])
@jwt_required()
def get_single_subtopic(subtopic_id: int):
    """Retrieve a single SubTopic by ID."""
    subtopic = SubTopic.query.get_or_404(subtopic_id)
    return jsonify(SubTopicSchema().dump(subtopic)), 200


@bp.route('/subtopic/<int:subtopic_id>', methods=['PUT'])
@jwt_required()
def update_content(subtopic_id: int):
    """Update an existing SubTopic."""
    subtopic = SubTopic.query.get_or_404(subtopic_id)
    json_data = request.get_json()
    if not json_data:
        logger.error("Update SubTopic failed: No input data provided")
        return jsonify({"error": "No input data provided"}), 400

    schema = SubTopicSchema(partial=True)
    try:
        validated = schema.load(json_data, partial=True)
    except ValidationError as err:
        logger.error(f"Update SubTopic validation error: {err.messages}")
        return jsonify({"errors": err.messages}), 400

    if 'title' in validated:
        validated['slug'] = slugify(validated['title'])

    for key, value in validated.items():
        setattr(subtopic, key, value)

    subtopic.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error during SubTopic update", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({
        "message": "Content updated successfully",
        "subtopic": schema.dump(subtopic)
    }), 200


@bp.route('/subtopic/<int:subtopic_id>', methods=['DELETE'])
@jwt_required()
def delete_content(subtopic_id: int):
    """Delete a SubTopic."""
    subtopic = SubTopic.query.get_or_404(subtopic_id)
    db.session.delete(subtopic)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error during SubTopic deletion", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({"message": "Subtopic deleted successfully"}), 200


# -----------------------
# CLIENT-FACING ENDPOINTS
# -----------------------

@bp.route('/sidebar', methods=['GET'])
def get_sidebar_topics():
    """Get all topics with published subtopics for sidebar display."""
    topics = Topic.query.all()
    result = []
    for topic in topics:
        result.append({
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "subtopics": [
                {"id": st.id, "title": st.title, "slug": st.slug}
                for st in topic.subtopics if st.status == 'published'
            ]
        })
    return jsonify(result)


@bp.route('/<string:topic_slug>/<string:subtopic_slug>', methods=['GET'])
def get_subtopic_content(topic_slug: str, subtopic_slug: str):
    """Retrieve content of a published SubTopic by topic and subtopic slugs, and next subtopic slug."""
    subtopic = get_subtopic_by_slug(topic_slug, subtopic_slug)
    if not subtopic:
        return jsonify({"error": "Subtopic not found"}), 404

    topic = subtopic.topic
    all_subtopics = SubTopic.query.filter_by(status='published').order_by(SubTopic.id.asc()).all()
    all_subtopic_slugs = [st.slug for st in all_subtopics]

    next_subtopic = (
        SubTopic.query
        .filter(SubTopic.topic_id == topic.id, SubTopic.status == 'published', SubTopic.id > subtopic.id)
        .order_by(SubTopic.id.asc())
        .first()
    )

    if not next_subtopic:
        next_topic = Topic.query.filter(Topic.id > topic.id).order_by(Topic.id.asc()).first()
        if next_topic:
            next_subtopic = (
                SubTopic.query
                .filter_by(topic_id=next_topic.id, status='published')
                .order_by(SubTopic.id.asc())
                .first()
            )

    return jsonify({
        "title": subtopic.title,
        "content": subtopic.content,
        "all_subtopics": all_subtopic_slugs,
        "next_subtopic_slug": next_subtopic.slug if next_subtopic else None
    }), 200


@bp.route('/search')
def search():
    """Search topics and subtopics by query string."""
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    results = []

    matched_topics = Topic.query.filter(Topic.title.ilike(f'%{query}%')).all()
    for topic in matched_topics:
        results.append({
            "type": "topic",
            "id": topic.id,
            "name": topic.title,
            "slug": topic.slug
        })
        for sub in topic.subtopics:
            if sub.status == "published":
                results.append({
                    "type": "subtopic",
                    "id": sub.id,
                    "name": sub.title,
                    "subtopic_slug": sub.slug,
                    "topic_id": topic.id,
                    "topic_name": topic.title,
                    "topic_slug": topic.slug
                })

    matched_subtopics = SubTopic.query.filter(SubTopic.title.ilike(f'%{query}%')).all()
    for sub in matched_subtopics:
        if sub.status == "published":
            results.append({
                "type": "subtopic",
                "id": sub.id,
                "name": sub.title,
                "subtopic_slug": sub.slug,
                "topic_id": sub.topic.id,
                "topic_name": sub.topic.title,
                "topic_slug": sub.topic.slug
            })

    return jsonify(results), 200


@bp.route("/subtopics/<subtopic_slug>/resolve-topic")
def resolve_topic_from_subtopic(subtopic_slug: str):
    """Resolve and return the topic slug from a subtopic slug."""
    subtopic = SubTopic.query.filter_by(slug=subtopic_slug, status='published').first()
    if not subtopic:
        return jsonify({"error": "Subtopic not found"}), 404

    return jsonify({"topic_slug": subtopic.topic.slug})


# -----------------------
# QUIZ ENDPOINTS
# -----------------------

@bp.route('/subtopics/<int:subtopic_id>/quizzes', methods=['POST'])
def add_quizzes(subtopic_id: int):
    """Add multiple quizzes to a subtopic."""
    SubTopic.query.get_or_404(subtopic_id)

    data = request.get_json()
    if not isinstance(data, list):
        logger.error("Add Quizzes failed: Expected a list of quizzes")
        return jsonify({"error": "Expected a list of quizzes"}), 400

    required_fields = {'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'}

    for i, quiz in enumerate(data):
        if not isinstance(quiz, dict) or not required_fields.issubset(quiz):
            logger.error(f"Add Quizzes failed: Missing fields in quiz at index {i}")
            return jsonify({"error": f"Missing fields in quiz at index {i}"}), 400

    quizzes = []
    for quiz in data:
        q = Quiz(
            question=quiz['question'].strip(),
            option_a=quiz['option_a'].strip(),
            option_b=quiz['option_b'].strip(),
            option_c=quiz['option_c'].strip(),
            option_d=quiz['option_d'].strip(),
            correct_answer=quiz['correct_answer'].strip(),
            subtopic_id=subtopic_id
        )
        quizzes.append(q)
        db.session.add(q)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Database error during Quizzes addition", exc_info=True)
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({"message": "Quizzes added successfully"}), 201

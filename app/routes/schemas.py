from marshmallow import Schema, fields, validate

class TopicSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, error="Title must be at least 3 characters")
    )
    slug = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)  # add if you track updates

class SubTopicSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, error="Title must be at least 3 characters")
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=10, error="Content must be at least 10 characters")
    )
    slug = fields.Str(dump_only=True)
    status = fields.Str(
        validate=validate.OneOf(["draft", "published"], error="Status must be 'draft' or 'published'"),
        load_default="draft"
    )
    topic_id = fields.Int(required=True, data_key="topicId")
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class QuizSchema(Schema):
    id = fields.Int(dump_only=True)
    question = fields.Str(
        required=True,
        validate=validate.Length(min=5, error="Question must be at least 5 characters")
    )
    option_a = fields.Str(required=True, validate=validate.Length(min=1))
    option_b = fields.Str(required=True, validate=validate.Length(min=1))
    option_c = fields.Str(required=True, validate=validate.Length(min=1))
    option_d = fields.Str(required=True, validate=validate.Length(min=1))
    correct_answer = fields.Str(
        required=True,
        validate=validate.OneOf(['a', 'b', 'c', 'd'], error="Correct answer must be one of 'a', 'b', 'c', 'd'")
    )
    subtopic_id = fields.Int(required=True)

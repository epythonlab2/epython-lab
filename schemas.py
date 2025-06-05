from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.tutorial import Topic, SubTopic, Quiz

class QuizSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Quiz
        load_instance = True

class SubTopicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SubTopic
        include_relationships = True
        load_instance = True
    quizzes = QuizSchema(many=True)

class TopicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Topic
        include_relationships = True
        load_instance = True
    subtopics = SubTopicSchema(many=True)

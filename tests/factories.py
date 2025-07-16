import factory
from app.models.user import User, Role
from app.models.tutorial import Topic, SubTopic, Quiz
from app.extensions import db


class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Role
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: f"role{n}")


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        pwd = extracted or "defaultpassword"
        self.set_password(pwd)

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for role in extracted:
                self.roles.append(role)

class TopicFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Topic
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    title = factory.Sequence(lambda n: f"Topic {n}")
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(" ", "-"))

class SubTopicFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SubTopic
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    title = factory.Sequence(lambda n: f"SubTopic {n}")
    content = "Some sample content"
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(" ", "-"))
    topic = factory.SubFactory(TopicFactory)  # Link to a Topic

class QuizFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Quiz
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    question = factory.Sequence(lambda n: f"Question {n+1}")
    option_a = "A"
    option_b = "B"
    option_c = "C"
    option_d = "D"
    correct_answer = "A"
    subtopic = factory.SubFactory(SubTopicFactory)  # Link to a SubTopic

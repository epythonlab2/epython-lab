import unittest
from app import create_app, db
from app.models.tutorial import Topic, SubTopic, Quiz
from sqlalchemy import inspect

class TutorialsApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        engine = db.engine
        if inspect(engine).dialect.name == 'sqlite':
            engine.dispose()
        self.app_context.pop()

    def test_create_and_get_topic(self):
        response = self.client.post('/api/v1/tutorials/', json={"title": "Python Basics"})
        self.assertEqual(response.status_code, 201)

        get_response = self.client.get('/api/v1/tutorials/')
        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Python Basics", get_response.get_data(as_text=True))

    def test_add_subtopic(self):
        topic = Topic(title="Flask")
        db.session.add(topic)
        db.session.commit()

        response = self.client.post(f'/api/v1/tutorials/{topic.id}/subtopics', json={
            "title": "Routing",
            "content": "How Flask routes requests",
            "code_snippet": "@app.route('/')"
        })
        self.assertEqual(response.status_code, 201)

    def test_add_quizzes(self):
        topic = Topic(title="Testing")
        db.session.add(topic)
        db.session.commit()

        sub = SubTopic(title="UnitTest", content="Testing in Python", topic_id=topic.id)
        db.session.add(sub)
        db.session.commit()

        quizzes = [{
            "question": f"Question {i+1}",
            "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
            "correct_answer": "A"
        } for i in range(10)]

        response = self.client.post(f'/api/v1/tutorials/subtopics/{sub.id}/quizzes', json=quizzes)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Quizzes added", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()

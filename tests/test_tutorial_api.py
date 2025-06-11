import unittest
from app import create_app, db
from app.models.tutorial import Topic, SubTopic, Quiz
from sqlalchemy import inspect
import json

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
        # Test topic creation
        response = self.client.post('/api/v1/topics/', json={"title": "Python Basics"})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['title'], "Python Basics")
        self.assertIn('slug', data)

        # Test get all topics (pagination defaults)
        get_response = self.client.get('/api/v1/topics/')
        self.assertEqual(get_response.status_code, 200)
        get_data = get_response.get_json()
        self.assertIn('topics', get_data)
        self.assertEqual(get_data['page'], 1)
        self.assertGreaterEqual(get_data['total_items'], 1)
        self.assertTrue(any(topic['title'] == "Python Basics" for topic in get_data['topics']))

    def test_create_topic_missing_title(self):
        response = self.client.post('/api/v1/topics/', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    def test_add_subtopic(self):
        # Setup topic
        topic = Topic(title="Flask", slug="flask")
        db.session.add(topic)
        db.session.commit()

        payload = {
            "title": "Routing",
            "content": "How Flask routes requests",
            "code_snippet": "@app.route('/')"
        }
        response = self.client.post(f'/api/v1/topics/{topic.id}/subtopics', json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['title'], "Routing")
        self.assertEqual(data['content'], "How Flask routes requests")
        self.assertIn('slug', data)

    def test_add_subtopic_missing_fields(self):
        topic = Topic(title="Flask", slug="flask")
        db.session.add(topic)
        db.session.commit()

        response = self.client.post(f'/api/v1/topics/{topic.id}/subtopics', json={"title": "Incomplete"})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    def test_add_quizzes(self):
        # Setup topic and subtopic
        topic = Topic(title="Testing", slug="testing")
        db.session.add(topic)
        db.session.commit()

        sub = SubTopic(title="UnitTest", content="Testing in Python", topic_id=topic.id, slug="unittest")
        db.session.add(sub)
        db.session.commit()

        quizzes = [{
            "question": f"Question {i+1}",
            "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
            "correct_answer": "A"
        } for i in range(10)]

        response = self.client.post(f'/api/v1/topics/subtopics/{sub.id}/quizzes', json=quizzes)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Quizzes added", response.get_data(as_text=True))

    def test_add_quizzes_invalid_payload(self):
        topic = Topic(title="Testing", slug="testing")
        db.session.add(topic)
        db.session.commit()

        sub = SubTopic(title="UnitTest", content="Testing in Python", topic_id=topic.id, slug="unittest")
        db.session.add(sub)
        db.session.commit()

        # Sending a dict instead of list should fail
        response = self.client.post(f'/api/v1/topics/subtopics/{sub.id}/quizzes', json={"question": "Invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

        # Missing required fields in quiz item
        invalid_quizzes = [{"question": "Q1"}]  # Missing other fields
        response = self.client.post(f'/api/v1/topics/subtopics/{sub.id}/quizzes', json=invalid_quizzes)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

if __name__ == '__main__':
    unittest.main()

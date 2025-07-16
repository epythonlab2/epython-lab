import pytest
from app.models.tutorial import Topic

@pytest.mark.usefixtures('client', 'auth_headers')
class TestTutorialsApi:

    def test_create_topic(self, client, auth_headers):
        response = client.post('/api/v1/topics/', json={"title": "Python Basics"}, headers=auth_headers)
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == "Python Basics"
        assert 'slug' in data

        # Test get all topics
        get_resp = client.get('/api/v1/topics/')
        assert get_resp.status_code == 200
        get_data = get_resp.get_json()
        assert 'topics' in get_data
        assert any(t['title'] == "Python Basics" for t in get_data['topics'])

    def test_create_topic_missing_title(self, client, auth_headers):
        resp = client.post('/api/v1/topics/', json={}, headers=auth_headers)
        assert resp.status_code == 400
        assert 'error' in resp.get_json()

    def test_add_subtopic(self, client, auth_headers):
        # Create topic
        topic_resp = client.post('/api/v1/topics/', json={"title": "Flask"}, headers=auth_headers)
        assert topic_resp.status_code == 201
        topic_id = topic_resp.get_json()['id']

        payload = {
            "title": "Routing",
            "content": "How Flask routes requests",
            # Avoid code_snippet as per your preference
        }
        sub_resp = client.post(f'/api/v1/topics/{topic_id}/subtopics', json=payload, headers=auth_headers)
        assert sub_resp.status_code == 201
        data = sub_resp.get_json()
        assert data['title'] == "Routing"
        assert 'slug' in data

    def test_add_subtopic_missing_fields(self, client, auth_headers):
        topic_resp = client.post('/api/v1/topics/', json={"title": "Flask"}, headers=auth_headers)
        assert topic_resp.status_code == 201
        topic_id = topic_resp.get_json()['id']

        # Create subtopic
        sub_payload = {
            "title": "UnitTest"
        }

        resp = client.post(f'/api/v1/topics/{topic_id}/subtopics', json=sub_payload, headers=auth_headers)
        assert resp.status_code == 400
        assert 'errors' in resp.get_json()
        assert 'content' in resp.get_json()['errors']

    def test_add_quizzes(self, client, auth_headers):
        # Create topic
        topic_resp = client.post('/api/v1/topics/', json={"title": "Testing"}, headers=auth_headers)
        assert topic_resp.status_code == 201
        topic_id = topic_resp.get_json()['id']

        # Create subtopic
        sub_payload = {
            "title": "UnitTest",
            "content": "Testing in Python"
        }
        sub_resp = client.post(f'/api/v1/topics/{topic_id}/subtopics', json=sub_payload, headers=auth_headers)
        assert sub_resp.status_code == 201
        sub_id = sub_resp.get_json()['id']

        quizzes = [{
            "question": f"Question {i+1}",
            "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
            "correct_answer": "A"
        } for i in range(10)]

        quiz_resp = client.post(f'/api/v1/topics/subtopics/{sub_id}/quizzes', json=quizzes, headers=auth_headers)
        assert quiz_resp.status_code == 201
        assert "Quizzes added" in quiz_resp.get_data(as_text=True)

    def test_add_quizzes_invalid_payload(self, client, auth_headers):
        topic_resp = client.post('/api/v1/topics/', json={"title": "Testing"}, headers=auth_headers)
        assert topic_resp.status_code == 201
        topic_id = topic_resp.get_json()['id']

        sub_payload = {
            "title": "UnitTest",
            "content": "Testing in Python"
        }
        sub_resp = client.post(f'/api/v1/topics/{topic_id}/subtopics', json=sub_payload, headers=auth_headers)
        assert sub_resp.status_code == 201
        sub_id = sub_resp.get_json()['id']

        # Sending dict instead of list - should fail
        resp = client.post(f'/api/v1/topics/subtopics/{sub_id}/quizzes', json={"question": "Invalid"}, headers=auth_headers)
        assert resp.status_code == 400
        assert 'error' in resp.get_json()

        # Missing required fields in quiz
        invalid_quizzes = [{"question": "Q1"}]
        resp = client.post(f'/api/v1/topics/subtopics/{sub_id}/quizzes', json=invalid_quizzes, headers=auth_headers)
        assert resp.status_code == 400
        assert 'error' in resp.get_json()

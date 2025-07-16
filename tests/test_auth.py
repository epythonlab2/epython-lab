import pytest
from app.models.user import User, Role


def test_register_user_success(client, db, auth_headers):
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'StrongPass123!',
        'role': 'viewer'
    }
    resp = client.post('/api/v1/auth/users/create', json=data, headers=auth_headers)
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert json_data['user']['username'] == 'newuser'
    assert json_data['user']['role'] == 'viewer'


def test_register_duplicate_username_or_email(client, db, auth_headers):
    # Create initial user
    client.post('/api/v1/auth/users/create', json={
        'username': 'dupuser',
        'email': 'dup@example.com',
        'password': 'pass',
        'role': 'viewer'
    }, headers=auth_headers)

    # Duplicate username
    resp = client.post('/api/v1/auth/users/create', json={
        'username': 'dupuser',
        'email': 'unique@example.com',
        'password': 'pass',
        'role': 'viewer'
    }, headers=auth_headers)
    assert resp.status_code == 400

    # Duplicate email
    resp = client.post('/api/v1/auth/users/create', json={
        'username': 'uniqueuser',
        'email': 'dup@example.com',
        'password': 'pass',
        'role': 'viewer'
    }, headers=auth_headers)
    assert resp.status_code == 400


@pytest.mark.parametrize("payload,status_code", [
    ({'username': 'rootuser', 'password': 'rootpass'}, 200),
    ({'username': 'rootuser', 'password': 'wrongpass'}, 401),
    ({'username': 'nonexistent', 'password': 'any'}, 401),
])
def test_login(client, root_user, payload, status_code):
    resp = client.post('/api/v1/auth/login', json=payload)
    if resp.status_code != status_code:
        print("Response JSON:", resp.get_json())
    assert resp.status_code == status_code
    if status_code == 200:
        data = resp.get_json()
        assert 'msg' in data and data['msg'] == 'Login successful'



def test_get_users_requires_auth(client):
    resp = client.get('/api/v1/auth/users')
    assert resp.status_code == 401  # Unauthorized without login


def test_get_users_list(client, db, auth_headers, root_user):
    # Create several users
    viewer_role = Role.query.filter_by(name='viewer').one()
    for i in range(3):
        user = User(username=f'user{i}', email=f'user{i}@example.com')
        user.set_password('pass123')
        user.roles.append(viewer_role)
        db.session.add(user)
    db.session.commit()

    resp = client.get('/api/v1/auth/users?limit=5&offset=0', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total' in data and data['total'] >= 3
    assert 'users' in data and isinstance(data['users'], list)
    assert any(u['username'].startswith('user') for u in data['users'])


def test_update_user_roles_permission(client, db, auth_headers):
    # Create a user with viewer role
    viewer_role = Role.query.filter_by(name='viewer').one()
    user = User(username='toupdate', email='toupdate@example.com')
    user.set_password('pass')
    user.roles.append(viewer_role)
    db.session.add(user)
    db.session.commit()

    # Root user tries to assign admin role
    resp = client.put(f'/api/v1/auth/users/{user.id}', json={
        'roles': ['admin']
    }, headers=auth_headers)
    assert resp.status_code == 200
    updated_user = User.query.get(user.id)
    assert any(role.name == 'admin' for role in updated_user.roles)


def test_delete_user_permission(client, db, auth_headers):
    # Create a viewer user
    viewer_role = Role.query.filter_by(name='viewer').one()
    user = User(username='todelete', email='todelete@example.com')
    user.set_password('pass')
    user.roles.append(viewer_role)
    db.session.add(user)
    db.session.commit()

    # Root deletes the user
    resp = client.delete(f'/api/v1/auth/users/{user.id}', headers=auth_headers)
    assert resp.status_code == 200
    assert b'User deleted successfully' in resp.data


# def test_audit_logs_access_control(client, auth_headers):
#     # Access audit logs with root user (allowed)
#     resp = client.get('/api/v1/auth/audit/logs', headers=auth_headers)
#     assert resp.status_code == 200
#     assert isinstance(resp.get_json(), list)
#
#     # Access audit logs without auth (forbidden)
#     resp = client.get('/api/v1/auth/audit/logs')
#     assert resp.status_code == 401


def test_logout(client, auth_headers):
    resp = client.post('/api/v1/auth/logout', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['msg'] == 'Logout successful'

import pytest
from app import create_app, db as _db
from sqlalchemy.orm import scoped_session, sessionmaker
from app.models.user import Role

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_COOKIE_SECURE': False,
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    _db.create_all()
    for role_name in ['root', 'admin', 'viewer']:
        if not Role.query.filter_by(name=role_name).first():
            _db.session.add(Role(name=role_name))
    _db.session.commit()
    yield _db
    _db.drop_all()

@pytest.fixture(autouse=True)
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)
    db.session = session
    yield session
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def root_user(db):
    from app.models.user import User
    root_role = Role.query.filter_by(name='root').one()
    user = User(username='rootuser', email='root@example.com')
    user.set_password('rootpass')
    user.roles.append(root_role)
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def auth_headers(client, root_user):
    resp = client.post('/api/v1/auth/login', json={
        'username': root_user.username,
        'password': 'rootpass'
    })
    assert resp.status_code == 200
    cookie = resp.headers.get('Set-Cookie')
    return {'Cookie': cookie}

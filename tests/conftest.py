import pytest
import os
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, SavedAccount
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def app():
    os.environ.setdefault('FLASK_ENV', 'testing')
    os.environ.setdefault('SESSION_TYPE', 'filesystem')

    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        JWT_SECRET_KEY=os.getenv('TEST_JWT_SECRET_KEY'),
        SESSION_COOKIE_SECURE=False
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_database():
    yield
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


@pytest.fixture()
def user():
    user = User(
        email='user@example.com',
        auth_hash=generate_password_hash('UserPassword123!'),
        enc_salt=os.urandom(16)
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def user_access_token(client, user):
    response = client.post('/login', json={
        'email': 'user@example.com', 'master_password': 'UserPassword123!'
        })
    
    assert response.status_code == 200
    assert 'access_token' in response.json

    access_token = response.json['access_token']
    return access_token

@pytest.fixture
def saved_account(client, user_access_token):
    response = client.post(
        '/accounts/add',
        headers={'Authorization': f'Bearer {user_access_token}'},
        json={
            'title': 'GitHub',
            'username': 'octocat',
            'email': 'octo@example.com',
            'password': 'Password123!'
        })
    
    assert response.status_code == 201
    data = response.get_json()

    saved_acc = SavedAccount.query.filter_by(id=data['id']).first()
    assert saved_acc is not None

    return saved_acc
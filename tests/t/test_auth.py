from app.models import User

def test_register(client):
    response = client.post(
        '/register',
        json={'email': 'user@example.com', 'master_password': 'UserPassword123!'})
    assert response.status_code == 200

    user = User.query.filter_by(email='user@example.com').first()
    assert user is not None

def test_login(client, user):
    response = client.post(
        '/login',
        json={'email': 'user@example.com', 'master_password': 'UserPassword123!'})
    assert response.status_code == 200

    assert 'access_token' in response.json
    access_token = response.json.get('access_token')
    assert access_token is not None
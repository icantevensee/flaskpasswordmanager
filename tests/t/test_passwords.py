from app.models import SavedAccount

def test_add_account_and_get_password(client, user, user_access_token):
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

    saved_acc = SavedAccount.query.filter_by(user_id=user.id, title='GitHub').first()
    assert saved_acc is not None

    response = client.get(
        f'/accounts/{saved_acc.id}/password',
        headers={'Authorization': f'Bearer {user_access_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['password'] == 'Password123!'

def test_get_accounts(client, user_access_token):
    response = client.get('/accounts', headers={'Authorization': f'Bearer {user_access_token}'})
    assert response.status_code == 200

def test_update_credentials(client, user, user_access_token, saved_account):
    response = client.put(
        f'/accounts/{saved_account.id}/update',
        headers={'Authorization': f'Bearer {user_access_token}'},
        json={
            'title': 'Google',
            'password': 'GooglePassword123!'
        }
    )

    assert response.status_code == 200
    data = response.get_json()

    saved_acc = SavedAccount.query.filter_by(user_id=user.id, title='Google').first()

    assert data['title'] == 'Google'

    assert saved_acc is not None

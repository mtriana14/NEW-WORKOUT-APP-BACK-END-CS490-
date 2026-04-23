from tests.pre_builts import create_user

def test_create_mealplan(client):
    resp = client.post('/api/auth/register', json=create_user(1))
    assert resp.status_code == 201
    resp = client.post('/api/auth/login', json={
        "email": "john@example.com",
        "password": "password"
    })
    assert resp.status_code == 200
    token = resp.json['token']
    resp = client.post('api/mealplan/create', json= {
        "user_id":1,
        "name":"diet",
        "description":"stuff",
        "status":"active"
    },
    headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201

'''
def test_update_mealplan(client):
    resp = client.post('/api/auth/register', json=create_user(1))
    assert resp.status_code == 201
    resp = client.post('/api/auth/login', json={
        "email": "john@example.com",
        "password": "password"
    })
    assert resp.status_code == 200
    token = resp.json['token']
    resp = client.patch('/api/mealplan/update/1'
        json={}
    )
'''
from tests.pre_builts import create_user
from tests.pre_builts import register_and_login

def test_create_user_success(client):
    response = client.post('/api/auth/register', json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "securepassword"
    })
    print(response.json)
    assert response.status_code == 201
    assert response.json['user']['id'] is not None
    assert response.json['user']['email'] is not None
    assert response.json['token'] is not None

def test_create_user_with_missing_fields(client):
    response = client.post('/api/auth/register', json = {
        "first_name":"John",
        "last_name":"Doe"
    }) # missing email, should error
    print(response.json)
    assert response.status_code == 400

def test_create_user_with_duplicate_data(client):
    data = {
        "first_name":"John",
        "last_name":"Doe",
        "email":"john@example.com",
        "password":"password"
    }
    client.post('/api/auth/register', json=data)  
    response = client.post('/api/auth/register', json=data)  
    assert response.status_code == 409

def test_successful_login(client):
    data = {
        "first_name":"John",
        "last_name":"Doe",
        "email":"john@example.com",
        "password":"password"
    }
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 201
    resp = client.post('api/auth/login', json = {
        "email":"john@example.com",
        "password":"password"
    })
    assert resp.status_code == 200
    assert resp.json['token'] is not None

def test_failed_login(client):
    data = {
    "first_name":"John",
    "last_name":"Doe",
    "email":"john@example.com",
    "password":"password"
}
    resp = client.post('/api/auth/register', json=data)
    assert resp.status_code == 201
    resp = client.post('api/auth/login', json = { # Incorrect password
        "email":"john@example.com",
        "password":"ijufhiwebf"
    })
    assert resp.status_code == 401
    resp = client.post('api/auth/login', json = { # Incorrect email
        "email":"osnsjdn",
        "password":"password"
    })
    assert resp.status_code == 401

def test_logout(client):
    token = register_and_login(client, 1)
    resp = client.post('/api/auth/logout', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    
def test_update_user(client):
    resp = client.post('/api/auth/register', json=create_user(1))
    assert resp.status_code == 201
    resp = client.post('/api/auth/login', json={
        "email": "john@example.com",
        "password": "password"
    })
    assert resp.status_code == 200 
    token = resp.json['token']
    resp = client.patch('/api/auth/update', 
        json={"height": 57},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200



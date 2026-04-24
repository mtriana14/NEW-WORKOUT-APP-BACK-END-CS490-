from tests.pre_builts import create_user
from app.seeders.mealplan_seeder import seed_mealplans
from tests.pre_builts import register_and_login

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

def test_invalid_mealplan(client):
    resp = client.post('/api/auth/register', json=create_user(1))
    assert resp.status_code == 201
    resp = client.post('/api/auth/login', json={
        "email": "john@example.com",
        "password": "password"
    })
    assert resp.status_code == 200
    token = resp.json['token']

    resp = client.post('api/mealplan/create', json= {
        "user_id":1, # Missing the name, should return 400
        "description":"stuff",
        "status":"active"
    },
    headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
 
def test_update_mealplan(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.patch('/api/mealplan/update/1',
        json = {"name":"A new name",
                "description":"A new desc"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json['name'] == "A new name"
    assert resp.json['description'] == "A new desc"
    assert resp.json['updated_at'] is not None

def test_invalid_update(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.patch('/api/mealplan/update/1',
        json = {"uahdue":"duyef"},
        headers={"Authorization": f"Bearer {token}"})
    # Note: The endpoint is supposed to return 200 if any valid data is present
    # If no valid data is present, the code returns 400
    assert resp.status_code == 400 
    resp = client.patch('/api/mealplan/update/1',
        json = {"uahdue":"duyef", "name":"A new name"}, # Valid data present
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json['name'] == "A new name"
    assert resp.json['updated_at'] is not None


def test_get_one_mealplan(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.get('/api/mealplan/getone/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json['name'] == "Vegan Diet"

def test_get_no_mealplans(client):
    token = register_and_login(client, 1)
    resp = client.get('/api/mealplan/getone/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

def test_get_all_mealplans(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.get('/api/mealplan/getall', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json["Mealplans"]) == 6 # hardcoded the seeder data to have 6 mealplans

def test_delete_mealplan(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.delete('/api/mealplan/delete/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    resp = client.get('/api/mealplan/getall', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json["Mealplans"]) == 5
    mealplans = resp.json["Mealplans"]
    ids = [mp['meal_plan_id'] for mp in mealplans]
    assert 1 not in ids
    resp = client.get('/api/getone/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
    
    
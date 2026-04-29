from tests.pre_builts import create_user
from app.seeders.mealplan_seeder import seed_mealplans
from tests.pre_builts import create_mealplan_food_item
from tests.pre_builts import register_and_login
from unittest.mock import patch

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
    
def test_add_food_item_success(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.post('/api/mealplan/1/foods',
        json={
            "day_of_week": "Monday",
            "meal_type": "breakfast",
            "food_name": "Oatmeal",
            "calories": 300,
            "protein": 10,
            "carbs": 50,
            "fat": 5,
            "portion_size": "1 cup",
            "notes": "Add honey"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 201
    assert resp.json['item_id'] is not None

def test_add_food_item_no_json(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.post('/api/mealplan/1/foods', json = {}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400

def test_add_food_item_no_mealplan(client):
    token = register_and_login(client, 1)
    resp = client.post('/api/mealplan/1/foods', json={
            "day_of_week": "Monday",
            "meal_type": "breakfast",
            "food_name": "Oatmeal",
            "calories": 300,
            "protein": 10,
            "carbs": 50,
            "fat": 5,
            "portion_size": "1 cup",
            "notes": "Add honey"
        },
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
    seed_mealplans()
    resp = client.post('/api/mealplan/999/foods', json={
            "day_of_week": "Monday",
            "meal_type": "breakfast",
            "food_name": "Oatmeal",
            "calories": 300,
            "protein": 10,
            "carbs": 50,
            "fat": 5,
            "portion_size": "1 cup",
            "notes": "Add honey"
        },
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

def test_add_item_missing_fields(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    resp = client.post('/api/mealplan/1/foods', json = {
        "day_of_week":"Monday"
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400

def test_add_food_item_wrong_user(client):
    resp = client.post('/api/auth/register', json = create_user(1))
    token2 = register_and_login(client, 2)
    seed_mealplans()
    resp = client.post('/api/mealplan/1/food',
        json={
            "day_of_week": "Monday",
            "meal_type": "breakfast",
            "food_name": "Oatmeal"
        },
        headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 404

BASE = 'app.controllers.mealplan_controller.db.session.commit'
def test_meal_plan_food_item_500(client):
    token = register_and_login(client, 1)
    seed_mealplans()
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.post('/api/mealplan/1/foods', json=create_mealplan_food_item(1), headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 500
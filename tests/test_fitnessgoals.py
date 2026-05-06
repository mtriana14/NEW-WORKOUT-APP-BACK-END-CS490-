from tests.pre_builts import register_and_login
from app.seeders.fitnessgoal_seeder import seed_fitnessgoals
from datetime import date
from unittest.mock import patch

BASE = 'app.controllers.fitnessgoal_controller.db.session.commit'

def test_create_fitnessgoal(client):
    token = register_and_login(client, 1)
    resp = client.post('api/fitnessgoal', 
        json = {"goal_type":"Weight loss",
                "target_value":185,
                "target_unit":"lbs",
                "deadline":date(2026,6,7).isoformat(),
                "status":"active"},
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    print(resp.json)
    assert resp.json['goal_type'] == "Weight loss"
    assert resp.json['target_value'] == 185
    assert resp.json['deadline'] == date(2026,6,7).isoformat()
    assert resp.json['status'] == "active"

def test_update_fitness_goal(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    name_to_update = "a new weight loss"
    resp = client.patch('/api/fitnessgoal/1',
        json = {"goal_type":f"{name_to_update}"},
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    resp = client.get('/api/fitnessgoal/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json['goal_type'] == name_to_update

def test_update_with_empty_json(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    resp = client.patch('api/fitnessgoal/1', json = {},headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400

def test_delete_fitnessgoal(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    resp = client.delete('/api/fitnessgoal/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    resp = client.get('api/fitnessgoal/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

def test_get_one_goal(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    resp = client.get('api/fitnessgoal/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json is not None
    assert resp.json['goal_type'] == "Weight Loss"

def test_get_empty__one_fitnessgoals(client):
    token = register_and_login(client, 1)
    resp = client.get('api/fitnessgoal/1', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

def test_get_all_fitnessgoals(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    resp = client.get('api/fitnessgoal', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_get_all_goals_when_none(client):
    token = register_and_login(client, 1)
    resp = client.get('api/fitnessgoal', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

def test_create_fitnessgoals_500(client):
    token = register_and_login(client, 1)
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.post('api/fitnessgoal', 
        json = {"goal_type":"Weight loss",
                "target_value":185,
                "target_unit":"lbs",
                "deadline":date(2026,6,7).isoformat(),
                "status":"active"},
        headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 500

def test_update_fitnessgoal_500(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.patch('/api/fitnessgoal/1',
            json={"goal_type": "Something"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 500

def test_delete_fitnessgoal_500(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.delete('/api/fitnessgoal/1',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 500

def test_get_all_goals_500(client):
    token = register_and_login(client, 1)
    seed_fitnessgoals()
    with patch('app.controllers.fitnessgoal_controller.FitnessGoal.query') as mock_commit:
        mock_commit.filter_by.side_effect = Exception('Database error')
        resp = client.get('/api/fitnessgoal', headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 500
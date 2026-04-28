from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.seeders.exercise_seeder import seed_exercises
from unittest.mock import patch

BASE = 'app.controllers.exercise_controller.db.session.commit'


def get_admin_token(client):
    seed_users()
    resp = client.post('/api/auth/login', json={
        'email': 'admin@fitnessapp.com',
        'password': 'password123'
    })
    assert resp.status_code == 200
    return resp.json['token']


# GET all exercises 

def test_get_all_exercises_empty(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/exercises',
        headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.json['exercises'] == []


def test_get_all_exercises_with_data(client):
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    resp = client.get('/api/admin/exercises',
        headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert len(resp.json['exercises']) > 0


def test_get_all_exercises_no_token(client):
    resp = client.get('/api/admin/exercises')
    assert resp.status_code == 401


# CREATE exercise 

def test_create_exercise_success(client):
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises',
        json={
            'name':         'Bench Press',
            'description':  'A chest pressing movement',
            'muscle_group': 'chest',
            'equipment_type': 'barbell',
            'difficulty':   'intermediate',
            'instructions': 'Lie on bench, lower bar to chest, press up'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    assert 'exercise' in resp.json
    assert 'e_id' in resp.json['exercise']


def test_create_exercise_missing_name(client):
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises',
        json={'muscle_group': 'chest'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 400
    assert 'error' in resp.json


def test_create_exercise_missing_muscle_group(client):
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises',
        json={'name': 'Some Exercise'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 400


def test_create_exercise_duplicate_name(client):
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises',
        json={
            'name':         'Barbell Squat',  # already seeded
            'muscle_group': 'legs'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 409


def test_create_exercise_non_admin(client):
    token = register_and_login(client, 1, role='client')
    resp = client.post('/api/admin/exercises',
        json={'name': 'Test', 'muscle_group': 'chest'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


def test_create_exercise_no_token(client):
    resp = client.post('/api/admin/exercises',
        json={'name': 'Test', 'muscle_group': 'chest'}
    )
    assert resp.status_code == 401


# UPDATE exercise 

def test_update_exercise_success(client):
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    resp = client.put('/api/admin/exercises/1',
        json={'description': 'Updated description'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200


def test_update_exercise_not_found(client):
    token = get_admin_token(client)
    resp = client.put('/api/admin/exercises/99999',
        json={'description': 'Updated'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404


def test_update_exercise_no_token(client):
    resp = client.put('/api/admin/exercises/1',
        json={'description': 'Updated'}
    )
    assert resp.status_code == 401


# DELETE exercise (soft delete)

def test_delete_exercise_success(client):
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    resp = client.delete('/api/admin/exercises/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    # Verify it no longer shows in active list
    resp = client.get('/api/admin/exercises',
        headers={'Authorization': f'Bearer {token}'}
    )
    ids = [e.get('id') or e.get('e_id') for e in resp.json['exercises']]
    assert 1 not in ids


def test_delete_exercise_not_found(client):
    token = get_admin_token(client)
    resp = client.delete('/api/admin/exercises/99999',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404


def test_delete_exercise_no_token(client):
    resp = client.delete('/api/admin/exercises/1')
    assert resp.status_code == 401


# 500 error simulation 

def test_create_exercise_500(client):
    token = get_admin_token(client)
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.post('/api/admin/exercises',
            json={'name': 'Error Exercise', 'muscle_group': 'core'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert resp.status_code == 500

from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.seeders.exercise_seeder import seed_exercises
from app.config.db import db
from app.models.exercise import Exercise
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


# GET /admin/exercises/<exercise_id>

def test_get_exercise_by_id_success(client):
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    resp = client.get('/api/admin/exercises/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    assert 'exercise' in resp.json


def test_get_exercise_by_id_response_shape(client):
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    resp = client.get('/api/admin/exercises/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    ex = resp.json['exercise']
    for key in ('e_id', 'name', 'description', 'muscle_group',
                'equipment_type', 'difficulty', 'is_active', 'created_at'):
        assert key in ex, f"Missing key: {key}"


def test_get_exercise_by_id_correct_data(client):
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    resp = client.get('/api/admin/exercises/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    ex = resp.json['exercise']
    assert ex['e_id'] == 1
    assert ex['name'] == 'Barbell Squat'
    assert ex['muscle_group'] == 'legs'
    assert ex['equipment_type'] == 'barbell'


def test_get_exercise_by_id_not_found(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/exercises/99999',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404
    assert 'error' in resp.json


def test_get_exercise_by_id_no_token(client):
    resp = client.get('/api/admin/exercises/1')
    assert resp.status_code == 401


def test_get_exercise_by_id_soft_deleted(client):
    """A soft-deleted exercise should return 404."""
    seed_users()
    seed_exercises()
    token = get_admin_token(client)
    client.delete('/api/admin/exercises/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    resp = client.get('/api/admin/exercises/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404


# POST /admin/exercises/common

def test_bulk_create_common_no_body(client):
    """No body — should seed the built-in list of common exercises."""
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises/common',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    data = resp.json
    assert data['created_count'] > 0
    assert 'exercises' in data


def test_bulk_create_common_response_shape(client):
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises/common',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    data = resp.json
    for key in ('message', 'created_count', 'skipped_count', 'exercises'):
        assert key in data, f"Missing key: {key}"


def test_bulk_create_common_exercises_persisted(client, app):
    """Verify exercises actually land in the DB."""
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises/common',
        headers={'Authorization': f'Bearer {token}'}
    )
    created_count = resp.json['created_count']
    with app.app_context():
        assert Exercise.query.count() == created_count


def test_bulk_create_common_with_custom_body(client):
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises/common',
        json={
            'exercises': [
                {
                    'name': 'Custom Exercise A',
                    'muscle_group': 'core',
                    'equipment_type': 'bodyweight',
                    'difficulty': 'beginner',
                    'description': 'A custom test exercise',
                    'instructions': 'Do the thing'
                },
                {
                    'name': 'Custom Exercise B',
                    'muscle_group': 'arms',
                    'equipment_type': 'dumbbell',
                    'difficulty': 'intermediate',
                }
            ]
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    assert resp.json['created_count'] == 2
    assert resp.json['skipped_count'] == 0


def test_bulk_create_common_skips_duplicates(client):
    """If an exercise name already exists it should be skipped, not error."""
    seed_users()
    seed_exercises()  # seeds 'Barbell Squat' among others
    token = get_admin_token(client)
    resp = client.post('/api/admin/exercises/common',
        json={
            'exercises': [
                {'name': 'Barbell Squat', 'muscle_group': 'legs'},  # duplicate
                {'name': 'Brand New Move', 'muscle_group': 'core'},
            ]
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    assert resp.json['created_count'] == 1
    assert resp.json['skipped_count'] == 1


def test_bulk_create_common_all_duplicates(client):
    """All exercises already exist — created_count should be 0."""
    token = get_admin_token(client)
    # First call creates them
    client.post('/api/admin/exercises/common',
        headers={'Authorization': f'Bearer {token}'}
    )
    # Second call should skip all
    resp = client.post('/api/admin/exercises/common',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    assert resp.json['created_count'] == 0
    assert resp.json['skipped_count'] > 0


def test_bulk_create_common_non_admin(client):
    seed_users()
    token = register_and_login(client, 2, role='client')
    resp = client.post('/api/admin/exercises/common',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


def test_bulk_create_common_no_token(client):
    resp = client.post('/api/admin/exercises/common')
    assert resp.status_code == 401


def test_bulk_create_common_500(client):
    token = get_admin_token(client)
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.post('/api/admin/exercises/common',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert resp.status_code == 500

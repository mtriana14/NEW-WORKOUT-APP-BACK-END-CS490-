from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.seeders.coach_seeder import seed_coaches
from unittest.mock import patch

BASE = 'app.controllers.coach_management_controller.db.session.commit'


def get_admin_token(client):
    seed_users()
    resp = client.post('/api/auth/login', json={
        'email': 'admin@fitnessapp.com',
        'password': 'password123'
    })
    assert resp.status_code == 200
    return resp.json['token']


def setup(client):
    """Seed users + coaches, return admin token. John's coach_id == 1."""
    seed_users()
    seed_coaches()
    return get_admin_token(client)


# GET /admin/coaches/<coach_id>

def test_get_coach_detail_success(client):
    admin_token = setup(client)
    resp = client.get('/api/admin/coaches/1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200
    assert 'coach' in resp.json


def test_get_coach_detail_response_shape(client):
    admin_token = setup(client)
    resp = client.get('/api/admin/coaches/1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200
    coach = resp.json['coach']
    for key in ('coach_id', 'user_id', 'name', 'email',
                'specialization', 'certifications', 'experience_years',
                'bio', 'hourly_rate', 'cost', 'status', 'created_at'):
        assert key in coach, f"Missing key: {key}"


def test_get_coach_detail_correct_data(client):
    admin_token = setup(client)
    resp = client.get('/api/admin/coaches/1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    coach = resp.json['coach']
    assert coach['coach_id'] == 1
    assert coach['name'] == 'John Smith'
    assert coach['email'] == 'john.coach@fitnessapp.com'
    assert coach['specialization'] == 'fitness'
    assert coach['status'] == 'approved'


def test_get_coach_detail_not_found(client):
    admin_token = setup(client)
    resp = client.get('/api/admin/coaches/99999',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 404
    assert 'error' in resp.json


def test_get_coach_detail_no_token(client):
    resp = client.get('/api/admin/coaches/1')
    assert resp.status_code == 401


def test_get_coach_detail_non_admin(client):
    seed_users()
    seed_coaches()
    token = register_and_login(client, 2, role='client')
    resp = client.get('/api/admin/coaches/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


def test_get_coach_detail_second_coach(client):
    """Sarah is coach_id 2 with pending status."""
    admin_token = setup(client)
    resp = client.get('/api/admin/coaches/2',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200
    coach = resp.json['coach']
    assert coach['coach_id'] == 2
    assert coach['name'] == 'Sarah Johnson'
    assert coach['status'] == 'pending'


def test_get_coach_detail_numeric_fields(client):
    """hourly_rate and cost should be floats, not strings."""
    admin_token = setup(client)
    resp = client.get('/api/admin/coaches/1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    coach = resp.json['coach']
    assert isinstance(coach['hourly_rate'], float)
    assert isinstance(coach['cost'], float)
    assert coach['hourly_rate'] == 50.0
    assert coach['cost'] == 50.0

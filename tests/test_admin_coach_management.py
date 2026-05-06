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

def setup_coach(client):
    """Seed users and coaches, return admin token and John's coach_id."""
    seed_users()
    seed_coaches()
    admin_token = get_admin_token(client)
    return admin_token

# Suspend coach

def test_suspend_coach_success(client):
    admin_token = setup_coach(client)
    resp = client.put('/api/admin/coaches/1/suspend',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200
    assert 'suspended' in resp.json['message'].lower()


def test_suspend_already_suspended_coach(client):
    admin_token = setup_coach(client)
    client.put('/api/admin/coaches/1/suspend',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    # Suspend again
    resp = client.put('/api/admin/coaches/1/suspend',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 400
    assert 'already' in resp.json['error'].lower()


def test_suspend_nonexistent_coach(client):
    admin_token = setup_coach(client)
    resp = client.put('/api/admin/coaches/99999/suspend',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 404


def test_suspend_coach_no_token(client):
    resp = client.put('/api/admin/coaches/1/suspend')
    assert resp.status_code == 401


def test_suspend_coach_non_admin(client):
    seed_users()
    seed_coaches()
    token = register_and_login(client, 2, role='client')
    resp = client.put('/api/admin/coaches/1/suspend',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


# Reactivate coach 

def test_reactivate_coach_success(client):
    admin_token = setup_coach(client)
    # First suspend
    client.put('/api/admin/coaches/1/suspend',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    # Then reactivate
    resp = client.put('/api/admin/coaches/1/reactivate',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200
    assert 'reactivated' in resp.json['message'].lower()


def test_reactivate_non_suspended_coach(client):
    admin_token = setup_coach(client)
    # John is 'approved' not 'suspended'
    resp = client.put('/api/admin/coaches/1/reactivate',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 400


def test_reactivate_nonexistent_coach(client):
    admin_token = setup_coach(client)
    resp = client.put('/api/admin/coaches/99999/reactivate',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 404


def test_reactivate_coach_no_token(client):
    resp = client.put('/api/admin/coaches/1/reactivate')
    assert resp.status_code == 401


# Disable coach 

def test_disable_coach_success(client):
    admin_token = setup_coach(client)
    resp = client.put('/api/admin/coaches/1/disable',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200
    assert 'disabled' in resp.json['message'].lower()


def test_disable_already_disabled_coach(client):
    admin_token = setup_coach(client)
    client.put('/api/admin/coaches/1/disable',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    resp = client.put('/api/admin/coaches/1/disable',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 400


def test_disable_nonexistent_coach(client):
    admin_token = setup_coach(client)
    resp = client.put('/api/admin/coaches/99999/disable',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 404


def test_disable_coach_no_token(client):
    resp = client.put('/api/admin/coaches/1/disable')
    assert resp.status_code == 401


# Status alias endpoint 

def test_status_endpoint_suspend(client):
    admin_token = setup_coach(client)
    resp = client.put('/api/admin/coaches/1/status',
        json={'status': 'suspend'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200


def test_status_endpoint_invalid_value(client):
    admin_token = setup_coach(client)
    resp = client.put('/api/admin/coaches/1/status',
        json={'status': 'invalidaction'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 400


def test_status_endpoint_no_token(client):
    resp = client.put('/api/admin/coaches/1/status',
        json={'status': 'suspend'}
    )
    assert resp.status_code == 401


# 500 error simulation 

def test_suspend_coach_500(client):
    admin_token = setup_coach(client)
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.put('/api/admin/coaches/1/suspend',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert resp.status_code == 500

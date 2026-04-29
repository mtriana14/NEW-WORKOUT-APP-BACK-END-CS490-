from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.seeders.coach_seeder import seed_coaches
from unittest.mock import patch

BASE = 'app.controllers.coach_registration_controller2.db.session.commit'


def get_admin_token(client):
    seed_users()
    resp = client.post('/api/auth/login', json={
        'email': 'admin@fitnessapp.com',
        'password': 'password123'
    })
    assert resp.status_code == 200
    return resp.json['token']


def apply_as_coach(client, user_token):
    """Helper — submit a coach application for the logged-in user."""
    return client.post('/api/coach/apply',
        json={
            'qualifications': 'NASM CPT',
            'specialty':      'fitness',
            'document_links': 'https://example.com/resume.pdf'
        },
        headers={'Authorization': f'Bearer {user_token}'}
    )


# GET pending registrations 

def test_get_pending_registrations_empty(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/coaches/pending',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert 'registrations' in data or 'Registrations' in data


def test_get_pending_registrations_with_data(client):
    seed_users()
    # Register a new client and have them apply
    client_token = register_and_login(client, 2, role='client')
    apply_resp = apply_as_coach(client, client_token)
    assert apply_resp.status_code == 201

    admin_token = get_admin_token(client)
    resp = client.get('/api/admin/coaches/pending',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    registrations = data.get('Registrations') or data.get('registrations', [])
    assert len(registrations) >= 1


def test_get_pending_registrations_no_token(client):
    resp = client.get('/api/admin/coaches/pending')
    assert resp.status_code == 401


def test_get_pending_registrations_non_admin(client):
    token = register_and_login(client, 1, role='client')
    resp = client.get('/api/admin/coaches/pending',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


# GET all registrations 

def test_get_all_registrations_empty(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/coaches/registrations',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200


def test_get_all_registrations_with_data(client):
    seed_users()
    client_token = register_and_login(client, 2, role='client')
    apply_as_coach(client, client_token)
    admin_token = get_admin_token(client)
    resp = client.get('/api/admin/coaches/registrations',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200


# PROCESS registration — approve 

def test_approve_coach_registration_success(client):
    seed_users()
    client_token = register_and_login(client, 2, role='client')
    apply_resp = apply_as_coach(client, client_token)
    assert apply_resp.status_code == 201
    reg_id = apply_resp.json.get('reg_id') or 1

    admin_token = get_admin_token(client)
    resp = client.put(f'/api/admin/coaches/{reg_id}/process',
        json={'action': 'approved', 'cost': 50.00},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 200


def test_approve_coach_registration_invalid_action(client):
    seed_users()
    client_token = register_and_login(client, 2, role='client')
    apply_as_coach(client, client_token)
    admin_token = get_admin_token(client)
    resp = client.put('/api/admin/coaches/1/process',
        json={'action': 'banana'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert resp.status_code == 400


def test_process_nonexistent_registration(client):
    token = get_admin_token(client)
    resp = client.put('/api/admin/coaches/99999/process',
        json={'action': 'approved'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404


def test_process_registration_no_token(client):
    resp = client.put('/api/admin/coaches/1/process',
        json={'action': 'approved'}
    )
    assert resp.status_code == 401


def test_process_registration_non_admin(client):
    token = register_and_login(client, 1, role='client')
    resp = client.put('/api/admin/coaches/1/process',
        json={'action': 'approved'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


# 500 error simulation 

def test_get_pending_registrations_500(client):
    token = get_admin_token(client)
    with patch('app.controllers.coach_registration_controller2.db.session.query') as mock_q:
        mock_q.side_effect = Exception('Database error')
        resp = client.get('/api/admin/coaches/pending',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert resp.status_code == 500

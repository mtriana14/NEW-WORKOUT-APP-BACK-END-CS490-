"""
Tests for client self-service meal plans and workout plans.
These tests require the updated create_mealplan and create_workout_plan
controllers that allow clients to create their own plans.
"""
from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.seeders.coach_seeder import seed_coaches


# CLIENT MEAL PLANS
# --------------------------------------------------------------

def test_client_create_mealplan_success(client):
    """Client should be able to create their own meal plan."""
    token = register_and_login(client, 1, role='client')
    resp = client.post('/api/mealplan/create',
        json={
            'name': 'My Personal Diet Plan',
            'description': 'Low carb, high protein'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    data = resp.json
    assert 'meal_plan_id' in data or 'Success' in data


def test_client_create_mealplan_missing_name(client):
    """Client creating meal plan without name should get 400."""
    token = register_and_login(client, 1, role='client')
    resp = client.post('/api/mealplan/create',
        json={'description': 'No name provided'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 400


def test_client_create_mealplan_no_token(client):
    resp = client.post('/api/mealplan/create',
        json={'name': 'My Plan'}
    )
    assert resp.status_code == 401


def test_client_get_own_mealplans(client):
    """Client should only see their own meal plans."""
    token = register_and_login(client, 1, role='client')
    # Create two plans
    client.post('/api/mealplan/create',
        json={'name': 'Plan A'},
        headers={'Authorization': f'Bearer {token}'}
    )
    client.post('/api/mealplan/create',
        json={'name': 'Plan B'},
        headers={'Authorization': f'Bearer {token}'}
    )
    resp = client.get('/api/mealplan/getall',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert 'Mealplans' in data
    assert len(data['Mealplans']) == 2


def test_client_cannot_see_other_client_plans(client):
    """Client A should not see Client B's meal plans."""
    token_a = register_and_login(client, 1, role='client')
    token_b = register_and_login(client, 2, role='client')

    # Client A creates a plan
    client.post('/api/mealplan/create',
        json={'name': "Client A's Plan"},
        headers={'Authorization': f'Bearer {token_a}'}
    )

    # Client B should see 0 plans
    resp = client.get('/api/mealplan/getall',
        headers={'Authorization': f'Bearer {token_b}'}
    )
    assert resp.status_code == 200
    assert len(resp.json['Mealplans']) == 0


def test_client_update_own_mealplan(client):
    """Client should be able to update their own meal plan."""
    token = register_and_login(client, 1, role='client')
    create_resp = client.post('/api/mealplan/create',
        json={'name': 'Original Name'},
        headers={'Authorization': f'Bearer {token}'}
    )
    plan_id = create_resp.json.get('meal_plan_id') or 1

    resp = client.patch(f'/api/mealplan/update/{plan_id}',
        json={'name': 'Updated Name'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200


def test_client_cannot_update_other_client_plan(client):
    """Client A should not be able to update Client B's plan."""
    token_a = register_and_login(client, 1, role='client')
    token_b = register_and_login(client, 2, role='client')

    create_resp = client.post('/api/mealplan/create',
        json={'name': "Client A's Plan"},
        headers={'Authorization': f'Bearer {token_a}'}
    )
    plan_id = create_resp.json.get('meal_plan_id') or 1

    resp = client.patch(f'/api/mealplan/update/{plan_id}',
        json={'name': 'Stolen Plan'},
        headers={'Authorization': f'Bearer {token_b}'}
    )
    assert resp.status_code == 403


def test_client_delete_own_mealplan(client):
    """Client should be able to delete their own meal plan."""
    token = register_and_login(client, 1, role='client')
    create_resp = client.post('/api/mealplan/create',
        json={'name': 'Plan to Delete'},
        headers={'Authorization': f'Bearer {token}'}
    )
    plan_id = create_resp.json.get('meal_plan_id') or 1

    resp = client.delete(f'/api/mealplan/delete/{plan_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200


def test_client_cannot_delete_other_client_plan(client):
    """Client A should not be able to delete Client B's plan."""
    token_a = register_and_login(client, 1, role='client')
    token_b = register_and_login(client, 2, role='client')

    create_resp = client.post('/api/mealplan/create',
        json={'name': "Client A's Plan"},
        headers={'Authorization': f'Bearer {token_a}'}
    )
    plan_id = create_resp.json.get('meal_plan_id') or 1

    resp = client.delete(f'/api/mealplan/delete/{plan_id}',
        headers={'Authorization': f'Bearer {token_b}'}
    )
    assert resp.status_code == 403


def test_coach_create_mealplan_for_client(client):
    """Coach should still be able to create a meal plan for a client."""
    seed_users()
    seed_coaches()
    # Login as John (coach, user_id=2)
    coach_resp = client.post('/api/auth/login', json={
        'email': 'john.coach@fitnessapp.com',
        'password': 'password123'
    })
    coach_token = coach_resp.json['token']

    # Register a client
    client_token = register_and_login(client, 1, role='client')
    client_login = client.post('/api/auth/login', json={
        'email': 'john@example.com',
        'password': 'password'
    })
    client_user_id = client_login.json['user']['id']

    resp = client.post('/api/mealplan/create',
        json={
            'name': 'Coach Created Plan',
            'description': 'High protein',
            'client_id': client_user_id
        },
        headers={'Authorization': f'Bearer {coach_token}'}
    )
    assert resp.status_code == 201


def test_coach_create_mealplan_missing_client_id(client):
    """Coach creating meal plan without client_id should get 400."""
    seed_users()
    seed_coaches()
    coach_resp = client.post('/api/auth/login', json={
        'email': 'john.coach@fitnessapp.com',
        'password': 'password123'
    })
    coach_token = coach_resp.json['token']

    resp = client.post('/api/mealplan/create',
        json={'name': 'No client specified'},
        headers={'Authorization': f'Bearer {coach_token}'}
    )
    assert resp.status_code == 400
    assert 'client_id' in resp.json.get('Error', '').lower()


# CLIENT WORKOUT PLANS
# ----------------------------------------------------------------------------------------------

def test_client_create_workout_plan_success(client):
    """Client should be able to create their own workout plan."""
    token = register_and_login(client, 1, role='client')
    resp = client.post('/api/coach/0/workout-plans',
        json={
            'name': 'My Push Day',
            'description': 'Chest, shoulders, triceps'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    assert 'plan_id' in resp.json


def test_client_create_workout_plan_missing_name(client):
    token = register_and_login(client, 1, role='client')
    resp = client.post('/api/coach/0/workout-plans',
        json={'description': 'No name'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 400


def test_client_create_workout_plan_no_token(client):
    resp = client.post('/api/coach/0/workout-plans',
        json={'name': 'My Plan'}
    )
    assert resp.status_code == 401


def test_client_get_own_workout_plans(client):
    """Client should be able to retrieve their own workout plans."""
    token = register_and_login(client, 1, role='client')
    # Create two plans
    client.post('/api/coach/0/workout-plans',
        json={'name': 'Push Day'},
        headers={'Authorization': f'Bearer {token}'}
    )
    client.post('/api/coach/0/workout-plans',
        json={'name': 'Pull Day'},
        headers={'Authorization': f'Bearer {token}'}
    )
    resp = client.get('/api/my/workout-plans',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert 'workout_plans' in data
    assert len(data['workout_plans']) == 2


def test_client_cannot_see_other_client_workout_plans(client):
    """Client A should not see Client B's workout plans."""
    token_a = register_and_login(client, 1, role='client')
    token_b = register_and_login(client, 2, role='client')

    client.post('/api/coach/0/workout-plans',
        json={'name': "Client A's Plan"},
        headers={'Authorization': f'Bearer {token_a}'}
    )

    resp = client.get('/api/my/workout-plans',
        headers={'Authorization': f'Bearer {token_b}'}
    )
    assert resp.status_code == 200
    assert len(resp.json['workout_plans']) == 0


def test_coach_create_workout_plan_for_client(client):
    """Coach should still be able to create a workout plan for a client."""
    seed_users()
    seed_coaches()
    coach_resp = client.post('/api/auth/login', json={
        'email': 'john.coach@fitnessapp.com',
        'password': 'password123'
    })
    coach_token = coach_resp.json['token']

    client_token = register_and_login(client, 1, role='client')
    client_login = client.post('/api/auth/login', json={
        'email': 'john@example.com',
        'password': 'password'
    })
    client_user_id = client_login.json['user']['id']

    resp = client.post('/api/coach/2/workout-plans',
        json={
            'name': 'Coach Assigned Plan',
            'description': 'Full body',
            'client_id': client_user_id
        },
        headers={'Authorization': f'Bearer {coach_token}'}
    )
    assert resp.status_code == 201


def test_coach_create_workout_plan_missing_client_id(client):
    """Coach creating workout plan without client_id should get 400."""
    seed_users()
    seed_coaches()
    coach_resp = client.post('/api/auth/login', json={
        'email': 'john.coach@fitnessapp.com',
        'password': 'password123'
    })
    coach_token = coach_resp.json['token']

    resp = client.post('/api/coach/2/workout-plans',
        json={'name': 'No client specified'},
        headers={'Authorization': f'Bearer {coach_token}'}
    )
    assert resp.status_code == 400
    assert 'client_id' in resp.json.get('error', '').lower()

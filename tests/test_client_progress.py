from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.config.db import db
from app.models.progress_entry import ProgressEntry
from unittest.mock import patch
from datetime import date, timedelta

BASE = 'app.controllers.progress_controller.db.session.commit'

# After seed_users(): admin=1, john_coach=2, sarah_coach=3, mike_client=4, emily_client=5
CLIENT_ID = 4
CLIENT_EMAIL = 'mike.client@fitnessapp.com'
CLIENT_PASSWORD = 'password123'


def get_client_token(client):
    seed_users()
    resp = client.post('/api/auth/login', json={
        'email': CLIENT_EMAIL,
        'password': CLIENT_PASSWORD
    })
    assert resp.status_code == 200
    return resp.json['token']


def seed_progress(entries):
    """Insert ProgressEntry rows. Call AFTER seed_users() so FK exists."""
    for e in entries:
        db.session.add(ProgressEntry(
            user_id=e.get('user_id', CLIENT_ID),
            entry_date=e['entry_date'],
            weight=e.get('weight'),
            workouts_completed=e.get('workouts_completed', 0),
            calories_burned=e.get('calories_burned', 0),
            goal_completed=e.get('goal_completed', False),
            notes=e.get('notes'),
        ))
    db.session.commit()


# GET /client/<user_id>/progress

def test_get_progress_empty(client):
    token = get_client_token(client)
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert data['entries'] == []
    assert data['summary']['entries_count'] == 0


def test_get_progress_response_shape(client):
    token = get_client_token(client)
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    assert 'entries' in resp.json
    assert 'summary' in resp.json


def test_get_progress_summary_keys(client):
    token = get_client_token(client)
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    summary = resp.json['summary']
    for key in ('total_workouts', 'current_streak', 'weekly_calories',
                'goals_met_percentage', 'latest_weight', 'weight_change',
                'entries_count'):
        assert key in summary, f"Missing summary key: {key}"


def test_get_progress_with_entries(client):
    token = get_client_token(client)  # seeds users first
    seed_progress([
        {'entry_date': date.today() - timedelta(days=2), 'workouts_completed': 3, 'calories_burned': 400},
        {'entry_date': date.today() - timedelta(days=1), 'workouts_completed': 2, 'calories_burned': 300},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    assert len(resp.json['entries']) == 2
    assert resp.json['summary']['entries_count'] == 2


def test_get_progress_ordered_by_date_desc(client):
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today() - timedelta(days=5), 'workouts_completed': 1},
        {'entry_date': date.today() - timedelta(days=1), 'workouts_completed': 2},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    dates = [e['entry_date'] for e in resp.json['entries']]
    assert dates == sorted(dates, reverse=True)


def test_get_progress_total_workouts(client):
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today() - timedelta(days=2), 'workouts_completed': 3},
        {'entry_date': date.today() - timedelta(days=1), 'workouts_completed': 5},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.json['summary']['total_workouts'] == 8


def test_get_progress_weekly_calories(client):
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today() - timedelta(days=3), 'calories_burned': 500},
        {'entry_date': date.today() - timedelta(days=1), 'calories_burned': 300},
        {'entry_date': date.today() - timedelta(days=30), 'calories_burned': 9999},  # outside window
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.json['summary']['weekly_calories'] == 800


def test_get_progress_goals_met_percentage(client):
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today() - timedelta(days=3), 'goal_completed': True},
        {'entry_date': date.today() - timedelta(days=2), 'goal_completed': True},
        {'entry_date': date.today() - timedelta(days=1), 'goal_completed': False},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    pct = resp.json['summary']['goals_met_percentage']
    assert abs(pct - 66.7) < 0.5


def test_get_progress_latest_weight(client):
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today() - timedelta(days=5), 'weight': 80.0},
        {'entry_date': date.today() - timedelta(days=1), 'weight': 78.5},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.json['summary']['latest_weight'] == 78.5


def test_get_progress_weight_change(client):
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today() - timedelta(days=10), 'weight': 85.0},
        {'entry_date': date.today() - timedelta(days=1),  'weight': 80.0},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    # latest - earliest = 80 - 85 = -5 (lost weight)
    assert resp.json['summary']['weight_change'] == -5.0


def test_get_progress_streak_with_todays_entry(client):
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today(), 'goal_completed': True},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.json['summary']['current_streak'] >= 1


def test_get_progress_streak_breaks_on_false(client):
    """Streak should be 0 if today's goal is not completed."""
    token = get_client_token(client)
    seed_progress([
        {'entry_date': date.today() - timedelta(days=1), 'goal_completed': True},
        {'entry_date': date.today(),                     'goal_completed': False},
    ])
    resp = client.get(f'/api/client/{CLIENT_ID}/progress',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.json['summary']['current_streak'] == 0


def test_get_progress_no_token(client):
    resp = client.get(f'/api/client/{CLIENT_ID}/progress')
    assert resp.status_code == 401


# POST /client/<user_id>/progress

def test_save_progress_success(client):
    token = get_client_token(client)
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={
            'entry_date': str(date.today()),
            'workouts_completed': 2,
            'calories_burned': 450,
            'goal_completed': True,
            'notes': 'Good session'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    data = resp.json
    assert data['message'] == 'Progress saved'
    assert 'entry' in data
    assert 'summary' in data


def test_save_progress_entry_shape(client):
    token = get_client_token(client)
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={'entry_date': str(date.today())},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    entry = resp.json['entry']
    for key in ('entry_id', 'user_id', 'entry_date', 'weight',
                'workouts_completed', 'calories_burned', 'goal_completed',
                'notes', 'created_at'):
        assert key in entry, f"Missing entry key: {key}"


def test_save_progress_summary_shape(client):
    token = get_client_token(client)
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={'entry_date': str(date.today()), 'workouts_completed': 1},
        headers={'Authorization': f'Bearer {token}'}
    )
    summary = resp.json['summary']
    for key in ('total_workouts', 'current_streak', 'weekly_calories',
                'goals_met_percentage', 'latest_weight', 'weight_change',
                'entries_count'):
        assert key in summary, f"Missing summary key: {key}"


def test_save_progress_persists_to_db(client):
    token = get_client_token(client)
    client.post(f'/api/client/{CLIENT_ID}/progress',
        json={
            'entry_date': str(date.today()),
            'workouts_completed': 3,
            'calories_burned': 600,
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    entry = ProgressEntry.query.filter_by(user_id=CLIENT_ID).first()
    assert entry is not None
    assert entry.workouts_completed == 3
    assert entry.calories_burned == 600


def test_save_progress_missing_entry_date(client):
    token = get_client_token(client)
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={'workouts_completed': 2},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 400
    assert 'error' in resp.json


def test_save_progress_no_token(client):
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={'entry_date': str(date.today())}
    )
    assert resp.status_code == 401


def test_save_progress_updates_summary(client):
    token = get_client_token(client)
    client.post(f'/api/client/{CLIENT_ID}/progress',
        json={'entry_date': str(date.today() - timedelta(days=1)), 'workouts_completed': 2},
        headers={'Authorization': f'Bearer {token}'}
    )
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={'entry_date': str(date.today()), 'workouts_completed': 3},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.json['summary']['entries_count'] == 2
    assert resp.json['summary']['total_workouts'] == 5


def test_save_progress_with_weight(client):
    token = get_client_token(client)
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={
            'entry_date': str(date.today()),
            'weight': 77.5,
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 201
    assert resp.json['entry']['weight'] == 77.5
    assert resp.json['summary']['latest_weight'] == 77.5


def test_save_progress_defaults(client):
    """workouts_completed, calories_burned, goal_completed should default to 0/0/False."""
    token = get_client_token(client)
    resp = client.post(f'/api/client/{CLIENT_ID}/progress',
        json={'entry_date': str(date.today())},
        headers={'Authorization': f'Bearer {token}'}
    )
    entry = resp.json['entry']
    assert entry['workouts_completed'] == 0
    assert entry['calories_burned'] == 0
    assert entry['goal_completed'] is False


def test_save_progress_500(client):
    token = get_client_token(client)
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.post(f'/api/client/{CLIENT_ID}/progress',
            json={'entry_date': str(date.today())},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert resp.status_code == 500

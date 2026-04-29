from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.seeders.coach_seeder import seed_coaches
from app.config.db import db
from app.models.payment import Payment
from app.models.subscription import Subscription
from unittest.mock import patch
from datetime import date

BASE = 'app.controllers.payment_dashboard_controller.db.session'


def get_admin_token(client):
    seed_users()
    resp = client.post('/api/auth/login', json={
        'email': 'admin@fitnessapp.com',
        'password': 'password123'
    })
    assert resp.status_code == 200
    return resp.json['token']


def seed_payments(app):
    """Seed test payment records directly into DB."""
    with app.app_context():
        sub = Subscription(
            user_id=4,
            coach_id=1,
            plan_type='monthly',
            amount=50.00,
            status='active',
            start_date=date.today()
        )
        db.session.add(sub)
        db.session.flush()

        payments = [
            Payment(
                client_id=4,
                coach_id=1,
                subscription_id=sub.subscription_id,
                amount=50.00,
                currency='USD',
                payment_method_type='credit_card',
                status='completed',
                transaction_id='TXN001'
            ),
            Payment(
                client_id=4,
                coach_id=1,
                subscription_id=sub.subscription_id,
                amount=50.00,
                currency='USD',
                payment_method_type='credit_card',
                status='pending',
                transaction_id='TXN002'
            ),
            Payment(
                client_id=4,
                coach_id=1,
                subscription_id=sub.subscription_id,
                amount=50.00,
                currency='USD',
                payment_method_type='debit_card',
                status='failed',
                transaction_id='TXN003'
            ),
        ]
        db.session.add_all(payments)
        db.session.commit()


# GET payment summary 

def test_get_payment_summary_empty(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/summary',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert 'total_revenue' in data
    assert 'total_transactions' in data
    assert 'status_breakdown' in data
    assert data['total_revenue'] == 0.0
    assert data['total_transactions'] == 0


def test_get_payment_summary_with_data(client, app):
    seed_users()
    seed_coaches()
    seed_payments(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/summary',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert data['total_revenue'] == 50.0      # only completed
    assert data['total_transactions'] == 3    # all statuses
    assert len(data['status_breakdown']) == 3


def test_get_payment_stats_alias(client):
    """stats endpoint should return same data as summary."""
    token = get_admin_token(client)
    summary = client.get('/api/admin/payments/summary',
        headers={'Authorization': f'Bearer {token}'}
    ).json
    stats = client.get('/api/admin/payments/stats',
        headers={'Authorization': f'Bearer {token}'}
    ).json
    assert summary['total_revenue'] == stats['total_revenue']
    assert summary['total_transactions'] == stats['total_transactions']


def test_get_payment_summary_no_token(client):
    resp = client.get('/api/admin/payments/summary')
    assert resp.status_code == 401


def test_get_payment_summary_non_admin(client):
    seed_users()
    token = register_and_login(client, 2, role='client')
    resp = client.get('/api/admin/payments/summary',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


#  GET all payments (paginated) 

def test_get_all_payments_empty(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert 'payments' in data
    assert 'total' in data
    assert 'pages' in data
    assert 'current_page' in data
    assert data['payments'] == []


def test_get_all_payments_with_data(client, app):
    seed_users()
    seed_coaches()
    seed_payments(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert data['total'] == 3
    assert len(data['payments']) == 3


def test_get_all_payments_pagination(client, app):
    seed_users()
    seed_coaches()
    seed_payments(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments?page=1&per_page=2',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert len(data['payments']) == 2
    assert data['pages'] == 2
    assert data['current_page'] == 1


def test_get_all_payments_response_shape(client, app):
    seed_users()
    seed_coaches()
    seed_payments(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    payment = resp.json['payments'][0]
    assert 'payment_id' in payment
    assert 'client_name' in payment
    assert 'coach_name' in payment
    assert 'amount' in payment
    assert 'status' in payment


def test_get_all_payments_no_token(client):
    resp = client.get('/api/admin/payments')
    assert resp.status_code == 401


def test_get_all_payments_non_admin(client):
    seed_users()
    token = register_and_login(client, 2, role='client')
    resp = client.get('/api/admin/payments',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


# GET coach payment summary

def test_get_coach_payment_summary_success(client, app):
    seed_users()
    seed_coaches()
    seed_payments(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/coach/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert 'coach_id' in data
    assert 'total_earned' in data
    assert 'total_transactions' in data
    assert data['total_earned'] == 50.0
    assert data['total_transactions'] == 3


def test_get_coach_payment_summary_not_found(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/coach/99999',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404


def test_get_coach_payment_summary_no_token(client):
    resp = client.get('/api/admin/payments/coach/1')
    assert resp.status_code == 401

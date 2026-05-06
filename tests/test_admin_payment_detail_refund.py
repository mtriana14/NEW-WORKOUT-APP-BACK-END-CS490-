from tests.pre_builts import register_and_login
from app.seeders.user_seeder import seed_users
from app.seeders.coach_seeder import seed_coaches
from app.config.db import db
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.notification import Notification
from unittest.mock import patch
from datetime import date

BASE = 'app.controllers.payment_dashboard_controller.db.session.commit'


def get_admin_token(client):
    seed_users()
    resp = client.post('/api/auth/login', json={
        'email': 'admin@fitnessapp.com',
        'password': 'password123'
    })
    assert resp.status_code == 200
    return resp.json['token']


def seed_payment(app, status='completed', transaction_id='TXN001'):
    """Insert a single payment record; returns payment_id (always 1 on fresh DB)."""
    with app.app_context():
        sub = Subscription(
            user_id=4,
            coach_id=1,
            plan_type='monthly',
            amount=75.00,
            status='active',
            start_date=date.today()
        )
        db.session.add(sub)
        db.session.flush()

        payment = Payment(
            client_id=4,
            coach_id=1,
            subscription_id=sub.subscription_id,
            amount=75.00,
            currency='USD',
            payment_method_type='credit_card',
            status=status,
            transaction_id=transaction_id,
            description='Monthly coaching subscription'
        )
        db.session.add(payment)
        db.session.commit()


# GET /admin/payments/<payment_id>

def test_get_payment_detail_success(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    assert 'payment' in resp.json


def test_get_payment_detail_response_shape(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    p = resp.json['payment']
    for key in ('payment_id', 'client_name', 'coach_name', 'amount',
                'currency', 'status', 'payment_method_type',
                'transaction_id', 'description', 'created_at'):
        assert key in p, f"Missing key: {key}"


def test_get_payment_detail_correct_data(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app)
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    p = resp.json['payment']
    assert p['payment_id'] == 1
    assert p['amount'] == 75.0
    assert p['currency'] == 'USD'
    assert p['status'] == 'completed'
    assert p['client_name'] == 'Mike Davis'
    assert p['coach_name'] == 'John Smith'


def test_get_payment_detail_not_found(client):
    token = get_admin_token(client)
    resp = client.get('/api/admin/payments/99999',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404
    assert 'error' in resp.json


def test_get_payment_detail_no_token(client):
    resp = client.get('/api/admin/payments/1')
    assert resp.status_code == 401


def test_get_payment_detail_non_admin(client):
    seed_users()
    token = register_and_login(client, 2, role='client')
    resp = client.get('/api/admin/payments/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


# POST /admin/payments/<payment_id>/refund

def test_refund_payment_success(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app, status='completed')
    token = get_admin_token(client)
    resp = client.post('/api/admin/payments/1/refund',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    data = resp.json
    assert data['new_status'] == 'refunded'
    assert data['payment_id'] == 1
    assert 'message' in data


def test_refund_payment_changes_status(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app, status='completed')
    token = get_admin_token(client)
    client.post('/api/admin/payments/1/refund',
        headers={'Authorization': f'Bearer {token}'}
    )
    # Verify via detail endpoint
    resp = client.get('/api/admin/payments/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.json['payment']['status'] == 'refunded'


def test_refund_already_refunded(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app, status='refunded', transaction_id='TXN_R')
    token = get_admin_token(client)
    resp = client.post('/api/admin/payments/1/refund',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 400
    assert 'error' in resp.json


def test_refund_payment_not_found(client):
    token = get_admin_token(client)
    resp = client.post('/api/admin/payments/99999/refund',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 404


def test_refund_payment_no_token(client):
    resp = client.post('/api/admin/payments/1/refund')
    assert resp.status_code == 401


def test_refund_payment_non_admin(client):
    seed_users()
    token = register_and_login(client, 2, role='client')
    resp = client.post('/api/admin/payments/1/refund',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 403


def test_refund_sends_notification(client, app):
    """Refunding should create a Notification for the client."""
    seed_users()
    seed_coaches()
    seed_payment(app, status='completed')
    token = get_admin_token(client)
    client.post('/api/admin/payments/1/refund',
        headers={'Authorization': f'Bearer {token}'}
    )
    with app.app_context():
        notif = Notification.query.filter_by(user_id=4, type='payment').first()
        assert notif is not None
        assert 'refunded' in notif.message.lower()


def test_refund_notification_includes_amount(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app, status='completed')
    token = get_admin_token(client)
    client.post('/api/admin/payments/1/refund',
        headers={'Authorization': f'Bearer {token}'}
    )
    with app.app_context():
        notif = Notification.query.filter_by(user_id=4, type='payment').first()
        assert '75' in notif.message


def test_refund_payment_500(client, app):
    seed_users()
    seed_coaches()
    seed_payment(app, status='completed')
    token = get_admin_token(client)
    with patch(BASE) as mock_commit:
        mock_commit.side_effect = Exception('Database error')
        resp = client.post('/api/admin/payments/1/refund',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert resp.status_code == 500

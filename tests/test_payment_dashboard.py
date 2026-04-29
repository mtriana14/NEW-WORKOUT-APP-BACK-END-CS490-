# tests/test_payment_dashboard.py
import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-that-is-long-enough-32chars'
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def auth_headers(client, role='admin'):
    from flask_jwt_extended import create_access_token
    with client.application.app_context():
        token = create_access_token(identity='1', additional_claims={'role': role})
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ─── UC 10.4: get_payment_summary ────────────────────────────────────────────

class TestGetPaymentSummary:

    @patch('app.controllers.payment_dashboard_controller.db')
    @patch('app.controllers.payment_dashboard_controller.Payment')
    def test_get_payment_summary_success(self, mock_payment_cls, mock_db, client):
        """Admin can retrieve payment summary."""
        mock_db.session.query.return_value.filter_by.return_value.scalar.return_value = 1500.00
        mock_payment_cls.query.count.return_value = 10
        mock_db.session.query.return_value.group_by.return_value.all.return_value = [
            ('completed', 8, 1500.00),
            ('pending', 2, 200.00)
        ]

        response = client.get('/api/admin/payments/summary', headers=auth_headers(client))
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_revenue' in data
        assert 'total_transactions' in data
        assert 'status_breakdown' in data

    @patch('app.controllers.payment_dashboard_controller.db')
    @patch('app.controllers.payment_dashboard_controller.Payment')
    def test_get_payment_summary_no_payments(self, mock_payment_cls, mock_db, client):
        """Returns zeros when no payments exist."""
        mock_db.session.query.return_value.filter_by.return_value.scalar.return_value = None
        mock_payment_cls.query.count.return_value = 0
        mock_db.session.query.return_value.group_by.return_value.all.return_value = []

        response = client.get('/api/admin/payments/summary', headers=auth_headers(client))
        assert response.status_code == 200
        assert response.get_json()['total_revenue'] == 0

    def test_get_payment_summary_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.get('/api/admin/payments/summary', headers=auth_headers(client, role='client'))
        assert response.status_code == 403

    @patch('app.controllers.payment_dashboard_controller.db')
    @patch('app.controllers.payment_dashboard_controller.Payment')
    def test_get_payment_stats_endpoint(self, mock_payment_cls, mock_db, client):
        """Stats endpoint returns same structure as summary."""
        mock_db.session.query.return_value.filter_by.return_value.scalar.return_value = 500.00
        mock_payment_cls.query.count.return_value = 5
        mock_db.session.query.return_value.group_by.return_value.all.return_value = []

        response = client.get('/api/admin/payments/stats', headers=auth_headers(client))
        assert response.status_code == 200
        assert 'total_revenue' in response.get_json()


# ─── UC 10.4: get_all_payments ───────────────────────────────────────────────

class TestGetAllPayments:

    @patch('app.controllers.payment_dashboard_controller.Coach')
    @patch('app.controllers.payment_dashboard_controller.User')
    @patch('app.controllers.payment_dashboard_controller.Payment')
    def test_get_all_payments_success(self, mock_payment_cls, mock_user_cls, mock_coach_cls, client):
        """Admin can retrieve paginated payment list."""
        mock_payment = MagicMock()
        mock_payment.payment_id = 1
        mock_payment.client_id = 5
        mock_payment.coach_id = 2
        mock_payment.amount = 100.00
        mock_payment.currency = 'USD'
        mock_payment.status = 'completed'
        mock_payment.payment_method_type = 'card'
        mock_payment.transaction_id = 'txn_123'
        mock_payment.paid_at = None
        mock_payment.created_at = None

        mock_paginate = MagicMock()
        mock_paginate.items = [mock_payment]
        mock_paginate.total = 1
        mock_paginate.pages = 1
        mock_paginate.page = 1
        mock_payment_cls.query.order_by.return_value.paginate.return_value = mock_paginate

        mock_user = MagicMock()
        mock_user.user_id = 5
        mock_user.first_name = 'John'
        mock_user.last_name = 'Doe'
        mock_user_cls.query.filter.return_value.all.return_value = [mock_user]

        mock_coach = MagicMock()
        mock_coach.coach_id = 2
        mock_coach.user = MagicMock(first_name='Jane', last_name='Smith')
        mock_coach_cls.query.filter.return_value.all.return_value = [mock_coach]

        response = client.get('/api/admin/payments', headers=auth_headers(client))
        assert response.status_code == 200
        data = response.get_json()
        assert 'payments' in data
        assert 'total' in data

    @patch('app.controllers.payment_dashboard_controller.Coach')
    @patch('app.controllers.payment_dashboard_controller.User')
    @patch('app.controllers.payment_dashboard_controller.Payment')
    def test_get_all_payments_empty(self, mock_payment_cls, mock_user_cls, mock_coach_cls, client):
        """Returns empty list when no payments exist."""
        mock_paginate = MagicMock()
        mock_paginate.items = []
        mock_paginate.total = 0
        mock_paginate.pages = 0
        mock_paginate.page = 1
        mock_payment_cls.query.order_by.return_value.paginate.return_value = mock_paginate
        mock_user_cls.query.filter.return_value.all.return_value = []
        mock_coach_cls.query.filter.return_value.all.return_value = []

        response = client.get('/api/admin/payments', headers=auth_headers(client))
        assert response.status_code == 200
        assert response.get_json()['payments'] == []

    def test_get_all_payments_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.get('/api/admin/payments', headers=auth_headers(client, role='coach'))
        assert response.status_code == 403


# ─── UC 10.4: get_coach_payment_summary ──────────────────────────────────────

class TestGetCoachPaymentSummary:

    @patch('app.controllers.payment_dashboard_controller.db')
    @patch('app.controllers.payment_dashboard_controller.Payment')
    @patch('app.controllers.payment_dashboard_controller.Coach')
    def test_get_coach_summary_success(self, mock_coach_cls, mock_payment_cls, mock_db, client):
        """Returns earnings summary for a specific coach."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach.user = MagicMock(first_name='Jane', last_name='Smith')
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        mock_db.session.query.return_value.filter_by.return_value.scalar.return_value = 800.00
        mock_payment_cls.query.filter_by.return_value.count.return_value = 6

        response = client.get('/api/admin/payments/coach/1', headers=auth_headers(client))
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_earned' in data
        assert 'total_transactions' in data

    @patch('app.controllers.payment_dashboard_controller.Coach')
    def test_get_coach_summary_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.get('/api/admin/payments/coach/999', headers=auth_headers(client))
        assert response.status_code == 404

    def test_get_coach_summary_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.get('/api/admin/payments/coach/1', headers=auth_headers(client, role='client'))
        assert response.status_code == 403
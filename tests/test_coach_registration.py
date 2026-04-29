# tests/test_coach_registration.py
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


# ─── UC 10.2: get_all_registrations ──────────────────────────────────────────

class TestGetAllRegistrations:

    @patch('app.controllers.coach_registration_controller2.db')
    def test_get_all_registrations_success(self, mock_db, client):
        """Admin can retrieve all registrations."""
        mock_user = MagicMock()
        mock_user.first_name = 'John'
        mock_user.last_name = 'Doe'
        mock_user.email = 'john@example.com'
        mock_user.phone = '1234567890'

        mock_reg = MagicMock()
        mock_reg.reg_id = 1
        mock_reg.user_id = 5
        mock_reg.qualifications = 'CPT'
        mock_reg.specialty = 'Strength'
        mock_reg.document_links = None
        mock_reg.application_status = 'pending'
        mock_reg.created_at = None
        mock_reg.updated_at = None

        mock_db.session.query.return_value.join.return_value.order_by.return_value.all.return_value = [
            (mock_reg, mock_user)
        ]

        response = client.get('/api/admin/coaches', headers=auth_headers(client))
        assert response.status_code == 200
        assert 'Registrations' in response.get_json()

    @patch('app.controllers.coach_registration_controller2.db')
    def test_get_all_registrations_empty(self, mock_db, client):
        """Returns empty list when no registrations exist."""
        mock_db.session.query.return_value.join.return_value.order_by.return_value.all.return_value = []

        response = client.get('/api/admin/coaches', headers=auth_headers(client))
        assert response.status_code == 200
        assert response.get_json()['Registrations'] == []

    def test_get_all_registrations_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.get('/api/admin/coaches', headers=auth_headers(client, role='coach'))
        assert response.status_code == 403


# ─── UC 10.2: get_pending_registrations ──────────────────────────────────────

class TestGetPendingRegistrations:

    @patch('app.controllers.coach_registration_controller2.db')
    def test_get_pending_registrations_success(self, mock_db, client):
        """Returns pending registrations."""
        mock_user = MagicMock()
        mock_user.first_name = 'Jane'
        mock_user.last_name = 'Smith'
        mock_user.email = 'jane@example.com'
        mock_user.phone = '0987654321'

        mock_reg = MagicMock()
        mock_reg.reg_id = 2
        mock_reg.user_id = 6
        mock_reg.qualifications = 'NSCA'
        mock_reg.specialty = 'Cardio'
        mock_reg.document_links = None
        mock_reg.application_status = 'pending'
        mock_reg.created_at = None
        mock_reg.updated_at = None

        mock_db.session.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [
            (mock_reg, mock_user)
        ]

        response = client.get('/api/admin/coaches/pending', headers=auth_headers(client))
        assert response.status_code == 200
        assert 'Registrations' in response.get_json()

    @patch('app.controllers.coach_registration_controller2.db')
    def test_get_pending_registrations_empty(self, mock_db, client):
        """Returns note when no pending registrations."""
        mock_db.session.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []

        response = client.get('/api/admin/coaches/pending', headers=auth_headers(client))
        assert response.status_code == 200
        assert 'registrations' in response.get_json()


# ─── UC 10.2: process_coach_registration ─────────────────────────────────────

class TestProcessCoachRegistration:

    @patch('app.controllers.coach_registration_controller2.Notification')
    @patch('app.controllers.coach_registration_controller2.db')
    @patch('app.controllers.coach_registration_controller2.Coach')
    @patch('app.controllers.coach_registration_controller2.User')
    @patch('app.controllers.coach_registration_controller2.CoachRegistration')
    def test_approve_registration_success(self, mock_cr_cls, mock_user_cls, mock_coach_cls, mock_db, mock_notif_cls, client):
        """Admin can approve a pending registration."""
        mock_reg = MagicMock()
        mock_reg.reg_id = 1
        mock_reg.user_id = 5
        mock_reg.qualifications = 'CPT'
        mock_cr_cls.query.filter_by.return_value.first.return_value = mock_reg
        mock_coach_cls.query.filter_by.return_value.first.return_value = None
        mock_user_cls.query.get.return_value = MagicMock()

        response = client.put(
            '/api/admin/coaches/1/process',
            json={'action': 'approved', 'cost': 50.00},
            headers=auth_headers(client)
        )
        assert response.status_code == 200
        assert mock_reg.application_status == 'approved'

    @patch('app.controllers.coach_registration_controller2.CoachRegistration')
    def test_approve_registration_not_found(self, mock_cr_cls, client):
        """Returns 404 when registration does not exist."""
        mock_cr_cls.query.filter_by.return_value.first.return_value = None

        response = client.put(
            '/api/admin/coaches/999/process',
            json={'action': 'approved'},
            headers=auth_headers(client)
        )
        assert response.status_code == 404

    @patch('app.controllers.coach_registration_controller2.Notification')
    @patch('app.controllers.coach_registration_controller2.db')
    @patch('app.controllers.coach_registration_controller2.CoachRegistration')
    def test_reject_registration_success(self, mock_cr_cls, mock_db, mock_notif_cls, client):
        """Admin can reject a pending registration with a reason."""
        mock_reg = MagicMock()
        mock_reg.reg_id = 1
        mock_reg.user_id = 5
        mock_cr_cls.query.filter_by.return_value.first.return_value = mock_reg

        response = client.put(
            '/api/admin/coaches/1/process',
            json={'action': 'rejected', 'rejection_reason': 'Incomplete documents'},
            headers=auth_headers(client)
        )
        assert response.status_code == 200
        assert mock_reg.application_status == 'rejected'

    @patch('app.controllers.coach_registration_controller2.CoachRegistration')
    def test_reject_registration_missing_reason(self, mock_cr_cls, client):
        """Returns 400 when rejection reason is missing."""
        mock_cr_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put(
            '/api/admin/coaches/1/process',
            json={'action': 'rejected'},
            headers=auth_headers(client)
        )
        assert response.status_code == 400

    def test_process_invalid_action(self, client):
        """Returns 400 for invalid action."""
        response = client.put(
            '/api/admin/coaches/1/process',
            json={'action': 'maybe'},
            headers=auth_headers(client)
        )
        assert response.status_code == 400

    def test_process_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.put(
            '/api/admin/coaches/1/process',
            json={'action': 'approved'},
            headers=auth_headers(client, role='client')
        )
        assert response.status_code == 403
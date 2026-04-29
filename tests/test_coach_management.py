# tests/test_coach_management.py
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


# ─── UC 10.3: suspend_coach ──────────────────────────────────────────────────

class TestSuspendCoach:

    @patch('app.controllers.coach_management_controller.Notification')
    @patch('app.controllers.coach_management_controller.db')
    @patch('app.controllers.coach_management_controller.User')
    @patch('app.controllers.coach_management_controller.Coach')
    def test_suspend_coach_success(self, mock_coach_cls, mock_user_cls, mock_db, mock_notif_cls, client):
        """Admin can suspend an active coach."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach.user_id = 5
        mock_coach.status = 'active'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_user_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put('/api/admin/coaches/1/suspend', headers=auth_headers(client))
        assert response.status_code == 200
        assert mock_coach.status == 'suspended'

    @patch('app.controllers.coach_management_controller.Coach')
    def test_suspend_coach_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.put('/api/admin/coaches/999/suspend', headers=auth_headers(client))
        assert response.status_code == 404

    @patch('app.controllers.coach_management_controller.Coach')
    def test_suspend_already_suspended(self, mock_coach_cls, client):
        """Returns 400 when coach is already suspended."""
        mock_coach = MagicMock()
        mock_coach.status = 'suspended'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        response = client.put('/api/admin/coaches/1/suspend', headers=auth_headers(client))
        assert response.status_code == 400

    def test_suspend_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.put('/api/admin/coaches/1/suspend', headers=auth_headers(client, role='client'))
        assert response.status_code == 403


# ─── UC 10.3: reactivate_coach ───────────────────────────────────────────────

class TestReactivateCoach:

    @patch('app.controllers.coach_management_controller.Notification')
    @patch('app.controllers.coach_management_controller.db')
    @patch('app.controllers.coach_management_controller.User')
    @patch('app.controllers.coach_management_controller.Coach')
    def test_reactivate_coach_success(self, mock_coach_cls, mock_user_cls, mock_db, mock_notif_cls, client):
        """Admin can reactivate a suspended coach."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach.user_id = 5
        mock_coach.status = 'suspended'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_user_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put('/api/admin/coaches/1/reactivate', headers=auth_headers(client))
        assert response.status_code == 200
        assert mock_coach.status == 'approved'

    @patch('app.controllers.coach_management_controller.Coach')
    def test_reactivate_coach_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.put('/api/admin/coaches/999/reactivate', headers=auth_headers(client))
        assert response.status_code == 404

    @patch('app.controllers.coach_management_controller.Coach')
    def test_reactivate_not_suspended(self, mock_coach_cls, client):
        """Returns 400 when coach is not suspended."""
        mock_coach = MagicMock()
        mock_coach.status = 'active'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        response = client.put('/api/admin/coaches/1/reactivate', headers=auth_headers(client))
        assert response.status_code == 400


# ─── UC 10.3: disable_coach ──────────────────────────────────────────────────

class TestDisableCoach:

    @patch('app.controllers.coach_management_controller.Notification')
    @patch('app.controllers.coach_management_controller.db')
    @patch('app.controllers.coach_management_controller.User')
    @patch('app.controllers.coach_management_controller.Coach')
    def test_disable_coach_success(self, mock_coach_cls, mock_user_cls, mock_db, mock_notif_cls, client):
        """Admin can permanently disable a coach."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach.user_id = 5
        mock_coach.status = 'active'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_user_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put('/api/admin/coaches/1/disable', headers=auth_headers(client))
        assert response.status_code == 200
        assert mock_coach.status == 'disabled'

    @patch('app.controllers.coach_management_controller.Coach')
    def test_disable_coach_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.put('/api/admin/coaches/999/disable', headers=auth_headers(client))
        assert response.status_code == 404

    @patch('app.controllers.coach_management_controller.Coach')
    def test_disable_already_disabled(self, mock_coach_cls, client):
        """Returns 400 when coach is already disabled."""
        mock_coach = MagicMock()
        mock_coach.status = 'disabled'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        response = client.put('/api/admin/coaches/1/disable', headers=auth_headers(client))
        assert response.status_code == 400


# ─── UC 10.3: update_coach_status ────────────────────────────────────────────

class TestUpdateCoachStatus:

    @patch('app.controllers.coach_management_controller.Notification')
    @patch('app.controllers.coach_management_controller.db')
    @patch('app.controllers.coach_management_controller.User')
    @patch('app.controllers.coach_management_controller.Coach')
    def test_update_status_suspend(self, mock_coach_cls, mock_user_cls, mock_db, mock_notif_cls, client):
        """Routes suspend action correctly."""
        mock_coach = MagicMock()
        mock_coach.status = 'active'
        mock_coach.user_id = 5
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_user_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put('/api/admin/coaches/1/status', json={'status': 'suspend'}, headers=auth_headers(client))
        assert response.status_code == 200

    @patch('app.controllers.coach_management_controller.Notification')
    @patch('app.controllers.coach_management_controller.db')
    @patch('app.controllers.coach_management_controller.User')
    @patch('app.controllers.coach_management_controller.Coach')
    def test_update_status_reactivate(self, mock_coach_cls, mock_user_cls, mock_db, mock_notif_cls, client):
        """Routes reactivate action correctly."""
        mock_coach = MagicMock()
        mock_coach.status = 'suspended'
        mock_coach.user_id = 5
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_user_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put('/api/admin/coaches/1/status', json={'status': 'reactivate'}, headers=auth_headers(client))
        assert response.status_code == 200

    @patch('app.controllers.coach_management_controller.Notification')
    @patch('app.controllers.coach_management_controller.db')
    @patch('app.controllers.coach_management_controller.User')
    @patch('app.controllers.coach_management_controller.Coach')
    def test_update_status_disable(self, mock_coach_cls, mock_user_cls, mock_db, mock_notif_cls, client):
        """Routes disable action correctly."""
        mock_coach = MagicMock()
        mock_coach.status = 'active'
        mock_coach.user_id = 5
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_user_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put('/api/admin/coaches/1/status', json={'status': 'disable'}, headers=auth_headers(client))
        assert response.status_code == 200

    def test_update_status_invalid(self, client):
        """Returns 400 for invalid status value."""
        response = client.put('/api/admin/coaches/1/status', json={'status': 'ban'}, headers=auth_headers(client))
        assert response.status_code == 400
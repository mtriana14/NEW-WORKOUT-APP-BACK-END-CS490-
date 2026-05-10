# tests/test_client_request.py
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from app.config.db import db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def auth_headers(client, role='client'):
    """Helper to get JWT token with a specific role."""
    from flask_jwt_extended import create_access_token
    with client.application.app_context():
        token = create_access_token(identity='1', additional_claims={'role': role})
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ─── UC 9.4: send_request ────────────────────────────────────────────────────

class TestSendRequest:

    @patch('app.controllers.client_request_controller.Notification')
    @patch('app.controllers.client_request_controller.db')
    @patch('app.controllers.client_request_controller.Hire')
    @patch('app.controllers.client_request_controller.ClientRequest')
    @patch('app.controllers.client_request_controller.Coach')
    def test_send_request_success(self, mock_coach_cls, mock_cr_cls, mock_hire_cls, mock_db, mock_notif_cls, client):
        """Client can successfully send a request to an available coach."""
        mock_coach = MagicMock()
        mock_coach.status = 'active'
        mock_coach.user_id = 99
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        mock_cr_cls.query.filter_by.return_value.first.return_value = None  # no existing request
        mock_hire_cls.query.filter_by.return_value.first.return_value = None  # no active hire

        mock_request_obj = MagicMock()
        mock_request_obj.request_id = 10
        mock_cr_cls.return_value = mock_request_obj

        response = client.post(
            '/api/client/request-coach/1',
            json={'message': 'I want coaching'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 201
        data = response.get_json()
        assert 'request_id' in data

    @patch('app.controllers.client_request_controller.Coach')
    def test_send_request_coach_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.post(
            '/api/client/request-coach/999',
            json={'message': 'Hello'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 404

    @patch('app.controllers.client_request_controller.Coach')
    def test_send_request_coach_not_available(self, mock_coach_cls, client):
        """Returns 400 when coach is suspended."""
        mock_coach = MagicMock()
        mock_coach.status = 'suspended'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        response = client.post(
            '/api/client/request-coach/1',
            json={'message': 'Hello'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 400

    @patch('app.controllers.client_request_controller.ClientRequest')
    @patch('app.controllers.client_request_controller.Coach')
    def test_send_request_duplicate_pending(self, mock_coach_cls, mock_cr_cls, client):
        """Returns 409 when client already has a pending request to the same coach."""
        mock_coach = MagicMock()
        mock_coach.status = 'active'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_cr_cls.query.filter_by.return_value.first.return_value = MagicMock()  # existing pending

        response = client.post(
            '/api/client/request-coach/1',
            json={'message': 'Again'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 409

    @patch('app.controllers.client_request_controller.Hire')
    @patch('app.controllers.client_request_controller.ClientRequest')
    @patch('app.controllers.client_request_controller.Coach')
    def test_send_request_already_hired(self, mock_coach_cls, mock_cr_cls, mock_hire_cls, client):
        """Returns 409 when client already has an active hire with this coach."""
        mock_coach = MagicMock()
        mock_coach.status = 'active'
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_cr_cls.query.filter_by.return_value.first.return_value = None
        mock_hire_cls.query.filter_by.return_value.first.return_value = MagicMock()  # active hire

        response = client.post(
            '/api/client/request-coach/1',
            json={'message': 'Hi'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 409


# ─── UC 9.4: get_pending_requests ────────────────────────────────────────────

class TestGetPendingRequests:

    @patch('app.controllers.client_request_controller.User')
    @patch('app.controllers.client_request_controller.ClientRequest')
    @patch('app.controllers.client_request_controller.Coach')
    def test_get_pending_requests_success(self, mock_coach_cls, mock_cr_cls, mock_user_cls, client):
        """Coach can retrieve their pending requests."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = MagicMock()
        mock_user_cls.query.filter_by.return_value.first.return_value = None

        mock_req = MagicMock()
        mock_req.request_id = 1
        mock_req.client_id = 5
        mock_req.coach_id = 1
        mock_req.message = 'Please coach me'
        mock_req.status = 'pending'
        mock_req.responded_at = None
        mock_req.created_at = '2026-01-01'
        mock_cr_cls.query.filter_by.return_value.all.return_value = [mock_req]

        response = client.get('/api/coach/1/requests', headers=auth_headers(client, role='coach'))
        assert response.status_code == 200
        data = response.get_json()
        assert 'requests' in data
        assert len(data['requests']) == 1

    @patch('app.controllers.client_request_controller.Coach')
    def test_get_pending_requests_coach_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.get('/api/coach/999/requests', headers=auth_headers(client, role='coach'))
        assert response.status_code == 404

    @patch('app.controllers.client_request_controller.ClientRequest')
    @patch('app.controllers.client_request_controller.Coach')
    def test_get_pending_requests_empty(self, mock_coach_cls, mock_cr_cls, client):
        """Returns empty list when no pending requests."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = MagicMock()
        mock_cr_cls.query.filter_by.return_value.all.return_value = []

        response = client.get('/api/coach/1/requests', headers=auth_headers(client, role='coach'))
        assert response.status_code == 200
        assert response.get_json()['requests'] == []


# ─── UC 9.4: respond_to_request ──────────────────────────────────────────────

class TestRespondToRequest:

    @patch('app.controllers.client_request_controller.Notification')
    @patch('app.controllers.client_request_controller.db')
    @patch('app.controllers.client_request_controller.Hire')
    @patch('app.controllers.client_request_controller.ClientRequest')
    def test_accept_request_success(self, mock_cr_cls, mock_hire_cls, mock_db, mock_notif_cls, client):
        """Coach can accept a pending request and a Hire record is created."""
        mock_req = MagicMock()
        mock_req.client_id = 5
        mock_req.coach_id = 1
        mock_cr_cls.query.filter_by.return_value.first.return_value = mock_req

        response = client.put(
            '/api/coach/requests/1/respond',
            json={'action': 'accepted'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 200
        mock_hire_cls.assert_called_once()

    @patch('app.controllers.client_request_controller.Notification')
    @patch('app.controllers.client_request_controller.db')
    @patch('app.controllers.client_request_controller.ClientRequest')
    def test_decline_request_success(self, mock_cr_cls, mock_db, mock_notif_cls, client):
        """Coach can decline a pending request, no Hire created."""
        mock_req = MagicMock()
        mock_req.client_id = 5
        mock_cr_cls.query.filter_by.return_value.first.return_value = mock_req

        response = client.put(
            '/api/coach/requests/1/respond',
            json={'action': 'declined'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 200

    @patch('app.controllers.client_request_controller.ClientRequest')
    def test_respond_invalid_action(self, mock_cr_cls, client):
        """Returns 400 for invalid action value."""
        response = client.put(
            '/api/coach/requests/1/respond',
            json={'action': 'maybe'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 400

    @patch('app.controllers.client_request_controller.ClientRequest')
    def test_respond_request_not_found(self, mock_cr_cls, client):
        """Returns 404 when request doesn't exist or already responded."""
        mock_cr_cls.query.filter_by.return_value.first.return_value = None

        response = client.put(
            '/api/coach/requests/999/respond',
            json={'action': 'accepted'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 404
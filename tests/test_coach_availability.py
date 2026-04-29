# tests/test_coach_availability.py
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


def auth_headers(client, role='coach'):
    from flask_jwt_extended import create_access_token
    with client.application.app_context():
        token = create_access_token(identity='1', additional_claims={'role': role})
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


VALID_SLOTS = [
    {'day_of_week': 'Monday', 'start_time': '09:00:00', 'end_time': '11:00:00', 'is_available': True},
    {'day_of_week': 'Wednesday', 'start_time': '14:00:00', 'end_time': '16:00:00', 'is_available': True}
]


# ─── UC 9.3: set_availability ────────────────────────────────────────────────

class TestSetAvailability:

    @patch('app.controllers.coach_availability_controller.db')
    @patch('app.controllers.coach_availability_controller.CoachAvailability')
    @patch('app.controllers.coach_availability_controller.Coach')
    def test_set_availability_success(self, mock_coach_cls, mock_avail_cls, mock_db, client):
        """Coach can set availability slots successfully."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach
        mock_avail_cls.query.filter_by.return_value.delete.return_value = None

        response = client.post(
            '/api/coach/availability',
            json={'slots': VALID_SLOTS},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Availability updated successfully'

    @patch('app.controllers.coach_availability_controller.Coach')
    def test_set_availability_coach_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.post(
            '/api/coach/availability',
            json={'slots': VALID_SLOTS},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 404

    @patch('app.controllers.coach_availability_controller.Coach')
    def test_set_availability_no_slots(self, mock_coach_cls, client):
        """Returns 400 when no slots are provided."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        response = client.post(
            '/api/coach/availability',
            json={'slots': []},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 400

    @patch('app.controllers.coach_availability_controller.Coach')
    def test_set_availability_missing_slots_key(self, mock_coach_cls, client):
        """Returns 400 when slots key is missing from payload."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        response = client.post(
            '/api/coach/availability',
            json={},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 400

    def test_set_availability_requires_coach_role(self, client):
        """Returns 403 when called with a non-coach token."""
        response = client.post(
            '/api/coach/availability',
            json={'slots': VALID_SLOTS},
            headers=auth_headers(client, role='client')
        )
        assert response.status_code == 403


# ─── UC 9.3: get_availability ────────────────────────────────────────────────

class TestGetAvailability:

    @patch('app.controllers.coach_availability_controller.CoachAvailability')
    @patch('app.controllers.coach_availability_controller.Coach')
    def test_get_availability_success(self, mock_coach_cls, mock_avail_cls, client):
        """Returns availability slots for a valid coach."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = MagicMock()

        mock_slot = MagicMock()
        mock_slot.availability_id = 1
        mock_slot.day_of_week = 'Monday'
        mock_slot.start_time = '09:00:00'
        mock_slot.end_time = '11:00:00'
        mock_slot.is_available = True
        mock_avail_cls.query.filter_by.return_value.all.return_value = [mock_slot]

        response = client.get('/api/coach/availability/1', headers=auth_headers(client, role='client'))
        assert response.status_code == 200
        data = response.get_json()
        assert 'availability' in data
        assert len(data['availability']) == 1

    @patch('app.controllers.coach_availability_controller.Coach')
    def test_get_availability_coach_not_found(self, mock_coach_cls, client):
        """Returns 404 when coach does not exist."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.get('/api/coach/availability/999', headers=auth_headers(client, role='client'))
        assert response.status_code == 404

    @patch('app.controllers.coach_availability_controller.CoachAvailability')
    @patch('app.controllers.coach_availability_controller.Coach')
    def test_get_availability_empty(self, mock_coach_cls, mock_avail_cls, client):
        """Returns empty list when coach has no availability set."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = MagicMock()
        mock_avail_cls.query.filter_by.return_value.all.return_value = []

        response = client.get('/api/coach/availability/1', headers=auth_headers(client, role='client'))
        assert response.status_code == 200
        assert response.get_json()['availability'] == []


# ─── UC 9.3: get_availability_by_user ────────────────────────────────────────

class TestGetAvailabilityByUser:

    @patch('app.controllers.coach_availability_controller.CoachAvailability')
    @patch('app.controllers.coach_availability_controller.Coach')
    def test_get_availability_by_user_success(self, mock_coach_cls, mock_avail_cls, client):
        """Returns availability when looked up by user_id."""
        mock_coach = MagicMock()
        mock_coach.coach_id = 1
        mock_coach_cls.query.filter_by.return_value.first.return_value = mock_coach

        mock_slot = MagicMock()
        mock_slot.availability_id = 1
        mock_slot.day_of_week = 'Friday'
        mock_slot.start_time = '10:00:00'
        mock_slot.end_time = '12:00:00'
        mock_slot.is_available = True
        mock_avail_cls.query.filter_by.return_value.all.return_value = [mock_slot]

        response = client.get('/api/coach/1/availability', headers=auth_headers(client, role='client'))
        assert response.status_code == 200
        assert 'availability' in response.get_json()

    @patch('app.controllers.coach_availability_controller.Coach')
    def test_get_availability_by_user_not_found(self, mock_coach_cls, client):
        """Returns 404 when user_id has no associated coach."""
        mock_coach_cls.query.filter_by.return_value.first.return_value = None

        response = client.get('/api/coach/999/availability', headers=auth_headers(client, role='client'))
        assert response.status_code == 404
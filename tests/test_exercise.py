# tests/test_exercise.py
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


VALID_EXERCISE = {
    'name': 'Bench Press',
    'muscle_group': 'chest',
    'equipment': 'barbell',
    'difficulty': 'intermediate',
    'instructions': 'Lie on bench and press',
    'video_url': 'http://example.com/video'
}


# ─── UC 10.1: get_all_exercises ──────────────────────────────────────────────

class TestGetAllExercises:

    @patch('app.controllers.exercise_controller.Exercise')
    def test_get_all_exercises_success(self, mock_ex_cls, client):
        """Returns list of active exercises."""
        mock_ex = MagicMock()
        mock_ex.e_id = 1
        mock_ex.name = 'Bench Press'
        mock_ex.description = 'Chest exercise'
        mock_ex.muscle_group = 'chest'
        mock_ex.equipment_type = 'barbell'
        mock_ex.difficulty = 'intermediate'
        mock_ex.instructions = 'Press up'
        mock_ex.video_url = 'http://example.com'
        mock_ex.created_at = '2026-01-01'
        mock_ex_cls.query.filter_by.return_value.all.return_value = [mock_ex]

        response = client.get('/api/admin/exercises', headers=auth_headers(client, role='client'))
        assert response.status_code == 200
        assert 'exercises' in response.get_json()

    @patch('app.controllers.exercise_controller.Exercise')
    def test_get_all_exercises_empty(self, mock_ex_cls, client):
        """Returns empty list when no active exercises exist."""
        mock_ex_cls.query.filter_by.return_value.all.return_value = []

        response = client.get('/api/admin/exercises', headers=auth_headers(client, role='client'))
        assert response.status_code == 200
        assert response.get_json()['exercises'] == []

    def test_get_all_exercises_requires_auth(self, client):
        """Returns 401 when no token provided."""
        response = client.get('/api/admin/exercises')
        assert response.status_code == 401


# ─── UC 10.1: create_exercise ────────────────────────────────────────────────

class TestCreateExercise:

    @patch('app.controllers.exercise_controller.db')
    @patch('app.controllers.exercise_controller.Exercise')
    def test_create_exercise_success(self, mock_ex_cls, mock_db, client):
        """Admin can create a new exercise."""
        mock_ex_cls.query.filter_by.return_value.first.return_value = None
        mock_instance = MagicMock()
        mock_instance.e_id = 1
        mock_ex_cls.return_value = mock_instance

        response = client.post('/api/admin/exercises', json=VALID_EXERCISE, headers=auth_headers(client))
        assert response.status_code == 201

    @patch('app.controllers.exercise_controller.Exercise')
    def test_create_exercise_missing_name(self, mock_ex_cls, client):
        """Returns 400 when name is missing."""
        response = client.post(
            '/api/admin/exercises',
            json={'muscle_group': 'chest'},
            headers=auth_headers(client)
        )
        assert response.status_code == 400

    @patch('app.controllers.exercise_controller.Exercise')
    def test_create_exercise_missing_muscle_group(self, mock_ex_cls, client):
        """Returns 400 when muscle_group is missing."""
        response = client.post(
            '/api/admin/exercises',
            json={'name': 'Squat'},
            headers=auth_headers(client)
        )
        assert response.status_code == 400

    @patch('app.controllers.exercise_controller.Exercise')
    def test_create_exercise_duplicate(self, mock_ex_cls, client):
        """Returns 409 when exercise name already exists."""
        mock_ex_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.post('/api/admin/exercises', json=VALID_EXERCISE, headers=auth_headers(client))
        assert response.status_code == 409

    def test_create_exercise_requires_admin(self, client):
        """Returns 403 when called with non-admin token."""
        response = client.post(
            '/api/admin/exercises',
            json=VALID_EXERCISE,
            headers=auth_headers(client, role='client')
        )
        assert response.status_code == 403


# ─── UC 10.1: update_exercise ────────────────────────────────────────────────

class TestUpdateExercise:

    @patch('app.controllers.exercise_controller.db')
    @patch('app.controllers.exercise_controller.Exercise')
    def test_update_exercise_success(self, mock_ex_cls, mock_db, client):
        """Admin can update an existing exercise."""
        mock_ex_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.put(
            '/api/admin/exercises/1',
            json={'name': 'Updated Bench Press'},
            headers=auth_headers(client)
        )
        assert response.status_code == 200

    @patch('app.controllers.exercise_controller.Exercise')
    def test_update_exercise_not_found(self, mock_ex_cls, client):
        """Returns 404 when exercise does not exist."""
        mock_ex_cls.query.filter_by.return_value.first.return_value = None

        response = client.put(
            '/api/admin/exercises/999',
            json={'name': 'Ghost'},
            headers=auth_headers(client)
        )
        assert response.status_code == 404

    def test_update_exercise_requires_admin(self, client):
        """Returns 403 when called with non-admin token."""
        response = client.put(
            '/api/admin/exercises/1',
            json={'name': 'Hack'},
            headers=auth_headers(client, role='coach')
        )
        assert response.status_code == 403


# ─── UC 10.1: delete_exercise ────────────────────────────────────────────────

class TestDeleteExercise:

    @patch('app.controllers.exercise_controller.db')
    @patch('app.controllers.exercise_controller.Exercise')
    def test_delete_exercise_success(self, mock_ex_cls, mock_db, client):
        """Admin can soft delete an exercise."""
        mock_exercise = MagicMock()
        mock_ex_cls.query.filter_by.return_value.first.return_value = mock_exercise

        response = client.delete('/api/admin/exercises/1', headers=auth_headers(client))
        assert response.status_code == 200
        assert mock_exercise.is_active == False

    @patch('app.controllers.exercise_controller.Exercise')
    def test_delete_exercise_not_found(self, mock_ex_cls, client):
        """Returns 404 when exercise does not exist."""
        mock_ex_cls.query.filter_by.return_value.first.return_value = None

        response = client.delete('/api/admin/exercises/999', headers=auth_headers(client))
        assert response.status_code == 404

    def test_delete_exercise_requires_admin(self, client):
        """Returns 403 when called with non-admin token."""
        response = client.delete(
            '/api/admin/exercises/1',
            headers=auth_headers(client, role='client')
        )
        assert response.status_code == 403
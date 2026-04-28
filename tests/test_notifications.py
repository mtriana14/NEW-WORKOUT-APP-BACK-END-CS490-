# tests/test_notifications.py
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


def auth_headers(client, role='client'):
    from flask_jwt_extended import create_access_token
    with client.application.app_context():
        token = create_access_token(identity='1', additional_claims={'role': role})
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ─── UC 11.1: get_all_notifications ──────────────────────────────────────────

class TestGetAllNotifications:

    @patch('app.controllers.notification_controller.User')
    @patch('app.controllers.notification_controller.Notification')
    def test_get_all_notifications_success(self, mock_notif_cls, mock_user_cls, client):
        """Admin can retrieve all notifications."""
        mock_n = MagicMock()
        mock_n.notification_id = 1
        mock_n.user_id = 5
        mock_n.title = 'Test'
        mock_n.message = 'Hello'
        mock_n.type = 'system'
        mock_n.is_read = False
        mock_n.created_at = '2026-01-01'
        mock_notif_cls.query.order_by.return_value.all.return_value = [mock_n]

        mock_user = MagicMock()
        mock_user.user_id = 5
        mock_user.first_name = 'John'
        mock_user.last_name = 'Doe'
        mock_user_cls.query.filter.return_value.all.return_value = [mock_user]

        response = client.get('/api/admin/notifications', headers=auth_headers(client, role='admin'))
        assert response.status_code == 200
        assert 'notifications' in response.get_json()

    def test_get_all_notifications_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.get('/api/admin/notifications', headers=auth_headers(client, role='client'))
        assert response.status_code == 403


# ─── UC 11.1: get_user_notifications ─────────────────────────────────────────

class TestGetUserNotifications:

    @patch('app.controllers.notification_controller.Notification')
    def test_get_user_notifications_success(self, mock_notif_cls, client):
        """User can retrieve their notifications."""
        mock_n = MagicMock()
        mock_n.notification_id = 1
        mock_n.title = 'Hello'
        mock_n.message = 'Test message'
        mock_n.type = 'system'
        mock_n.is_read = False
        mock_n.created_at = '2026-01-01'
        mock_notif_cls.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_n]

        response = client.get('/api/notifications/user/1', headers=auth_headers(client))
        assert response.status_code == 200
        assert 'notifications' in response.get_json()

    @patch('app.controllers.notification_controller.Notification')
    def test_get_user_notifications_empty(self, mock_notif_cls, client):
        """Returns empty list when user has no notifications."""
        mock_notif_cls.query.filter_by.return_value.order_by.return_value.all.return_value = []

        response = client.get('/api/notifications/user/1', headers=auth_headers(client))
        assert response.status_code == 200
        assert response.get_json()['notifications'] == []


# ─── UC 11.1: get_unread_notifications ───────────────────────────────────────

class TestGetUnreadNotifications:

    @patch('app.controllers.notification_controller.Notification')
    def test_get_unread_notifications_success(self, mock_notif_cls, client):
        """Returns only unread notifications with count."""
        mock_n = MagicMock()
        mock_n.notification_id = 1
        mock_n.title = 'Unread'
        mock_n.message = 'You have a message'
        mock_n.type = 'system'
        mock_n.created_at = '2026-01-01'
        mock_notif_cls.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_n]

        response = client.get('/api/notifications/user/1/unread', headers=auth_headers(client))
        assert response.status_code == 200
        data = response.get_json()
        assert 'unread_count' in data
        assert data['unread_count'] == 1

    @patch('app.controllers.notification_controller.Notification')
    def test_get_unread_notifications_none(self, mock_notif_cls, client):
        """Returns zero count when all notifications are read."""
        mock_notif_cls.query.filter_by.return_value.order_by.return_value.all.return_value = []

        response = client.get('/api/notifications/user/1/unread', headers=auth_headers(client))
        assert response.status_code == 200
        assert response.get_json()['unread_count'] == 0


# ─── UC 11.1: mark_as_read ───────────────────────────────────────────────────

class TestMarkAsRead:

    @patch('app.controllers.notification_controller.db')
    @patch('app.controllers.notification_controller.Notification')
    def test_mark_as_read_success(self, mock_notif_cls, mock_db, client):
        """User can mark a notification as read."""
        mock_n = MagicMock()
        mock_notif_cls.query.filter_by.return_value.first.return_value = mock_n

        response = client.put('/api/notifications/1/read', headers=auth_headers(client))
        assert response.status_code == 200
        assert mock_n.is_read == True

    @patch('app.controllers.notification_controller.Notification')
    def test_mark_as_read_not_found(self, mock_notif_cls, client):
        """Returns 404 when notification does not exist."""
        mock_notif_cls.query.filter_by.return_value.first.return_value = None

        response = client.put('/api/notifications/999/read', headers=auth_headers(client))
        assert response.status_code == 404


# ─── UC 11.1: mark_all_as_read ───────────────────────────────────────────────

class TestMarkAllAsRead:

    @patch('app.controllers.notification_controller.db')
    @patch('app.controllers.notification_controller.Notification')
    def test_mark_all_as_read_success(self, mock_notif_cls, mock_db, client):
        """User can mark all notifications as read."""
        mock_notif_cls.query.filter_by.return_value.update.return_value = None

        response = client.put('/api/notifications/user/1/read-all', headers=auth_headers(client))
        assert response.status_code == 200


# ─── UC 11.1: send_notification ──────────────────────────────────────────────

class TestSendNotification:

    @patch('app.controllers.notification_controller.db')
    @patch('app.controllers.notification_controller.Notification')
    def test_send_notification_success(self, mock_notif_cls, mock_db, client):
        """Admin can send a notification to a user."""
        mock_instance = MagicMock()
        mock_instance.notification_id = 1
        mock_notif_cls.return_value = mock_instance

        response = client.post(
            '/api/notifications',
            json={'user_id': 5, 'title': 'Hello', 'message': 'Test'},
            headers=auth_headers(client, role='admin')
        )
        assert response.status_code == 201

    def test_send_notification_missing_fields(self, client):
        """Returns 400 when required fields are missing."""
        response = client.post(
            '/api/notifications',
            json={'title': 'Hello'},
            headers=auth_headers(client, role='admin')
        )
        assert response.status_code == 400

    def test_send_notification_requires_admin(self, client):
        """Returns 403 for non-admin."""
        response = client.post(
            '/api/notifications',
            json={'user_id': 5, 'title': 'Hello', 'message': 'Test'},
            headers=auth_headers(client, role='client')
        )
        assert response.status_code == 403


# ─── UC 11.1: delete_notification ────────────────────────────────────────────

class TestDeleteNotification:

    @patch('app.controllers.notification_controller.db')
    @patch('app.controllers.notification_controller.Notification')
    def test_delete_notification_success(self, mock_notif_cls, mock_db, client):
        """User can delete a notification."""
        mock_notif_cls.query.filter_by.return_value.first.return_value = MagicMock()

        response = client.delete('/api/notifications/1', headers=auth_headers(client))
        assert response.status_code == 200

    @patch('app.controllers.notification_controller.Notification')
    def test_delete_notification_not_found(self, mock_notif_cls, client):
        """Returns 404 when notification does not exist."""
        mock_notif_cls.query.filter_by.return_value.first.return_value = None

        response = client.delete('/api/notifications/999', headers=auth_headers(client))
        assert response.status_code == 404
import pytest
from app import create_app
from app.config.db import db
from tests.pre_builts import create_user

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DB_NAME'] = 'test_db'

    with app.app_context():
        yield app

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        yield
        db.session.rollback()
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
        db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    client.post('/api/auth/register', json=create_user(1))
    resp = client.post('/api/auth/login', json={
        "email": create_user(1)['email'],
        "password": "password"
    })
    token = resp.json['token']

    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return client
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db
from app.models import User, UserRole
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    with app.app_context():
        db.create_all()
        # Create a test admin user
        admin = User(
            firstname='Admin',
            lastname='User',
            username='admin',
            email='admin@example.com',
            role=UserRole.ADMIN
        )
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_token(app, user_id, role):
    with app.app_context():
        return create_access_token(identity=user_id, additional_claims={'role': role})

def test_user_registration(client):
    res = client.post('/users/', json={
        'firstname': 'John',
        'lastname': 'Doe',
        'username': 'johndoe',
        'email': 'john@example.com',
        'password': 'pass123'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['username'] == 'johndoe'
    assert data['email'] == 'john@example.com'

def test_login(client, app):
    # Register a user
    client.post('/users/', json={
        'firstname': 'Jane',
        'lastname': 'Smith',
        'username': 'janesmith',
        'email': 'jane@example.com',
        'password': 'pass456'
    })
    # Login
    res = client.post('/auth/login', json={
        'username': 'janesmith',
        'password': 'pass456'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_get_users_admin_only(client, app):
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        token = get_token(app, admin.id, admin.role)
    res = client.get('/users/', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    users = res.get_json()
    assert isinstance(users, list)

def test_admin_can_delete_user(client, app):
    # Register a user
    res = client.post('/users/', json={
        'firstname': 'ToDelete',
        'lastname': 'User',
        'username': 'deleteuser',
        'email': 'delete@example.com',
        'password': 'deletepass'
    })
    user_id = res.get_json()['id']
    # Get admin token
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        token = get_token(app, admin.id, admin.role)
    # Delete user
    res = client.delete(f'/users/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 204

def test_telemetry_post_researcher(client, app):
    # Register researcher
    res = client.post('/users/', json={
        'firstname': 'Res',
        'lastname': 'Earcher',
        'username': 'researcher',
        'email': 'researcher@example.com',
        'password': 'researchpass'
    })
    user_id = res.get_json()['id']
    with app.app_context():
        user = User.query.get(user_id)
        user.role = UserRole.RESEARCHER
        db.session.commit()
        token = get_token(app, user.id, user.role)
    telemetry = {
        "date": "2025-09-01",
        "time": "09:00:00",
        "timezone": "UTC",
        "coordinates": "12,34",
        "temperatures": {"C": 23, "F": 73},
        "humidity": 55,
        "wind": {"speed": 10, "direction": "N"},
        "precipitation": 1.2,
        "haze": False,
        "notes": "Sunny",
        "salinity": 3.2,
        "ph_level": 7.5,
        "pollutants": {"NO2": 0.01}
    }
    res = client.post('/telemetry/', json=telemetry, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 201
    data = res.get_json()
    assert data['coordinates'] == "12,34"

def test_unauthenticated_access(client):
    res = client.get('/telemetry/')
    assert res.status_code == 401
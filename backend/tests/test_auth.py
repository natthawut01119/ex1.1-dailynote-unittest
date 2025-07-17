import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app  # ✅ import ได้แน่นอนตอนนี้
from models import User
from mongoengine import disconnect, connect
import mongomock


@pytest.fixture(autouse=True)
def mongo_mock():
    disconnect()

    # สร้าง client ด้วย mongomock + ใส่ uuidRepresentation
    mock_client = mongomock.MongoClient(uuidRepresentation="standard")

    connect(
        db='testdb',
        alias='default',
        host='mongodb://localhost',  # ต้องใส่อะไรสักอย่างให้ไม่เป็น None
        mongo_client_class=lambda *args, **kwargs: mock_client  # ✅ ใช้ lambda คืน client
    )

    yield
    disconnect()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register_success(client):
    response = client.post('/api/register', json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert response.get_json()["msg"] == "User registered successfully"

def test_register_duplicate(client):
    User(username="testuser", password="hashed").save()
    response = client.post('/api/register', json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 400
    assert response.get_json()["msg"] == "Username already exists"

def test_login_success(client):
    from werkzeug.security import generate_password_hash
    hashed_pw = generate_password_hash("testpass")
    User(username="testuser", password=hashed_pw).save()

    response = client.post('/api/login', json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_invalid_password(client):
    from werkzeug.security import generate_password_hash
    hashed_pw = generate_password_hash("correctpass")
    User(username="testuser", password=hashed_pw).save()

    response = client.post('/api/login', json={
        "username": "testuser",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.get_json()["msg"] == "Invalid credentials"

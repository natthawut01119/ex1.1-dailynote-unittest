import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from models import User, Note
from werkzeug.security import generate_password_hash
import mongomock
from mongoengine import connect, disconnect

@pytest.fixture(autouse=True)
def mongo_mock():
    disconnect()
    mock_client = mongomock.MongoClient(uuidRepresentation="standard")
    connect(
        db='testdb',
        alias='default',
        host='mongodb://localhost',
        mongo_client_class=lambda *args, **kwargs: mock_client
    )
    yield
    disconnect()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def access_token(client):
    password = generate_password_hash("testpass")
    user = User(username="testuser", password=password)
    user.save()
    res = client.post('/api/login', json={"username": "testuser", "password": "testpass"})
    return res.get_json()['access_token']

def test_create_note(client, access_token):
    res = client.post('/api/notes',
        json={"title": "Test Note", "content": "Note content"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert res.status_code == 200
    assert res.get_json()["msg"] == "Note created!"

def test_get_notes(client, access_token):
    user = User.objects.first()
    Note(title="Note 1", content="Text 1", user=user).save()
    Note(title="Note 2", content="Text 2", user=user).save()

    res = client.get('/api/notes',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 2
    assert data[0]["title"] in ["Note 1", "Note 2"]

def test_update_note(client, access_token):
    user = User.objects.first()
    note = Note(title="Before", content="Before", user=user).save()

    res = client.put(f'/api/notes/{note.id}',
        json={"title": "After", "content": "Updated"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert res.status_code == 200
    assert res.get_json()["msg"] == "Note updated!"
    updated = Note.objects(id=note.id).first()
    assert updated.title == "After"

def test_delete_note(client, access_token):
    user = User.objects.first()
    note = Note(title="To Delete", content="Bye", user=user).save()

    res = client.delete(f'/api/notes/{note.id}',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert res.status_code == 200
    assert res.get_json()["msg"] == "Note deleted!"
    assert Note.objects(id=note.id).first() is None

def test_search_notes(client, access_token):
    user = User.objects.first()
    Note(title="Python Tips", content="Use pytest", user=user).save()
    Note(title="Vue Guide", content="Vue is awesome", user=user).save()
    Note(title="Random", content="Just a note", user=user).save()

    # ค้นหา title ที่มีคำว่า 'python'
    res = client.get('/api/notes/search?title=python',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    data = res.get_json()

    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == "Python Tips"
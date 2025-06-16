import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def created_ticket():
    response = client.post("/tickets/", json={"title": "Bug", "description": "Fix crash"})
    return response.json()

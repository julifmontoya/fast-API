# app/tests/test_tickets.py
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.ticket import TicketOut  # ✅ Import your Pydantic model

import pytest

client = TestClient(app)

@pytest.fixture
def created_ticket():
    payload = {"title": "Bug", "description": "Fix crash"}
    response = client.post("/tickets/", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_ticket():
    payload = {"title": "Bug", "description": "Fix crash"}
    response = client.post("/tickets/", json=payload)
    assert response.status_code == 201

    ticket = TicketOut(**response.json())  # ✅ Pydantic validation
    assert ticket.title == payload["title"]
    assert ticket.status == "open"


def test_get_ticket(created_ticket):
    ticket_id = created_ticket["id"]
    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200

    ticket = TicketOut(**response.json())  # ✅ Validate structure
    assert ticket.id == ticket_id


def test_list_tickets():
    response = client.get("/tickets/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    for ticket_data in response.json():
        TicketOut(**ticket_data)  # ✅ All items must match schema


def test_update_ticket(created_ticket):
    ticket_id = created_ticket["id"]
    response = client.put(f"/tickets/{ticket_id}", json={"status": "closed"})
    assert response.status_code == 200

    ticket = TicketOut(**response.json())  # ✅ Validate update
    assert ticket.status == "closed"


def test_delete_ticket(created_ticket):
    ticket_id = created_ticket["id"]
    response = client.delete(f"/tickets/{ticket_id}")
    assert response.status_code == 200 or response.status_code == 204

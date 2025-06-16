# Learning Flask-API Fast with Senior-Level Structure
We'll build a simple Ticket Management System with these 5 endpoints:

```
POST /tickets – Create a new ticket
GET /tickets – List all tickets
GET /tickets/{ticket_id} – Get a single ticket
PUT /tickets/{ticket_id} – Update a ticket
DELETE /tickets/{ticket_id} – Delete a ticket
```

## Run app
```
uvicorn app.main:app --reload
```

## 1. Folder Structure
```
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   └── ticket.py
│   ├── schemas/
│   │   └── ticket.py
│   ├── database.py
│   ├── routes/
│   │   └── ticket_routes.py
│   ├── services/
│   │   └── ticket_service.py
│
├── tests/
│   └── test_tickets.py
│
├── .env
├── requirements.txt
└── README.md
```

## 2. Requirements
```
pip install -r requirements.txt
python -m venv venv
venv\Scripts\activate 
```

## 3. Initialize Flask App
In app/database.py
```
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./tickets.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

In app/models/ticket.py
```
from sqlalchemy import Column, Integer, String
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="open")
```

In app/schemas/ticket.py
```
from pydantic import BaseModel

class TicketBase(BaseModel):
    title: str
    description: str

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None

class TicketOut(TicketBase):
    id: int
    status: str

    model_config = {
        "from_attributes": True
    }
```

In app/services/ticket_service.py
```
from sqlalchemy.orm import Session
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate

def get_all_tickets(db: Session):
    return db.query(Ticket).all()

def get_ticket(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def create_ticket(db: Session, ticket: TicketCreate):
    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def update_ticket(db: Session, ticket_id: int, ticket: TicketUpdate):
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    for field, value in ticket.model_dump(exclude_unset=True).items():
        setattr(db_ticket, field, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def delete_ticket(db: Session, ticket_id: int):
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    db.delete(db_ticket)
    db.commit()
    return db_ticket
```

In  app/routes/ticket_routes.py
```
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.ticket import TicketCreate, TicketOut, TicketUpdate
from app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TicketOut, status_code=201)
def create(ticket: TicketCreate, db: Session = Depends(get_db)):
    return ticket_service.create_ticket(db, ticket)

@router.get("/", response_model=list[TicketOut])
def list_all(db: Session = Depends(get_db)):
    return ticket_service.get_all_tickets(db)

@router.get("/{ticket_id}", response_model=TicketOut)
def get(ticket_id: int, db: Session = Depends(get_db)):
    ticket = ticket_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=TicketOut)
def update(ticket_id: int, ticket: TicketUpdate, db: Session = Depends(get_db)):
    updated = ticket_service.update_ticket(db, ticket_id, ticket)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return updated

@router.delete("/{ticket_id}", response_model=TicketOut)
def delete(ticket_id: int, db: Session = Depends(get_db)):
    deleted = ticket_service.delete_ticket(db, ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return deleted
```

In app/main.py
```
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import ticket_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Issue Tracker API",
    description="A mini ticket system with FastAPI",
    version="1.0.0"
)

app.include_router(ticket_routes.router)
```

## 4. tests/test_tickets.py
In app/tests/conftest

```
import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def created_ticket():
    response = client.post("/tickets/", json={"title": "Bug", "description": "Fix crash"})
    return response.json()

```

In app/tests/test_tickets

```
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
```

## 5. Run the app:
uvicorn app.main:app --reload

## 6. Swagger / OpenAPI Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## 7. Run Unit test
```
pytest -s
```
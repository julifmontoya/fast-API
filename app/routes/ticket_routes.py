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

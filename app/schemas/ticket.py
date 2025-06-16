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
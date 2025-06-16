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

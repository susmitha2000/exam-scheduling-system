
from fastapi import FastAPI
from app.database import Base, engine
from app.models import entities

app = FastAPI(
    title="Exam Scheduling System",
    description="Exam scheduling, room allocation and conflict validation API",
    version="1.0.0",
)


@app.on_event("startup")
def create_database():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Exam Scheduling System API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/v1/database-check")
def database_check():
    return {
        "database": "connected",
        "tables": list(Base.metadata.tables.keys()),
    }

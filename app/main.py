from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routers import (
    alerts,
    auth,
    interventions,
    predictions,
    reports,
    settings,
    students,
    uploads,
    users,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Beacon API",
    version="1.0.0",
    description="Student dropout early-warning system backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(students.router)
app.include_router(uploads.router)
app.include_router(predictions.router)
app.include_router(alerts.router)
app.include_router(interventions.router)
app.include_router(reports.router)
app.include_router(settings.router)


@app.get("/")
def root():
    return {
        "message": "Beacon backend is running",
        "docs": "/docs",
    }
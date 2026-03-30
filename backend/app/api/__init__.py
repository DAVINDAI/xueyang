from fastapi import APIRouter
from app.api import chat, coding_playground, details, search, stats, resume, notes, auth, evolution, assistant, communication

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(coding_playground.router)
api_router.include_router(details.router)
api_router.include_router(search.router)
api_router.include_router(stats.router)
api_router.include_router(resume.router)
api_router.include_router(notes.router)
api_router.include_router(evolution.router)
api_router.include_router(assistant.router)
api_router.include_router(communication.router, prefix="/communication", tags=["communication"])

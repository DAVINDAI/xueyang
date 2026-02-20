from fastapi import APIRouter
from app.api import chat, details, search, stats, resume

api_router = APIRouter()

api_router.include_router(chat.router)
api_router.include_router(details.router)
api_router.include_router(search.router)
api_router.include_router(stats.router)
api_router.include_router(resume.router)

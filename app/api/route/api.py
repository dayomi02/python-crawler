from fastapi import APIRouter

from app.api.router import open_api

router = APIRouter()
router.include_router(open_api.router, tags=["open_api"], prefix="/open_api")

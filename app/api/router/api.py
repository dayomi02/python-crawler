from fastapi import APIRouter

from app.api.router import open_api
from app.api.router import write_data

router = APIRouter()
router.include_router(open_api.router, tags=["open_api"], prefix="/open_api")
router.include_router(write_data.router, tags=["crawler"], prefix="/crawler")

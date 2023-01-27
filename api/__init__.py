from fastapi import APIRouter
from api.photos import photos_router


router = APIRouter(
    prefix="/api",
)

router.include_router(photos_router)

from fastapi import APIRouter
from api.photos import photos_router
from api.auth import auth_router
from api.persons import persons_router


router = APIRouter(
    prefix="/api",
)

router.include_router(photos_router)
router.include_router(auth_router)
router.include_router(persons_router)

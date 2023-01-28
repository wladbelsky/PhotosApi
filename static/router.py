from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from api.auth.router import check_token, User
from api.photos.models import Photo as PhotoModel
from sqlalchemy import select
from database import Database
from config import file_save_path
from os import path

router = APIRouter(
    prefix="/static/images",
)

@router.get("{filename}", response_class=FileResponse)
async def get_image(filename: str, user: User = Depends(check_token)):
    db: Database = await Database()
    async with db.get_session() as session:
        result = await session.execute(select(PhotoModel).where(PhotoModel.filename == filename))
        photo: PhotoModel = result.scalars().first()
        if photo and photo.user_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if photo:
            return FileResponse(path.join(file_save_path, photo.filename))
        raise HTTPException(status_code=404, detail="Image not found")
from fastapi import APIRouter, File, UploadFile, Body, Depends, HTTPException
from .schemas import Photo, PhotoResponse, GeoLocation, Person, PhotoFilters
from database import Database
from .utils import save_file
from .models import Person as PersonModel, Photo as PhotoModel
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from config import server_address
from api.auth.resource import check_token
from api.auth.schemas import User
from datetime import datetime
from typing import Optional


router = APIRouter(
    prefix="/photos",
)


def create_photo_response(photo: PhotoModel):
    return PhotoResponse(
        id=photo.id,
        name=photo.name,
        description=photo.description,
        geolocation=GeoLocation(lat=photo.latitude, lng=photo.longitude),
        persons=[Person(id=person.id, name=person.name) for person in photo.persons],
        filename=photo.filename,
        url=f"{server_address}/static/images/{photo.filename}",
    )


@router.get("/", response_model=list[PhotoResponse])
async def get_photos(user: User = Depends(check_token), filters: PhotoFilters = Depends()):
    db: Database = await Database()
    models = (PhotoModel, PersonModel)

    def parse_filters(filter: dict, table: str = 'photos'):
        sql_filters = []
        model = next(models, lambda m: m.__tablename__ == table, None)
        if not model:
            return []
        for key, val in filter.dict().items():
            if val is not None:
                sql_filters.append(getattr(model, key) == val)
        return sql_filters

    async with db.get_session() as session:
        result = await session.execute(
            select(PhotoModel)\
                .where(
                    PhotoModel.user_id == user.id,
                    *parse_filters(filters.dict()) if filters else [])\
                .options(selectinload(PhotoModel.persons)))
        photos: list[PhotoModel] = result.scalars().all()
        return list(map(create_photo_response, photos))


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, user: User = Depends(check_token)):
    db: Database = await Database()
    async with db.get_session() as session:
        result = await session.execute(select(PhotoModel).where(PhotoModel.id == photo_id))
        photo: PhotoModel = result.scalars().first()
        if user.id != photo.user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return create_photo_response(photo)


@router.post("/", response_model=PhotoResponse)
async def post_photos(data: Photo = Body(...), file: UploadFile = File(...), user: User = Depends(check_token)):
    db: Database = await Database()
    file_name = await save_file(file)

    async with db.get_session() as session:
        photo: PhotoModel = PhotoModel(
            name=data.name,
            datetime=datetime.now(),
            user_id=user.id,
            description=data.description,
            filename=file_name,
            latitude=data.geolocation.lat if data.geolocation else None,
            longitude=data.geolocation.lng if data.geolocation else None,
        )
        session.add(photo)
        await session.commit()
        await session.refresh(photo)
        if data.persons:
            for person in data.persons:
                session.add(PersonModel(name=person.name, photo_id=photo.id))
        await session.commit()
        result = await session.execute(select(PhotoModel).where(PhotoModel.id == photo.id)
                                            .options(selectinload(PhotoModel.persons)))
        photo = result.scalars().first()                                            
        return create_photo_response(photo)

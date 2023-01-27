from fastapi import APIRouter, File, UploadFile, Body
from .schemas import Photo, PhotoResponse, GeoLocation, Person
from database import Database
from .utils import save_file
from .models import Person as PersonModel, Photo as PhotoModel
from sqlalchemy.orm import selectinload
from sqlalchemy import select


router = APIRouter(
    prefix="/photos",
)

@router.get("/")
async def get_photos():
    return {"message": "Hello World"}


@router.get("/{photo_id}")
async def get_photo(photo_id: int):
    ...


@router.post("/", response_model=PhotoResponse)
async def post_photos(data: Photo = Body(...), file: UploadFile = File(...)):
    db: Database = await Database()
    file_name = await save_file(file)

    async with db.get_session() as session:
        photo: PhotoModel = PhotoModel(
            title=data.name,
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
        response = PhotoResponse(
            id=photo.id,
            name=photo.title,
            description=photo.description,
            geolocation=GeoLocation(lat=photo.latitude, lng=photo.longitude),
            persons=[Person(id=person.id, name=person.name) for person in photo.persons],
            filename=file_name,
            url=f"http://localhost:8000/static/images/{file_name}",
        )
        return response

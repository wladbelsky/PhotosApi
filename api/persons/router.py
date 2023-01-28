from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from database import Database
from .models import Person as PersonModel
from sqlalchemy.orm import selectinload, joinedload


router = APIRouter(
    prefix="/persons",
)

@router.get("/autocomplete", response_model=list[str])
async def get_persons_autocomplete(person_name: str):
    db: Database = await Database()
    async with db.get_session() as session:
        result = await session.execute(
            select(PersonModel.name)\
                .where(PersonModel.name.like(f"{person_name}%"))\
                .distinct())
        persons: list[str] = result.scalars().all()
        return persons

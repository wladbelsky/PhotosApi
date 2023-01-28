from pydantic import BaseModel, create_model
from sqlalchemy import inspect
from typing import List, Optional, Set
from datetime import datetime
from .models import Photo as PhotoModel
import json


class GeoLocation(BaseModel):
    lat: float
    lng: float


class Person(BaseModel):
    id: int
    name: str


class Photo(BaseModel):
    name: str
    date: Optional[datetime]
    description: Optional[str]
    geolocation: Optional[GeoLocation]
    persons: Optional[List[Person]]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class PhotoResponse(Photo):
    id: int
    filename: str
    url: str


def create_schema_from_model(model, exclude: Set[str] = None):
    if exclude is None:
        exclude = set()
    return {c.name: (Optional[c.type.python_type], None) for c in model.columns if c.name not in exclude}

def create_schema_from_relationship(rel):
    model = rel.target
    return str(model.name), create_schema_from_model(model)

photo_filters = create_schema_from_model(PhotoModel.__table__, exclude={"user_id"})
for name, inner_model in map(create_schema_from_relationship, inspect(PhotoModel).relationships):
    photo_filters[name] = (create_model(name, **inner_model), None)
PhotoFilters = create_model("PhotoFilters", **photo_filters)

from pydantic import BaseModel, Field
from fastapi import Form
from typing import List, Optional
import json

class GeoLocation(BaseModel):
    lat: float
    lng: float


class Person(BaseModel):
    id: int
    name: str


class Photo(BaseModel):
    name: str
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

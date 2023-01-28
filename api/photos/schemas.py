from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import json


class GeoLocation(BaseModel):
    lat: float
    lng: float


class Person(BaseModel):
    id: int
    name: str


class Photo(BaseModel):
    name: str
    date: Optional[date]
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


class PhotoFilters(BaseModel):
    name: Optional[str]
    description: Optional[str]
    date: Optional[date]
    person_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
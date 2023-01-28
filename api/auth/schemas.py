from pydantic import BaseModel, Field
from fastapi import Form
from typing import List, Optional
from datetime import datetime
import json


class UserLogin(BaseModel):
    username: str
    password: str

class User(UserLogin):
    id: int
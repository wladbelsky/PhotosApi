from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import Database
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from config import jwt_secret
from hashlib import sha256
from .models import User as UserModel
from .schemas import User, UserLogin
from jwt import encode as jwt_encode, decode as jwt_decode, DecodeError

router = APIRouter(
    prefix="/auth",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def hash_password(password: str):
    return sha256(password.encode()).hexdigest()


async def create_token(username, password):
    db: Database = await Database()
    password = hash_password(password)
    async with db.get_session() as session:
        result = await session.execute(select(UserModel).where(UserModel.username == username))
        user: UserModel = result.scalars().first()
        if user and user.password == password:
            token = {
                "id": user.id,
                "username": user.username,
                "password": password,
            }
            return jwt_encode(token, jwt_secret, algorithm="HS256")
        raise HTTPException(status_code=401, detail="Invalid username or password")


async def check_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt_decode(token, jwt_secret, algorithms=["HS256"])
        username = payload["username"]
        password = payload["password"]
        db: Database = await Database()
        async with db.get_session() as session:
            result = await session.execute(select(UserModel).where(UserModel.username == username))
            user: UserModel = result.scalars().first()
            if user and user.password == password:
                return User(id=user.id, username=user.username, password=user.password)
    except DecodeError:
        pass
    raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", status_code=201, description="Register new user")
async def register(user: UserLogin):
    db: Database = await Database()
    username = user.username
    password = user.password
    async with db.get_session() as session:
        result = await session.execute(select(UserModel).where(UserModel.username == username))
        user = result.scalars().first()
        if user:
            raise HTTPException(status_code=400, detail="User already exists")
        session.add(UserModel(username=username, password=hash_password(password)))
        await session.commit()
        return {"message": "User created"}


@router.post("/token", description="Get authentification token")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    return {"access_token": await create_token(username, password), "token_type": "bearer"}

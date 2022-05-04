from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session
from starlette.responses import Response

import models
from database import engine, SessionLocal

# secret key generated using 256-bit
SECRET_KEY = "ShVmYq3t6w9z$C&F)J@NcRfTjWnZr4u7"
ALGORITHM = "HS256"


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hashed(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    else:
        expire = datetime.utcnow() + timedelta(minute=15)

    encode.update({"exp": expire})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()

    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name

    create_user_model.hashed_password = get_password_hashed(create_user.password)
    create_user_model.is_active = True

    db.add(create_user_model)
    db.commit()

    # return create_user_model


# method to return JSON web token
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # return "User Validated!"
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)

    return {"token":  token}

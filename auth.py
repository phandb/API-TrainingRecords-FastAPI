from fastapi import FastAPI, Depends
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hashed(password):
    return bcrypt_context.hash(password)


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


import sys
sys.path.append("..")
from pydantic import BaseModel
from routers.auth import get_current_user, get_user_exception, verify_password, get_password_hashed
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found!!"}}
)

models.Base.metadata.create_all(bind=engine)


# Setup database
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


# ------ Users API Endpoints-----------
@router.get("/")
async def read_all_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@router.get("/{user_id}")
async def read_user_by_path_param(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    return 'User id is invalid'


@router.get("/user")
async def read_user_by_query_param(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    return 'Invalid user_id'


@router.put("/password")
async def update_user_password(user_verification: UserVerification,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    # Validate logged in user
    if user is None:
        raise get_user_exception()

    # Get logged in user's info and put into variable user_model
    user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()

    # Validate user model
    if user_model is not None:
        if user_verification.username == user_model.username and verify_password(
                user_verification.password, user_model.hashed_password):
            #  Update password
            user_model.hashed_password = get_password_hashed(user_verification.new_password)
            db.add(user_model)
            db.commit()
            return 'successful'
    return 'Invalid user or request'


@router.delete("/")
async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    if user is None:
        return get_user_exception()

    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    if user_model is None:
        return "Invalid user or request"
    db.query(models.Users).filter(models.Users.id == user.get("id")).delete()
    db.commit()
    return 'Delete Successful'


# ---------------End of API Endpoints--------
def http_exception():
    return HTTPException(status_code=404, detail="User not found")

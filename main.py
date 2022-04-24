from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, SessionLocal
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


'''
# Create database at the beginning
@app.get("/")
async def create_database():
    return {"Database": "Created"}
'''


# ---------CRUD API-----------------
@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Tasks).all()


@app.get("/task/{task_id}")
async def read_task(task_id: int, db: Session = Depends(get_db)):
    task_model = db.query(models.Tasks).filter(models.Tasks.id == task_id).first()

    if task_model is not None:
        return task_model
    raise http_exception()


def http_exception():
    return HTTPException(status_code=404, detail="Task not found")

from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
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


class Task(BaseModel):
    task_name: str
    task_category: str
    date_taken: datetime


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


@app.post("/")
async def create_task(task: Task, db: Session = Depends(get_db)):
    task_model = models.Tasks()

    task_model.task_name = task.task_name
    task_model.task_category = task.task_category
    task_model.date_taken = task.date_taken

    db.add(task_model)
    db.commit()

    return {
        'status': 201,
        'transaction': 'Successful'
    }


@app.put("/task/{task_id}")
async def update_task(task_id: int, task: Task, db: Session = Depends(get_db)):
    # find task based on id
    task_model = db.query(models.Tasks)\
        .filter(models.Tasks.id == task_id)\
        .first()

    # Check the task_model
    if task_model is None:
        raise http_exception()

    task_model.task_name = task.task_name
    task_model.task_category = task.task_category
    task_model.date_taken = task.date_taken

    # Update database
    db.add(task_model)
    db.commit()

    return {
        'status': 200,
        'transaction': 'Successful'
    }


def http_exception():
    return HTTPException(status_code=404, detail="Task not found")

from fastapi import FastAPI
import models
from database import engine
from routers import auth, tasks, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Add auth router to the main app
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)


# The following codes were moved to the task.py file
"""  
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


# ---------CRUD API End Points-----------------
@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Tasks).all()


@app.get("/tasks/user")
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()
    return db.query(models.Tasks)\
        .filter(models.Tasks.owner_id == user.get("id"))\
        .all()


# Add user dictionary to parameter to retrieve task for that user
@app.get("/task/{task_id}")
async def read_task(task_id: int,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # Validate the user
    if user is None:
        raise get_user_exception()
    # retrieve requested task for the user
    task_model = db.query(models.Tasks)\
        .filter(models.Tasks.id == task_id)\
        .filter(models.Tasks.owner_id == user.get("id"))\
        .first()

    if task_model is not None:
        return task_model
    raise http_exception()


# modified to get current user
@app.post("/")
async def create_task(task: Task,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    # Validate the user
    if user is None:
        raise get_user_exception()
    task_model = models.Tasks()

    task_model.task_name = task.task_name
    task_model.task_category = task.task_category
    task_model.date_taken = task.date_taken
    task_model.owner_id = user.get("id")  # assign task to current user

    db.add(task_model)
    db.commit()

    return {
        'status': 201,
        'transaction': 'Successful'
    }


@app.put("/task/{task_id}")
async def update_task(task_id: int,
                      task: Task,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    # Validate the user
    if user is None:
        raise get_user_exception()
    # find task based on id
    task_model = db.query(models.Tasks)\
        .filter(models.Tasks.id == task_id)\
        .filter(models.Tasks.owner_id == user.get("id"))\
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


@app.delete("/task/{task_id}")
async def delete_task(task_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):

    # Validate user
    if user is None:
        raise get_user_exception()
    # Retrieve the task based on id
    task_model = db.query(models.Tasks)\
        .filter(models.Tasks.id == task_id)\
        .first()

    # Check for the task
    if task_model is None:
        raise http_exception()

    # Delete the object in the database
    db.query(models.Tasks)\
        .filter(models.Tasks.id == task_id)\
        .delete()

    #  Update the database
    db.commit()

    return {
        'status': 200,
        'transaction': 'Successful'
    }


def http_exception():
    return HTTPException(status_code=404, detail="Task not found")


"""
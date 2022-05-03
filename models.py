from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, date


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    tasks = relationship("Tasks", back_populates="owner")


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String)
    task_category = Column(String)
    date_taken = Column(Date, default=date.today())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="tasks")

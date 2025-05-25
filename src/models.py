from sqlalchemy import Column, Integer, String, Boolean
from src.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index = True)
    status_completed = Column(Boolean, index=True)
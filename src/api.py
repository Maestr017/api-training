from fastapi import HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from src.models import Task
from src.schemas import TaskCreate, TaskEditStatus, TaskEditTitle, TaskResponse
from src.dependecies import get_db

main_router = APIRouter()

@main_router.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    db_task = Task(title=task.title, status_completed=task.status_completed)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@main_router.get("/tasks/", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@main_router.patch("/tasks/edit-status/{task_id}", response_model=TaskResponse)  # Лучше использовать patch, потому что put меняет объект целиком
async def update_task_status(task_id: int, status_data: TaskEditStatus, db: Session = Depends(get_db)) -> TaskResponse:
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail=f"Задача с ID {task_id} не найдена")

    db_task.status_completed = status_data.new_status
    db.commit()
    db.refresh(db_task)

    return db_task

@main_router.patch("/tasks/edit-title/{task_id}", response_model=TaskResponse)
async def update_task_title(task_id: int, title_data: TaskEditTitle, db: Session = Depends(get_db)) -> TaskResponse:
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail=f"Задача с ID {task_id} не найдена")

    db_task.title = title_data.new_title
    db.commit()
    db.refresh(db_task)

    return db_task

@main_router.delete("/tasks/delete/{id}", response_model=TaskResponse)
async def delete_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404,detail=f'Задача с id {task_id} не найдена')

    db.delete(db_task)
    db.commit()

    return db_task  # После коммита задача еще доступна